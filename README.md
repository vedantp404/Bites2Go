# Bites2Go

**Offline-first nutrition tracking for everyday meals, with optional AI-assisted food logging.**

Bites2Go is an Android-focused nutrition diary built with Expo, React Native and TypeScript. It helps you search foods, track portions and nutrients, create recipes, review your progress, and log meals by photo or spoken description. The diary is stored locally in SQLite; AI suggestions are **reviewed and confirmed by the user** before they become diary entries.

> **Project status:** Active development / Android preview testing. The app and its FastAPI AI backend are functional, but AI provider availability, free-tier quotas, device acceptance, and production security hardening remain in progress. This repository is not presented as a production-ready medical or nutrition service.

## Features

- **Food diary:** Log breakfast, lunch, dinner and snacks; edit or delete portions; browse previous days in a calendar; view daily calories and available macros.
- **Food search and portions:** Search a bundled food catalogue, choose gram quantities or supported servings, and review nutrient calculations before saving.
- **My Foods, Meals & Recipes:** Create custom foods from label values, combine ingredients into saved meals, calculate yields and per-serving nutrition, and log fractional servings. Previously saved diary entries retain their original nutrition snapshots.
- **Favourites and recents:** Return quickly to frequently used foods and recently logged items.
- **Progress and insights:** Track weight, goals, BMI calculations, and historical nutrition summaries. Partial or unknown nutrient values remain explicitly unknown rather than being treated as zero.
- **AI photo recognition:** Submit a meal photograph for suggested foods and quantities, then review and correct the results before logging.
- **AI voice meal parsing:** Speak or type a meal description (including common Indian foods and Hinglish phrasing), then review the extracted items and portions.
- **Offline-first experience:** Manual diary logging, saved foods and historical records work without a cloud AI connection. Light, dark and system themes are supported.

## How it works

```text
Android app (Expo / React Native)
  ├── Food search, diary, recipes, goals, insights
  │     └── Local SQLite (authoritative diary and user data)
  └── Optional AI-assisted logging
        └── FastAPI backend (Render)
              ├── Photo: Gemini primary → OpenRouter vision fallback
              └── Voice transcript: OpenRouter Nemotron primary → Gemini fallback
                    ↓
             Structured candidate foods
                    ↓
             User reviews and confirms
                    ↓
             Saved locally in SQLite
```

The backend does not write directly to the mobile diary. A cloud authentication/synchronization design exists in the repository, but **live cloud sync is not enabled** in the current app.

### AI configuration

The current backend implementation uses separate routing for each task:

| Task | Primary | Fallback |
| --- | --- | --- |
| Photo recognition | `gemini-3.5-flash` | `nvidia/nemotron-3.5-super-vl:free` via OpenRouter; an optional alternative free vision model |
| Voice meal parsing (text transcript) | `nvidia/nemotron-3-ultra-550b-a55b:free` via OpenRouter | `gemini-3.5-flash` |

The mobile app supplies a **text transcript** for AI voice meal parsing; the text-only Nemotron Ultra model is not used for image recognition. Provider models and deadlines are configurable on the backend. Requests can still fail because of upstream outages, free-tier limits, invalid model output, or network issues. Manual logging remains the reliable alternative.

## Tech stack

| Layer | Technology |
| --- | --- |
| Mobile | React Native, Expo Router, Expo SDK 58, TypeScript |
| Offline storage | Expo SQLite |
| Backend | Python, FastAPI, Pydantic, Uvicorn |
| AI integrations | Google Gemini API, OpenRouter API |
| Deployment | Expo EAS (Android preview builds), Render (backend) |
| Planned / disabled | Supabase-based authentication and diary sync |

## Repository layout

```text
Bites2Go/
├── apps/
│   └── mobile/             # Expo Android app, screens, domain logic and tests
├── backend/
│   ├── app/                # FastAPI application, routers and AI providers
│   └── tests/              # Backend tests, including provider failover
├── docs/                   # Architecture, product, security and test documentation
├── .planning/              # GSD project planning and milestone state
├── scripts/                # Data and developer utilities
├── TASKS.md                # Project task history and handoffs
└── README.md
```

## Getting started

### Prerequisites

- Node.js and npm compatible with the lockfile (Node.js 22 is used in development)
- Python 3.13 or another version supported by `backend/requirements.txt`
- Android phone with a compatible Expo development build, or an Android emulator
- API keys **only if you want to run the AI backend**

### 1. Clone the repository

```bash
git clone https://github.com/vedantp404/Bites2Go.git
cd Bites2Go
```

### 2. Run the mobile app

```bash
cd apps/mobile
npm ci
npx expo start --clear
```

Open the project using a **compatible development build** on your Android device (or the available Expo workflow for your project setup). A normal installed preview APK does not need Metro running for everyday use. Native configuration changes require a new native build.

For a production-style Android JavaScript bundle check (not an APK):

```bash
npx expo export --platform android
```

### 3. Run the backend locally (optional)

From the repository root, in PowerShell:

```powershell
cd backend
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
# Edit backend/.env with your own local API keys and settings.
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Check the local backend at `http://127.0.0.1:8000/health` and interactive API docs at `http://127.0.0.1:8000/docs`.

The mobile app uses `EXPO_PUBLIC_AI_BACKEND_URL` to choose its API endpoint. For an installed preview APK, this is normally configured at build time to point to the hosted backend. Changing the URL in a local `.env` file does **not** change an already-installed APK. Use the appropriate network-accessible host address when testing on a physical phone; the phone cannot reach your PC through its own `localhost`.

**Security:** Never commit `.env`, `.env.local`, API keys, personal meal data, or access tokens. Only public `EXPO_PUBLIC_*` values belong in the client bundle.

## Testing

From the repository root:

```powershell
# Backend
.\backend\.venv\Scripts\python.exe -m pytest backend/tests -v

# Mobile unit tests
npm test --prefix apps/mobile

# Mobile TypeScript check
npx tsc --noEmit --project apps/mobile/tsconfig.json

# Android bundle validation
cd apps/mobile
npx expo export --platform android
```

Unit tests and bundle exports do not replace physical-device checks. Before a release, verify permission flows, speech recognition, photo capture, offline persistence, accessibility, and real AI failure/recovery behavior on Android. See the [test plan](docs/TEST_PLAN.md).

## Deployment notes

- **Backend:** The project has been tested on a Render Python web service using `uvicorn app.main:app --host 0.0.0.0 --port $PORT`. Keep Gemini/OpenRouter secrets in Render's environment settings, not in the mobile app.
- **Android:** Preview builds use Expo EAS. An `expo export` bundle is not an installable APK.
- **Model availability:** Free API endpoints may throttle, time out or return invalid/empty outputs. A successful `/health` response confirms configuration, **not** guaranteed inference availability.
- **Before public release:** Review API abuse protection, rate limiting, data handling, dependency advisories, free-tier quota limits, and release-device acceptance. The `environment` field in `/health` should be checked against deployment configuration.

## Documentation

| Guide | Description |
| --- | --- |
| [Product requirements](docs/PRD.md) | Product goals and user journeys |
| [Architecture](docs/ARCHITECTURE.md) | Modules, data models and offline boundaries |
| [Backend guide](backend/README.md) | AI service setup, endpoints and provider configuration |
| [Test plan](docs/TEST_PLAN.md) | Automated and device validation |
| [Security](docs/SECURITY.md) | Privacy and security considerations |
| [Release readiness](docs/RELEASE_READINESS.md) | Outstanding release gates |
| [Project tasks](TASKS.md) | Implementation history and next steps |
| [Development rules](RULES.md) | Repository workflow and conventions |

## Contributing

Bites2Go is under active development. Before contributing, read [RULES.md](RULES.md) and the relevant documentation. Keep changes focused, preserve unrelated working-tree edits, run the relevant checks, and use descriptive Git commits. Do not push changes or deploy without the project maintainer's approval.

## Limitations and disclaimer

Bites2Go's nutrition values and AI meal estimates are informational and may be incomplete or inaccurate. Food photos cannot reliably determine exact quantities, ingredients or cooking methods; users should verify entries. BMI and nutrition insights are not medical diagnoses. Offline app data can be lost if the app is uninstalled or its data is cleared unless an independent backup exists.

## License

A public software license has **not yet been selected**. Repository visibility does not, by itself, grant permission to reuse or redistribute the code.
