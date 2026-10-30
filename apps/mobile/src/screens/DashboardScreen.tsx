import { LinearGradient } from 'expo-linear-gradient';
import { Link } from 'expo-router';
import { AppIcon } from '../components/NutritionVisuals';
import { theme as t } from '../theme/tokens';
import { useEffect, useState } from 'react';
import { AppState, ScrollView, Text, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { AddFood, PreviewNotice, ui } from '../components/dashboard';
import { DaySummary, DiaryMeals, DiaryStatus } from '../components/DiaryViews';
import { useDiary } from '../state/DiaryProvider';
import { localDateKey } from '../domain/diary';
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
  const diary = useDiary();
  const date = localDateKey(now);
  const entries =
    diary.entriesByDate === null ? null : (diary.entriesByDate.get(date) ?? []);
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
          <DiaryStatus />
          {entries ? (
            <>
              <DaySummary entries={entries} />
              <AddFood date={date} />
            </>
          ) : null}
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
        </View>
      </ScrollView>
    </View>
  );
}
