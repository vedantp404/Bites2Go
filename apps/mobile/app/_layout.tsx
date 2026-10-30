import { DiaryProvider } from '../src/state/DiaryProvider';
import { Stack, usePathname } from 'expo-router';
import { StatusBar } from 'expo-status-bar';
export default function Layout() {
  return (
    <DiaryProvider>
      <StatusBar style={usePathname() === '/' ? 'light' : 'dark'} />
      <Stack screenOptions={{ headerShown: false }}>
        <Stack.Screen name="(tabs)" />
        <Stack.Screen name="food-search" options={{ gestureEnabled: false }} />
        <Stack.Screen name="diary-entry" options={{ gestureEnabled: false }} />
      </Stack>
    </DiaryProvider>
  );
}
