import test from 'node:test';
import assert from 'node:assert/strict';
import { totals, progress } from '../src/domain/dashboard.ts';
test('totals aggregate meals and preserve empty diary zero', () => {
  assert.deepEqual(totals([]), { calories: 0, protein: 0, carbs: 0, fat: 0 });
  const meal = {
    name: 'Test',
    entries: [
      {
        name: 'Fixture',
        nutrients: { calories: 100, protein: 10, carbs: 12, fat: 3 },
      },
    ],
  };
  assert.deepEqual(totals([meal, meal]), {
    calories: 200,
    protein: 20,
    carbs: 24,
    fat: 6,
  });
});
test('progress retains over-target information while clamping the visual', () => {
  assert.deepEqual(progress(125, 100), {
    percent: 125,
    fill: 100,
    remaining: -25,
  });
  assert.deepEqual(progress(25, 100), { percent: 25, fill: 25, remaining: 75 });
  assert.deepEqual(progress(0, 100), { percent: 0, fill: 0, remaining: 100 });
});
test('unset and invalid targets do not divide by zero', () => {
  for (const value of [0, -1, NaN, Infinity])
    assert.deepEqual(progress(10, value), {
      percent: null,
      fill: 0,
      remaining: null,
    });
});
test('invalid intake is rejected', () => {
  for (const value of [-1, NaN, Infinity])
    assert.throws(() => progress(value, 100));
  assert.throws(() =>
    totals([
      {
        name: 'test',
        entries: [
          {
            name: 'bad',
            nutrients: { calories: NaN, protein: 0, carbs: 0, fat: 0 },
          },
        ],
      },
    ]),
  );
});
