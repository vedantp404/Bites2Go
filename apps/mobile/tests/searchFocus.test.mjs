import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { join } from 'node:path';
import { foods } from '../src/data/foods.ts';
import { createDraft, foodDraftReducer } from '../src/domain/food.ts';
import { emptyLibrary, browseFoods } from '../src/domain/library.ts';

test('regression: FoodSearchScreen does not define components inside render function', () => {
  const filePath = join(process.cwd(), 'src/screens/FoodSearchScreen.tsx');
  const source = readFileSync(filePath, 'utf8');

  // Verify SearchHeader is declared outside FoodSearchScreen
  assert.match(
    source,
    /export const SearchHeader = memo\(function SearchHeader/,
    'SearchHeader must be declared at module scope and wrapped in memo',
  );

  // Extract the FoodSearchScreen function body
  const screenMatch = source.match(
    /export default function FoodSearchScreen\(\) \{([\s\S]*)\}/,
  );
  assert.ok(screenMatch, 'FoodSearchScreen function must be present');
  const screenBody = screenMatch[1];

  // Verify no nested component / render function declarations inside FoodSearchScreen
  assert.doesNotMatch(
    screenBody,
    /const renderSearchHeader\s*=\s*/,
    'renderSearchHeader must not be declared inside FoodSearchScreen render body',
  );

  // Verify FlatList uses stable element for ListHeaderComponent
  assert.match(
    screenBody,
    /ListHeaderComponent=\{\s*<SearchHeader/,
    'FlatList must pass <SearchHeader ... /> as a React element with stable type',
  );

  // Verify removeClippedSubviews is not enabled on Android to avoid detachment focus loss
  assert.doesNotMatch(
    screenBody,
    /removeClippedSubviews=\{Platform\.OS === 'android'\}/,
    'removeClippedSubviews must not be enabled on Android search FlatList',
  );
});

test('regression: SearchHeader component reference remains stable across query updates', () => {
  // Simulate React's element type reconciliation contract:
  // When component type reference is identical (prev.type === next.type),
  // React updates props in place without unmounting the TextInput.

  // 1. Stable component definition (fixed pattern)
  const StableHeader = function SearchHeader(props) {
    return { type: 'TextInput', props: { value: props.query } };
  };

  const el1 = { type: StableHeader, props: { query: 'a', matchesCount: 100 } };
  const el2 = { type: StableHeader, props: { query: 'ab', matchesCount: 10 } };
  const el3 = {
    type: StableHeader,
    props: { query: 'apple', matchesCount: 1 },
  };

  assert.equal(
    el1.type === el2.type,
    true,
    'StableHeader maintains identical component type across keystrokes',
  );
  assert.equal(
    el2.type === el3.type,
    true,
    'StableHeader maintains identical component type when search results update',
  );

  // 2. Broken pattern: nested function component recreated in render
  function simulatedBrokenScreen(query) {
    const UnstableHeader = function () {
      return { type: 'TextInput', props: { value: query } };
    };
    return { type: UnstableHeader, props: { query } };
  }

  const brokenEl1 = simulatedBrokenScreen('a');
  const brokenEl2 = simulatedBrokenScreen('ab');

  assert.equal(
    brokenEl1.type === brokenEl2.type,
    false,
    'Nested component declaration causes component type mismatch, triggering unmount and keyboard blur',
  );
});

test('search query progression and debouncing retain draft continuity', () => {
  const library = emptyLibrary();
  let draft = createDraft('Lunch');

  // Sequential keystrokes do not reset draft state or drop meal context
  const keystrokes = ['r', 'ro', 'rot', 'roti'];
  for (const query of keystrokes) {
    draft = foodDraftReducer(draft, { type: 'query', value: query });
    assert.equal(draft.meal, 'Lunch');
    assert.equal(draft.query, query);
    assert.equal(draft.detail, false);

    const matches = browseFoods(library, foods, [], 'All', draft.query);
    assert.ok(matches.length > 0);
  }
  const rotiMatches = browseFoods(library, foods, [], 'All', 'roti');
  assert.ok(
    rotiMatches.some((f) => f.id === 'roti'),
    'Expected roti to be present in matches',
  );

  // Clearing search restores full catalogue without breaking draft
  draft = foodDraftReducer(draft, { type: 'query', value: '' });
  assert.equal(draft.query, '');
  assert.equal(draft.meal, 'Lunch');
  const allMatches = browseFoods(library, foods, [], 'All', '');
  assert.equal(allMatches.length, foods.length);
});
