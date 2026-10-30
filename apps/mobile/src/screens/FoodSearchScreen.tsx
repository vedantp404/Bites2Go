import { useCallback, useReducer, useRef, useState } from 'react';
import { randomUUID } from 'expo-crypto';
import { Action, Nutrition, styles } from '../components/FoodControls';
import { useDiary } from '../state/DiaryProvider';
import { createEntry, localDateKey, validDateKey } from '../domain/diary';
import type { DiaryEntry } from '../domain/diary';
import { router, useFocusEffect, useLocalSearchParams } from 'expo-router';
import {
  BackHandler,
  Keyboard,
  KeyboardAvoidingView,
  Platform,
  Pressable,
  ScrollView,
  Text,
  TextInput,
  View,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Card, ui } from '../components/dashboard';
import { foods } from '../data/foods';
import {
  meals,
  createDraft,
  foodDraftReducer,
  formatNutrient,
  parseGrams,
  scaleNutrients,
  searchFoods,
} from '../domain/food';
import type { FoodNutrients } from '../domain/food';
import { theme as t } from '../theme/tokens';
export default function FoodSearchScreen() {
  const { meal, date: routeDate } = useLocalSearchParams<{
    meal?: string | string[];
    date?: string | string[];
  }>();
  const [date] = useState(() =>
    routeDate === undefined
      ? localDateKey()
      : validDateKey(routeDate)
        ? routeDate
        : null,
  );
  const diary = useDiary();
  const [busy, setBusy] = useState(false);
  const [attempted, setAttempted] = useState(false);
  const saving = useRef(false);
  const pending = useRef<DiaryEntry | null>(null);
  const [saveError, setSaveError] = useState('');
  const [draft, dispatch] = useReducer(foodDraftReducer, meal, createDraft);
  const selected = foods.find((food) => food.id === draft.foodId);
  const matches = searchFoods(foods, draft.query);
  const back = useCallback(() => {
    if (saving.current) return;
    Keyboard.dismiss();
    if (draft.detail && !pending.current) dispatch({ type: 'back' });
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
  async function save() {
    if (
      saving.current ||
      !selected ||
      !draft.meal ||
      !date ||
      date > localDateKey() ||
      diary.entries === null ||
      !calculated ||
      grams === null
    )
      return;
    saving.current = true;
    setBusy(true);
    setSaveError('');
    Keyboard.dismiss();
    try {
      setAttempted(true);
      pending.current ??= createEntry(
        selected,
        draft.meal,
        date,
        grams,
        randomUUID(),
        new Date().toISOString(),
      );
      await diary.save(pending.current);
      if (router.canGoBack()) router.back();
      else router.replace('/diary');
    } catch (error) {
      setSaveError(
        error instanceof Error
          ? error.message
          : 'Saving failed. Retry the same entry.',
      );
    } finally {
      saving.current = false;
      setBusy(false);
    }
  }
  return (
    <SafeAreaView style={ui.page}>
      <View style={[ui.content, { paddingBottom: 0, gap: t.spacing.sm }]}>
        <Pressable
          accessibilityRole="button"
          accessibilityLabel={
            draft.detail && !attempted
              ? 'Back to food search'
              : 'Back to dashboard or diary'
          }
          onPress={back}
          style={styles.back}
        >
          <Text style={ui.label}>
            {draft.detail && !attempted ? '< Back to search' : '< Back'}
          </Text>
        </Pressable>
        <Text accessibilityRole="header" style={ui.title}>
          {draft.detail ? 'Food details' : 'Find food'}
        </Text>
        <Text style={ui.label}>
          {date ?? 'Invalid date'} / {draft.meal ?? 'Choose a meal below'}
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
            ILLUSTRATIVE FOOD VALUES, not nutritional guidance. Entries are
            saved only on this device after confirmation.
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
                  <Text style={ui.label}>Meal</Text>
                  <View style={ui.row}>
                    {meals.map((meal) => (
                      <Pressable
                        key={meal}
                        accessibilityRole="radio"
                        accessibilityState={{
                          checked: draft.meal === meal,
                          disabled: busy || attempted,
                        }}
                        disabled={busy || attempted}
                        style={[
                          styles.back,
                          {
                            backgroundColor:
                              draft.meal === meal
                                ? t.colors.accent
                                : t.colors.surface,
                          },
                        ]}
                        onPress={() => dispatch({ type: 'meal', value: meal })}
                      >
                        <Text style={ui.label}>{meal}</Text>
                      </Pressable>
                    ))}
                  </View>
                  <Text style={ui.body}>Amount in grams</Text>
                  <TextInput
                    editable={!busy && !attempted}
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
                  {saveError ? (
                    <Text accessibilityRole="alert" style={ui.body}>
                      {saveError}
                    </Text>
                  ) : null}
                  {diary.entries === null ? (
                    <Text style={ui.body}>
                      Diary is not available. Return and retry loading it before
                      saving.
                    </Text>
                  ) : null}
                  {!date || date > localDateKey() ? (
                    <Text style={ui.body}>
                      Choose a valid diary date no later than today.
                    </Text>
                  ) : null}
                  <Action
                    label={
                      busy
                        ? 'Saving...'
                        : attempted
                          ? 'Retry saving this entry'
                          : 'Confirm and save food'
                    }
                    disabled={
                      busy ||
                      !calculated ||
                      !draft.meal ||
                      !date ||
                      date > localDateKey() ||
                      diary.entries === null
                    }
                    onPress={() => {
                      void save();
                    }}
                  />
                </Card>
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
                works offline. Only confirmed entries are saved.
              </Text>
            </>
          )}
        </ScrollView>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}
