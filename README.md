# Bites2Go

An Android nutrition tracker designed around everyday Indian meals, reliable food data, and optional AI-assisted logging.

**Status: Stage 2 mobile foundation implemented; Android device verification pending.** Product name is a working name based on the workspace folder. Stage 1 is committed as 458c3c1. Mobile dependencies are installed locally; no external services provisioned.

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
  App.tsx                         # safe-area provider and screen
  src/screens/WelcomeScreen.tsx   # empty diary and preview action
  src/theme/tokens.ts             # reusable design system
  tests/theme.test.mjs            # AA text contrast check
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
npm start
npm run typecheck
npm run lint
npm test
npm run format:check
npm run doctor
```

Use `npm run format` to format. On a physical phone, use matching SDK 57 Expo Go and scan Metro's QR code on the same network. Recheck Expo Go support when installing. `npm run android` requires a configured Android SDK and running emulator/USB device. None was available here. Verify initial screen, scrolling at large text sizes, safe areas, Add Food alert and reload. Android bundle export (`npx expo export --platform android`) passed; it does not produce an installable APK or verify device behavior.

Typecheck, lint, formatting, one contrast test, Expo Doctor (21/21), config validation and bundle export passed. Metro started with `npm start -- --localhost`; device rendering remains unverified. Eight transitive npm advisories remain after compatible remediation; see Test Plan. Never use forced audit downgrades without compatibility review.

Only public configuration may be bundled in the app. No `.env` is required. Backend setup is deferred.

## Screenshots

Screenshots will be added after the Stage 3 prototype exists. No mockups are presented as working product screenshots.

## Contributing

Read RULES and the relevant documentation, agree one bounded task, preserve unrelated changes, validate, and review the diff. Use meaningful conventional commits and PRs for larger features. No automatic commit or push during Stage 1. A code license has not been selected; public hosting alone would not grant reuse rights.
