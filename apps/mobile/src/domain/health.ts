import { validDateKey, localDateKey } from './diary.ts';
import { progress } from './dashboard.ts';
export const nutrientKeys = ['calories', 'protein', 'carbs', 'fat'] as const;
export type NutrientKey = (typeof nutrientKeys)[number];
export type Targets = Record<NutrientKey, number | null>;
export const unsetTargets: Targets = {
  calories: null,
  protein: null,
  carbs: null,
  fat: null,
};
export const limits = { calories: 10000, protein: 500, carbs: 1500, fat: 500 };
export type Weight = { id: string; date: string; kg: number; unit: 'kg' };
export type NutritionGoal = { date: string; targets: Targets };
export type WeightGoal = {
  targetKg: number;
  setDate: string;
  start: { kg: number; date: string } | null;
};
export type Health = {
  version: 1;
  weights: Weight[];
  nutritionGoals: NutritionGoal[];
  heightCm: number | null;
  weightGoal: WeightGoal | null;
};
export const emptyHealth = (): Health => ({
  version: 1,
  weights: [],
  nutritionGoals: [],
  heightCm: null,
  weightGoal: null,
});
export const inRange = (
  value: unknown,
  min: number,
  max: number,
): value is number =>
  typeof value === 'number' &&
  Number.isFinite(value) &&
  value >= min &&
  value <= max;
export function inputNumber(
  text: string,
  min: number,
  max: number,
  optional = false,
): number | null {
  if (!text.trim() && optional) return null;
  if (!/^\d+(?:\.\d+)?$/.test(text.trim()))
    throw Error('Use a plain positive number, such as 70 or 70.5.');
  const value = Number(text.trim());
  if (!inRange(value, min, max))
    throw Error(`Enter a value from ${min} to ${max}.`);
  return value;
}
export function assertRecordDate(date: string, today = localDateKey()) {
  if (!validDateKey(date) || date > today)
    throw Error(
      'Use a real date in YYYY-MM-DD format, from 1900-01-01 through today.',
    );
}
export function decodeHealth(raw: string | null): Health {
  if (raw === null) return emptyHealth();
  return validateHealth(JSON.parse(raw));
}
export function validateHealth(data: Health): Health {
  if (
    !data ||
    data.version !== 1 ||
    !Array.isArray(data.weights) ||
    !Array.isArray(data.nutritionGoals) ||
    !(data.heightCm === null || inRange(data.heightCm, 100, 250))
  )
    throw Error('Unsupported or invalid progress data.');
  const ids = new Set();
  const dates = new Set();
  const weights: Weight[] = data.weights.map((w: Weight) => {
    if (
      !w ||
      typeof w.id !== 'string' ||
      !w.id ||
      w.id.length > 100 ||
      !validDateKey(w.date) ||
      !inRange(w.kg, 20, 500) ||
      w.unit !== 'kg' ||
      ids.has(w.id) ||
      dates.has(w.date)
    )
      throw Error('Invalid or conflicting weight records.');
    ids.add(w.id);
    dates.add(w.date);
    return { id: w.id, date: w.date, kg: w.kg, unit: 'kg' };
  });
  const goalDates = new Set();
  const nutritionGoals: NutritionGoal[] = data.nutritionGoals.map(
    (g: NutritionGoal) => {
      if (
        !g ||
        !validDateKey(g.date) ||
        goalDates.has(g.date) ||
        !g.targets ||
        nutrientKeys.some(
          (k) =>
            !(
              g.targets[k] === null ||
              g.targets[k] === 0 ||
              inRange(g.targets[k], k === 'calories' ? 1 : 0.1, limits[k])
            ),
        )
      )
        throw Error(
          'Targets must be blank or zero, or 1–10000 kcal, 0.1–500 g protein/fat, and 0.1–1500 g carbohydrates.',
        );
      goalDates.add(g.date);
      return {
        date: g.date,
        targets: Object.fromEntries(
          nutrientKeys.map((k) => [k, g.targets[k]]),
        ) as Targets,
      };
    },
  );
  const goal = data.weightGoal;
  if (
    goal !== null &&
    (!goal ||
      !validDateKey(goal.setDate) ||
      !inRange(goal.targetKg, 20, 500) ||
      !(
        goal.start === null ||
        (goal.start &&
          validDateKey(goal.start.date) &&
          inRange(goal.start.kg, 20, 500))
      ))
  )
    throw Error('Invalid weight goal.');
  return {
    version: 1,
    weights: weights.sort((a, b) => a.date.localeCompare(b.date)),
    nutritionGoals: nutritionGoals.sort((a, b) => a.date.localeCompare(b.date)),
    heightCm: data.heightCm,
    weightGoal:
      goal === null
        ? null
        : {
            targetKg: goal.targetKg,
            setDate: goal.setDate,
            start:
              goal.start === null
                ? null
                : { kg: goal.start.kg, date: goal.start.date },
          },
  };
}
export function recordWeight(
  data: Health,
  weight: Weight,
  editing = false,
  today = localDateKey(),
): Health {
  assertRecordDate(weight.date, today);
  const existing = data.weights.find((w) => w.id === weight.id);
  if (editing && !existing)
    throw Error('Measurement no longer exists. Reload progress.');
  if (
    !editing &&
    existing &&
    JSON.stringify(existing) !== JSON.stringify(weight)
  )
    throw Error('Measurement ID already exists.');
  if (data.weights.some((w) => w.date === weight.date && w.id !== weight.id))
    throw Error(
      'A measurement already exists on this date. Edit that record instead.',
    );
  const weights = [...data.weights.filter((w) => w.id !== weight.id), weight];
  const next = { ...data, weights };
  // A goal set before the first measurement starts at the first subsequently recorded date.
  if (
    next.weightGoal &&
    !next.weightGoal.start &&
    weight.date >= next.weightGoal.setDate
  )
    next.weightGoal = {
      ...next.weightGoal,
      start: { kg: weight.kg, date: weight.date },
    };
  return validateHealth(next);
}
export function removeWeight(data: Health, id: string): Health {
  return { ...data, weights: data.weights.filter((w) => w.id !== id) };
}
export function targetsForDate(data: Health, date: string): Targets {
  return (
    [...data.nutritionGoals].reverse().find((g) => g.date <= date)?.targets ??
    unsetTargets
  );
}
export function saveSettings(
  data: Health,
  date: string,
  targets: Targets,
  heightCm: number | null,
  targetKg: number | null,
  today = localDateKey(),
): Health {
  assertRecordDate(date, today);
  const latest = data.weights.filter((w) => w.date <= date).at(-1);
  const weightGoal =
    targetKg === null
      ? null
      : data.weightGoal?.targetKg === targetKg
        ? data.weightGoal
        : {
            targetKg,
            setDate: date,
            start: latest ? { kg: latest.kg, date: latest.date } : null,
          };
  return validateHealth({
    ...data,
    heightCm,
    weightGoal,
    nutritionGoals: [
      ...data.nutritionGoals.filter((g) => g.date !== date),
      { date, targets },
    ],
  });
}
export function nutrientProgress(
  consumed: number | null,
  target: number | null,
  partial = false,
) {
  if (consumed === null || partial)
    return { percent: null, fill: 0, remaining: null };
  return progress(consumed, target ?? 0);
}
export function bmi(heightCm: number | null, weightKg: number | null) {
  return inRange(heightCm, 100, 250) && inRange(weightKg, 20, 500)
    ? weightKg / (heightCm / 100) ** 2
    : null;
}
export function weightProgress(
  current: number | null,
  goal: WeightGoal | null,
  currentDate?: string,
) {
  if (!inRange(current, 20, 500) || !goal || !inRange(goal.targetKg, 20, 500))
    return { difference: null, percent: null, fill: 0 };
  const difference = goal.targetKg - current;
  const start = goal.start?.kg;
  const percent =
    start === undefined ||
    !inRange(start, 20, 500) ||
    start === goal.targetKg ||
    (currentDate !== undefined &&
      goal.start !== null &&
      currentDate < goal.start.date)
      ? null
      : ((current - start) / (goal.targetKg - start)) * 100;
  return {
    difference,
    percent,
    fill: percent === null ? 0 : Math.min(100, Math.max(0, percent)),
  };
}
// UTC is used only as an ordinal for already validated local date keys, never to choose a measurement date.
export const dateOrdinal = (date: string) => {
  if (!validDateKey(date)) throw Error('Invalid chart date');
  return Date.parse(date + 'T12:00:00Z') / 86400000;
};
export function weightPoints(weights: Weight[]) {
  const ordered = [...weights].sort((a, b) => a.date.localeCompare(b.date));
  if (!ordered.length) return [];
  const start = dateOrdinal(ordered[0].date),
    end = dateOrdinal(ordered.at(-1)!.date);
  const low = Math.min(...ordered.map((w) => w.kg)),
    high = Math.max(...ordered.map((w) => w.kg));
  return ordered.map((w) => ({
    ...w,
    x: end === start ? 0.5 : (dateOrdinal(w.date) - start) / (end - start),
    y: high === low ? 0.5 : (w.kg - low) / (high - low),
  }));
}
