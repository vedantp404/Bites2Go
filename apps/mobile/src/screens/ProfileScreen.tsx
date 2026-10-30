import { cloudConfiguration } from '../cloud/config';
import { router } from 'expo-router';
import { Action } from '../components/FoodControls';
import { HealthStatus, BmiCard } from '../components/HealthControls';
import { Pressable, ScrollView, Text, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Card, useUI } from '../components/dashboard';
import { useTheme } from '../theme/ThemeProvider';
import type { Preference } from '../theme/appearance';
const options: { value: Preference; title: string; detail: string }[] = [
  { value: 'light', title: 'Light', detail: 'Warm surfaces and fresh greens' },
  { value: 'dark', title: 'Dark', detail: 'Soft charcoal and gentle contrast' },
  {
    value: 'system',
    title: 'System',
    detail: 'Follow your device appearance (default)',
  },
];
export default function ProfileScreen() {
  const { ui, t } = useUI();
  const cloud = cloudConfiguration(
    process.env.EXPO_PUBLIC_SUPABASE_URL,
    process.env.EXPO_PUBLIC_SUPABASE_PUBLISHABLE_KEY,
  );
  const { preference, mode, select, saving, error } = useTheme();
  return (
    <SafeAreaView edges={['top', 'left', 'right']} style={ui.page}>
      <ScrollView contentContainerStyle={ui.content}>
        <Text style={ui.label}>MAKE IT YOURS</Text>
        <Text accessibilityRole="header" style={ui.title}>
          Profile
        </Text>
        <Card>
          <Text accessibilityRole="header" style={ui.heading}>
            Account and cloud
          </Text>
          <Text style={ui.label}>Offline mode / not signed in</Text>
          <Text style={ui.body}>{cloud.message}</Text>
          <Text style={ui.body}>
            No records are uploaded. Food logging, history, goals and appearance
            work without an account. Cloud sign-in and synchronisation are not
            available yet.
          </Text>
        </Card>
        <HealthStatus />
        <Action
          label="Nutrition goals, height and weight target"
          onPress={() => router.push('/goals')}
        />
        <Action
          variant="secondary"
          label="My foods and recipes"
          onPress={() => router.push('/my-foods')}
        />
        <BmiCard />
        <Card>
          <Text accessibilityRole="header" style={ui.heading}>
            Appearance
          </Text>
          <Text style={ui.body}>A comfortable view, any time of day.</Text>
          {options.map((option) => (
            <Pressable
              key={option.value}
              accessibilityRole="radio"
              accessibilityState={{
                checked: preference === option.value,
                disabled: saving,
              }}
              disabled={saving}
              onPress={() => {
                void select(option.value);
              }}
              style={[
                ui.card,
                {
                  minHeight: 64,
                  backgroundColor:
                    preference === option.value
                      ? t.colors.selected
                      : t.colors.surface,
                  borderColor:
                    preference === option.value
                      ? t.colors.primary
                      : t.colors.border,
                },
              ]}
            >
              <View style={ui.row}>
                <Text style={ui.heading}>{option.title}</Text>
                <Text style={ui.label}>
                  {preference === option.value ? 'Selected' : ''}
                </Text>
              </View>
              <Text style={ui.body}>{option.detail}</Text>
            </Pressable>
          ))}
          <Text accessibilityLiveRegion="polite" style={ui.body}>
            {saving
              ? 'Saving appearance...'
              : `${preference === 'system' ? 'System' : 'Current'} appearance: ${mode}.`}
          </Text>
          {error ? (
            <Text
              accessibilityRole="alert"
              style={[ui.body, { color: t.colors.error }]}
            >
              {error}
            </Text>
          ) : null}
        </Card>
        <Text style={ui.body}>
          Appearance and goals are saved on this device. Account settings are
          not available.
        </Text>
      </ScrollView>
    </SafeAreaView>
  );
}
