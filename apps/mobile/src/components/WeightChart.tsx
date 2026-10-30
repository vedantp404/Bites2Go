import { Text, View } from 'react-native';
import Svg, { Circle, Line, Text as SvgText } from 'react-native-svg';
import { useUI } from './dashboard';
import { weightPoints, type Weight } from '../domain/health';
export function WeightChart({ weights }: { weights: Weight[] }) {
  const { ui, t } = useUI();
  const points = weightPoints(weights);
  if (!points.length)
    return (
      <Text style={ui.body}>
        Your chart will appear after you record a measurement. No sample weights
        are added.
      </Text>
    );
  const low = Math.min(...weights.map((w) => w.kg)),
    high = Math.max(...weights.map((w) => w.kg));
  return (
    <View style={{ gap: 8 }}>
      <Text style={ui.body}>
        Recorded weights / kg. Dots are measurements; gaps are unrecorded days.
        Exact dates and values are listed below.
      </Text>
      <Svg width="100%" height={200} viewBox="0 0 320 200" accessible={false}>
        <Line x1={48} x2={300} y1={155} y2={155} stroke={t.colors.border} />
        <SvgText x={4} y={32} fill={t.colors.muted} fontSize={12}>
          {high.toFixed(1)}
        </SvgText>
        <SvgText x={4} y={155} fill={t.colors.muted} fontSize={12}>
          {low.toFixed(1)}
        </SvgText>
        {points.map((p) => (
          <Circle
            key={p.id}
            cx={52 + p.x * 238}
            cy={150 - p.y * 118}
            r={5}
            fill={t.colors.primary}
          />
        ))}
        <SvgText x={48} y={185} fill={t.colors.muted} fontSize={12}>
          {points[0].date}
        </SvgText>
        {points.length > 1 ? (
          <SvgText
            x={300}
            y={185}
            textAnchor="end"
            fill={t.colors.muted}
            fontSize={12}
          >
            {points.at(-1)!.date}
          </SvgText>
        ) : null}
      </Svg>
      <Text style={ui.body}>
        {points.length === 1
          ? 'One measurement; a trend needs more records.'
          : `${points.length} measurements from ${points[0].date} to ${points.at(-1)!.date}.`}
      </Text>
    </View>
  );
}
