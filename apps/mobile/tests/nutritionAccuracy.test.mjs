import test from 'node:test';
import assert from 'node:assert/strict';
import { foods } from '../src/data/foods.ts';
import { scaleNutrients } from '../src/domain/food.ts';
import { recipeNutrition } from '../src/domain/library.ts';
import { createEntry, diaryTotals, assertEntry } from '../src/domain/diary.ts';

test('catalogue data integrity: all 894 foods meet physical and nutritional bounds', () => {
  assert.equal(
    foods.length,
    894,
    'Exact catalogue size of 894 foods must be preserved',
  );

  const seenIds = new Set();
  const seenNames = new Set();

  for (const food of foods) {
    // Identity & metadata
    assert.ok(food.id && typeof food.id === 'string', `Invalid ID on food`);
    assert.ok(!seenIds.has(food.id), `Duplicate ID detected: ${food.id}`);
    seenIds.add(food.id);

    assert.ok(
      food.name && food.name.trim().length > 0,
      `Empty name for ${food.id}`,
    );
    const normName = food.name
      .toLowerCase()
      .trim()
      .replace(/[^a-z0-9]/g, '');
    assert.ok(
      !seenNames.has(normName),
      `Duplicate normalized food name: ${food.name}`,
    );
    seenNames.add(normName);

    assert.equal(
      food.referenceGrams,
      100,
      `Reference grams must be 100: ${food.id}`,
    );

    const { calories, protein, carbs, fat, fiber, sugar, sodium } =
      food.nutrients;

    // Non-negative and finite
    assert.ok(
      calories !== null && calories >= 0 && Number.isFinite(calories),
      `Invalid calories: ${food.id}`,
    );
    assert.ok(
      protein !== null && protein >= 0 && Number.isFinite(protein),
      `Invalid protein: ${food.id}`,
    );
    assert.ok(
      carbs !== null && carbs >= 0 && Number.isFinite(carbs),
      `Invalid carbs: ${food.id}`,
    );
    assert.ok(
      fat !== null && fat >= 0 && Number.isFinite(fat),
      `Invalid fat: ${food.id}`,
    );
    if (sodium !== undefined && sodium !== null) {
      assert.ok(
        sodium >= 0 && Number.isFinite(sodium),
        `Invalid sodium: ${food.id}`,
      );
    }

    // Physical law: Macronutrient sum per 100g cannot exceed 100g (allow 100.5g for minor 1-decimal rounding)
    const macroSum = protein + carbs + fat;
    assert.ok(
      macroSum <= 100.5,
      `Macronutrient sum (${macroSum.toFixed(1)}g) exceeds physical 100g bound in ${food.id}`,
    );

    // Sub-components must not exceed parent nutrients
    if (sugar !== null && sugar !== undefined) {
      assert.ok(
        sugar <= carbs + 0.1,
        `Sugar (${sugar}g) exceeds total carbohydrates (${carbs}g) in ${food.id}`,
      );
    }
    if (fiber !== null && fiber !== undefined) {
      assert.ok(
        fiber <= carbs + 0.1,
        `Fiber (${fiber}g) exceeds total carbohydrates (${carbs}g) in ${food.id}`,
      );
    }

    // Serving size validity
    if (food.servingGrams !== undefined) {
      assert.ok(
        food.servingGrams > 0 && food.servingGrams <= 5000,
        `Invalid servingGrams in ${food.id}`,
      );
    }
    if (food.commonServings) {
      for (const s of food.commonServings) {
        assert.ok(
          s.description && s.description.trim().length > 0,
          `Empty serving description in ${food.id}`,
        );
        assert.ok(
          s.grams > 0 && Number.isFinite(s.grams) && s.grams <= 5000,
          `Invalid serving grams in ${food.id}`,
        );
      }
    }
  }
});

test('whey-protein-milk: verified against combined whey isolate and toned milk composition', () => {
  const shake = foods.find((f) => f.id === 'whey-protein-milk');
  assert.ok(shake, 'whey-protein-milk must exist');

  // Per 100g: 82 kcal, 9.8g protein, 4.4g carbs, 2.8g fat
  assert.equal(shake.nutrients.calories, 82);
  assert.equal(shake.nutrients.protein, 9.8);
  assert.equal(shake.nutrients.carbs, 4.4);
  assert.equal(shake.nutrients.fat, 2.8);

  // In a 330g shake portion (1 scoop whey + 250ml milk)
  const portion = scaleNutrients(shake.nutrients, 330);
  assert.ok(
    portion.calories >= 265 && portion.calories <= 275,
    'Expected ~271 kcal per 330g shake',
  );
  assert.ok(
    portion.protein >= 31 && portion.protein <= 34,
    'Expected ~32.3g protein per 330g shake',
  );
  assert.ok(
    portion.carbs >= 13 && portion.carbs <= 16,
    'Expected ~14.5g carbs per 330g shake',
  );
  assert.ok(
    portion.fat >= 8 && portion.fat <= 10.5,
    'Expected ~9.2g fat per 330g shake',
  );

  // Verify Atwater factor exactness
  const atwaterCal = portion.protein * 4 + portion.carbs * 4 + portion.fat * 9;
  assert.ok(
    Math.abs(portion.calories - atwaterCal) < 3,
    'Caloric estimate must closely match Atwater sum',
  );
});

test('portion calculation and serving size conversions scale accurately', () => {
  const roti = foods.find((f) => f.id === 'roti');
  assert.ok(roti);

  // 1 standard phulka is 35g
  const oneRoti = scaleNutrients(roti.nutrients, 35);
  assert.equal(Number(oneRoti.calories.toFixed(1)), 87.5);
  assert.equal(Number(oneRoti.protein.toFixed(1)), 2.8);
  assert.equal(Number(oneRoti.carbs.toFixed(1)), 16.8);
  assert.equal(Number(oneRoti.fat.toFixed(1)), 1.4);

  // 2 rotis (70g) must be exactly double 1 roti
  const twoRotis = scaleNutrients(roti.nutrients, 70);
  assert.equal(twoRotis.calories, oneRoti.calories * 2);
  assert.equal(twoRotis.protein, oneRoti.protein * 2);
  assert.equal(twoRotis.carbs, oneRoti.carbs * 2);
  assert.equal(twoRotis.fat, oneRoti.fat * 2);

  // Fractional portions (e.g. 17.5g = half a roti)
  const halfRoti = scaleNutrients(roti.nutrients, 17.5);
  assert.equal(halfRoti.calories, oneRoti.calories / 2);

  // Invalid portions throw RangeError
  assert.throws(
    () => scaleNutrients(roti.nutrients, 0),
    /positive, finite portion/,
  );
  assert.throws(
    () => scaleNutrients(roti.nutrients, -50),
    /positive, finite portion/,
  );
  assert.throws(
    () => scaleNutrients(roti.nutrients, NaN),
    /positive, finite portion/,
  );
  assert.throws(
    () => scaleNutrients(roti.nutrients, Infinity),
    /positive, finite portion/,
  );
});

test('recipe nutrition: accurately sums ingredients, yield, and per-serving amounts', () => {
  const roti = foods.find((f) => f.id === 'roti');
  const dal = foods.find((f) => f.id === 'moong');
  const rice = foods.find((f) => f.id === 'rice-cooked');

  const recipe = {
    id: 'recipe:sample-thali',
    name: 'Sample Indian Thali',
    description: '2 rotis, 1 bowl dal, 1 bowl rice',
    ingredients: [
      {
        foodId: roti.id,
        name: roti.name,
        reference: { ...roti.nutrients },
        grams: 70,
      },
      {
        foodId: dal.id,
        name: dal.name,
        reference: { ...dal.nutrients },
        grams: 180,
      },
      {
        foodId: rice.id,
        name: rice.name,
        reference: { ...rice.nutrients },
        grams: 150,
      },
    ],
    yieldGrams: 400,
    servings: 1,
    createdAt: '2026-10-31T03:00:00.000Z',
    updatedAt: '2026-10-31T03:00:00.000Z',
  };

  const calculated = recipeNutrition(recipe);

  // Individual ingredient contributions
  const rotiN = scaleNutrients(roti.nutrients, 70);
  const dalN = scaleNutrients(dal.nutrients, 180);
  const riceN = scaleNutrients(rice.nutrients, 150);

  const expectedTotalCal = rotiN.calories + dalN.calories + riceN.calories;
  const expectedTotalP = rotiN.protein + dalN.protein + riceN.protein;
  const expectedTotalC = rotiN.carbs + dalN.carbs + riceN.carbs;
  const expectedTotalF = rotiN.fat + dalN.fat + riceN.fat;

  assert.equal(calculated.total.values.calories, expectedTotalCal);
  assert.equal(calculated.total.values.protein, expectedTotalP);
  assert.equal(calculated.total.values.carbs, expectedTotalC);
  assert.equal(calculated.total.values.fat, expectedTotalF);

  // perServing must equal total / servings (servings = 1)
  assert.equal(calculated.perServing.calories, expectedTotalCal);
  assert.equal(calculated.perServing.protein, expectedTotalP);

  // per100 scaled by yieldGrams must equal total
  const scaledBack = scaleNutrients(calculated.per100, recipe.yieldGrams);
  assert.ok(Math.abs(scaledBack.calories - expectedTotalCal) < 1e-6);
  assert.ok(Math.abs(scaledBack.protein - expectedTotalP) < 1e-6);
});

test('diary totals match exact sum of individual food entries without rounding drift', () => {
  const roti = foods.find((f) => f.id === 'roti');
  const curd = foods.find((f) => f.id === 'curd');

  const now = '2026-10-31T03:00:00.000Z';
  const entry1 = createEntry(
    roti,
    'Breakfast',
    '2026-10-31',
    70,
    'entry-1',
    now,
  );
  const entry2 = createEntry(
    curd,
    'Breakfast',
    '2026-10-31',
    150,
    'entry-2',
    now,
  );

  assert.doesNotThrow(() => assertEntry(entry1));
  assert.doesNotThrow(() => assertEntry(entry2));

  const dayTotals = diaryTotals([entry1, entry2]);

  assert.equal(
    dayTotals.values.calories,
    entry1.nutrients.calories + entry2.nutrients.calories,
  );
  assert.equal(
    dayTotals.values.protein,
    entry1.nutrients.protein + entry2.nutrients.protein,
  );
  assert.equal(
    dayTotals.values.carbs,
    entry1.nutrients.carbs + entry2.nutrients.carbs,
  );
  assert.equal(
    dayTotals.values.fat,
    entry1.nutrients.fat + entry2.nutrients.fat,
  );
});
