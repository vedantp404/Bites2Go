import { Text } from 'react-native';
import { router, useLocalSearchParams } from 'expo-router';
import { Card, useUI } from '../components/dashboard';
import { Action } from '../components/FoodControls';
import { HealthPage } from '../components/HealthControls';
import { FoodChoice, LibraryStatus } from '../components/LibraryControls';
import { useLibrary } from '../state/LibraryProvider';
import { customAsFood, recipeAsFood } from '../domain/library';
import { localDateKey, validDateKey } from '../domain/diary';
import { mealContext } from '../domain/food';
export default function MyFoodsScreen() {
  const { data, reload } = useLibrary();
  const { ui } = useUI();
  const params = useLocalSearchParams<{ date?: string; meal?: string }>();
  const date = validDateKey(params.date) ? params.date : localDateKey();
  const meal = mealContext(params.meal);
  return (
    <HealthPage title="My foods and recipes">
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
          <Action
            label="Create custom food"
            onPress={() => router.push('/custom-food')}
          />
          <Action
            label="Create recipe"
            onPress={() => router.push('/recipe')}
          />
          <Text style={ui.body}>
            Your food values may be estimates. Library changes never rewrite
            already logged nutrition.
          </Text>
          {[
            ...data.customFoods.map(customAsFood),
            ...data.recipes.map(recipeAsFood),
          ].map((food) => (
            <Card key={food.id}>
              <FoodChoice
                food={food}
                onPress={() =>
                  router.push({
                    pathname: '/food-search',
                    params: {
                      foodId: food.id,
                      date,
                      ...(meal ? { meal } : {}),
                    },
                  })
                }
              />
              <Action
                variant="secondary"
                label={`Edit or delete ${food.name}`}
                onPress={() =>
                  router.push({
                    pathname: food.id.startsWith('custom:')
                      ? '/custom-food'
                      : '/recipe',
                    params: { id: food.id },
                  })
                }
              />
            </Card>
          ))}
          {!data.customFoods.length && !data.recipes.length ? (
            <Text style={ui.body}>
              No custom foods or recipes yet. Create one above, then select it
              to review and log.
            </Text>
          ) : null}
          <Action variant="secondary" label="Reload library" onPress={reload} />
        </>
      ) : null}
    </HealthPage>
  );
}
