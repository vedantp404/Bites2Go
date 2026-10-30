# Bites2Go

## Stage 7: weights, goals and BMI

Progress now provides dated kg measurements, latest/all-time change, edit/delete confirmation, a chart of actual recorded points and gain/loss/maintenance goal tracking. Profile and Progress link to Goals and height. BMI uses saved height and latest dated weight, displays one decimal and makes no diagnosis or weight-category classification.

Personal calorie/protein/carbohydrate/fat targets start unset. Save your own targets in Profile; Home, Diary and Calendar use the targets effective on the displayed date. Earlier goal history is preserved. Zero disables progress; unknown nutrients keep remaining amounts unavailable. Existing illustrative food values are unchanged.

Weights, height and goals use a separate local SQLite KV document (`bites2go.health.v1`). Diary and appearance records are untouched. One weight per local date; future measurements are rejected. No backend, sync or new packages. [Architecture](docs/ARCHITECTURE.md) documents initialization, validation and conflict/retry handling; [Test Plan](docs/TEST_PLAN.md) contains the Android acceptance checklist.

51 automated tests, TypeScript, lint, formatting, Expo Doctor 20/20, configuration validation and Android export passed during implementation. Audit remains 5 low / 3 high. Physical-device and rendered accessibility/theme verification is pending. Stage 8 is not implemented.

## Visual redesign and appearance

The app now uses the Vibrant Food App direction: warm light surfaces, charcoal dark surfaces, green actions, restrained orange accents, rounded cards, local food photography and consistent navigation.

- Home: daily nutrition ring, macro bars, food inspiration and saved meals.
- Search/details: category chips, thumbnails, prominent food images and unchanged portion confirmation.
- Diary/calendar: themed meal groups, historical food images, date markers and a themed delete confirmation.
- Profile: Appearance → Light, Dark or System (default), with the effective mode displayed. Changes apply immediately and persist locally. Progress remains explicitly unfinished.

Appearance uses the separate SQLite key `bites2go.appearance.v1`; diary schema and nutrient snapshots are unchanged. The app waits for preference loading before mounting its screens. Persistence failures are reported in Profile with a retry by selecting the mode again.

Two CC0 photos (apple/banana, about 228 KB total) are bundled for offline use; other foods use a reusable placeholder. See [image credits](apps/mobile/assets/food/README.md). Food values remain illustrative and photos do not represent exact portions.

Run `cd apps/mobile` then `npm start -- --clear`, and scan with SDK 58 Expo Go on Android. Native configuration changes apply to rebuilt standalone/development clients; Expo Go controls its own launch screen and system-bar configuration. Physical Android acceptance is pending; see [Test Plan](docs/TEST_PLAN.md). Stage 7 is not implemented.

An Android nutrition tracker designed around everyday Indian meals, reliable food data, and optional AI-assisted logging.

**Status: Stage 6 calendar/history implemented; calendar Android checks pending. Stage 5 persistence was verified by the user.** Product name is a working name based on the workspace folder. Stage 1 is committed as 458c3c1. Mobile dependencies are installed locally; no external services provisioned.

## Goals and scope

Make manual food logging quick, make nutrition calculations explainable, and preserve trustworthy diary history. The core product must work without an AI provider.

The MVP includes a polished dashboard, food search, gram and supported serving entry, editable meal logs, daily totals, persistent diaries, past dates, basic nutrition goals, and weight records. Recipes, favorites, advanced insights, achievements, photo recognition, voice, and conversational assistance follow later.

## Proposed stack

React Native + Expo + TypeScript for Android; Python + FastAPI + Pydantic for the backend; Supabase PostgreSQL and Auth with Row Level Security (RLS). AI stays behind the backend, with xAI and Gemini evaluated before Stage 10. Exact dependency versions will be selected and locked during initialization.

## Documentation map

| File | Purpose |
| --- | --- |
| [RULES.md](RULES.md) | Rules for future development sessions |
| [TASKS.md](TASKS.md) | Ordered roadmap and Stage 2 acceptance criteria |
| [PRD](docs/PRD.md) | Requirements, journeys, MVP, acceptance criteria |
| [Architecture](docs/ARCHITECTURE.md) | Modules, data model, calculations, boundaries |
| [Design](docs/DESIGN.md) | Visual tokens, screen inventory, accessibility |
| [Test plan](docs/TEST_PLAN.md) | Business, integration, security and Android checks |
| [Security](docs/SECURITY.md) | Auth, RLS, secrets, uploads and privacy |
| [Decisions](docs/DECISIONS.md) | Confirmed constraints and provisional recommendations |
| [Memory](docs/MEMORY.md) | Verified workspace state and next step |
| [Research](docs/RESEARCH.md) | Official source, provider, licensing and cost findings |
| [GitHub workflow](docs/GITHUB_WORKFLOW.md) | Safe repository setup and contribution process |

Actual mobile structure:

```text
apps/mobile/
  app/                            # root Stack, five routes under (tabs), food-search
  src/screens/                    # Home, Diary, FoodSearch, unfinished sections
  src/components/dashboard.tsx    # cards, actions, accessible nutrient bars
  src/data/dashboardPreview.ts    # isolated synthetic meals and targets
  src/domain/dashboard.ts         # deterministic totals and progress
  src/theme/tokens.ts             # reusable design system
  tests/                          # calculation, progress and contrast tests
  app.json, tsconfig.json, eslint.config.js
  package.json, package-lock.json
```

Expo template assets and its MIT notice are retained; final product branding/license selection remains pending.

## Roadmap

1. Foundation documentation (this stage).
2. Minimal Expo app, TypeScript, tokens and developer checks.
3. Dashboard and navigation prototype with labeled mock data.
4. Local illustrative food catalog, offline search and portion calculations. Production catalog rights and backend setup remain future prerequisites.
5. Local persistent diary; cloud/authentication deferred.
6. Calendar, history and logging streaks.
7. Goals, BMI and weight progress: completes MVP scope.
8. Custom foods, recipes, favorites and saved meals.
9. Nutrient gap insights.
10. Reviewed AI-assisted logging.
11. Consolidated quality, privacy and security validation.
12. APK packaging and release preparation.

Testing and security are requirements throughout, not work postponed to Stage 11.

## Setup and testing

Requires Node 22.23.2 (tested), npm 10.9.8, and a compatible Android Expo Go installation for physical-device testing. No credentials needed.

```powershell
cd apps/mobile
npm ci
npm start -- --clear --lan
npm run typecheck
npm run lint
npm test
npm run format:check
npm run doctor
```

Use `npm run format` to format. On a physical phone, use SDK 58 Expo Go and scan Metro's QR code on the same network. Recheck Expo Go support when installing. `npm run android` requires a configured Android SDK and running emulator/USB device. None was available here. Verify initial screen, scrolling at large text sizes, safe areas, Add Food alert and reload. Android bundle export (`npx expo export --platform android`) passed; it does not produce an installable APK or verify device behavior.

Typecheck, lint, formatting, one contrast test, Expo Doctor (20/20), config validation and bundle export passed. The earlier SDK 57 localhost startup did not verify phone connectivity; use LAN mode for your phone. Device rendering remains unverified. Eight transitive npm advisories remain after compatible remediation; see Test Plan. Never use forced audit downgrades without compatibility review.

Only public configuration may be bundled in the app. No `.env` is required. Backend setup is deferred.

## Screenshots

Screenshots will be added after the Stage 3 prototype exists. No mockups are presented as working product screenshots.

## Contributing

Read RULES and the relevant documentation, agree one bounded task, preserve unrelated changes, validate, and review the diff. Use meaningful conventional commits and PRs for larger features. No automatic commit or push during Stage 1. A code license has not been selected; public hosting alone would not grant reuse rights.

## SDK 58 upgrade

On `codex/expo-sdk-58`: Expo 58.0.21, React Native 0.88.1, React 19.3.0 and TypeScript 6.0.3. The lockfile records the Expo-aligned dependency set. Master remains unchanged pending review.

To preview on Android, stop old Metro servers, run the commands above from `apps/mobile`, connect your computer and phone to the same Wi-Fi, and scan the QR code with SDK 58 Expo Go. Allow Node through Windows Firewall for the private network if prompted. Do not use localhost mode for a separate phone. Android Studio is not required for Expo Go. Verify the screen, Add Food alert, scrolling at larger text sizes and reload; physical-device verification is still pending.

## Stage 3 dashboard preview

Branch `codex/stage-3-dashboard` builds on SDK 58 commit 64e5f33. Home displays local today, calorie target/consumed/remaining, macro progress and four meals. Diary reuses the preview meals. Calendar, Progress and Profile are explicitly unfinished. Expo Router supplies tab navigation; all food actions explain that logging is unavailable.

Demo targets and meal totals are synthetic UI fixtures, not user records or nutrition advice. Breakfast/lunch contain labeled samples; Snacks/Dinner demonstrate empty states. No data is saved. SDK 58 remains installed. Five tests, typecheck, lint, formatting, Doctor (20/20), config and Android export pass. Physical-device, TalkBack and large-text layout checks remain pending.

Run `npm start -- --clear --lan` in apps/mobile and scan in SDK 58 Expo Go on the same Wi-Fi. Test all five tabs, Android Back, each meal's Add Food flow, large-text scrolling and screen-reader progress announcements. Stage 4 now adds local food search; see the instructions below.

The dashboard now follows the supplied visual reference: green header, calorie ring, compact macro bars, rounded meal cards and icon tabs. Physical-device visual verification remains pending.

## Try Stage 5

```powershell
cd C:\Users\Asus\Music\Bites2Go\apps\mobile
npm ci
npm start -- --clear --lan
```

Open SDK 58 Expo Go on the same Wi-Fi and scan the QR code. Add Food opens search, carries the chosen diary date/meal, and lets you choose a meal when needed. Review grams and confirm to save locally. Home uses today's saved entries; Diary supports Previous day / Today / Next day (no future entries). Tap an entry to edit its portion or delete with confirmation. Cancelling does not save a draft. Success feedback and totals appear only after persistence succeeds; failed actions retain drafts for retry.

Storage: Expo SQLite 58.0.14 key-value API and Expo Crypto 58.0.7 UUIDs. All 12 food records remain illustrative; saved reference/portion snapshots preserve history. Sample dashboard meals are never counted. Targets are clearly labeled sample settings, not medical recommendations. No account, cloud sync, analytics or app uploads. Local data is not application-encrypted and can be lost when uninstalling/clearing app data; OS/Expo Go host backup policies apply. Invalid/unsupported diary data blocks writes without clearing it. No destructive automatic migration or recovery reset is provided.

Run `npm run typecheck`, `npm run lint`, `npm run format:check`, `npm test`, `npx expo-doctor`, `npx expo config --type public`, `npx expo export --platform android`, and `npm audit`. See Test Plan for actual results. **Still required on Android:** save, close/reopen, edit/cancel, delete/cancel, separate dates, duplicate taps, keyboard and accessibility. Prior Stage 4 verification does not establish native persistence.

## Stage 6 calendar and history

Open Calendar to browse months. Monday is the first weekday. Today has a text label, the selected day has an outline, and a dot indicates actual saved entries. Tap a date to show its diary below the grid. Meal cards show portions, calories and available macros; add/edit/delete reuse the existing persistent diary and preserve that date. Month arrows only browse; they do not change the selected diary. Previous/Next day changes selection and month; Today returns to the actual current day. Home always shows today. Future dates can be viewed but cannot be logged yet.

No schema migration, duplicate database, new package or cloud service. Navigation reuses a memoized date index of the existing loaded diary. On narrow screens, swipe the calendar grid horizontally; date targets are not shrunk below 48 dp. Selection survives tab changes during the session; after restarting, selection defaults to today while entries persist. Follow the Stage 6 Test Plan on Android; automated checks do not establish device rendering or Back behavior.

## Development workflow

Work directly on `master` by default, validate and review changes, then commit and push to `origin/master` and verify its hash. PRs/feature branches are only required when explicitly requested or mandated by repository policy. Follow AGENTS.md and RULES.md. Stage 4 Android acceptance is user-reported; detailed device/accessibility evidence is not recorded. Wait for explicit authorization before the next stage.
