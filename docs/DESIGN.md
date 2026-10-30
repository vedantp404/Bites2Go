# Design system and screen plan

## My Meals presentation

Profile and Add Food expose My Meals & Recipes. Existing themed library page presents My Meals first, with an empty state/create action and accessible cards for ingredient quantities, whole-meal known totals and per-serving nutrition. Unknown values have an explicit incomplete notice. Each card offers Log Meal and edit/delete; custom foods remain available below for missing ingredients. Recipe editor retains shared keyboard-aware fields, measured yield, serving count and confirmed deletion. Logging defaults to one serving, permits positive decimals and shows the converted grams and computed nutrition before confirmation. Existing safe areas, scalable text, touch targets and Light/Dark/System tokens are retained. Native visual/TalkBack checks remain manual.

## Stage 10 Insights presentation

Progress links to a dedicated Nutrition insights stack screen; existing five tabs remain. Shared Light/Dark/System cards organize range controls, coverage, daily nutrition, selectable nutrient trend, averages, consistency, observations and weights. Custom date fields reuse the existing keyboard-aware page and require an explicit Apply action; invalid drafts leave the applied range unchanged. Previous/Next daily navigation stays within that range. Add Food carries the displayed date; generic Open food diary and Open weight progress navigate to existing destinations.

Intake dots and target dashes use primary/secondary tokens plus shape/text labels. Excluded dates show gaps, not zero or connecting/interpolated lines. SVG is supplementary: exact daily text values and eligibility/target labels are available through Show exact daily values. Date points have at least 52 px spacing with horizontal scrolling for long ranges; body text/actions can wrap and scale. Shared controls provide accessible labels, radio selected states and 48 dp touch targets. Loading, data/range errors, no-entry and insufficient-data states are explicit. Native contrast/rendering, TalkBack focus, large fonts, scrolling and theme acceptance still require the Android checklist; no physical visual review is claimed.

## Stage 9 offline account disclosure

Profile adds one shared themed card for Account and cloud. It shows Offline mode / not signed in, safe missing/invalid/configured-but-disabled messages, and states that no records are uploaded. No authentication form is presented before a configured and tested SDK integration. Existing tabs, forms, theme and navigation remain unchanged. Future consent must identify the account, selected records/date range and data leaving the device; future conflicts need explicit choices without silently choosing a version. Native rendering/TalkBack acceptance remains pending.

## Stage 8 library interactions

Keep the existing Vibrant Food App palette and Light/Dark/System tokens. Profile and Add Food link to My foods and recipes; create/edit forms are stack routes with safe areas, keyboard-aware scrolling, labelled inputs and shared actions/delete dialogs. Existing FoodImage renders bundled images by stable ID and placeholders for custom foods/recipes; no new network assets.

Search filters expose All/Favourites/Recent/Custom/Recipes without adding tabs. Cards distinguish built-in illustrative foods, user-created estimates and recipe snapshot estimates. Details offer favourites and grams/defined-serving radio controls before the existing confirm action; tapping the active unit preserves the quantity. Recipe ingredient search reuses FoodChoice and the existing search engine. Loading, unavailable-source, no-results, unknown nutrients, validation and retry states are visible. Shared controls retain accessible labels and 48-point actions. Native narrow-screen, large-text, TalkBack and theme inspection still needs Android acceptance; export is not visual verification.

## Stage 7 progress and settings

Reuse the existing Light/Dark/System tokens, cards, 48 dp actions, safe areas and keyboard-aware scroll containers. Progress separates latest measurement, weight goal, dated chart/history and BMI. History is the accessible textual equivalent of the SVG chart; no line interpolation or invented missing-day values. Points and progress fills use theme primary, labels use text/muted, and errors use error tokens.

Goals and height live in one clearly labeled editor reached from Profile or Progress. Numeric fields display units and limits, and blank/zero behavior is explained before confirmation. Date entry uses YYYY-MM-DD with a keyboard that supports separators; future and duplicate dates have explicit errors. Deletion uses a themed confirmation with Cancel, Android Back dismissal and no write until confirmation.

Home/Diary/Calendar retain existing meal content and display targets for their own date. Consumed, target and remaining/over-target labels are distinct. Zero targets are visibly disabled. Partial/null nutrition suppresses exact remaining/percentage. No sample personal goals or progress. BMI shows inputs/date and one decimal with adult screening limitations; no health-category colors or recommendations.

Manual narrow-screen, large-font, TalkBack/modal focus, keyboard, system-appearance and native startup acceptance remains pending.

## Implemented visual direction: Vibrant Food App

This section supersedes the historical Stage 1 palette below. `src/theme/tokens.ts` owns both complete semantic palettes; screens subscribe through `useTheme` / `useUI` rather than importing a static theme. Light uses warm #FAF7F0, white surfaces, #176044 green and #A64321 accents; Dark uses #151C18 / #202B24 charcoal, #9DE3B1 green and #FFB58F accents. Use `onPrimary` for button text, never `surface`. Semantic tokens include elevated surfaces, selected/input/disabled states, success/warning/error, hero and macro colors.

Typography remains system-native, with stronger heading weight, 24 px card corners and 48 px minimum controls. Food thumbnails are 72 px; detail/inspiration photos are 180 px tall with cover cropping. Accent colors are reserved for categories, fallback tiles and charts. Labels accompany progress and calendar markers. No fake logged entries or nutrition scores were introduced.

Appearance lives in Profile and defaults to System; explicit modes override the app palette only, while System observes OS changes. All screens, tab navigation, inputs and the delete dialog use theme tokens. Status/navigation icon styles follow the effective palette. Keep native launch-screen backgrounds aligned with the token palette when editing app.json.

Local CC0 photo provenance and thumbnail sizes are recorded in `apps/mobile/assets/food/README.md`. Stable food IDs map to image keys independently of food data and historical snapshots; missing/null IDs and image errors use a coherent leaf placeholder. Android layout, large text, screen reader and actual system-bar acceptance remain manual checks.

Stage 1 specification, not implemented UI. Aim for a calm consumer food diary with readable values and one clear primary action per screen.

## Tokens

| Token | Value | Use |
| --- | --- | --- |
| color.primary | #185C42 | Forest green actions and key progress |
| color.background | #FAF8F2 | Warm off-white canvas |
| color.surface | #FFFFFF | Cards and inputs |
| color.accent | #DCEDE2 | Muted mint fills; charcoal foreground |
| color.text | #252B27 | Primary charcoal text |
| color.textMuted | #58635B | Supporting text |
| color.border | #D7DED7 | Decorative boundaries; not sole control identifier |
| color.error | #A12D2D | Error text/icons with written explanation |
| color.warning | #805400 | Partial-data notices |
| color.focus | #185C42 | Visible 2 dp focus boundary |

Validate actual foreground/background pairs with a contrast tool during Stage 2/3. Never use pale mint text on white. Provisional chart series: forest green for energy, #285E8E protein, #805400 carbohydrate, #7A4C83 fat; add labels/patterns so color alone carries no meaning. Do not alter token meanings per screen.

Use Android system sans-serif initially, avoiding font downloads. Sizes in scalable text units: display 32/40, heading 24/32, section 20/28, body 16/24, label 14/20, caption 12/18. Weight 400 body, 500 labels, 600 headings. Essential values and instructions use at least body/label, never tiny captions. Tabular numerals where supported; allow labels to wrap with large text.

Spacing scale in dp: 4, 8, 12, 16, 24, 32, 48. Screen gutters 16; card padding 16; section gaps 24; card radius 16; input/button radius 12. Subtle 1 dp borders, at most restrained elevation 1–2. Avoid gratuitous gradients, animations and decorative charts.

## Components and interactions

- Primary button: forest fill, white label, minimum 48 dp height, clear loading/disabled state; only one dominant action. Secondary: outlined with forest text. Tertiary: text action. Destructive: labeled red action with deletion confirmation or reliable undo.
- Inputs: persistent label, explicit unit, useful decimal keyboard, helper/error text below; do not use placeholder as the only label. Quantity changes update previews, preserving entered text during network errors. Never normalize an invalid value silently.
- Cards: one radius/padding/border convention. Meal row shows food, preparation, amount and energy plus partial/source indicators. Larger tap area opens detail; accessible overflow supports edit/delete.
- Progress: label consumed/target and unit alongside bar/ring. Clamp visual fill but show signed remaining or amount over target. Unset/zero target uses no percentage. Unknown or partial data has explicit text.
- Chart: labeled axes, units, readable scale, accessible textual summary/table alternative, gaps for missing days, no false smoothing. Weight chart explains available-sample weekly averages. Avoid pies with many segments and misleading truncated axes.
- Date control: explicit selected date, today shortcut, month/year navigation; use local date labels. Always show the target day before a backdated save or meal copy.
- Add Food opens manual search by default. Camera is a later optional action, with review and consent before upload. Save disables while in flight; retry uses the same request ID.

## Navigation and screen purposes

Recommend five bottom tabs for the full product: Home, Diary, Calendar, Progress, Profile. Stage 2 has only a minimal landing screen; Stage 3 prototypes navigation with labeled placeholders. Keep Add Food reachable from Home and Diary; do not crowd the tab bar with a sixth item. Retain selected diary date when returning from food detail.

| Screen | Purpose and primary interaction |
| --- | --- |
| Onboarding | Explain manual-first tracking, units, preferences and optional goals; no forced photo access |
| Profile/preferences | Timezone, dietary preferences/exclusions, profile details; avoid collecting unnecessary demographics |
| Home | Date, energy overview, macro/fiber rows, meal summary, Add Food; weight/streak below primary content |
| Add food/search | Query, aliases, recent results later; raw/cooked/source badges; choose a food |
| Food selection/serving | Reference source, grams or verified conversion, preview, missing values, selected meal/date and Save |
| Meal details | Review entries and meal totals; edit/delete; later copy/save meal |
| Daily diary | Date switch, four meal sections, totals and explicit logging-complete action |
| Calendar | Month grid; distinguish logged/completed/goal-achieved states; open selected diary |
| BMI | Height and weight inputs, result and plain-language limitations |
| Weight | Dated record, trend and optional target; edit daily measurement |
| Progress | Weight and nutrient history with range control and missing-day labels |
| Nutrition goals | Manual energy and macro/fiber targets, effective date and safe validation |
| Nutrient insights | Later: recorded gaps, coverage limitations and filtered food suggestions |
| Saved meals/favorites | Later: reusable combinations and explicit destination-date copy |
| Custom foods/recipes | Later: source/label values, ingredients, yield, version-aware preview |
| AI recognition | Later: upload consent, processing, editable candidates/grams, uncertain ingredients, explicit confirmation |
| Settings | Session, privacy, permissions, units, future export/account deletion, version/about |

## States and accessibility

Loading shows a stable skeleton or named spinner; avoid fabricated totals while fetching. Empty diary says “No foods logged for this date” and offers Add Food. No search match offers query tips; custom-food creation appears only when available. Errors state what failed and give retry without clearing drafts. Offline views show cached timestamp and prevent ambiguous saves. Partial nutrients say “Known subtotal — some values unavailable.”

Meet WCAG AA text contrast targets (4.5:1 normal, 3:1 large), 3:1 essential non-text boundaries, and Android minimum 48 × 48 dp targets. Test TalkBack traversal, meaningful icon labels, announced save/error status, font scaling to 200%, keyboard avoidance, screen-reader chart summaries and reduced motion. Announce progress semantically; do not rely on rings or color alone. Screen sizes and safe areas must be tested on small and large Android devices before release.

## Reference-inspired UI refinement

User supplied a nutrition-app visual reference. Adapted Home with a forest-green fading header, centered identity/date, calorie progress ring, compact colored macro bars, pill action and rounded meal rows. Diary shares meal-card styling; tabs now have consistent SVG line icons. Demo labeling remains visible and calculations/features are unchanged. No invented nutrition score, history chart or food-search feature was added.

Added Expo-compatible SVG/linear-gradient modules. Installation exposed an existing react-dom 19.3.1 peer mismatch with React 19.3.0; `expo install react-dom` aligned it to the SDK-compatible version without force/legacy flags. Initial refactor syntax and strict icon-color typing failures were fixed; types, lint, formatting, five tests, Doctor 20/20 and Android export passed. Existing eight audit advisories remain. Visual fidelity, physical Android rendering, large text and TalkBack remain unverified and require phone review.
