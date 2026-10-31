import test from 'node:test';
import assert from 'node:assert/strict';
import { foods } from '../src/data/foods.ts';
import {
  searchFoods,
  parseGrams,
  scaleNutrients,
  sumNutrients,
  formatNutrient,
  createDraft,
  foodDraftReducer,
  mealContext,
  meals,
  defaultFoodPortion,
} from '../src/domain/food.ts';
const fixture = { calories: 150, protein: 10, carbs: 20, fat: 0, fiber: null };
test('search: exact/partial names, aliases, case, empty, no matches, multi-word and deduplication', () => {
  assert.equal(searchFoods(foods, 'Cooked white rice')[0].id, 'rice-cooked');
  assert.deepEqual(
    searchFoods(foods, 'rice')
      .slice(0, 2)
      .map((f) => f.id),
    ['rice-cooked', 'rice-raw'],
  );
  assert.equal(searchFoods(foods, '  CHAPATI ')[0].id, 'roti');
  assert.equal(searchFoods(foods, 'dah')[0].id, 'curd');
  assert.equal(searchFoods(foods, 'brown rice')[0].id, 'rice-brown-cooked');
  assert.deepEqual(searchFoods(foods, '   '), foods);
  assert.deepEqual(searchFoods(foods, 'zzzz'), []);
  assert.equal(searchFoods([foods[0], foods[0]], 'rice').length, 1);
});
test('catalog identities, provenance and raw/cooked distinction across 850+ items', () => {
  assert.ok(
    foods.length >= 850,
    `Catalogue should have >= 850 items, got ${foods.length}`,
  );
  assert.equal(new Set(foods.map((f) => f.id)).size, foods.length);
  for (const food of foods) {
    assert.equal(food.referenceGrams, 100);
    assert.ok(
      ['illustrative', 'estimated', 'verified'].includes(food.status),
      `Invalid status ${food.status} on ${food.id}`,
    );
    assert.ok(
      typeof food.source === 'string' && food.source.trim().length > 0,
      `Empty source on ${food.id}`,
    );
    assert.doesNotThrow(() => scaleNutrients(food.nutrients, 100));
    assert.ok(food.category.length > 0);
    assert.ok(food.preparation.length > 0);
  }
  const [cooked, raw] = searchFoods(foods, 'rice');
  assert.notEqual(cooked.preparation, raw.preparation);
  assert.notDeepEqual(cooked.nutrients, raw.nutrients);
});
test('portion scaling preserves precision, unknowns and explicit zero; rounding is display-only', () => {
  assert.deepEqual(scaleNutrients(fixture, 200), {
    calories: 300,
    protein: 20,
    carbs: 40,
    fat: 0,
    fiber: null,
  });
  assert.equal(scaleNutrients(fixture, 12.5).calories, 18.75);
  assert.ok(Math.abs(scaleNutrients(fixture, 0.01).calories - 0.015) < 1e-12);
  assert.equal(scaleNutrients(fixture, 10000).calories, 15000);
  assert.equal(formatNutrient(18.75, 'kcal'), '19 kcal');
  assert.equal(formatNutrient(1.25, 'g'), '1.3 g');
  assert.equal(formatNutrient(null, 'g'), 'Unknown');
  assert.equal(formatNutrient(0, 'g'), '0.0 g');
  assert.equal(fixture.calories, 150);
});
test('invalid/nonfinite/overflow/underflow quantities and source values are rejected', () => {
  for (const grams of [
    0,
    -1,
    NaN,
    Infinity,
    -Infinity,
    Number.MAX_VALUE,
    Number.MIN_VALUE,
  ])
    assert.throws(() => scaleNutrients(fixture, grams), RangeError);
  for (const value of [-1, NaN, Infinity])
    assert.throws(
      () => scaleNutrients({ ...fixture, protein: value }, 100),
      RangeError,
    );
  for (const input of [
    '',
    ' ',
    '0',
    '-2',
    'NaN',
    'Infinity',
    '1e3',
    '12g',
    '1.2.3',
    '0x10',
    '+100',
    '0.0',
    '-0',
    '1,2,3',
    '.',
    ',',
  ])
    assert.equal(parseGrams(input), null);
  for (const [input, expected] of [
    ['100', 100],
    [' 12.5 ', 12.5],
    ['12,5', 12.5],
    ['.5', 0.5],
    [',5', 0.5],
    ['100.', 100],
    ['\t 50 \n', 50],
  ])
    assert.equal(parseGrams(input), expected);
});
test('sumNutrients aggregates all fields, preserves nulls and reports partial status', () => {
  assert.deepEqual(sumNutrients([]), {
    values: { calories: 0, protein: 0, carbs: 0, fat: 0, fiber: 0 },
    partial: {
      calories: false,
      protein: false,
      carbs: false,
      fat: false,
      fiber: false,
    },
    count: 0,
  });
  const single = sumNutrients([
    { calories: 150, protein: 5, carbs: 20, fat: 2, fiber: null },
  ]);
  assert.equal(single.count, 1);
  assert.equal(single.values.calories, 150);
  assert.equal(single.values.fiber, null);
  assert.equal(single.partial.calories, false);
  assert.equal(single.partial.fiber, true);

  const multiple = sumNutrients([
    { calories: 100, protein: 10, carbs: 15, fat: 2, fiber: null },
    { calories: 200, protein: null, carbs: 25, fat: 8, fiber: 3 },
  ]);
  assert.equal(multiple.count, 2);
  assert.equal(multiple.values.calories, 300);
  assert.equal(multiple.values.protein, 10);
  assert.equal(multiple.partial.protein, true);
  assert.equal(multiple.values.carbs, 40);
  assert.equal(multiple.partial.carbs, false);
  assert.equal(multiple.values.fat, 10);
  assert.equal(multiple.partial.fat, false);
  assert.equal(multiple.values.fiber, 3);
  assert.equal(multiple.partial.fiber, true);

  assert.throws(
    () =>
      sumNutrients([
        { ...fixture, calories: Number.MAX_VALUE },
        { ...fixture, calories: Number.MAX_VALUE },
      ]),
    /Nutrition total exceeds supported range/,
  );
});
test('defaultFoodPortion chooses servings for recipes and grams otherwise', () => {
  assert.deepEqual(defaultFoodPortion('recipe:soup'), {
    mode: 'servings',
    quantity: '1',
  });
  assert.deepEqual(defaultFoodPortion('custom:salad'), {
    mode: 'grams',
    quantity: '100',
  });
  assert.deepEqual(defaultFoodPortion('rice-cooked'), {
    mode: 'grams',
    quantity: '100',
  });
  assert.deepEqual(defaultFoodPortion(null), {
    mode: 'grams',
    quantity: '100',
  });
  assert.deepEqual(defaultFoodPortion(undefined), {
    mode: 'grams',
    quantity: '100',
  });
});
test('draft keeps meal, query and portion on Back; changing food resets portion and confirmation', () => {
  for (const meal of meals) {
    let draft = createDraft(meal);
    draft = foodDraftReducer(draft, { type: 'query', value: 'rice' });
    draft = foodDraftReducer(draft, { type: 'select', id: 'rice-cooked' });
    draft = foodDraftReducer(draft, { type: 'grams', value: '125.5' });
    draft = foodDraftReducer(draft, { type: 'confirm' });
    assert.equal(draft.confirmed, true);
    draft = foodDraftReducer(draft, { type: 'back' });
    assert.equal(draft.detail, false);
    assert.equal(draft.meal, meal);
    assert.equal(draft.query, 'rice');
    draft = foodDraftReducer(draft, { type: 'select', id: 'rice-cooked' });
    assert.equal(draft.grams, '125.5');
    draft = foodDraftReducer(draft, { type: 'grams', value: '0' });
    assert.equal(foodDraftReducer(draft, { type: 'confirm' }).confirmed, false);
    draft = foodDraftReducer(draft, { type: 'select', id: 'rice-raw' });
    assert.equal(draft.grams, '100');
    assert.equal(draft.confirmed, false);
  }
  for (const invalid of [undefined, 'other', ['Breakfast']])
    assert.equal(mealContext(invalid), null);
  assert.equal(
    foodDraftReducer(createDraft(undefined), { type: 'confirm' }).confirmed,
    false,
  );
});
