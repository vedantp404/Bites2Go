import { useState } from 'react';
import { Text } from 'react-native';
import { randomUUID } from 'expo-crypto';
import { router, useLocalSearchParams } from 'expo-router';
import { useLibrary } from '../state/LibraryProvider';
import { Card, useUI } from '../components/dashboard';
import { Action, Nutrition } from '../components/FoodControls';
import { HealthPage, Field, ConfirmDelete } from '../components/HealthControls';
import { LibraryStatus, useLibraryForm } from '../components/LibraryControls';
import { FoodImage } from '../components/FoodImage';
import {
  customAsFood,
  saveCustom,
  removeLibraryItem,
  type Library,
  type CustomFood,
} from '../domain/library';
import { foodNutrientKeys, type FoodNutrients } from '../domain/food';
import { inputNumber } from '../domain/health';
export default function CustomFoodScreen() {
  const { data } = useLibrary();
  const { id } = useLocalSearchParams<{ id?: string }>();
  const { ui } = useUI();
  const item = data?.customFoods.find((f) => f.id === id);
  if (!data || (id && !item))
    return (
      <HealthPage title="Custom food">
        <LibraryStatus />
        {data ? (
          <Text style={ui.body}>This food is no longer available.</Text>
        ) : null}
        <Action
          label="Back to library"
          onPress={() => router.replace('/my-foods')}
        />
      </HealthPage>
    );
  return <Editor key={id ?? 'new'} initial={data} item={item} />;
}
function Editor({ initial, item }: { initial: Library; item?: CustomFood }) {
  const [original] = useState(initial);
  const [id] = useState(() => item?.id ?? `custom:${randomUUID()}`);
  const [createdAt] = useState(
    () => item?.createdAt ?? new Date().toISOString(),
  );
  const [name, setName] = useState(item?.name ?? '');
  const [description, setDescription] = useState(item?.description ?? '');
  const [grams, setGrams] = useState(String(item?.servingGrams ?? 100));
  const [values, setValues] = useState(
    () =>
      Object.fromEntries(
        foodNutrientKeys.map((k) => [
          k,
          String(item?.servingNutrients[k] ?? ''),
        ]),
      ) as Record<keyof FoodNutrients, string>,
  );
  const [confirm, setConfirm] = useState(false);
  const form = useLibraryForm(original);
  const { ui, t } = useUI();
  function build(): CustomFood {
    return {
      id,
      name: name.trim(),
      description: description.trim(),
      servingGrams: inputNumber(grams, 0.1, 10000)!,
      servingNutrients: Object.fromEntries(
        foodNutrientKeys.map((k) => [
          k,
          inputNumber(values[k], 0, 1000000, true),
        ]),
      ) as FoodNutrients,
      createdAt,
      updatedAt: new Date().toISOString(),
    };
  }
  let preview: ReturnType<typeof customAsFood> | null = null;
  try {
    const candidate = build();
    preview = customAsFood(candidate);
  } catch {
    /* Editable input is validated on save. */
  }
  return (
    <HealthPage title={item ? 'Edit custom food' : 'Create custom food'}>
      <Action
        variant="secondary"
        label="Cancel / Back"
        disabled={form.busy}
        onPress={form.back}
      />
      <Card>
        <FoodImage foodId={id} />
        <Field
          text
          label="Food name (1–120 characters)"
          value={name}
          onChangeText={setName}
          disabled={form.disabled}
        />
        <Field
          text
          label="Description or brand (optional, up to 500 characters)"
          value={description}
          onChangeText={setDescription}
          disabled={form.disabled}
        />
        <Field
          label="Serving weight in grams (0.1–10,000)"
          value={grams}
          onChangeText={setGrams}
          disabled={form.disabled}
        />
        <Text style={ui.body}>
          Enter nutrition for that serving, not per 100 g unless the serving
          weighs 100 g. Blank is unknown; 0 means an explicit zero. User-entered
          values may be estimates.
        </Text>
        {foodNutrientKeys.map((k) => (
          <Field
            key={k}
            label={`${k === 'carbs' ? 'Carbohydrates' : k[0].toUpperCase() + k.slice(1)} (${k === 'calories' ? 'kcal' : 'g'}) per serving`}
            value={values[k]}
            onChangeText={(v) => setValues({ ...values, [k]: v })}
            disabled={form.disabled}
          />
        ))}
      </Card>
      {preview ? (
        <Card>
          <Text style={ui.heading}>Review / per 100 g</Text>
          <Nutrition values={preview.nutrients} />
        </Card>
      ) : null}
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
              ? 'Retry pending library change'
              : 'Confirm and save food'
        }
        disabled={form.busy}
        onPress={() => {
          void form.submit(() => saveCustom(original, build(), Boolean(item)));
        }}
      />
      {item ? (
        <Action
          variant="danger"
          label="Delete custom food"
          disabled={form.disabled}
          onPress={() => setConfirm(true)}
        />
      ) : null}
      <ConfirmDelete
        title="Delete custom food?"
        message="Existing diary entries and recipe ingredient snapshots stay unchanged. This food will leave search, recents and favourites."
        confirmLabel="Delete food"
        visible={confirm}
        onCancel={() => setConfirm(false)}
        onConfirm={() => {
          setConfirm(false);
          void form.submit(() => removeLibraryItem(original, id));
        }}
      />
    </HealthPage>
  );
}
