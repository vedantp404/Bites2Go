export type Preference = 'light' | 'dark' | 'system';
export const preferenceKey = 'bites2go.appearance.v1';
export function isPreference(value: unknown): value is Preference {
  return value === 'light' || value === 'dark' || value === 'system';
}
export function effectiveTheme(
  preference: Preference,
  system: string | null | undefined,
): 'light' | 'dark' {
  return preference === 'system'
    ? system === 'dark'
      ? 'dark'
      : 'light'
    : preference;
}
type Storage = {
  getItemAsync(key: string): Promise<string | null>;
  setItemAsync(key: string, value: string): Promise<void>;
};
type Snapshot = {
  preference: Preference;
  ready: boolean;
  saving: boolean;
  error: string;
};
export function createAppearanceStore(storage: Storage) {
  let state: Snapshot = {
    preference: 'system',
    ready: false,
    saving: false,
    error: '',
  };
  const listeners = new Set<() => void>();
  const update = (patch: Partial<Snapshot>) => {
    state = { ...state, ...patch };
    listeners.forEach((listener) => listener());
  };
  let loading: Promise<void> | undefined;
  return {
    getSnapshot: () => state,
    subscribe(listener: () => void) {
      listeners.add(listener);
      return () => {
        listeners.delete(listener);
      };
    },
    load() {
      return (loading ??= (async () => {
        try {
          const saved = await storage.getItemAsync(preferenceKey);
          update({
            preference: isPreference(saved) ? saved : 'system',
            ready: true,
            error:
              saved !== null && !isPreference(saved)
                ? 'Saved appearance was not recognized. Using System; choose a mode to save a new preference.'
                : '',
          });
        } catch {
          update({
            ready: true,
            error:
              'Appearance could not be loaded. Using System. Choose a mode to retry saving.',
          });
        }
      })());
    },
    async select(preference: Preference) {
      if (!isPreference(preference) || !state.ready || state.saving) return;
      update({ preference, saving: true, error: '' });
      try {
        await storage.setItemAsync(preferenceKey, preference);
        update({ saving: false });
      } catch {
        update({
          saving: false,
          error:
            'Appearance changed for this session but was not saved. Select the mode again to retry.',
        });
      }
    },
  };
}
