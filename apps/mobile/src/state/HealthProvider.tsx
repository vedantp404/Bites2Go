import {
  createContext,
  useContext,
  useEffect,
  useRef,
  useState,
  type PropsWithChildren,
} from 'react';
import Storage from 'expo-sqlite/kv-store';
import { createHealthRepository } from '../storage/healthRepository';
import type { Health } from '../domain/health';
const repository = createHealthRepository({
  getItem: (key) => Storage.getItemAsync(key),
  setItem: (key, value) => Storage.setItemAsync(key, value),
});
type State = {
  data: Health | null;
  error: string;
  reload: () => void;
  save: (next: Health, original: Health) => Promise<void>;
};
const Context = createContext<State | null>(null);
export function HealthProvider({ children }: PropsWithChildren) {
  const [data, setData] = useState<Health | null>(null);
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
  const save = async (next: Health, original: Health) => {
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
export function useHealth() {
  const context = useContext(Context);
  if (!context) throw Error('HealthProvider required');
  return context;
}
