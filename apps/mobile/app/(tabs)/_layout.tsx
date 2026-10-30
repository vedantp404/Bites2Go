import { AppIcon } from '../../src/components/NutritionVisuals';
import { Tabs } from 'expo-router';
import { useTheme } from '../../src/theme/ThemeProvider';
export default function Layout() {
  const { theme } = useTheme();
  return (
    <>
      <Tabs
        screenOptions={({ route }) => ({
          headerShown: false,
          tabBarActiveTintColor: theme.colors.primary,
          tabBarInactiveTintColor: theme.colors.muted,
          tabBarStyle: {
            backgroundColor: theme.colors.surface,
            borderTopColor: theme.colors.border,
          },
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
