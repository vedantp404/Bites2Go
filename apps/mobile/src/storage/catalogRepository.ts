import type { DiaryStorage } from './diaryRepository.ts';
import { foods } from '../data/foods.ts';
import type { Food } from '../domain/food.ts';

export const catalogKey = 'bites2go.catalog.v1';

export type CatalogMetadata = {
  version: 1;
  foodCount: number;
  categories: readonly string[];
  updatedAt: string;
};

export function createCatalogRepository(storage: DiaryStorage) {
  let queue: Promise<unknown> = Promise.resolve();
  function serialize<T>(work: () => Promise<T>): Promise<T> {
    const result = queue.then(work);
    queue = result.catch(() => undefined);
    return result;
  }

  async function getMetadata(): Promise<CatalogMetadata | null> {
    try {
      const raw = await storage.getItem(catalogKey);
      if (!raw) return null;
      const parsed = JSON.parse(raw);
      if (
        parsed &&
        parsed.version === 1 &&
        typeof parsed.foodCount === 'number' &&
        Array.isArray(parsed.categories) &&
        typeof parsed.updatedAt === 'string'
      ) {
        return parsed as CatalogMetadata;
      }
      return null;
    } catch {
      return null;
    }
  }

  async function initializeCatalog(
    builtins: readonly Food[] = foods,
  ): Promise<CatalogMetadata> {
    const existing = await getMetadata();
    const categories = Array.from(
      new Set(builtins.map((f) => f.category)),
    ).sort();

    // Idempotent: if metadata matches current builtin count, preserve existing
    if (existing && existing.foodCount === builtins.length) {
      return existing;
    }

    const metadata: CatalogMetadata = {
      version: 1,
      foodCount: builtins.length,
      categories,
      updatedAt: new Date().toISOString(),
    };

    try {
      await storage.setItem(catalogKey, JSON.stringify(metadata));
    } catch {
      throw new Error(
        'Could not persist catalogue metadata. Stored foods and user data remain intact.',
      );
    }

    return metadata;
  }

  return {
    getMetadata: () => serialize(getMetadata),
    initializeCatalog: (builtins?: readonly Food[]) =>
      serialize(() => initializeCatalog(builtins)),
  };
}
