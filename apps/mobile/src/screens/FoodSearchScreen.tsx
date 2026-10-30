import { useLibrary } from '../state/LibraryProvider';
import {
  LibraryStatus,
  FavouriteButton,
  FoodChoice,
} from '../components/LibraryControls';
import {
  emptyLibrary,
  libraryFoods,
  browseFoods,
  portionGrams,
  foodOrigin,
  type LibraryFilter,
} from '../domain/library';
import { FoodImage } from '../components/FoodImage';
import { useCallback, useReducer, useRef, useState } from 'react';
import { randomUUID } from 'expo-crypto';
import { Action, Nutrition, useFoodStyles } from '../components/FoodControls';
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
import { Card, useUI } from '../components/dashboard';
import { foods } from '../data/foods';
import {
  meals,
  createDraft,
  foodDraftReducer,
  scaleNutrients,
} from '../domain/food';
import type { FoodNutrients } from '../domain/food';

export default function FoodSearchScreen() {
  const styles = useFoodStyles();
  const { ui, t } = useUI();
  const {
    meal,
    date: routeDate,
    foodId: routeFoodId,
  } = useLocalSearchParams<{
    meal?: string | string[];
    date?: string | string[];
    foodId?: string | string[];
  }>();
  const [date] = useState(() =>
    routeDate === undefined
      ? localDateKey()
      : validDateKey(routeDate)
        ? routeDate
        : null,
  );
  const diary = useDiary();
  const library = useLibrary();
  const [filter, setFilter] = useState<LibraryFilter>('All');
  const [quantityMode, setQuantityMode] = useState<'grams' | 'servings'>(
    'grams',
  );
  const available = libraryFoods(library.data ?? emptyLibrary(), foods);
  const [busy, setBusy] = useState(false);
  const [attempted, setAttempted] = useState(false);
  const saving = useRef(false);
  const pending = useRef<DiaryEntry | null>(null);
  const [saveError, setSaveError] = useState('');
  const [draft, dispatch] = useReducer(foodDraftReducer, meal, (value) => {
    const initial = createDraft(value);
    return typeof routeFoodId === 'string'
      ? foodDraftReducer(initial, { type: 'select', id: routeFoodId })
      : initial;
  });
  const [category, setCategory] = useState<string | null>(null);
  const categories = [...new Set(available.map((food) => food.category))];
  const selected = available.find((food) => food.id === draft.foodId);
  const matches = browseFoods(
    library.data ?? emptyLibrary(),
    foods,
    diary.entries ?? [],
    filter,
    draft.query,
  ).filter((food) => category === null || food.category === category);
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
  const grams = portionGrams(draft.grams, quantityMode, selected);
  let calculated: FoodNutrients | null = null;
  let error =
    grams === null ? 'Enter a positive quantity in the selected unit.' : '';
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
    if (draft.foodId !== id) setQuantityMode('grams');
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
            Food values are illustrative or user-entered estimates, not
            nutritional guidance. Entries are saved only on this device after
            confirmation.
          </Text>
          <LibraryStatus />
          {draft.detail ? (
            selected ? (
              <>
                <Card>
                  <FoodImage foodId={selected.id} prominent />
                  <Text accessibilityRole="header" style={ui.heading}>
                    {selected.name}
                  </Text>
                  <Text style={ui.label}>
                    {foodOrigin(selected)} / {selected.category} /{' '}
                    {selected.preparation}
                  </Text>
                  <Text style={ui.body}>
                    Reference values per {selected.referenceGrams} g edible
                    portion (estimate)
                  </Text>
                  <Nutrition values={selected.nutrients} />
                  <Text style={ui.body}>{selected.source}</Text>
                  <FavouriteButton
                    key={selected.id}
                    food={selected}
                    disabled={busy || attempted}
                  />
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
                  {selected.servingGrams ? (
                    <>
                      <Text style={ui.body}>
                        One defined serving = {selected.servingGrams.toFixed(2)}{' '}
                        g.
                      </Text>
                      <View style={ui.row}>
                        {(['grams', 'servings'] as const).map((mode) => (
                          <Pressable
                            key={mode}
                            accessibilityRole="radio"
                            accessibilityState={{
                              checked: quantityMode === mode,
                              disabled: busy || attempted,
                            }}
                            disabled={busy || attempted}
                            onPress={() => {
                              if (quantityMode === mode) return;
                              setQuantityMode(mode);
                              dispatch({
                                type: 'grams',
                                value: mode === 'grams' ? '100' : '1',
                              });
                            }}
                            style={[
                              styles.back,
                              {
                                backgroundColor:
                                  quantityMode === mode
                                    ? t.colors.selected
                                    : t.colors.surface,
                              },
                            ]}
                          >
                            <Text style={ui.label}>
                              {mode === 'grams' ? 'Grams' : 'Servings'}
                            </Text>
                          </Pressable>
                        ))}
                      </View>
                    </>
                  ) : null}
                  <Text style={ui.body}>Amount in {quantityMode}</Text>
                  <TextInput
                    selectionColor={t.colors.primary}
                    editable={!busy && !attempted}
                    accessibilityLabel={`Portion in ${quantityMode}`}
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
                        Calculated for {grams} g
                        {quantityMode === 'servings'
                          ? ` / ${draft.grams} servings`
                          : ''}{' '}
                        (estimate)
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
              <Action
                variant="secondary"
                label="My foods / create food or recipe"
                onPress={() =>
                  router.push({
                    pathname: '/my-foods',
                    params: {
                      ...(date ? { date } : {}),
                      ...(draft.meal ? { meal: draft.meal } : {}),
                    },
                  })
                }
              />
              <ScrollView
                horizontal
                showsHorizontalScrollIndicator={false}
                contentContainerStyle={{ gap: t.spacing.sm }}
              >
                {(
                  ['All', 'Favourites', 'Recent', 'Custom', 'Recipes'] as const
                ).map((value) => (
                  <Pressable
                    key={value}
                    accessibilityRole="button"
                    accessibilityState={{ selected: filter === value }}
                    onPress={() => {
                      setFilter(value);
                      setCategory(null);
                    }}
                    style={{
                      minHeight: 48,
                      paddingHorizontal: 16,
                      justifyContent: 'center',
                      borderRadius: 24,
                      backgroundColor:
                        filter === value ? t.colors.primary : t.colors.elevated,
                    }}
                  >
                    <Text
                      style={{
                        ...t.typography.label,
                        color:
                          filter === value ? t.colors.onPrimary : t.colors.text,
                      }}
                    >
                      {value}
                    </Text>
                  </Pressable>
                ))}
              </ScrollView>
              {filter === 'Recent' && diary.entries === null ? (
                <Text style={ui.body}>
                  Recent foods are unavailable until the diary loads. Return to
                  Diary to retry loading.
                </Text>
              ) : null}
              <ScrollView
                horizontal
                showsHorizontalScrollIndicator={false}
                contentContainerStyle={{ gap: t.spacing.sm }}
              >
                {[null, ...categories].map((item) => (
                  <Pressable
                    key={item ?? 'all'}
                    accessibilityRole="button"
                    accessibilityState={{ selected: category === item }}
                    onPress={() => setCategory(item)}
                    style={{
                      minHeight: 48,
                      paddingHorizontal: 20,
                      justifyContent: 'center',
                      borderRadius: 24,
                      backgroundColor:
                        category === item
                          ? t.colors.primary
                          : t.colors.elevated,
                    }}
                  >
                    <Text
                      style={{
                        ...t.typography.label,
                        color:
                          category === item
                            ? t.colors.onPrimary
                            : t.colors.text,
                      }}
                    >
                      {item ?? 'All foods'}
                    </Text>
                  </Pressable>
                ))}
              </ScrollView>
              <Text style={ui.body}>Search by food name or alias</Text>
              <TextInput
                selectionColor={t.colors.primary}
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
                    Current preview: {selected.name}, {draft.grams}{' '}
                    {quantityMode}. Retained while this flow is open.
                  </Text>
                  <Action
                    label="Review current selection"
                    onPress={() => select(selected.id)}
                  />
                </Card>
              ) : null}
              <Text accessibilityLiveRegion="polite" style={ui.label}>
                {draft.query.trim()
                  ? `${matches.length} matching foods`
                  : `${matches.length} foods${category ? ` / ${category}` : ''}`}
              </Text>
              {matches.length === 0 ? (
                <Card>
                  <Text style={ui.heading}>No foods found</Text>
                  <Text style={ui.body}>
                    Try All foods, a shorter name or another alias. Add
                    favourites from food details; recents appear after confirmed
                    diary saves. Create custom foods and recipes in My foods.
                  </Text>
                </Card>
              ) : (
                matches.map((food) => (
                  <FoodChoice
                    key={food.id}
                    food={food}
                    onPress={() => select(food.id)}
                  />
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
