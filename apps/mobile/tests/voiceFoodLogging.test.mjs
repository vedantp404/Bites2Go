import test from 'node:test';
import assert from 'node:assert/strict';
import {
  matchVoiceItemsToCatalogue,
  buildDiaryEntriesFromVoiceCandidates,
  buildAvailableFoodPool,
} from '../src/services/voiceFoodLogging.ts';
import { assertEntry } from '../src/domain/diary.ts';
import { unifiedFoods } from '../src/data/unifiedFoods.ts';
import { emptyLibrary } from '../src/domain/library.ts';

test('buildAvailableFoodPool: merges unified catalogue with custom foods and recipes', () => {
  const library = emptyLibrary();
  library.customFoods.push({
    id: 'custom:protein-smoothie',
    name: 'Home Protein Smoothie',
    description: 'Whey and berries',
    servingGrams: 300,
    servingNutrients: {
      calories: 250,
      protein: 30,
      carbs: 20,
      fat: 3,
      fiber: 4,
    },
    createdAt: '2026-10-31T10:00:00.000Z',
    updatedAt: '2026-10-31T10:00:00.000Z',
  });

  const pool = buildAvailableFoodPool(library, unifiedFoods);
  assert.ok(pool.length > unifiedFoods.length);
  const found = pool.find((f) => f.id === 'custom:protein-smoothie');
  assert.ok(found);
  assert.equal(found.name, 'Home Protein Smoothie');
  assert.equal(found.category, 'Custom');
});

test('matchVoiceItemsToCatalogue: matches common foods and preserves dataset-first priority', () => {
  const pool = buildAvailableFoodPool(null, unifiedFoods);

  const parsedItems = [
    {
      food_description: 'Scrambled Eggs',
      quantity: 2,
      unit: 'eggs',
      preparation: 'scrambled',
      state: 'cooked',
      estimated_grams: 100,
      calories: 140,
      protein: 12,
      carbohydrates: 1.5,
      fat: 9.5,
      confidence: 0.95,
      confidence_level: 'high',
      alternatives: ['Omelette'],
      notes: null,
    },
    {
      food_description: 'Roti',
      quantity: 2,
      unit: 'pieces',
      preparation: 'whole wheat flatbread',
      state: 'cooked',
      estimated_grams: 70,
      calories: 190,
      protein: 6,
      carbohydrates: 38,
      fat: 2,
      confidence: 0.92,
      confidence_level: 'high',
      alternatives: ['Chapati', 'Phulka'],
      notes: null,
    },
    {
      food_description: 'Steamed Basmati Rice',
      quantity: 1,
      unit: 'cup',
      preparation: 'steamed plain',
      state: 'cooked',
      estimated_grams: 150,
      calories: 195,
      protein: 4,
      carbohydrates: 42,
      fat: 0.5,
      confidence: 0.9,
      confidence_level: 'high',
      alternatives: ['Plain Rice'],
      notes: null,
    },
  ];

  const matched = matchVoiceItemsToCatalogue(parsedItems, pool);
  assert.equal(matched.length, 3);

  // Scrambled Eggs
  assert.ok(matched[0].availableMatches.length > 0);
  assert.equal(matched[0].estimated_grams, 100);

  // Roti
  assert.ok(matched[1].availableMatches.length > 0);
  assert.ok(
    matched[1].availableMatches.some(
      (m) =>
        m.name.toLowerCase().includes('roti') ||
        m.name.toLowerCase().includes('chapati'),
    ),
  );

  // Rice
  assert.ok(matched[2].availableMatches.length > 0);
  assert.ok(
    matched[2].availableMatches.some((m) =>
      m.name.toLowerCase().includes('rice'),
    ),
  );
});

test('matchVoiceItemsToCatalogue: handles raw vs cooked items with correct state and nutrients', () => {
  const pool = buildAvailableFoodPool(null, unifiedFoods);

  const rawItem = {
    food_description: 'Raw Chicken Breast',
    quantity: 100,
    unit: 'gram',
    preparation: 'uncooked',
    state: 'raw',
    estimated_grams: 100,
    calories: 120,
    protein: 26,
    carbohydrates: 0,
    fat: 1.5,
    confidence: 0.95,
    confidence_level: 'high',
    alternatives: [],
    notes: null,
  };

  const matched = matchVoiceItemsToCatalogue([rawItem], pool);
  assert.equal(matched.length, 1);
  assert.equal(matched[0].state, 'raw');
  assert.equal(matched[0].calories, 120);
  assert.equal(matched[0].protein, 26);
});

test('buildDiaryEntriesFromVoiceCandidates: builds verified catalogue entries and AI entries atomically', () => {
  const pool = buildAvailableFoodPool(null, unifiedFoods);
  const rotiMatch = pool.find(
    (f) =>
      f.name.toLowerCase() === 'roti' || f.name.toLowerCase().includes('roti'),
  );
  assert.ok(rotiMatch, 'Catalogue must contain roti');

  const candidates = [
    {
      id: 'voice-1',
      stableEntryId: 'entry-uuid-1',
      originalParsedItem: {
        food_description: 'Roti',
        quantity: 2,
        unit: 'pieces',
        state: 'cooked',
        estimated_grams: 70,
        calories: 190,
        protein: 6,
        carbohydrates: 38,
        fat: 2,
        confidence: 0.9,
        confidence_level: 'high',
        alternatives: [],
      },
      food_name: rotiMatch.name,
      quantity: 2,
      unit: 'pieces',
      estimated_grams: 70,
      calories: 190,
      protein: 6,
      carbohydrates: 38,
      fat: 2,
      state: 'cooked',
      preparation: rotiMatch.preparation,
      notes: '',
      confidence: 0.9,
      confidence_level: 'high',
      matchedCatalogueFood: rotiMatch,
      availableMatches: [rotiMatch],
      sourceMode: 'catalogue',
      reference: { ...rotiMatch.nutrients },
    },
    {
      id: 'voice-2',
      stableEntryId: 'entry-uuid-2',
      originalParsedItem: {
        food_description: 'Special Homestyle Bhindi Masala',
        quantity: 1,
        unit: 'bowl',
        state: 'cooked',
        estimated_grams: 150,
        calories: 140,
        protein: 3.5,
        carbohydrates: 15,
        fat: 7,
        confidence: 0.85,
        confidence_level: 'high',
        alternatives: [],
      },
      food_name: 'Special Homestyle Bhindi Masala',
      quantity: 1,
      unit: 'bowl',
      estimated_grams: 150,
      calories: 140,
      protein: 3.5,
      carbohydrates: 15,
      fat: 7,
      state: 'cooked',
      preparation: 'Cooked with onion, tomato and spices',
      notes: '',
      confidence: 0.85,
      confidence_level: 'high',
      matchedCatalogueFood: null,
      availableMatches: [],
      sourceMode: 'ai',
      reference: {
        calories: (140 / 150) * 100,
        protein: (3.5 / 150) * 100,
        carbs: (15 / 150) * 100,
        fat: (7 / 150) * 100,
        fiber: 0,
      },
    },
  ];

  const entries = buildDiaryEntriesFromVoiceCandidates(
    candidates,
    'Dinner',
    '2026-10-31',
  );
  assert.equal(entries.length, 2);

  // Item 1: Catalogue entry
  const entry1 = entries[0];
  assert.doesNotThrow(() => assertEntry(entry1));
  assert.equal(entry1.foodId, rotiMatch.id);
  assert.equal(entry1.status, rotiMatch.status);
  assert.equal(entry1.grams, 70);
  assert.equal(entry1.meal, 'Dinner');
  assert.equal(entry1.date, '2026-10-31');

  // Item 2: AI entry
  const entry2 = entries[1];
  assert.doesNotThrow(() => assertEntry(entry2));
  assert.equal(entry2.foodId, null);
  assert.equal(entry2.foodName, 'Special Homestyle Bhindi Masala');
  assert.equal(entry2.source, 'Gemini AI Voice Parser');
  assert.equal(entry2.status, 'illustrative');
  assert.equal(entry2.grams, 150);
  assert.equal(entry2.nutrients.calories, 140);
  assert.equal(entry2.nutrients.protein, 3.5);
});

test('buildDiaryEntriesFromVoiceCandidates: validation safety rejects invalid candidates before saving', () => {
  const invalidCandidates = [
    {
      id: 'bad-1',
      stableEntryId: 'bad-uuid',
      food_name: '   ', // empty name
      quantity: 1,
      unit: 'serving',
      estimated_grams: 100,
      calories: 100,
      protein: 10,
      carbohydrates: 10,
      fat: 5,
      state: 'unspecified',
      preparation: '',
      notes: '',
      confidence: 0.8,
      confidence_level: 'high',
      matchedCatalogueFood: null,
      availableMatches: [],
      sourceMode: 'ai',
      reference: { calories: 100, protein: 10, carbs: 10, fat: 5, fiber: 0 },
    },
  ];

  assert.throws(
    () =>
      buildDiaryEntriesFromVoiceCandidates(
        invalidCandidates,
        'Lunch',
        '2026-10-31',
      ),
    /Food name cannot be empty/,
  );

  // Non-positive grams
  invalidCandidates[0].food_name = 'Valid Name';
  invalidCandidates[0].estimated_grams = -50;
  assert.throws(
    () =>
      buildDiaryEntriesFromVoiceCandidates(
        invalidCandidates,
        'Lunch',
        '2026-10-31',
      ),
    /Portion for "Valid Name" must be a positive number of grams/,
  );

  // Negative calories
  invalidCandidates[0].estimated_grams = 100;
  invalidCandidates[0].calories = -10;
  assert.throws(
    () =>
      buildDiaryEntriesFromVoiceCandidates(
        invalidCandidates,
        'Lunch',
        '2026-10-31',
      ),
    /Nutritional values for "Valid Name" must be non-negative finite numbers/,
  );
});

test('portion adjustment & source toggle preserves mathematical consistency', () => {
  const pool = buildAvailableFoodPool(null, unifiedFoods);
  const dalItem = {
    food_description: 'Yellow Dal Tadka',
    quantity: 1,
    unit: 'bowl',
    preparation: 'cooked with cumin tadka',
    state: 'cooked',
    estimated_grams: 180,
    calories: 160,
    protein: 8.5,
    carbohydrates: 22,
    fat: 4.5,
    confidence: 0.9,
    confidence_level: 'high',
    alternatives: ['Moong Dal'],
    notes: null,
  };

  const matched = matchVoiceItemsToCatalogue([dalItem], pool);
  assert.equal(matched.length, 1);
  const cand = matched[0];

  // Adjust portion from 180g to 270g (1.5x)
  const newGrams = 270;
  const scaled = {
    ...cand,
    estimated_grams: newGrams,
    calories: (cand.calories / cand.estimated_grams) * newGrams,
    protein: (cand.protein / cand.estimated_grams) * newGrams,
    carbohydrates: (cand.carbohydrates / cand.estimated_grams) * newGrams,
    fat: (cand.fat / cand.estimated_grams) * newGrams,
  };

  const entries = buildDiaryEntriesFromVoiceCandidates(
    [scaled],
    'Lunch',
    '2026-10-31',
  );
  assert.equal(entries.length, 1);
  assert.doesNotThrow(() => assertEntry(entries[0]));
  assert.equal(entries[0].grams, 270);
  assert.equal(
    Math.round(entries[0].nutrients.calories),
    Math.round(cand.calories * 1.5),
  );
});

test('atomic repository saveAll: saves all voice entries or aborts without partial writes', async () => {
  const pool = buildAvailableFoodPool(null, unifiedFoods);
  const candidates = [
    {
      id: 'v1',
      stableEntryId: 'atomic-voice-1',
      food_name: 'Steamed Basmati Rice',
      quantity: 1,
      unit: 'cup',
      estimated_grams: 150,
      calories: 195,
      protein: 4,
      carbohydrates: 42,
      fat: 0.5,
      state: 'cooked',
      preparation: 'Steamed',
      notes: '',
      confidence: 0.9,
      confidence_level: 'high',
      matchedCatalogueFood:
        pool.find((f) => f.name.toLowerCase().includes('rice')) || null,
      availableMatches: [],
      sourceMode: 'ai',
      reference: {
        calories: 130,
        protein: 2.67,
        carbs: 28,
        fat: 0.33,
        fiber: 0,
      },
    },
    {
      id: 'v2',
      stableEntryId: 'atomic-voice-2',
      food_name: 'Dal Tadka',
      quantity: 1,
      unit: 'bowl',
      estimated_grams: 180,
      calories: 160,
      protein: 8.5,
      carbohydrates: 22,
      fat: 4.5,
      state: 'cooked',
      preparation: 'Lentil soup with tadka',
      notes: '',
      confidence: 0.9,
      confidence_level: 'high',
      matchedCatalogueFood: null,
      availableMatches: [],
      sourceMode: 'ai',
      reference: {
        calories: 88.9,
        protein: 4.7,
        carbs: 12.2,
        fat: 2.5,
        fiber: 0,
      },
    },
  ];

  const entries = buildDiaryEntriesFromVoiceCandidates(
    candidates,
    'Lunch',
    '2026-10-31',
  );

  // Create mock storage
  let rawStorage = null;
  const storage = {
    getItem: async () => rawStorage,
    setItem: async (_key, val) => {
      rawStorage = val;
    },
  };
  const { createDiaryRepository } =
    await import('../src/storage/diaryRepository.ts');
  const repo = createDiaryRepository(storage);

  // Successful saveAll
  await repo.saveAll(entries);
  const loaded = await repo.loadDate('2026-10-31');
  assert.equal(loaded.length, 2);
  assert.equal(loaded[0].id, 'atomic-voice-1');
  assert.equal(loaded[1].id, 'atomic-voice-2');

  // Verify failure rollback: if storage setItem fails, no corrupted writes persist
  let writeFailed = false;
  const failingStorage = {
    getItem: async () => rawStorage,
    setItem: async () => {
      writeFailed = true;
      throw new Error('Disk write error');
    },
  };
  const failingRepo = createDiaryRepository(failingStorage);

  const extraEntry = buildDiaryEntriesFromVoiceCandidates(
    [candidates[0]],
    'Dinner',
    '2026-10-31',
  )[0];
  extraEntry.id = 'extra-fail-entry';

  await assert.rejects(
    () => failingRepo.saveAll([extraEntry]),
    /Could not confirm the diary write/,
  );
  assert.equal(writeFailed, true);
  // Original storage was not overwritten
  const verifyOriginal = await repo.loadDate('2026-10-31');
  assert.equal(verifyOriginal.length, 2);
  assert.ok(!verifyOriginal.some((e) => e.id === 'extra-fail-entry'));
});
