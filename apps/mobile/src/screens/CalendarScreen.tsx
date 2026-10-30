import type { Theme } from '../theme/tokens';
import type { ComponentRef } from 'react';
import { useMemo, useReducer, useRef } from 'react';
import { Pressable, ScrollView, StyleSheet, Text, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Card, PreviewNotice, useUI } from '../components/dashboard';
import { Action } from '../components/FoodControls';
import { DaySummary, DiaryMeals, DiaryStatus } from '../components/DiaryViews';
import { useDiary, useToday } from '../state/DiaryProvider';
import {
  calendarReducer,
  calendarState,
  loggedDatesInMonth,
  monthCells,
  monthTitle,
} from '../domain/calendar';

const weekdays = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
export default function CalendarScreen() {
  const { ui, t } = useUI();
  const styles = useMemo(() => makeStyles(t), [t]);
  const today = useToday();
  const scroll = useRef<ComponentRef<typeof ScrollView>>(null);
  const diaryTop = useRef(0);
  const [state, dispatch] = useReducer(calendarReducer, today, calendarState);
  const diary = useDiary();
  const cells = monthCells(state.month);
  const logged = useMemo(
    () =>
      diary.entriesByDate === null
        ? null
        : new Set(loggedDatesInMonth(diary.entriesByDate, state.month)),
    [diary.entriesByDate, state.month],
  );
  const entries =
    diary.entriesByDate === null
      ? null
      : (diary.entriesByDate.get(state.selected) ?? []);
  const rows = Array.from({ length: cells.length / 7 }, (_, row) =>
    cells.slice(row * 7, row * 7 + 7),
  );
  return (
    <SafeAreaView edges={['top', 'left', 'right']} style={ui.page}>
      <ScrollView ref={scroll} contentContainerStyle={ui.content}>
        <Text accessibilityRole="header" style={ui.title}>
          Calendar
        </Text>
        <Card>
          <Text
            accessibilityRole="header"
            accessibilityLiveRegion="polite"
            style={ui.heading}
          >
            {monthTitle(state.month)}
          </Text>
          <View style={ui.row}>
            <Action
              variant="secondary"
              label="Previous month"
              disabled={state.month === '1900-01'}
              onPress={() => dispatch({ type: 'month', offset: -1 })}
            />
            <Action
              variant="secondary"
              label="Next month"
              disabled={state.month === '9999-12'}
              onPress={() => dispatch({ type: 'month', offset: 1 })}
            />
            <Action
              variant="secondary"
              label="Today"
              onPress={() => dispatch({ type: 'today', date: today })}
            />
          </View>
          <Text style={ui.body}>
            Monday first. A dot means saved entries; an outline marks your
            selection. Today is labeled. Swipe the grid sideways on narrow
            screens.
          </Text>
          <ScrollView
            horizontal
            contentContainerStyle={{ flexGrow: 1 }}
            showsHorizontalScrollIndicator
          >
            <View style={{ minWidth: 336, flex: 1 }}>
              <View style={styles.week}>
                {weekdays.map((day) => (
                  <Text
                    key={day}
                    style={[
                      styles.cell,
                      ui.label,
                      { textAlign: 'center', minHeight: 32 },
                    ]}
                  >
                    {day}
                  </Text>
                ))}
              </View>
              {rows.map((row, index) => (
                <View key={index} style={styles.week}>
                  {row.map((date, column) =>
                    date ? (
                      <Pressable
                        key={date}
                        accessibilityRole="button"
                        accessibilityState={{
                          selected: date === state.selected,
                        }}
                        accessibilityLabel={`${date}${date === today ? ', today' : ''}${date === state.selected ? ', selected' : ''}${logged === null ? ', diary not loaded' : logged.has(date) ? `, ${diary.entriesByDate?.get(date)?.length} saved entries` : ', no saved entries'}. Show diary.`}
                        onPress={() => {
                          dispatch({ type: 'select', date });
                          scroll.current?.scrollTo({
                            y: diaryTop.current,
                            animated: true,
                          });
                        }}
                        style={({ pressed }) => [
                          styles.cell,
                          styles.day,
                          {
                            borderColor:
                              date === state.selected
                                ? t.colors.primary
                                : t.colors.transparent,
                            backgroundColor:
                              date === state.selected
                                ? t.colors.accent
                                : pressed
                                  ? t.colors.background
                                  : t.colors.surface,
                          },
                        ]}
                      >
                        <Text
                          style={[
                            ui.body,
                            {
                              color: t.colors.text,
                              fontWeight:
                                date === state.selected ? '700' : '400',
                            },
                          ]}
                        >
                          {Number(date.slice(-2))}
                        </Text>
                        {date === today ? (
                          <Text style={styles.marker}>Today</Text>
                        ) : null}
                        {logged?.has(date) ? (
                          <Text style={styles.marker}>●</Text>
                        ) : null}
                      </Pressable>
                    ) : (
                      <View key={`blank-${column}`} style={styles.cell} />
                    ),
                  )}
                </View>
              ))}
            </View>
          </ScrollView>
          {logged !== null ? (
            <Text style={ui.body}>
              {logged.size === 0
                ? 'No saved entries in this month.'
                : `${logged.size} dates with saved entries this month.`}
            </Text>
          ) : (
            <Text style={ui.body}>
              Entry indicators will appear when the diary loads.
            </Text>
          )}
        </Card>
        <Text
          onLayout={(event) => {
            diaryTop.current = event.nativeEvent.layout.y;
          }}
          accessibilityRole="header"
          accessibilityLiveRegion="polite"
          style={ui.heading}
        >
          Diary / {state.selected}
          {state.selected === today ? ' / Today' : ''}
        </Text>
        <View style={ui.row}>
          <Action
            variant="secondary"
            label="Previous day"
            disabled={state.selected === '1900-01-01'}
            onPress={() => dispatch({ type: 'day', offset: -1 })}
          />
          <Action
            variant="secondary"
            label="Next day"
            disabled={state.selected === '9999-12-31'}
            onPress={() => dispatch({ type: 'day', offset: 1 })}
          />
        </View>
        {state.selected > today ? (
          <Text style={ui.body}>
            Future date: viewing is available, but food logging opens on that
            day.
          </Text>
        ) : null}
        <DiaryStatus />
        {entries ? (
          <>
            <DaySummary entries={entries} />
            <DiaryMeals
              entries={entries}
              date={state.selected}
              allowAdding={state.selected <= today}
            />
          </>
        ) : null}
        <PreviewNotice />
      </ScrollView>
    </SafeAreaView>
  );
}
const makeStyles = (t: Theme) =>
  StyleSheet.create({
    week: { flexDirection: 'row' },
    cell: { flex: 1, minWidth: 48 },
    day: {
      minHeight: 64,
      borderWidth: 2,
      borderRadius: 12,
      alignItems: 'center',
      justifyContent: 'center',
      paddingVertical: 6,
    },
    marker: { ...t.typography.label, color: t.colors.primary, fontSize: 12 },
  });
