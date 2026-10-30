// Presentation-only image registry for decorative illustrations.
// Food search, detail rows, and diary entries use clean text-based layouts for high performance.

export const decorativeImageKeys = [
  'apple',
  'banana',
  'dosa',
  'carrot',
  'oats',
] as const;

export type DecorativeImageKey = (typeof decorativeImageKeys)[number];
export type FoodImageAsset = DecorativeImageKey;

export const availableImageAssets = decorativeImageKeys;

export const foodImageKeys: Readonly<Record<string, DecorativeImageKey>> = {
  apple: 'apple',
  banana: 'banana',
  dosa: 'dosa',
  carrot: 'carrot',
  oats: 'oats',
};

export function foodImageKey(
  target: { id?: string; imageKey?: string } | string | null | undefined,
  failed = false,
): DecorativeImageKey | null {
  if (!target || failed) return null;
  const key =
    typeof target === 'string' ? target : (target.imageKey ?? target.id);
  if (!key || typeof key !== 'string') return null;
  return Object.hasOwn(foodImageKeys, key) ? foodImageKeys[key] : null;
}

export function categoryIcon(category?: string): string {
  switch (category) {
    case 'Bread':
      return 'bread';
    case 'Dairy':
      return 'dairy';
    case 'Meat':
      return 'meat';
    case 'Fruit':
      return 'fruit';
    case 'Vegetables':
      return 'leaf';
    case 'Grains':
    case 'Pulses':
    case 'Curries':
    case 'Soups':
    case 'Salads':
    case 'Pasta':
      return 'bowl';
    case 'Beverages':
      return 'cup';
    case 'Snacks':
    case 'Sweets':
    case 'Fast Food':
    case 'Breakfast':
      return 'snack';
    default:
      return 'leaf';
  }
}
