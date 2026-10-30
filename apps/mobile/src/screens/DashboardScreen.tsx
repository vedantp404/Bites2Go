import { LinearGradient } from 'expo-linear-gradient';
import { Link } from 'expo-router';
import { ScrollView, Text, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { AddFood, PreviewNotice, useUI, Card } from '../components/dashboard';
import { FoodImage } from '../components/FoodImage';
import { DaySummary, DiaryMeals, DiaryStatus } from '../components/DiaryViews';
import { useDiary, useToday } from '../state/DiaryProvider';
export default function DashboardScreen() {
  const { ui, t } = useUI();
  const date = useToday();
  const diary = useDiary();
  const entries =
    diary.entriesByDate === null ? null : (diary.entriesByDate.get(date) ?? []);
  const [year, month, day] = date.split('-').map(Number);
  const dateLabel = new Date(year, month - 1, day).toLocaleDateString(
    undefined,
    { weekday: 'long', day: 'numeric', month: 'long' },
  );
  return (
    <SafeAreaView edges={['top', 'left', 'right']} style={ui.page}>
      <ScrollView contentContainerStyle={ui.content}>
        <View>
          <Text style={ui.label}>BITES2GO / YOUR DAILY DIARY</Text>
          <Text accessibilityRole="header" style={ui.title}>
            A little more balance.
          </Text>
          <Text style={ui.body}>{dateLabel}</Text>
        </View>
        <LinearGradient
          colors={[t.colors.hero, t.colors.heroEnd]}
          style={{
            borderRadius: t.radii.card,
            padding: t.spacing.lg,
            gap: t.spacing.sm,
          }}
        >
          <Text style={{ ...t.typography.heading, color: t.colors.onHero }}>
            Good food. Your rhythm.
          </Text>
          <Text style={{ ...t.typography.body, color: t.colors.onHero }}>
            Make room for the foods you love. Start with your next meal.
          </Text>
        </LinearGradient>
        <DiaryStatus />
        {entries ? (
          <>
            <DaySummary entries={entries} date={date} />
            <AddFood date={date} />
          </>
        ) : null}
        <Card>
          <View style={ui.row}>
            <Text accessibilityRole="header" style={ui.heading}>
              Fresh inspiration
            </Text>
            <Text style={[ui.label, { color: t.colors.secondary }]}>
              EXPLORE
            </Text>
          </View>
          <FoodImage foodId="apple" prominent />
          <Text style={ui.body}>
            Browse our small offline food catalog. Photos are illustrative;
            nothing here has been logged for you.
          </Text>
          <Link
            href={{ pathname: '/food-search', params: { date } }}
            style={[ui.label, { paddingVertical: 14 }]}
          >
            Browse foods →
          </Link>
        </Card>
        <View style={[ui.row, { alignItems: 'center' }]}>
          <Text accessibilityRole="header" style={ui.heading}>
            Today&apos;s meals
          </Text>
          <Link href="/diary" style={{ ...ui.label, padding: 14 }}>
            See diary
          </Link>
        </View>
        {entries ? <DiaryMeals entries={entries} date={date} /> : null}
        <PreviewNotice />
      </ScrollView>
    </SafeAreaView>
  );
}
