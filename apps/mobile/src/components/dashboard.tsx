import { router } from 'expo-router';
import { AppIcon } from './NutritionVisuals';
import type { PropsWithChildren } from 'react';
import { Pressable, StyleSheet, Text, View } from 'react-native';
import { progress } from '../domain/dashboard';
import type { PreviewMeal } from '../domain/dashboard';
import { theme as t } from '../theme/tokens';
export const ui = StyleSheet.create({
  page: { flex: 1, backgroundColor: t.colors.background },
  content: {
    padding: t.spacing.md,
    gap: t.spacing.lg,
    width: '100%',
    maxWidth: t.sizing.contentMax,
    alignSelf: 'center',
  },
  title: { ...t.typography.title, color: t.colors.text },
  heading: { ...t.typography.heading, color: t.colors.text },
  body: { ...t.typography.body, color: t.colors.muted },
  label: { ...t.typography.label, color: t.colors.primary },
  card: {
    padding: t.spacing.md,
    gap: t.spacing.md,
    backgroundColor: t.colors.surface,
    borderRadius: t.radii.card,
    borderWidth: 1,
    borderColor: t.colors.border,
  },
  row: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: t.spacing.md,
    justifyContent: 'space-between',
  },
});
export function Card({ children }: PropsWithChildren) {
  return <View style={ui.card}>{children}</View>;
}
export function PreviewNotice() {
  return (
    <View
      style={{
        backgroundColor: t.colors.accent,
        padding: t.spacing.md,
        borderRadius: t.radii.control,
      }}
    >
      <Text style={ui.label}>DEMO PREVIEW</Text>
      <Text style={ui.body}>
        Sample meals and targets only. Nothing here was logged by you. Targets
        are not recommendations.
      </Text>
    </View>
  );
}
export function AddFood({ meal }: { meal?: string }) {
  return (
    <Pressable
      accessibilityRole="button"
      accessibilityLabel={meal ? `Add food to ${meal}` : 'Add food'}
      onPress={() =>
        router.push({ pathname: '/food-search', params: meal ? { meal } : {} })
      }
      style={({ pressed }) => ({
        minHeight: t.sizing.touchTarget,
        padding: t.spacing.md,
        borderRadius: 28,
        backgroundColor: t.colors.primary,
        opacity: pressed ? 0.8 : 1,
        alignItems: 'center',
        justifyContent: 'center',
      })}
    >
      <Text
        style={{
          ...t.typography.body,
          color: t.colors.surface,
          fontWeight: '600',
        }}
      >
        + Add Food
      </Text>
    </Pressable>
  );
}
export function NutrientProgress({
  label,
  consumed,
  target,
  unit,
  color = t.colors.primary,
  compact = false,
}: {
  label: string;
  consumed: number;
  target: number;
  unit: string;
  color?: string;
  compact?: boolean;
}) {
  const value = progress(consumed, target);
  const description = `${label}: ${consumed} of ${target} ${unit}${value.percent === null ? ', target not set' : `, ${Math.round(value.percent)} percent`}`;
  return (
    <View
      accessible
      accessibilityRole="progressbar"
      accessibilityLabel={description}
      accessibilityValue={
        value.percent === null
          ? { text: 'Target not set' }
          : { min: 0, max: 100, now: value.fill, text: description }
      }
      style={{
        gap: t.spacing.sm,
        flex: compact ? 1 : undefined,
        minWidth: compact ? 84 : undefined,
      }}
    >
      <View style={compact ? { gap: 4 } : ui.row}>
        <Text style={ui.label}>{label}</Text>
        <Text style={ui.body}>
          {consumed} / {target > 0 ? target : 'Not set'} {unit}
        </Text>
      </View>
      <View
        style={{
          height: 5,
          borderRadius: 5,
          backgroundColor: t.colors.accent,
          overflow: 'hidden',
        }}
      >
        <View
          style={{
            height: '100%',
            width: `${value.fill}%`,
            backgroundColor: color,
          }}
        />
      </View>
    </View>
  );
}
export function MealCard({ meal }: { meal: PreviewMeal }) {
  return (
    <Card>
      <View style={{ flexDirection: 'row', gap: 16, alignItems: 'center' }}>
        <View
          style={{
            backgroundColor: t.colors.accent,
            padding: 12,
            borderRadius: 16,
          }}
        >
          <AppIcon name="leaf" />
        </View>
        <View style={{ flex: 1, gap: 4 }}>
          <Text
            accessibilityRole="header"
            style={{
              ...t.typography.body,
              color: t.colors.text,
              fontWeight: '600',
            }}
          >
            {meal.name}
          </Text>
          {meal.entries.length === 0 ? (
            <Text style={ui.body}>No sample entries yet</Text>
          ) : (
            meal.entries.map((entry) => (
              <View key={entry.name}>
                <Text
                  style={{
                    ...t.typography.body,
                    color: t.colors.text,
                    fontWeight: '600',
                  }}
                >
                  {entry.nutrients.calories} kcal
                </Text>
                <Text style={ui.body}>{entry.name} (demo)</Text>
                <Text style={ui.label}>
                  P {entry.nutrients.protein}g C {entry.nutrients.carbs}g F{' '}
                  {entry.nutrients.fat}g
                </Text>
              </View>
            ))
          )}
        </View>
      </View>
      <AddFood meal={meal.name} />
    </Card>
  );
}
