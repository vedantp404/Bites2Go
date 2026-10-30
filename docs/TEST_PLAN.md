# Test strategy

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
