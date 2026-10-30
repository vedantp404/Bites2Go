// Presentation-only image registry. Food and diary schemas remain unchanged.
import type { Food } from '../domain/food.ts';

export const availableImageAssets = [
  'almonds',
  'apple',
  'banana',
  'bread',
  'broccoli',
  'burger',
  'carrot',
  'chicken_breast',
  'chickpeas',
  'chocolate',
  'coffee',
  'curd',
  'dal',
  'dosa',
  'egg',
  'grapes',
  'idli',
  'mango',
  'milk',
  'oats',
  'orange',
  'paneer',
  'pasta',
  'pizza',
  'potato',
  'rice',
  'roti',
  'salmon',
  'samosa',
  'spinach',
  'strawberry',
  'tea',
  'tomato',
  'watermelon',
] as const;

export type FoodImageAsset = (typeof availableImageAssets)[number];

export const foodImageKeys: Readonly<Record<string, FoodImageAsset>> = {
  // Baseline items
  apple: 'apple',
  banana: 'banana',
  'rice-cooked': 'rice',
  'rice-raw': 'rice',
  roti: 'roti',
  moong: 'dal',
  chickpeas: 'chickpeas',
  milk: 'milk',
  curd: 'curd',
  almonds: 'almonds',
  oats: 'oats',
  paneer: 'paneer',
};

export function foodImageKey(
  foodOrId: string | Food | null | undefined,
  failed = false,
): FoodImageAsset | null {
  if (!foodOrId || failed) return null;

  if (typeof foodOrId === 'object') {
    if (
      foodOrId.imageKey &&
      availableImageAssets.includes(foodOrId.imageKey as FoodImageAsset)
    ) {
      return foodOrId.imageKey as FoodImageAsset;
    }
    return Object.hasOwn(foodImageKeys, foodOrId.id)
      ? foodImageKeys[foodOrId.id]
      : null;
  }

  return Object.hasOwn(foodImageKeys, foodOrId)
    ? foodImageKeys[foodOrId]
    : null;
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
