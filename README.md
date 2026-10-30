# Bites2Go

An Android nutrition tracker designed around everyday Indian meals, reliable food data, and optional AI-assisted logging.

**Status: Stage 1 documentation foundation. No runnable application yet.** Product name is a working name based on the workspace folder. No services have been provisioned, dependencies installed, or code committed or pushed in this stage.

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

Only these documents, `.gitignore`, `.env.example`, and the root `AGENTS.md` entrypoint exist as project files today. Future folders are `mobile/`, `backend/`, and `supabase/migrations/`; see Architecture. They have not been scaffolded.

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

No install, run, lint, or test scripts exist yet. Do not run Expo scaffolding in the repository root or supply credentials now. After Stage 2 approval, initialize inside `mobile/`, record the chosen Expo SDK and compatible runtime, and add reproducible npm scripts and a lockfile. Stage 2 will document actual commands and Android launch evidence. Backend setup follows in Stage 4.

Observed: Node 22.23.2, npm 10.9.8, Python 3.13.13, Java 21.0.8 and Git 2.55.0.windows.3. Android SDK tools are unavailable on PATH; an emulator or physical device has not been tested. See Memory for compatibility risks.

`.env.example` documents future variable names only. Public mobile variables are bundled into the app and must never contain secrets. Read Security before using real user data. Do not commit meal photos, private diaries, tokens or database dumps.

## Screenshots

Screenshots will be added after the Stage 3 prototype exists. No mockups are presented as working product screenshots.

## Contributing

Read RULES and the relevant documentation, agree one bounded task, preserve unrelated changes, validate, and review the diff. Use meaningful conventional commits and PRs for larger features. No automatic commit or push during Stage 1. A code license has not been selected; public hosting alone would not grant reuse rights.
