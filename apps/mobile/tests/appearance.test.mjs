import test from 'node:test';
import assert from 'node:assert/strict';
import {
  createAppearanceStore,
  effectiveTheme,
  preferenceKey,
} from '../src/theme/appearance.ts';
import { lightTheme, darkTheme } from '../src/theme/tokens.ts';
import { foodImageKey } from '../src/data/foodImages.ts';
const memory = () => {
  const data = new Map();
  return {
    data,
    async getItemAsync(key) {
      return data.get(key) ?? null;
    },
    async setItemAsync(key, value) {
      data.set(key, value);
    },
  };
};
test('first launch defaults to system; every selection survives a new store', async () => {
  const storage = memory();
  const store = createAppearanceStore(storage);
  assert.equal(store.getSnapshot().ready, false);
  await store.load();
  assert.equal(store.getSnapshot().preference, 'system');
  for (const choice of ['light', 'dark', 'system']) {
    await store.select(choice);
    const restart = createAppearanceStore(storage);
    await restart.load();
    assert.equal(restart.getSnapshot().preference, choice);
    assert.equal(storage.data.get(preferenceKey), choice);
  }
  assert.deepEqual([...storage.data.keys()], [preferenceKey]);
});
test('system tracks changes; explicit modes ignore OS changes; unspecified OS uses light', () => {
  assert.equal(effectiveTheme('system', 'light'), 'light');
  assert.equal(effectiveTheme('system', 'dark'), 'dark');
  assert.equal(effectiveTheme('system', null), 'light');
  for (const mode of ['light', 'dark'])
    for (const os of ['light', 'dark', null])
      assert.equal(effectiveTheme(mode, os), mode);
});
test('subscribers see selection immediately before persistence finishes; concurrent writes blocked', async () => {
  let finish;
  const storage = memory();
  storage.setItemAsync = () =>
    new Promise((resolve) => {
      finish = resolve;
    });
  const store = createAppearanceStore(storage);
  await store.load();
  const seen = [];
  const unsubscribe = store.subscribe(() =>
    seen.push(store.getSnapshot().preference),
  );
  const pending = store.select('dark');
  assert.equal(store.getSnapshot().preference, 'dark');
  assert.equal(store.getSnapshot().saving, true);
  assert.deepEqual(seen, ['dark']);
  await store.select('light');
  assert.equal(store.getSnapshot().preference, 'dark');
  finish();
  await pending;
  assert.equal(store.getSnapshot().saving, false);
  unsubscribe();
});
test('read/write errors remain visible; retries save; invalid stored values are not overwritten on read', async () => {
  const storage = memory();
  storage.data.set(preferenceKey, 'invalid');
  const store = createAppearanceStore(storage);
  await store.load();
  assert.equal(store.getSnapshot().preference, 'system');
  assert.ok(store.getSnapshot().error);
  assert.equal(storage.data.get(preferenceKey), 'invalid');
  storage.setItemAsync = async () => {
    throw Error('disk');
  };
  await store.select('dark');
  assert.equal(store.getSnapshot().preference, 'dark');
  assert.match(store.getSnapshot().error, /not saved/);
  storage.setItemAsync = async (key, value) => {
    storage.data.set(key, value);
  };
  await store.select('dark');
  assert.equal(store.getSnapshot().error, '');
  assert.equal(storage.data.get(preferenceKey), 'dark');
  const broken = createAppearanceStore({
    ...storage,
    getItemAsync: async () => {
      throw Error('read');
    },
  });
  await broken.load();
  assert.equal(broken.getSnapshot().ready, true);
  assert.match(broken.getSnapshot().error, /could not be loaded/);
});
test('both themes expose the same semantic tokens and adequate touch targets', () => {
  assert.deepEqual(
    Object.keys(lightTheme.colors),
    Object.keys(darkTheme.colors),
  );
  for (const t of [lightTheme, darkTheme]) {
    for (const name of [
      'background',
      'surface',
      'elevated',
      'text',
      'muted',
      'border',
      'primary',
      'onPrimary',
      'secondary',
      'success',
      'warning',
      'error',
      'carbs',
      'protein',
      'fat',
      'input',
      'selected',
      'disabled',
    ])
      assert.match(t.colors[name], /^#[0-9A-F]{6}$/i);
    assert.ok(t.sizing.touchTarget >= 48);
  }
});
test('image registry uses stable IDs, including missing, historical null IDs and load errors', () => {
  assert.equal(foodImageKey('apple'), 'apple');
  assert.equal(foodImageKey('banana'), 'banana');
  for (const id of ['unknown', 'Cooked white rice', 'toString', null])
    assert.equal(foodImageKey(id), null);
  assert.equal(foodImageKey('apple', true), null);
  assert.equal(foodImageKey('apple', false), 'apple');
});
