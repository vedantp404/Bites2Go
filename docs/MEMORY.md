# Project memory

## Current handoff: Nutrition Data Quality & Staple Foods Provenance

Audited all 1,411 searchable foods in Bites2Go's unified catalogue (894 built-in foods in `apps/mobile/src/data/foods.ts` and 517 Kaggle dataset foods in `apps/mobile/src/data/kaggleFoods.ts`) to improve nutritional data quality, eliminate synthetic values for core staples, and establish rigorous provenance tracking.

Key Achievements:

- Audited 1,411 Unified Foods: Comprehensive evaluation of macronutrient density, energy density, and Atwater factor bounds (4P + 4C + 9F ~= kcal). Documented known variance factors including dietary fiber subtractions in chia/flax seeds and standard alcohol conversions.
- Upgraded 68 High-Priority Staples: Enhanced 68 essential foods across 7 categories:
  - Breads & Grains (12): Basmati rice, white bread, whole wheat bread, sourdough, phulka, tandoori roti, plain naan, butter naan, plain paratha, aloo paratha, paneer paratha, bhatura.
  - Dairy & Cheese (10): Cheddar, mozzarella, parmesan, feta, creamed cottage cheese, skimmed cow milk, plain Greek yogurt, desi ghee, salted butter, buttermilk/chaas.
  - Pulses & Legumes (6): Cooked urad dal, panchmel dal, dal fry, dal makhani, sambar, lobia curry.
  - Nuts & Seeds (7): Creamy peanut butter, shelled walnuts, raw cashews, roasted peanuts, shelled pistachios, chia seeds, flax seeds.
  - Produce & Fruits (13): Green grapes, fresh strawberries, fresh blueberries, raw avocado, muskmelon, steamed broccoli, green capsicum, boiled green peas, raw ginger, raw garlic, raw lemon, raw cabbage, boiled sweet potato.
  - Meats, Fish & Eggs (10): Grilled chicken breast, grilled chicken thigh, grilled salmon, canned tuna in water, scrambled egg, fried egg, poached egg, masala omelette, Goan fish curry, mutton curry.
  - Indian Breakfast & Snacks (10): Medu vada, khaman dhokla, semiya upma, poha chivda, Mumbai bhel puri, pani puri / golgappa, pav bhaji, chicken biryani, vegetable biryani, misal pav curry.
- Provenance Status Transformation:
  - Total Verified: 78 items (up from 36 baseline; +42 items with explicit USDA FDC ID or ICMR-NIN IFCT 2017 code).
  - Total Estimated: 40 items (up from 14 baseline; +26 items with documented composite IFCT recipe formulations).
  - Total Illustrative: 1,293 items (down from 1,361; preserved for synthetic Kaggle records and unverified fixtures).
- Strict Baseline Invariance Preserved: Items 0–11 (`rice-cooked`, `rice-raw`, `roti`, `moong`, `chickpeas`, `milk`, `curd`, `banana`, `apple`, `almonds`, `oats`, `paneer`) were maintained to protect existing calendar, diary, and library test fixtures. Specifically, `rice-cooked` retains its legacy 150 kcal baseline and undefined `servingGrams`, while `rice-basmati-cooked` provides the authoritative 130 kcal USDA composition.
- Automated Testing & Verification: All 150 mobile tests passed (including updated `nutritionAccuracy.test.mjs`), 19 backend tests passed, TypeScript, ESLint, Prettier, Expo doctor (20/20 passed), Android release export succeeded, and secret scan verified 0 pattern findings.
- Comprehensive Documentation: Full audit report, category breakdown, and formulation tables published in `docs/NUTRITION_DATA_QUALITY_REPORT.md`.

## Current handoff: Kaggle Dataset Integration (`adilshamim8/daily-food-and-nutrition-dataset`)

Integrated the Kaggle daily food and nutrition dataset (v2) by Adil Shamim into Bites2Go's food search system without corrupting nutrition models or breaking existing search performance:

- Schema & Provenance: The dataset contains 651 raw records with synthetic dietary records. All imported records are strictly assigned `status: 'illustrative'` (never verified) with explicit source attribution to Adil Shamim v2.
- Preprocessing Pipeline (`scripts/import_kaggle_dataset.py`): Normalizes portions to per-100g reference values, enforces physical laws (macronutrient density <= 100.5g/100g, calorie density <= 900 kcal/100g), quarantines physically impossible items (Line 486 Corn Nuts, 102.1g/100g), and merges 58 internal duplicates to produce 592 unique items.
- Conservative Deduplication: 75 certain matches with existing built-in foods were merged preserving original stable IDs (`apple`, `banana`, `almonds`, `rice-brown-cooked`), 40 meaningfully different varieties were kept separate (e.g. 2% milk vs whole milk, steamed vs roasted), and 35 ambiguous matches with >35% calorie variance were kept separate.
- Catalogue Integration: Exported 517 new foods prefixed with `kaggle:` into `kaggleFoods.ts`, creating a 1411-food `unifiedFoods.ts` catalogue. Built-in `foods.ts` invariant remains at 894 items, preserving all baseline test fixtures.
- Dataset-First Ranking: `searchFoods` in `food.ts` applies tier bonuses (Tier 1 Kaggle +0.4, Tier 2 Built-in +0.2, Tier 3 Custom/Recipe +0.0), guaranteeing that Kaggle items rank first for equal relevance matches while built-in and custom foods remain discoverable.
- Stability & Quality: Preserved module-scope memoized `SearchHeader` in `FoodSearchScreen.tsx` preventing Android keyboard focus blur. All 149 mobile tests pass (including 10 new tests in `kaggleSearch.test.mjs`).

## Current handoff: Expanded Food Catalogue & Food Images

Expanded the built-in food catalogue to 894 unique, production-grade food entries covering diverse Indian staples, regional Maharashtrian cuisine, South Indian breakfast, dals, sabzis, street food, snacks, traditional mithai, international fruits, vegetables, healthy fitness foods, proteins, dairy, grains, fast food, and beverages. Baseline items 0-11 were strictly preserved to guarantee zero regressions for existing library, diary, and calendar test suites.

Added 32 optimized CC0/Public Domain/CC-BY food photo thumbnails (~400 KB total) with complete license documentation in `apps/mobile/assets/food/README.md`. Upgraded the food image system (`foodImages.ts` and `FoodImage.tsx`) with 34 bundled photographic assets and category-specific SVG fallback badges (`bowl`, `cup`, `bread`, `dairy`, `meat`, `fruit`, `leaf`, `snack`) for items without photos.

Implemented scored search ranking in `food.ts` (exact name 1000, exact alias 950, prefix 800-850, word prefix 700, substring 500-600, multi-word token matching). Search results (`FoodChoice`) now show thumbnails, short serving descriptions, calories, and macro breakdown. Food detail (`FoodSearchScreen.tsx`) provides interactive portion chips for common servings with live recalculation. Implemented idempotent SQLite catalogue repository (`catalogRepository.ts`) managing `bites2go.catalog.v1` metadata without altering custom foods, recipes, or immutable diary snapshots.

Validation: 119 mobile tests passed (including new `catalog.test.mjs`), 19 backend tests passed, TypeScript, ESLint, Prettier, Expo doctor (20/20 passed), Android release export bundled (3.3MB JS bundle + 34 food photo assets), and security scan passed with 0 findings.

## Current handoff: My Meals & Recipes

Explicit user request authorizes this focused feature after Stage11, working on clean master 1088789808dd7777c3739058cf30f3ca80630e83. Reused existing Recipe/Library v1 SQLite and diary snapshot pipeline; no migration or new model. MyFoods now separates My Meals and custom foods, shows ingredients/whole/per-serving nutrition, and provides Log Meal plus edit/delete. Profile/Add Food entry labels updated. Recipe editor reused; defaultFoodPortion shares one-serving recipe defaults between draft reducer and logging screen, while other foods remain 100 g. Same-item reselection preserves edits. Fractional/multiple servings log one combined entry; history/insights stay snapshot-based and unknowns remain null.

Baseline 96 tests; focused 22 tests passed; final 98 tests, types/lint/format, Doctor 20/20, public config and Android export passed. Extended real SQLite close/reopen multi-ingredient/1.5-serving test plus retry, source edit/delete, calendar/insights and 0.5/2-serving integration coverage. Audit FAILS exit 1 unchanged 3 high / 5 low; no dependency/lockfile or cloud changes. No physical Android/emulator, signed install or live-backend test performed. Native acceptance remains in Test Plan. Commit/push outcome and hashes reported after verification; stop without AI food recognition or other features.

## Current handoff: Stage 11 final development acceptance

User explicitly authorizes direct master commit/push after all development criteria pass, with the unchanged investigated audit excepted only for development. This supersedes earlier no-commit notes in historical entries. Fresh 96 tests, types/lint/format, Doctor20/20, config, Android export, isolated PostgreSQL and scoped credential scan pass; audit still FAILS exit1 with identical 3 high/5 low rows. No dependencies/schema changes, no known new regression in review. Production remains blocked pending remediation/formal security decision plus native/privacy release gates.

Reviewed all intended Stage 11 files from baseline369d562b7bfeee014810d9236f1097bef2d2ce85; no unexpected user work. All prior implementation preserved. No specific Stage 11 device acceptance reported; regular user Android testing and prior Stage4/5 reports do not establish it. No Codex device/emulator, signed build/install or live Supabase tests; cloud stays disabled. See RELEASE_READINESS.md for final evidence. Commit/push and exact hashes are reported only after Git verifies them; do not create a follow-up commit solely to record its own hash. Stop here, no new feature authorized.

## Historical handoff: Stage 11 initial blocked release gate (superseded below by final acceptance)

Authorized Stage 11 supersedes earlier stop-before-11 notes. Started clean master/fetched origin 369d562b7bfeee014810d9236f1097bef2d2ce85. Baseline 93 tests pass; final 96 pass. Types/lint/format, Doctor 20/20, public config, final Android export and isolated PostgreSQL policies pass. Initial lint failure was fixed, not suppressed. No device/emulator or hosted Supabase tested.

Local changes reconcile diary display on exit after uncertain save/edit/delete, group diary validation by date, reject checkpoint rollback/removal and remove raw splash error logging. Existing theme contrast coverage expanded; scoped current/history/export credential scanner added (zero patterns). No dependencies/schema/cloud changes. All 3 high and 5 low audit rows remain: Zod 3.25.76 requires breaking major upgrade unsupported by current Expo CLI; deepmerge 4.3.1 has no patched release. Export source map has neither module, but tooling risks remain. See RELEASE_READINESS.md for exact paths, advisories and reproduction.

User conditions commit/push on all required checks passing: no Stage 11 commit or push; changes intentionally remain in working tree on master. Preserve them on resume. Do not claim release-ready, enable cloud or begin another stage. Android/native, privacy and signed-build acceptance remain pending.

## Current handoff: Stage 10 Nutrition Insights

Started from clean verified master/origin 703b25ae1c5a726491d880f4955de2944ece3475; baseline 79 tests passed. Explicit Stage 10 nutrition-insights request supersedes older Stage 10 AI plans. Implemented read-only Insights stack route from Progress using existing diary/health providers and shared totals, local dates, historical targets and weight logic. 7/30-day rolling windows include today; custom ranges are 1–92 days, no future dates. Existing five tabs remain.

No completion flag exists. Eligibility proxy requires a past day with all four meal sections and known values for that nutrient. Today/absent/limited-meal/unknown-nutrient days are excluded from averages, plotted intake and target consistency with explicit counts and caveats. Daily known subtotals remain visible without incomplete percentages. Calorie/protein comparison uses inclusive 90–110% of each historical positive target. Weight points are actual in-range records; current goal shown only when its date permits, with no historical goal invention or prediction. Details in INSIGHTS.md.

Final 93 tests pass (14 new), plus types/lint/format, Doctor 20/20, public config, Android export and existing isolated PostgreSQL integration check. Audit unchanged 5 low/3 high. No dependencies/schema changes/storage writes/cloud activation; source-food changes cannot alter insights from diary snapshots. Native Android rendering, interaction, TalkBack and themes were not tested; checklist remains pending. Pure UI view-state/label tests are not rendered-device tests. Final commit/remote hash reported after push verification. Stop after Stage 10; recommend Stage 11 quality/security only after user acceptance and authorization.

## Current handoff: Stage 9 tested integration boundary

Started from clean master/origin at 6f6794add78f9017089a9f100baaaee9e0b48c53 in C:\Users\Asus\Music\Bites2Go. User authorizes Stage 9 and direct master push, superseding earlier stop-before-9 notes. No backend URL/public key exists in repo env files or process configuration. No external account/service/deployment was created and no local personal data was accessed/uploaded. Selected Supabase after current official comparison in BACKEND.md.

Delivered the brief's no-configuration fallback: Profile offline status and public-config validator; pure diary-only account-consented sync plan/guarded merge/injected upload interface; isolated optional checkpoint repository; PostgreSQL RLS/CAS migration and tests. The app does not mount a sync worker/checkpoint or SDK, and configuration alone cannot enable cloud. Existing SQLite providers and diary/health/library/appearance schemas remain unchanged. No new dependencies. Auth screens/secure session persistence/live transport/consent-conflict UI/local transactional coordinator remain required before any uploads; no realtime sync.

79 automated tests pass, including mocked transport/session gating and real SQLite preservation. Actual migration/policies passed in disposable PostgreSQL 18 using synthetic auth roles/identities; server stopped and temp data removed. Types, lint, format, Doctor 20/20, public config and Android export pass. Audit unchanged 5 low/3 high. Supabase Auth/PostgREST/email/gateway and physical Android checks were not run. BACKEND.md documents exact setup/remaining implementation, account binding, tombstones, conflict semantics, SQL payload-validation limits, export/deletion and secure storage requirements. Final commit/remote hash reported after verification. Stop after Stage 9 and await review; no Stage 10.

## Current handoff: Stage 8

Started from clean master and fetched origin/master both at e0c0ffee137392ae893b95da5375d3fedbbc3525 in C:\Users\Asus\Music\Bites2Go. Stage 8 supersedes earlier stop-before-8 notes. Added custom-food CRUD, recipe builder from ingredient snapshots, favourites, real diary-derived recents, and grams/defined-serving quick-add. New MyFoods/CustomFood/Recipe routes reuse existing theme, images and controls; five tabs retained. No dependencies or Stage 9 work.

Separate `bites2go.library.v1` uses the existing parameterized SQLite KV adapter. Absent key loads empty without touching existing diary/health/appearance; no new SQL table/field migration. Source deletion and favourite cleanup are atomic in one document. Validation precedes serialization; corrupt/unsupported data blocks mutation. Serialized compare-before-write operations and retained pending payloads support safe retries. Recipe ingredient snapshots survive source edits/deletion; confirmed diary snapshots remain unchanged. Recents use actual entry creation times and currently available IDs, never synthetic history.

Shared scaling/aggregation handles final measured recipe yield and servings; incomplete nutrient subtotals are disclosed and affected per-serving/per-100-g values remain null for logging. Built-in values remain illustrative and custom/recipe values labelled estimates. Gram units only, no nested recipes or guessed cooking changes. See Architecture for limits and Test Plan for acceptance scenarios.

66 automated tests including actual temporary SQLite close/reopen, types, lint, formatting, Doctor 20/20, public config and Android export passed. Audit unchanged: 5 low/3 high, no forced fixes. No physical device/emulator, native SQLite bridge, rendered theme or TalkBack verification performed. Existing user-reported Stage 5 acceptance does not establish Stage 8 acceptance. Final commit and verified remote hash are reported after push; stop and await review before Stage 9.

## Current handoff: Stage 7

Verified clean synchronized master at 2214b4861f0522be4f1c806d384f112d49008a99. Stage 7 is explicitly authorized and supersedes earlier stop-before-7 notes. Implemented dated weight CRUD/history/chart, effective-dated calorie/protein/carbs/fat goals, canonical cm height, numeric adult BMI and gain/loss/maintenance weight targets. Five tabs retained; new weight-entry and goals stack routes. No Stage 8 or new dependencies.

Separate `bites2go.health.v1` SQLite KV document initializes empty only when absent; no diary/appearance migration or overwrite. Numeric validation precedes JSON serialization; corrupt/unsupported documents block mutation without clearing data. Existing parameterized Expo KV writes are serialized and compared with original snapshots; uncertain writes retain payload for idempotent retry. No user data was accessed/reset.

Personal targets begin unset, not copied from preview fixtures. Goal revisions preserve earlier dates. Weight target starting points are explicit snapshots, retained after record edit/deletion; changed target resets baseline. BMI is one decimal, 20+ adult scope, no category/diagnosis. SVG plots actual records only with date-proportional spacing. Limits and migration notes are documented in PRD/Architecture.

51 tests, types, lint, format, Doctor 20/20, public config and Android export pass during implementation. Includes real temporary SQLite close/reopen testing, not Android bridge/device acceptance. Audit remains 5 low/3 high, no forced fixes. Native UI, restart, theme/TalkBack and diary regressions remain on the user's Android checklist. Stop after Stage 7 and await review before Stage 8; final commit/remote hashes are reported after verified push.

## Current handoff: visual redesign and themes

Started from clean master at verified Stage 6 commit 1f61e752422f2c13b251d05ff24326caaa360d44. Implemented the Vibrant Food App direction and Light/Dark/System throughout the app, with Profile appearance controls. Existing diary schema, snapshots, nutrient values, CRUD repository, date logic and future-date restriction are preserved. Progress remains unfinished; no Stage 7 work.

Preference defaults to System and uses separate SQLite key `bites2go.appearance.v1`. The pure store updates subscribers immediately, preserves failed-write session selection, exposes retryable errors, and never resets diary data. Root waits for theme read before mounting. Expo native modules support automatic Android appearance, system buttons and splash hold; a rebuilt native client is required to exercise config-plugin changes outside Expo Go.

Two local CC0 photographs (apple and banana) total about 228 KB with source/license records beside assets. Image matching uses stable IDs, not names; unknown/historical null IDs and failed loads render placeholders.

37 tests, TypeScript, lint, formatting, Doctor 20/20, public config and Android export passed, including native config introspection after splash configuration. Audit remains 5 low/3 high in Expo tooling, without forced upgrades. No device testing claimed. User must review visual/large-text/TalkBack behavior, theme persistence/system switching, native startup/system bars, and diary/calendar regression flows. Stop here before Stage 7. Final commit and verified remote hash are reported after push, not via a self-referential documentation commit.

## Current handoff: Stage 6

Started from clean synchronized master 5a9f96b. User confirms Stage 5 save/restart/edit/delete worked on Android. Implemented monthly Calendar and inline historical diary, Today and adjacent-day navigation, actual-entry dots/counts, selected outline, accessible date labels and date-index reuse. Home remains current-day-only. Existing SQLite v1 schema/storage operations and food snapshots are unchanged; no migration or new dependencies.

31 tests, types, lint, formatting, Doctor 20/20, public config and Android export pass. Test Plan records initial type fixes and unchanged audit findings (5 low/3 high). User data was not accessed, copied or reset. Stage 6 physical-device layout/navigation/accessibility remains unverified. History is still loaded as a single document at startup/write; calendar navigation reuses a memoized index.

Exact next step: user runs the Stage 6 Android checklist and reviews the result. Only after acceptance and explicit authorization, consider Stage 7 weight/goals/BMI under the roadmap. No Stage 7 code. Actual commit/push hashes are reported in completion output after verification.

## Current handoff: Stage 5 local diary

Work started from clean synchronized master 412625c; direct-to-master policy remains. User explicitly approved local persistence instead of the earlier Auth/cloud roadmap. Implemented save/reload, meal selection, date navigation, real-entry-only Home/Diary totals, detached portion editing and confirmed deletion. Expo selected expo-sqlite 58.0.14 and expo-crypto 58.0.7; existing Expo/RN/React/TypeScript versions remain unchanged. Source nutrition and targets remain illustrative, not production guidance.

Repository validation preserves malformed/unsupported data and blocks writes; no reset, telemetry or cloud service. Persisted source snapshots keep history independent of fixtures. 23 tests, typecheck, lint, formatting, Doctor 20/20, public config and Android export pass; Test Plan records initial failures/fixes and unchanged 8 audit findings. Device restart/native-storage/visual acceptance is still pending; Stage 4 user-reported phone verification is not Stage 5 evidence.

Next: user executes the Stage 5 Android checklist and reviews local data/privacy limitations. Stop; do not start Stage 6. After acceptance and explicit authorization, minimal calendar/history is the recommended next stage. No branch/PR or automatic cloud/auth setup. Completion message records actual commit/push hashes after remote verification; no self-referential follow-up commit.

## Current workflow and integration

Direct-to-master development is now the default under AGENTS and RULES; earlier branch-only/no-merge instructions are historical. The fetched remote master at 845b953 already contained SDK 58 (64e5f33) and the first dashboard (2c548e2). Integration preserves that merge and adds the dependent visual refinement (2e81e27) and local food search (b9f76f3) without cherry-picking or duplicating commits. The merge was conflict-free and its application tree matched the Stage 4 branch.

The user reports manually verifying Stage 4 on an Android phone. This is user-reported acceptance, not a new agent-run device test; device/OS and individual accessibility scenarios were not supplied. No next development stage is authorized. Wait for the next explicit instruction.

## Current Stage 4 status — 2026-10-30

Stage 4 is the user-authorized **offline food-search and portion-preview foundation**, superseding the earlier Stage 4a/4b backend scope. Historical stage notes below are retained as history, not current instructions. No backend/authentication/persistence has been implemented. Stop before Stage 5.

Updated: 2026-10-30, Asia/Calcutta. Stage 2 implemented; Android verification and user review pending. Current root: C:\Users\Asus\Music\Bites2Go. Current branch codex/expo-sdk-58 (SDK 58); master preserved at f75c4f3. Remote https://github.com/vedantp404/Bites2Go.git. Foundation commit 458c3c1. Read the Stage 2 section below for current results; preceding Stage 1 observations are historical.

## Verified workspace inspection

- Root: `C:\Users\Asus\OneDrive\Documents\ChatGPT\bites2go`.
- Full initial workspace listing contained only `.git` and its metadata/sample hooks. No source, dependencies, configuration, documentation or pre-existing uncommitted project files. Root is already the Git top-level; no nested repository initialized.
- Initial `git status --short --branch`: no commits yet on `master`; `git log` reports unborn branch. `git remote -v`: no output/remotes. Git 2.55.0.windows.3.
- Git author name/email configuration is accessible and nonempty; account ownership and GitHub attribution were not verified. Personal email is intentionally not copied into this public-facing document.
- `gh` missing on PATH; attempted `gh auth status` could not execute. No other GitHub authentication test or remote access was performed. No remote added, branch renamed, commit made or push attempted.
- Node v22.23.2, npm 10.9.8, Python 3.13.13 and Java 21.0.8 are executable. Java printed shared archive warnings and a VM build-version difference; no Android/Gradle compatibility check exists yet.
- `adb`, `emulator`, `eas`, `supabase`, `docker` and `gh` unavailable on PATH. This does not establish whether a GUI app or tool exists elsewhere. `JAVA_HOME` points to JDK 21; `ANDROID_HOME` and `ANDROID_SDK_ROOT` were unset. No connected-device or emulator test performed.
- Parent directories checked for AGENTS.md at ChatGPT, Documents and user home contained none. Root AGENTS.md was created as a short entrypoint to RULES and status.

## Completed milestone and current task

Created the seven required docs (PRD, Architecture, Design, Test Plan, Security, Decisions, Memory), root RULES/TASKS/README/.env.example/.gitignore, plus AGENTS.md and dedicated Research/GitHub Workflow docs. Researched official food-data rights, AI capabilities/pricing/privacy, Supabase, Expo/EAS and preview hosting. No application code or datasets were imported.

Important decisions: manual-first; source-based deterministic calculations; immutable food versions and diary snapshots; effective-dated goals; explicit local dates; server authorization and RLS; no photo retention by default; AI provider undecided pending evaluation. Read Decisions for confirmed versus provisional status.

## Known issues and unresolved choices

IFCT electronic product rights require written permission; Indian prepared-food coverage is not yet validated. SDK transition and local Android runtime compatibility need verification. No remote or CLI authentication, app license, service accounts, backend packages, deployment or test runners configured. Supabase write-function privilege design requires integration proof before private logging. Monitoring price retrieval failed; no monitoring price is claimed. Full offline sync is deferred, not promised.

## Latest validation

Stage 1 validation passed: 15 required/foundation files present, 17 local Markdown links resolve, Markdown code fences balanced, no trailing whitespace, all environment placeholders empty, and 19 Git ignore probes behave as expected (12 secret/cache/build/data paths excluded; seven source/example/migration/test/lockfile paths retained). Requirements, roadmap dependencies, MVP boundaries and provisional decisions were reviewed for consistency. `git diff --check` returned success but has no tracked diff on this unborn repository; the separate Python checks inspected every new file. Final status confirms only the new foundation files are untracked and no remotes exist. No application tests, lint/type checks, API inference or Android build/run can be reported; no application exists.

Last meaningful commit: none (unborn `master`). Stage 1 changes remain untracked/uncommitted; nothing pushed.

## Exact next step

Wait for the user's approval of Stage 1. Then execute only the Stage 2 minimal Expo task in TASKS, first rechecking SDK/device support and Git state. No credentials or paid resources are required to review this foundation. User should later choose Android test route, confirm GitHub account/email and repository visibility/URL, and choose license before public connection/publication. Do not start Stage 2 automatically.

## Stage 2 implementation — 2026-10-30

User approved Stage 2 in the current request. Implemented in `apps/mobile/` (supersedes the earlier `mobile/` proposal). Single empty diary screen, theme tokens, strict TypeScript, safe areas and a clearly labeled placeholder Add Food alert. No real nutrition data or services.

Verified: typecheck, lint, formatting, one AA contrast test, Expo Doctor 21/21, public Expo config and Android Hermes bundle export passed. `npm start -- --localhost` started Metro at port 8081; its status endpoint returned `packager-status:running`. This verifies development-server startup, not on-device rendering. No Android execution: adb/emulator unavailable on PATH, Android SDK variables unset and standard local SDK adb absent. Device layout, TalkBack and font scaling still require manual verification.

Installed: Expo 57.0.31, React Native 0.86.3, React 19.2.3, safe-area-context 5.7.0, TypeScript 6.0.3, ESLint 9.39.5/config-expo 57.0.2, Prettier 3.9.10, Expo Doctor 1.21.5. Node 22.23.2/npm 10.9.8. Lockfile records transitive versions. SDK 57 follows current Expo Go transition guidance: https://docs.expo.dev/get-started/create-a-project/ . No navigation library needed yet.

Known issues: npm audit retains 8 transitive advisories (5 low, 3 high) involving Expo tooling's deepmerge/zod chain after compatible `npm audit fix`; forced remediation proposes incompatible Expo 51 downgrade and was not applied. Resolve/reassess before release. Expo-selected ESLint 9 emits an upstream support warning; retain compatibility pending supported SDK upgrade. The Node contrast test emits a module-type detection warning but passes. No claim of production security readiness.

Next: review Stage 2 and verify the screen on Android before Stage 3. Stage 3 has not begun.

## SDK 58 verification — 2026-10-30

Branch `codex/expo-sdk-58`, based on master f75c4f3. Installed Expo 58.0.21, React Native 0.88.1, React 19.3.0, TypeScript 6.0.3. Expo-selected @types/react 19.3.0, eslint-config-expo 58.0.4, expo-status-bar 58.0.4 and safe-area-context 5.10.1. No changes to application features.

| Check                                               | Result                                                                                                      |
| --------------------------------------------------- | ----------------------------------------------------------------------------------------------------------- |
| `npm run typecheck`                                 | Passed                                                                                                      |
| `npm run lint`                                      | Passed                                                                                                      |
| `npm run format:check`                              | Initially failed on Expo-generated app.json formatting; targeted Prettier formatting fixed it; rerun passed |
| `npm test`                                          | 1 passed, 0 failed (AA contrast)                                                                            |
| `npx expo-doctor`                                   | 20/20 passed                                                                                                |
| `npx expo config --type public`                     | Passed, SDK 58.0.0                                                                                          |
| `npx expo export --platform android`                | Passed, Android Hermes bundle exported; not an APK/device test                                              |
| Manifest/lockfile comparison and `npm ls --depth=0` | Dependency ranges agree; installed tree valid                                                               |
| `npm audit` before and after                        | Both report 8 affected packages: 5 low, 3 high; audit is not clean                                          |

Unchanged root advisories: deepmerge prototype poisoning (GHSA-gcqx-w48m-w2h4) and zod oversized-collection memory exhaustion (GHSA-mrhx-c7xc-m3w5), propagated through Expo config/CLI tooling. No newly reported advisory compared with the immediate pre-upgrade baseline. These remain release risks; a passing bundle does not establish security. No forced remediation applied.

Existing Node module-type detection warning in the contrast test and NO_COLOR/FORCE_COLOR warnings during bundling remain visible; they were not suppressed. Physical Android execution, layout and interaction verification remain pending the user's SDK 58 Expo Go test. No Stage 3 work or merge into master.

## Stage 3 dashboard — 2026-10-30

Current branch: codex/stage-3-dashboard, based on SDK 58 64e5f33. Stage 3 implementation is ready for review: Home dashboard, sample Diary and clearly unfinished Calendar/Progress/Profile, reusable UI, isolated demo fixtures and tested sums/progress. All five tests, types, lint, formatting, Doctor 20/20, config and Android export pass. UTF-8 replacement-character scan passes. Physical Android and accessibility interaction checks remain pending. No backend, persistent logging or Stage 4. Next: user reviews preview on phone; do not merge or start Stage 4 automatically.

## Reference-inspired UI refinement

User supplied a nutrition-app visual reference. Adapted Home with a forest-green fading header, centered identity/date, calorie progress ring, compact colored macro bars, pill action and rounded meal rows. Diary shares meal-card styling; tabs now have consistent SVG line icons. Demo labeling remains visible and calculations/features are unchanged. No invented nutrition score, history chart or food-search feature was added.

Added Expo-compatible SVG/linear-gradient modules. Installation exposed an existing react-dom 19.3.1 peer mismatch with React 19.3.0; `expo install react-dom` aligned it to the SDK-compatible version without force/legacy flags. Initial refactor syntax and strict icon-color typing failures were fixed; types, lint, formatting, five tests, Doctor 20/20 and Android export passed. Existing eight audit advisories remain. Visual fidelity, physical Android rendering, large text and TalkBack remain unverified and require phone review.

## Stage 4 handoff

Current branch codex/stage-4-food-search from clean codex/stage-3-dashboard 2e81e27, correct origin vedantp404/Bites2Go. Stage 4 implements local illustrative food search, retained meal/draft, detail nutrition and gram preview with honest temporary confirmation. Existing SDK 58, dashboard, ring, macros and tabs preserved. No dependency changes or backend/persistence. Ten tests pass; types, lint, Doctor 20/20, public config and Android export pass. Formatting correction and fresh audit details are in Test Plan. Existing eight audit findings remain.

Exact next task: user reviews Stage 4 on Android using the Test Plan checklist. Do not begin Stage 5 or merge into master. After approval, resolve production food-data rights/coverage and agree persistence/auth-isolation scope before real diary logging. Drafts are memory-only; fixture nutrition is not authoritative. Physical visual/accessibility checks remain pending. Commit/push outcomes are reported in the completion message, not predicted here.

## Master integration validation

TypeScript, lint, all 10 automated tests, Expo Doctor (20/20), public Expo configuration and Android Hermes export passed on the integrated application. Formatting initially failed because core.autocrlf=true converted checkout text to CRLF. Verified normalized content matched committed source; added .gitattributes for LF mobile text and normalized working files. Formatting rerun passed. No application logic or dependency versions changed beyond the existing feature commits.

Fresh npm audit still exits 1 with 8 affected packages (5 low, 3 high): deepmerge GHSA-gcqx-w48m-w2h4 and zod GHSA-mrhx-c7xc-m3w5 through Expo tooling. No forced fixes applied. Existing Node module-type and Metro color warnings remain visible. User reports Stage 4 phone verification; agent did not run a device test. Commit/push outcomes are verified and reported in the completion message; no self-referential follow-up commit is required.

## Stage 11 dependency follow-up (2026-10-30)

Explicit investigation-only request: no commit/push, no next phase. Fresh audit remains 3 high/5 low. Registry confirms installed Expo/CLI are latest stable and no compatible Zod/deepmerge patch; no dependency changes. Installed CLI schema bounded invalid-array probe demonstrates issue-count growth; no remote exploit or OOM test claimed. Fresh export source map again excludes both libraries. 96 tests, types/lint/format, Doctor20/20, config/export pass. Existing code/test/manifest/lockfile hashes preserved; only appended notes in RELEASE_READINESS.md, TASKS.md and this Memory. Physical Android/live Supabase not tested. Acceptance criteria were not changed: user reviews evidence before any commit decision. Full eight-row table, ranges, parent edges and commands are appended to RELEASE_READINESS.md.
