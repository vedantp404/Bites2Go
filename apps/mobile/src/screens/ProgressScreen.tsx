import { router } from 'expo-router';
import { Text, View } from 'react-native';
import { Card, useUI } from '../components/dashboard';
import { Action } from '../components/FoodControls';
import {
  BmiCard,
  HealthPage,
  HealthStatus,
} from '../components/HealthControls';
import { WeightChart } from '../components/WeightChart';
import { useHealth } from '../state/HealthProvider';
import { weightProgress } from '../domain/health';
export default function ProgressScreen() {
  const { ui, t } = useUI();
  const { data, reload } = useHealth();
  const latest = data?.weights.at(-1);
  const earliest = data?.weights[0];
  const goal = weightProgress(
    latest?.kg ?? null,
    data?.weightGoal ?? null,
    latest?.date,
  );
  return (
    <HealthPage title="Your progress">
      <HealthStatus />
      {data ? (
        <>
          <Card>
            <Text style={ui.label}>LATEST RECORDED WEIGHT</Text>
            <Text style={ui.title}>
              {latest ? `${latest.kg} kg` : 'No measurements yet'}
            </Text>
            <Text style={ui.body}>
              {latest
                ? latest.date
                : 'Start with a measurement when you are ready.'}
            </Text>
            {earliest && latest && earliest.id !== latest.id ? (
              <Text style={ui.body}>
                Change since {earliest.date}:{' '}
                {latest.kg - earliest.kg > 0 ? '+' : ''}
                {(latest.kg - earliest.kg).toFixed(1)} kg ({earliest.kg} →{' '}
                {latest.kg} kg).
              </Text>
            ) : null}
            <Action
              label="Record weight"
              onPress={() => router.push('/weight-entry')}
            />
            <Action
              variant="secondary"
              label="Nutrition, height and weight goals"
              onPress={() => router.push('/goals')}
            />
          </Card>
          <Card>
            <Text accessibilityRole="header" style={ui.heading}>
              Weight goal
            </Text>
            {data.weightGoal ? (
              <>
                <Text style={ui.body}>
                  Target: {data.weightGoal.targetKg} kg / Current:{' '}
                  {latest ? `${latest.kg} kg (${latest.date})` : 'not recorded'}
                </Text>
                <Text style={ui.body}>
                  {goal.difference === null
                    ? 'Record weight to see the difference.'
                    : goal.difference === 0
                      ? 'Current recorded weight equals your target.'
                      : `${Math.abs(goal.difference).toFixed(1)} kg ${goal.difference > 0 ? 'below' : 'above'} target.`}
                </Text>
                {data.weightGoal.start ? (
                  <Text style={ui.body}>
                    Saved starting point: {data.weightGoal.start.kg} kg on{' '}
                    {data.weightGoal.start.date}. Goal set{' '}
                    {data.weightGoal.setDate}.
                  </Text>
                ) : null}
                {goal.percent !== null ? (
                  <View
                    accessible
                    accessibilityRole="progressbar"
                    accessibilityLabel="Weight goal progress"
                    accessibilityValue={{
                      min: 0,
                      max: 100,
                      now: goal.fill,
                      text: `${goal.percent.toFixed(0)} percent of the change from your starting point`,
                    }}
                  >
                    <Text style={ui.label}>
                      {goal.percent.toFixed(0)}% of the change from your
                      starting point
                    </Text>
                    <View
                      style={{
                        height: 8,
                        backgroundColor: t.colors.accent,
                        borderRadius: 8,
                        overflow: 'hidden',
                      }}
                    >
                      <View
                        style={{
                          height: 8,
                          width: `${goal.fill}%`,
                          backgroundColor: t.colors.primary,
                        }}
                      />
                    </View>
                  </View>
                ) : (
                  <Text style={ui.body}>
                    {data.weightGoal.start?.kg === data.weightGoal.targetKg
                      ? 'Starting weight equals target; compare the difference instead of a percentage.'
                      : 'A starting point and a current measurement on or after that date are needed for percentage progress.'}
                  </Text>
                )}
                <Text style={ui.body}>
                  This is your tracking target, not a recommended rate or amount
                  of weight change.
                </Text>
              </>
            ) : (
              <Text style={ui.body}>
                No weight target set. You can record measurements without
                setting a goal.
              </Text>
            )}
          </Card>
          <Card>
            <Text accessibilityRole="header" style={ui.heading}>
              Weight history
            </Text>
            <WeightChart weights={data.weights} />
            {[...data.weights].reverse().map((w) => (
              <View
                key={w.id}
                style={[ui.card, { backgroundColor: t.colors.elevated }]}
              >
                <Text style={ui.heading}>{w.kg} kg</Text>
                <Text style={ui.body}>{w.date}</Text>
                <Action
                  variant="secondary"
                  label={`Edit or delete ${w.date}`}
                  onPress={() =>
                    router.push({
                      pathname: '/weight-entry',
                      params: { id: w.id },
                    })
                  }
                />
              </View>
            ))}
          </Card>
          <BmiCard />
          <Action
            variant="secondary"
            label="Reload saved progress"
            onPress={reload}
          />
          <Text style={ui.body}>
            Saved on this device only. No cloud backup. Missing measurements are
            not estimated.
          </Text>
        </>
      ) : null}
    </HealthPage>
  );
}
