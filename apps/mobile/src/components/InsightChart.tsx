import { ScrollView, Text, View } from 'react-native';
import Svg, { Circle, Line, Text as SvgText } from 'react-native-svg';
import { useUI } from './dashboard';
import {
  nutrientNames,
  unitFor,
  type Insights,
  type Nutrient,
} from '../domain/insights';
export function InsightChart({
  data,
  nutrient,
}: {
  data: Insights;
  nutrient: Nutrient;
}) {
  const { ui, t } = useUI();
  const points = data.days.filter((day) => day.nutrients[nutrient].eligible);
  if (!points.length)
    return (
      <Text style={ui.body}>
        No eligible {nutrientNames[nutrient].toLowerCase()} days to plot. Review
        meal coverage and unknown values below.
      </Text>
    );
  const high = Math.max(
    1,
    ...points.flatMap((day) => [
      day.nutrients[nutrient].value!,
      day.nutrients[nutrient].target ?? 0,
    ]),
  );
  const width = Math.max(320, data.days.length * 52 + 40);
  const x = (index: number) =>
    30 + (index * (width - 60)) / Math.max(1, data.days.length - 1);
  const y = (value: number) => 140 - (value / high) * 110;
  return (
    <View style={{ gap: 8 }}>
      <Text style={ui.body}>
        Recorded intake: green dots. Applicable positive target: orange dashes.
        Gaps are excluded days, not zero. No interpolation.
      </Text>
      <Text style={ui.label}>
        Scale: 0–{high.toFixed(1)} {unitFor(nutrient)}. Swipe horizontally;
        exact daily values follow.
      </Text>
      <ScrollView
        horizontal
        accessibilityLabel={`${nutrientNames[nutrient]} chart from ${data.range.start} to ${data.range.end}; ${points.length} eligible days. Exact values in the daily list.`}
      >
        <Svg width={width} height={190} accessible={false}>
          <Line
            x1={20}
            x2={width - 20}
            y1={140}
            y2={140}
            stroke={t.colors.border}
          />
          {data.days.map((day, index) => {
            const item = day.nutrients[nutrient];
            return (
              <ViewPoint
                key={day.date}
                x={x(index)}
                date={day.date.slice(5)}
                valueY={item.eligible ? y(item.value!) : null}
                targetY={
                  item.eligible && (item.target ?? 0) > 0
                    ? y(item.target!)
                    : null
                }
                primary={t.colors.primary}
                secondary={t.colors.secondary}
                muted={t.colors.muted}
              />
            );
          })}
        </Svg>
      </ScrollView>
    </View>
  );
}
function ViewPoint({
  x,
  date,
  valueY,
  targetY,
  primary,
  secondary,
  muted,
}: {
  x: number;
  date: string;
  valueY: number | null;
  targetY: number | null;
  primary: string;
  secondary: string;
  muted: string;
}) {
  return (
    <>
      {valueY !== null ? (
        <Circle cx={x} cy={valueY} r={5} fill={primary} />
      ) : null}
      {targetY !== null ? (
        <Line
          x1={x - 9}
          x2={x + 9}
          y1={targetY}
          y2={targetY}
          stroke={secondary}
          strokeWidth={3}
        />
      ) : null}
      <SvgText x={x} y={168} textAnchor="middle" fill={muted} fontSize={12}>
        {date}
      </SvgText>
      {valueY === null ? (
        <SvgText x={x} y={125} textAnchor="middle" fill={muted} fontSize={14}>
          —
        </SvgText>
      ) : null}
    </>
  );
}
