import { router } from 'expo-router';
import type { PropsWithChildren } from 'react';
import { Pressable, StyleSheet, Text, View } from 'react-native';
import { progress } from '../domain/dashboard';
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
      <Text style={ui.label}>NUTRITION DATA NOTICE</Text>
      <Text style={ui.body}>
        Saved entries use illustrative food values. Targets are sample settings,
        not medical recommendations. No sample meals are counted automatically.
      </Text>
    </View>
  );
}
export function AddFood({
  meal,
  date,
  disabled = false,
}: {
  meal?: string;
  date: string;
  disabled?: boolean;
}) {
  return (
    <Pressable
      accessibilityRole="button"
      disabled={disabled}
      accessibilityState={{ disabled }}
      accessibilityLabel={meal ? `Add food to ${meal}` : 'Add food'}
      onPress={() =>
        router.push({
          pathname: '/food-search',
          params: { date, ...(meal ? { meal } : {}) },
        })
      }
      style={({ pressed }) => ({
        minHeight: t.sizing.touchTarget,
        padding: t.spacing.md,
        borderRadius: 28,
        backgroundColor: t.colors.primary,
        opacity: disabled ? 0.5 : pressed ? 0.8 : 1,
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
  partial = false,
}: {
  label: string;
  consumed: number | null;
  target: number;
  unit: string;
  color?: string;
  compact?: boolean;
  partial?: boolean;
}) {
  const value = progress(consumed ?? 0, target);
  const incomplete = partial || consumed === null;
  const amount = consumed === null ? 'Unknown' : consumed.toFixed(1);
  const description = `${label}: ${amount}${incomplete ? ' (incomplete data)' : ''} of ${target} ${unit}${incomplete ? ', percentage unavailable' : value.percent === null ? ', target not set' : `, ${Math.round(value.percent)} percent`}`;
  return (
    <View
      accessible
      accessibilityRole="progressbar"
      accessibilityLabel={description}
      accessibilityValue={
        incomplete || value.percent === null
          ? {
              text: incomplete ? 'Incomplete nutrition data' : 'Target not set',
            }
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
          {amount}
          {incomplete ? ' (incomplete)' : ''} /{' '}
          {target > 0 ? target : 'Not set'} {unit}
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
            width: `${incomplete ? 0 : value.fill}%`,
            backgroundColor: color,
          }}
        />
      </View>
    </View>
  );
}
