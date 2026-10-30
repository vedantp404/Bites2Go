# Decision register

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
