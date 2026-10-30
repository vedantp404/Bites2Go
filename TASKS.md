# Ordered roadmap

## Current Stage 4 status — 2026-10-30

Stage 4 is the user-authorized **offline food-search and portion-preview foundation**, superseding the earlier Stage 4a/4b backend scope. Historical stage notes below are retained as history, not current instructions. No backend/authentication/persistence has been implemented. Stop before Stage 5.

Status as of 2026-10-30. Stage 2 is authorized; Stage 3 awaits review. A stage is complete only with documented evidence. Each stage can contain multiple small reviewed tasks; do not implement a stage's entire feature list in one generation.

- [x] **Stage 1 — Foundation.** Inspect complete project workspace and Git/tools; preserve existing state; document product, architecture, design, tests, security, research, decisions, rules and GitHub process; review links/consistency. No app implementation, commits or pushes.
- [x] **Approval gate.** User reviews Stage 1 and approves Stage 2. No dependent implementation before approval.
- [ ] **Stage 2 — Minimal Expo application.** Depends on approval. Acceptance checklist below; no backend/services needed.
- [ ] **Stage 3 — UI prototype.** Depends on 2. Build dashboard and five-tab navigation in separate tasks using labeled synthetic data. Acceptance: Design tokens consistent, Add Food prototype reachable, empty/partial/error states and small-screen/TalkBack checks recorded; no fake persistence claim.
- [ ] **Stage 4a — Data and backend decisions.** Depends on 3. Approve source coverage/rights matrix, runtime versions, Auth plan and environment approach. Acceptance: every MVP food category has lawful source or explicit documented gap; blockers resolved before catalog publication; no unverified values.
- [ ] **Stage 4b — Nutrition foundation.** Depends on 4a. Initialize modular FastAPI/Pydantic, schema/migrations and read-only catalog/search, serving conversions and deterministic engine. Acceptance: calculation/unit/import tests, source/missingness metadata and shared preview fixtures pass; dependencies locked; no private data until RLS gate.
- [ ] **Stage 5a — Auth and isolation.** Depends on 4b and authorized Supabase environment. Acceptance: JWT validation, secure session flow, private-table RLS/grants and restricted write function pass two-user/anonymous/direct-API tests.
- [ ] **Stage 5b — Persistent logging.** Depends on 5a. Add/edit/delete four meal categories, quantity previews, snapshots, daily totals and historical dates. Acceptance: restart/refetch works; no duplicate retry or silent concurrent overwrite; old catalog versions stable; network errors preserve drafts.
- [ ] **Stage 6 — Calendar/history.** Depends on 5b. Monthly navigation, diary date selection, completeness and simple logging/goal streak calculations. Acceptance: product rule review completed, timezone/leap/gap/backfill/deletion cases pass. Goal streak shows not evaluable until goals exist; use synthetic target fixtures for tests.
- [ ] **Stage 7 — Weight and goals; MVP checkpoint.** Depends on 6. Manual nutrition targets, effective dates, BMI, dated weights and trends. Acceptance: gain/loss/maintenance/zero targets handled, weekly averages show sample counts; end-to-end Android MVP manual journey and privacy gates pass. No AI dependency.
- [ ] **Stage 8 — Custom and reusable foods.** Depends on MVP. Custom foods, recipes/yields/versions, favorites, saved meals and copy flow in separate tasks. Acceptance: ingredient arithmetic, private ownership, stable history and independent idempotent copies verified.
- [ ] **Stage 9 — Nutrient insights.** Depends on 8 and sufficient licensed nutrient data. Acceptance: data-coverage limitations, preferences/exclusions, calorie context and optional budget respected; no deficiency diagnosis.
- [ ] **Stage 10 — AI assistance.** Depends on reliable MVP, source mapping, explicit processing/privacy/budget approval and provider re-evaluation. Implement adapter/evaluation, then photo review and later text logging as separate tasks. Acceptance: benchmark recorded, uploads cleaned up, estimates editable, no save without confirmation, manual fallback and spend limits tested. Voice/assistant remain optional later tasks.
- [ ] **Stage 11 — Consolidated quality/security.** Depends on selected release scope. Acceptance: automated checks, RLS, dependency review, network failure, accessibility, privacy/retention/delete/export and agreed performance checks recorded; no unresolved critical/high security/data-loss issues. Testing also occurs in all earlier stages.
- [ ] **Stage 12 — Android release preparation.** Depends on 11 plus authorized build configuration. Acceptance: installable APK built and installed on a recorded device/OS, signing/config/secrets reviewed, release procedure and limitations documented. Store publication requires separate approval.

## Exact next implementation task: Stage 2

Create one minimal Expo TypeScript app in `apps/mobile/`, keeping root documentation intact. Use npm and a lockfile; no root workspace tooling, backend, auth, real food dataset or AI. Use one presentational landing screen to demonstrate the theme, not a functional dashboard.

Acceptance criteria:

- [x] Reinspect Git/user changes and read RULES, Memory, Architecture and Design before scaffolding.
- [ ] Recheck official Expo SDK/device compatibility and package Node engines. Record exact Expo, React Native, React, Node and npm versions. Current docs show SDK 58 versus Expo Go SDK 57 transition; choose deliberately.
- [x] Initialize only `apps/mobile/` with TypeScript and strict checking; no nested `.git` repository. Keep a single root Git history and review generated files.
- [x] Add reusable color, typography, spacing and radius tokens; minimal accessible screen shows Bites2Go and one clearly labeled demo action. Respect safe area and font scaling.
- [x] Configure actual npm `lint` and `typecheck` scripts; run them successfully along with Expo Doctor. Record exact commands/output; fix relevant failures.
- [ ] Launch on a recorded Android device or emulator and verify screen, interaction and reload without crash. Expo Go is acceptable for this small first task when SDK-compatible. A web preview alone does not satisfy Android acceptance.
- [x] Add no services, secrets, API calls, paid builds or feature-wide implementation. Do not create external accounts. If no Android device/emulator is available, report Stage 2 incomplete with that exact blocker rather than claiming launch success.
- [x] Update README with working install/run/check commands, chosen launch route, limitations and reproducible setup; update Memory and this checklist with actual evidence.
- [x] Review diff and generated dependency files for secrets/unrelated changes. Follow the user's then-current commit authorization and GitHub workflow; absence of a remote does not justify invented push success.

Android path recommendation: use a physical device with matching Expo Go for Stage 2 if available; otherwise arrange local SDK/emulator setup after agreement. Own development builds and APK signing remain later bounded tasks.

## Stage 2 implementation — 2026-10-30

User approved Stage 2 in the current request. Implemented in `apps/mobile/` (supersedes the earlier `mobile/` proposal). Single empty diary screen, theme tokens, strict TypeScript, safe areas and a clearly labeled placeholder Add Food alert. No real nutrition data or services.

Verified: typecheck, lint, formatting, one AA contrast test, Expo Doctor 21/21, public Expo config and Android Hermes bundle export passed. `npm start -- --localhost` started Metro at port 8081; its status endpoint returned `packager-status:running`. This verifies development-server startup, not on-device rendering. No Android execution: adb/emulator unavailable on PATH, Android SDK variables unset and standard local SDK adb absent. Device layout, TalkBack and font scaling still require manual verification.

Installed: Expo 57.0.31, React Native 0.86.3, React 19.2.3, safe-area-context 5.7.0, TypeScript 6.0.3, ESLint 9.39.5/config-expo 57.0.2, Prettier 3.9.10, Expo Doctor 1.21.5. Node 22.23.2/npm 10.9.8. Lockfile records transitive versions. SDK 57 follows current Expo Go transition guidance: https://docs.expo.dev/get-started/create-a-project/ . No navigation library needed yet.

Known issues: npm audit retains 8 transitive advisories (5 low, 3 high) involving Expo tooling's deepmerge/zod chain after compatible `npm audit fix`; forced remediation proposes incompatible Expo 51 downgrade and was not applied. Resolve/reassess before release. Expo-selected ESLint 9 emits an upstream support warning; retain compatibility pending supported SDK upgrade. The Node contrast test emits a module-type detection warning but passes. No claim of production security readiness.

Next: review Stage 2 and verify the screen on Android before Stage 3. Stage 3 has not begun.

- [x] Mobile foundation and developer checks implemented and verified.
- [ ] Android device launch, layout and interaction verification (tooling/device unavailable).
- [ ] Review unresolved dependency advisories before release.

## SDK 58 compatibility follow-up

- [x] Create codex/expo-sdk-58 from clean master f75c4f3 and align dependencies through Expo.
- [x] Verify types, lint, formatting, contrast test, config, Doctor and Android bundle export.
- [x] Compare fresh audits before/after; unchanged 8 advisories remain documented in Test Plan.
- [x] Update SDK versions and Android LAN preview instructions.
- [ ] User verifies physical Android preview with SDK 58 Expo Go, layout, Add Food alert and reload.
- [ ] Review upgrade branch before any merge; master unchanged. Stage 3 remains deferred.

## Stage 3 implementation checklist

- [x] Branch from verified clean SDK 58 commit 64e5f33.
- [x] Home summary, macros and four meals with labeled demo data and empty states.
- [x] Five Expo Router tabs; sample Diary and explicit unfinished sections.
- [x] Pure preview totals/progress, five passing tests and developer/build checks.
- [x] Fix preview wording and verify UTF-8 source without replacement characters.
- [ ] Physical Android, TalkBack and large-text visual/navigation verification.
- [ ] User review before Stage 4; no merge into master.

## Stage 4 local foundation checklist

- [x] Verify clean approved Stage 3 commit 2e81e27 and create codex/stage-4-food-search.
- [x] Add 12 explicitly illustrative foods with provenance, preparation, per-100 g values and nullable fiber.
- [x] Connect Add Food to local search/detail/portion preview; retain originating meal and draft within flow.
- [x] Verify search/scaling/draft logic with 10 passing tests and types/lint/Doctor/config/Android export.
- [x] Reconcile roadmap and document source/precision/persistence limitations.
- [ ] Verify actual Android keyboard, Back, TalkBack, font scaling and visual layout.
- [ ] User review before Stage 5. Production catalog licensing and backend/auth isolation remain prerequisites to persistent logging.
