# Design system and screen plan

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
