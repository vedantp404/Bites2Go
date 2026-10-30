import { memo, useState } from 'react';
import { Image, Text, View } from 'react-native';
import { foodImageKey } from '../data/foodImages';
import { useTheme } from '../theme/ThemeProvider';
import { AppIcon } from './NutritionVisuals';
const assets = {
  apple: require('../../assets/food/apple.jpg'),
  banana: require('../../assets/food/banana.jpg'),
};
export const FoodImage = memo(function FoodImage({
  foodId,
  prominent = false,
}: {
  foodId: string | null;
  prominent?: boolean;
}) {
  const { theme: t } = useTheme();
  const [failedId, setFailedId] = useState<string | null>(null);
  const key = foodImageKey(foodId, failedId === foodId);
  return (
    <View
      accessible
      accessibilityLabel={
        key
          ? 'Illustrative food photo; not a serving measurement'
          : 'Food image unavailable'
      }
      style={{
        height: prominent ? 180 : 72,
        width: prominent ? '100%' : 72,
        borderRadius: t.radii.control,
        backgroundColor: t.colors.highlight,
        overflow: 'hidden',
        alignItems: 'center',
        justifyContent: 'center',
        gap: 8,
      }}
    >
      {key ? (
        <Image
          accessible={false}
          source={assets[key]}
          resizeMode="cover"
          style={{ width: '100%', height: '100%' }}
          onError={() => setFailedId(foodId)}
        />
      ) : (
        <>
          <AppIcon
            name="leaf"
            size={prominent ? 48 : 28}
            color={t.colors.secondary}
          />
          {prominent ? (
            <Text style={{ ...t.typography.label, color: t.colors.secondary }}>
              Food photo coming later
            </Text>
          ) : null}
        </>
      )}
    </View>
  );
});
