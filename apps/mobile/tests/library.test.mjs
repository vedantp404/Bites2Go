import test from 'node:test';
import assert from 'node:assert/strict';
import { DatabaseSync } from 'node:sqlite';
import { mkdtempSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, resolve, sep } from 'node:path';
import {
  emptyLibrary,
  validateLibrary,
  decodeLibrary,
  saveCustom,
  saveRecipe,
  removeLibraryItem,
  customAsFood,
  recipeAsFood,
  recipeNutrition,
  libraryFoods,
  ingredientFromFood,
  setFavourite,
  recentFoods,
  browseFoods,
  portionGrams,
} from '../src/domain/library.ts';
import {
  createLibraryRepository,
  libraryKey,
} from '../src/storage/libraryRepository.ts';
import { createEntry, editPortion, diaryTotals } from '../src/domain/diary.ts';
import { createDiaryRepository } from '../src/storage/diaryRepository.ts';
import {
  createDraft,
  foodDraftReducer,
  scaleNutrients,
  sumNutrients,
} from '../src/domain/food.ts';
import { foods } from '../src/data/foods.ts';
const now = '2026-10-30T12:00:00.000Z';
const values = { calories: 200, protein: 10, carbs: 20, fat: 5, fiber: null };
const custom = (id = 'custom:a') => ({
  id,
  name: 'Homemade curd',
  description: 'My brand',
  servingGrams: 50,
  servingNutrients: { ...values },
  createdAt: now,
  updatedAt: now,
});
const recipe = (ingredients) => ({
  id: 'recipe:a',
  name: 'Rice bowl',
  description: 'Two portions',
  ingredients: ingredients ?? [ingredientFromFood(foods[0].id, foods, 200)],
  yieldGrams: 300,
  servings: 2,
  createdAt: now,
  updatedAt: now,
});
const memory = () => {
  const state = {
    map: new Map(),
    readError: false,
    writeError: false,
    ackError: false,
  };
  return {
    state,
    storage: {
      getItem: async (key) => {
        if (state.readError) throw Error('read');
        return state.map.get(key) ?? null;
      },
      setItem: async (key, value) => {
        if (state.writeError) throw Error('write');
        state.map.set(key, value);
        if (state.ackError) throw Error('ack');
      },
    },
  };
};
test('custom creation, canonical serving conversion, zero/null and search', () => {
  const item = { ...custom(), servingNutrients: { ...values, fat: 0 } };
  const data = saveCustom(emptyLibrary(), item);
  const food = customAsFood(data.customFoods[0]);
  assert.equal(food.nutrients.calories, 400);
  assert.equal(food.nutrients.fat, 0);
  assert.equal(food.nutrients.fiber, null);
  assert.equal(food.servingGrams, 50);
  assert.equal(
    browseFoods(data, foods, [], 'Custom', 'HOMEMADE')[0].id,
    item.id,
  );
  assert.equal(browseFoods(data, foods, [], 'All', 'my brand')[0].id, item.id);
  assert.equal(saveCustom(data, item).customFoods.length, 1);
});
test('custom validation rejects missing names, invalid servings/nutrients and metadata before JSON conversion', () => {
  for (const patch of [
    { name: ' ' },
    { name: 'x'.repeat(121) },
    { description: 'x'.repeat(501) },
    { servingGrams: 0 },
    { servingGrams: -1 },
    { servingGrams: NaN },
    { servingGrams: 10001 },
    { createdAt: 'bad' },
    { id: 'rice-cooked' },
  ])
    assert.throws(() => saveCustom(emptyLibrary(), { ...custom(), ...patch }));
  for (const number of [-1, NaN, Infinity, 1000001])
    assert.throws(() =>
      saveCustom(emptyLibrary(), {
        ...custom(),
        servingNutrients: { ...values, protein: number },
      }),
    );
  assert.doesNotThrow(() =>
    saveCustom(emptyLibrary(), {
      ...custom(),
      servingNutrients: {
        calories: null,
        protein: 0,
        carbs: null,
        fat: 0,
        fiber: null,
      },
    }),
  );
});
test('custom edits/deletes do not change saved diary snapshots or their portion-edit basis', () => {
  const initial = saveCustom(emptyLibrary(), custom());
  const food = customAsFood(initial.customFoods[0]);
  const entry = createEntry(food, 'Lunch', '2026-10-29', 75, 'entry', now);
  const bytes = JSON.stringify(entry);
  let next = saveCustom(
    initial,
    {
      ...custom(),
      name: 'Changed',
      servingNutrients: { ...values, calories: 400 },
      updatedAt: '2026-10-30T13:00:00.000Z',
    },
    true,
  );
  assert.equal(customAsFood(next.customFoods[0]).nutrients.calories, 800);
  next = removeLibraryItem(next, food.id);
  assert.equal(next.customFoods.length, 0);
  assert.equal(JSON.stringify(entry), bytes);
  assert.equal(editPortion(entry, 150, now).nutrients.calories, 600);
  assert.equal(initial.customFoods[0].name, 'Homemade curd');
  assert.throws(() => saveCustom(next, custom(), true));
});
function close(actual, expected) {
  assert.ok(
    Math.abs(actual - expected) < 1e-9,
    `${actual} differs from ${expected}`,
  );
}
test('recipe quantity scaling, final yield and per-serving math reuse the engine', () => {
  const r = recipe();
  const before = JSON.stringify(foods);
  const result = recipeNutrition(r);
  assert.equal(result.total.values.calories, 300);
  close(result.per100.calories, 100);
  assert.equal(result.perServing.calories, 150);
  assert.equal(result.servingGrams, 150);
  assert.equal(JSON.stringify(foods), before);
  const logged = scaleNutrients(recipeAsFood(r).nutrients, 150);
  for (const key of Object.keys(result.perServing)) {
    if (result.perServing[key] === null) assert.equal(logged[key], null);
    else close(logged[key], result.perServing[key]);
  }
  const edited = {
    ...r,
    ingredients: [{ ...r.ingredients[0], grams: 100 }],
    servings: 1,
  };
  assert.equal(recipeNutrition(edited).total.values.calories, 150);
  assert.equal(r.ingredients[0].grams, 200);
});
test('recipes preserve missing nutrients instead of logging known subtotals as complete', () => {
  const a = {
    foodId: 'a',
    name: 'A',
    grams: 100,
    reference: { calories: 100, protein: 10, carbs: 0, fat: 0, fiber: null },
  };
  const b = {
    foodId: 'b',
    name: 'B',
    grams: 100,
    reference: { calories: null, protein: 5, carbs: 0, fat: null, fiber: null },
  };
  const r = recipe([a, b]);
  const n = recipeNutrition(r);
  assert.equal(n.total.values.calories, 100);
  assert.equal(n.total.partial.calories, true);
  assert.equal(n.perServing.calories, null);
  assert.equal(n.perServing.protein, 7.5);
  assert.equal(n.perServing.carbs, 0);
  assert.equal(n.perServing.fat, null);
  assert.equal(n.perServing.fiber, null);
  const entry = createEntry(
    recipeAsFood(r),
    'Dinner',
    '2026-10-29',
    150,
    'x',
    now,
  );
  assert.equal(entry.nutrients.calories, null);
  assert.equal(diaryTotals([entry]).values.calories, null);
});
test('recipe validation blocks empty, invalid/duplicate/nested ingredients and invalid yields', () => {
  for (const patch of [
    { ingredients: [] },
    { yieldGrams: 0 },
    { yieldGrams: NaN },
    { servings: 0 },
    { servings: Infinity },
    { name: '' },
    { ingredients: [{ ...recipe().ingredients[0], grams: 0 }] },
    { ingredients: [{ ...recipe().ingredients[0], foodId: 'recipe:nested' }] },
  ])
    assert.throws(() => saveRecipe(emptyLibrary(), { ...recipe(), ...patch }));
  assert.throws(() =>
    saveRecipe(
      emptyLibrary(),
      recipe([recipe().ingredients[0], recipe().ingredients[0]]),
    ),
  );
  assert.throws(() => ingredientFromFood('missing', foods, 100));
  assert.throws(() => ingredientFromFood(foods[0].id, foods, -1));
  const overflow = recipe([
    {
      foodId: 'huge',
      name: 'Huge',
      grams: 1000000,
      reference: { ...values, calories: Number.MAX_VALUE },
    },
  ]);
  assert.throws(() => saveRecipe(emptyLibrary(), overflow));
});
test('recipe ingredients retain snapshots after custom edit/delete; source data is not changed', () => {
  let data = saveCustom(emptyLibrary(), custom());
  const ingredient = ingredientFromFood(
    'custom:a',
    libraryFoods(data, foods),
    100,
  );
  const r = recipe([ingredient]);
  data = saveRecipe(data, r);
  const original = recipeNutrition(data.recipes[0]);
  data = saveCustom(
    data,
    { ...custom(), servingNutrients: { ...values, calories: 999 } },
    true,
  );
  data = removeLibraryItem(data, 'custom:a');
  assert.deepEqual(recipeNutrition(data.recipes[0]), original);
  assert.equal(data.recipes[0].ingredients[0].foodId, 'custom:a');
  assert.equal(decodeLibrary(JSON.stringify(data)).recipes.length, 1);
});
test('recipe edits/deletion leave logged history stable', () => {
  let data = saveRecipe(emptyLibrary(), recipe());
  const entry = createEntry(
    recipeAsFood(data.recipes[0]),
    'Breakfast',
    '2026-10-28',
    150,
    'r',
    now,
  );
  const original = JSON.stringify(entry);
  data = saveRecipe(data, { ...recipe(), yieldGrams: 600 }, true);
  close(recipeAsFood(data.recipes[0]).nutrients.calories, 50);
  data = removeLibraryItem(data, 'recipe:a');
  assert.equal(JSON.stringify(entry), original);
  close(entry.nutrients.calories, 150);
  close(editPortion(entry, 300, now).nutrients.calories, 300);
});
test('favourites are idempotent, filterable and removed atomically with source deletion', () => {
  let data = saveRecipe(saveCustom(emptyLibrary(), custom()), recipe());
  for (const id of [foods[0].id, 'custom:a', 'recipe:a'])
    data = setFavourite(data, id, true, foods);
  data = setFavourite(data, 'custom:a', true, foods);
  assert.equal(data.favourites.length, 3);
  assert.equal(browseFoods(data, foods, [], 'Favourites', '').length, 3);
  data = setFavourite(data, foods[0].id, false, foods);
  assert.equal(data.favourites.length, 2);
  data = removeLibraryItem(data, 'custom:a');
  assert.deepEqual(data.favourites, ['recipe:a']);
  data = removeLibraryItem(data, 'recipe:a');
  assert.deepEqual(data.favourites, []);
  assert.throws(() => setFavourite(data, 'unavailable', true, foods));
  // A previously bundled source may disappear after an update; keep its stored ID but do not offer it.
  data = { ...data, favourites: ['retired-built-in'] };
  assert.equal(
    browseFoods(validateLibrary(data), foods, [], 'Favourites', '').length,
    0,
  );
});
test('recents follow actual creation time, deduplicate, ignore diary date and skip deleted records', () => {
  const data = saveCustom(emptyLibrary(), custom());
  const all = libraryFoods(data, foods);
  const make = (food, id, date, time) =>
    createEntry(food, 'Snacks', date, 100, id, time);
  const entries = [
    make(foods[0], 'a', '2026-10-29', '2026-10-30T10:00:00.000Z'),
    make(foods[1], 'b', '2026-01-01', '2026-10-30T11:00:00.000Z'),
    make(foods[0], 'c', '2026-01-02', '2026-10-30T12:00:00.000Z'),
    make(all.at(-1), 'd', '2026-10-29', '2026-10-30T13:00:00.000Z'),
  ];
  assert.deepEqual(
    recentFoods(entries, all).map((f) => f.id),
    ['custom:a', foods[0].id, foods[1].id],
  );
  assert.equal(recentFoods([], all).length, 0);
  const deleted = libraryFoods(removeLibraryItem(data, 'custom:a'), foods);
  assert.deepEqual(
    recentFoods(entries, deleted).map((f) => f.id),
    [foods[0].id, foods[1].id],
  );
  assert.equal(
    browseFoods(data, foods, entries, 'Recent', 'uncooked')[0].id,
    foods[1].id,
  );
});
test('quick-add grams/servings keep meal, past date, confirmation and independent snapshots', () => {
  const food = recipeAsFood(recipe());
  let draft = createDraft('Dinner');
  draft = foodDraftReducer(draft, { type: 'select', id: food.id });
  draft = foodDraftReducer(draft, { type: 'grams', value: '1.5' });
  const grams = portionGrams(draft.grams, 'servings', food);
  assert.equal(grams, 225);
  assert.equal(draft.confirmed, false);
  const entry = createEntry(
    food,
    draft.meal,
    '2024-02-29',
    grams,
    'quick',
    now,
  );
  assert.equal(entry.meal, 'Dinner');
  assert.equal(entry.date, '2024-02-29');
  assert.equal(entry.grams, 225);
  close(entry.nutrients.calories, 225);
  assert.equal(portionGrams('50', 'grams', food), 50);
  assert.equal(portionGrams('0', 'servings', food), null);
  assert.equal(portionGrams('1', 'servings', foods[0]), null);
  assert.equal(portionGrams('NaN', 'grams', food), null);
});
test('shared aggregation retains diary empty, zero, partial and overflow semantics', () => {
  assert.equal(sumNutrients([]).values.calories, 0);
  assert.equal(sumNutrients([{ ...values, calories: 0 }]).values.calories, 0);
  assert.equal(
    sumNutrients([{ ...values, calories: null }, values]).partial.calories,
    true,
  );
  assert.throws(() =>
    sumNutrients([
      { ...values, calories: Number.MAX_VALUE },
      { ...values, calories: Number.MAX_VALUE },
    ]),
  );
});
test('library initializes non-destructively and preserves malformed/unsupported bytes', async () => {
  const { state, storage } = memory();
  const repo = createLibraryRepository(storage);
  assert.deepEqual(await repo.load(), emptyLibrary());
  assert.equal(state.map.size, 0);
  for (const raw of [
    'bad',
    JSON.stringify({ ...emptyLibrary(), version: 2 }),
    JSON.stringify({ ...emptyLibrary(), favourites: ['x', 'x'] }),
  ]) {
    state.map.set(libraryKey, raw);
    await assert.rejects(repo.load());
    await assert.rejects(repo.save(emptyLibrary(), emptyLibrary()));
    assert.equal(state.map.get(libraryKey), raw);
  }
  state.readError = true;
  await assert.rejects(repo.load());
});
test('failed/interrupted library writes retry idempotently; stale changes do not overwrite', async () => {
  const { state, storage } = memory();
  const repo = createLibraryRepository(storage);
  const original = await repo.load();
  const next = saveCustom(original, custom());
  state.writeError = true;
  await assert.rejects(repo.save(next, original));
  assert.equal(state.map.size, 0);
  state.writeError = false;
  state.ackError = true;
  await assert.rejects(repo.save(next, original));
  state.ackError = false;
  assert.equal((await repo.save(next, original)).customFoods.length, 1);
  await assert.rejects(
    repo.save(saveRecipe(original, recipe()), original),
    /changed/,
  );
  const fav = setFavourite(next, 'custom:a', true, foods);
  await Promise.all([repo.save(fav, next), repo.save(fav, next)]);
  assert.equal((await repo.load()).favourites.length, 1);
  const deleted = removeLibraryItem(fav, 'custom:a');
  state.ackError = true;
  await assert.rejects(repo.save(deleted, fav));
  state.ackError = false;
  const result = await repo.save(deleted, fav);
  assert.equal(result.customFoods.length, 0);
  assert.equal(result.favourites.length, 0);
});
test('library and real diary entries survive SQLite close/reopen without health/appearance changes', async () => {
  const directory = mkdtempSync(join(tmpdir(), 'bites2go-library-test-'));
  const file = join(directory, 'library.db');
  let db;
  const open = () => {
    db = new DatabaseSync(file);
    db.exec(
      'CREATE TABLE IF NOT EXISTS storage (key TEXT PRIMARY KEY NOT NULL,value TEXT)',
    );
    return {
      getItem: async (key) =>
        db.prepare('SELECT value FROM storage WHERE key=?').get(key)?.value ??
        null,
      setItem: async (key, value) => {
        db.prepare(
          'INSERT INTO storage VALUES (?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value',
        ).run(key, value);
      },
    };
  };
  try {
    let storage = open();
    let repo = createLibraryRepository(storage);
    let diary = createDiaryRepository(storage);
    await storage.setItem('bites2go.health.v1', 'health fixture');
    await storage.setItem('bites2go.appearance.v1', 'dark');
    let data = saveCustom(emptyLibrary(), custom());
    data = saveRecipe(
      data,
      recipe([ingredientFromFood('custom:a', libraryFoods(data, foods), 100)]),
    );
    data = setFavourite(data, 'recipe:a', true, foods);
    await repo.save(data, emptyLibrary());
    const entry = createEntry(
      recipeAsFood(data.recipes[0]),
      'Lunch',
      '2026-10-29',
      150,
      'logged',
      now,
    );
    await diary.save(entry);
    db.close();
    db = null;
    storage = open();
    repo = createLibraryRepository(storage);
    diary = createDiaryRepository(storage);
    assert.deepEqual(await repo.load(), data);
    assert.deepEqual(await diary.loadAll(), [entry]);
    assert.equal(await storage.getItem('bites2go.health.v1'), 'health fixture');
    assert.equal(await storage.getItem('bites2go.appearance.v1'), 'dark');
    const deleted = removeLibraryItem(data, 'recipe:a');
    await repo.save(deleted, data);
    db.close();
    db = null;
    storage = open();
    repo = createLibraryRepository(storage);
    diary = createDiaryRepository(storage);
    assert.equal((await repo.load()).recipes.length, 0);
    assert.equal((await repo.load()).favourites.length, 0);
    assert.deepEqual(await diary.loadAll(), [entry]);
  } finally {
    db?.close();
    assert.ok(resolve(directory).startsWith(resolve(tmpdir()) + sep));
    assert.ok(directory.includes('bites2go-library-test-'));
    rmSync(directory, { recursive: true, force: true });
  }
});
