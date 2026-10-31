import { useCallback, useMemo } from 'react';
import { Text } from 'react-native';
import { router, useLocalSearchParams } from 'expo-router';
import { Card, useUI } from '../components/dashboard';
import { Action, Nutrition } from '../components/FoodControls';
import { HealthPage } from '../components/HealthControls';
import { FoodChoice, LibraryStatus } from '../components/LibraryControls';
import { useLibrary } from '../state/LibraryProvider';
import { customAsFood, recipeNutrition } from '../domain/library';
import { localDateKey, validDateKey } from '../domain/diary';
import { mealContext } from '../domain/food';
export default function MyFoodsScreen() {
  const { data, reload } = useLibrary();
  const { ui } = useUI();
  const params = useLocalSearchParams<{ date?: string; meal?: string }>();
  const date = validDateKey(params.date) ? params.date : localDateKey();
  const meal = mealContext(params.meal);
  const log = useCallback(
    (foodId: string) =>
      router.push({
        pathname: '/food-search',
        params: { foodId, date, ...(meal ? { meal } : {}) },
      }),
    [date, meal],
  );
  const customFoods = useMemo(
    () => data?.customFoods.map(customAsFood) ?? [],
    [data?.customFoods],
  );
  return (
    <HealthPage title="My Meals & Recipes">
      <Action
        variant="secondary"
        label="Back"
        onPress={() =>
          router.canGoBack() ? router.back() : router.replace('/profile')
        }
      />
      <LibraryStatus />
      {data ? (
        <>
          <Text style={ui.body}>
            Save your own ingredient combinations, then log a whole meal in one
            entry. Values come from saved ingredient data and may be estimates.
            Library changes never rewrite already logged nutrition.
          </Text>
          <Text accessibilityRole="header" style={ui.heading}>
            My Meals
          </Text>
          <Action
            label="Create meal / recipe"
            onPress={() => router.push('/recipe')}
          />
          {!data.recipes.length ? (
            <Text style={ui.body}>
              No saved meals yet. Create a meal with ingredients and quantities,
              define its servings, then use Log Meal whenever you eat it.
            </Text>
          ) : null}
          {data.recipes.map((recipe) => {
            const nutrition = recipeNutrition(recipe);
            return (
              <Card key={recipe.id}>
                <Text accessibilityRole="header" style={ui.heading}>
                  {recipe.name}
                </Text>
                {recipe.description ? (
                  <Text style={ui.body}>{recipe.description}</Text>
                ) : null}
                <Text style={ui.label}>
                  Makes {recipe.servings} servings / {recipe.yieldGrams} g total
                </Text>
                <Text style={ui.label}>Ingredients for the whole meal</Text>
                {recipe.ingredients.map((ingredient) => (
                  <Text key={ingredient.foodId} style={ui.body}>
                    {ingredient.name}: {ingredient.grams} g
                  </Text>
                ))}
                <Text style={ui.label}>Whole meal / known amounts</Text>
                <Nutrition values={nutrition.total.values} />
                {Object.values(nutrition.total.partial).some(Boolean) ? (
                  <Text style={ui.body}>
                    Incomplete nutrition: known totals are subtotals. Missing
                    nutrients remain Unknown per serving and when logged.
                  </Text>
                ) : null}
                <Text style={ui.label}>
                  Per serving ({nutrition.servingGrams.toFixed(1)} g)
                </Text>
                <Nutrition values={nutrition.perServing} />
                <Action
                  label={`Log Meal: ${recipe.name}`}
                  onPress={() => log(recipe.id)}
                />
                <Action
                  variant="secondary"
                  label={`Edit or delete ${recipe.name}`}
                  onPress={() =>
                    router.push({
                      pathname: '/recipe',
                      params: { id: recipe.id },
                    })
                  }
                />
              </Card>
            );
          })}
          <Text accessibilityRole="header" style={ui.heading}>
            My custom foods
          </Text>
          <Action
            label="Create custom food"
            onPress={() => router.push('/custom-food')}
          />
          <Text style={ui.body}>
            Missing an ingredient? Add its serving weight and nutrition from
            your own food label here, then use it in a meal.
          </Text>
          {customFoods.map((food) => (
            <Card key={food.id}>
              <FoodChoice food={food} onPress={() => log(food.id)} />
              <Action
                variant="secondary"
                label={`Edit or delete ${food.name}`}
                onPress={() =>
                  router.push({
                    pathname: '/custom-food',
                    params: { id: food.id },
                  })
                }
              />
            </Card>
          ))}
          {!data.customFoods.length ? (
            <Text style={ui.body}>No custom foods yet.</Text>
          ) : null}
          <Action variant="secondary" label="Reload library" onPress={reload} />
        </>
      ) : null}
    </HealthPage>
  );
}
