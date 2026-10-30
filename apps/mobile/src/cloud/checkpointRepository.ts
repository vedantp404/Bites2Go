import { validateSyncState, same } from './diarySync.ts';
import type { SyncState } from './diarySync.ts';
import type { DiaryStorage } from '../storage/diaryRepository.ts';
export const syncKey = 'bites2go.sync.diary.v1';
// Not mounted by the app until authenticated transport and consent UI pass live tests.
export function createCheckpointRepository(storage: DiaryStorage) {
  let queue: Promise<unknown> = Promise.resolve();
  function serial<T>(work: () => Promise<T>): Promise<T> {
    const result = queue.then(work);
    queue = result.catch(() => undefined);
    return result;
  }
  async function read(): Promise<SyncState | null> {
    try {
      const raw = await storage.getItem(syncKey);
      return raw === null ? null : validateSyncState(JSON.parse(raw));
    } catch {
      throw Error(
        'Cannot load sync checkpoint. Existing data was not cleared.',
      );
    }
  }
  return {
    load: () => serial(read),
    save: (next: SyncState, original: SyncState | null) =>
      serial(async () => {
        validateSyncState(next);
        if (original) validateSyncState(original);
        const current = await read();
        if (current && current.ownerId !== next.ownerId)
          throw Error('Account binding cannot be reassigned.');
        if (same(current, next)) return current;
        if (!same(current, original))
          throw Error('Sync checkpoint changed. Reload before retrying.');
        const nextRows = new Map(next.base.map((row) => [row.id, row]));
        for (const previous of current?.base ?? []) {
          const row = nextRows.get(previous.id);
          if (
            !row ||
            row.revision < previous.revision ||
            (row.revision === previous.revision && !same(row, previous))
          )
            throw Error(
              'Acknowledged sync revisions cannot be removed or rewound.',
            );
        }
        try {
          await storage.setItem(syncKey, JSON.stringify(next));
        } catch {
          throw Error(
            'Could not confirm checkpoint save. Retry the same checkpoint.',
          );
        }
        return next;
      }),
  };
}
