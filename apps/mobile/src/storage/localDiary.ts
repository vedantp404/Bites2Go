import Storage from 'expo-sqlite/kv-store';
import { createDiaryRepository } from './diaryRepository';
export const diaryRepository = createDiaryRepository({
  getItem: (key) => Storage.getItemAsync(key),
  setItem: (key, value) => Storage.setItemAsync(key, value),
});
