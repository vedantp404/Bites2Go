import test from 'node:test';
import assert from 'node:assert/strict';
import { foods } from '../src/data/foods.ts';
import {
  availableImageAssets,
  foodImageKey,
  categoryIcon,
} from '../src/data/foodImages.ts';
import {
  createCatalogRepository,
  catalogKey,
} from '../src/storage/catalogRepository.ts';
import { scaleNutrients, searchFoods } from '../src/domain/food.ts';

function createMemoryStorage(initial = {}) {
  const store = new Map(Object.entries(initial));
  return {
    getItem: async (key) => store.get(key) ?? null,
    setItem: async (key, value) => {
      store.set(key, value);
    },
    dump: () => Object.fromEntries(store.entries()),
  };
}

test('catalogue expansion contains >= 850 unique items with valid nutrients and categories', () => {
  assert.ok(
    foods.length >= 850,
    `Expected >= 850 items, but got ${foods.length}`,
  );

  const ids = new Set();
  const categories = new Set();

  for (const food of foods) {
    assert.ok(food.id && typeof food.id === 'string', 'Valid id');
    assert.ok(!ids.has(food.id), `Duplicate ID detected: ${food.id}`);
    ids.add(food.id);

    assert.ok(food.name && food.name.trim().length > 0, 'Non-empty name');
    assert.ok(
      food.category && food.category.trim().length > 0,
      'Non-empty category',
    );
    categories.add(food.category);

    assert.equal(food.referenceGrams, 100);
    assert.equal(food.status, 'illustrative');
    assert.match(food.source, /synthetic/);

    const { calories, protein, carbs, fat } = food.nutrients;
    assert.ok(
      calories !== null && calories >= 0,
      `Calories must be non-negative: ${food.id}`,
    );
    assert.ok(
      protein !== null && protein >= 0,
      `Protein must be non-negative: ${food.id}`,
    );
    assert.ok(
      carbs !== null && carbs >= 0,
      `Carbs must be non-negative: ${food.id}`,
    );
    assert.ok(fat !== null && fat >= 0, `Fat must be non-negative: ${food.id}`);

    // Verify nutrient scaling does not throw
    const scaled = scaleNutrients(food.nutrients, 150);
    assert.ok(scaled.calories !== null && scaled.calories >= 0);
  }

  // Verify diverse category representation
  assert.ok(categories.size >= 12, 'Expected at least 12 distinct categories');
  assert.ok(categories.has('Grains'));
  assert.ok(categories.has('Bread'));
  assert.ok(categories.has('Pulses'));
  assert.ok(categories.has('Curries'));
  assert.ok(categories.has('Dairy'));
  assert.ok(categories.has('Fruit'));
  assert.ok(categories.has('Vegetables'));
  assert.ok(categories.has('Meat'));
  assert.ok(categories.has('Snacks'));
  assert.ok(categories.has('Breakfast'));
  assert.ok(categories.has('Beverages'));
  assert.ok(categories.has('Sweets'));
});

test('baseline fixtures 0-11 are preserved for backward compatibility', () => {
  assert.equal(foods[0].id, 'rice-cooked');
  assert.equal(foods[1].id, 'rice-raw');
  assert.equal(foods[2].id, 'roti');
  assert.equal(foods[3].id, 'moong');
  assert.equal(foods[4].id, 'chickpeas');
  assert.equal(foods[5].id, 'milk');
  assert.equal(foods[6].id, 'curd');
  assert.equal(foods[7].id, 'banana');
  assert.equal(foods[8].id, 'apple');
  assert.equal(foods[9].id, 'almonds');
  assert.equal(foods[10].id, 'oats');
  assert.equal(foods[11].id, 'paneer');

  // foods[0] servingGrams is omitted so legacy portionGrams returns null
  assert.equal(foods[0].servingGrams, undefined);
});

test('food image registry correctly resolves assets and handles failures', () => {
  // Decorative assets (max 5 retained)
  assert.equal(foodImageKey('apple'), 'apple');
  assert.equal(foodImageKey('banana'), 'banana');
  assert.equal(foodImageKey('dosa'), 'dosa');
  assert.equal(foodImageKey('carrot'), 'carrot');
  assert.equal(foodImageKey('oats'), 'oats');

  // Individual food photographs are removed
  assert.equal(foodImageKey('rice-cooked'), null);
  assert.equal(foodImageKey('roti'), null);
  assert.equal(foodImageKey('paneer'), null);
  assert.equal(foodImageKey('milk'), null);

  // Food objects with imageKey
  const foodWithImage = foods.find((f) => f.imageKey === 'dosa');
  assert.ok(foodWithImage, 'Found food with imageKey dosa');
  assert.equal(foodImageKey(foodWithImage), 'dosa');

  // Failure fallback
  assert.equal(foodImageKey('apple', true), null);
  assert.equal(foodImageKey(null), null);
  assert.equal(foodImageKey('nonexistent-food-id'), null);

  // Exactly 5 distinct decorative image assets are bundled
  assert.equal(availableImageAssets.length, 5);
});

test('category fallback icons map accurately for all categories', () => {
  assert.equal(categoryIcon('Bread'), 'bread');
  assert.equal(categoryIcon('Dairy'), 'dairy');
  assert.equal(categoryIcon('Meat'), 'meat');
  assert.equal(categoryIcon('Fruit'), 'fruit');
  assert.equal(categoryIcon('Vegetables'), 'leaf');
  assert.equal(categoryIcon('Grains'), 'bowl');
  assert.equal(categoryIcon('Pulses'), 'bowl');
  assert.equal(categoryIcon('Curries'), 'bowl');
  assert.equal(categoryIcon('Beverages'), 'cup');
  assert.equal(categoryIcon('Snacks'), 'snack');
  assert.equal(categoryIcon('Sweets'), 'snack');
  assert.equal(categoryIcon('UnknownCategory'), 'leaf');
  assert.equal(categoryIcon(undefined), 'leaf');
});

test('common servings are present, well-formed and scalable', () => {
  const withServings = foods.filter(
    (f) => f.commonServings && f.commonServings.length > 0,
  );
  assert.ok(
    withServings.length >= 800,
    'Almost all foods should have defined common servings',
  );

  for (const food of withServings) {
    for (const s of food.commonServings) {
      assert.ok(s.description.length > 0);
      assert.ok(s.grams > 0 && Number.isFinite(s.grams));
      const scaled = scaleNutrients(food.nutrients, s.grams);
      assert.ok(scaled.calories !== null && scaled.calories >= 0);
    }
  }
});

test('catalog repository idempotently saves and reads metadata in SQLite store', async () => {
  const storage = createMemoryStorage();
  const repo = createCatalogRepository(storage);

  // Initial read is null
  const initial = await repo.getMetadata();
  assert.equal(initial, null);

  // Initialize
  const meta = await repo.initializeCatalog(foods);
  assert.equal(meta.version, 1);
  assert.equal(meta.foodCount, foods.length);
  assert.ok(meta.categories.length >= 12);
  assert.ok(meta.updatedAt.length > 0);

  // Second initialization is idempotent (does not overwrite or fail)
  const meta2 = await repo.initializeCatalog(foods);
  assert.equal(meta2.foodCount, meta.foodCount);
  assert.equal(meta2.updatedAt, meta.updatedAt);

  // Stored JSON is valid
  const raw = await storage.getItem(catalogKey);
  assert.ok(raw);
  const parsed = JSON.parse(raw);
  assert.equal(parsed.foodCount, foods.length);
});

test('search ranking accurately prioritizes exact matches, aliases, and multi-word queries', () => {
  // Exact name match
  const rotiMatch = searchFoods(foods, 'Whole-wheat roti');
  assert.equal(rotiMatch[0].id, 'roti');

  // Exact alias match
  const dahiMatch = searchFoods(foods, 'dahi');
  assert.equal(dahiMatch[0].id, 'curd');

  const chapatiMatch = searchFoods(foods, 'chapati');
  assert.equal(chapatiMatch[0].id, 'roti');

  // Regional Maharashtrian dishes
  const pohaMatch = searchFoods(foods, 'poha');
  assert.ok(pohaMatch.length > 0);
  assert.ok(pohaMatch.some((f) => f.id.includes('poha')));

  const misalMatch = searchFoods(foods, 'misal');
  assert.ok(misalMatch.length > 0);
  assert.ok(misalMatch[0].id.includes('misal'));

  // Multi-word search
  const brownRice = searchFoods(foods, 'brown rice');
  assert.ok(brownRice.length > 0);
  assert.ok(brownRice[0].id.includes('brown'));

  const chickenSalad = searchFoods(foods, 'chicken caesar');
  assert.ok(chickenSalad.length > 0);
  assert.ok(chickenSalad[0].id.includes('caesar'));
});
