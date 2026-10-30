# Bites2Go

An Android nutrition tracker designed around everyday Indian meals, reliable food data, and optional AI-assisted logging.

**Status: Stage 3 dashboard preview implemented; Android device verification pending.** Product name is a working name based on the workspace folder. Stage 1 is committed as 458c3c1. Mobile dependencies are installed locally; no external services provisioned.

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
  app/                            # Expo Router: five tab routes and layout
  src/screens/                    # Home, Diary, unfinished-section screen
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
4. Licensed food catalog, backend foundation and calculation engine.
5. Authenticated, persistent food logging.
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

Run `npm start -- --clear --lan` in apps/mobile and scan in SDK 58 Expo Go on the same Wi-Fi. Test all five tabs, Android Back, each meal's Add Food alert, large-text scrolling and screen-reader progress announcements. Stage 4 has not started.
