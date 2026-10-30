---
last_mapped_commit: f54c1f195289ce4d54a79e7def2170fb84f20858
last_mapped_at: 2026-10-30
---
# Codebase Structure

**Analysis Date:** 2026-10-30

## Directory Layout

```
bites2go/
├── .planning/                  # Project roadmap, GSD state, codebase maps
│   └── codebase/               # High-level architecture and convention documentation
├── apps/
│   └── mobile/                 # React Native / Expo mobile application
│       ├── app/                # Expo Router file-based route definitions
│       │   ├── (tabs)/         # Bottom navigation tab screens (Today, Diary, Calendar, Progress, Profile)
│       │   ├── _layout.tsx     # Root navigation layout and theme/splash provider mounting
│       │   ├── custom-food.tsx # Stack route for creating/editing custom foods
│       │   ├── diary-entry.tsx # Stack route for portion editing and meal confirmation
│       │   ├── food-search.tsx # Stack route for browsing built-in, custom, and recent foods
│       │   ├── goals.tsx       # Stack route for editing nutritional and weight goals
│       │   ├── insights.tsx    # Stack route for nutrition trends and observations
│       │   ├── my-foods.tsx    # Stack route for managing custom foods and recipes
│       │   ├── recipe.tsx      # Stack route for creating/editing multi-ingredient recipes
│       │   └── weight-entry.tsx# Stack route for adding/editing dated weight records
│       ├── assets/             # Bundled visual assets, CC0 food images, adaptive icons
│       ├── src/                # Core mobile application code
│       │   ├── cloud/          # Supabase sync contracts, configuration, and checkpoints
│       │   ├── components/     # Reusable UI widgets and SVG chart components
│       │   ├── data/           # Static food fixtures and CC0 image registry
│       │   ├── domain/         # Pure business logic (diary, health, library, insights, calendar)
│       │   ├── screens/        # Screen-level presentation components
│       │   ├── state/          # React Context state providers (Diary, Health, Library)
│       │   ├── storage/        # SQLite KV storage repositories and serialization queues
│       │   └── theme/          # Design tokens, color palettes, appearance store
│       └── tests/              # Native Node.js test runner unit and integration suites
├── docs/                       # Project documentation (PRD, MEMORY, SECURITY, TEST_PLAN)
├── scripts/                    # Automation scripts (security scanner, local SQL runner)
└── supabase/                   # Supabase backend definitions
    ├── migrations/             # PostgreSQL migrations with RLS and RPC procedures
    └── tests/                  # Local PostgreSQL policy and isolation tests
```

## Directory Purposes

**`apps/mobile/app/`:**
- Purpose: File-based routing for Expo Router.
- Contains: Layouts (`_layout.tsx`, `(tabs)/_layout.tsx`) and route screens mapped directly to navigation URLs.
- Key files: `apps/mobile/app/_layout.tsx`, `apps/mobile/app/(tabs)/index.tsx`, `apps/mobile/app/diary-entry.tsx`.

**`apps/mobile/src/domain/`:**
- Purpose: Pure functional domain models, business logic, calculations, and data assertions.
- Contains: Arithmetic engines, nutritional scaling, validation schemas, and date key manipulation.
- Key files: `apps/mobile/src/domain/diary.ts`, `apps/mobile/src/domain/food.ts`, `apps/mobile/src/domain/health.ts`, `apps/mobile/src/domain/library.ts`, `apps/mobile/src/domain/insights.ts`.

**`apps/mobile/src/storage/`:**
- Purpose: Persistent storage abstractions and serialized access queues.
- Contains: Repository implementations wrapping `expo-sqlite/kv-store`.
- Key files: `apps/mobile/src/storage/diaryRepository.ts`, `apps/mobile/src/storage/healthRepository.ts`, `apps/mobile/src/storage/libraryRepository.ts`, `apps/mobile/src/storage/localDiary.ts`.

**`apps/mobile/src/state/`:**
- Purpose: Application state management bridging storage and UI via React Context.
- Contains: State providers managing in-memory snapshots, loading states, and error handling.
- Key files: `apps/mobile/src/state/DiaryProvider.tsx`, `apps/mobile/src/state/HealthProvider.tsx`, `apps/mobile/src/state/LibraryProvider.tsx`.

**`apps/mobile/src/components/`:**
- Purpose: Reusable UI widgets, visual indicators, cards, and SVG charts.
- Contains: Dumb/controlled UI components with accessible props.
- Key files: `apps/mobile/src/components/InsightChart.tsx`, `apps/mobile/src/components/WeightChart.tsx`, `apps/mobile/src/components/NutritionVisuals.tsx`.

**`apps/mobile/src/theme/`:**
- Purpose: Theme preferences, semantic color tokens, and style utilities.
- Contains: Color token definitions for Light and Dark modes, appearance preference store.
- Key files: `apps/mobile/src/theme/tokens.ts`, `apps/mobile/src/theme/appearance.ts`, `apps/mobile/src/theme/ThemeProvider.tsx`.

**`apps/mobile/tests/`:**
- Purpose: Unit and integration test suites run with Node's native test runner.
- Contains: `.test.mjs` test files asserting domain logic, SQLite repositories, contrast, and edge cases.
- Key files: `apps/mobile/tests/diary.test.mjs`, `apps/mobile/tests/health.test.mjs`, `apps/mobile/tests/library.test.mjs`, `apps/mobile/tests/insights.test.mjs`.

**`supabase/migrations/` and `supabase/tests/`:**
- Purpose: PostgreSQL backend foundation, Row Level Security policies, and verification tests.
- Key files: `supabase/migrations/202610300001_diary_sync.sql`, `supabase/tests/bootstrap-local.sql`, `supabase/tests/diary-access.sql`.

## Key File Locations

**Entry Points:**
- `apps/mobile/app/_layout.tsx`: Root layout, theme mounting, and splash control.
- `apps/mobile/app/(tabs)/index.tsx`: Application home dashboard screen.

**Configuration:**
- `apps/mobile/package.json`: Dependencies, scripts, and package versioning.
- `apps/mobile/app.json`: Expo app configuration and build manifest.
- `apps/mobile/tsconfig.json`: TypeScript compiler options (`strict: true`, `allowImportingTsExtensions: true`).
- `apps/mobile/eslint.config.js`: ESLint flat configuration.
- `apps/mobile/.prettierrc.json`: Prettier code style rules.

**Core Logic:**
- `apps/mobile/src/domain/food.ts`: Nutritional arithmetic, macro scaling, and static food catalogue.
- `apps/mobile/src/domain/diary.ts`: Diary entry definitions, local date key math, and aggregation logic.
- `apps/mobile/src/domain/health.ts`: Weight history, BMI math, and effective-dated targets.
- `apps/mobile/src/domain/library.ts`: Custom food formulas, recipe yield math, and favourites handling.

**Testing:**
- `apps/mobile/tests/*.test.mjs`: Node native test runner suites covering all features and SQLite lifecycle.

## Naming Conventions

**Files:**
- React components and screens: PascalCase (e.g. `apps/mobile/src/screens/DashboardScreen.tsx`, `apps/mobile/src/components/FoodControls.tsx`).
- Routes in Expo Router: kebab-case (e.g. `apps/mobile/app/custom-food.tsx`, `apps/mobile/app/diary-entry.tsx`).
- Domain modules, utilities, and storage repositories: camelCase (e.g. `apps/mobile/src/domain/diary.ts`, `apps/mobile/src/storage/diaryRepository.ts`).
- Test suites: `.test.mjs` suffix with kebab-case or single noun (e.g. `apps/mobile/tests/diary.test.mjs`).

**Directories:**
- Feature and layer directories: lowercase single words or kebab-case (e.g. `apps/mobile/src/domain`, `apps/mobile/src/components`, `apps/mobile/app/(tabs)`).

## Where to Add New Code

**New Feature (e.g. Water Tracking):**
- Domain logic: `apps/mobile/src/domain/water.ts` (pure functions, units, date keys).
- Storage repository: `apps/mobile/src/storage/waterRepository.ts` (KV adapter, serialized queue).
- State provider: `apps/mobile/src/state/WaterProvider.tsx` (React Context provider).
- UI Screens & Components: `apps/mobile/src/screens/WaterScreen.tsx` and `apps/mobile/src/components/WaterControls.tsx`.
- Route: `apps/mobile/app/water.tsx` (or add to `apps/mobile/app/(tabs)/`).
- Tests: `apps/mobile/tests/water.test.mjs` (unit tests and SQLite close/reopen lifecycle tests).

**New Component/Widget:**
- Implementation: `apps/mobile/src/components/[ComponentName].tsx`.
- Styling: Consume semantic tokens from `apps/mobile/src/theme/tokens.ts`.

**Utilities:**
- Pure helpers: Add to respective domain module in `apps/mobile/src/domain/` or shared helper file.

## Special Directories

**`apps/mobile/dist/`:**
- Purpose: Build artifacts from `npx expo export`.
- Generated: Yes.
- Committed: No (ignored via `.gitignore`).

**`apps/mobile/node_modules/`:**
- Purpose: Installed npm dependencies.
- Generated: Yes.
- Committed: No (ignored via `.gitignore`).

**`docs/`:**
- Purpose: Authoritative architecture, release readiness, and memory documentation.
- Generated: No.
- Committed: Yes.

---

*Structure analysis: 2026-10-30*
