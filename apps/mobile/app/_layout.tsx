import { Tabs } from 'expo-router';
import { StatusBar } from 'expo-status-bar';
import { theme } from '../src/theme/tokens';
export default function Layout() {
  return (
    <>
      <StatusBar style="dark" />
      <Tabs
        screenOptions={{
          headerShown: false,
          tabBarActiveTintColor: theme.colors.primary,
          tabBarInactiveTintColor: theme.colors.muted,
          tabBarStyle: { backgroundColor: theme.colors.surface },
          tabBarLabelStyle: { fontSize: 12 },
          tabBarIconStyle: { display: 'none' },
          tabBarItemStyle: { minHeight: 48 },
        }}
      >
        <Tabs.Screen name="index" options={{ title: 'Home' }} />
        <Tabs.Screen name="diary" options={{ title: 'Diary' }} />
        <Tabs.Screen name="calendar" options={{ title: 'Calendar' }} />
        <Tabs.Screen name="progress" options={{ title: 'Progress' }} />
        <Tabs.Screen name="profile" options={{ title: 'Profile' }} />
      </Tabs>
    </>
  );
}
