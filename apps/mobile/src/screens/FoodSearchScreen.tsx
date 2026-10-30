import { useCallback, useReducer } from 'react';
import { router, useFocusEffect, useLocalSearchParams } from 'expo-router';
import {
  BackHandler,
  Keyboard,
  KeyboardAvoidingView,
  Platform,
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  View,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Card, ui } from '../components/dashboard';
import { foods } from '../data/foods';
import {
  createDraft,
  foodDraftReducer,
  formatNutrient,
  parseGrams,
  scaleNutrients,
  searchFoods,
} from '../domain/food';
import type { FoodNutrients } from '../domain/food';
import { theme as t } from '../theme/tokens';
function Action({
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
function Nutrition({ values }: { values: FoodNutrients }) {
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
export default function FoodSearchScreen() {
  const { meal } = useLocalSearchParams<{ meal?: string | string[] }>();
  const [draft, dispatch] = useReducer(foodDraftReducer, meal, createDraft);
  const selected = foods.find((food) => food.id === draft.foodId);
  const matches = searchFoods(foods, draft.query);
  const back = useCallback(() => {
    Keyboard.dismiss();
    if (draft.detail) dispatch({ type: 'back' });
    else if (router.canGoBack()) router.back();
    else router.replace('/');
  }, [draft.detail]);
  useFocusEffect(
    useCallback(() => {
      const subscription = BackHandler.addEventListener(
        'hardwareBackPress',
        () => {
          back();
          return true;
        },
      );
      return () => subscription.remove();
    }, [back]),
  );
  const grams = parseGrams(draft.grams);
  let calculated: FoodNutrients | null = null;
  let error =
    grams === null
      ? 'Enter a number greater than zero in grams, such as 100 or 125.5.'
      : '';
  if (selected && grams !== null) {
    try {
      calculated = scaleNutrients(selected.nutrients, grams);
    } catch {
      error =
        'This portion cannot be calculated. Enter a positive amount within the supported numeric range.';
    }
  }
  const select = (id: string) => {
    Keyboard.dismiss();
    dispatch({ type: 'select', id });
  };
  return (
    <SafeAreaView style={ui.page}>
      <View style={[ui.content, { paddingBottom: 0, gap: t.spacing.sm }]}>
        <Pressable
          accessibilityRole="button"
          accessibilityLabel={
            draft.detail ? 'Back to food search' : 'Back to dashboard or diary'
          }
          onPress={back}
          style={styles.back}
        >
          <Text style={ui.label}>
            {draft.detail ? '< Back to search' : '< Back'}
          </Text>
        </Pressable>
        <Text accessibilityRole="header" style={ui.title}>
          {draft.detail ? 'Food details' : 'Find food'}
        </Text>
        <Text style={ui.label}>
          {draft.meal ? `For ${draft.meal}` : 'Food preview - no meal selected'}
        </Text>
      </View>
      <KeyboardAvoidingView
        style={{ flex: 1 }}
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      >
        <ScrollView
          key={draft.detail ? 'detail' : 'search'}
          keyboardShouldPersistTaps="handled"
          keyboardDismissMode="on-drag"
          contentContainerStyle={[ui.content, { gap: t.spacing.md }]}
        >
          <Text style={ui.body}>
            ILLUSTRATIVE SAMPLE DATA. Preview only, not nutritional guidance.
            Nothing is saved to your diary.
          </Text>
          {draft.detail ? (
            selected ? (
              <>
                <Card>
                  <Text accessibilityRole="header" style={ui.heading}>
                    {selected.name}
                  </Text>
                  <Text style={ui.label}>
                    {selected.category} / {selected.preparation}
                  </Text>
                  <Text style={ui.body}>
                    Reference values per {selected.referenceGrams} g edible
                    portion (sample)
                  </Text>
                  <Nutrition values={selected.nutrients} />
                  <Text style={ui.body}>{selected.source}</Text>
                </Card>
                <Card>
                  <Text accessibilityRole="header" style={ui.heading}>
                    Your portion
                  </Text>
                  <Text style={ui.body}>Amount in grams</Text>
                  <TextInput
                    accessibilityLabel="Portion in grams"
                    accessibilityHint="Enter a positive decimal amount"
                    keyboardType="decimal-pad"
                    value={draft.grams}
                    onChangeText={(value) => dispatch({ type: 'grams', value })}
                    style={styles.input}
                  />
                  {error ? (
                    <Text
                      accessibilityRole="alert"
                      accessibilityLiveRegion="polite"
                      style={ui.body}
                    >
                      {error}
                    </Text>
                  ) : null}
                  {calculated ? (
                    <>
                      <Text style={ui.label}>
                        Calculated for {draft.grams.trim()} g (sample)
                      </Text>
                      <Nutrition values={calculated} />
                    </>
                  ) : null}
                  <Action
                    label="Confirm preview selection"
                    disabled={!calculated}
                    onPress={() => {
                      Keyboard.dismiss();
                      dispatch({ type: 'confirm' });
                    }}
                  />
                </Card>
                {draft.confirmed && calculated ? (
                  <Card>
                    <Text
                      accessibilityRole="header"
                      accessibilityLiveRegion="polite"
                      style={ui.heading}
                    >
                      Preview confirmed
                    </Text>
                    <Text style={ui.body}>
                      {selected.name}, {draft.grams.trim()} g
                      {draft.meal ? ` for ${draft.meal}` : ''}. This is a
                      temporary sample selection, not a logged meal. Dashboard
                      totals are unchanged.
                    </Text>
                    <Action label="Back to search" onPress={back} />
                  </Card>
                ) : null}
              </>
            ) : (
              <Card>
                <Text accessibilityRole="alert" style={ui.body}>
                  This food is unavailable.
                </Text>
                <Action label="Back to search" onPress={back} />
              </Card>
            )
          ) : (
            <>
              <Text style={ui.body}>Search by food name or alias</Text>
              <TextInput
                accessibilityLabel="Search foods"
                placeholder="Try rice, chapati or dahi"
                placeholderTextColor={t.colors.muted}
                value={draft.query}
                onChangeText={(value) => dispatch({ type: 'query', value })}
                autoCapitalize="none"
                autoCorrect={false}
                returnKeyType="search"
                onSubmitEditing={Keyboard.dismiss}
                style={styles.input}
              />
              {draft.query ? (
                <Pressable
                  accessibilityRole="button"
                  onPress={() => dispatch({ type: 'query', value: '' })}
                  style={styles.back}
                >
                  <Text style={ui.label}>Clear search</Text>
                </Pressable>
              ) : null}
              {selected ? (
                <Card>
                  <Text style={ui.body}>
                    Current preview: {selected.name}, {draft.grams} g. Retained
                    while this flow is open.
                  </Text>
                  <Action
                    label="Review current selection"
                    onPress={() => select(selected.id)}
                  />
                </Card>
              ) : null}
              <Text accessibilityLiveRegion="polite" style={ui.label}>
                {draft.query.trim()
                  ? `${matches.length} matching sample foods`
                  : 'Browse all sample foods'}
              </Text>
              {matches.length === 0 ? (
                <Card>
                  <Text style={ui.heading}>No foods found</Text>
                  <Text style={ui.body}>
                    Try a shorter name or another alias. This development
                    catalog contains only 12 foods.
                  </Text>
                </Card>
              ) : (
                matches.map((food) => (
                  <Pressable
                    key={food.id}
                    accessibilityRole="button"
                    accessibilityLabel={`${food.name}, ${food.preparation}, illustrative sample. View details`}
                    onPress={() => select(food.id)}
                    style={({ pressed }) => [
                      ui.card,
                      { opacity: pressed ? 0.8 : 1 },
                    ]}
                  >
                    <Text style={ui.heading}>{food.name}</Text>
                    <Text style={ui.label}>
                      {food.preparation} /{' '}
                      {formatNutrient(food.nutrients.calories, 'kcal')} per 100
                      g
                    </Text>
                    <Text style={ui.body}>
                      Illustrative sample - view details
                    </Text>
                  </Pressable>
                ))
              )}
              <Text style={ui.body}>
                Leaving food search clears this temporary selection. Search
                works offline; saving meals is a later stage.
              </Text>
            </>
          )}
        </ScrollView>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}
const styles = StyleSheet.create({
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
