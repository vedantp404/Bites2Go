# Context Intel

## Vision and Audience
- source: docs/PRD.md
People tracking Indian meals need recognizable foods, realistic serving conversions and trustworthy history. Generic dish names hide variation in ingredients and oil; photo estimates add uncertainty. Build a useful manual tracker first, then add optional assistance without making AI a dependency.
Primary audience: adults pursuing muscle gain, weight loss, maintenance or general nutrition awareness. Initial language is English with searchable Indian food aliases.

## Data & Behavior Rules
- source: docs/PRD.md
- No entries means no recorded intake, not proof of fasting.
- Unknown nutrients show an em dash; partial totals show known subtotals plus a partial label.
- Streaks count consecutive calendar dates with at least one saved entry.
- Goals use effective dating; modifying today's goal does not alter past historical targets.
