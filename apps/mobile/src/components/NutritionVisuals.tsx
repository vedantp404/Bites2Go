import Svg, { Circle, Path } from 'react-native-svg';
import { Text, View } from 'react-native';
import { useTheme } from '../theme/ThemeProvider';
import { nutrientProgress } from '../domain/health';
export function AppIcon({
  name,
  color,
  size = 24,
}: {
  name: string;
  color?: string;
  size?: number;
}) {
  const { theme: t } = useTheme();
  const paths: Record<string, string> = {
    index: 'M3 10L12 3L21 10M5 9V21H10V14H14V21H19V9',
    diary:
      'M4 4H10Q12 4 12 6Q12 4 14 4H20V20H14Q12 20 12 22Q12 20 10 20H4ZM12 6V19',
    calendar: 'M4 5H20V21H4ZM4 10H20M8 2V7M16 2V7',
    progress: 'M4 20V12M12 20V4M20 20V8',
    profile:
      'M8 7A4 4 0 1 0 16 7A4 4 0 1 0 8 7M4 22V19Q4 13 12 13Q20 13 20 19V22',
    leaf: 'M4 20Q2 4 21 3Q22 21 4 20M4 20L16 8',
    bowl: 'M3 11C3 16 7 20 12 20C17 20 21 16 21 11H3ZM6 11V7M12 11V5M18 11V7',
    cup: 'M4 6H18V13C18 16 15 19 11 19C7 19 4 16 4 13V6ZM18 8H21C22 8 22 12 21 12H18',
    bread:
      'M5 7C5 5 7 4 12 4C17 4 19 5 19 7C20 9 20 17 19 19C17 20 7 20 5 19C4 17 4 9 5 7Z',
    dairy:
      'M7 3H17V6H7V3ZM5 9L7 6H17L19 9V20C19 21 18 21 17 21H7C6 21 5 21 5 20V9Z',
    meat: 'M18 6C15 3 11 5 8 8C5 11 3 15 6 18C7 19 8 19 9 18L13 14M16 8L18 6M13 14L18 19C19 20 20 20 21 19C22 18 22 17 21 16L16 11',
    snack:
      'M12 2C6.5 2 2 6.5 2 12C2 17.5 6.5 22 12 22C17.5 22 22 17.5 22 12C22 10 20 8 18 8C17 8 16 7 16 6C16 4 14 2 12 2ZM8 9A1 1 0 1 1 8 7A1 1 0 0 1 8 9ZM15 13A1 1 0 1 1 15 11A1 1 0 0 1 15 13ZM11 16A1 1 0 1 1 11 14A1 1 0 0 1 11 16Z',
    fruit:
      'M12 3C12 3 13 5 15 6M12 6C7 6 4 10 4 15C4 19 7 21 12 21C17 21 20 19 20 15C20 10 17 6 12 6Z',
  };
  return (
    <Svg width={size} height={size} viewBox="0 0 24 24" accessible={false}>
      <Path
        d={paths[name] ?? paths.leaf}
        fill="none"
        stroke={color ?? t.colors.primary}
        strokeWidth={1.7}
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </Svg>
  );
}
export function CalorieRing({
  consumed,
  target,
  partial = false,
}: {
  consumed: number | null;
  target: number | null;
  partial?: boolean;
}) {
  const { theme: t } = useTheme();
  const value = nutrientProgress(consumed, target, partial);
  const incomplete = consumed === null || partial;
  const circumference = 2 * Math.PI * 68;
  return (
    <View
      accessible
      accessibilityRole="progressbar"
      accessibilityLabel={
        incomplete
          ? 'Calories incomplete; remaining is unknown'
          : value.remaining === null
            ? 'Calorie target not set'
            : `Calories: ${consumed?.toFixed(0)} consumed, ${target} target, ${value.remaining?.toFixed(0)} remaining`
      }
      accessibilityValue={
        incomplete || value.remaining === null
          ? { text: incomplete ? 'Unknown remaining' : 'Target not set' }
          : { min: 0, max: 100, now: value.fill }
      }
      style={{
        alignItems: 'center',
        justifyContent: 'center',
        width: 160,
        minHeight: 160,
      }}
    >
      <Svg
        width={160}
        height={160}
        viewBox="0 0 160 160"
        style={{ position: 'absolute' }}
        accessible={false}
      >
        <Circle
          cx={80}
          cy={80}
          r={68}
          fill="none"
          stroke={t.colors.border}
          strokeWidth={8}
        />
        <Circle
          cx={80}
          cy={80}
          r={68}
          fill="none"
          stroke={t.colors.primary}
          strokeWidth={8}
          strokeDasharray={`${circumference} ${circumference}`}
          strokeDashoffset={
            circumference * (1 - (incomplete ? 0 : value.fill) / 100)
          }
          strokeLinecap="round"
          rotation={-90}
          origin="80,80"
        />
      </Svg>
      <Text style={{ ...t.typography.title, color: t.colors.text }}>
        {incomplete
          ? 'Unknown'
          : value.remaining === null
            ? 'Not set'
            : Math.abs(value.remaining).toFixed(0)}
      </Text>
      <Text style={{ ...t.typography.label, color: t.colors.muted }}>
        {value.remaining !== null && value.remaining < 0
          ? 'kcal over target'
          : 'kcal remaining'}
      </Text>
    </View>
  );
}
