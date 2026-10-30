import { decodeLibrary, validateLibrary } from '../domain/library.ts';
import type { Library } from '../domain/library.ts';
import type { DiaryStorage } from './diaryRepository.ts';
export const libraryKey = 'bites2go.library.v1';
// Initial additive migration: an absent key represents empty v1. Existing keys are never modified.
export function createLibraryRepository(storage: DiaryStorage) {
  let queue: Promise<unknown> = Promise.resolve();
  function serialize<T>(work: () => Promise<T>) {
    const result = queue.then(work);
    queue = result.catch(() => undefined);
    return result;
  }
  async function read() {
    try {
      return decodeLibrary(await storage.getItem(libraryKey));
    } catch {
      throw Error(
        'Food library data could not be loaded. Stored data has not been cleared. Retry without clearing app data.',
      );
    }
  }
  return {
    load: () => serialize(read),
    save: (next: Library, original: Library) =>
      serialize(async () => {
        const valid = validateLibrary(next);
        const expected = validateLibrary(original);
        const stored = await read();
        if (JSON.stringify(valid) === JSON.stringify(stored)) return stored;
        if (JSON.stringify(stored) !== JSON.stringify(expected))
          throw Error(
            'Food library changed since this form opened. Go back and reload before editing.',
          );
        try {
          await storage.setItem(libraryKey, JSON.stringify(valid));
        } catch {
          throw Error(
            'Could not confirm the save. Retry this same action, or go back and reload to check stored data.',
          );
        }
        return valid;
      }),
  };
}
