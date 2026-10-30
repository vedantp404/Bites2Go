# Test strategy

## Stage 6 verification

31 automated tests pass (0 failed/skipped), including eight new calendar/history tests: month lengths/leap centuries; Monday-first padding/six-week months; month/year limits; selection versus browsing/Today; logged indicators and empty dates; historical save/edit/delete/reload isolation and no navigation storage reads; unknown/partial snapshot totals; local midnight and DST across Kolkata/Los Angeles subprocesses. Tests use existing injected storage and pure logic, not a device or rendered navigation automation.

TypeScript, lint, formatting, Expo Doctor 20/20, public Expo SDK 58 config and Android Hermes export (1324 modules) pass. Initial TypeScript failures were the action union narrowing and React Native ScrollView ref type; both corrected. No scripts or warnings suppressed. Existing Node module-type and Metro color warnings remain.

Fresh audit remains 8 affected packages (5 low, 3 high): deepmerge GHSA-gcqx-w48m-w2h4 and zod GHSA-mrhx-c7xc-m3w5 in Expo tooling. No dependency/lockfile changes or forced fixes.

User reports Stage 5 save/restart/edit/delete verification, not Stage 6. Pending Android: browse February/leap year/December–January, confirm weekday alignment; distinguish today, selected and logged dots; select an empty date and a logged date; add to a historical meal, use Back/cancel, edit then delete its last entry, verify totals and marker removal; return Home (today only), then Calendar (retained selection); browse months without changing the selected diary; Today resets explicitly; close/reopen and confirm existing entries remain intact. Check narrow-screen horizontal grid scrolling, date targets, large fonts, TalkBack labels, auto-scroll to diary, and loading/error behavior. Future dates must explain disabled logging.


## Stage 5 verification

Final code: TypeScript and lint pass; 23 Node tests pass (0 failed/skipped). Formatting, Expo Doctor 20/20, public SDK 58 configuration and Android Hermes export pass. Initial checks found a save handler nested in an effect and React ref/effect lint violations; these were corrected without suppressions. Existing Node module-type and Metro color warnings remain visible.

Thirteen new tests cover missing/empty storage; save and repository recreation; all meals and isolated dates; snapshot totals and null/partial coverage; edit/delete; cancellation with unchanged storage; fixture independence; concurrent saves/double submission; read/write failures with byte preservation; uncertain acknowledgements and idempotent retries; malformed/versioned/duplicate records; stale updates/deletes; leap/month/year/local-midnight/DST and two timezone subprocesses; unknown persistence and aggregate overflow rejection. Storage is an injected memory fake. No native SQLite/device execution or rendered-screen automation is claimed.

Fresh npm audit: unchanged 8 affected packages, 5 low/3 high. deepmerge GHSA-gcqx-w48m-w2h4 and zod GHSA-mrhx-c7xc-m3w5 propagate through Expo tooling. No new advisory reported for SQLite/Crypto. Forced remediation proposes incompatible Expo 51 and was not run. These remain release risks, not waived by a successful bundle.

Required Android acceptance (pending): start SDK 58 Expo Go, open an initially empty diary; save rice 200 g into Lunch, rapidly tap Save, verify exactly one entry and 300 illustrative kcal. Fully close/reopen the app and verify entry/meal/date/values persist. Edit to 100 g, cancel once (no change), then save (150 kcal); close/reopen again. Cancel deletion, then confirm deletion and verify totals only change on success. Repeat across Breakfast/Snacks/Dinner and yesterday, ensure Home shows today only and Diary keeps its chosen date on returning from search/edit. Generic Add Food requires choosing a meal. Verify unknown fiber, empty states, keyboard scrolling, Back, large text, TalkBack and offline use after bundle loading. Do not clear app data to test restart. No claim that prior Stage 4 phone verification covers Stage 5 storage.


## Current Stage 4 status — 2026-10-30

Stage 4 is the user-authorized **offline food-search and portion-preview foundation**, superseding the earlier Stage 4a/4b backend scope. Historical stage notes below are retained as history, not current instructions. No backend/authentication/persistence has been implemented. Stop before Stage 5.

Stage 1 defines tests only. No application tests, lint, type checking or Android execution have run because no application or test runner exists. Documentation checks are recorded in Memory.

## Layers and gates

Use pytest for pure Python calculation/validation tests at Stage 4; React Native Testing Library with an Expo-compatible Jest setup when interactive behavior exists. Share synthetic decimal fixtures across Python, TypeScript previews and SQL snapshot calculations. Use a disposable Supabase test environment for migration/RLS/API integration; do not test against production user data. Evaluate Maestro or manual scripts for Android journeys when screens exist; choose tooling then.

Each task runs relevant focused checks, then configured type/lint checks. GitHub Actions begins only after commands exist. Gate every persistence feature with negative authorization tests, every calculation change with numeric fixtures, and every release with an installed-device smoke run. Record actual commands, versions and results; deferred checks remain explicitly unverified.

## Scenario matrix

| Area | Required cases and pass condition |
| --- | --- |
| Quantity arithmetic | Synthetic 100 kcal, 10 g protein per 100 g at 150 g yields 150 kcal and 15 g protein. These are test fixtures, not real food claims. Zero/negative/NaN/infinity/overflow rejected for log quantities. |
| Precision | Fractional grams, repeated additions, half-up boundary, large allowed input, decimal-string serialization; sum raw values before rounding; Python/mobile/SQL agree within specified persistence precision. |
| Energy | Reported kcal preserved despite macro-derived mismatch; kJ / 4.184 conversion flagged; unknown energy stays unknown; no automatic 4/4/9 substitution. |
| Serving conversion | Two synthetic 30 g servings become 60 g; food-specific conversion required; missing/zero/negative conversion rejected; changing food cannot reuse another food's serving. |
| Food variants/import | Raw/cooked rice and added-fat roti/dal distinct; ingredient versus mixed dish distinguishable; repeated imports idempotent; invalid units, duplicate nutrient codes and incompatible carb basis quarantined. |
| Missingness | Explicit zero differs from absent. Mixed known/missing produces partial subtotal and counts; all-missing unknown; no entries has no-entries status; goals/insights cannot claim success from incomplete data. |
| Diary totals | Four meals, edit, delete last entry, retry save, restart/refetch; total equals authoritative snapshots and selected day only. |
| History | Catalog and recipe revision do not change saved history; quantity edit uses original version; selecting a newer version is explicit. Past-date corrections recalculate only affected results. |
| Dates/calendar | Asia/Kolkata midnight, another timezone, DST zones, travel, month/year/leap-day transitions; local date survives UTC serialization and profile timezone change. No future dates initially. |
| Goals | Effective-date selection, unset/zero/no division, negative invalid, over-target signed remainder, boundaries ±10% energy, exact minimum macros, incomplete day and no enabled goals. Past targets remain stable. |
| BMI | Synthetic 70 kg and 1.75 m yields about 22.86; cm conversion explicit; zero/nonfinite invalid; limitations visible, no diagnosis. |
| Weight | Gain/loss/equal start-target/overshoot, one record per date, edit/delete, missing days, available-only weekly mean and count; chart does not interpolate absent records. |
| Streaks | Logged versus explicitly complete versus achieved; gap, today pending, backfill, delete, timezone change and goal edit; logging and goal streaks remain separate. |
| Achievements | First action and weekly criteria awarded once per rule/key; correction revokes invalid evidence; repeated saves do not multiply awards. |
| Auth | Sign-in/out, expired/forged/wrong-issuer/wrong-audience tokens, key rotation, refresh failure, secure-session persistence and removal of private cached data at logout. |
| Isolation | User A cannot read/write/delete B's rows via API, direct Data API, RPC, guessed IDs, nested parents or custom-food versions. Anonymous denied. Owner spoofing and fabricated nutrition snapshots rejected. Test SELECT/INSERT/UPDATE/DELETE and grants with real user JWTs, never only service role. |
| Persistence | Restart and second client observe committed data; transaction rollback leaves no partial day/entries; repeated idempotency key returns prior result; changed payload conflicts; stale edit version conflicts; migration fresh/upgrade and restore rehearsed. |
| Custom foods | Owner-only, finite units/reference basis validation, label provenance, revision leaves logs unchanged. |
| Recipes | Ingredient sum, water/oil, grams/yield, serving count, zero/missing yield, partial nutrients, inaccessible ingredients, revision and nested-cycle denial; per-serving and per-weight arithmetic correct. |
| Saved meals | Favorite uniqueness, multi-item atomic copy, correct destination date, independent edits and retries without duplicates. |
| Insights | Complete versus sparse micronutrients, preference/exclusion filters, no affordable candidate, no remaining calories, no clinical deficiency wording. |
| AI | Mock provider contract, schema errors, invented IDs, unknown grams, hidden oil, wrong matches, cancel/review/edit/confirm, timeout/429/5xx/budget cutoff; zero diary writes before confirmation; manual path works when disabled. |
| Upload/privacy | Spoofed MIME, malformed/polyglot, oversized bytes and dimensions, EXIF, HEIC conversion need, unauthorized upload, temp cleanup on success/error/cancel/crash sweep; no photo/prompt in logs or public storage. |
| Android/UI | Cold start, all available navigation, keyboard, date/quantity input, Back button, rotation behavior, small/large screens, TalkBack, large font, offline retry and slow network. |
| Builds | Chosen SDK passes Expo Doctor, type and lint scripts; Android smoke evidence records model/OS; later development APK and release APK install/launch, signing/secrets review, clean build reproducibility. An AAB alone is not an installation test. |

## Release evidence

Maintain a short checklist of tested commit, device/OS, backend schema version, commands, failures and exceptions in Memory or release notes. No real diaries/photos in public test reports. Stage 11 blocks release on unresolved critical/high security or data-loss defects; Stage 12 verifies installation and release configuration after fixes.

## Stage 2 implementation — 2026-10-30

User approved Stage 2 in the current request. Implemented in `apps/mobile/` (supersedes the earlier `mobile/` proposal). Single empty diary screen, theme tokens, strict TypeScript, safe areas and a clearly labeled placeholder Add Food alert. No real nutrition data or services.

Verified: typecheck, lint, formatting, one AA contrast test, Expo Doctor 21/21, public Expo config and Android Hermes bundle export passed. `npm start -- --localhost` started Metro at port 8081; its status endpoint returned `packager-status:running`. This verifies development-server startup, not on-device rendering. No Android execution: adb/emulator unavailable on PATH, Android SDK variables unset and standard local SDK adb absent. Device layout, TalkBack and font scaling still require manual verification.

Installed: Expo 57.0.31, React Native 0.86.3, React 19.2.3, safe-area-context 5.7.0, TypeScript 6.0.3, ESLint 9.39.5/config-expo 57.0.2, Prettier 3.9.10, Expo Doctor 1.21.5. Node 22.23.2/npm 10.9.8. Lockfile records transitive versions. SDK 57 follows current Expo Go transition guidance: https://docs.expo.dev/get-started/create-a-project/ . No navigation library needed yet.

Known issues: npm audit retains 8 transitive advisories (5 low, 3 high) involving Expo tooling's deepmerge/zod chain after compatible `npm audit fix`; forced remediation proposes incompatible Expo 51 downgrade and was not applied. Resolve/reassess before release. Expo-selected ESLint 9 emits an upstream support warning; retain compatibility pending supported SDK upgrade. The Node contrast test emits a module-type detection warning but passes. No claim of production security readiness.

Next: review Stage 2 and verify the screen on Android before Stage 3. Stage 3 has not begun.

## SDK 58 verification — 2026-10-30

Branch `codex/expo-sdk-58`, based on master f75c4f3. Installed Expo 58.0.21, React Native 0.88.1, React 19.3.0, TypeScript 6.0.3. Expo-selected @types/react 19.3.0, eslint-config-expo 58.0.4, expo-status-bar 58.0.4 and safe-area-context 5.10.1. No changes to application features.

| Check | Result |
| --- | --- |
| `npm run typecheck` | Passed |
| `npm run lint` | Passed |
| `npm run format:check` | Initially failed on Expo-generated app.json formatting; targeted Prettier formatting fixed it; rerun passed |
| `npm test` | 1 passed, 0 failed (AA contrast) |
| `npx expo-doctor` | 20/20 passed |
| `npx expo config --type public` | Passed, SDK 58.0.0 |
| `npx expo export --platform android` | Passed, Android Hermes bundle exported; not an APK/device test |
| Manifest/lockfile comparison and `npm ls --depth=0` | Dependency ranges agree; installed tree valid |
| `npm audit` before and after | Both report 8 affected packages: 5 low, 3 high; audit is not clean |

Unchanged root advisories: deepmerge prototype poisoning (GHSA-gcqx-w48m-w2h4) and zod oversized-collection memory exhaustion (GHSA-mrhx-c7xc-m3w5), propagated through Expo config/CLI tooling. No newly reported advisory compared with the immediate pre-upgrade baseline. These remain release risks; a passing bundle does not establish security. No forced remediation applied.

Existing Node module-type detection warning in the contrast test and NO_COLOR/FORCE_COLOR warnings during bundling remain visible; they were not suppressed. Physical Android execution, layout and interaction verification remain pending the user's SDK 58 Expo Go test. No Stage 3 work or merge into master.

## Stage 3 dashboard — 2026-10-30

Stage 3 results: typecheck, lint, formatting, Expo Doctor 20/20, configuration validation and Android export pass. Five node tests pass: meal aggregation/empty totals; progress and over-target clamping; zero/invalid targets; invalid intake; AA text contrast. Initial JSX apostrophe lint error was corrected, then formatting reapplied. UTF-8 scan of app/src files finds no U+FFFD replacement characters; the old preview sentence was replaced with ASCII punctuation. npm install reports the existing eight advisories; no forced fix applied. Node module-type and bundler color warnings remain unsuppressed. Physical-device preview, TalkBack, font scaling, navigation/back behavior and visual layout remain manual checks, not verified results.

## Reference-inspired UI refinement

User supplied a nutrition-app visual reference. Adapted Home with a forest-green fading header, centered identity/date, calorie progress ring, compact colored macro bars, pill action and rounded meal rows. Diary shares meal-card styling; tabs now have consistent SVG line icons. Demo labeling remains visible and calculations/features are unchanged. No invented nutrition score, history chart or food-search feature was added.

Added Expo-compatible SVG/linear-gradient modules. Installation exposed an existing react-dom 19.3.1 peer mismatch with React 19.3.0; `expo install react-dom` aligned it to the SDK-compatible version without force/legacy flags. Initial refactor syntax and strict icon-color typing failures were fixed; types, lint, formatting, five tests, Doctor 20/20 and Android export passed. Existing eight audit advisories remain. Visual fidelity, physical Android rendering, large text and TalkBack remain unverified and require phone review.

## Stage 4 results and manual acceptance

Passed: `npm run typecheck`; `npm run lint`; `npm test` (10 passed, 0 failed, 0 skipped); `npx expo-doctor` (20/20); `npx expo config --type public` (SDK 58); `npx expo export --platform android` (1274 modules, Hermes bundle). Formatting initially flagged mobile AGENTS.md; corrected and rerun passed. Existing Node module-type and Metro color warnings remain visible. A file-writing attempt used a duplicated relative path and failed before writing; corrected paths were used. No failed application tests. Diff review caught documentation encoding changes from the Windows default codec; original Unicode characters were restored with explicit UTF-8.

Five added tests cover exact/partial/alias/case/blank/no-match/deduplicated search; catalog identities/provenance/raw-cooked distinction; integer/fractional/boundary scaling and null/zero/display rounding; invalid/nonfinite/overflow/underflow inputs; meal allowlist and draft back/reselect/reset/confirm logic. These are pure Node tests, not rendered UI or Android automation.

Fresh `npm audit`: exit 1, unchanged 8 affected packages (5 low, 3 high), deepmerge GHSA-gcqx-w48m-w2h4 and zod GHSA-mrhx-c7xc-m3w5 through Expo tooling. No packages/lockfile changed; no forced fix, overrides or warning suppression. Audit's forced remedy still proposes incompatible Expo 51.

Pending physical Android: open from all four meal sections on Home and Diary, verify correct meal; generic Add Food must not invent a meal. Search rice/CHAPATI/dahi, blank and nonsense; clear query. Select cooked versus raw rice, compare reference and 200/12.5 g preview; enter blank/0/negative/invalid/very large values, verify confirmation disabled and unknown fiber. Confirm must say preview with unchanged dashboard totals. Detail Back (button and Android Back) retains query/grams and Review current selection; exit returns to originating tab. Test keyboard with portion input/confirm visible via scrolling, small screen, large fonts, TalkBack labels/focus and all five tabs. Airplane-mode local search should work after app bundle is loaded. No actual device/emulator verification performed.

## Master integration validation

TypeScript, lint, all 10 automated tests, Expo Doctor (20/20), public Expo configuration and Android Hermes export passed on the integrated application. Formatting initially failed because core.autocrlf=true converted checkout text to CRLF. Verified normalized content matched committed source; added .gitattributes for LF mobile text and normalized working files. Formatting rerun passed. No application logic or dependency versions changed beyond the existing feature commits.

Fresh npm audit still exits 1 with 8 affected packages (5 low, 3 high): deepmerge GHSA-gcqx-w48m-w2h4 and zod GHSA-mrhx-c7xc-m3w5 through Expo tooling. No forced fixes applied. Existing Node module-type and Metro color warnings remain visible. User reports Stage 4 phone verification; agent did not run a device test. Commit/push outcomes are verified and reported in the completion message; no self-referential follow-up commit is required.
