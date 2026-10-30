import {
  Alert,
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  View,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { theme as t } from '../theme/tokens';

export function WelcomeScreen() {
  return (
    <SafeAreaView style={s.safe}>
      <ScrollView contentContainerStyle={s.scroll}>
        <View style={s.content}>
          <Text style={s.brand} accessibilityRole="header">
            Bites2Go
          </Text>
          <Text style={s.subtitle}>Everyday food. A clearer picture.</Text>
          <View style={s.intro}>
            <Text style={s.eyebrow}>YOUR NUTRITION TRACKER</Text>
            <Text style={s.title} accessibilityRole="header">
              Make room for better habits.
            </Text>
            <Text style={s.body}>
              A simple place to understand your meals, one day at a time.
            </Text>
          </View>
          <View style={s.card}>
            <Text style={s.heading} accessibilityRole="header">
              Your food diary
            </Text>
            <View style={s.badge}>
              <Text style={s.badgeText}>No entries yet</Text>
            </View>
            <Text style={s.body}>
              Your diary is empty. Nutrition totals will appear here once food
              logging is available.
            </Text>
            <Pressable
              accessibilityRole="button"
              accessibilityLabel="Add food"
              accessibilityHint="Shows information about upcoming food logging"
              onPress={() =>
                Alert.alert(
                  'Food logging is coming soon',
                  'This preview introduces your diary. Food search and saving meals will be added in a later stage.',
                )
              }
              style={({ pressed }) => [s.button, pressed && s.pressed]}
            >
              <Text style={s.buttonText}>+ Add Food</Text>
            </Pressable>
            <Text style={s.note}>
              Preview only � adding food is not available yet.
            </Text>
          </View>
          <Text style={s.footer}>Built around the way you eat.</Text>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}
const s = StyleSheet.create({
  safe: { flex: 1, backgroundColor: t.colors.background },
  scroll: { flexGrow: 1, padding: t.spacing.lg },
  content: {
    width: '100%',
    maxWidth: t.sizing.contentMax,
    alignSelf: 'center',
    gap: t.spacing.sm,
  },
  brand: { ...t.typography.heading, color: t.colors.primary },
  subtitle: { ...t.typography.label, color: t.colors.muted },
  intro: { paddingVertical: t.spacing.xl, gap: t.spacing.md },
  eyebrow: { ...t.typography.label, color: t.colors.primary, letterSpacing: 1 },
  title: { ...t.typography.title, color: t.colors.text },
  heading: { ...t.typography.heading, color: t.colors.text },
  body: { ...t.typography.body, color: t.colors.muted },
  card: {
    padding: t.spacing.lg,
    gap: t.spacing.lg,
    backgroundColor: t.colors.surface,
    borderRadius: t.radii.card,
    borderWidth: 1,
    borderColor: t.colors.border,
  },
  badge: {
    alignSelf: 'flex-start',
    backgroundColor: t.colors.accent,
    paddingHorizontal: t.spacing.md,
    paddingVertical: t.spacing.sm,
    borderRadius: t.radii.control,
  },
  badgeText: { ...t.typography.label, color: t.colors.primary },
  button: {
    minHeight: t.sizing.touchTarget,
    padding: t.spacing.md,
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: t.colors.primary,
    borderRadius: t.radii.control,
  },
  pressed: { opacity: 0.8 },
  buttonText: {
    ...t.typography.body,
    fontWeight: '600',
    color: t.colors.surface,
  },
  note: { ...t.typography.label, color: t.colors.muted },
  footer: {
    ...t.typography.label,
    color: t.colors.muted,
    textAlign: 'center',
    paddingVertical: t.spacing.lg,
  },
});
