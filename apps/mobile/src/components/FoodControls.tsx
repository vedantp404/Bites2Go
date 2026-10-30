import { Pressable, StyleSheet, Text, View } from 'react-native';
import type { FoodNutrients } from '../domain/food';
import { formatNutrient } from '../domain/food';
import { ui } from './dashboard';
import { theme as t } from '../theme/tokens';
export function Action({
  label,
  onPress,
  disabled = false,
}: {
  label: string;
  onPress: () => void;
  disabled?: boolean;
}) {
  return (
    <Pressable
      accessibilityRole="button"
      accessibilityState={{ disabled }}
      disabled={disabled}
      onPress={onPress}
      style={({ pressed }) => [
        styles.button,
        { opacity: disabled ? 0.5 : pressed ? 0.8 : 1 },
      ]}
    >
      <Text style={styles.buttonText}>{label}</Text>
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
export const styles = StyleSheet.create({
  input: {
    ...t.typography.body,
    color: t.colors.text,
    backgroundColor: t.colors.surface,
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
    color: t.colors.surface,
    fontWeight: '600',
  },
});
