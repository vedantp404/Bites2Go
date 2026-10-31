import { memo, useCallback, useRef, useState } from 'react';
import { BackHandler, Keyboard, Text, View, Pressable } from 'react-native';
import { router, useFocusEffect } from 'expo-router';
import { useLibrary } from '../state/LibraryProvider';
import type { Library } from '../domain/library';
import { setFavourite, foodOrigin } from '../domain/library';
import type { Food } from '../domain/food';
import { unifiedFoods } from '../data/unifiedFoods';
import { Card, useUI } from './dashboard';
import { Action } from './FoodControls';
export function LibraryStatus() {
  const { data, error, reload } = useLibrary();
  const { ui, t } = useUI();
  return data ? null : (
    <Card>
      <Text
        accessibilityRole={error ? 'alert' : undefined}
        style={[ui.body, { color: error ? t.colors.error : t.colors.muted }]}
      >
        {error || 'Loading your food library...'}
      </Text>
      {error ? <Action label="Retry food library" onPress={reload} /> : null}
    </Card>
  );
}
export const FoodChoice = memo(function FoodChoice({
  food,
  onPress,
  disabled = false,
}: {
  food: Food;
  onPress: () => void;
  disabled?: boolean;
}) {
  const { ui, t } = useUI();
  const servingDesc =
    food.commonServings?.[0]?.description ??
    (food.servingGrams ? `${food.servingGrams}g` : '100g');
  const cal =
    food.nutrients.calories != null
      ? `${Math.round(food.nutrients.calories)} kcal`
      : 'Cal unknown';
  const p =
    food.nutrients.protein != null ? `${food.nutrients.protein}g P` : '-';
  const c = food.nutrients.carbs != null ? `${food.nutrients.carbs}g C` : '-';
  const f = food.nutrients.fat != null ? `${food.nutrients.fat}g F` : '-';

  return (
    <Pressable
      accessibilityRole="button"
      accessibilityLabel={`${food.name}, ${servingDesc}, ${cal}, ${p}, ${c}, ${f}. ${foodOrigin(food)}. Select food`}
      accessibilityState={{ disabled }}
      disabled={disabled}
      onPress={onPress}
      style={[
        ui.card,
        {
          minHeight: 64,
          paddingVertical: t.spacing.sm,
          paddingHorizontal: t.spacing.md,
          gap: 4,
        },
      ]}
    >
      <View
        style={{
          flexDirection: 'row',
          justifyContent: 'space-between',
          alignItems: 'baseline',
          gap: t.spacing.sm,
        }}
      >
        <Text style={[ui.heading, { flex: 1 }]} numberOfLines={1}>
          {food.name}
        </Text>
        <Text
          style={{
            ...t.typography.body,
            fontWeight: '700',
            color: t.colors.primary,
          }}
        >
          {cal}
        </Text>
      </View>
      <View
        style={{
          flexDirection: 'row',
          justifyContent: 'space-between',
          alignItems: 'center',
          gap: t.spacing.sm,
        }}
      >
        <Text style={[ui.label, { flex: 1 }]} numberOfLines={1}>
          {servingDesc} · {foodOrigin(food)}
        </Text>
        <Text style={[ui.label, { color: t.colors.secondary }]}>
          {p} · {c} · {f}
        </Text>
      </View>
    </Pressable>
  );
});
export function FavouriteButton({
  food,
  disabled = false,
}: {
  food: Food;
  disabled?: boolean;
}) {
  const library = useLibrary();
  const { ui, t } = useUI();
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const locked = useRef(false);
  const pending = useRef<{ next: Library; original: Library } | null>(null);
  const [attempted, setAttempted] = useState(false);
  if (!library.data) return null;
  const favourite = library.data.favourites.includes(food.id);
  async function save() {
    if (locked.current || !library.data) return;
    locked.current = true;
    setBusy(true);
    setError('');
    try {
      pending.current ??= {
        next: setFavourite(library.data, food.id, !favourite, unifiedFoods),
        original: library.data,
      };
      setAttempted(true);
      await library.save(pending.current.next, pending.current.original);
      pending.current = null;
      setAttempted(false);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Could not save favourite.');
    } finally {
      locked.current = false;
      setBusy(false);
    }
  }
  return (
    <View style={{ gap: 8 }}>
      <Action
        variant="secondary"
        disabled={disabled || busy}
        label={
          busy
            ? 'Saving favourite...'
            : attempted
              ? 'Retry favourite change'
              : favourite
                ? 'Remove favourite'
                : 'Add favourite'
        }
        onPress={() => {
          void save();
        }}
      />
      {error ? (
        <>
          <Text
            accessibilityRole="alert"
            style={[ui.body, { color: t.colors.error }]}
          >
            {error}
          </Text>
          <Action
            variant="secondary"
            label="Reload favourites"
            onPress={() => {
              pending.current = null;
              setAttempted(false);
              setError('');
              library.reload();
            }}
          />
        </>
      ) : null}
    </View>
  );
}
export function useLibraryForm(original: Library) {
  const library = useLibrary();
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const [attempted, setAttempted] = useState(false);
  const pending = useRef<Library | null>(null);
  const locked = useRef(false);
  const back = useCallback(() => {
    if (locked.current) return;
    Keyboard.dismiss();
    if (pending.current) library.reload();
    if (router.canGoBack()) router.back();
    else router.replace('/my-foods');
  }, [library]);
  useFocusEffect(
    useCallback(() => {
      const sub = BackHandler.addEventListener('hardwareBackPress', () => {
        back();
        return true;
      });
      return () => sub.remove();
    }, [back]),
  );
  async function submit(build: () => Library) {
    if (locked.current) return;
    locked.current = true;
    setBusy(true);
    setError('');
    Keyboard.dismiss();
    try {
      pending.current ??= build();
      setAttempted(true);
      await library.save(pending.current, original);
      pending.current = null;
      if (router.canGoBack()) router.back();
      else router.replace('/my-foods');
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Save failed. Retry.');
    } finally {
      locked.current = false;
      setBusy(false);
    }
  }
  return {
    busy,
    error,
    back,
    submit,
    disabled: busy || attempted,
    pending: attempted,
  };
}
