import { useState } from 'react';
import { Text } from 'react-native';
import { router, useLocalSearchParams } from 'expo-router';
import { randomUUID } from 'expo-crypto';
import { useHealth } from '../state/HealthProvider';
import { useUI, Card } from '../components/dashboard';
import { Action } from '../components/FoodControls';
import {
  ConfirmDelete,
  Field,
  HealthPage,
  HealthStatus,
  useHealthForm,
} from '../components/HealthControls';
import {
  inputNumber,
  recordWeight,
  removeWeight,
  type Health,
  type Weight,
} from '../domain/health';
import { localDateKey } from '../domain/diary';
export default function WeightEntryScreen() {
  const { data } = useHealth();
  const { id } = useLocalSearchParams<{ id?: string }>();
  const { ui } = useUI();
  const entry = data?.weights.find((w) => w.id === id);
  if (!data || (id && !entry))
    return (
      <HealthPage title="Weight measurement">
        <HealthStatus />
        {data ? (
          <Text style={ui.body}>Measurement not found. Reload Progress.</Text>
        ) : null}
        <Action
          label="Back to Progress"
          onPress={() => router.replace('/progress')}
        />
      </HealthPage>
    );
  return <Editor original={data} entry={entry} />;
}
function Editor({
  original: initial,
  entry,
}: {
  original: Health;
  entry?: Weight;
}) {
  const [original] = useState(initial);
  const [id] = useState(() => entry?.id ?? randomUUID());
  const [date, setDate] = useState(entry?.date ?? localDateKey());
  const [kg, setKg] = useState(entry ? String(entry.kg) : '');
  const [confirm, setConfirm] = useState(false);
  const form = useHealthForm(original);
  const { ui, t } = useUI();
  return (
    <HealthPage title={entry ? 'Edit weight' : 'Record weight'}>
      <Action
        label="Cancel / Back"
        variant="secondary"
        disabled={form.busy}
        onPress={form.back}
      />
      <Card>
        <Field
          label="Measurement date (YYYY-MM-DD)"
          date
          value={date}
          onChangeText={setDate}
          disabled={form.disabled}
        />
        <Text style={ui.body}>
          Today or a past date. One measurement per date; edit an existing
          record to replace it.
        </Text>
        <Field
          label="Weight (kg)"
          value={kg}
          onChangeText={setKg}
          disabled={form.disabled}
        />
        <Text style={ui.body}>
          Supported range: 20–500 kg. This is an input limit, not a health
          recommendation.
        </Text>
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
                ? 'Retry pending change'
                : 'Save measurement'
          }
          disabled={form.busy}
          onPress={() => {
            void form.submit(() =>
              recordWeight(
                original,
                {
                  id,
                  date: date.trim(),
                  kg: inputNumber(kg, 20, 500)!,
                  unit: 'kg',
                },
                Boolean(entry),
              ),
            );
          }}
        />
        {entry ? (
          <Action
            label="Delete measurement"
            variant="danger"
            disabled={form.disabled}
            onPress={() => setConfirm(true)}
          />
        ) : null}
      </Card>
      <ConfirmDelete
        visible={confirm}
        onCancel={() => setConfirm(false)}
        onConfirm={() => {
          setConfirm(false);
          void form.submit(() => removeWeight(original, id));
        }}
      />
    </HealthPage>
  );
}
