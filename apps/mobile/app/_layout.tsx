import { AppIcon } from '../src/components/NutritionVisuals';
import { Tabs, usePathname } from 'expo-router';
import { StatusBar } from 'expo-status-bar';
import { theme } from '../src/theme/tokens';
export default function Layout() {
  const home = usePathname() === '/';
  return (
    <>
      <StatusBar style={home ? 'light' : 'dark'} />
      <Tabs
        screenOptions={({ route }) => ({
          headerShown: false,
          tabBarActiveTintColor: theme.colors.primary,
          tabBarInactiveTintColor: theme.colors.muted,
          tabBarStyle: { backgroundColor: theme.colors.surface },
          tabBarLabelStyle: { fontSize: 12 },
          tabBarIcon: ({ focused, size }) => (
            <AppIcon
              name={route.name}
              color={focused ? theme.colors.primary : theme.colors.muted}
              size={size}
            />
          ),
          tabBarItemStyle: { minHeight: 48 },
        })}
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
