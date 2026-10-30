---
last_mapped_commit: f54c1f195289ce4d54a79e7def2170fb84f20858
last_mapped_at: 2026-10-30
---
# Testing Patterns

**Analysis Date:** 2026-10-30

## Test Framework

**Runner:**
- Node.js built-in test runner (`node:test`, `node:assert/strict`).
- Dependency-free testing without third-party frameworks (no Jest, Vitest, or Mocha).
- Config: Defined in `apps/mobile/package.json`:
  ```json
  "test": "node --experimental-strip-types --test tests/*.test.mjs"
  ```

**Assertion Library:**
- `node:assert/strict`

**Run Commands:**
```bash
npm test --prefix apps/mobile                           # Run all 98 unit & integration tests
node --experimental-strip-types --test tests/diary.test.mjs # Run a specific test file from apps/mobile
npm run typecheck --prefix apps/mobile                  # Check TypeScript types
npm run lint --prefix apps/mobile                       # Check ESLint rules
npm run doctor --prefix apps/mobile                     # Verify Expo package health
./scripts/test-cloud-sql.ps1                            # Run PostgreSQL RLS and RPC integration tests
python scripts/security-scan.py                         # Run credential and secret scanning script
```

## Test File Organization

**Location:**
- Mobile test suites: `apps/mobile/tests/`.
- Backend SQL policy tests: `supabase/tests/`.

**Naming:**
- Filename pattern: `[feature].test.mjs` using ESM format.

**Structure:**
```
apps/mobile/tests/
├── appearance.test.mjs     # Theme tokens, system appearance observer, contrast assertions
├── calendar.test.mjs       # Monday-first grid alignment, leap years, timezone/midnight boundaries
├── cloud.test.mjs          # Fail-closed public config, offline sync planning, merge rules
├── dashboard.test.mjs      # Dashboard card summaries, progress meters, target comparisons
├── diary.test.mjs          # Local date keys, entry CRUD, SQLite KV persistence, corrupt-read safety
├── food.test.mjs           # Portion math, nutrient scaling, zero/null/overflow edge cases
├── health.test.mjs         # Weight records, BMI, effective-dated targets, SQLite close/reopen
├── insights.test.mjs       # Rolling ranges, target consistency, exclusion of today and incomplete days
├── library.test.mjs        # Custom foods, recipes with snapshots, favourites, recents ranking
└── theme.test.mjs          # WCAG AA contrast ratio compliance for all semantic color pairs
```

## Test Structure

**Suite Organization:**
```javascript
import test from 'node:test';
import assert from 'node:assert/strict';
import { createEntry, diaryTotals } from '../src/domain/diary.ts';
import { createDiaryRepository } from '../src/storage/diaryRepository.ts';
import { foods } from '../src/data/foods.ts';

test('dates and all meal categories remain separate; no demo seed consumption', async () => {
  const { repo } = memory();
  for (const meal of ['Breakfast', 'Lunch', 'Snacks', 'Dinner']) {
    await repo.save(entry(meal, '2026-10-29', meal));
  }
  await repo.save(entry());
  assert.equal((await repo.loadDate('2026-10-29')).length, 4);
  assert.equal((await repo.loadDate('2026-10-30')).length, 1);
  assert.deepEqual(await repo.loadDate('2026-10-28'), []);
});
```

**Patterns:**
- **In-Memory Storage Simulator:** Tests create an in-memory test double of the `DiaryStorage` interface tracking reads, writes, and error injections:
  ```javascript
  function memory(raw = null) {
    const state = { raw, readError: false, writeError: false, writes: 0 };
    const storage = {
      getItem: async () => {
        if (state.readError) throw Error('read');
        return state.raw;
      },
      setItem: async (_key, value) => {
        state.writes++;
        if (state.writeError) throw Error('write');
        state.raw = value;
      },
    };
    return { state, storage, repo: createDiaryRepository(storage) };
  }
  ```
- **Temporary Real SQLite Close/Reopen:** Key test suites (such as `apps/mobile/tests/diary.test.mjs`, `apps/mobile/tests/health.test.mjs`, `apps/mobile/tests/library.test.mjs`) spawn a temporary native SQLite database on disk, write real documents, close the database connection, reopen it, and assert snapshot preservation.
- **Strict Equality & Deep Diffs:** `assert.deepEqual` and `assert.equal` are used throughout to enforce exact object shapes.

## Mocking

**Framework:** None. Pure JavaScript closures and dependency injection.

**Patterns:**
- Custom storage interfaces (`getItem`, `setItem`) are injected into repository factories (`createDiaryRepository`, `createHealthRepository`, `createLibraryRepository`).
- Timers and dates passed as explicit string timestamps (e.g. `const now = '2026-10-30T12:00:00.000Z'`).

**What to Mock:**
- Storage layer implementations (`expo-sqlite/kv-store`).
- Network responses and Supabase PostgREST endpoints (`apps/mobile/tests/cloud.test.mjs`).

**What NOT to Mock:**
- Domain arithmetic (`scaleNutrients`, `sumNutrients`, `diaryTotals`).
- Local date parsing and shift logic (`localDateKey`, `shiftDay`).
- Recipe and custom food formulas.
- Accessibility contrast evaluation (`apps/mobile/tests/theme.test.mjs`).

## Fixtures and Factories

**Test Data:**
- Authoritative static food fixture catalogue: `apps/mobile/src/data/foods.ts`.
- Entry factory helper:
  ```javascript
  const entry = (id = 'one', date = '2026-10-30', meal = 'Lunch') =>
    createEntry(foods[0], meal, date, 200, id, '2026-10-30T12:00:00.000Z');
  ```

**Location:**
- Shared fixtures: `apps/mobile/src/data/foods.ts`.
- Test-specific builders: defined locally at the top of each `.test.mjs` file.

## Coverage

**Requirements:**
- High branch coverage across domain logic, calculations, date bounds, and storage error conditions.
- 98 automated unit/integration tests running in ~600 ms.

**View Coverage:**
- Node test runner supports `--experimental-test-coverage`.

## Test Types

**Unit Tests:**
- Validate pure functions in `apps/mobile/src/domain/` (nutrient math, date boundaries, leap century handling, BMI, custom serving conversions).
- Contrast ratio assertions in `apps/mobile/tests/theme.test.mjs` verifying WCAG AA standards.

**Integration Tests:**
- Validate repository serialization, stale-write detection, uncertain write retries, and corrupted document preservation.
- Temporary real SQLite lifecycle verification (close and reopen).
- Supabase SQL policy integration via `scripts/test-cloud-sql.ps1`.

**E2E / Native Tests:**
- Not automated via CI. Documented as physical Android acceptance checklist in `docs/TEST_PLAN.md`.

## Common Patterns

**Async Testing:**
```javascript
test('failed write retains payload and allows idempotent retry', async () => {
  const { state, repo } = memory();
  state.writeError = true;
  await assert.rejects(() => repo.save(entry()), /write/);
  state.writeError = false;
  await repo.save(entry());
  assert.equal((await repo.loadAll()).length, 1);
});
```

**Error Testing:**
```javascript
test('validation rejects invalid date keys', () => {
  assert.throws(() => shiftDay('not-a-date', 1), /Invalid diary date/);
  assert.throws(() => shiftDay('2026-02-31', 1), /Invalid diary date/);
});
```

---

*Testing analysis: 2026-10-30*
