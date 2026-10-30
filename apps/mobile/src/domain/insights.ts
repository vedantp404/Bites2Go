import { assertEntry, diaryTotals, shiftDay, validDateKey } from './diary.ts';
import type { DiaryEntry } from './diary.ts';
import { indexDiaryDates } from './calendar.ts';
import { meals, foodNutrientKeys, formatNutrient } from './food.ts';
import type { FoodNutrients } from './food.ts';
import {
  targetsForDate,
  dateOrdinal,
  validateHealth,
  weightProgress,
} from './health.ts';
import type { Health } from './health.ts';
export type Nutrient = keyof FoodNutrients;
export type InsightRange = { start: string; end: string };
export const nutrientNames: Record<Nutrient, string> = {
  calories: 'Calories',
  protein: 'Protein',
  carbs: 'Carbohydrates',
  fat: 'Fat',
  fiber: 'Fiber',
};
export const unitFor = (key: Nutrient) => (key === 'calories' ? 'kcal' : 'g');
export const eligibilityNote =
  'Period calculations include only past days with entries in Breakfast, Lunch, Snacks and Dinner, and no unknown values for that nutrient. This is a logging proxy, not proof of a complete day; intentionally skipped meals are excluded. Today is still in progress.';
export function rollingRange(today: string, count: 7 | 30): InsightRange {
  if (!validDateKey(today)) throw Error('Invalid local date.');
  const available = dateOrdinal(today) - dateOrdinal('1900-01-01');
  return {
    start: shiftDay(today, -Math.min(count - 1, available)),
    end: today,
  };
}
export function rangeDates(range: InsightRange, today: string): string[] {
  if (
    !validDateKey(today) ||
    !validDateKey(range.start) ||
    !validDateKey(range.end) ||
    range.start > range.end ||
    range.end > today
  )
    throw Error(
      'Choose real local dates, with start before end and no future dates.',
    );
  const length = dateOrdinal(range.end) - dateOrdinal(range.start) + 1;
  if (length > 92) throw Error('Choose a range of at most 92 days.');
  return Array.from({ length }, (_, index) => shiftDay(range.start, index));
}
export function selectedInsightDate(selected: string, range: InsightRange) {
  return validDateKey(selected) &&
    selected >= range.start &&
    selected <= range.end
    ? selected
    : range.end;
}
export function buildInsights(
  entries: DiaryEntry[],
  rawHealth: Health,
  range: InsightRange,
  today: string,
) {
  const dates = rangeDates(range, today),
    health = validateHealth(rawHealth);
  const ids = new Set<string>();
  for (const entry of entries) {
    assertEntry(entry);
    if (ids.has(entry.id))
      throw Error(
        'Duplicate diary identity. Reload saved data before viewing insights.',
      );
    ids.add(entry.id);
  }
  const byDate = indexDiaryDates(entries);
  const days = dates.map((date) => {
    const records = byDate.get(date) ?? [];
    const totals = diaryTotals(records);
    const mealCount = new Set(records.map((entry) => entry.meal)).size;
    const targets = { ...targetsForDate(health, date), fiber: null };
    const nutrients = Object.fromEntries(
      foodNutrientKeys.map((key) => {
        const known =
          records.length > 0 &&
          !totals.partial[key] &&
          totals.values[key] !== null;
        return [
          key,
          {
            value: records.length ? totals.values[key] : null,
            partial: records.length > 0 && totals.partial[key],
            target: targets[key],
            eligible: date < today && mealCount === meals.length && known,
          },
        ];
      }),
    ) as Record<
      Nutrient,
      {
        value: number | null;
        partial: boolean;
        target: number | null;
        eligible: boolean;
      }
    >;
    return {
      date,
      entryCount: records.length,
      mealCount,
      inProgress: date === today,
      nutrients,
    };
  });
  const stats = Object.fromEntries(
    foodNutrientKeys.map((key) => {
      const eligible = days.filter((day) => day.nutrients[key].eligible);
      const targeted = eligible.filter(
        (day) => (day.nutrients[key].target ?? 0) > 0,
      );
      const mean = (values: number[]) =>
        values.length
          ? values.reduce((sum, value) => sum + value / values.length, 0)
          : null;
      let below = 0,
        within = 0,
        above = 0;
      for (const day of targeted) {
        const ratio = day.nutrients[key].value! / day.nutrients[key].target!;
        if (ratio < 0.9 - 1e-12) below++;
        else if (ratio > 1.1 + 1e-12) above++;
        else within++;
      }
      return [
        key,
        {
          eligible: eligible.length,
          average: mean(eligible.map((day) => day.nutrients[key].value!)),
          unknownDays: days.filter((day) => day.nutrients[key].partial).length,
          goalDays: targeted.length,
          within,
          below,
          above,
          percent: targeted.length ? (within / targeted.length) * 100 : null,
          pairedAverage: mean(targeted.map((day) => day.nutrients[key].value!)),
          averageTarget: mean(
            targeted.map((day) => day.nutrients[key].target!),
          ),
        },
      ];
    }),
  ) as Record<
    Nutrient,
    {
      eligible: number;
      average: number | null;
      unknownDays: number;
      goalDays: number;
      within: number;
      below: number;
      above: number;
      percent: number | null;
      pairedAverage: number | null;
      averageTarget: number | null;
    }
  >;
  const weights = health.weights.filter(
    (w) => w.date >= range.start && w.date <= range.end,
  );
  const first = weights[0],
    latest = weights.at(-1);
  const goal =
    health.weightGoal && latest && health.weightGoal.setDate <= latest.date
      ? health.weightGoal
      : null;
  const weight = {
    records: weights,
    latest,
    change: weights.length > 1 ? latest!.kg - first.kg : null,
    goal,
    progress: weightProgress(latest?.kg ?? null, goal, latest?.date),
  };
  const loggedDays = days.filter((day) => day.entryCount > 0).length;
  const observations = [
    `${range.start} to ${range.end}: ${loggedDays} of ${days.length} days have entries. ${days.length - loggedDays} days have no entries; this does not mean zero intake.`,
  ];
  if (stats.protein.goalDays)
    observations.push(
      `${stats.protein.below} of ${stats.protein.goalDays} eligible protein-target days recorded less than 90% of that day's target. Only recorded intake is compared.`,
    );
  else
    observations.push(
      'There are no eligible protein-target days in this period. Review meal coverage, unknown nutrients and your saved targets.',
    );
  if (stats.calories.goalDays)
    observations.push(
      `Across ${stats.calories.goalDays} eligible calorie-target days, average recorded calories were ${formatNutrient(stats.calories.pairedAverage, 'kcal')} and average applicable target was ${formatNutrient(stats.calories.averageTarget, 'kcal')}.`,
    );
  else
    observations.push(
      'More eligible calorie-target days are needed for a period comparison. Logging completeness cannot be confirmed by this app.',
    );
  return {
    range,
    days,
    stats,
    weight,
    loggedDays,
    noEntryDays: days.length - loggedDays,
    limitedMealDays: days.filter(
      (day) => day.entryCount > 0 && day.mealCount < meals.length,
    ).length,
    observations,
  };
}
export type Insights = ReturnType<typeof buildInsights>;
export function dayNutrientLabel(day: Insights['days'][number], key: Nutrient) {
  const nutrient = day.nutrients[key];
  const status = !day.entryCount
    ? 'No entries; intake unknown'
    : nutrient.partial
      ? 'Unknown nutrients; known subtotal only'
      : day.inProgress
        ? 'Today in progress'
        : day.mealCount < meals.length
          ? `${day.mealCount} of 4 meal sections recorded`
          : 'Eligible recorded day';
  return `${day.date}: ${nutrientNames[key]} ${formatNutrient(nutrient.value, unitFor(key))}. ${status}. Target ${nutrient.target === null ? 'not set' : nutrient.target === 0 ? 'disabled' : formatNutrient(nutrient.target, unitFor(key))}.`;
}
export function insightView(
  entries: DiaryEntry[] | null,
  health: Health | null,
  range: InsightRange,
  today: string,
  error = '',
):
  | { status: 'loading' | 'error'; message: string }
  | { status: 'ready'; data: Insights } {
  if (error)
    return {
      status: 'error',
      message:
        'Saved data could not be loaded. Retry without clearing app data.',
    };
  if (entries === null || health === null)
    return {
      status: 'loading',
      message: 'Loading saved diary and historical targets...',
    };
  try {
    return {
      status: 'ready',
      data: buildInsights(entries, health, range, today),
    };
  } catch {
    return {
      status: 'error',
      message:
        'Insights could not be calculated. Check the date range and retry loading saved data; no records were changed.',
    };
  }
}
