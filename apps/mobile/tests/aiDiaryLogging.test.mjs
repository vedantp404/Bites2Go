import test from 'node:test';
import assert from 'node:assert/strict';
import {
  createAIDiaryEntry,
  assertEntry,
  editPortion,
} from '../src/domain/diary.ts';
import { createDiaryRepository } from '../src/storage/diaryRepository.ts';

function createMockStorage(initial = null) {
  const state = {
    raw: initial,
    writes: 0,
    failNextWrite: false,
  };
  const storage = {
    getItem: async () => state.raw,
    setItem: async (_key, value) => {
      state.writes++;
      if (state.failNextWrite) {
        state.failNextWrite = false;
        throw new Error('Simulated SQLite write failure');
      }
      state.raw = value;
    },
  };
  return { state, storage, repo: createDiaryRepository(storage) };
}

test('reproduces original bug: independently rounded reference vs nutrients throws Invalid nutrition snapshot', () => {
  // Original buggy implementation rounded reference and nutrients independently:
  const grams = 150;
  const refRatio = 100 / grams;
  const buggyEntry = {
    id: 'buggy-1',
    foodId: null,
    foodName: 'Scrambled Eggs',
    meal: 'Lunch',
    date: '2026-10-31',
    grams: 150,
    unit: 'g',
    referenceGrams: 100,
    reference: {
      calories: Math.round(140 * refRatio), // Math.round(93.333) = 93
      protein: Math.round(12.5 * refRatio * 10) / 10,
      carbs: Math.round(20 * refRatio * 10) / 10,
      fat: Math.round(5.5 * refRatio * 10) / 10,
      fiber: 0,
    },
    nutrients: {
      calories: Math.round(140), // 140 (expected from reference 93 * 1.5 is 139.5!)
      protein: Math.round(12.5 * 10) / 10,
      carbs: Math.round(20 * 10) / 10,
      fat: Math.round(5.5 * 10) / 10,
      fiber: 0,
    },
    preparation: 'Recognized by Gemini AI',
    source: 'Gemini AI',
    status: 'illustrative',
    createdAt: '2026-10-31T12:00:00.000Z',
    updatedAt: '2026-10-31T12:00:00.000Z',
  };

  assert.throws(
    () => assertEntry(buggyEntry),
    /Invalid nutrition snapshot/,
    'Buggy independent rounding should trigger Invalid nutrition snapshot',
  );
});

test('createAIDiaryEntry: AI results log successfully without Invalid nutrition snapshot error', async () => {
  const { repo } = createMockStorage();

  const entry = createAIDiaryEntry({
    id: 'ai-lunch-1',
    foodName: 'Grilled Chicken Breast',
    meal: 'Lunch',
    date: '2026-10-31',
    grams: 150,
    calories: 248,
    protein: 46.5,
    carbs: 0,
    fat: 5.4,
  });

  assert.doesNotThrow(() => assertEntry(entry));
  assert.equal(entry.foodName, 'Grilled Chicken Breast');
  assert.equal(entry.grams, 150);
  assert.equal(entry.meal, 'Lunch');
  assert.equal(entry.nutrients.calories, 248);

  // Save into repository
  await repo.save(entry);
  const loaded = await repo.loadDate('2026-10-31');
  assert.equal(loaded.length, 1);
  assert.equal(loaded[0].id, 'ai-lunch-1');
  assert.equal(loaded[0].nutrients.protein, 46.5);
});

test('decimal nutrition: handles fractional macros (e.g. 4.5g protein) with exact precision', () => {
  const entry = createAIDiaryEntry({
    id: 'ai-decimal-1',
    foodName: 'Greek Yogurt with Berries',
    meal: 'Breakfast',
    date: '2026-10-31',
    grams: 73.5,
    calories: 45.2,
    protein: 4.5,
    carbs: 5.8,
    fat: 0.3,
    fiber: 1.1,
  });

  assert.doesNotThrow(() => assertEntry(entry));
  assert.equal(entry.nutrients.protein, 4.5);
  assert.equal(entry.nutrients.fat, 0.3);
  assert.equal(entry.nutrients.fiber, 1.1);
});

test('edited portions: subsequent portion adjustments preserve proportional nutrition calculations', () => {
  const initial = createAIDiaryEntry({
    id: 'ai-portion-1',
    foodName: 'Steamed Rice',
    meal: 'Dinner',
    date: '2026-10-31',
    grams: 100,
    calories: 130,
    protein: 2.7,
    carbs: 28.2,
    fat: 0.3,
  });

  // Edit portion to 200g
  const now = '2026-10-31T13:00:00.000Z';
  const edited200 = editPortion(initial, 200, now);
  assert.doesNotThrow(() => assertEntry(edited200));
  assert.equal(edited200.grams, 200);
  assert.equal(edited200.nutrients.calories, 260);
  assert.equal(edited200.nutrients.protein, 5.4);
  assert.equal(edited200.nutrients.carbs, 56.4);
  assert.equal(edited200.nutrients.fat, 0.6);

  // Edit portion to 50g
  const edited50 = editPortion(initial, 50, now);
  assert.doesNotThrow(() => assertEntry(edited50));
  assert.equal(edited50.grams, 50);
  assert.equal(edited50.nutrients.calories, 65);
  assert.equal(edited50.nutrients.protein, 1.35);
});

test('validation safety: rejects empty names, non-positive grams, negative macros, and invalid dates', () => {
  const validBase = {
    id: 'valid-1',
    foodName: 'Apple',
    meal: 'Snacks',
    date: '2026-10-31',
    grams: 100,
    calories: 52,
    protein: 0.3,
    carbs: 14,
    fat: 0.2,
  };

  // Empty food name
  assert.throws(
    () => createAIDiaryEntry({ ...validBase, foodName: '   ' }),
    /Food name cannot be empty/,
  );

  // Zero or negative grams
  assert.throws(
    () => createAIDiaryEntry({ ...validBase, grams: 0 }),
    /Portion must be a positive number of grams/,
  );
  assert.throws(
    () => createAIDiaryEntry({ ...validBase, grams: -50 }),
    /Portion must be a positive number of grams/,
  );
  assert.throws(
    () => createAIDiaryEntry({ ...validBase, grams: NaN }),
    /Portion must be a positive number of grams/,
  );

  // Negative nutrients
  assert.throws(
    () => createAIDiaryEntry({ ...validBase, calories: -10 }),
    /Calories must be a non-negative finite number/,
  );
  assert.throws(
    () => createAIDiaryEntry({ ...validBase, protein: -1 }),
    /Protein must be a non-negative finite number/,
  );

  // Invalid meal
  assert.throws(
    () => createAIDiaryEntry({ ...validBase, meal: 'InvalidMeal' }),
    /Invalid meal category/,
  );

  // Invalid date
  assert.throws(
    () => createAIDiaryEntry({ ...validBase, date: 'not-a-date' }),
    /Invalid diary date/,
  );
});

test('atomic saveAll: saves multi-item meals without partial entries or duplicates on retry', async () => {
  const { state, repo } = createMockStorage();

  const item1 = createAIDiaryEntry({
    id: 'meal-item-1',
    foodName: 'Grilled Chicken Breast',
    meal: 'Lunch',
    date: '2026-10-31',
    grams: 150,
    calories: 248,
    protein: 46.5,
    carbs: 0,
    fat: 5.4,
  });

  const item2 = createAIDiaryEntry({
    id: 'meal-item-2',
    foodName: 'Brown Rice',
    meal: 'Lunch',
    date: '2026-10-31',
    grams: 120,
    calories: 133,
    protein: 2.7,
    carbs: 27.6,
    fat: 1.0,
  });

  const item3 = createAIDiaryEntry({
    id: 'meal-item-3',
    foodName: 'Steamed Broccoli',
    meal: 'Lunch',
    date: '2026-10-31',
    grams: 80,
    calories: 28,
    protein: 2.3,
    carbs: 5.6,
    fat: 0.3,
  });

  // 1. Save all 3 items atomically in one operation
  await repo.saveAll([item1, item2, item3]);
  assert.equal(state.writes, 1, 'All items saved in a single atomic write');

  const loaded = await repo.loadDate('2026-10-31');
  assert.equal(loaded.length, 3);
  assert.deepEqual(
    loaded.map((e) => e.foodName),
    ['Grilled Chicken Breast', 'Brown Rice', 'Steamed Broccoli'],
  );

  // 2. Retry with exact same items (idempotent retry): no duplicates created
  await repo.saveAll([item1, item2, item3]);
  const loadedAfterRetry = await repo.loadDate('2026-10-31');
  assert.equal(
    loadedAfterRetry.length,
    3,
    'Retry must not duplicate existing entries',
  );

  // 3. Simulated storage write failure: no partial entries
  state.failNextWrite = true;
  const newItem = createAIDiaryEntry({
    id: 'meal-item-4',
    foodName: 'Avocado',
    meal: 'Lunch',
    date: '2026-10-31',
    grams: 50,
    calories: 80,
    protein: 1,
    carbs: 4,
    fat: 7,
  });

  await assert.rejects(
    () => repo.saveAll([newItem]),
    /Could not confirm the diary write/,
  );

  // The diary must still contain only the original 3 items, perfectly intact
  const finalLoaded = await repo.loadDate('2026-10-31');
  assert.equal(finalLoaded.length, 3);
});

test('mixed Indian meal: logs Roti, Dal, Basmati Rice, and Bhindi with exact portion scaling and atomicity', async () => {
  const { repo } = createMockStorage();

  const roti = createAIDiaryEntry({
    id: 'thali-roti-1',
    foodName: 'Whole Wheat Roti',
    meal: 'Dinner',
    date: '2026-10-31',
    grams: 70, // 2 rotis
    calories: 190,
    protein: 6.2,
    carbs: 38.5,
    fat: 1.4,
  });

  const dal = createAIDiaryEntry({
    id: 'thali-dal-1',
    foodName: 'Yellow Dal Tadka',
    meal: 'Dinner',
    date: '2026-10-31',
    grams: 180, // 1 katori
    calories: 154,
    protein: 9.3,
    carbs: 21.2,
    fat: 4.1,
  });

  const rice = createAIDiaryEntry({
    id: 'thali-rice-1',
    foodName: 'Steamed Basmati Rice',
    meal: 'Dinner',
    date: '2026-10-31',
    grams: 150,
    calories: 195,
    protein: 4.1,
    carbs: 43.2,
    fat: 0.5,
  });

  const bhindi = createAIDiaryEntry({
    id: 'thali-bhindi-1',
    foodName: 'Bhindi Masala (Okra Sabzi)',
    meal: 'Dinner',
    date: '2026-10-31',
    grams: 120,
    calories: 112,
    protein: 2.8,
    carbs: 12.4,
    fat: 6.2,
  });

  // Verify all 4 entries validate against diary snapshot integrity
  assert.doesNotThrow(() => assertEntry(roti));
  assert.doesNotThrow(() => assertEntry(dal));
  assert.doesNotThrow(() => assertEntry(rice));
  assert.doesNotThrow(() => assertEntry(bhindi));

  // Save all 4 items to Dinner
  await repo.saveAll([roti, dal, rice, bhindi]);

  const loaded = await repo.loadDate('2026-10-31');
  assert.equal(loaded.length, 4);

  // Total dinner nutrition calculation
  const totalCalories = loaded.reduce(
    (sum, e) => sum + e.nutrients.calories,
    0,
  );
  const totalProtein = loaded.reduce((sum, e) => sum + e.nutrients.protein, 0);
  assert.equal(totalCalories, 651);
  assert.equal(Math.round(totalProtein * 10) / 10, 22.4);
});

test('ambiguous dish alternative & portion editing: switching dish name and adjusting portion preserves assertEntry integrity', () => {
  // Candidate initially detected as ambiguous "Paneer Butter Masala" with alternative "Tofu Tikka Masala"
  const originalEntry = createAIDiaryEntry({
    id: 'curry-1',
    foodName: 'Paneer Butter Masala',
    meal: 'Lunch',
    date: '2026-10-31',
    grams: 200,
    calories: 320,
    protein: 12,
    carbs: 16,
    fat: 24,
  });

  // User taps alternative chip to switch foodName to "Tofu Tikka Masala" and updates portion to 150g
  const switchedAndEdited = editPortion(
    {
      ...originalEntry,
      foodName: 'Tofu Tikka Masala',
    },
    150,
    new Date().toISOString(),
  );

  assert.doesNotThrow(() => assertEntry(switchedAndEdited));
  assert.equal(switchedAndEdited.foodName, 'Tofu Tikka Masala');
  assert.equal(switchedAndEdited.grams, 150);
  assert.equal(switchedAndEdited.nutrients.calories, 240);
  assert.equal(switchedAndEdited.nutrients.protein, 9);
  assert.equal(switchedAndEdited.nutrients.carbs, 12);
  assert.equal(switchedAndEdited.nutrients.fat, 18);
});
