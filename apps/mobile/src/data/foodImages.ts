// Presentation-only registry. Food and diary schemas remain unchanged.
export const foodImageKeys: Readonly<Record<string, 'apple' | 'banana'>> = {
  apple: 'apple',
  banana: 'banana',
};
export function foodImageKey(foodId: string | null, failed = false) {
  return foodId === null || failed || !Object.hasOwn(foodImageKeys, foodId)
    ? null
    : foodImageKeys[foodId];
}
