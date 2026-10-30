# Product requirements

## Stage 8 delivered scope

Users can manage custom foods and recipes from Profile or Add Food, search them alongside the illustrative catalogue, favourite available items, and reuse actual recently logged foods. Custom nutrition is entered per defined gram serving with optional description/brand and nullable calories/protein/carbs/fat/fiber. Recipes combine built-in/custom ingredients with editable gram quantities, final measured yield and serving count. Totals and per-serving estimates are reviewed before confirmation; incomplete nutrients are explicit.

Quick-add supports grams and defined servings while retaining selected historical date, meal, quantity review and explicit save. Source changes affect future selections only; existing diary and recipe ingredient snapshots remain stable. Delete requires confirmation and removes the item from favourites/recents without deleting diary history. Unknown source records are not offered as available foods. All records are local; there is no account, backend, upload, sync or Stage 9 work. Android acceptance remains pending; automated evidence is in Test Plan. Earlier stage scope/status sections below are historical.

## Implemented Stage 7 scope

This current section supersedes the historical Stage 1 plans below for Stage 7. Local, adult-focused tracking only: dated kg records (one per date), manual calorie/protein/carbohydrate/fat goals, cm height, numeric BMI and a target weight. No account, cloud synchronization, automatic dietary prescription, pediatric interpretation or Stage 8 functionality. Fiber goals and weekly averages from the earlier roadmap are outside this explicit four-target stage request.

Acceptable measurement/target weight is 20–500 kg and height 100–250 cm. Nutrition targets may be unset, disabled (zero), or positive: calories 1–10000 kcal, protein/fat 0.1–500 g, carbs 0.1–1500 g. These are application input bounds, not medically appropriate ranges. No fake measurements or automatic targets. Earlier sample nutrition targets were presentation fixtures, not personal settings, and are not promoted into saved goals.

Nutrition goals are effective-dated. Saving applies to the form's displayed local date until a later revision; prior dates are unchanged and dates before the first goal remain unset. Current settings can be cleared explicitly. Recorded intake uses existing snapshot totals; remaining is signed internally and shown as remaining/over-target, with no meaningful percentage for unset/zero or incomplete data.

Weight goal starts from the latest measurement when a different target is confirmed. If none exists, the first recorded measurement on/after the goal date supplies its baseline. The saved starting point is a snapshot: later record edits/deletes do not silently rewrite it. Equal start/target uses a difference instead of a percentage; no percentage is shown if the current record predates the baseline. The chart plots actual points with proportional date spacing, no fabricated/interpolated entries. History lists exact values/dates.

BMI is weight in kg divided by height in metres squared, shown to one decimal. Adults 20+ only; no classifications or diagnosis and no pediatric/adolescent interpretation. The interface states that BMI is a screening measure, not a complete measure of health/body composition. Formula and limitation checked against [CDC BMI information](https://www.cdc.gov/bmi/about/).

Status: Stage 1 specification, 2026-10-30. Working name: Bites2Go. All features below are planned, not implemented.

## Vision, problem and audience

People tracking Indian meals need recognizable foods, realistic serving conversions and trustworthy history. Generic dish names hide variation in ingredients and oil; photo estimates add uncertainty. Build a useful manual tracker first, then add optional assistance without making AI a dependency.

Primary audience: adults pursuing muscle gain, weight loss, maintenance or general nutrition awareness. Initial language is English with searchable Indian food aliases; translations are deferred. This is a general wellness product, not a diagnostic or therapeutic system. Initial release is adult-focused; specialized pediatric, pregnancy and clinical recommendations are out of scope.

## Journeys

1. Configure preferences and manual goals; open today's diary; search a cooked food; review grams, source and nutrition; save to lunch; see updated totals.
2. Open a past date; edit a quantity or delete an entry; only that day's totals change; database corrections do not change unrelated history.
3. Record a dated weight; compare a weekly average and target without treating daily fluctuations as tissue changes.
4. Later: photograph a meal; review possible foods, portion estimates and unknown ingredients; map to catalog entries; correct and explicitly confirm; deterministic totals are saved. Failure returns to manual search.

## Scope and functional acceptance

| ID | Requirement and acceptance | Delivery |
| --- | --- | --- |
| F01 | Home shows date, calories consumed/target/remaining, protein/carbs/fat/fiber, meal summaries and Add Food. No-entry days say no entries; partial data carries a completeness label. Weight and streak summaries stay secondary. | MVP, Stages 3–7 |
| F02 | Search by name/alias; choose food state, source and reference values; enter positive grams or a supported food-specific serving; preview recalculates before save. No universal bowl/roti conversion. | MVP, 4–5 |
| F03 | Add, edit and delete breakfast/lunch/snacks/dinner entries on today or a selected past date. Retry cannot duplicate a save; errors preserve draft input. | MVP, 5 |
| F04 | Curate Indian-relevant rice, roti/chapati, dal, rajma/chana, vegetables/curries, paneer, milk/curd, eggs, chicken/fish, oats, fruits, nuts/seeds, bread and snacks. Raw/cooked and added-fat variants have distinct identities. Generic dishes are labeled estimates of a specific preparation. Catalog coverage must pass the Stage 4 gate. | MVP, 4 |
| F05 | Every imported food has provenance, reference basis, units and reuse rights. Missing nutrient data remains missing; energy and carbohydrate conventions are visible where materially different. | MVP, 4 |
| F06 | Deterministic per-100 g scaling, known serving conversion, complete/partial daily totals, stable snapshots and tested precision. | MVP, 4–5 |
| F07 | Configure calorie, protein, carb, fat and fiber goals. Show consumed, target, signed remaining and meaningful percentage. Unset/zero target has no percentage; negatives are rejected. No automatic aggressive restriction advice. | MVP, 7 |
| F08 | Persist user-isolated diaries with explicit diary dates; navigate month boundaries, leap days and past dates. Calendar distinguishes entries, user-completed logging and achieved goals. Trends show gaps rather than invented zeros. | MVP, 5–7 |
| F09 | BMI accepts finite positive height and weight; kg/m² calculation; explains screening limitations, muscle/body-fat limits and no diagnosis. No automatic calorie prescription. | Stage 7 |
| F10 | Dated weights, start/current/target, gain/loss/maintenance, trend and weekly averages. Equal start/target never divides by zero; overshoot is represented clearly; no exact finish date prediction. | MVP, 7 |
| F11 | Separate logging and goal streaks. Achievements have transparent criteria: first entry; first explicitly completed day; seven consecutive logged days; first weight; first achieved nutrition day; five logged days in a Monday–Sunday week. No reward for eating less or excessive activity. | Logging streak 6; achievements later |
| F12 | Nutrient insights compare sufficiently complete recorded intake with manual targets or reviewed reference values. Say recorded intake may be low, never diagnose deficiency. Filter suggestions by preferences, exclusions, remaining energy, meal context and optional budget. Unknown nutrient coverage suppresses definitive claims. | Stage 9 |
| F13 | Private custom foods, versioned recipes, ingredients, final yield and serving count. New revisions affect future selections only; old diary snapshots remain stable. | Stage 8 |
| F14 | Favorites, saved meal combinations, recent-food reuse and copying to another date. Copied entries are independent; explicit confirmation and idempotency prevent accidental duplicates. | Stage 8 |
| F15 | AI image suggestions show uncertainty, missing/hidden ingredients and editable portions. Cannot write diary until user confirmation and database mapping. Manual fallback always available. Text logging follows; voice and assistant are later options. | Stage 10+ |

## Data and behavior rules

- Diary date is a user-selected `YYYY-MM-DD`, defaulted in the profile's IANA timezone; timestamps use UTC separately. Changing timezone never re-buckets old entries. Future diary dates are excluded initially. Weight dates use the same policy.
- No entries means no recorded intake, not proof of fasting. The UI may show a numerical recorded subtotal of zero only alongside the no-entries state. Unknown nutrients show an em dash; partial totals show a known subtotal plus a partial label. Explicit zeros remain zero.
- A day has independent logging status: unstarted, partial, or explicitly complete. Editing a complete day reopens it as partial until reconfirmed. Completeness of nutrient data is separate from completeness of logging.
- Logging streak counts consecutive dates with at least one saved entry. A missing day breaks it; today may remain pending without breaking the streak ending yesterday. Backfills and deletes recompute streaks from diary dates; no freeze tokens.
- Goal achievement requires explicitly complete logging and complete data for all enabled goals. Provisional rule: energy within ±10% of its target, protein/carbs/fat/fiber at least their targets. Unset/zero goals are excluded; no enabled goals means not evaluable. This configurable rule awaits product review before Stage 6; it is a tracking convention, not health guidance. Goal streak counts consecutive achieved dates, separately from logging.
- Goals use effective dates. Editing today's goals does not rewrite past targets; deliberate historical target corrections must be explicit. Dates before the first goal have no target. A target or logging change recomputes the affected achievement view.
- Recipes sum ingredient nutrients, then scale by measured edible final yield. Added water changes weight, not nutrient amount; oil belongs in ingredients. Unknown yield prevents per-gram output. Cooking losses are not inferred without supported retention factors.
- Weight progress for unequal start/target is `(current-start)/(target-start) × 100`; chart can show overshoot while progress bar is clamped 0–100. Equal start/target shows maintenance difference rather than a progress percentage. Weekly average uses available measurements, displays sample count, and never fills missing days.

## Non-functional requirements and release gates

- Correctness: calculation fixtures, snapshot stability and date-boundary cases pass; no known critical arithmetic or privacy defects.
- Reliability: manual operation works without AI. MVP requires network for authoritative writes; failures preserve unsaved drafts visibly. Durable offline synchronization is deferred. Cached read-only views must show age and signed-out users must lose access to private cache.
- Security: two-user and anonymous RLS denial tests pass before any real private diary is stored. Deletion and restore behavior are verified before public release.
- Accessibility: 48 dp touch targets, TalkBack labels, scalable type, non-color indicators and contrast requirements in Design.
- Performance targets, not measured claims: on an agreed mid-range Android device and controlled network, cached screen interactions under 200 ms and food search p95 under 1 s excluding upstream cold starts. Record dataset size and environment; benchmark at Stage 4/11.
- Privacy: no photos saved by default; no diary contents in analytics. Export/account deletion and a reviewed privacy notice are public-release gates.

## Success measures

MVP acceptance is a real Android manual journey from search to saved past diary and weight record, surviving restart and cross-user denial. Formative usability goal: at least four of five consenting testers log a known food within 30 seconds after onboarding, without help. Track calculation defects and save failures using synthetic/local testing first; analytics needs a separate privacy decision. These are proposed targets, not observed results.

## Deferred scope

AI, voice, advanced recommendations, recipes, saved meals, extensive achievements, barcode scanning, wearables, social features, subscriptions, full offline sync, iOS release and automatic clinical target prescriptions. Calendar and simple logging streaks precede the Stage 7 MVP completion; advanced gamification does not block it.
