import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { kaggleFoods } from '../src/data/kaggleFoods.ts';
import { foods } from '../src/data/foods.ts';
import { unifiedFoods } from '../src/data/unifiedFoods.ts';
import { searchFoods, scaleNutrients } from '../src/domain/food.ts';
import {
  foodOrigin,
  emptyLibrary,
  browseFoods,
} from '../src/domain/library.ts';

test('kaggle dataset schema: 517 imported records with physical bounds and illustrative status', () => {
  assert.equal(
    kaggleFoods.length,
    517,
    'Must have exactly 517 imported Kaggle foods',
  );
  assert.equal(
    foods.length,
    894,
    'Built-in foods invariant must remain at 894 items',
  );
  assert.equal(
    unifiedFoods.length,
    1411,
    'Unified search catalogue must have 1411 items',
  );

  for (const food of kaggleFoods) {
    assert.ok(
      food.id.startsWith('kaggle:'),
      `ID must start with kaggle: - ${food.id}`,
    );
    assert.equal(
      food.referenceGrams,
      100,
      `referenceGrams must be 100: ${food.id}`,
    );
    assert.equal(
      food.status,
      'illustrative',
      `Kaggle foods must strictly be illustrative: ${food.id}`,
    );
    assert.ok(
      food.source.includes('Kaggle'),
      `Source must identify Kaggle: ${food.id}`,
    );
    assert.ok(
      food.sourceId && food.sourceId.startsWith('kaggle:v2:'),
      `sourceId must reference kaggle row: ${food.id}`,
    );
    assert.ok(
      food.name.trim().length > 0,
      `Name must not be empty: ${food.id}`,
    );
    assert.ok(
      Array.isArray(food.aliases) && food.aliases.length > 0,
      `Aliases must not be empty: ${food.id}`,
    );
    assert.ok(
      food.servingGrams > 0,
      `Serving grams must be positive: ${food.id}`,
    );
    assert.ok(
      Array.isArray(food.commonServings) && food.commonServings.length > 0,
      `Common servings required: ${food.id}`,
    );

    const { calories, protein, carbs, fat, fiber, sugar, sodium } =
      food.nutrients;
    assert.ok(
      calories !== null && calories >= 0,
      `Calories must be >= 0: ${food.id}`,
    );
    assert.ok(
      protein !== null && protein >= 0,
      `Protein must be >= 0: ${food.id}`,
    );
    assert.ok(carbs !== null && carbs >= 0, `Carbs must be >= 0: ${food.id}`);
    assert.ok(fat !== null && fat >= 0, `Fat must be >= 0: ${food.id}`);
    if (fiber !== null) assert.ok(fiber >= 0, `Fiber must be >= 0: ${food.id}`);
    if (sugar !== null) assert.ok(sugar >= 0, `Sugar must be >= 0: ${food.id}`);
    if (sodium !== null)
      assert.ok(sodium >= 0, `Sodium must be >= 0: ${food.id}`);

    // Physical law: Macronutrients per 100g cannot exceed 100.5g
    const macroSum = (protein ?? 0) + (carbs ?? 0) + (fat ?? 0);
    assert.ok(
      macroSum <= 100.5,
      `Physical macronutrient bound exceeded in ${food.id}: sum is ${macroSum}g / 100g`,
    );

    // Energy density bound: Pure fat is ~900 kcal / 100g
    assert.ok(
      calories <= 900,
      `Physical calorie density bound exceeded in ${food.id}: ${calories} kcal / 100g`,
    );
  }
});

test('duplicate detection, unique IDs, and case/punctuation insensitive search', () => {
  const kaggleIdSet = new Set(kaggleFoods.map((f) => f.id));
  assert.equal(
    kaggleIdSet.size,
    kaggleFoods.length,
    'All Kaggle food IDs must be unique',
  );

  const unifiedIdSet = new Set(unifiedFoods.map((f) => f.id));
  assert.equal(
    unifiedIdSet.size,
    unifiedFoods.length,
    'All unified food IDs must be unique',
  );

  // Case insensitivity and whitespace handling
  const exactLower = searchFoods(unifiedFoods, 'acai bowl');
  const exactUpper = searchFoods(unifiedFoods, 'ACAI BOWL');
  const exactPadded = searchFoods(unifiedFoods, '   acai bowl   ');

  assert.ok(exactLower.length > 0);
  assert.equal(exactLower[0].id, 'kaggle:acai-bowl');
  assert.equal(exactUpper[0].id, 'kaggle:acai-bowl');
  assert.equal(exactPadded[0].id, 'kaggle:acai-bowl');

  // Partial search within Kaggle items
  const partial = searchFoods(kaggleFoods, 'acai');
  assert.equal(partial[0].id, 'kaggle:acai-bowl');

  // Exact array deduplication: duplicate elements in candidates are deduplicated
  const dups = [kaggleFoods[0], kaggleFoods[0], kaggleFoods[1]];
  const res = searchFoods(dups, kaggleFoods[0].name.slice(0, 4));
  assert.equal(res.filter((f) => f.id === kaggleFoods[0].id).length, 1);
});

test('conservative merging preserves existing IDs and aliases for established foods', () => {
  // Check that staple foods matched as certain merges retain their stable original IDs
  const stapleIds = [
    'banana',
    'apple',
    'almonds',
    'rice-brown-cooked',
    'cheese-cheddar',
  ];
  for (const id of stapleIds) {
    const found = unifiedFoods.find((f) => f.id === id);
    assert.ok(
      found,
      `Staple food ${id} must exist in unified catalogue with original ID`,
    );
  }

  // Searching for staple foods returns the canonical item
  const bananaSearch = searchFoods(unifiedFoods, 'banana');
  assert.equal(bananaSearch[0].id, 'banana');

  const appleSearch = searchFoods(unifiedFoods, 'apple');
  assert.equal(appleSearch[0].id, 'apple');

  const almondsSearch = searchFoods(unifiedFoods, 'almonds');
  assert.equal(almondsSearch[0].id, 'almonds');
});

test('meaningfully different preparations and milk fats remain separate entries', () => {
  // 2% milk from Kaggle vs whole milk from built-ins
  const kaggle2PctMilk = kaggleFoods.find((f) => f.id === 'kaggle:milk');
  assert.ok(kaggle2PctMilk, 'Kaggle 2% milk must exist');
  assert.equal(kaggle2PctMilk.name, 'Milk (2%, 1 cup)');

  const builtinWholeMilk = foods.find((f) => f.id === 'milk');
  assert.ok(builtinWholeMilk, 'Built-in whole milk must exist');

  assert.notEqual(kaggle2PctMilk.id, builtinWholeMilk.id);
  assert.notEqual(
    kaggle2PctMilk.nutrients.calories,
    builtinWholeMilk.nutrients.calories,
  );

  // Steamed edamame in pod (Kaggle) vs existing steamed edamame
  const kaggleEdamame = kaggleFoods.find((f) => f.id === 'kaggle:edamame');
  assert.ok(kaggleEdamame, 'Kaggle edamame must exist as separate item');

  // Both exist in unifiedFoods
  assert.ok(unifiedFoods.some((f) => f.id === 'kaggle:milk'));
  assert.ok(unifiedFoods.some((f) => f.id === 'milk'));
});

test('quarantined invalid record rejection: Corn Nuts (1 oz) is rejected and not in catalogue', () => {
  // Raw line 486 has 2g P + 23g C + 4g F in 28.35g portion = 102.1g/100g (violating physics)
  const inKaggle = kaggleFoods.some((f) =>
    f.name.toLowerCase().includes('corn nuts'),
  );
  assert.equal(
    inKaggle,
    false,
    'Corn Nuts (1 oz) must be quarantined from kaggleFoods',
  );

  const inUnified = unifiedFoods.some((f) =>
    f.name.toLowerCase().includes('corn nuts'),
  );
  assert.equal(
    inUnified,
    false,
    'Corn Nuts (1 oz) must not be present in unifiedFoods',
  );
});

test('serving size conversions and per-100g scaling consistency', () => {
  // For each Kaggle food, scaling nutrients to servingGrams reproduces positive values
  for (const food of kaggleFoods.slice(0, 50)) {
    const scaled = scaleNutrients(food.nutrients, food.servingGrams);
    assert.ok(scaled.calories !== null && scaled.calories >= 0);
    assert.ok(scaled.protein !== null && scaled.protein >= 0);
    assert.ok(scaled.carbs !== null && scaled.carbs >= 0);
    assert.ok(scaled.fat !== null && scaled.fat >= 0);
  }

  // Check specific item: Aioli (Garlic 1 tbsp)
  // Raw was: 95 kcal, 0.1g P, 0.5g C, 10.5g F in 15g portion
  const aioli = kaggleFoods.find((f) => f.id === 'kaggle:aioli');
  assert.ok(aioli, 'Aioli must exist');
  assert.equal(aioli.servingGrams, 15);
  const scaledAioli = scaleNutrients(aioli.nutrients, 15);
  // Reference per-100g is 633.3 kcal -> 15g is 94.995 kcal (~95 kcal)
  assert.ok(
    Math.abs(scaledAioli.calories - 95) < 0.5,
    'Scaled aioli calories match raw portion',
  );
  assert.ok(
    Math.abs(scaledAioli.fat - 10.5) < 0.2,
    'Scaled aioli fat matches raw portion',
  );
});

test('dataset-first search ranking: Kaggle (Tier 1) > Built-in (Tier 2) > Custom (Tier 3)', () => {
  // Create mock foods with identical names to test pure tier scoring
  const customFood = {
    id: 'custom:test-granola',
    name: 'Granola Bar',
    aliases: ['granola bar'],
    category: 'Snacks',
    preparation: 'Homemade',
    referenceGrams: 100,
    nutrients: { calories: 400, protein: 10, carbs: 60, fat: 12, fiber: 5 },
    status: 'estimated',
    source: 'User Custom Food',
    servingGrams: 40,
    servingUnit: 'bar',
    commonServings: [{ description: '1 bar (40g)', grams: 40 }],
  };

  const builtinFood = {
    id: 'granola-bar-builtin',
    name: 'Granola Bar',
    aliases: ['granola bar'],
    category: 'Snacks',
    preparation: 'Commercial',
    referenceGrams: 100,
    nutrients: { calories: 420, protein: 8, carbs: 65, fat: 14, fiber: 4 },
    status: 'illustrative',
    source: 'Built-in database',
    servingGrams: 40,
    servingUnit: 'bar',
    commonServings: [{ description: '1 bar (40g)', grams: 40 }],
  };

  const kaggleFood = {
    id: 'kaggle:granola-bar',
    name: 'Granola Bar',
    aliases: ['granola bar'],
    category: 'Snacks',
    preparation: 'Kaggle imported',
    referenceGrams: 100,
    nutrients: { calories: 410, protein: 9, carbs: 62, fat: 13, fiber: 5 },
    status: 'illustrative',
    source: 'Kaggle Daily Food Dataset',
    sourceId: 'kaggle:v2:999',
    servingGrams: 40,
    servingUnit: 'bar',
    commonServings: [{ description: '1 bar (40g)', grams: 40 }],
  };

  // Provide candidates in arbitrary order: custom first, then builtin, then kaggle
  const candidates = [customFood, builtinFood, kaggleFood];
  const results = searchFoods(candidates, 'Granola Bar');

  assert.equal(results.length, 3);
  assert.equal(
    results[0].id,
    kaggleFood.id,
    'Kaggle item must rank first (Tier 1 +0.4)',
  );
  assert.equal(
    results[1].id,
    builtinFood.id,
    'Built-in item must rank second (Tier 2 +0.2)',
  );
  assert.equal(
    results[2].id,
    customFood.id,
    'Custom item must rank third (Tier 3 +0.0)',
  );
});

test('built-in catalogue fallback for queries absent in Kaggle', () => {
  // Indian traditional foods that do not exist in Kaggle dataset must still be found seamlessly
  const chapatiResults = searchFoods(unifiedFoods, 'chapati');
  assert.ok(chapatiResults.length > 0, 'Chapati search must return results');
  assert.equal(chapatiResults[0].id, 'roti');

  const rotiResults = searchFoods(unifiedFoods, 'roti');
  assert.ok(
    rotiResults.some((f) => f.id === 'roti'),
    'Roti search must include whole-wheat roti',
  );

  const idliResults = searchFoods(unifiedFoods, 'idli');
  assert.ok(idliResults.length > 0, 'Idli search must return results');
  assert.ok(idliResults[0].id.includes('idli'));

  const dosaResults = searchFoods(unifiedFoods, 'dosa');
  assert.ok(dosaResults.length > 0, 'Dosa search must return results');
  assert.ok(dosaResults[0].id.includes('dosa'));

  const dalMakhaniResults = searchFoods(unifiedFoods, 'dal makhani');
  assert.ok(
    dalMakhaniResults.length > 0,
    'Dal makhani search must return results',
  );
  assert.equal(dalMakhaniResults[0].id, 'dal-makhani');
});

test('custom food search and origin identification (foodOrigin)', () => {
  const kaggleItem = kaggleFoods[0];
  const builtinItem = foods[0];
  const customItem = {
    id: 'custom:my-smoothie',
    name: 'My Morning Smoothie',
    aliases: ['smoothie'],
    category: 'Beverages',
    preparation: 'Blended',
    referenceGrams: 100,
    nutrients: { calories: 80, protein: 3, carbs: 15, fat: 1, fiber: 2 },
    status: 'estimated',
    source: 'Custom',
    servingGrams: 250,
    servingUnit: 'glass',
    commonServings: [{ description: '1 glass (250g)', grams: 250 }],
  };
  const recipeItem = {
    id: 'recipe:special-dal',
    name: 'Special Tadka Dal',
    aliases: ['dal'],
    category: 'Lunch',
    preparation: 'Simmered',
    referenceGrams: 100,
    nutrients: { calories: 120, protein: 7, carbs: 18, fat: 3, fiber: 4 },
    status: 'estimated',
    source: 'Recipe',
    servingGrams: 150,
    servingUnit: 'bowl',
    commonServings: [{ description: '1 bowl (150g)', grams: 150 }],
  };

  assert.equal(foodOrigin(kaggleItem), 'Kaggle dataset illustrative food');
  assert.equal(foodOrigin(builtinItem), 'Built-in illustrative food');
  assert.equal(foodOrigin(customItem), 'User-created estimate');
  assert.equal(foodOrigin(recipeItem), 'Recipe / snapshot estimates');

  // Verify browsing library custom food
  const lib = emptyLibrary();
  const customFoodEntry = {
    id: 'custom:high-protein-shake',
    name: 'High Protein Shake',
    description: 'Post workout',
    servingGrams: 300,
    servingNutrients: {
      calories: 250,
      protein: 35,
      carbs: 15,
      fat: 4,
      fiber: 2,
    },
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  };
  lib.customFoods.push(customFoodEntry);

  const found = browseFoods(lib, unifiedFoods, [], 'Custom', 'Protein Shake');
  assert.equal(found.length, 1);
  assert.equal(found[0].id, 'custom:high-protein-shake');
  assert.equal(foodOrigin(found[0]), 'User-created estimate');
});

test('historical diary snapshot compatibility and search latency benchmark', () => {
  // Confirm essential baseline foods from early stages exist in unifiedFoods
  const baselineIds = [
    'apple',
    'banana',
    'rice-cooked',
    'roti',
    'curd',
    'milk',
    'paneer',
  ];
  for (const id of baselineIds) {
    const item = unifiedFoods.find((f) => f.id === id);
    assert.ok(
      item,
      `Baseline food ${id} must remain available for diary snapshot replay`,
    );
    assert.equal(item.referenceGrams, 100);
  }

  // Performance benchmark: searching 1411 foods for various common queries
  const queries = [
    'chicken',
    'salad',
    'rice',
    'apple',
    'paneer',
    'coffee',
    'soup',
  ];
  const start = performance.now();
  for (const q of queries) {
    const results = searchFoods(unifiedFoods, q);
    assert.ok(results.length > 0, `Search for '${q}' returned results`);
  }
  const elapsed = performance.now() - start;
  const avgPerQuery = elapsed / queries.length;

  assert.ok(
    avgPerQuery < 30,
    `Search latency should be < 30ms per query across 1411 foods (got ${avgPerQuery.toFixed(2)}ms)`,
  );

  // Search focus regression safety: verify FoodSearchScreen preserves module-level SearchHeader
  const searchScreenPath = fileURLToPath(
    new URL('../src/screens/FoodSearchScreen.tsx', import.meta.url),
  );
  const screenSource = readFileSync(searchScreenPath, 'utf8');

  assert.match(
    screenSource,
    /import\s*\{\s*unifiedFoods\s*\}\s*from\s*['"]\.\.\/data\/unifiedFoods['"]/,
    'FoodSearchScreen must import unifiedFoods',
  );
  assert.match(
    screenSource,
    /export const SearchHeader = memo\(function SearchHeader/,
    'SearchHeader must remain at module scope wrapped in memo',
  );
});
