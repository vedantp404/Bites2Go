import { indexDiaryDates } from '../domain/calendar';
import {
  createContext,
  useContext,
  useEffect,
  useMemo,
  useRef,
  useState,
} from 'react';
import type { PropsWithChildren } from 'react';
import { AppState } from 'react-native';
import { diaryRepository } from '../storage/localDiary';
import type { DiaryEntry } from '../domain/diary';
import { localDateKey } from '../domain/diary';
type DiaryState = {
  entries: DiaryEntry[] | null;
  entriesByDate: ReadonlyMap<string, DiaryEntry[]> | null;
  error: string;
  reload: () => void;
  save: (entry: DiaryEntry) => Promise<void>;
  update: (entry: DiaryEntry, original: DiaryEntry) => Promise<void>;
  remove: (entry: DiaryEntry) => Promise<void>;
  message: string;
};
const Context = createContext<DiaryState | null>(null);
export function DiaryProvider({ children }: PropsWithChildren) {
  const [entries, setEntries] = useState<DiaryEntry[] | null>(null);
  const [error, setError] = useState('');
  const [message, setMessage] = useState('');
  const revision = useRef(0);
  const entriesByDate = useMemo(
    () => (entries === null ? null : indexDiaryDates(entries)),
    [entries],
  );
  const reload = () => {
    const current = ++revision.current;
    void diaryRepository
      .loadAll()
      .then((data) => {
        if (current === revision.current) {
          setEntries(data);
          setError('');
        }
      })
      .catch(() => {
        if (current === revision.current) {
          setEntries(null);
          setError(
            'Diary could not be loaded. Data has not been cleared. Retry loading; do not clear app data.',
          );
        }
      });
  };
  useEffect(() => {
    reload();
  }, []);
  async function commit(operation: Promise<DiaryEntry[]>, notice: string) {
    const next = await operation;
    revision.current++;
    setEntries(next);
    setError('');
    setMessage(notice);
  }
  return (
    <Context.Provider
      value={{
        entries,
        entriesByDate,
        error,
        reload,
        message,
        save: (entry) =>
          commit(diaryRepository.save(entry), 'Food saved on this device.'),
        update: (entry, original) =>
          commit(
            diaryRepository.update(entry, original),
            'Portion updated on this device.',
          ),
        remove: (entry) =>
          commit(
            diaryRepository.remove(entry),
            'Entry deleted from this device.',
          ),
      }}
    >
      {children}
    </Context.Provider>
  );
}
export function useDiary() {
  const value = useContext(Context);
  if (!value) throw new Error('Diary provider missing.');
  return value;
}
export function useToday() {
  const [today, setToday] = useState(localDateKey);
  useEffect(() => {
    const update = () => setToday(localDateKey());
    const timer = setInterval(update, 30000);
    const sub = AppState.addEventListener('change', (state) => {
      if (state === 'active') update();
    });
    return () => {
      clearInterval(timer);
      sub.remove();
    };
  }, []);
  return today;
}
