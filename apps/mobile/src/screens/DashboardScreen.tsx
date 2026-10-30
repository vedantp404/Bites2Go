import { LinearGradient } from 'expo-linear-gradient';
import { Link } from 'expo-router';
import { CalorieRing, AppIcon } from '../components/NutritionVisuals';
import { theme as t } from '../theme/tokens';
import { useEffect, useState } from 'react';
import { AppState, ScrollView, Text, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import {
  AddFood,
  Card,
  MealCard,
  NutrientProgress,
  PreviewNotice,
  ui,
} from '../components/dashboard';
import { previewMeals, previewTargets } from '../data/dashboardPreview';
import { totals } from '../domain/dashboard';
export default function DashboardScreen() {
  const [now, setNow] = useState(() => new Date());
  useEffect(() => {
    const timer = setInterval(() => setNow(new Date()), 60000);
    const sub = AppState.addEventListener('change', (state) => {
      if (state === 'active') setNow(new Date());
    });
    return () => {
      clearInterval(timer);
      sub.remove();
    };
  }, []);
  const intake = totals(previewMeals);
  return (
    <View style={ui.page}>
      <ScrollView>
        <LinearGradient
          colors={[t.colors.primary, '#427667', t.colors.background]}
          locations={[0, 0.6, 1]}
        >
          <SafeAreaView edges={['top', 'left', 'right']}>
            <View
              style={{
                padding: 24,
                paddingBottom: 48,
                alignItems: 'center',
                gap: 12,
              }}
            >
              <AppIcon name="leaf" color="white" size={30} />
              <Text style={{ ...t.typography.heading, color: 'white' }}>
                Bites2Go
              </Text>
              <Text style={{ ...t.typography.label, color: 'white' }}>
                {now.toLocaleDateString(undefined, {
                  weekday: 'long',
                  day: 'numeric',
                  month: 'long',
                })}
              </Text>
            </View>
          </SafeAreaView>
        </LinearGradient>
        <View style={[ui.content, { marginTop: -24 }]}>
          <Text style={[ui.label, { textAlign: 'center' }]}>
            DEMO PREVIEW - SAMPLE DATA
          </Text>
          <Card>
            <View
              style={{
                flexDirection: 'row',
                flexWrap: 'wrap',
                justifyContent: 'center',
                alignItems: 'center',
                gap: 12,
              }}
            >
              <View style={{ alignItems: 'center' }}>
                <Text style={ui.heading}>{intake.calories}</Text>
                <Text style={ui.body}>consumed</Text>
              </View>
              <CalorieRing
                consumed={intake.calories}
                target={previewTargets.calories}
              />
              <View style={{ alignItems: 'center' }}>
                <Text style={ui.heading}>{previewTargets.calories}</Text>
                <Text style={ui.body}>target</Text>
              </View>
            </View>
            <View style={{ flexDirection: 'row', flexWrap: 'wrap', gap: 16 }}>
              {(
                [
                  { key: 'carbs', label: 'Carbs', color: '#A65A13' },
                  { key: 'protein', label: 'Protein', color: t.colors.primary },
                  { key: 'fat', label: 'Fat', color: '#8B6516' },
                ] as const
              ).map(({ key, label, color }) => (
                <NutrientProgress
                  key={key}
                  compact
                  color={color}
                  label={label}
                  consumed={intake[key]}
                  target={previewTargets[key]}
                  unit="g"
                />
              ))}
            </View>
            <View
              style={{
                borderTopWidth: 1,
                borderColor: t.colors.border,
                paddingTop: 16,
              }}
            >
              <Text style={[ui.body, { textAlign: 'center' }]}>
                A little more awareness, one meal at a time.
              </Text>
            </View>
          </Card>
          <AddFood />
          <View style={[ui.row, { alignItems: 'center' }]}>
            <Text accessibilityRole="header" style={ui.heading}>
              Today&apos;s meals
            </Text>
            <Link href="/diary" style={{ ...ui.label, padding: 14 }}>
              See diary
            </Link>
          </View>
          {previewMeals.map((meal) => (
            <MealCard key={meal.name} meal={meal} />
          ))}
          <PreviewNotice />
        </View>
      </ScrollView>
    </View>
  );
}
