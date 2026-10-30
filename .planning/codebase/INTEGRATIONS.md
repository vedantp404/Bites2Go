---
last_mapped_commit: f54c1f195289ce4d54a79e7def2170fb84f20858
last_mapped_at: 2026-10-30
---
# External Integrations

**Analysis Date:** 2026-10-30

## APIs & External Services

**Supabase Backend Foundation (Prepared / Offline by Default):**
- Service: Supabase (PostgreSQL 15+, Supabase Auth, PostgREST RPC)
- Purpose: Planned cloud sync and cloud backup for food diary records (`docs/BACKEND.md`).
- SDK/Client: Direct HTTP/PostgREST upload contract defined in `apps/mobile/src/cloud/diarySync.ts`.
- Auth Config: `EXPO_PUBLIC_SUPABASE_URL` and `EXPO_PUBLIC_SUPABASE_PUBLISHABLE_KEY` in `apps/mobile/.env.example`.
- Operational State: Fail-closed offline mode is active (`apps/mobile/src/cloud/config.ts`). The application runs 100% offline; no live network calls or telemetry are initiated.

**AI Food Recognition:**
- Status: Not implemented / Deferred. PRD outlines future image recognition, but all current image handling is local CC0 bundled assets.

## Data Storage

**Databases:**
- **Local SQLite (`expo-sqlite/kv-store`):**
  - Connection: Local persistent SQLite database managed by Expo SDK 58.
  - Client: `Storage` abstraction in `apps/mobile/src/storage/localDiary.ts`.
  - Stored Documents (Versioned JSON values):
    - `bites2go.diary.v1` (`apps/mobile/src/storage/diaryRepository.ts`): Diary entries with food reference snapshots and portions.
    - `bites2go.health.v1` (`apps/mobile/src/storage/healthRepository.ts`): Weight entries, height, and effective-dated calorie/macro goals.
    - `bites2go.library.v1` (`apps/mobile/src/storage/libraryRepository.ts`): Custom foods, recipes with ingredient snapshots, and favourites.
    - `bites2go.appearance.v1` (`apps/mobile/src/theme/appearance.ts`): Theme preference (`'system' | 'light' | 'dark'`).
    - `bites2go.checkpoint.v1` (`apps/mobile/src/cloud/checkpointRepository.ts`): Sync checkpoint tracking (unmounted from runtime UI).
- **Remote PostgreSQL (Supabase Migration Prepared):**
  - File: `supabase/migrations/202610300001_diary_sync.sql`
  - Tables: `diary_records` (owner_id, record_id, revision, payload, deleted_at, updated_at).
  - Security: Row Level Security (RLS) enforced (`auth.uid() = owner_id`). Direct INSERT/UPDATE prohibited; writes go through SECURITY DEFINER stored procedure `sync_diary_record`.

**File Storage:**
- Local filesystem only (`apps/mobile/assets/`): Bundled CC0 food images (apple, banana), app icons, and splash screens. No remote image storage or CDN integration.

**Caching:**
- In-memory memoized caches:
  - Date index `indexDiaryDates` (`apps/mobile/src/domain/calendar.ts`, `apps/mobile/src/state/DiaryProvider.tsx`) for instant month grid rendering.
  - Nutrition calculations and eligibility summaries (`apps/mobile/src/domain/insights.ts`).

## Authentication & Identity

**Auth Provider:**
- Current: Offline local device mode. No user login or registration UI is displayed.
- Planned Architecture: Supabase Auth (`auth.users`) using email/password or magic links (`docs/BACKEND.md`). Session tokens must be securely stored using `expo-secure-store` before activation.

## Monitoring & Observability

**Error Tracking:**
- None installed. Errors are surfaced directly in UI state (`error` and `retry` triggers in state providers).
- No third-party trackers (e.g. Sentry, Datadog, Firebase Crashlytics) to respect strict offline privacy.

**Logs:**
- Console diagnostics only (`console.warn`, `console.error`).
- Splash screen error handler (`apps/mobile/app/_layout.tsx`) suppresses raw error dumps to prevent accidental credential or stack trace exposure.

## CI/CD & Deployment

**Hosting:**
- Mobile App: Android Standalone APK / AAB.
- Backend: Supabase project instance (local PostgreSQL container or hosted Supabase platform).

**CI Pipeline:**
- Test Automation: Node test runner (`npm test --prefix apps/mobile`).
- SQL Verification: `scripts/test-cloud-sql.ps1` runs against local/disposable PostgreSQL instances.
- Security Scanner: `scripts/security-scan.py` verifies git history and build artifacts against credential leak patterns.

## Environment Configuration

**Required env vars:**
- `EXPO_PUBLIC_SUPABASE_URL`: HTTPS endpoint for Supabase project (optional, defaults to offline mode).
- `EXPO_PUBLIC_SUPABASE_PUBLISHABLE_KEY`: Public anonymous API key (optional, defaults to offline mode).

**Secrets location:**
- No secrets are stored in Git.
- Client `.env.example` explicitly documents that only public, non-sensitive tokens may use the `EXPO_PUBLIC_` prefix.

## Webhooks & Callbacks

**Incoming:**
- None.

**Outgoing:**
- None.

---

*Integration audit: 2026-10-30*
