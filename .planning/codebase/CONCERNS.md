---
last_mapped_commit: f54c1f195289ce4d54a79e7def2170fb84f20858
last_mapped_at: 2026-10-30
---
# Codebase Concerns

**Analysis Date:** 2026-10-30

## Tech Debt

**Single Document SQLite Storage per Domain:**
- Issue: Entire histories are serialized and stored as monolithic JSON strings under single KV keys (`bites2go.diary.v1`, `bites2go.health.v1`, `bites2go.library.v1`).
- Files: `apps/mobile/src/storage/diaryRepository.ts#L7`, `apps/mobile/src/storage/healthRepository.ts`, `apps/mobile/src/storage/libraryRepository.ts`.
- Impact: Full document read and deserialization required on startup and every write operation. As users log entries over multiple months/years, memory consumption and serialization latency increase linearly.
- Fix approach: Migrate from key-value documents to normalized relational SQLite tables with indexed date columns (`YYYY-MM-DD`) and row-level operations once multi-year scale or cloud sync demands it.

**In-Memory Memoization vs Query-Level Filtering:**
- Issue: Filtering by date or calculating nutritional metrics involves in-memory iterations over all loaded records rather than SQL `WHERE` clauses.
- Files: `apps/mobile/src/state/DiaryProvider.tsx`, `apps/mobile/src/domain/insights.ts`.
- Impact: In-memory arrays remain lightweight for hundreds of entries, but unbounded growth could slow rendering on low-end Android hardware.
- Fix approach: Transition to SQLite indexed queries with paging.

## Known Bugs

**Uncertain Write Recovery Edge Case:**
- Symptoms: If an acknowledgement fails after a write commits to SQLite, an uncertain write warning is surfaced. If the user forces an app restart instead of retrying or reloading, the UI state upon reopening must safely re-sync.
- Files: `apps/mobile/src/storage/diaryRepository.ts`, `apps/mobile/src/state/DiaryProvider.tsx`.
- Trigger: Process termination, battery exhaustion, or native crash precisely during storage acknowledgement.
- Workaround: The application reloads authoritative persisted state on exit and startup, hiding stale displayed entries while loading.

## Security Considerations

**Audit Vulnerabilities in Tooling (3 High / 5 Low):**
- Risk: `npm audit` reports 3 high severity vulnerabilities in `zod` 3.25.76 (GHSA-mrhx-c7xc-m3w5) and Expo CLI wrapper dependencies, and 5 low severity vulnerabilities in `deepmerge` 4.3.1 (GHSA-gcqx-w48m-w2h4).
- Files: `apps/mobile/package-lock.json`, `docs/RELEASE_READINESS.md`.
- Current mitigation: Detailed analysis in `docs/RELEASE_READINESS.md` confirms neither `zod` nor `deepmerge` are imported into application runtime code; Android Hermes export source maps contain 0 instances. Exposure is isolated to local dev tooling and DevTools plugins. Production release remains strictly blocked pending upstream Expo CLI patches.
- Recommendations: Monitor upstream Expo SDK updates for compatible patch releases. Do not run untrusted third-party Expo plugins.

**Unencrypted Local Database:**
- Risk: SQLite database file is stored in standard application sandbox without app-level encryption. Physical device access or root access can view logged nutrition and weight history.
- Files: `apps/mobile/src/storage/localDiary.ts`.
- Current mitigation: Standard Android OS sandbox permissions protect files between non-rooted applications. No network uploads or telemetry.
- Recommendations: Incorporate SQLCipher or encrypted storage adapters before general public distribution if privacy regulations mandate app-level encryption at rest.

## Performance Bottlenecks

**Large List Rendering in Custom Foods and Weight History:**
- Problem: `ScrollView` is used rather than virtualized `FlatList` or `FlashList` for browsing custom foods, recipes, and historical weight logs.
- Files: `apps/mobile/src/screens/MyFoodsScreen.tsx`, `apps/mobile/src/screens/ProgressScreen.tsx`.
- Cause: Unvirtualized lists mount all child components simultaneously into the React Native view hierarchy.
- Improvement path: Profile long user histories on physical Android devices; migrate to `FlashList` or `FlatList` with `getItemLayout` when item count exceeds 100.

## Fragile Areas

**Date Handling Across Timezone and DST Transitions:**
- Files: `apps/mobile/src/domain/diary.ts#L10-L28`, `apps/mobile/src/domain/calendar.ts`.
- Why fragile: Date arithmetic mixing UTC timestamps and local calendar dates can shift entries across midnight boundaries or misalign calendar grids during daylight saving transitions.
- Safe modification: Always construct dates at local noon (`new Date(y, m - 1, d, 12)`) and format using explicit component padding (`getFullYear()`, `getMonth() + 1`, `getDate()`). Never use `toISOString().split('T')[0]`.
- Test coverage: Extensively guarded in `apps/mobile/tests/calendar.test.mjs` and `apps/mobile/tests/diary.test.mjs`.

**Monolithic Single-Key Write Concurrency:**
- Files: `apps/mobile/src/storage/diaryRepository.ts#L10-L15`.
- Why fragile: Concurrent writes could overwrite state without a serialized queue.
- Safe modification: All operations MUST funnel through the internal `serialize()` queue. Never call `Storage.setItemAsync` directly outside repositories.
- Test coverage: Tested in `apps/mobile/tests/diary.test.mjs` and `apps/mobile/tests/health.test.mjs`.

## Scaling Limits

**History Size:**
- Current capacity: Tested cleanly with up to 10,000 synthetic entries.
- Limit: ~50,000 entries (roughly 10 MB JSON payload).
- Scaling path: Refactor to relational table structure with indexed row queries before multi-year continuous usage.

## Dependencies at Risk

**Expo CLI Transitive Zod Dependency:**
- Risk: Zod 3.25.76 has an unpatched memory exhaustion vulnerability on large invalid schemas; Zod 4 migration has breaking changes unsupported by current Expo CLI.
- Impact: Blocks formal security clearance for production release (`docs/RELEASE_READINESS.md`).
- Migration plan: Await Expo SDK release that bumps or isolates the internal CLI validator.

## Missing Critical Features

**Live Cloud Sync & Auth UI:**
- Problem: The backend PostgreSQL schema and sync planning contracts are fully drafted (`supabase/migrations/202610300001_diary_sync.sql`, `apps/mobile/src/cloud/diarySync.ts`), but user authentication screens, live HTTP transport, and consent/conflict resolution dialogs are not yet mounted in the app.
- Blocks: Multi-device synchronization and off-device cloud backups.

**Physical Android Device Verification:**
- Problem: Development tests run via Node test runner and simulated environments; physical Android TalkBack, native splash transitions, keyboard avoidance, and hardware Back button navigation require formal on-device acceptance.
- Blocks: Final release readiness.

## Test Coverage Gaps

**Native OS Gesture & Keyboard Navigation:**
- What's not tested: Native predictive back gesture, keyboard dismiss events on varied Android screen densities, TalkBack screen reader accessibility traversal.
- Files: `apps/mobile/src/screens/*.tsx`.
- Risk: Subtle rendering or focus bugs on non-standard Android form factors.
- Priority: Medium (requires physical device verification per `docs/TEST_PLAN.md`).

---

*Concerns audit: 2026-10-30*
