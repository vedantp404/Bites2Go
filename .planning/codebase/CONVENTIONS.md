---
last_mapped_commit: f54c1f195289ce4d54a79e7def2170fb84f20858
last_mapped_at: 2026-10-30
---
# Coding Conventions

**Analysis Date:** 2026-10-30

## Naming Patterns

**Files:**
- Component & screen files: PascalCase (e.g. `apps/mobile/src/screens/DashboardScreen.tsx`, `apps/mobile/src/components/InsightChart.tsx`).
- Route files: kebab-case (e.g. `apps/mobile/app/custom-food.tsx`, `apps/mobile/app/diary-entry.tsx`).
- Domain, state, and utility files: camelCase (e.g. `apps/mobile/src/domain/diary.ts`, `apps/mobile/src/storage/diaryRepository.ts`).
- Test files: `.test.mjs` suffix with module descriptor (e.g. `apps/mobile/tests/diary.test.mjs`).

**Functions:**
- camelCase for functions and methods (e.g. `scaleNutrients`, `createEntry`, `validDateKey`, `loadDate`).
- Factory functions prefixed with `create` (e.g. `createDiaryRepository`, `createEntry`).
- Validation predicates prefixed with `assert` (for throwing) or `is`/`valid` (for type guards): e.g. `assertEntry`, `validDateKey`.

**Variables:**
- camelCase for regular variables, properties, and parameters (e.g. `foodId`, `selectedDate`, `portionGrams`).
- UPPER_SNAKE_CASE for constant values or static sets (e.g. `EXPO_PUBLIC_SUPABASE_URL`).

**Types:**
- PascalCase for type aliases and interfaces (e.g. `DiaryEntry`, `FoodNutrients`, `DiaryStorage`, `WeightRecord`).
- Discriminated union status literals: lowercase strings (e.g. `status: 'illustrative' | 'verified'`).

## Code Style

**Formatting:**
- Prettier 3.9.10 configured in `apps/mobile/.prettierrc.json`.
- Settings: `{ "singleQuote": true, "trailingComma": "all" }`.
- Run command: `npm run format --prefix apps/mobile` and `npm run format:check --prefix apps/mobile`.

**Linting:**
- ESLint 9.39.5 with flat config in `apps/mobile/eslint.config.js`.
- Key rules: `eslint-config-expo/flat`, ignores `dist/**`.
- Run command: `npm run lint --prefix apps/mobile`.

## Import Organization

**Order:**
1. React / React Native built-in packages (`react`, `react-native`, `expo-*`).
2. Third-party libraries (`react-native-svg`, etc.).
3. Project domain and utility imports with explicit extensions:
   - Notice: `apps/mobile/tsconfig.json` enables `allowImportingTsExtensions: true`.
   - Domain imports in TypeScript files use explicit `.ts` extensions: `import { scaleNutrients } from './food.ts';`.
   - Node tests (`.mjs`) import directly from `../src/domain/*.ts` without a compilation step.
4. Type-only imports using `import type { ... }`:
   - e.g. `import type { DiaryEntry } from '../domain/diary.ts';`.

**Path Aliases:**
- Relative paths (`./`, `../`) are standard throughout `apps/mobile/src/`. No ambiguous path aliases configured.

## Error Handling

**Patterns:**
- **Explicit Domain Guarding:** Functions throw descriptive `Error` objects on invalid input rather than returning `null` or NaN (e.g. `if (!validDateKey(key)) throw new Error('Invalid diary date.');` in `apps/mobile/src/domain/diary.ts`).
- **Data Preservation on Corrupted Read:** Storage repositories wrap JSON decoding in try/catch and abort operations without clearing the stored key, preventing accidental data loss:
  ```typescript
  try {
    return decodeDiary(await storage.getItem(diaryKey));
  } catch {
    throw new Error('Cannot read the diary. Stored data was not cleared. Retry; if this persists, keep app data intact for recovery.');
  }
  ```
- **Uncertain Write Reconciliation:** If a write acknowledgement fails, the uncommitted payload is preserved for idempotent retry. If the user exits, the app reloads the authoritative persisted state to avoid desynchronization (`apps/mobile/src/state/DiaryProvider.tsx`).
- **Sanitized UI Errors:** User-facing error banners display actionable instructions without leaking file paths or internal runtime traces.

## Logging

**Framework:** Built-in `console.warn` and `console.error` for development diagnostics only.
**Patterns:**
- No sensitive user data (nutritional diary entries, weights, tokens) in log output.
- Native error objects are sanitized before logging (e.g. in `apps/mobile/app/_layout.tsx`).

## Comments

**When to Comment:**
- Document architectural shortcuts with `// shortcut: ...` comments (e.g. `// shortcut: a single document suits a small diary; migrate to indexed rows before large histories or sync.` in `apps/mobile/src/storage/diaryRepository.ts#L7`).
- Explain non-obvious domain boundaries (e.g. why midnight crossing must not alter open drafts, why calories are never computed from macronutrients).

**JSDoc/TSDoc:**
- Used selectively on exported public interface methods to document parameters and return types.

## Function Design

**Size:**
- Small, focused, pure domain functions (< 40 lines) residing in `apps/mobile/src/domain/`.

**Parameters:**
- Explicit positional arguments for pure functions (e.g. `createEntry(food, meal, date, grams, id, now)`).
- Destructured options objects for React component props and complex configurations.

**Return Values:**
- Deterministic, immutable objects.
- Collections return new array copies rather than mutating inputs.

## Module Design

**Exports:**
- Named exports preferred (`export function ...`, `export const ...`, `export type ...`).
- Default exports used strictly for Expo Router screens and layouts as required by framework conventions (`export default function ...Screen()`).

**Barrel Files:**
- Avoid sprawling index barrel re-exports; import directly from the target module to maintain tree-shaking efficiency and clean dependency boundaries.

---

*Convention analysis: 2026-10-30*
