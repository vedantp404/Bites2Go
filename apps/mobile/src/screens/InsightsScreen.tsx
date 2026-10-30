import { useMemo, useState } from 'react';
import { Pressable, Text, View } from 'react-native';
import { router } from 'expo-router';
import { useDiary, useToday } from '../state/DiaryProvider';
import { useHealth } from '../state/HealthProvider';
import {
  Card,
  useUI,
  NutrientProgress,
  AddFood,
} from '../components/dashboard';
import { Action } from '../components/FoodControls';
import { HealthPage, Field } from '../components/HealthControls';
import { InsightChart } from '../components/InsightChart';
import { WeightChart } from '../components/WeightChart';
import { foodNutrientKeys, formatNutrient } from '../domain/food';
import { shiftDay } from '../domain/diary';
import {
  rollingRange,
  rangeDates,
  selectedInsightDate,
  insightView,
  eligibilityNote,
  nutrientNames,
  unitFor,
  dayNutrientLabel,
  type InsightRange,
  type Nutrient,
} from '../domain/insights';
export default function InsightsScreen() {
  const { ui, t } = useUI();
  const today = useToday(),
    diary = useDiary(),
    health = useHealth();
  const [period, setPeriod] = useState<7 | 30 | 'custom'>(7);
  const [custom, setCustom] = useState<InsightRange>(() =>
    rollingRange(today, 7),
  );
  const [start, setStart] = useState(custom.start),
    [end, setEnd] = useState(custom.end);
  const [rangeError, setRangeError] = useState('');
  const [selected, setSelected] = useState(today);
  const [nutrient, setNutrient] = useState<Nutrient>('calories');
  const [showDays, setShowDays] = useState(false);
  const range = useMemo(
    () => (period === 'custom' ? custom : rollingRange(today, period)),
    [period, custom, today],
  );
  const view = useMemo(
    () =>
      insightView(
        diary.entries,
        health.data,
        range,
        today,
        diary.error || health.error,
      ),
    [diary.entries, health.data, range, today, diary.error, health.error],
  );
  const date = selectedInsightDate(selected, range);
  const data = view.status === 'ready' ? view.data : null;
  const day = data?.days.find((item) => item.date === date);
  const reload = () => {
    diary.reload();
    health.reload();
  };
  return (
    <HealthPage title="Nutrition insights">
      <View style={ui.row}>
        <Action
          variant="secondary"
          label="Back"
          onPress={() =>
            router.canGoBack() ? router.back() : router.replace('/progress')
          }
        />
        <Action
          variant="secondary"
          label="Open food diary"
          onPress={() => router.push('/diary')}
        />
      </View>
      <Card>
        <Text style={ui.label}>YOUR RECORDED PATTERNS</Text>
        <Text style={ui.heading}>A little context for your food diary</Text>
        <Text style={ui.body}>
          Local records and your personal targets, with gaps kept visible. These
          comparisons do not assess diet quality or medical adequacy.
        </Text>
        <View style={ui.row}>
          {([7, 30, 'custom'] as const).map((value) => (
            <Pressable
              key={value}
              accessibilityRole="radio"
              accessibilityState={{ checked: period === value }}
              onPress={() => {
                setPeriod(value);
                setRangeError('');
              }}
              style={[
                ui.card,
                {
                  minHeight: 48,
                  backgroundColor:
                    period === value ? t.colors.selected : t.colors.surface,
                },
              ]}
            >
              <Text style={ui.label}>
                {value === 'custom' ? 'Custom range' : `Last ${value} days`}
              </Text>
            </Pressable>
          ))}
        </View>
        {period === 'custom' ? (
          <>
            <Field
              date
              label="Start date (YYYY-MM-DD)"
              value={start}
              onChangeText={setStart}
            />
            <Field
              date
              label="End date (YYYY-MM-DD)"
              value={end}
              onChangeText={setEnd}
            />
            <Action
              label="Apply custom range"
              onPress={() => {
                try {
                  rangeDates({ start, end }, today);
                  setCustom({ start, end });
                  setSelected(end);
                  setRangeError('');
                } catch (e) {
                  setRangeError(
                    e instanceof Error ? e.message : 'Invalid range.',
                  );
                }
              }}
            />
            <Text style={ui.body}>
              Up to 92 days. The applied period stays unchanged until valid
              dates are applied.
            </Text>
          </>
        ) : null}
        {rangeError ? (
          <Text
            accessibilityRole="alert"
            style={[ui.body, { color: t.colors.error }]}
          >
            {rangeError}
          </Text>
        ) : null}
        <Text accessibilityLiveRegion="polite" style={ui.heading}>
          {range.start} → {range.end}
        </Text>
        <Text style={ui.body}>{eligibilityNote}</Text>
      </Card>
      {view.status !== 'ready' ? (
        <Card>
          <Text
            accessibilityRole={view.status === 'error' ? 'alert' : undefined}
            style={ui.body}
          >
            {view.message}
          </Text>
          {view.status === 'error' ? (
            <Action label="Retry loading insights" onPress={reload} />
          ) : null}
        </Card>
      ) : null}
      {data && day ? (
        <>
          <Card>
            <Text accessibilityRole="header" style={ui.heading}>
              Diary coverage
            </Text>
            <Text style={ui.title}>
              {data.loggedDays} / {data.days.length} days with entries
            </Text>
            <Text style={ui.body}>
              {data.noEntryDays} days have no entries. {data.limitedMealDays}{' '}
              logged days have fewer than four meal sections. These counts
              include today if selected; today never enters period averages or
              consistency.
            </Text>
            {!data.loggedDays ? (
              <Text style={ui.body}>
                No recorded meals in this period. Add entries to your diary to
                begin seeing observations. No sample data is included.
              </Text>
            ) : null}
          </Card>
          <Card>
            <Text accessibilityRole="header" style={ui.heading}>
              Daily recorded nutrition
            </Text>
            <Text accessibilityLiveRegion="polite" style={ui.label}>
              {date}
              {day.inProgress ? ' / Today — in progress' : ''}
            </Text>
            <View style={ui.row}>
              <Action
                variant="secondary"
                label="Previous insight day"
                disabled={date <= range.start}
                onPress={() => setSelected(shiftDay(date, -1))}
              />
              <Action
                variant="secondary"
                label="Next insight day"
                disabled={date >= range.end}
                onPress={() => setSelected(shiftDay(date, 1))}
              />
            </View>
            <Text style={ui.body}>
              {day.entryCount
                ? `${day.entryCount} entries across ${day.mealCount} of 4 meal sections. Known amounts describe recorded food only; they may not describe the whole day.`
                : 'No diary entries: intake is unknown, not a confirmed zero.'}
            </Text>
            {foodNutrientKeys.map((key) => (
              <NutrientProgress
                key={key}
                label={`${nutrientNames[key]} recorded`}
                consumed={day.nutrients[key].value}
                partial={day.nutrients[key].partial}
                target={day.nutrients[key].target}
                unit={unitFor(key)}
              />
            ))}
            <Text style={ui.body}>
              Targets apply on {date}. Incomplete nutrient subtotals have no
              percentage. Fiber has no configurable target in the current model.
            </Text>
            <AddFood date={date} />
          </Card>
          <Card>
            <Text accessibilityRole="header" style={ui.heading}>
              Period trends
            </Text>
            <View style={ui.row}>
              {foodNutrientKeys.map((key) => (
                <Pressable
                  key={key}
                  accessibilityRole="radio"
                  accessibilityState={{ checked: nutrient === key }}
                  onPress={() => setNutrient(key)}
                  style={[
                    ui.card,
                    {
                      minHeight: 48,
                      backgroundColor:
                        nutrient === key ? t.colors.selected : t.colors.surface,
                    },
                  ]}
                >
                  <Text style={ui.label}>{nutrientNames[key]}</Text>
                </Pressable>
              ))}
            </View>
            <InsightChart data={data} nutrient={nutrient} />
            <Text style={ui.body}>
              {data.stats[nutrient].eligible} eligible past days;{' '}
              {data.stats[nutrient].unknownDays} logged days have unknown{' '}
              {nutrientNames[nutrient].toLowerCase()} values (may overlap
              limited meal coverage).
            </Text>
            <Action
              variant="secondary"
              label={showDays ? 'Hide daily values' : 'Show exact daily values'}
              onPress={() => setShowDays(!showDays)}
            />
            {showDays
              ? data.days.map((item) => (
                  <Pressable
                    key={item.date}
                    accessibilityRole="button"
                    accessibilityLabel={`${dayNutrientLabel(item, nutrient)} Select daily summary.`}
                    onPress={() => setSelected(item.date)}
                    style={[
                      ui.card,
                      {
                        minHeight: 48,
                        backgroundColor:
                          item.date === date
                            ? t.colors.selected
                            : t.colors.surface,
                      },
                    ]}
                  >
                    <Text style={ui.body}>
                      {dayNutrientLabel(item, nutrient)}
                    </Text>
                  </Pressable>
                ))
              : null}
          </Card>
          <Card>
            <Text accessibilityRole="header" style={ui.heading}>
              Average recorded intake
            </Text>
            {foodNutrientKeys.map((key) => (
              <View key={key} style={{ gap: 4 }}>
                <Text style={ui.label}>
                  {nutrientNames[key]}:{' '}
                  {formatNutrient(data.stats[key].average, unitFor(key))}
                </Text>
                <Text style={ui.body}>
                  {data.stats[key].eligible} eligible past days included;{' '}
                  {data.days.length - data.stats[key].eligible} excluded.{' '}
                  {data.stats[key].eligible === 1
                    ? 'One day is not a trend.'
                    : ''}
                </Text>
              </View>
            ))}
            <Text style={ui.body}>
              Each nutrient uses its own eligible days. Unknown values and
              missing days are never included as zero.
            </Text>
          </Card>
          <Card>
            <Text accessibilityRole="header" style={ui.heading}>
              Personal target consistency
            </Text>
            <Text style={ui.body}>
              Within 90–110% of the positive target saved for each date,
              inclusive. A descriptive comparison, not a recommended intake
              band. Unset/disabled targets are excluded.
            </Text>
            {(['calories', 'protein'] as const).map((key) => {
              const item = data.stats[key];
              return (
                <View key={key} style={{ gap: 4 }}>
                  <Text style={ui.label}>
                    {nutrientNames[key]}:{' '}
                    {item.percent === null
                      ? 'Not enough eligible target data'
                      : `${item.within} / ${item.goalDays} eligible target days (${item.percent.toFixed(0)}%)`}
                  </Text>
                  <Text style={ui.body}>
                    {item.below} below the band; {item.above} above.{' '}
                    {data.days.length - item.goalDays} days excluded, not
                    counted as missed targets.
                  </Text>
                </View>
              );
            })}
          </Card>
          <Card>
            <Text accessibilityRole="header" style={ui.heading}>
              Observations for this period
            </Text>
            {data.observations.map((text) => (
              <Text key={text} style={ui.body}>
                {text}
              </Text>
            ))}
          </Card>
          <Card>
            <Text accessibilityRole="header" style={ui.heading}>
              Recorded weight in this period
            </Text>
            <WeightChart weights={data.weight.records} />
            {data.weight.records.map((w) => (
              <Text key={w.id} style={ui.body}>
                {w.date}: {w.kg} kg
              </Text>
            ))}
            {data.weight.latest ? (
              <Text style={ui.label}>
                Latest in range: {data.weight.latest.kg} kg /{' '}
                {data.weight.latest.date}
              </Text>
            ) : null}
            <Text style={ui.body}>
              {data.weight.change === null
                ? 'Two measurements in this range are needed for a change comparison.'
                : `Change between the first and last recorded measurements: ${data.weight.change > 0 ? '+' : ''}${data.weight.change.toFixed(1)} kg. This alone does not establish a medically meaningful trend.`}
            </Text>
            <Text style={ui.body}>
              {data.weight.goal
                ? `Current saved weight goal: ${data.weight.goal.targetKg} kg, set ${data.weight.goal.setDate}. ${data.weight.progress.percent === null ? 'Percentage progress unavailable.' : `${data.weight.progress.percent.toFixed(0)}% of the change from the saved starting point.`}`
                : 'No current weight goal applicable to the latest measurement in this range. Historical weight goals are not stored.'}
            </Text>
            <Action
              variant="secondary"
              label="Open weight progress"
              onPress={() => router.push('/progress')}
            />
          </Card>
        </>
      ) : null}
    </HealthPage>
  );
}
