import { useState } from 'react';
import { ScrollView, Text, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { PreviewNotice, ui } from '../components/dashboard';
import { DaySummary, DiaryMeals, DiaryStatus } from '../components/DiaryViews';
import { Action } from '../components/FoodControls';
import { shiftDay } from '../domain/diary';
import { useDiary, useToday } from '../state/DiaryProvider';
export default function DiaryScreen() {
  const today = useToday();
  const [selected, setSelected] = useState<string | null>(null);
  const date = selected ?? today;
  const diary = useDiary();
  const entries =
    diary.entriesByDate === null ? null : (diary.entriesByDate.get(date) ?? []);
  return (
    <SafeAreaView edges={['top', 'left', 'right']} style={ui.page}>
      <ScrollView contentContainerStyle={ui.content}>
        <Text accessibilityRole="header" style={ui.title}>
          Food diary
        </Text>
        <Text style={ui.heading}>
          {date}
          {date === today ? ' / Today' : ''}
        </Text>
        <View style={ui.row}>
          <Action
            label="Previous day"
            disabled={date === '1900-01-01'}
            onPress={() => setSelected(shiftDay(date, -1))}
          />
          <Action label="Today" onPress={() => setSelected(null)} />
          <Action
            label="Next day"
            disabled={date >= today}
            onPress={() => setSelected(shiftDay(date, 1))}
          />
        </View>
        <DiaryStatus />
        {entries ? (
          <>
            <DaySummary entries={entries} />
            <DiaryMeals entries={entries} date={date} />
          </>
        ) : null}
        <PreviewNotice />
        <Text style={ui.body}>
          Saved on this device only. Uninstalling or clearing app data can
          remove your diary. No cloud backup or account sync.
        </Text>
      </ScrollView>
    </SafeAreaView>
  );
}
