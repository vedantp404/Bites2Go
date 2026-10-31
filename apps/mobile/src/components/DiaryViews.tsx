import { useHealth } from '../state/HealthProvider';
import { targetsForDate, unsetTargets } from '../domain/health';
import { HealthStatus } from './HealthControls';
import { Text, View, Pressable } from 'react-native';
import { Link, router } from 'expo-router';
import { AddFood, Card, NutrientProgress, useUI } from './dashboard';
import {
  calculateNutrientProgress,
  calculateMacroDistribution,
} from '../domain/dashboard';
import { Action } from './FoodControls';
import { CalorieRing, AppIcon } from './NutritionVisuals';
import { useDiary } from '../state/DiaryProvider';
import { diaryTotals } from '../domain/diary';
import type { DiaryEntry } from '../domain/diary';
import { formatNutrient, meals } from '../domain/food';

export function DiaryStatus() {
  const { ui } = useUI();
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
export function DaySummary({
  entries,
  date,
}: {
  entries: DiaryEntry[];
  date: string;
}) {
  const { data } = useHealth();
  const targets = data ? targetsForDate(data, date) : unsetTargets;
  const { ui, t } = useUI();
  const total = diaryTotals(entries);

  if (entries.length === 0) {
    return (
      <View style={{ gap: t.spacing.md }}>
        <HealthStatus />
        <Card>
          <View
            style={{
              alignItems: 'center',
              paddingVertical: t.spacing.md,
              gap: t.spacing.sm,
            }}
          >
            <View
              style={{
                width: 60,
                height: 60,
                borderRadius: 30,
                backgroundColor: t.colors.accent,
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              <AppIcon name="diary" size={32} color={t.colors.primary} />
            </View>
            <Text
              accessibilityRole="header"
              style={[ui.heading, { textAlign: 'center' }]}
            >
              No entries recorded for this day
            </Text>
            <Text
              style={[
                ui.body,
                { textAlign: 'center', maxWidth: 300, fontSize: 13 },
              ]}
            >
              Log breakfast, lunch, dinner, or snacks to track calories and
              macronutrients toward your daily goals.
            </Text>
            {targets.calories ? (
              <View
                style={{
                  flexDirection: 'row',
                  alignItems: 'center',
                  gap: 6,
                  backgroundColor: t.colors.accent,
                  paddingHorizontal: 12,
                  paddingVertical: 6,
                  borderRadius: 16,
                  marginTop: 4,
                }}
              >
                <Text
                  style={{
                    ...t.typography.label,
                    fontSize: 12,
                    color: t.colors.primary,
                  }}
                >
                  Daily Target: {targets.calories} kcal
                </Text>
              </View>
            ) : null}
          </View>
          <AddFood date={date} />
          <View style={{ flexDirection: 'row', justifyContent: 'center' }}>
            <Link
              href="/goals"
              style={[
                ui.label,
                { fontSize: 13, paddingVertical: 6, textAlign: 'center' },
              ]}
            >
              {targets.calories
                ? 'Adjust nutrition goals →'
                : 'Set your nutrition goals →'}
            </Link>
          </View>
        </Card>
      </View>
    );
  }

  const calorieProgress = calculateNutrientProgress(
    total.values.calories,
    targets.calories,
    total.partial.calories,
    'kcal',
  );

  const macroDist = calculateMacroDistribution(
    total.values.protein,
    total.values.carbs,
    total.values.fat,
  );

  const loggedMealsCount = new Set(entries.map((e) => e.meal)).size;
  const loggedItemsCount = entries.length;

  return (
    <View style={{ gap: t.spacing.md }}>
      <HealthStatus />

      {/* 1. Daily Calorie Progress Card */}
      <Card>
        <View
          style={{
            flexDirection: 'row',
            alignItems: 'center',
            justifyContent: 'space-between',
          }}
        >
          <View>
            <Text style={ui.label}>DAILY CALORIES</Text>
            <Text accessibilityRole="header" style={ui.heading}>
              Energy Balance
            </Text>
          </View>
          <Link
            href="/goals"
            accessibilityLabel="Edit daily nutrition goals"
            style={[ui.label, { fontSize: 13, padding: 4 }]}
          >
            {targets.calories ? 'Edit Goals' : '+ Set Goal'}
          </Link>
        </View>

        <View
          style={{
            alignItems: 'center',
            justifyContent: 'center',
            paddingVertical: t.spacing.sm,
          }}
        >
          <CalorieRing
            consumed={total.values.calories}
            partial={total.partial.calories}
            target={targets.calories}
            size={168}
          />
        </View>

        <View
          style={{
            flexDirection: 'row',
            justifyContent: 'space-between',
            backgroundColor: t.colors.accent,
            borderRadius: t.radii.control,
            padding: t.spacing.md,
          }}
        >
          <View style={{ flex: 1, alignItems: 'center' }}>
            <Text
              style={{
                ...t.typography.heading,
                fontSize: 17,
                color: t.colors.text,
              }}
            >
              {formatNutrient(total.values.calories, 'kcal')}
            </Text>
            <Text
              style={{
                ...t.typography.body,
                fontSize: 12,
                color: t.colors.muted,
              }}
            >
              {total.partial.calories ? 'subtotal' : 'consumed'}
            </Text>
          </View>

          <View
            style={{
              width: 1,
              backgroundColor: t.colors.border,
              marginVertical: 2,
            }}
          />

          <View style={{ flex: 1, alignItems: 'center' }}>
            <Text
              style={{
                ...t.typography.heading,
                fontSize: 17,
                color: t.colors.text,
              }}
            >
              {targets.calories ? `${targets.calories} kcal` : 'Not set'}
            </Text>
            <Text
              style={{
                ...t.typography.body,
                fontSize: 12,
                color: t.colors.muted,
              }}
            >
              daily target
            </Text>
          </View>

          <View
            style={{
              width: 1,
              backgroundColor: t.colors.border,
              marginVertical: 2,
            }}
          />

          <View style={{ flex: 1, alignItems: 'center' }}>
            <Text
              style={{
                ...t.typography.heading,
                fontSize: 17,
                color: calorieProgress.isExceeded
                  ? t.colors.warning
                  : t.colors.text,
              }}
            >
              {total.partial.calories
                ? 'Unknown'
                : !calorieProgress.isTargetSet
                  ? '--'
                  : calorieProgress.isExceeded
                    ? `+${Math.round(calorieProgress.exceeded)}`
                    : `${Math.round(calorieProgress.remaining ?? 0)}`}
            </Text>
            <Text
              style={{
                ...t.typography.body,
                fontSize: 12,
                color: calorieProgress.isExceeded
                  ? t.colors.warning
                  : t.colors.muted,
                fontWeight: calorieProgress.isExceeded ? '600' : '400',
              }}
            >
              {total.partial.calories
                ? 'subtotal'
                : !calorieProgress.isTargetSet
                  ? 'target unset'
                  : calorieProgress.isExceeded
                    ? 'exceeded'
                    : 'remaining'}
            </Text>
          </View>
        </View>
      </Card>

      {/* 2. Macronutrient Tracking Card */}
      <Card>
        <View
          style={{
            flexDirection: 'row',
            alignItems: 'center',
            justifyContent: 'space-between',
          }}
        >
          <View>
            <Text style={ui.label}>MACRONUTRIENTS</Text>
            <Text accessibilityRole="header" style={ui.heading}>
              Daily Targets
            </Text>
          </View>
          {targets.protein === null ||
          targets.carbs === null ||
          targets.fat === null ? (
            <Link
              href="/goals"
              accessibilityLabel="Set macro targets in goals"
              style={[ui.label, { fontSize: 13, padding: 4 }]}
            >
              Set Macro Goals →
            </Link>
          ) : null}
        </View>

        <View style={{ gap: t.spacing.md }}>
          <NutrientProgress
            label="Protein"
            consumed={total.values.protein}
            partial={total.partial.protein}
            target={targets.protein}
            unit="g"
            color={t.colors.primary}
          />
          <NutrientProgress
            label="Carbohydrates"
            consumed={total.values.carbs}
            partial={total.partial.carbs}
            target={targets.carbs}
            unit="g"
            color={t.colors.carbs}
          />
          <NutrientProgress
            label="Fat"
            consumed={total.values.fat}
            partial={total.partial.fat}
            target={targets.fat}
            unit="g"
            color={t.colors.fat}
          />
        </View>
      </Card>

      {/* 3. Daily Nutrition Overview Card */}
      <Card>
        <View style={ui.row}>
          <View>
            <Text style={ui.label}>DAILY OVERVIEW</Text>
            <Text accessibilityRole="header" style={ui.heading}>
              Intake Breakdown
            </Text>
          </View>
          <View
            style={{
              backgroundColor: t.colors.accent,
              paddingHorizontal: 10,
              paddingVertical: 4,
              borderRadius: 12,
              alignSelf: 'flex-start',
            }}
          >
            <Text
              style={{
                ...t.typography.label,
                fontSize: 12,
                color: t.colors.primary,
              }}
            >
              {loggedItemsCount} {loggedItemsCount === 1 ? 'item' : 'items'} •{' '}
              {loggedMealsCount} {loggedMealsCount === 1 ? 'meal' : 'meals'}
            </Text>
          </View>
        </View>

        {/* Macro Totals Pills */}
        <View
          style={{
            flexDirection: 'row',
            flexWrap: 'wrap',
            gap: 8,
          }}
        >
          <View
            style={{
              flex: 1,
              minWidth: 90,
              padding: 10,
              backgroundColor: t.colors.accent,
              borderRadius: t.radii.control,
              borderLeftWidth: 3,
              borderLeftColor: t.colors.primary,
            }}
          >
            <Text
              style={{
                ...t.typography.label,
                fontSize: 11,
                color: t.colors.primary,
              }}
            >
              PROTEIN
            </Text>
            <Text
              style={{
                ...t.typography.heading,
                fontSize: 15,
                color: t.colors.text,
              }}
            >
              {total.values.protein !== null
                ? `${total.values.protein.toFixed(1)} g`
                : 'Unknown'}
            </Text>
            <Text
              style={{
                ...t.typography.body,
                fontSize: 11,
                color: t.colors.muted,
              }}
            >
              {macroDist.proteinPct}% cal
            </Text>
          </View>

          <View
            style={{
              flex: 1,
              minWidth: 90,
              padding: 10,
              backgroundColor: t.colors.accent,
              borderRadius: t.radii.control,
              borderLeftWidth: 3,
              borderLeftColor: t.colors.carbs,
            }}
          >
            <Text
              style={{
                ...t.typography.label,
                fontSize: 11,
                color: t.colors.carbs,
              }}
            >
              CARBS
            </Text>
            <Text
              style={{
                ...t.typography.heading,
                fontSize: 15,
                color: t.colors.text,
              }}
            >
              {total.values.carbs !== null
                ? `${total.values.carbs.toFixed(1)} g`
                : 'Unknown'}
            </Text>
            <Text
              style={{
                ...t.typography.body,
                fontSize: 11,
                color: t.colors.muted,
              }}
            >
              {macroDist.carbsPct}% cal
            </Text>
          </View>

          <View
            style={{
              flex: 1,
              minWidth: 90,
              padding: 10,
              backgroundColor: t.colors.accent,
              borderRadius: t.radii.control,
              borderLeftWidth: 3,
              borderLeftColor: t.colors.fat,
            }}
          >
            <Text
              style={{
                ...t.typography.label,
                fontSize: 11,
                color: t.colors.fat,
              }}
            >
              FAT
            </Text>
            <Text
              style={{
                ...t.typography.heading,
                fontSize: 15,
                color: t.colors.text,
              }}
            >
              {total.values.fat !== null
                ? `${total.values.fat.toFixed(1)} g`
                : 'Unknown'}
            </Text>
            <Text
              style={{
                ...t.typography.body,
                fontSize: 11,
                color: t.colors.muted,
              }}
            >
              {macroDist.fatPct}% cal
            </Text>
          </View>
        </View>

        {/* Macro Distribution Stacked Bar */}
        {macroDist.proteinPct + macroDist.carbsPct + macroDist.fatPct > 0 ? (
          <View style={{ gap: 6, marginTop: 4 }}>
            <Text
              style={{
                ...t.typography.label,
                fontSize: 11,
                color: t.colors.muted,
              }}
            >
              CALORIC ENERGY SHARE
            </Text>
            <View
              style={{
                height: 8,
                flexDirection: 'row',
                borderRadius: 4,
                overflow: 'hidden',
                backgroundColor: t.colors.accent,
              }}
            >
              {macroDist.proteinPct > 0 ? (
                <View
                  style={{
                    width: `${macroDist.proteinPct}%`,
                    backgroundColor: t.colors.primary,
                  }}
                />
              ) : null}
              {macroDist.carbsPct > 0 ? (
                <View
                  style={{
                    width: `${macroDist.carbsPct}%`,
                    backgroundColor: t.colors.carbs,
                  }}
                />
              ) : null}
              {macroDist.fatPct > 0 ? (
                <View
                  style={{
                    width: `${macroDist.fatPct}%`,
                    backgroundColor: t.colors.fat,
                  }}
                />
              ) : null}
            </View>
          </View>
        ) : null}

        <Text style={[ui.body, { fontSize: 12, lineHeight: 16 }]}>
          Targets shown are effective for {date}. Set your own in Goals. Food
          nutrition is illustrative; targets are not medical recommendations.
        </Text>
      </Card>
    </View>
  );
}
export function DiaryMeals({
  entries,
  date,
  allowAdding = true,
}: {
  entries: DiaryEntry[];
  date: string;
  allowAdding?: boolean;
}) {
  const { ui, t } = useUI();
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
                <Text style={ui.body}>
                  P {formatNutrient(entry.nutrients.protein, 'g')} / C{' '}
                  {formatNutrient(entry.nutrients.carbs, 'g')} / F{' '}
                  {formatNutrient(entry.nutrients.fat, 'g')}
                </Text>
                <Text style={ui.label}>
                  {entry.status === 'verified'
                    ? 'Verified source'
                    : entry.status === 'estimated'
                      ? 'Estimated nutrition'
                      : 'Illustrative nutrition'}{' '}
                  / Edit or delete
                </Text>
              </Pressable>
            ))}
            <AddFood meal={meal} date={date} disabled={!allowAdding} />
          </Card>
        );
      })}
    </>
  );
}
