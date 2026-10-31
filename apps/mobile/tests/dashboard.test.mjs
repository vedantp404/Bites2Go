import test from 'node:test';
import assert from 'node:assert/strict';
import {
  totals,
  progress,
  calculateNutrientProgress,
  calculateMacroDistribution,
} from '../src/domain/dashboard.ts';
import { diaryTotals, shiftDay } from '../src/domain/diary.ts';
import { lightTheme, darkTheme } from '../src/theme/tokens.ts';

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

test('invalid intake is rejected by totals and progress', () => {
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

test('calculateNutrientProgress: empty diary (0 consumed) with normal target', () => {
  const state = calculateNutrientProgress(0, 2000, false, 'kcal');
  assert.equal(state.consumed, 0);
  assert.equal(state.target, 2000);
  assert.equal(state.remaining, 2000);
  assert.equal(state.exceeded, 0);
  assert.equal(state.isExceeded, false);
  assert.equal(state.percent, 0);
  assert.equal(state.fill, 0);
  assert.equal(state.formattedPercent, '0%');
  assert.equal(state.isPartial, false);
  assert.equal(state.isTargetSet, true);
  assert.equal(state.statusText, '2000 kcal remaining');
});

test('calculateNutrientProgress: normal progress toward daily target', () => {
  const state = calculateNutrientProgress(1500, 2000, false, 'kcal');
  assert.equal(state.consumed, 1500);
  assert.equal(state.target, 2000);
  assert.equal(state.remaining, 500);
  assert.equal(state.exceeded, 0);
  assert.equal(state.isExceeded, false);
  assert.equal(state.percent, 75);
  assert.equal(state.fill, 75);
  assert.equal(state.formattedPercent, '75%');
  assert.equal(state.statusText, '500 kcal remaining');
});

test('calculateNutrientProgress: exact goal completion', () => {
  const state = calculateNutrientProgress(2000, 2000, false, 'kcal');
  assert.equal(state.consumed, 2000);
  assert.equal(state.remaining, 0);
  assert.equal(state.exceeded, 0);
  assert.equal(state.isExceeded, false);
  assert.equal(state.fill, 100);
  assert.equal(state.formattedPercent, '100%');
  assert.equal(state.statusText, '0 kcal remaining');
});

test('calculateNutrientProgress: exceeding target shows excess clearly and clamps fill to 100 without capping consumed', () => {
  const state = calculateNutrientProgress(2350, 2000, false, 'kcal');
  assert.equal(state.consumed, 2350); // Uncapped!
  assert.equal(state.target, 2000);
  assert.equal(state.remaining, 0); // Not negative!
  assert.equal(state.exceeded, 350);
  assert.equal(state.isExceeded, true);
  assert.equal(state.percent, 117.5);
  assert.equal(state.fill, 100); // Visual bar clamped to 100
  assert.equal(state.formattedPercent, '118%');
  assert.equal(state.statusText, '350 kcal exceeded');
});

test('calculateNutrientProgress: individual macronutrient exceeding while calories remain under target', () => {
  // Protein exceeded by 20.5g
  const proteinState = calculateNutrientProgress(120.5, 100, false, 'g');
  assert.equal(proteinState.consumed, 120.5);
  assert.equal(proteinState.isExceeded, true);
  assert.equal(proteinState.remaining, 0);
  assert.equal(proteinState.exceeded, 20.5);
  assert.equal(proteinState.statusText, '20.5 g exceeded');

  // Carbs remaining under target
  const carbsState = calculateNutrientProgress(150, 250, false, 'g');
  assert.equal(carbsState.isExceeded, false);
  assert.equal(carbsState.remaining, 100);
  assert.equal(carbsState.statusText, '100.0 g remaining');

  // Fat remaining under target
  const fatState = calculateNutrientProgress(45.2, 65, false, 'g');
  assert.equal(fatState.isExceeded, false);
  assert.equal(fatState.remaining, 19.8);
  assert.equal(fatState.statusText, '19.8 g remaining');

  // Overall calories under target
  const calorieState = calculateNutrientProgress(1500, 2000, false, 'kcal');
  assert.equal(calorieState.isExceeded, false);
  assert.equal(calorieState.remaining, 500);
});

test('calculateNutrientProgress: missing, unset, and zero targets handled gracefully', () => {
  // Null target
  const nullTarget = calculateNutrientProgress(500, null, false, 'kcal');
  assert.equal(nullTarget.target, null);
  assert.equal(nullTarget.isTargetSet, false);
  assert.equal(nullTarget.percent, null);
  assert.equal(nullTarget.fill, 0);
  assert.equal(nullTarget.remaining, null);
  assert.equal(nullTarget.statusText, 'Target not set');

  // Zero target (tracking disabled)
  const zeroTarget = calculateNutrientProgress(500, 0, false, 'kcal');
  assert.equal(zeroTarget.target, 0);
  assert.equal(zeroTarget.isTargetSet, false);
  assert.equal(zeroTarget.percent, null);
  assert.equal(zeroTarget.fill, 0);
  assert.equal(zeroTarget.remaining, null);
  assert.equal(zeroTarget.statusText, 'Tracking disabled');

  // Negative and non-finite targets
  for (const bad of [-10, NaN, Infinity]) {
    const badTarget = calculateNutrientProgress(500, bad, false, 'kcal');
    assert.equal(badTarget.isTargetSet, false);
    assert.equal(badTarget.percent, null);
  }
});

test('calculateNutrientProgress: partial/incomplete data displays safe fallback', () => {
  const partialState = calculateNutrientProgress(400, 2000, true, 'kcal');
  assert.equal(partialState.isPartial, true);
  assert.equal(partialState.remaining, null);
  assert.equal(partialState.percent, null);
  assert.equal(partialState.fill, 0);
  assert.equal(partialState.formattedPercent, '--');
  assert.equal(partialState.statusText, 'Incomplete data');
});

test('calculateMacroDistribution: calculates energy percentages accurately without division by zero', () => {
  // 100g Protein (400 kcal), 200g Carbs (800 kcal), 50g Fat (450 kcal)
  // Total macro calories: 400 + 800 + 450 = 1650 kcal
  // P: 400/1650 = 24.24% -> 24%
  // C: 800/1650 = 48.48% -> 48%
  // F: 450/1650 = 27.27% -> 27%
  const dist = calculateMacroDistribution(100, 200, 50);
  assert.equal(dist.proteinCalories, 400);
  assert.equal(dist.carbsCalories, 800);
  assert.equal(dist.fatCalories, 450);
  assert.equal(dist.proteinPct, 24);
  assert.equal(dist.carbsPct, 48);
  assert.equal(dist.fatPct, 27);

  // Empty macros (0g all)
  const emptyDist = calculateMacroDistribution(0, 0, 0);
  assert.deepEqual(emptyDist, {
    proteinCalories: 0,
    carbsCalories: 0,
    fatCalories: 0,
    proteinPct: 0,
    carbsPct: 0,
    fatPct: 0,
  });

  // Safe against negative or NaN inputs
  const safeDist = calculateMacroDistribution(-10, NaN, 20);
  assert.equal(safeDist.proteinCalories, 0);
  assert.equal(safeDist.carbsCalories, 0);
  assert.equal(safeDist.fatCalories, 180);
  assert.equal(safeDist.fatPct, 100);
});

test('diary entries: reactivity on add, edit, delete and date switching', () => {
  const day1 = '2026-10-30';
  const day2 = shiftDay(day1, 1);
  assert.equal(day2, '2026-10-31');

  // Initial empty state for day 1
  const entriesDay1 = [];
  assert.equal(diaryTotals(entriesDay1).values.calories, 0);

  // Add entry to day 1
  const entryA = {
    id: 1,
    date: day1,
    meal: 'breakfast',
    foodId: 'apple',
    servingId: '1-medium',
    quantity: 1,
    grams: 182,
    nutrients: {
      calories: 95,
      protein: 0.5,
      carbs: 25.1,
      fat: 0.3,
      fiber: 4.4,
      sugar: 19.0,
    },
    snapshot: {
      name: 'Apple',
      calories: 95,
      protein: 0.5,
      carbs: 25.1,
      fat: 0.3,
      fiber: 4.4,
      sugar: 19.0,
      source: 'USDA FDC 171688',
      status: 'verified',
    },
    createdAt: '2026-10-30T08:00:00Z',
  };
  entriesDay1.push(entryA);
  assert.equal(diaryTotals(entriesDay1).values.calories, 95);

  // Add second entry to day 1 (lunch)
  const entryB = {
    id: 2,
    date: day1,
    meal: 'lunch',
    foodId: 'egg-boiled',
    servingId: '1-large',
    quantity: 2,
    grams: 100,
    nutrients: {
      calories: 155,
      protein: 12.6,
      carbs: 1.1,
      fat: 10.6,
      fiber: null,
      sugar: 1.1,
    },
    snapshot: {
      name: 'Hard Boiled Egg',
      calories: 155,
      protein: 12.6,
      carbs: 1.1,
      fat: 10.6,
      fiber: null,
      sugar: 1.1,
      source: 'USDA FDC 173424',
      status: 'verified',
    },
    createdAt: '2026-10-30T12:30:00Z',
  };
  entriesDay1.push(entryB);
  const updatedTotal = diaryTotals(entriesDay1);
  assert.equal(updatedTotal.values.calories, 250);
  assert.equal(updatedTotal.values.protein, 13.1);

  // Edit quantity of entry B (double portion)
  const editedEntryB = {
    ...entryB,
    quantity: 4,
    grams: 200,
    nutrients: {
      calories: 310,
      protein: 25.2,
      carbs: 2.2,
      fat: 21.2,
      fiber: null,
      sugar: 2.2,
    },
  };
  const entriesAfterEdit = [entryA, editedEntryB];
  const editedTotal = diaryTotals(entriesAfterEdit);
  assert.equal(editedTotal.values.calories, 405);
  assert.equal(editedTotal.values.protein, 25.7);

  // Delete entry A
  const entriesAfterDelete = [editedEntryB];
  const deleteTotal = diaryTotals(entriesAfterDelete);
  assert.equal(deleteTotal.values.calories, 310);
  assert.equal(deleteTotal.values.protein, 25.2);

  // Day 2 remains separate and empty
  const entriesDay2 = [];
  assert.equal(diaryTotals(entriesDay2).values.calories, 0);
});

test('theme compatibility: colors for progress and nutrition indicators are distinct and defined', () => {
  for (const theme of [lightTheme, darkTheme]) {
    assert.ok(theme.colors.primary, 'primary color exists');
    assert.ok(theme.colors.carbs, 'carbs color exists');
    assert.ok(theme.colors.fat, 'fat color exists');
    assert.ok(theme.colors.warning, 'warning color exists');
    assert.ok(theme.colors.success, 'success color exists');
    assert.ok(theme.colors.accent, 'accent background exists');
    assert.ok(theme.colors.surface, 'surface color exists');
    assert.ok(theme.colors.text, 'text color exists');
    assert.ok(theme.colors.muted, 'muted color exists');

    // Ensure distinct colors between macronutrients
    assert.notEqual(theme.colors.primary, theme.colors.carbs);
    assert.notEqual(theme.colors.carbs, theme.colors.fat);
    assert.notEqual(theme.colors.primary, theme.colors.fat);
  }
});
