import test from 'node:test';
import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';
import {
  createEntry,
  editPortion,
  diaryTotals,
  decodeDiary,
  localDateKey,
  shiftDay,
  validDateKey,
} from '../src/domain/diary.ts';
import { createDiaryRepository } from '../src/storage/diaryRepository.ts';
import { foods } from '../src/data/foods.ts';
const now = '2026-10-30T12:00:00.000Z';
const entry = (id = 'one', date = '2026-10-30', meal = 'Lunch') =>
  createEntry(foods[0], meal, date, 200, id, now);
function memory(raw = null) {
  const state = {
    raw,
    readError: false,
    writeError: false,
    ackError: false,
    writes: 0,
  };
  const storage = {
    getItem: async () => {
      if (state.readError) throw Error('read');
      return state.raw;
    },
    setItem: async (_key, value) => {
      state.writes++;
      if (state.writeError) throw Error('write');
      state.raw = value;
      if (state.ackError) throw Error('ack');
    },
  };
  return { state, storage, repo: createDiaryRepository(storage) };
}
test('empty/missing diary and save survive repository recreation with exact snapshots', async () => {
  const { state, storage, repo } = memory();
  assert.deepEqual(await repo.loadAll(), []);
  assert.equal(state.writes, 0);
  const value = entry();
  await repo.save(value);
  assert.deepEqual(await createDiaryRepository(storage).loadDate(value.date), [
    value,
  ]);
  assert.equal(state.writes, 1);
});
test('dates and all meal categories remain separate; no demo seed consumption', async () => {
  const { repo } = memory();
  for (const meal of ['Breakfast', 'Lunch', 'Snacks', 'Dinner'])
    await repo.save(entry(meal, '2026-10-29', meal));
  await repo.save(entry());
  assert.equal((await repo.loadDate('2026-10-29')).length, 4);
  assert.equal((await repo.loadDate('2026-10-30')).length, 1);
  assert.deepEqual(await repo.loadDate('2026-10-28'), []);
  assert.deepEqual(
    (await repo.loadDate('2026-10-29')).map((e) => e.meal),
    ['Breakfast', 'Lunch', 'Snacks', 'Dinner'],
  );
});
test('totals use snapshots, preserve nulls and report partial coverage', () => {
  const a = entry();
  const b = {
    ...entry('two'),
    nutrients: {
      calories: null,
      protein: null,
      carbs: null,
      fat: null,
      fiber: null,
    },
  };
  assert.deepEqual(diaryTotals([a]).values, {
    calories: 300,
    protein: 6,
    carbs: 64,
    fat: 2,
    fiber: null,
  });
  const partial = diaryTotals([a, b]);
  assert.equal(partial.values.calories, 300);
  assert.equal(partial.partial.calories, true);
  assert.equal(partial.values.fiber, null);
  assert.equal(diaryTotals([b]).values.calories, null);
  assert.equal(diaryTotals([]).values.calories, 0);
  assert.equal(diaryTotals([]).count, 0);
  assert.equal(diaryTotals([]).partial.calories, false);
});
test('edit uses recorded basis, preserves identity/date, and cancellation makes no write', async () => {
  const { repo, state } = memory();
  const original = entry();
  await repo.save(original);
  const before = state.raw;
  const draft = editPortion(original, 12.5, '2026-10-31T12:00:00.000Z');
  assert.equal(state.raw, before);
  assert.equal(original.grams, 200);
  await repo.update(draft, original);
  const saved = (await repo.loadAll())[0];
  assert.equal(saved.grams, 12.5);
  assert.equal(saved.nutrients.calories, 18.75);
  assert.equal(saved.id, original.id);
  assert.equal(saved.date, original.date);
  assert.equal(saved.createdAt, original.createdAt);
  await repo.remove(saved);
  assert.deepEqual(await repo.loadAll(), []);
});
test('historical snapshots do not follow changes in food fixtures', async () => {
  const food = structuredClone(foods[0]);
  const record = createEntry(food, 'Dinner', '2026-10-29', 100, 'history', now);
  const { repo } = memory();
  await repo.save(record);
  food.nutrients.calories = 999;
  food.name = 'changed';
  const saved = (await repo.loadAll())[0];
  assert.equal(saved.foodName, record.foodName);
  assert.equal(saved.nutrients.calories, 150);
  assert.equal(editPortion(saved, 200, now).nutrients.calories, 300);
});
test('duplicate submissions and concurrent saves do not duplicate or lose entries', async () => {
  const { repo, state } = memory();
  const first = entry();
  await Promise.all([
    repo.save(first),
    repo.save(first),
    repo.save(entry('two')),
  ]);
  assert.equal((await repo.loadAll()).length, 2);
  assert.equal(state.writes, 2);
  await assert.rejects(
    repo.save({ ...first, grams: 100, nutrients: { ...first.reference } }),
    /different details/,
  );
});
test('read/write failures preserve bytes and retryable operations; queue recovers', async () => {
  const { repo, state } = memory();
  await repo.save(entry());
  const before = state.raw;
  state.readError = true;
  await assert.rejects(repo.loadAll(), /not cleared/);
  await assert.rejects(repo.save(entry('two')), /not cleared/);
  assert.equal(state.raw, before);
  state.readError = false;
  state.writeError = true;
  await assert.rejects(repo.save(entry('two')), /Could not confirm/);
  assert.equal(state.raw, before);
  await assert.rejects(
    repo.update(editPortion(entry(), 100, now), entry()),
    /Could not confirm/,
  );
  await assert.rejects(repo.remove(entry()), /Could not confirm/);
  assert.equal(state.raw, before);
  state.writeError = false;
  await repo.save(entry('two'));
  assert.equal((await repo.loadAll()).length, 2);
});
test('retry after uncertain write acknowledgment is idempotent for add, edit and delete', async () => {
  const { repo, state } = memory();
  state.ackError = true;
  await assert.rejects(repo.save(entry()));
  state.ackError = false;
  await repo.save(entry());
  assert.equal((await repo.loadAll()).length, 1);
  const changed = editPortion(entry(), 125, now);
  state.ackError = true;
  await assert.rejects(repo.update(changed, entry()));
  state.ackError = false;
  await repo.update(changed, entry());
  assert.equal((await repo.loadAll())[0].grams, 125);
  state.ackError = true;
  await assert.rejects(repo.remove(changed));
  state.ackError = false;
  await repo.remove(changed);
  assert.deepEqual(await repo.loadAll(), []);
});
test('invalid records and unknown versions block mutation without discarding recoverable bytes', async () => {
  const bad = [
    '',
    '{',
    '{}',
    JSON.stringify({ version: 2, entries: [] }),
    JSON.stringify({ version: 1, entries: [{ ...entry(), meal: 'Other' }] }),
    JSON.stringify({
      version: 1,
      entries: [{ ...entry(), date: '2026-02-30' }],
    }),
    JSON.stringify({
      version: 1,
      entries: [
        { ...entry(), nutrients: { ...entry().nutrients, calories: null } },
      ],
    }),
    JSON.stringify({ version: 1, entries: [entry(), entry()] }),
  ];
  for (const raw of bad) {
    const { repo, state } = memory(raw);
    await assert.rejects(repo.loadAll());
    await assert.rejects(repo.save(entry('new')));
    assert.equal(state.raw, raw);
    assert.equal(state.writes, 0);
  }
  assert.throws(() =>
    decodeDiary(
      JSON.stringify({ version: 1, entries: [{ ...entry(), grams: 0 }] }),
    ),
  );
});
test('stale edits and deletes cannot overwrite a newer entry', async () => {
  const { repo } = memory();
  await repo.save(entry());
  await repo.update(editPortion(entry(), 150, now), entry());
  await assert.rejects(
    repo.update(editPortion(entry(), 50, now), entry()),
    /changed/,
  );
  await assert.rejects(repo.remove(entry()), /changed/);
});
test('calendar validation and day stepping respect leap/month/year boundaries', () => {
  assert.equal(shiftDay('2024-02-28', 1), '2024-02-29');
  assert.equal(shiftDay('2024-03-01', -1), '2024-02-29');
  assert.equal(shiftDay('2026-12-31', 1), '2027-01-01');
  assert.equal(validDateKey('2026-02-29'), false);
  assert.equal(validDateKey('2026-13-01'), false);
  assert.equal(localDateKey(new Date(2026, 9, 30, 23, 59)), '2026-10-30');
});
test('local date keys near UTC midnight and DST retain explicit calendar dates', () => {
  const script = `import {localDateKey,shiftDay} from './src/domain/diary.ts'; console.log(JSON.stringify([localDateKey(new Date('2026-10-30T00:30:00Z')),shiftDay('2026-03-08',1),shiftDay('2026-11-01',1)]));`;
  for (const [TZ, expected] of [
    ['Asia/Kolkata', '2026-10-30'],
    ['America/Los_Angeles', '2026-10-29'],
  ]) {
    const result = execFileSync(
      process.execPath,
      ['--experimental-strip-types', '--input-type=module', '-e', script],
      {
        encoding: 'utf8',
        env: { ...process.env, TZ },
        stdio: ['pipe', 'pipe', 'pipe'],
      },
    );
    assert.deepEqual(JSON.parse(result), [
      expected,
      '2026-03-09',
      '2026-11-02',
    ]);
  }
});

test('unknown values survive persistence; overflowing stored totals are rejected safely', async () => {
  const unknownFood = {
    ...foods[0],
    nutrients: {
      calories: null,
      protein: 0,
      carbs: null,
      fat: null,
      fiber: null,
    },
  };
  const { repo } = memory();
  const saved = createEntry(
    unknownFood,
    'Snacks',
    '2026-10-30',
    50,
    'unknown',
    now,
  );
  await repo.save(saved);
  assert.deepEqual((await repo.loadAll())[0].nutrients, unknownFood.nutrients);
  const enormousFood = {
    ...foods[0],
    nutrients: {
      calories: Number.MAX_VALUE,
      protein: 0,
      carbs: 0,
      fat: 0,
      fiber: null,
    },
  };
  const a = createEntry(
    enormousFood,
    'Lunch',
    '2026-10-30',
    100,
    'large1',
    now,
  );
  const b = { ...a, id: 'large2' };
  const raw = JSON.stringify({ version: 1, entries: [a, b] });
  const corrupt = memory(raw);
  await assert.rejects(corrupt.repo.loadAll());
  assert.equal(corrupt.state.raw, raw);
  assert.equal(corrupt.state.writes, 0);
});

test('large date-separated histories retain order, unknowns and per-day overflow validation', () => {
  const entries = Array.from({ length: 5000 }, (_, i) =>
    entry(String(i), shiftDay('1990-01-01', i)),
  );
  assert.deepEqual(
    decodeDiary(JSON.stringify({ version: 1, entries })),
    entries,
  );
  const huge = entry('huge');
  huge.reference.calories = 5e307;
  huge.nutrients.calories = 1e308;
  const second = { ...huge, id: 'second', date: shiftDay(huge.date, -1) };
  assert.equal(
    decodeDiary(JSON.stringify({ version: 1, entries: [huge, second] })).length,
    2,
  );
  assert.throws(() =>
    decodeDiary(
      JSON.stringify({
        version: 1,
        entries: [huge, { ...second, date: huge.date }],
      }),
    ),
  );
});

test('reload after uncertain save, edit and delete reconciles persisted outcomes', async () => {
  const { repo, state } = memory();
  state.ackError = true;
  const value = entry();
  await assert.rejects(repo.save(value));
  assert.deepEqual(await repo.loadAll(), [value]);
  const changed = editPortion(value, 300, now);
  await assert.rejects(repo.update(changed, value));
  assert.deepEqual(await repo.loadAll(), [changed]);
  await assert.rejects(repo.remove(changed));
  assert.deepEqual(await repo.loadAll(), []);
});
