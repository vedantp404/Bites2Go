import { assertEntry, decodeDiary, validDateKey } from '../domain/diary.ts';
import type { DiaryEntry } from '../domain/diary.ts';
export interface DiaryStorage {
  getItem(key: string): Promise<string | null>;
  setItem(key: string, value: string): Promise<void>;
}
// shortcut: a single document suits a small diary; migrate to indexed rows before large histories or sync.
export const diaryKey = 'bites2go.diary.v1';
export function createDiaryRepository(storage: DiaryStorage) {
  let queue: Promise<unknown> = Promise.resolve();
  function serialize<T>(work: () => Promise<T>): Promise<T> {
    const result = queue.then(work);
    queue = result.catch(() => undefined);
    return result;
  }
  async function read() {
    try {
      return decodeDiary(await storage.getItem(diaryKey));
    } catch {
      throw new Error(
        'Cannot read the diary. Stored data was not cleared. Retry; if this persists, keep app data intact for recovery.',
      );
    }
  }
  async function write(entries: DiaryEntry[]) {
    // Validate the complete next document before replacing the single SQLite value.
    decodeDiary(JSON.stringify({ version: 1, entries }));
    try {
      await storage.setItem(diaryKey, JSON.stringify({ version: 1, entries }));
    } catch {
      throw new Error(
        'Could not confirm the diary write. Retry the same action; do not clear app data.',
      );
    }
    return entries;
  }
  return {
    loadAll: () => serialize(read),
    loadDate: (date: string) =>
      serialize(async () => {
        if (!validDateKey(date)) throw new Error('Invalid date.');
        return (await read()).filter((e) => e.date === date);
      }),
    save: (entry: DiaryEntry) =>
      serialize(async () => {
        assertEntry(entry);
        const entries = await read();
        const existing = entries.find((e) => e.id === entry.id);
        if (existing) {
          if (JSON.stringify(existing) !== JSON.stringify(entry))
            throw new Error(
              'This entry ID is already saved with different details. Reload the diary.',
            );
          return entries;
        }
        return write([...entries, entry]);
      }),
    update: (entry: DiaryEntry, original: DiaryEntry) =>
      serialize(async () => {
        assertEntry(entry);
        const entries = await read();
        const existing = entries.find((e) => e.id === entry.id);
        if (!existing)
          throw new Error('Entry no longer exists. Reload the diary.');
        if (JSON.stringify(existing) === JSON.stringify(entry)) return entries;
        if (
          JSON.stringify(existing) !== JSON.stringify(original) ||
          entry.date !== original.date ||
          entry.createdAt !== original.createdAt ||
          entry.foodId !== original.foodId ||
          JSON.stringify(entry.reference) !== JSON.stringify(original.reference)
        )
          throw new Error('Entry changed. Reload it before editing.');
        return write(entries.map((e) => (e.id === entry.id ? entry : e)));
      }),
    remove: (original: DiaryEntry) =>
      serialize(async () => {
        const entries = await read();
        const existing = entries.find((e) => e.id === original.id);
        if (!existing) return entries;
        if (JSON.stringify(existing) !== JSON.stringify(original))
          throw new Error('Entry changed. Reload it before deleting.');
        return write(entries.filter((e) => e.id !== original.id));
      }),
  };
}
export type DiaryRepository = ReturnType<typeof createDiaryRepository>;
