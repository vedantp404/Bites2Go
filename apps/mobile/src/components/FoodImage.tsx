import { memo, useState } from 'react';
import { Image, View } from 'react-native';
import { foodImageKey, type DecorativeImageKey } from '../data/foodImages';
import { useTheme } from '../theme/ThemeProvider';

const decorativeAssets: Record<DecorativeImageKey, any> = {
  apple: require('../../assets/food/apple.jpg'),
  banana: require('../../assets/food/banana.jpg'),
  dosa: require('../../assets/food/dosa.jpg'),
  carrot: require('../../assets/food/carrot.jpg'),
  oats: require('../../assets/food/oats.jpg'),
};

export const FoodImage = memo(function FoodImage({
  foodId,
  prominent = false,
}: {
  foodId: string | null;
  category?: string;
  prominent?: boolean;
}) {
  const { theme: t } = useTheme();
  const [failed, setFailed] = useState(false);
  const key = foodImageKey(foodId, failed);

  if (!key) return null;

  return (
    <View
      accessible
      accessibilityLabel="Decorative food illustration"
      style={{
        height: prominent ? 160 : 72,
        width: prominent ? '100%' : 72,
        borderRadius: t.radii.control,
        backgroundColor: t.colors.highlight,
        overflow: 'hidden',
        alignItems: 'center',
        justifyContent: 'center',
      }}
    >
      <Image
        accessible={false}
        source={decorativeAssets[key]}
        resizeMode="cover"
        style={{ width: '100%', height: '100%' }}
        onError={() => setFailed(true)}
      />
    </View>
  );
});
