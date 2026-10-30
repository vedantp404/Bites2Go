import test from 'node:test';
import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';
import {
  calendarState,
  calendarReducer,
  indexDiaryDates,
  loggedDatesInMonth,
  monthCells,
  monthKey,
  shiftMonth,
} from '../src/domain/calendar.ts';
import { createEntry, diaryTotals, editPortion } from '../src/domain/diary.ts';
import { createDiaryRepository } from '../src/storage/diaryRepository.ts';
import { foods } from '../src/data/foods.ts';
const days = (month) => monthCells(month).filter(Boolean);
const now = '2026-10-30T12:00:00.000Z';
const entry = (date, id, meal = 'Lunch') =>
  createEntry(foods[0], meal, date, 200, id, now);
test('month lengths and leap-century rules are correct', () => {
  for (const [month, count] of [
    ['2026-01', 31],
    ['2026-04', 30],
    ['2026-02', 28],
    ['2024-02', 29],
    ['2000-02', 29],
    ['1900-02', 28],
    ['2100-02', 28],
  ]) {
    const cells = monthCells(month);
    assert.equal(days(month).length, count);
    assert.equal(cells.length % 7, 0);
    assert.equal(new Set(days(month)).size, count);
    assert.equal(days(month)[0], `${month}-01`);
  }
});
test('Monday-first alignment and padding include six-row months', () => {
  assert.equal(monthCells('2026-06')[0], '2026-06-01');
  assert.equal(monthCells('2026-02')[6], '2026-02-01');
  assert.deepEqual(monthCells('2026-02').slice(0, 6), Array(6).fill(null));
  assert.equal(monthCells('2026-03').length, 42);
  assert.equal(monthCells('2026-10')[3], '2026-10-01');
});
test('month/year bounds validate dates without interpreting UTC timestamps', () => {
  assert.equal(shiftMonth('2026-12', 1), '2027-01');
  assert.equal(shiftMonth('2026-01', -1), '2025-12');
  assert.equal(shiftMonth('2024-03', -1), '2024-02');
  for (const month of ['2026-13', '2026-00', '2026-1', '2026-01-01', 'bad'])
    assert.throws(() => monthCells(month));
  assert.throws(() => shiftMonth('1900-01', -1));
  assert.throws(() => shiftMonth('9999-12', 1));
  assert.throws(() => shiftMonth('2026-01', 0.5));
  assert.throws(() => monthKey('2026-02-30'));
});
test('selected day stays independent from month browsing and today; returning to today is explicit', () => {
  let state = calendarState('2026-10-30');
  state = calendarReducer(state, { type: 'select', date: '2024-02-29' });
  const selected = state.selected;
  state = calendarReducer(state, { type: 'month', offset: 1 });
  assert.equal(state.month, '2024-03');
  assert.equal(state.selected, selected);
  state = calendarReducer(state, { type: 'day', offset: 1 });
  assert.equal(state.selected, '2024-03-01');
  assert.equal(state.month, '2024-03');
  state = calendarReducer(state, { type: 'today', date: '2026-10-31' });
  assert.deepEqual(state, { selected: '2026-10-31', month: '2026-10' });
  assert.throws(() => calendarReducer(state, { type: 'select', date: 'bad' }));
});
test('month indicators reflect only saved entries, not today or duplicate foods', () => {
  const entries = [
    entry('2026-10-03', 'a'),
    entry('2026-10-03', 'b'),
    entry('2026-09-30', 'c'),
    entry('2025-10-03', 'd'),
  ];
  const index = indexDiaryDates(entries);
  assert.deepEqual(loggedDatesInMonth(index, '2026-10'), ['2026-10-03']);
  assert.equal(index.get('2026-10-03').length, 2);
  assert.equal(index.has('2026-10-30'), false);
  assert.deepEqual(loggedDatesInMonth(indexDiaryDates([]), '2026-10'), []);
  assert.equal(diaryTotals(index.get('2026-10-04') ?? []).values.calories, 0);
  assert.equal(diaryTotals(index.get('2026-10-03')).values.calories, 600);
});
test('historical selection, add, edit, delete and restart share existing storage without mixing dates', async () => {
  let raw = null,
    reads = 0;
  const storage = {
    getItem: async () => {
      reads++;
      return raw;
    },
    setItem: async (_key, value) => {
      raw = value;
    },
  };
  const repo = createDiaryRepository(storage);
  await repo.save(entry('2026-10-30', 'today'));
  const state = calendarReducer(calendarState('2026-10-30'), {
    type: 'select',
    date: '2024-02-29',
  });
  const historical = entry(state.selected, 'past', 'Breakfast');
  await repo.save(historical);
  const before = raw;
  let index = indexDiaryDates(await repo.loadAll());
  const readsBeforeNavigation = reads;
  assert.equal(index.get(state.selected)[0].meal, 'Breakfast');
  assert.deepEqual(loggedDatesInMonth(index, state.month), [state.selected]);
  calendarReducer(state, { type: 'month', offset: 1 });
  assert.equal(raw, before);
  assert.equal(reads, readsBeforeNavigation);
  const changed = editPortion(historical, 100, now);
  await repo.update(changed, historical);
  index = indexDiaryDates(await repo.loadAll());
  assert.equal(diaryTotals(index.get(state.selected)).values.calories, 150);
  assert.equal(diaryTotals(index.get('2026-10-30')).values.calories, 300);
  await repo.remove(changed);
  index = indexDiaryDates(await createDiaryRepository(storage).loadAll());
  assert.deepEqual(loggedDatesInMonth(index, '2024-02'), []);
  assert.equal(index.get('2026-10-30').length, 1);
  assert.equal(diaryTotals(index.get(state.selected) ?? []).count, 0);
});
test('historical unknown nutrients remain unknown and partial totals stay partial', () => {
  const food = {
    ...foods[0],
    nutrients: {
      calories: null,
      protein: null,
      carbs: null,
      fat: null,
      fiber: null,
    },
  };
  const missing = createEntry(
    food,
    'Dinner',
    '2024-02-29',
    100,
    'missing',
    now,
  );
  const index = indexDiaryDates([missing, entry('2024-02-29', 'known')]);
  const total = diaryTotals(index.get('2024-02-29'));
  assert.equal(total.values.calories, 300);
  assert.equal(total.partial.calories, true);
  assert.equal(total.values.fiber, null);
});
test('local dates and calendar layout stay correct near midnight and DST across timezones', () => {
  const script = `import {localDateKey} from './src/domain/diary.ts'; import {monthCells,calendarState,calendarReducer} from './src/domain/calendar.ts';console.log(JSON.stringify([localDateKey(new Date('2026-03-01T00:30:00Z')),monthCells('2026-03').indexOf('2026-03-01'),calendarReducer(calendarState('2026-03-08'),{type:'day',offset:1}).selected]));`;
  for (const [TZ, date] of [
    ['Asia/Kolkata', '2026-03-01'],
    ['America/Los_Angeles', '2026-02-28'],
  ]) {
    const output = execFileSync(
      process.execPath,
      ['--experimental-strip-types', '--input-type=module', '-e', script],
      {
        encoding: 'utf8',
        env: { ...process.env, TZ },
        stdio: ['pipe', 'pipe', 'pipe'],
      },
    );
    assert.deepEqual(JSON.parse(output), [date, 6, '2026-03-09']);
  }
});
