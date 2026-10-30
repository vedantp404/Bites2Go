import { ScrollView, Text } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { MealCard, PreviewNotice, ui } from '../components/dashboard';
import { previewMeals } from '../data/dashboardPreview';
export default function DiaryScreen() {
  return (
    <SafeAreaView edges={['top', 'left', 'right']} style={ui.page}>
      <ScrollView contentContainerStyle={ui.content}>
        <Text accessibilityRole="header" style={ui.title}>
          Diary preview
        </Text>
        <PreviewNotice />
        <Text style={ui.body}>
          Explore sample foods with Add Food. Saving and editing diary meals are
          not available yet.
        </Text>
        {previewMeals.map((meal) => (
          <MealCard key={meal.name} meal={meal} />
        ))}
      </ScrollView>
    </SafeAreaView>
  );
}
