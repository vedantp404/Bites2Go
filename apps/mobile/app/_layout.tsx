import { DiaryProvider } from '../src/state/DiaryProvider';
import { ThemeProvider, useTheme } from '../src/theme/ThemeProvider';
import {
  Stack,
  SplashScreen,
  ThemeProvider as NavigationThemeProvider,
} from 'expo-router';
import { StatusBar } from 'expo-status-bar';
import { NavigationBar } from 'expo-navigation-bar';
import { View } from 'react-native';
export default function Layout() {
  return (
    <ThemeProvider>
      <App />
    </ThemeProvider>
  );
}
function App() {
  const { theme: t, mode } = useTheme();
  const font = { fontFamily: 'System', fontWeight: '400' as const };
  const navigationTheme = {
    dark: mode === 'dark',
    colors: {
      primary: t.colors.primary,
      background: t.colors.background,
      card: t.colors.surface,
      text: t.colors.text,
      border: t.colors.border,
      notification: t.colors.secondary,
    },
    fonts: { regular: font, medium: font, bold: font, heavy: font },
  };
  return (
    <View
      style={{ flex: 1, backgroundColor: t.colors.background }}
      onLayout={() => {
        void SplashScreen.hideAsync().catch((error) =>
          console.warn('Splash screen hide failed', error),
        );
      }}
    >
      <NavigationThemeProvider value={navigationTheme}>
        <DiaryProvider>
          <StatusBar style={mode === 'dark' ? 'light' : 'dark'} />
          <NavigationBar style={mode === 'dark' ? 'light' : 'dark'} />
          <Stack
            screenOptions={{
              headerShown: false,
              contentStyle: { backgroundColor: t.colors.background },
            }}
          >
            <Stack.Screen name="(tabs)" />
            <Stack.Screen
              name="food-search"
              options={{ gestureEnabled: false }}
            />
            <Stack.Screen
              name="diary-entry"
              options={{ gestureEnabled: false }}
            />
          </Stack>
        </DiaryProvider>
      </NavigationThemeProvider>
    </View>
  );
}
