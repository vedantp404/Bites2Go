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
import {
  memo,
  useCallback,
  useEffect,
  useMemo,
  useReducer,
  useRef,
  useState,
} from 'react';
import { randomUUID } from 'expo-crypto';
import { Action, Nutrition, useFoodStyles } from '../components/FoodControls';
import { AIFoodScannerModal } from '../components/AIFoodScannerModal';
import { useDiary } from '../state/DiaryProvider';
import { createEntry, localDateKey, validDateKey } from '../domain/diary';
import type { DiaryEntry } from '../domain/diary';
import { router, useFocusEffect, useLocalSearchParams } from 'expo-router';
import {
  BackHandler,
  FlatList,
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
import { unifiedFoods } from '../data/unifiedFoods';
import {
  meals,
  createDraft,
  defaultFoodPortion,
  foodDraftReducer,
  scaleNutrients,
  type Food,
  type FoodNutrients,
} from '../domain/food';

export type SearchHeaderProps = {
  ui: ReturnType<typeof useUI>['ui'];
  t: ReturnType<typeof useUI>['t'];
  styles: ReturnType<typeof useFoodStyles>;
  queryInput: string;
  onChangeQueryInput: (text: string) => void;
  onClearQueryInput: () => void;
  filter: LibraryFilter;
  onSelectFilter: (filter: LibraryFilter) => void;
  category: string | null;
  onSelectCategory: (category: string | null) => void;
  categories: string[];
  selected?: Food;
  draftGrams: string;
  quantityMode: 'grams' | 'servings';
  onReviewSelected: (id: string) => void;
  matchesCount: number;
  draftQuery: string;
  diaryEntriesUnavailable: boolean;
  onOpenAiScanner: () => void;
  onOpenMyFoods: () => void;
};

export const SearchHeader = memo(function SearchHeader({
  ui,
  t,
  styles,
  queryInput,
  onChangeQueryInput,
  onClearQueryInput,
  filter,
  onSelectFilter,
  category,
  onSelectCategory,
  categories,
  selected,
  draftGrams,
  quantityMode,
  onReviewSelected,
  matchesCount,
  draftQuery,
  diaryEntriesUnavailable,
  onOpenAiScanner,
  onOpenMyFoods,
}: SearchHeaderProps) {
  return (
    <View style={{ gap: t.spacing.md }}>
      <Text style={ui.body}>
        Food values are illustrative or user-entered estimates, not nutritional
        guidance. Entries are saved only on this device after confirmation.
      </Text>
      <LibraryStatus />
      <Action
        variant="primary"
        label="Scan Meal with Gemini AI"
        onPress={onOpenAiScanner}
      />
      <Action
        variant="secondary"
        label="My Meals & Recipes / custom foods"
        onPress={onOpenMyFoods}
      />
      <ScrollView
        horizontal
        showsHorizontalScrollIndicator={false}
        contentContainerStyle={{ gap: t.spacing.sm }}
      >
        {(['All', 'Favourites', 'Recent', 'Custom', 'Recipes'] as const).map(
          (value) => (
            <Pressable
              key={value}
              accessibilityRole="button"
              accessibilityState={{ selected: filter === value }}
              onPress={() => onSelectFilter(value)}
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
                  color: filter === value ? t.colors.onPrimary : t.colors.text,
                }}
              >
                {value}
              </Text>
            </Pressable>
          ),
        )}
      </ScrollView>
      {filter === 'Recent' && diaryEntriesUnavailable ? (
        <Text style={ui.body}>
          Recent foods are unavailable until the diary loads. Return to Diary to
          retry loading.
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
            onPress={() => onSelectCategory(item)}
            style={{
              minHeight: 48,
              paddingHorizontal: 20,
              justifyContent: 'center',
              borderRadius: 24,
              backgroundColor:
                category === item ? t.colors.primary : t.colors.elevated,
            }}
          >
            <Text
              style={{
                ...t.typography.label,
                color: category === item ? t.colors.onPrimary : t.colors.text,
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
        value={queryInput}
        onChangeText={onChangeQueryInput}
        autoCapitalize="none"
        autoCorrect={false}
        returnKeyType="search"
        onSubmitEditing={Keyboard.dismiss}
        style={styles.input}
      />
      {queryInput ? (
        <Pressable
          accessibilityRole="button"
          onPress={onClearQueryInput}
          style={styles.back}
        >
          <Text style={ui.label}>Clear search</Text>
        </Pressable>
      ) : null}
      {selected ? (
        <Card>
          <Text style={ui.body}>
            Current preview: {selected.name}, {draftGrams} {quantityMode}.
            Retained while this flow is open.
          </Text>
          <Action
            label="Review current selection"
            onPress={() => onReviewSelected(selected.id)}
          />
        </Card>
      ) : null}
      <Text accessibilityLiveRegion="polite" style={ui.label}>
        {draftQuery.trim()
          ? `${matchesCount} matching foods`
          : `${matchesCount} foods${category ? ` / ${category}` : ''}`}
      </Text>
    </View>
  );
});

const BASE_CATEGORIES: string[] = Array.from(
  new Set(unifiedFoods.map((f) => f.category)),
);
const INITIAL_PAGE_SIZE = 40;
const PAGE_INCREMENT = 40;

export interface FoodSearchRowProps {
  food: Food;
  onSelect: (id: string) => void;
}

export const FoodSearchRow = memo(function FoodSearchRow({
  food,
  onSelect,
}: FoodSearchRowProps) {
  const handlePress = useCallback(() => {
    onSelect(food.id);
  }, [food.id, onSelect]);

  return <FoodChoice food={food} onPress={handlePress} />;
});

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
    () =>
      defaultFoodPortion(typeof routeFoodId === 'string' ? routeFoodId : null)
        .mode,
  );
  const available = useMemo(
    () => libraryFoods(library.data ?? emptyLibrary(), unifiedFoods),
    [library.data],
  );
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
  const [queryInput, setQueryInput] = useState(draft.query);
  const [category, setCategory] = useState<string | null>(null);
  const [aiScannerOpen, setAiScannerOpen] = useState(false);

  // Debounce search query input to prevent UI thread lockups during typing
  useEffect(() => {
    const timer = setTimeout(() => {
      if (draft.query !== queryInput) {
        dispatch({ type: 'query', value: queryInput });
      }
    }, 120);
    return () => clearTimeout(timer);
  }, [queryInput, draft.query]);

  const categories = useMemo(() => {
    if (!library.data?.customFoods.length && !library.data?.recipes.length) {
      return BASE_CATEGORIES;
    }
    const set = new Set(BASE_CATEGORIES);
    for (const food of available) {
      if (food.category) set.add(food.category);
    }
    return Array.from(set);
  }, [available, library.data]);
  const selected = useMemo(
    () => available.find((food) => food.id === draft.foodId),
    [available, draft.foodId],
  );
  const matches = useMemo(() => {
    const list = browseFoods(
      library.data ?? emptyLibrary(),
      unifiedFoods,
      diary.entries ?? [],
      filter,
      draft.query,
    );
    return category === null
      ? list
      : list.filter((food) => food.category === category);
  }, [library.data, diary.entries, filter, draft.query, category]);

  const [displayLimit, setDisplayLimit] = useState(INITIAL_PAGE_SIZE);
  const [prevSearchKey, setPrevSearchKey] = useState('');

  // Reset pagination synchronously when search parameters change (no cascading render)
  const searchKey = `${draft.query}|${category ?? ''}|${filter}`;
  if (prevSearchKey !== searchKey) {
    setPrevSearchKey(searchKey);
    setDisplayLimit(INITIAL_PAGE_SIZE);
  }

  const displayedFoods = useMemo(() => {
    if (matches.length <= INITIAL_PAGE_SIZE) return matches;
    return matches.slice(0, displayLimit);
  }, [matches, displayLimit]);

  const handleEndReached = useCallback(() => {
    setDisplayLimit((prev) => {
      if (prev >= matches.length) return prev;
      return Math.min(prev + PAGE_INCREMENT, matches.length);
    });
  }, [matches.length]);

  const back = useCallback(() => {
    if (saving.current) return;
    Keyboard.dismiss();
    if (draft.detail && !pending.current) dispatch({ type: 'back' });
    else {
      // A write may have succeeded before its acknowledgement failed.
      if (pending.current) diary.reload();
      if (router.canGoBack()) router.back();
      else router.replace('/');
    }
  }, [draft.detail, diary]);
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

  const draftFoodIdRef = useRef(draft.foodId);
  useEffect(() => {
    draftFoodIdRef.current = draft.foodId;
  }, [draft.foodId]);

  const select = useCallback((id: string) => {
    Keyboard.dismiss();
    if (draftFoodIdRef.current !== id) {
      setQuantityMode(defaultFoodPortion(id).mode);
    }
    dispatch({ type: 'select', id });
  }, []);

  const handleClearQuery = useCallback(() => {
    setQueryInput('');
    dispatch({ type: 'query', value: '' });
  }, []);

  const handleSelectFilter = useCallback((value: LibraryFilter) => {
    setFilter(value);
    setCategory(null);
  }, []);

  const handleOpenAiScanner = useCallback(() => {
    setAiScannerOpen(true);
  }, []);

  const handleOpenMyFoods = useCallback(() => {
    router.push({
      pathname: '/my-foods',
      params: {
        ...(date ? { date } : {}),
        ...(draft.meal ? { meal: draft.meal } : {}),
      },
    });
  }, [date, draft.meal]);

  const renderItem = useCallback(
    ({ item }: { item: Food }) => (
      <FoodSearchRow food={item} onSelect={select} />
    ),
    [select],
  );

  const keyExtractor = useCallback((item: Food) => item.id, []);
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
          {draft.detail
            ? selected?.id.startsWith('recipe:')
              ? 'Log Meal'
              : 'Food details'
            : 'Find food'}
        </Text>
        <Text style={ui.label}>
          {date ?? 'Invalid date'} / {draft.meal ?? 'Choose a meal below'}
        </Text>
      </View>
      <KeyboardAvoidingView
        style={{ flex: 1 }}
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      >
        {draft.detail ? (
          <ScrollView
            key="detail"
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
            {selected ? (
              <>
                <Card>
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
                  {selected.id.startsWith('recipe:') ? (
                    <Text style={ui.body}>
                      Log this whole meal as one diary entry. Choose 0.5, 1, 2
                      or another positive number of servings below. Later recipe
                      changes will not change this logged nutrition.
                    </Text>
                  ) : null}
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
                  {selected.commonServings &&
                  selected.commonServings.length > 0 ? (
                    <>
                      <Text style={ui.label}>Suggested portions</Text>
                      <View
                        style={[
                          ui.row,
                          { flexWrap: 'wrap', gap: t.spacing.xs },
                        ]}
                      >
                        {selected.commonServings.map((serving, index) => (
                          <Pressable
                            key={index}
                            accessibilityRole="button"
                            accessibilityLabel={`Select portion: ${serving.description}`}
                            disabled={busy || attempted}
                            onPress={() => {
                              setQuantityMode('grams');
                              dispatch({
                                type: 'grams',
                                value: String(serving.grams),
                              });
                            }}
                            style={[
                              styles.back,
                              {
                                backgroundColor:
                                  quantityMode === 'grams' &&
                                  draft.grams === String(serving.grams)
                                    ? t.colors.accent
                                    : t.colors.surface,
                              },
                            ]}
                          >
                            <Text style={ui.label}>{serving.description}</Text>
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
                          : selected.id.startsWith('recipe:')
                            ? 'Confirm and Log Meal'
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
            )}
          </ScrollView>
        ) : (
          <FlatList
            key="search"
            data={displayedFoods}
            keyExtractor={keyExtractor}
            renderItem={renderItem}
            initialNumToRender={10}
            maxToRenderPerBatch={10}
            windowSize={5}
            onEndReached={handleEndReached}
            onEndReachedThreshold={0.5}
            keyboardShouldPersistTaps="handled"
            keyboardDismissMode="on-drag"
            contentContainerStyle={[ui.content, { gap: t.spacing.sm }]}
            ListHeaderComponent={
              <SearchHeader
                ui={ui}
                t={t}
                styles={styles}
                queryInput={queryInput}
                onChangeQueryInput={setQueryInput}
                onClearQueryInput={handleClearQuery}
                filter={filter}
                onSelectFilter={handleSelectFilter}
                category={category}
                onSelectCategory={setCategory}
                categories={categories}
                selected={selected}
                draftGrams={draft.grams}
                quantityMode={quantityMode}
                onReviewSelected={select}
                matchesCount={matches.length}
                draftQuery={draft.query}
                diaryEntriesUnavailable={diary.entries === null}
                onOpenAiScanner={handleOpenAiScanner}
                onOpenMyFoods={handleOpenMyFoods}
              />
            }
            ListEmptyComponent={
              <Card>
                <Text style={ui.heading}>No foods found</Text>
                <Text style={ui.body}>
                  Try All foods, a shorter name or another alias. Add favourites
                  from food details; recents appear after confirmed diary saves.
                  Create custom foods and recipes in My foods.
                </Text>
              </Card>
            }
            ListFooterComponent={
              <View
                style={{ paddingVertical: t.spacing.md, gap: t.spacing.xs }}
              >
                {displayedFoods.length < matches.length ? (
                  <Text style={[ui.label, { textAlign: 'center' }]}>
                    Showing top {displayedFoods.length} of {matches.length}{' '}
                    foods. Scroll to load more.
                  </Text>
                ) : null}
                <Text style={ui.body}>
                  Leaving food search clears this temporary selection. Search
                  works offline. Only confirmed entries are saved.
                </Text>
              </View>
            }
          />
        )}
      </KeyboardAvoidingView>
      <AIFoodScannerModal
        visible={aiScannerOpen}
        meal={draft.meal || 'Lunch'}
        date={date}
        onClose={() => setAiScannerOpen(false)}
        onSuccess={() => {
          setAiScannerOpen(false);
          router.back();
        }}
      />
    </SafeAreaView>
  );
}
