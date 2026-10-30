import type { Nutrients, PreviewMeal } from '../domain/dashboard';
// Synthetic UI fixture, not authoritative food composition or a user's diary.
export const previewTargets: Nutrients = {
  calories: 2200,
  protein: 120,
  carbs: 275,
  fat: 70,
};
export const previewMeals: PreviewMeal[] = [
  {
    name: 'Breakfast',
    entries: [
      {
        name: 'Example breakfast',
        nutrients: { calories: 420, protein: 24, carbs: 54, fat: 12 },
      },
    ],
  },
  {
    name: 'Lunch',
    entries: [
      {
        name: 'Example lunch',
        nutrients: { calories: 610, protein: 32, carbs: 75, fat: 20 },
      },
    ],
  },
  { name: 'Snacks', entries: [] },
  { name: 'Dinner', entries: [] },
];
