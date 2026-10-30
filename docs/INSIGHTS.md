# Nutrition Insights rules

Open Progress → Nutrition insights. Everything is computed offline from loaded local diary and health snapshots. No new storage, migrations, source-food lookup, cloud sync, AI or external data. Existing custom-food/recipe diary entries are ordinary immutable diary snapshots, so later source edits/deletion never rewrite these results.

## Dates and coverage

Last 7/30 days include the device's current local calendar date. Custom start/end fields accept 1–92 inclusive local dates; invalid, reversed or future ranges are rejected without changing the applied period. Local shiftDay helpers cross month/year/leap/DST boundaries; UTC noon is used only by the existing ordinal helper for already selected calendar keys, never to choose today's date. The existing foreground/timer hook updates today. Current-day records can be inspected but are never counted as completed days in period statistics. Future records outside the requested range are ignored. Duplicate diary IDs cause an error instead of double-counting.

Coverage counts distinguish no entries, recorded meal sections and nutrient-specific unknowns. Some categories overlap: a two-meal day can also have unknown protein. A no-entry day has unknown intake, not a confirmed zero. Entry count or meal coverage does not prove that the user logged everything.

## Eligibility and averages

The schema has no completed-diary flag. For a deliberately conservative proxy, a nutrient-day is eligible only if it is before today, contains at least one entry in **each** of Breakfast/Lunch/Snacks/Dinner, and all entries have a known value for that nutrient. This excludes intentionally skipped meals. It is a product calculation rule, not a medical or dietary standard. A later completion-marker design needs explicit approval and migration; this stage does not invent one.

The same eligibility flag controls charted intake, period averages and goal consistency. Daily detail still shows all recorded data. Shared diaryTotals sums known values and marks partial totals; a partial amount is labelled incomplete and no percentage is shown. Entirely unknown values remain null. Genuine explicit zero values remain zero and can be eligible if the other conditions hold. Calories are recorded source calories, never inferred from macros.

Average for a nutrient = sum of that nutrient's eligible daily totals / its eligible-day count. Zero eligible days yields Unknown, never zero. Each nutrient displays its own denominator and excluded-day count. One eligible day can provide an average but is not a trend. Round only for display; stored snapshots and calculations retain their precision. Fiber can be inspected/averaged but has no configurable target in the current health model.

## Personal target consistency

For calories and protein, further restrict eligible days to dates with a positive target returned by targetsForDate. Unset and zero-disabled targets are excluded. Within-band count uses **90–110% inclusive** of the target on each date, with a 1e-12 ratio comparison tolerance for floating-point boundary noise. Percentage = within-band days / eligible positive-target days × 100. Below/above are neutral relative-to-band categories; missing data is not a missed target. The band is descriptive, not a recommendation or assurance of nutritional adequacy.

Changes to effective-dated targets apply to their historical intervals; today's target never replaces all past targets. The calorie observation compares recorded mean and target mean across exactly the same eligible target dates, not unrelated sets. Observations state their period/denominators and cannot diagnose deficiencies, causal relationships or future outcomes.

## Charts, weight and accessibility

The nutrient selector shows calories, protein, carbohydrates, fat or fiber. Green intake dots and orange positive-target dashes appear only on eligible dates; excluded days have explicit gaps/dashes, not zero or interpolated lines. The zero-based scale includes eligible intake and target values. Dates are spaced for horizontal scrolling through at most 92 days. The SVG is supplementary; Show exact daily values exposes accessible text with full dates, amounts/units, targets and exclusion status. Selecting a row changes the daily summary; Previous/Next also navigates within the applied range.

Weights are existing actual measurements within the selected date range, rendered by the existing WeightChart. With at least two records, change = latest kg − earliest kg; no interpolation, predicted timeline or medically meaningful trend is inferred. The current saved weight goal is available only if set on/before the latest measurement; existing weightProgress also guards its starting point. The schema does not store weight-goal revisions, so the UI does not invent a goal that applied historically. Open weight progress retains the existing full-history editing destination.

Light/Dark/System tokens, shared controls, safe areas and keyboard scrolling are reused. Loading/error states do not masquerade as empty data. No records are changed on calculation failures. Physical Android/TalkBack/large-text verification remains pending in TEST_PLAN.md; automated pure view-state/label tests are not rendered native acceptance.
