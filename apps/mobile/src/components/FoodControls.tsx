import { useMemo } from 'react';
import type { Theme } from '../theme/tokens';
import { Pressable, StyleSheet, Text, View } from 'react-native';
import type { FoodNutrients } from '../domain/food';
import { formatNutrient } from '../domain/food';
import { useUI } from './dashboard';

export function Action({
  label,
  onPress,
  disabled = false,
  variant = 'primary',
}: {
  label: string;
  onPress: () => void;
  disabled?: boolean;
  variant?: 'primary' | 'secondary' | 'danger';
}) {
  const styles = useFoodStyles();
  const { t } = useUI();
  const background =
    variant === 'primary'
      ? t.colors.primary
      : variant === 'danger'
        ? t.colors.highlight
        : t.colors.elevated;
  const foreground =
    variant === 'primary'
      ? t.colors.onPrimary
      : variant === 'danger'
        ? t.colors.error
        : t.colors.text;
  return (
    <Pressable
      accessibilityRole="button"
      accessibilityState={{ disabled }}
      disabled={disabled}
      onPress={onPress}
      style={({ pressed }) => [
        styles.button,
        { backgroundColor: background },
        { opacity: disabled ? 0.5 : pressed ? 0.8 : 1 },
      ]}
    >
      <Text style={[styles.buttonText, { color: foreground }]}>{label}</Text>
    </Pressable>
  );
}
const labels = {
  calories: 'Energy',
  protein: 'Protein',
  carbs: 'Carbohydrates',
  fat: 'Fat',
  fiber: 'Fiber',
} as const;
export function Nutrition({ values }: { values: FoodNutrients }) {
  const { ui, t } = useUI();
  return (
    <View style={{ gap: t.spacing.sm }}>
      {(Object.keys(labels) as (keyof FoodNutrients)[]).map((key) => (
        <View key={key} style={ui.row}>
          <Text style={ui.body}>{labels[key]}</Text>
          <Text style={ui.label}>
            {formatNutrient(values[key], key === 'calories' ? 'kcal' : 'g')}
          </Text>
        </View>
      ))}
    </View>
  );
}
const makeStyles = (t: Theme) =>
  StyleSheet.create({
    input: {
      ...t.typography.body,
      color: t.colors.text,
      backgroundColor: t.colors.input,
      minHeight: t.sizing.touchTarget,
      borderWidth: 1,
      borderColor: t.colors.border,
      borderRadius: t.radii.control,
      padding: t.spacing.md,
    },
    back: {
      minHeight: t.sizing.touchTarget,
      justifyContent: 'center',
      alignSelf: 'flex-start',
      paddingHorizontal: t.spacing.sm,
    },
    button: {
      minHeight: t.sizing.touchTarget,
      padding: t.spacing.md,
      borderRadius: 28,
      backgroundColor: t.colors.primary,
      alignItems: 'center',
      justifyContent: 'center',
    },
    buttonText: {
      ...t.typography.body,
      color: t.colors.onPrimary,
      fontWeight: '600',
    },
  });

export function useFoodStyles() {
  const { t } = useUI();
  return useMemo(() => makeStyles(t), [t]);
}
