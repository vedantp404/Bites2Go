import {
  createContext,
  useContext,
  useEffect,
  useSyncExternalStore,
  type PropsWithChildren,
} from 'react';
import { useColorScheme } from 'react-native';
import Storage from 'expo-sqlite/kv-store';
import { SplashScreen } from 'expo-router';
import { createAppearanceStore, effectiveTheme } from './appearance';
import { lightTheme, darkTheme } from './tokens';
const store = createAppearanceStore(Storage);
const ThemeContext = createContext<ReturnType<typeof useAppearance> | null>(
  null,
);
void SplashScreen.preventAutoHideAsync().catch((error) =>
  console.warn('Splash screen hold unavailable', error),
);
function useAppearance() {
  const state = useSyncExternalStore(
    store.subscribe,
    store.getSnapshot,
    store.getSnapshot,
  );
  const system = useColorScheme();
  const mode = effectiveTheme(state.preference, system);
  return {
    ...state,
    mode,
    theme: mode === 'dark' ? darkTheme : lightTheme,
    select: store.select,
  };
}
export function ThemeProvider({ children }: PropsWithChildren) {
  const value = useAppearance();
  useEffect(() => {
    void store.load();
  }, []);
  return (
    <ThemeContext.Provider value={value}>
      {value.ready ? children : null}
    </ThemeContext.Provider>
  );
}
export function useTheme() {
  const value = useContext(ThemeContext);
  if (!value) throw new Error('ThemeProvider is required');
  return value;
}
