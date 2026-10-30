# Requirements Intel

## REQ-home-dashboard
- source: docs/PRD.md
- description: Home shows date, calories consumed/target/remaining, protein/carbs/fat/fiber, meal summaries and Add Food. No-entry days say no entries; partial data carries a completeness label. Weight and streak summaries stay secondary.
- acceptance: Date header, daily nutritional totals, progress bars, meal buckets (Breakfast, Lunch, Snacks, Dinner), Add Food CTA.
- scope: Dashboard, navigation

## REQ-food-search
- source: docs/PRD.md
- description: Search by name/alias; choose food state, source and reference values; enter positive grams or a supported food-specific serving; preview recalculates before save. No universal bowl/roti conversion.
- acceptance: Instant search, state filters, gram and serving unit support, dynamic portion nutrition recalculation.
- scope: Food catalogue, search

## REQ-diary-crud
- source: docs/PRD.md
- description: Add, edit and delete breakfast/lunch/snacks/dinner entries on today or a selected past date. Retry cannot duplicate a save; errors preserve draft input.
- acceptance: Full CRUD on entries, idempotent retries, draft preservation on failure, confirmed delete modal.
- scope: Diary logging, persistence

## REQ-indian-catalog
- source: docs/PRD.md
- description: Curate Indian-relevant rice, roti/chapati, dal, rajma/chana, vegetables/curries, paneer, milk/curd, eggs, chicken/fish, oats, fruits, nuts/seeds, bread and snacks. Raw/cooked and added-fat variants have distinct identities. Generic dishes are labeled estimates of a specific preparation.
- acceptance: Curated static fixture dataset representing common Indian culinary preparations with distinct raw/cooked items.
- scope: Food fixtures

## REQ-food-provenance
- source: docs/PRD.md
- description: Every imported food has provenance, reference basis, units and reuse rights. Missing nutrient data remains missing; energy and carbohydrate conventions are visible where materially different.
- acceptance: Source attribution, explicit 100 g reference basis, null for unknown nutrients without fabricating zero.
- scope: Data integrity

## REQ-nutrient-scaling
- source: docs/PRD.md
- description: Deterministic per-100 g scaling, known serving conversion, complete/partial daily totals, stable snapshots and tested precision.
- acceptance: Floating-point precision scaling, independent meal snapshots unaffected by future catalogue changes.
- scope: Arithmetic, snapshots

## REQ-nutrition-goals
- source: docs/PRD.md
- description: Configure calorie, protein, carb, fat and fiber goals. Show consumed, target, signed remaining and meaningful percentage. Unset/zero target has no percentage; negatives are rejected. No automatic aggressive restriction advice.
- acceptance: Effective-dated nutritional targets, signed remaining calculation, suppression of percentage for zero/unset targets.
- scope: Goals, health

## REQ-calendar-history
- source: docs/PRD.md
- description: Persist user-isolated diaries with explicit diary dates; navigate month boundaries, leap days and past dates. Calendar distinguishes entries, user-completed logging and achieved goals. Trends show gaps rather than invented zeros.
- acceptance: Monday-first monthly calendar view, date selection, inline diary view for historical days, entry dot indicators.
- scope: Calendar, navigation

## REQ-bmi-screening
- source: docs/PRD.md
- description: BMI accepts finite positive height and weight; kg/m² calculation; explains screening limitations, muscle/body-fat limits and no diagnosis. No automatic calorie prescription.
- acceptance: Height (cm) and weight (kg) input, 1-decimal BMI output, adult 20+ scoping, prominent medical disclaimer.
- scope: Health, BMI

## REQ-weight-tracking
- source: docs/PRD.md
- description: Dated weights, start/current/target, gain/loss/maintenance, trend and weekly averages. Equal start/target never divides by zero; overshoot is represented clearly; no exact finish date prediction.
- acceptance: Dated kg records, chronological history, SVG chart with actual points, baseline snapshot preservation.
- scope: Weight progress, charts

## REQ-logging-streaks
- source: docs/PRD.md
- description: Separate logging and goal streaks. Achievements have transparent criteria: first entry; first explicitly completed day; seven consecutive logged days; first weight; first achieved nutrition day; five logged days in a Monday–Sunday week.
- acceptance: Daily streak counting based on local calendar dates with no artificial freeze mechanics.
- scope: Streaks, gamification

## REQ-nutrition-insights
- source: docs/PRD.md
- description: Nutrient insights compare sufficiently complete recorded intake with manual targets or reviewed reference values. Say recorded intake may be low, never diagnose deficiency. Filter suggestions by preferences, exclusions, remaining energy, meal context and optional budget. Unknown nutrient coverage suppresses definitive claims.
- acceptance: 7/30-day and custom 1-92 day ranges, exclusion of today and incomplete days, nutrient trend charts, deterministic observations.
- scope: Insights, analysis

## REQ-custom-foods-recipes
- source: docs/PRD.md
- description: Private custom foods, versioned recipes, ingredients, final yield and serving count. New revisions affect future selections only; old diary snapshots remain stable.
- acceptance: Custom food CRUD, recipe builder with ingredient snapshots, calculated yield and per-serving nutrition.
- scope: Library, recipes

## REQ-favourites-quick-add
- source: docs/PRD.md
- description: Favorites, saved meal combinations, recent-food reuse and copying to another date. Copied entries are independent; explicit confirmation and idempotency prevent accidental duplicates.
- acceptance: Toggle favourites, diary-derived recents, quick-add grams/servings preserving date and meal context.
- scope: Library, quick-add

## REQ-ai-image-assistance
- source: docs/PRD.md
- description: AI image suggestions show uncertainty, missing/hidden ingredients and editable portions. Cannot write diary until user confirmation and database mapping. Manual fallback always available. Text logging follows; voice and assistant are later options.
- acceptance: Deferred/future capability. Must never bypass manual review or user confirmation.
- scope: AI recognition (future)
