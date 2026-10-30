import { useState } from 'react';
import { Text } from 'react-native';
import { router } from 'expo-router';
import { useHealth } from '../state/HealthProvider';
import { useUI, Card } from '../components/dashboard';
import { Action } from '../components/FoodControls';
import {
  Field,
  HealthPage,
  HealthStatus,
  useHealthForm,
} from '../components/HealthControls';
import {
  inputNumber,
  nutrientKeys,
  limits,
  saveSettings,
  targetsForDate,
  type Health,
  type Targets,
} from '../domain/health';
import { localDateKey } from '../domain/diary';
const labels = {
  calories: 'Calories (kcal)',
  protein: 'Protein (g)',
  carbs: 'Carbohydrates (g)',
  fat: 'Fat (g)',
};
export default function GoalsScreen() {
  const { data } = useHealth();
  return data ? (
    <Editor initial={data} />
  ) : (
    <HealthPage title="Goals and height">
      <HealthStatus />
      <Action
        label="Back to Profile"
        onPress={() => router.replace('/profile')}
      />
    </HealthPage>
  );
}
function Editor({ initial }: { initial: Health }) {
  const [original] = useState(initial);
  const [date] = useState(localDateKey);
  const [values, setValues] = useState(
    () =>
      Object.fromEntries(
        nutrientKeys.map((k) => [
          k,
          String(targetsForDate(initial, date)[k] ?? ''),
        ]),
      ) as Record<(typeof nutrientKeys)[number], string>,
  );
  const [height, setHeight] = useState(String(initial.heightCm ?? ''));
  const [weight, setWeight] = useState(
    String(initial.weightGoal?.targetKg ?? ''),
  );
  const form = useHealthForm(original);
  const { ui, t } = useUI();
  return (
    <HealthPage title="Goals and height">
      <Action
        label="Cancel / Back"
        variant="secondary"
        disabled={form.busy}
        onPress={form.back}
      />
      <Card>
        <Text accessibilityRole="header" style={ui.heading}>
          Daily nutrition targets
        </Text>
        <Text style={ui.body}>
          Effective {date}. Saving replaces targets for this date and later
          until your next change. Earlier dates stay unchanged. Blank means
          unset; zero disables percentage progress. Positive targets start at 1
          kcal or 0.1 g. No targets are prescribed automatically.
        </Text>
        {nutrientKeys.map((k) => (
          <Field
            key={k}
            label={`${labels[k]} / 0–${limits[k]}`}
            value={values[k]}
            disabled={form.disabled}
            onChangeText={(value) => setValues({ ...values, [k]: value })}
          />
        ))}
      </Card>
      <Card>
        <Text accessibilityRole="header" style={ui.heading}>
          Height and weight goal
        </Text>
        <Field
          label="Height (cm) / 100–250, optional"
          value={height}
          onChangeText={setHeight}
          disabled={form.disabled}
        />
        <Field
          label="Target weight (kg) / 20–500, optional"
          value={weight}
          onChangeText={setWeight}
          disabled={form.disabled}
        />
        <Text style={ui.body}>
          Blank clears the setting. A changed weight target starts from the
          latest recorded weight, or your first measurement dated on/after
          today. Keeping the same target preserves its starting point. These
          limits are for input validation, not personal recommendations.
        </Text>
      </Card>
      {form.error ? (
        <Text
          accessibilityRole="alert"
          style={[ui.body, { color: t.colors.error }]}
        >
          {form.error}
        </Text>
      ) : null}
      <Action
        label={
          form.busy
            ? 'Saving...'
            : form.pending
              ? 'Retry saving settings'
              : 'Confirm and save settings'
        }
        disabled={form.busy}
        onPress={() => {
          void form.submit(() => {
            const targets = Object.fromEntries(
              nutrientKeys.map((k) => [
                k,
                inputNumber(values[k], 0, limits[k], true),
              ]),
            ) as Targets;
            return saveSettings(
              original,
              date,
              targets,
              inputNumber(height, 100, 250, true),
              inputNumber(weight, 20, 500, true),
            );
          });
        }}
      />
      <Text style={ui.body}>
        BMI is shown in Profile and Progress using your height and latest dated
        weight. No calorie prescription or medical interpretation is generated.
      </Text>
    </HealthPage>
  );
}
