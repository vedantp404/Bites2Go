import test from 'node:test';
import assert from 'node:assert/strict';
import { execFileSync } from 'node:child_process';
import {
  rollingRange,
  rangeDates,
  buildInsights,
  insightView,
  selectedInsightDate,
  dayNutrientLabel,
  eligibilityNote,
} from '../src/domain/insights.ts';
import { createEntry } from '../src/domain/diary.ts';
import {
  emptyHealth,
  saveSettings,
  recordWeight,
} from '../src/domain/health.ts';
import { foods } from '../src/data/foods.ts';
import { meals } from '../src/domain/food.ts';
const today = '2026-10-30';
const range = { start: '2026-10-24', end: today };
const values = { calories: 250, protein: 25, carbs: 50, fat: 10, fiber: 2 };
const food = { ...foods[0], nutrients: values };
function day(date = '2026-10-29', overrides = {}, count = 4) {
  return meals
    .slice(0, count)
    .map((meal, index) =>
      createEntry(
        { ...food, nutrients: { ...values, ...overrides } },
        meal,
        date,
        100,
        `${date}-${index}`,
        '2026-10-30T12:00:00.000Z',
      ),
    );
}
const goals = () =>
  saveSettings(
    emptyHealth(),
    '2026-10-01',
    { calories: 1000, protein: 100, carbs: 200, fat: 40 },
    null,
    null,
    today,
  );
const build = (entries = [], health = goals(), selected = range) =>
  buildInsights(entries, health, selected, today);
test('7/30-day windows include today across month/year/leap boundaries', () => {
  assert.deepEqual(rollingRange('2026-01-03', 7), {
    start: '2025-12-28',
    end: '2026-01-03',
  });
  assert.equal(rangeDates(rollingRange(today, 30), today).length, 30);
  assert.deepEqual(rollingRange('2024-03-01', 7), {
    start: '2024-02-24',
    end: '2024-03-01',
  });
  assert.ok(
    rangeDates(rollingRange('2024-03-01', 7), '2024-03-01').includes(
      '2024-02-29',
    ),
  );
  assert.deepEqual(rollingRange('1900-01-01', 30), {
    start: '1900-01-01',
    end: '1900-01-01',
  });
});
test('custom ranges reject invalid/reversed/future/overlong dates; allow bounded long labels', () => {
  for (const r of [
    { start: '2026-02-30', end: today },
    { start: today, end: '2026-10-29' },
    { start: today, end: '2026-10-31' },
    { start: '2020-01-01', end: today },
  ])
    assert.throws(() => rangeDates(r, today));
  assert.equal(
    rangeDates({ start: '2026-07-31', end: today }, today).length,
    92,
  );
  assert.equal(rangeDates({ start: today, end: today }, today).length, 1);
  assert.equal(selectedInsightDate('2026-10-01', range), today);
  assert.equal(selectedInsightDate('2026-10-28', range), '2026-10-28');
});
test('local dates survive DST and UTC-midnight differences', () => {
  const source = `import {localDateKey} from './src/domain/diary.ts'; import {rollingRange,rangeDates} from './src/domain/insights.ts'; const today=localDateKey(new Date('2026-03-09T02:00:00Z')); console.log(JSON.stringify({today,days:rangeDates(rollingRange(today,7),today)}));`;
  const result = JSON.parse(
    execFileSync(
      process.execPath,
      ['--experimental-strip-types', '--input-type=module', '-e', source],
      {
        cwd: process.cwd(),
        env: { ...process.env, TZ: 'America/New_York' },
        encoding: 'utf8',
      },
    ),
  );
  assert.equal(result.today, '2026-03-08');
  assert.equal(result.days.length, 7);
  assert.equal(result.days[0], '2026-03-02');
  const india = JSON.parse(
    execFileSync(
      process.execPath,
      ['--experimental-strip-types', '--input-type=module', '-e', source],
      {
        cwd: process.cwd(),
        env: { ...process.env, TZ: 'Asia/Kolkata' },
        encoding: 'utf8',
      },
    ),
  );
  assert.equal(india.today, '2026-03-09');
});
test('empty diary is unknown intake with no average, percentage or fake history', () => {
  const data = build();
  assert.equal(data.noEntryDays, 7);
  assert.equal(data.loggedDays, 0);
  for (const key of Object.keys(values)) {
    assert.equal(data.stats[key].average, null);
    assert.equal(data.stats[key].eligible, 0);
    assert.equal(data.days[0].nutrients[key].value, null);
  }
  assert.equal(data.stats.calories.percent, null);
  assert.match(
    dayNutrientLabel(data.days[0], 'calories'),
    /No entries; intake unknown/,
  );
  assert.match(data.observations[0], /does not mean zero intake/);
});
test('complete snapshots aggregate and compare correctly without modifying inputs', () => {
  const entries = day(),
    health = goals(),
    before = JSON.stringify({ entries, health });
  const data = build(entries, health);
  assert.equal(data.stats.calories.average, 1000);
  assert.equal(data.stats.protein.average, 100);
  assert.equal(data.stats.fiber.average, 8);
  assert.equal(data.stats.calories.eligible, 1);
  assert.equal(data.stats.calories.within, 1);
  assert.equal(data.stats.calories.percent, 100);
  assert.equal(JSON.stringify({ entries, health }), before);
  const changedFood = { ...food, nutrients: { ...values, calories: 999 } };
  assert.equal(changedFood.nutrients.calories, 999);
  assert.equal(build(entries).stats.calories.average, 1000);
});
test('unknown nutrients exclude only the affected nutrient and preserve known subtotals', () => {
  const entries = day();
  entries[0] = createEntry(
    { ...food, nutrients: { ...values, protein: null } },
    'Breakfast',
    '2026-10-29',
    100,
    '2026-10-29-0',
    '2026-10-30T12:00:00.000Z',
  );
  const data = build(entries),
    record = data.days.at(-2);
  assert.equal(record.nutrients.protein.value, 75);
  assert.equal(record.nutrients.protein.partial, true);
  assert.equal(data.stats.protein.average, null);
  assert.equal(data.stats.protein.goalDays, 0);
  assert.equal(data.stats.protein.unknownDays, 1);
  assert.equal(data.stats.calories.average, 1000);
  assert.equal(data.stats.calories.eligible, 1);
  assert.match(dayNutrientLabel(record, 'protein'), /known subtotal only/);
  const unknown = build(day('2026-10-29', { calories: null }));
  assert.equal(unknown.days.at(-2).nutrients.calories.value, null);
  assert.equal(unknown.stats.calories.goalDays, 0);
});
test('partly logged meal sections are visible but excluded from period calculations', () => {
  const data = build(day('2026-10-29', {}, 2));
  assert.equal(data.loggedDays, 1);
  assert.equal(data.limitedMealDays, 1);
  assert.equal(data.days.at(-2).nutrients.calories.value, 500);
  assert.equal(data.stats.calories.eligible, 0);
  assert.equal(data.stats.calories.percent, null);
  assert.match(dayNutrientLabel(data.days.at(-2), 'calories'), /2 of 4/);
  assert.match(eligibilityNote, /intentionally skipped meals/);
});
test('today remains in progress; future entries do not enter the selected range', () => {
  const data = build([
    ...day(today),
    ...day('2026-10-31'),
    ...day('2026-10-29'),
  ]);
  assert.equal(data.loggedDays, 2);
  assert.equal(data.stats.calories.eligible, 1);
  assert.equal(data.days.at(-1).inProgress, true);
  assert.match(dayNutrientLabel(data.days.at(-1), 'calories'), /in progress/);
});
test('duplicate identities fail closed; distinct entries in a meal are counted once each', () => {
  const entries = day();
  assert.throws(() => build([...entries, entries[0]]), /Duplicate/);
  const extra = { ...entries[0], id: 'another-serving' };
  assert.equal(build([...entries, extra]).stats.calories.average, 1250);
});
test('averages use eligible days only and explicit zero remains a legitimate value', () => {
  const data = build([
    ...day('2026-10-27'),
    ...day('2026-10-28', { calories: 500 }),
    ...day('2026-10-29', { calories: null }),
  ]);
  assert.equal(data.stats.calories.eligible, 2);
  assert.equal(data.stats.calories.average, 1500);
  assert.equal(data.stats.protein.eligible, 3);
  assert.equal(data.stats.protein.average, 100);
  const zero = build(day('2026-10-29', { calories: 0 }));
  assert.equal(zero.stats.calories.average, 0);
  assert.equal(zero.stats.calories.eligible, 1);
  assert.equal(zero.stats.calories.below, 1);
});
test('effective-dated targets use each historical date and only paired eligible days', () => {
  const health = saveSettings(
    goals(),
    '2026-10-28',
    { calories: 2000, protein: 200, carbs: 200, fat: 40 },
    null,
    null,
    today,
  );
  const data = build([...day('2026-10-27'), ...day('2026-10-28')], health);
  assert.equal(data.stats.calories.within, 1);
  assert.equal(data.stats.calories.below, 1);
  assert.equal(data.stats.calories.percent, 50);
  assert.equal(data.stats.calories.averageTarget, 1500);
  assert.equal(data.stats.calories.pairedAverage, 1000);
  assert.equal(
    data.days.find((d) => d.date === '2026-10-27').nutrients.calories.target,
    1000,
  );
  const unset = build(day(), emptyHealth());
  assert.equal(unset.stats.calories.average, 1000);
  assert.equal(unset.stats.calories.percent, null);
  const disabled = saveSettings(
    goals(),
    '2026-10-29',
    { calories: 0, protein: null, carbs: null, fat: null },
    null,
    null,
    today,
  );
  assert.equal(build(day(), disabled).stats.calories.goalDays, 0);
});
test('inclusive tolerance handles exact/below/above targets and excluded unknown days', () => {
  const data = build([
    ...day('2026-10-24', { calories: 225, protein: 22.5 }),
    ...day('2026-10-25', { calories: 275, protein: 27.5 }),
    ...day('2026-10-26', { calories: 224, protein: 22.4 }),
    ...day('2026-10-27', { calories: 276, protein: 27.6 }),
    ...day('2026-10-28'),
    ...day('2026-10-29', { calories: null, protein: null }),
  ]);
  for (const key of ['calories', 'protein']) {
    assert.equal(data.stats[key].goalDays, 5);
    assert.equal(data.stats[key].within, 3);
    assert.equal(data.stats[key].below, 1);
    assert.equal(data.stats[key].above, 1);
    assert.equal(data.stats[key].percent, 60);
  }
});
test('weight summaries use actual in-range measurements and safe current-goal dates', () => {
  assert.equal(build().weight.change, null);
  let health = recordWeight(
    goals(),
    { id: 'first', date: '2026-10-24', kg: 80, unit: 'kg' },
    false,
    today,
  );
  assert.equal(build([], health).weight.change, null);
  health = recordWeight(
    health,
    { id: 'last', date: '2026-10-29', kg: 79, unit: 'kg' },
    false,
    today,
  );
  health = saveSettings(
    health,
    '2026-10-24',
    { calories: 1000, protein: 100, carbs: 200, fat: 40 },
    170,
    75,
    today,
  );
  const weight = build([], health).weight;
  assert.equal(weight.change, -1);
  assert.equal(weight.records.length, 2);
  assert.equal(weight.progress.percent, 20);
  const later = saveSettings(
    health,
    today,
    { calories: 1000, protein: 100, carbs: 200, fat: 40 },
    170,
    74,
    today,
  );
  assert.equal(build([], later).weight.goal, null);
  const past = build([], health, { start: '2026-10-25', end: '2026-10-28' });
  assert.equal(past.weight.records.length, 0);
});
test('UI view states, selected dates and accessible daily labels follow the calculation model', () => {
  assert.equal(insightView(null, goals(), range, today).status, 'loading');
  assert.equal(insightView([], null, range, today).status, 'loading');
  assert.equal(
    insightView(null, null, range, today, 'storage failure').status,
    'error',
  );
  assert.equal(insightView([{}], goals(), range, today).status, 'error');
  assert.equal(insightView([], goals(), range, today).status, 'ready');
  const data = build(day());
  const label = dayNutrientLabel(data.days.at(-2), 'calories');
  assert.match(label, /2026-10-29/);
  assert.match(label, /1000 kcal/);
  assert.match(label, /Eligible recorded day/);
  assert.match(label, /Target 1000 kcal/);
  assert.equal(
    selectedInsightDate('2026-10-29', rollingRange(today, 30)),
    '2026-10-29',
  );
});
