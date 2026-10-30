import { localDateKey, shiftDay, validDateKey } from './diary.ts';
import type { DiaryEntry } from './diary.ts';
export function monthKey(date: string): string {
  if (!validDateKey(date)) throw new Error('Invalid calendar date.');
  return date.slice(0, 7);
}
function monthDate(month: string): Date {
  if (!validDateKey(`${month}-01`)) throw new Error('Invalid calendar month.');
  const [year, number] = month.split('-').map(Number);
  return new Date(year, number - 1, 1, 12);
}
export function shiftMonth(month: string, offset: number): string {
  if (!Number.isInteger(offset)) throw new Error('Invalid month offset.');
  const date = monthDate(month);
  date.setMonth(date.getMonth() + offset);
  return monthKey(localDateKey(date));
}
export function monthCells(month: string): (string | null)[] {
  const first = monthDate(month);
  const leading = (first.getDay() + 6) % 7;
  const count = new Date(
    first.getFullYear(),
    first.getMonth() + 1,
    0,
    12,
  ).getDate();
  const cells: (string | null)[] = Array(leading).fill(null);
  for (let day = 1; day <= count; day++)
    cells.push(`${month}-${String(day).padStart(2, '0')}`);
  while (cells.length % 7) cells.push(null);
  return cells;
}
export function monthTitle(month: string): string {
  return monthDate(month).toLocaleDateString(undefined, {
    month: 'long',
    year: 'numeric',
  });
}
export function indexDiaryDates(
  entries: readonly DiaryEntry[],
): ReadonlyMap<string, DiaryEntry[]> {
  const dates = new Map<string, DiaryEntry[]>();
  for (const entry of entries) {
    const bucket = dates.get(entry.date);
    if (bucket) bucket.push(entry);
    else dates.set(entry.date, [entry]);
  }
  return dates;
}
export function loggedDatesInMonth(
  index: ReadonlyMap<string, DiaryEntry[]>,
  month: string,
): string[] {
  return monthCells(month).filter(
    (date): date is string =>
      date !== null && (index.get(date)?.length ?? 0) > 0,
  );
}
export type CalendarState = { month: string; selected: string };
export function calendarState(today: string): CalendarState {
  return { month: monthKey(today), selected: today };
}
export type CalendarAction =
  | { type: 'select'; date: string }
  | { type: 'today'; date: string }
  | { type: 'month'; offset: number }
  | { type: 'day'; offset: number };
export function calendarReducer(
  state: CalendarState,
  action: CalendarAction,
): CalendarState {
  if (action.type === 'month')
    return { ...state, month: shiftMonth(state.month, action.offset) };
  if (action.type === 'day')
    return calendarState(shiftDay(state.selected, action.offset));
  return calendarState(action.date);
}
