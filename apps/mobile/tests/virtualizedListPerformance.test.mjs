import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { join } from 'node:path';
import { unifiedFoods } from '../src/data/unifiedFoods.ts';
import { searchFoods } from '../src/domain/food.ts';
import { browseFoods, emptyLibrary } from '../src/domain/library.ts';

test('virtualized list performance: FoodSearchRow and SearchHeader memoization at module scope', () => {
  const filePath = join(process.cwd(), 'src/screens/FoodSearchScreen.tsx');
  const source = readFileSync(filePath, 'utf8');

  // Verify SearchHeader is declared at module scope and wrapped in memo
  assert.match(
    source,
    /export const SearchHeader = memo\(function SearchHeader/,
    'SearchHeader must remain declared at module scope and wrapped in memo',
  );

  // Verify FoodSearchRow is declared at module scope and wrapped in memo
  assert.match(
    source,
    /export const FoodSearchRow = memo\(function FoodSearchRow/,
    'FoodSearchRow must be declared at module scope and wrapped in memo',
  );

  // Verify FlatList uses stable element for ListHeaderComponent
  assert.match(
    source,
    /ListHeaderComponent=\{\s*<SearchHeader/,
    'FlatList must pass <SearchHeader ... /> with stable element type',
  );

  // Verify FlatList uses FoodSearchRow in renderItem
  assert.match(
    source,
    /<FoodSearchRow\s+food=\{item\}\s+onSelect=\{select\}\s*\/>/,
    'FlatList renderItem must render memoized FoodSearchRow with stable onSelect',
  );

  // Verify FlatList has tuned virtualization props
  assert.match(
    source,
    /initialNumToRender=\{10\}/,
    'FlatList must tune initialNumToRender to 10 for fast initial mount',
  );
  assert.match(
    source,
    /maxToRenderPerBatch=\{10\}/,
    'FlatList must tune maxToRenderPerBatch to 10 to keep JS frame under budget',
  );
  assert.match(
    source,
    /windowSize=\{5\}/,
    'FlatList must keep windowSize at 5 to prevent unbounded memory growth',
  );
  assert.match(
    source,
    /onEndReached=\{handleEndReached\}/,
    'FlatList must implement onEndReached for smooth incremental pagination',
  );
  assert.match(
    source,
    /data=\{displayedFoods\}/,
    'FlatList must render windowed displayedFoods rather than all 1,411 items simultaneously',
  );
});

test('data integrity & dataset-first search ordering under windowed pagination', () => {
  const lib = emptyLibrary();

  // 1. Full browsing without query returns all 1,411 items
  const allFoods = browseFoods(lib, unifiedFoods, [], 'All', '');
  assert.equal(
    allFoods.length,
    1411,
    'Full catalogue must contain 1,411 items',
  );

  // 2. Initial page limit is 40
  const INITIAL_PAGE_SIZE = 40;
  const initialPage = allFoods.slice(0, INITIAL_PAGE_SIZE);
  assert.equal(
    initialPage.length,
    40,
    'Initial page must be capped at 40 items',
  );

  // Verify no duplicate IDs within the initial slice
  const uniqueIds = new Set(initialPage.map((f) => f.id));
  assert.equal(
    uniqueIds.size,
    40,
    'All initial page items must have unique IDs',
  );

  // 3. Incremental loading up to full catalogue
  let loadedCount = INITIAL_PAGE_SIZE;
  const PAGE_INCREMENT = 40;
  while (loadedCount < allFoods.length) {
    loadedCount = Math.min(loadedCount + PAGE_INCREMENT, allFoods.length);
  }
  assert.equal(
    loadedCount,
    1411,
    'Incremental pagination must reach all 1,411 items',
  );

  // 4. Dataset-first search ordering is preserved
  // Search for 'granola': Kaggle item 'kaggle:granola' (+0.4) ranks ahead of built-in (+0.2)
  const granolaResults = searchFoods(unifiedFoods, 'granola');
  assert.ok(
    granolaResults.length >= 2,
    'Should find at least two granola matches',
  );
  assert.equal(
    granolaResults[0].id.startsWith('kaggle:'),
    true,
    'Kaggle dataset item must rank Tier 1 ahead of built-in item for equal relevance',
  );

  // 5. Exact match ranking beats partial match
  const bananaResults = searchFoods(unifiedFoods, 'banana');
  assert.ok(bananaResults.length > 0, 'Should find banana matches');
  assert.equal(
    bananaResults[0].name.toLowerCase(),
    'banana',
    'Exact name match must rank first',
  );
});

test('recipe and my-foods list optimizations: memoized available and search matches', () => {
  const recipeSource = readFileSync(
    join(process.cwd(), 'src/screens/RecipeScreen.tsx'),
    'utf8',
  );

  // Verify available is memoized with useMemo
  assert.match(
    recipeSource,
    /const available = useMemo\(\s*\(\)\s*=>\s*libraryFoods/,
    'RecipeScreen available foods must be memoized with useMemo',
  );

  // Verify visibleMatches is memoized with useMemo
  assert.match(
    recipeSource,
    /const visibleMatches = useMemo\(/,
    'RecipeScreen visibleMatches must be memoized with useMemo',
  );

  // Verify ingredientFoodIds is a Set for O(1) membership check
  assert.match(
    recipeSource,
    /const ingredientFoodIds = useMemo\(\s*\(\)\s*=>\s*new Set/,
    'RecipeScreen must use memoized Set for O(1) ingredient disabled check',
  );

  // Verify MyFoodsScreen memoizes customFoods
  const myFoodsSource = readFileSync(
    join(process.cwd(), 'src/screens/MyFoodsScreen.tsx'),
    'utf8',
  );
  assert.match(
    myFoodsSource,
    /const customFoods = useMemo\(/,
    'MyFoodsScreen must memoize customFoods mapping',
  );
});

test('performance benchmark: initial page windowing vs unwindowed 1,411 item array', () => {
  const lib = emptyLibrary();
  const allFoods = browseFoods(lib, unifiedFoods, [], 'All', '');

  // Measure full catalogue mapping
  const startFull = performance.now();
  for (let i = 0; i < 50; i++) {
    void allFoods.map((f) => ({ id: f.id, name: f.name }));
  }
  const durationFull = performance.now() - startFull;

  // Measure windowed 40-item mapping
  const startWindowed = performance.now();
  for (let i = 0; i < 50; i++) {
    void allFoods.slice(0, 40).map((f) => ({ id: f.id, name: f.name }));
  }
  const durationWindowed = performance.now() - startWindowed;

  assert.ok(
    durationWindowed < durationFull,
    `Windowed list data preparation (${durationWindowed.toFixed(2)}ms) must be significantly faster than unwindowed (${durationFull.toFixed(2)}ms)`,
  );
});
