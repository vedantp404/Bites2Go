import { useState } from 'react';
import { Text } from 'react-native';
import { randomUUID } from 'expo-crypto';
import { router, useLocalSearchParams } from 'expo-router';
import { useLibrary } from '../state/LibraryProvider';
import { Card, useUI } from '../components/dashboard';
import { Action, Nutrition } from '../components/FoodControls';
import { HealthPage, Field, ConfirmDelete } from '../components/HealthControls';
import {
  FoodChoice,
  LibraryStatus,
  useLibraryForm,
} from '../components/LibraryControls';
import { FoodImage } from '../components/FoodImage';
import { foods } from '../data/foods';
import {
  libraryFoods,
  ingredientFromFood,
  recipeNutrition,
  saveRecipe,
  removeLibraryItem,
  type Library,
  type Recipe,
  type Ingredient,
} from '../domain/library';
import { searchFoods } from '../domain/food';
import { inputNumber } from '../domain/health';
export default function RecipeScreen() {
  const { data } = useLibrary();
  const { id } = useLocalSearchParams<{ id?: string }>();
  const { ui } = useUI();
  const item = data?.recipes.find((f) => f.id === id);
  if (!data || (id && !item))
    return (
      <HealthPage title="Recipe">
        <LibraryStatus />
        {data ? (
          <Text style={ui.body}>This recipe is no longer available.</Text>
        ) : null}
        <Action
          label="Back to library"
          onPress={() => router.replace('/my-foods')}
        />
      </HealthPage>
    );
  return <Editor key={id ?? 'new'} initial={data} item={item} />;
}
function Editor({ initial, item }: { initial: Library; item?: Recipe }) {
  const [original] = useState(initial);
  const [id] = useState(() => item?.id ?? `recipe:${randomUUID()}`);
  const [createdAt] = useState(
    () => item?.createdAt ?? new Date().toISOString(),
  );
  const [name, setName] = useState(item?.name ?? '');
  const [description, setDescription] = useState(item?.description ?? '');
  const [yieldGrams, setYield] = useState(String(item?.yieldGrams ?? ''));
  const [servings, setServings] = useState(String(item?.servings ?? 1));
  const [ingredients, setIngredients] = useState<
    (Ingredient & { amount: string })[]
  >(
    () =>
      item?.ingredients.map((i) => ({ ...i, amount: String(i.grams) })) ?? [],
  );
  const [query, setQuery] = useState('');
  const [searching, setSearching] = useState(false);
  const [confirm, setConfirm] = useState(false);
  const form = useLibraryForm(original);
  const { ui, t } = useUI();
  const available = libraryFoods(original, foods).filter(
    (f) => !f.id.startsWith('recipe:'),
  );
  function build(): Recipe {
    return {
      id,
      name: name.trim(),
      description: description.trim(),
      ingredients: ingredients.map(({ amount, ...i }) => ({
        ...i,
        grams: inputNumber(amount, 0.1, 1000000)!,
      })),
      yieldGrams: inputNumber(yieldGrams, 0.1, 1000000)!,
      servings: inputNumber(servings, 0.1, 10000)!,
      createdAt,
      updatedAt: new Date().toISOString(),
    };
  }
  let preview: ReturnType<typeof recipeNutrition> | null = null;
  try {
    preview = recipeNutrition(build());
  } catch {
    /* Show a preview only for valid quantities/yield. */
  }
  return (
    <HealthPage title={item ? 'Edit meal / recipe' : 'Create meal / recipe'}>
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
          label="Meal / recipe name (1–120 characters)"
          value={name}
          onChangeText={setName}
          disabled={form.disabled}
        />
        <Field
          text
          label="Description (optional, up to 500 characters)"
          value={description}
          onChangeText={setDescription}
          disabled={form.disabled}
        />
      </Card>
      <Card>
        <Text style={ui.heading}>Ingredients</Text>
        <Text style={ui.body}>
          Use grams of built-in or custom foods. Ingredients keep the nutrition
          snapshot selected here. Remove and re-add one to refresh it from its
          source.
        </Text>
        {ingredients.map((i, index) => (
          <Card key={i.foodId}>
            <Text style={ui.heading}>{i.name}</Text>
            {!available.some((f) => f.id === i.foodId) ? (
              <Text style={ui.body}>
                Source unavailable; saved ingredient nutrition is retained.
              </Text>
            ) : null}
            <Field
              label={`${i.name} quantity (g)`}
              value={i.amount}
              disabled={form.disabled}
              onChangeText={(amount) =>
                setIngredients(
                  ingredients.map((x, n) =>
                    n === index ? { ...x, amount } : x,
                  ),
                )
              }
            />
            <Action
              variant="secondary"
              label={`Remove ${i.name} ingredient`}
              disabled={form.disabled}
              onPress={() =>
                setIngredients(ingredients.filter((_, n) => n !== index))
              }
            />
          </Card>
        ))}
        {!ingredients.length ? (
          <Text style={ui.body}>No ingredients yet. Add at least one.</Text>
        ) : null}
        <Action
          variant="secondary"
          label={searching ? 'Close ingredient search' : 'Add ingredient'}
          disabled={form.disabled || ingredients.length >= 100}
          onPress={() => setSearching(!searching)}
        />
        {searching ? (
          <>
            <Field
              text
              label="Search ingredients by food name or alias"
              value={query}
              onChangeText={setQuery}
              disabled={form.disabled}
            />
            {searchFoods(available, query).length === 0 ? (
              <Text style={ui.body}>
                No matching ingredients. Create a custom food in My foods first
                if needed.
              </Text>
            ) : null}
            {searchFoods(available, query).map((food) => (
              <FoodChoice
                key={food.id}
                food={food}
                disabled={
                  form.disabled || ingredients.some((i) => i.foodId === food.id)
                }
                onPress={() => {
                  setIngredients([
                    ...ingredients,
                    {
                      ...ingredientFromFood(food.id, available, 100),
                      amount: '100',
                    },
                  ]);
                  setSearching(false);
                  setQuery('');
                }}
              />
            ))}
          </>
        ) : null}
      </Card>
      <Card>
        <Field
          label="Measured final recipe yield (g) / 0.1–1,000,000"
          value={yieldGrams}
          onChangeText={setYield}
          disabled={form.disabled}
        />
        <Field
          label="Number of servings / 0.1–10,000"
          value={servings}
          onChangeText={setServings}
          disabled={form.disabled}
        />
        <Text style={ui.body}>
          Use the final edible weight after cooking. A serving weighs yield ÷
          serving count. Cooking losses or added water are not guessed.
          Nutrition may be estimated.
        </Text>
      </Card>
      {preview ? (
        <Card>
          <Text style={ui.heading}>Review recipe nutrition</Text>
          <Text style={ui.label}>Whole recipe / known amounts</Text>
          <Nutrition values={preview.total.values} />
          {Object.values(preview.total.partial).some(Boolean) ? (
            <Text style={ui.body}>
              Incomplete: one or more ingredients have unknown nutrients. Known
              totals are subtotals; affected nutrients stay Unknown per serving
              and when logged.
            </Text>
          ) : null}
          <Text style={ui.label}>
            Per serving ({preview.servingGrams.toFixed(1)} g)
          </Text>
          <Nutrition values={preview.perServing} />
        </Card>
      ) : (
        <Text style={ui.body}>
          Add ingredients with valid quantities and set the yield to review
          nutrition before saving.
        </Text>
      )}
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
              : 'Confirm and save meal'
        }
        disabled={form.busy}
        onPress={() => {
          void form.submit(() => saveRecipe(original, build(), Boolean(item)));
        }}
      />
      {item ? (
        <Action
          variant="danger"
          label="Delete recipe"
          disabled={form.disabled}
          onPress={() => setConfirm(true)}
        />
      ) : null}
      <ConfirmDelete
        title="Delete recipe?"
        message="Existing diary entries stay unchanged. This recipe will leave search, recents and favourites."
        confirmLabel="Delete recipe"
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
