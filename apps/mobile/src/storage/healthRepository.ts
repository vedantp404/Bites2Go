import { decodeHealth, validateHealth } from '../domain/health.ts';
import type { Health } from '../domain/health.ts';
import type { DiaryStorage } from './diaryRepository.ts';
export const healthKey = 'bites2go.health.v1';
// Initial additive migration: an absent key represents empty v1. Existing keys are never modified.
export function createHealthRepository(storage: DiaryStorage) {
  let queue: Promise<unknown> = Promise.resolve();
  function serialize<T>(work: () => Promise<T>) {
    const result = queue.then(work);
    queue = result.catch(() => undefined);
    return result;
  }
  async function read() {
    try {
      return decodeHealth(await storage.getItem(healthKey));
    } catch {
      throw Error(
        'Progress data could not be loaded. Stored data has not been cleared. Retry without clearing app data.',
      );
    }
  }
  return {
    load: () => serialize(read),
    save: (next: Health, original: Health) =>
      serialize(async () => {
        const valid = validateHealth(next);
        const expected = validateHealth(original);
        const stored = await read();
        if (JSON.stringify(valid) === JSON.stringify(stored)) return stored;
        if (JSON.stringify(stored) !== JSON.stringify(expected))
          throw Error(
            'Progress changed since this form opened. Go back and reload before editing.',
          );
        try {
          await storage.setItem(healthKey, JSON.stringify(valid));
        } catch {
          throw Error(
            'Could not confirm the save. Retry this same action, or go back and reload to check stored data.',
          );
        }
        return valid;
      }),
  };
}
