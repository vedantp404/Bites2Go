import { Text, View, Pressable } from 'react-native';
import { router } from 'expo-router';
import { AddFood, Card, NutrientProgress, ui } from './dashboard';
import { Action } from './FoodControls';
import { CalorieRing, AppIcon } from './NutritionVisuals';
import { useDiary } from '../state/DiaryProvider';
import { diaryTotals } from '../domain/diary';
import type { DiaryEntry } from '../domain/diary';
import { formatNutrient, meals } from '../domain/food';
import { theme as t } from '../theme/tokens';
import { previewTargets } from '../data/dashboardPreview';
export function DiaryStatus() {
  const diary = useDiary();
  if (diary.entries !== null)
    return diary.message ? (
      <Text accessibilityLiveRegion="polite" style={ui.label}>
        {diary.message}
      </Text>
    ) : null;
  return (
    <Card>
      <Text
        accessibilityRole={diary.error ? 'alert' : undefined}
        style={ui.body}
      >
        {diary.error || 'Loading saved diary...'}
      </Text>
      {diary.error ? (
        <Action label="Retry loading diary" onPress={diary.reload} />
      ) : null}
    </Card>
  );
}
export function DaySummary({ entries }: { entries: DiaryEntry[] }) {
  const total = diaryTotals(entries);
  return (
    <Card>
      <Text style={ui.label}>
        {entries.length
          ? 'Recorded intake'
          : 'No entries recorded for this day'}
      </Text>
      <View
        style={{
          flexDirection: 'row',
          flexWrap: 'wrap',
          justifyContent: 'center',
          alignItems: 'center',
          gap: 12,
        }}
      >
        <View>
          <Text style={ui.heading}>
            {formatNutrient(total.values.calories, 'kcal')}
          </Text>
          <Text style={ui.body}>
            {total.partial.calories
              ? 'known subtotal (incomplete)'
              : 'consumed'}
          </Text>
        </View>
        <CalorieRing
          consumed={total.values.calories}
          partial={total.partial.calories}
          target={previewTargets.calories}
        />
        <View>
          <Text style={ui.heading}>{previewTargets.calories}</Text>
          <Text style={ui.body}>sample target</Text>
        </View>
      </View>
      <View style={{ flexDirection: 'row', flexWrap: 'wrap', gap: 16 }}>
        {(['carbs', 'protein', 'fat'] as const).map((key) => (
          <NutrientProgress
            key={key}
            compact
            color={
              key === 'carbs'
                ? '#A65A13'
                : key === 'fat'
                  ? '#8B6516'
                  : t.colors.primary
            }
            label={
              key === 'carbs' ? 'Carbs' : key === 'fat' ? 'Fat' : 'Protein'
            }
            consumed={total.values[key]}
            partial={total.partial[key]}
            target={previewTargets[key]}
            unit="g"
          />
        ))}
      </View>
      <Text style={ui.body}>
        Targets are sample settings, not medical recommendations. Food nutrition
        is illustrative.
      </Text>
    </Card>
  );
}
export function DiaryMeals({
  entries,
  date,
}: {
  entries: DiaryEntry[];
  date: string;
}) {
  return (
    <>
      {meals.map((meal) => {
        const selected = entries.filter((entry) => entry.meal === meal);
        const total = diaryTotals(selected);
        return (
          <Card key={meal}>
            <View
              style={{ flexDirection: 'row', alignItems: 'center', gap: 16 }}
            >
              <View
                style={{
                  backgroundColor: t.colors.accent,
                  padding: 12,
                  borderRadius: 16,
                }}
              >
                <AppIcon name="leaf" />
              </View>
              <Text accessibilityRole="header" style={ui.heading}>
                {meal}
              </Text>
            </View>
            {selected.length ? (
              <Text style={ui.label}>
                {formatNutrient(total.values.calories, 'kcal')}
                {total.partial.calories ? ' (incomplete)' : ''} / P{' '}
                {formatNutrient(total.values.protein, 'g')}
                {total.partial.protein ? ' (incomplete)' : ''} / C{' '}
                {formatNutrient(total.values.carbs, 'g')}
                {total.partial.carbs ? ' (incomplete)' : ''} / F{' '}
                {formatNutrient(total.values.fat, 'g')}
                {total.partial.fat ? ' (incomplete)' : ''}
              </Text>
            ) : (
              <Text style={ui.body}>No entries yet</Text>
            )}
            {selected.map((entry) => (
              <Pressable
                key={entry.id}
                accessibilityRole="button"
                accessibilityLabel={`Review or edit ${entry.foodName}, ${entry.grams} grams`}
                style={[ui.card, { minHeight: 48 }]}
                onPress={() =>
                  router.push({
                    pathname: '/diary-entry',
                    params: { id: entry.id },
                  })
                }
              >
                <Text style={ui.heading}>{entry.foodName}</Text>
                <Text style={ui.body}>
                  {entry.grams} g /{' '}
                  {formatNutrient(entry.nutrients.calories, 'kcal')}
                </Text>
                <Text style={ui.label}>
                  {entry.status === 'illustrative'
                    ? 'Illustrative nutrition'
                    : 'Verified source'}{' '}
                  / Edit or delete
                </Text>
              </Pressable>
            ))}
            <AddFood meal={meal} date={date} />
          </Card>
        );
      })}
    </>
  );
}
