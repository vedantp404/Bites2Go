import { router } from 'expo-router';
import { useMemo, type PropsWithChildren } from 'react';
import { Pressable, StyleSheet, Text, View } from 'react-native';
import { calculateNutrientProgress } from '../domain/dashboard';
import type { Theme } from '../theme/tokens';
import { useTheme } from '../theme/ThemeProvider';
const makeUI = (t: Theme) =>
  StyleSheet.create({
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
export function useUI() {
  const { theme: t } = useTheme();
  const ui = useMemo(() => makeUI(t), [t]);
  return { ui, t };
}
export function Card({ children }: PropsWithChildren) {
  const { ui } = useUI();
  return <View style={ui.card}>{children}</View>;
}
export function PreviewNotice() {
  const { ui, t } = useUI();
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
        Saved entries use illustrative food values. Personal targets are
        tracking settings, not medical recommendations. No sample meals are
        counted automatically.
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
  const { t } = useUI();
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
        backgroundColor: disabled
          ? t.colors.elevated
          : meal
            ? t.colors.selected
            : t.colors.primary,
        opacity: pressed ? 0.8 : 1,
        alignItems: 'center',
        justifyContent: 'center',
      })}
    >
      <Text
        style={{
          ...t.typography.body,
          color: disabled
            ? t.colors.disabled
            : meal
              ? t.colors.primary
              : t.colors.onPrimary,
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
  color,
  compact = false,
  partial = false,
}: {
  label: string;
  consumed: number | null;
  target: number | null;
  unit: string;
  color?: string;
  compact?: boolean;
  partial?: boolean;
}) {
  const { ui, t } = useUI();
  const state = calculateNutrientProgress(consumed, target, partial, unit);
  const incomplete = state.isPartial;
  const amount = consumed === null ? 'Unknown' : consumed.toFixed(1);
  const barColor = color ?? t.colors.primary;

  const description = `${label}: ${amount}${incomplete ? ' (incomplete data)' : ''} of ${target ?? 'unset'} ${unit}${incomplete ? ', percentage unavailable' : state.percent === null ? ', target not set' : `, ${Math.round(state.percent)} percent`}${state.isExceeded ? `, ${state.exceeded.toFixed(1)} ${unit} exceeded` : state.remaining !== null ? `, ${state.remaining.toFixed(1)} ${unit} remaining` : ''}`;

  return (
    <View
      accessible
      accessibilityRole="progressbar"
      accessibilityLabel={description}
      accessibilityValue={
        incomplete || state.percent === null
          ? {
              text: incomplete ? 'Incomplete nutrition data' : 'Target not set',
            }
          : { min: 0, max: 100, now: state.fill, text: description }
      }
      style={{
        gap: t.spacing.xs,
        flex: compact ? 1 : undefined,
        minWidth: compact ? 92 : undefined,
      }}
    >
      <View
        style={{
          flexDirection: 'row',
          alignItems: 'center',
          justifyContent: 'space-between',
        }}
      >
        <View style={{ flexDirection: 'row', alignItems: 'center', gap: 6 }}>
          <View
            style={{
              width: 8,
              height: 8,
              borderRadius: 4,
              backgroundColor: barColor,
            }}
          />
          <Text style={ui.label}>{label}</Text>
        </View>
        <Text
          style={{
            ...t.typography.label,
            fontSize: 12,
            fontWeight: '600',
            color: state.isExceeded ? t.colors.warning : t.colors.muted,
          }}
        >
          {incomplete ? '--' : state.formattedPercent}
        </Text>
      </View>

      <View
        style={{
          height: 7,
          borderRadius: 4,
          backgroundColor: t.colors.accent,
          overflow: 'hidden',
          marginVertical: 2,
        }}
      >
        <View
          style={{
            height: '100%',
            width: `${incomplete ? 0 : state.fill}%`,
            backgroundColor: state.isExceeded ? t.colors.warning : barColor,
            borderRadius: 4,
          }}
        />
      </View>

      <View style={compact ? { gap: 2 } : ui.row}>
        <Text
          style={{
            ...t.typography.body,
            fontSize: 13,
            lineHeight: 18,
            color: t.colors.text,
          }}
        >
          {amount} {unit}
          <Text style={{ color: t.colors.muted, fontSize: 12 }}>
            {' '}
            / {target ? `${target} ${unit}` : 'Not set'}
          </Text>
        </Text>
        <Text
          style={{
            ...t.typography.body,
            fontSize: 12,
            lineHeight: 16,
            color: state.isExceeded ? t.colors.warning : t.colors.muted,
            fontWeight: state.isExceeded ? '600' : '400',
          }}
        >
          {state.statusText}
        </Text>
      </View>
    </View>
  );
}
