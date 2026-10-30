import {
  createContext,
  useContext,
  useEffect,
  useRef,
  useState,
  type PropsWithChildren,
} from 'react';
import Storage from 'expo-sqlite/kv-store';
import { createLibraryRepository } from '../storage/libraryRepository';
import type { Library } from '../domain/library';
const repository = createLibraryRepository({
  getItem: (key) => Storage.getItemAsync(key),
  setItem: (key, value) => Storage.setItemAsync(key, value),
});
type State = {
  data: Library | null;
  error: string;
  reload: () => void;
  save: (next: Library, original: Library) => Promise<void>;
};
const Context = createContext<State | null>(null);
export function LibraryProvider({ children }: PropsWithChildren) {
  const [data, setData] = useState<Library | null>(null);
  const [error, setError] = useState('');
  const revision = useRef(0);
  const reload = () => {
    const request = ++revision.current;
    void repository
      .load()
      .then((value) => {
        if (request === revision.current) {
          setData(value);
          setError('');
        }
      })
      .catch((e) => {
        if (request === revision.current) {
          setData(null);
          setError(e.message);
        }
      });
  };
  useEffect(() => {
    reload();
  }, []);
  const save = async (next: Library, original: Library) => {
    const result = await repository.save(next, original);
    revision.current++;
    setData(result);
    setError('');
  };
  return (
    <Context.Provider value={{ data, error, reload, save }}>
      {children}
    </Context.Provider>
  );
}
export function useLibrary() {
  const context = useContext(Context);
  if (!context) throw Error('LibraryProvider required');
  return context;
}
