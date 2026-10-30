# Decision register

## Stage 7 implementation plan

Use a separate versioned SQLite KV document for weights, height, weight goal and effective-dated nutrition goals. Initial migration is absent key to empty v1; no diary/appearance schema changes or destructive SQL. Reuse the existing parameterized KV adapter and serialized, compare-before-write repository pattern. Defaults remain unset; today's explicit goal changes preserve earlier dates. Weight records are unique by local date and use kg; height uses cm. UI limits: weight/target 20–500 kg, height 100–250 cm, calories 0–10000 kcal, protein/fat 0–500 g, carbs 0–1500 g; these are data-entry bounds, not recommendations. Use existing SVG for dated measurement points without interpolated data. BMI is numeric only, adult-focused (20+), with screening limitations and no classification. No dependencies or Stage 8 work planned.

## Visual redesign and theme milestone

- Adopt Option B (Vibrant Food App) without changing food values, diary schema, local date rules or stage scope.
- Default to System, with Light/Dark overrides saved separately in existing SQLite. Apply selection before awaiting persistence; report failures honestly and allow retry.
- Centralize complete semantic palettes and subscribe all UI consumers. Keep native status/navigation chrome aligned and hold splash during preference loading.
- Add only Expo-compatible native modules required for automatic Android appearance, navigation icons and startup splash. Avoid new image or persistence libraries.
- Bundle two verified CC0 food photos; map by stable ID and retain polished placeholders for other foods. Provenance lives beside the assets.
- Use a themed delete confirmation instead of an OS-themed alert, keeping cancellation and storage semantics intact.
- Automated and export verification is not Android device acceptance. Stage 7 remains out of scope.

Recorded 2026-10-30. “Confirmed” means supplied project constraints or direct observations; “recommended” is provisional architecture awaiting review, not an implementation claim.

| ID / status | Decision | Alternatives, reason and revisit point |
| --- | --- | --- |
| D01 Confirmed | Android first; Expo/React Native/TypeScript, FastAPI/Pydantic, Supabase PostgreSQL/Auth proposed stack retained. | Native Kotlin or another database adds no demonstrated benefit for the requested MVP. No dependencies pinned until Stage 2/4. |
| D02 Confirmed | Manual core precedes AI; deterministic nutrition, user-confirmed predictions and historical snapshots are mandatory. | Model-generated calories cannot provide reproducible source-based history. |
| D03 Recommended | One repository, `mobile/`, `backend/`, `supabase/migrations/`; no npm workspaces or microservices initially. | Separate repos/queues add coordination without current need. Revisit only for demonstrated deployment/team constraints. |
| D04 Recommended | Auth directly with Supabase; FastAPI forwards verified user JWT to Data API; RLS plus checked write functions. | Direct privileged DB access would need careful request-role propagation; service-role user CRUD rejected. Test RPC/grants feasibility at Stage 5 before real data. |
| D05 Recommended | Immutable food/recipe versions plus per-entry snapshots; effective-dated goals. | Referencing mutable catalog rows alone corrupts history; snapshot duplication is deliberate. |
| D06 Recommended | Explicit local diary date and stored IANA timezone; UTC audit times separately. | Inferring diary dates from UTC timestamps causes travel/midnight errors. Confirm backfill/streak conventions before Stage 6. |
| D07 Recommended | Decimal/NUMERIC calculations, authoritative writes and shared preview vectors; preserve source energy and missingness. | Floating-point totals or automatic 4/4/9 overwrite obscure data quality. Verify SQL/Python/mobile parity at Stage 4/5. |
| D08 Recommended | Curated USDA base catalog; IFCT blocked pending written product rights. | Public PDF availability does not grant electronic product rights. Stage 4 cannot publish Indian coverage until provenance/coverage gate passes. |
| D09 Recommended | Online writes, visibly cached read-only data; full offline sync deferred. | Multi-device queues/conflict resolution would enlarge MVP. Preserve drafts and make retry safe; revisit based on testing needs. |
| D10 Confirmed | Photos not saved by default; AI keys stay backend-only. | Persistent photo history requires opt-in and storage policies; do not create a bucket now. |
| D11 Recommended | xAI Grok 4.7 and Gemini 2.5 Flash as evaluation candidates only. | No provider selected on marketing claims; benchmark quality, privacy, latency and cost at Stage 10. Pricing/model availability must be rechecked. |
| D12 Recommended | Five tabs in full UI, warm/forest/mint tokens, system typography, accessible manual Add Food. | Stage 2 remains one screen; Stage 3 prototypes navigation. No large component suite needed initially. |
| D13 Recommended | Stage 2: Expo Go-compatible minimal app where supported; own development builds later. | Current official docs show SDK 58/57 transition; choose after recheck. Do not independently upgrade React Native/React outside the SDK compatibility set. |
| D14 Confirmed | No Stage 1 commits, pushes, installs or services. Preserve existing `master` repository. | Renaming to `main` and connecting GitHub are later reviewed actions; do not initialize another repository. |
| D15 Recommended | Goal achievement rule and streak semantics as explicitly specified in PRD. | Macro minimums/energy tolerance are tracking conventions; user-configurable bands could follow. Review this policy before Stage 6; do not market as a medical optimum. |
| D16 Recommended | Auth/backend/migrations begin Stage 4, persistence isolation gate Stage 5; goals UI Stage 7. | This clarifies dependencies missing from the feature-only roadmap. Security/tests happen in every stage, with Stage 11 a consolidated gate. |

## Open decisions and risks

- Before Stage 2: user approval; choose Expo Go physical device or local emulator route, supported SDK and Node engine. Node is installed, but package compatibility has not been tested. Android SDK absence on PATH does not prove Android Studio is absent.
- Before GitHub connection: confirm account ownership, visibility, actual repository URL and associated email or GitHub no-reply; choose code license. Existing Git identity is configured but GitHub attribution is unverified.
- Before Stage 4: verify Python package compatibility with installed 3.13; choose a supported interpreter if required, record exact versions; obtain external-service authorization only when needed. No downgrade performed now.
- Before Stage 5: choose email/password versus OTP (recommend email/password with verification for MVP), recovery/deep-link settings and production email delivery; validate restricted diary-write function permissions.
- Before Stage 6/7: confirm goal bands, streak backfills and weight/date limits with product review. Start with manual targets; no automatic medical recommendations.
- Before Stage 10/release: real-user consent, provider retention/region/age terms, evaluation budget, hosting region/cost and privacy obligations. No account-specific quotas or model reliability verified.
- OneDrive workspace may interfere with file watching, long paths or Android builds. If observed, use a user-approved nonsynced checkout later; do not move the workspace preemptively. Java printed shared archive warnings; Android Gradle/JDK compatibility remains unverified.

## Stage 2 implementation — 2026-10-30

User approved Stage 2 in the current request. Implemented in `apps/mobile/` (supersedes the earlier `mobile/` proposal). Single empty diary screen, theme tokens, strict TypeScript, safe areas and a clearly labeled placeholder Add Food alert. No real nutrition data or services.

Verified: typecheck, lint, formatting, one AA contrast test, Expo Doctor 21/21, public Expo config and Android Hermes bundle export passed. `npm start -- --localhost` started Metro at port 8081; its status endpoint returned `packager-status:running`. This verifies development-server startup, not on-device rendering. No Android execution: adb/emulator unavailable on PATH, Android SDK variables unset and standard local SDK adb absent. Device layout, TalkBack and font scaling still require manual verification.

Installed: Expo 57.0.31, React Native 0.86.3, React 19.2.3, safe-area-context 5.7.0, TypeScript 6.0.3, ESLint 9.39.5/config-expo 57.0.2, Prettier 3.9.10, Expo Doctor 1.21.5. Node 22.23.2/npm 10.9.8. Lockfile records transitive versions. SDK 57 follows current Expo Go transition guidance: https://docs.expo.dev/get-started/create-a-project/ . No navigation library needed yet.

Known issues: npm audit retains 8 transitive advisories (5 low, 3 high) involving Expo tooling's deepmerge/zod chain after compatible `npm audit fix`; forced remediation proposes incompatible Expo 51 downgrade and was not applied. Resolve/reassess before release. Expo-selected ESLint 9 emits an upstream support warning; retain compatibility pending supported SDK upgrade. The Node contrast test emits a module-type detection warning but passes. No claim of production security readiness.

Next: review Stage 2 and verify the screen on Android before Stage 3. Stage 3 has not begun.

## D17 — Approved SDK 58 migration (2026-10-30)

User's installed Android Expo Go requires SDK 58. Upgrade on `codex/expo-sdk-58` from clean master f75c4f3, using `npm install expo@^58.0.0` then `npx expo install --fix`; Expo selected compatible versions. Keep the existing app and tooling, with no independent React/RN version guesses. This supersedes D13's SDK 57 preview recommendation. Master must not be merged or changed by this task.

Reviewed [upgrade guide](https://docs.expo.dev/workflow/upgrading-expo-sdk-walkthrough/), [SDK 58 walkthrough](https://expo.dev/blog/how-to-upgrade-to-sdk-58), [version reference](https://docs.expo.dev/versions/v58.0.0/) and [release notes](https://expo.dev/changelog/sdk-58). Relevant risks were stricter React Native types and removed APIs; the current screen uses none of the identified removed APIs and passed typecheck. Router/iOS/native-project migrations do not apply. The status-bar plugin was added by Expo alignment. No source compatibility changes were necessary.

Retain and disclose the existing npm audit findings; the reported forced remedy downgrades Expo to 51 and conflicts with the task. No force fix, dependency overrides or warning suppression. Reassess upstream fixes before release.

## Stage 3 dashboard — 2026-10-30

Stage 3 authorized on codex/stage-3-dashboard from clean SDK 58 branch 64e5f33. Adopt the previously recommended Expo Router for five real tab destinations; avoid ad-hoc navigation state. Use labeled synthetic example meals for nonzero progress and two empty meal sections. Targets are demo values, not recommendations. Present incomplete destinations honestly. Current local date refreshes each minute and on foreground; no history/timezone persistence is implied. Keep strict typing and existing design tokens. No Stage 4 implementation.

## Reference-inspired UI refinement

User supplied a nutrition-app visual reference. Adapted Home with a forest-green fading header, centered identity/date, calorie progress ring, compact colored macro bars, pill action and rounded meal rows. Diary shares meal-card styling; tabs now have consistent SVG line icons. Demo labeling remains visible and calculations/features are unchanged. No invented nutrition score, history chart or food-search feature was added.

Added Expo-compatible SVG/linear-gradient modules. Installation exposed an existing react-dom 19.3.1 peer mismatch with React 19.3.0; `expo install react-dom` aligned it to the SDK-compatible version without force/legacy flags. Initial refactor syntax and strict icon-color typing failures were fixed; types, lint, formatting, five tests, Doctor 20/20 and Android export passed. Existing eight audit advisories remain. Visual fidelity, physical Android rendering, large text and TalkBack remain unverified and require phone review.

## Stage 4 scope and implementation plan

The explicit Stage 4 request supersedes D16 and the old Stage 4a/4b backend roadmap: implement offline food search and portion previews only. No source catalog exists. Use 12 authored illustrative fixtures, each with sample provenance; no external composition dataset is imported or represented as verified. Production source rights/coverage remain unresolved.

Wrap existing tabs in an Expo Router Stack; one food-search route owns search/detail draft state and preserves query, grams and meal context when returning from detail. Exiting the flow discards the temporary draft. Retain native Android Back behavior within that flow. Use existing tokens/components and dependencies. Pure TypeScript functions handle search, validation and scaling; Node tests cover them. Local preview uses unrounded JavaScript numbers with finite-result validation, not the future Decimal persistence contract. No saved nutrition or dashboard totals change.

## Stage 5 local persistence plan

The explicit Stage 5 request supersedes the earlier cloud/Auth scope. No existing storage library is installed. Use Expo-selected expo-sqlite (SDK 58/Expo Go supported) via its async key-value API for one versioned diary document, and expo-crypto UUIDs for stable retry-safe entry IDs. This is a small local diary, not an encrypted clinical record store. A single repository serializes read/validate/write operations; UI consumes shared state updated only after successful persistence. Invalid/unsupported documents block writes and remain untouched. No automatic clearing or destructive migration.

Store immutable food/reference/portion snapshots, source/status, meal, local YYYY-MM-DD and UTC audit timestamps. Edits use recorded reference nutrition. Pure totals preserve missingness. Calendar-component date keys and noon-based day stepping avoid UTC slicing and DST day-length arithmetic. Existing demo targets remain explicitly illustrative; sample meal fixtures never seed the diary. A provider separates screens from storage; future sync needs explicit conflict/version/privacy design. No backend, accounts, analytics or Stage 6.

References: https://docs.expo.dev/versions/v58.0.0/sdk/sqlite/ and https://docs.expo.dev/versions/v58.0.0/sdk/crypto/.

## Stage 6 calendar plan

Reuse the validated Stage 5 SQLite document and provider; do not migrate or duplicate records. Build a memoized date index once per entries update. Home/Diary/Calendar select date buckets; calendar checks only the displayed month's cells. No per-month full-document rereads, second cache of persisted data, new library, or SQL schema migration. SQL row queries would require a broader migration of the single JSON document and are deferred until history size justifies it.

Calendar renders a Monday-first month grid with independent visible month and selected diary date, today text, logged bullet/count semantics and selected outline. Its selected-day diary reuses existing summaries/meals/actions inline, so stack Back returns from Add Food/edit to the same calendar state. Month browsing alone never changes the selected date. Today explicitly selects the device-local date. Future dates can be browsed, but the existing PRD/Stage 5 future-logging restriction remains clearly labeled. Minimum 48 dp date targets use horizontal scrolling on narrow screens. No streaks, weight, accounts, cloud or Stage 7.
