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
