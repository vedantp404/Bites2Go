---
last_mapped_commit: f54c1f195289ce4d54a79e7def2170fb84f20858
last_mapped_at: 2026-10-30
---
<!-- refreshed: 2026-10-30 -->
# Architecture

**Analysis Date:** 2026-10-30

## System Overview

```text
┌─────────────────────────────────────────────────────────────┐
│                   UI & Routing Layer                        │
├──────────────────┬──────────────────┬───────────────────────┤
│  Root & Tabs     │  Modal & Stack   │  Components           │
│  `app/_layout`   │  `app/diary-entry`│ `src/components/`    │
│  `app/(tabs)/*`  │  `app/recipe`    │ `InsightChart`, etc.  │
└────────┬─────────┴────────┬─────────┴──────────┬────────────┘
         │                  │                     │
         ▼                  ▼                     ▼
┌─────────────────────────────────────────────────────────────┐
│                 State & Provider Layer                      │
│ `src/state/DiaryProvider.tsx`, `HealthProvider.tsx`,        │
│ `LibraryProvider.tsx`, `src/theme/ThemeProvider.tsx`        │
└────────────────────────────┬────────────────────────────────┘
                             │
         ┌───────────────────┴───────────────────┐
         ▼                                       ▼
┌────────────────────────────────┐ ┌──────────────────────────┐
│        Domain Services         │ │    Storage Adapters      │
│ `src/domain/diary.ts`          │ │ `src/storage/`           │
│ `src/domain/food.ts`           │ │ `diaryRepository.ts`    │
│ `src/domain/health.ts`         │ │ `healthRepository.ts`   │
│ `src/domain/library.ts`        │ │ `libraryRepository.ts`  │
│ `src/domain/insights.ts`       │ │ `localDiary.ts`          │
└────────────────────────────────┘ └─────────────┬────────────┘
                                                 │
                                                 ▼
                                   ┌──────────────────────────┐
                                   │  Local SQLite KV Engine  │
                                   │  `expo-sqlite/kv-store`  │
                                   └──────────────────────────┘
```

## Component Responsibilities

| Component | Responsibility | File |
|-----------|----------------|------|
| `RootLayout` | Splash screen hold, theme provider mounting, global navigation stack configuration | `apps/mobile/app/_layout.tsx` |
| `TabLayout` | Bottom tab bar orchestration (Today, Diary, Calendar, Progress, Profile) | `apps/mobile/app/(tabs)/_layout.tsx` |
| `DiaryProvider` | In-memory diary state, memoized date index, serialized write coordination | `apps/mobile/src/state/DiaryProvider.tsx` |
| `HealthProvider` | In-memory weight, height, and goal state, draft locking, write queuing | `apps/mobile/src/state/HealthProvider.tsx` |
| `LibraryProvider` | In-memory custom foods, recipes, and favourites state | `apps/mobile/src/state/LibraryProvider.tsx` |
| `ThemeProvider` | System/Light/Dark appearance preferences and semantic design token dispatch | `apps/mobile/src/theme/ThemeProvider.tsx` |
| `diaryRepository` | Serialized read/validate/compare/write pipeline to SQLite KV | `apps/mobile/src/storage/diaryRepository.ts` |
| `healthRepository` | Serialized write and retry pipeline for health documents | `apps/mobile/src/storage/healthRepository.ts` |
| `libraryRepository`| Atomic custom food, recipe, and favourite persistence | `apps/mobile/src/storage/libraryRepository.ts` |
| `diaryDomain` | Pure local date calculations, entry validation, portion scaling, daily totals | `apps/mobile/src/domain/diary.ts` |
| `healthDomain` | BMI calculations, weight progress, target date resolution | `apps/mobile/src/domain/health.ts` |
| `libraryDomain` | Recipe aggregation, custom food conversions, recents ranking | `apps/mobile/src/domain/library.ts` |
| `insightsDomain` | Rolling range windows, target consistency, nutrient observations | `apps/mobile/src/domain/insights.ts` |
| `foodDomain` | Nutrient arithmetic, macro scaling, and static food fixture registry | `apps/mobile/src/domain/food.ts` |

## Pattern Overview

**Overall:** Layered Offline-First Architecture with Injected Repositories and Unidirectional Data Flow.

**Key Characteristics:**
- **Immutable Nutritional Snapshots:** Logged entries and recipe ingredients preserve independent snapshots of referenced nutrition at time of creation, preventing historical corruption when source food records are updated or deleted.
- **Fail-Closed Validation:** Strict domain assertion runs before serialization. Corrupted or unparseable documents halt mutations to preserve raw data for manual recovery rather than silently wiping storage.
- **Serialized Write Queue:** Single-promise write queues prevent race conditions and concurrent write hazards in the single-process SQLite KV store.

## Layers

**UI & Navigation Layer:**
- Purpose: Render screens, capture user input, manage modals, and handle screen-to-screen transitions.
- Location: `apps/mobile/app/` and `apps/mobile/src/screens/`
- Contains: React Native components, Expo Router layouts, screen views (`DashboardScreen`, `DiaryScreen`, `CalendarScreen`, `InsightsScreen`, etc.).
- Depends on: State Providers, Theme Tokens, Domain types.
- Used by: Mobile app runtime entry.

**State / Context Layer:**
- Purpose: Bridge persistent repositories with React UI components; provide reactivity and error/loading statuses.
- Location: `apps/mobile/src/state/` and `apps/mobile/src/theme/`
- Contains: `DiaryProvider.tsx`, `HealthProvider.tsx`, `LibraryProvider.tsx`, `ThemeProvider.tsx`.
- Depends on: Storage repositories and Domain logic.
- Used by: UI screens and components.

**Domain Logic Layer:**
- Purpose: Pure functional business rules, unit conversions, nutritional math, date manipulation, and data validation.
- Location: `apps/mobile/src/domain/`
- Contains: `diary.ts`, `food.ts`, `health.ts`, `library.ts`, `insights.ts`, `calendar.ts`, `dashboard.ts`.
- Depends on: No external libraries (pure TypeScript logic).
- Used by: State Providers, Storage Repositories, and Tests.

**Storage Layer:**
- Purpose: Manage persistence contracts, serialize read/write operations, handle versioning and error envelopes.
- Location: `apps/mobile/src/storage/` and `apps/mobile/src/cloud/`
- Contains: `diaryRepository.ts`, `healthRepository.ts`, `libraryRepository.ts`, `localDiary.ts`, `checkpointRepository.ts`.
- Depends on: `expo-sqlite/kv-store` and Domain validators.
- Used by: State Providers.

## Data Flow

### Primary Request Path (Logging a Meal)

1. User selects food or recipe in `FoodSearchScreen.tsx` or `RecipeScreen.tsx` (`apps/mobile/src/screens/FoodSearchScreen.tsx`).
2. Selection is converted to an uncommitted draft via `foodDraftReducer` with default portion calculation (`apps/mobile/src/domain/library.ts`).
3. User confirms portion and meal category in `DiaryEntryScreen.tsx` (`apps/mobile/src/screens/DiaryEntryScreen.tsx`).
4. `createEntry` creates an immutable `DiaryEntry` containing food metadata and scaled nutrients (`apps/mobile/src/domain/diary.ts`).
5. `DiaryProvider.save(entry)` delegates to `diaryRepository.save` (`apps/mobile/src/storage/diaryRepository.ts`).
6. `diaryRepository` queues the write, re-reads existing SQLite KV document `bites2go.diary.v1`, asserts schema validity, and replaces the document atomically.
7. Upon successful write resolution, `DiaryProvider` updates its in-memory entries snapshot and refreshes memoized date index `indexDiaryDates`.
8. UI screens (`DashboardScreen`, `DiaryScreen`, `CalendarScreen`) re-render with updated nutrition totals.

### Health & Weight Tracking Path

1. User submits weight in `WeightEntryScreen.tsx` (`apps/mobile/src/screens/WeightEntryScreen.tsx`).
2. Input is validated for positive finite numbers and non-future date bounds (`apps/mobile/src/domain/health.ts`).
3. `HealthProvider.saveWeight` pushes the record into `bites2go.health.v1` via `healthRepository.ts` (`apps/mobile/src/storage/healthRepository.ts`).
4. Progress views update BMI and weight graphs (`apps/mobile/src/components/WeightChart.tsx`).

**State Management:**
- React Context + useReducer / useState for top-level provider state.
- No third-party state libraries (Redux, Zustand, MobX) — keeping runtime footprint minimal and deterministic.

## Key Abstractions

**Injected Storage Interface (`DiaryStorage`):**
- Purpose: Decouples domain repository logic from physical SQLite implementation, enabling clean in-memory test mocks.
- Examples: `apps/mobile/src/storage/diaryRepository.ts#L3-L6`
- Pattern: Inversion of Control / Repository Pattern.

**Nutritional Snapshot (`FoodNutrients`):**
- Purpose: Stores calories, protein, carbs, fat, fiber as explicit numbers or nulls, ensuring calculations never infer macros from calories or vice versa.
- Examples: `apps/mobile/src/domain/food.ts#L1-L8`
- Pattern: Value Object / Data Transfer Object.

**Versioned Document Container:**
- Purpose: Encapsulates persisted data with a numeric `version` tag for future forward-migration compatibility.
- Examples: `{ version: 1, entries: DiaryEntry[] }` in `apps/mobile/src/storage/diaryRepository.ts#L27`.
- Pattern: Document Versioning / Envelope Pattern.

## Entry Points

**Expo Router Root Entry:**
- Location: `apps/mobile/app/_layout.tsx`
- Triggers: Application boot on mobile device.
- Responsibilities: Mounts theme provider, holds splash screen until storage readiness, initializes navigation hierarchy.

**Dashboard Entry (Home Tab):**
- Location: `apps/mobile/app/(tabs)/index.tsx`
- Triggers: User launches app or navigates to Home tab.
- Responsibilities: Renders daily nutrition dashboard for current local date.

## Architectural Constraints

- **Single Writer Model:** Local persistence uses a serialized in-process queue. It does not support concurrent multi-threaded or multi-process writes.
- **Single Document KV Storage:** History is loaded and written as a whole JSON document per domain (`bites2go.diary.v1`). Scalability limit exists for very large multi-year histories before migrating to indexed SQL rows.
- **No Direct Cloud Writes:** Mobile client does not directly execute cloud queries or bypass local storage; all cloud operations are architected through staged checkpoints (`apps/mobile/src/cloud/diarySync.ts`).
- **Strict Date Separation:** Local calendar arithmetic uses device-local components (`getFullYear()`, `getMonth()`, `getDate()`) at noon, avoiding UTC timestamp drift across DST boundaries.

## Anti-Patterns

### Modifying Stored Entries When Source Foods Change

**What happens:** Re-fetching food fixtures to recalculate historical logs when food definitions are edited or deleted.
**Why it's wrong:** Alters user history, violates diet integrity, and causes historical totals to drift unexpectedly.
**Do this instead:** Store immutable nutrient snapshots inside each `DiaryEntry` at logging time (`apps/mobile/src/domain/diary.ts#L62-L64`).

### Inferring Caloric Totals from Macronutrients

**What happens:** Calculating calories as `4 * protein + 4 * carbs + 9 * fat`.
**Why it's wrong:** Disagrees with published packaging and authoritative food databases that account for specific fiber, alcohol, or organic acids.
**Do this instead:** Scale authoritative source calories directly using `scaleNutrients` (`apps/mobile/src/domain/food.ts#L25-L38`).

## Error Handling

**Strategy:** Fail-closed with retryable error states; never clear or overwrite corrupt stored data automatically.

**Patterns:**
- Re-read and validate document before writing (`apps/mobile/src/storage/diaryRepository.ts#L27`).
- Uncertain mutation handling: If an acknowledgement fails, retain payload for retry and prompt user to inspect stored state before navigating away (`apps/mobile/src/state/DiaryProvider.tsx`).
- Safe UI error messages that strip technical stack traces and confidential identifiers.

## Cross-Cutting Concerns

**Logging:** Sanitized development diagnostics; no production analytics or telemetry.
**Validation:** Pure domain validators (`assertEntry`, `validDateKey`, `validateHealth`) executed before any storage serialization.
**Authentication:** Prepared fail-closed Supabase integration; runs completely offline by default.

---

*Architecture analysis: 2026-10-30*
