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
import { progress, totals } from '../domain/dashboard';
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
  const energy = progress(intake.calories, previewTargets.calories);
  return (
    <SafeAreaView edges={['top', 'left', 'right']} style={ui.page}>
      <ScrollView contentContainerStyle={ui.content}>
        <View>
          <Text style={ui.label}>Bites2Go</Text>
          <Text accessibilityRole="header" style={ui.title}>
            Today, in balance
          </Text>
          <Text style={ui.body}>
            {now.toLocaleDateString(undefined, {
              weekday: 'long',
              day: 'numeric',
              month: 'long',
            })}
          </Text>
        </View>
        <PreviewNotice />
        <Card>
          <Text accessibilityRole="header" style={ui.heading}>
            Today&apos;s energy
          </Text>
          <View style={ui.row}>
            <View>
              <Text style={ui.title}>{energy.remaining}</Text>
              <Text style={ui.body}>kcal remaining (demo)</Text>
            </View>
            <View>
              <Text style={ui.heading}>{previewTargets.calories}</Text>
              <Text style={ui.body}>daily target</Text>
            </View>
          </View>
          <NutrientProgress
            label="Calories consumed"
            consumed={intake.calories}
            target={previewTargets.calories}
            unit="kcal"
          />
          <AddFood />
        </Card>
        <Card>
          <Text accessibilityRole="header" style={ui.heading}>
            Macronutrients
          </Text>
          {(
            [
              { key: 'protein', label: 'Protein' },
              { key: 'carbs', label: 'Carbohydrates' },
              { key: 'fat', label: 'Fat' },
            ] as const
          ).map(({ key, label }) => (
            <NutrientProgress
              key={key}
              label={label}
              consumed={intake[key]}
              target={previewTargets[key]}
              unit="g"
            />
          ))}
        </Card>
        <Text accessibilityRole="header" style={ui.heading}>
          Your meals · demo
        </Text>
        {previewMeals.map((meal) => (
          <MealCard key={meal.name} meal={meal} />
        ))}
      </ScrollView>
    </SafeAreaView>
  );
}
