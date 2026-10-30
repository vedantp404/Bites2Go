import { memo, useState } from 'react';
import { Image, Text, View } from 'react-native';
import {
  categoryIcon,
  foodImageKey,
  type FoodImageAsset,
} from '../data/foodImages';
import { useTheme } from '../theme/ThemeProvider';
import { AppIcon } from './NutritionVisuals';

const assets: Record<FoodImageAsset, any> = {
  almonds: require('../../assets/food/almonds.jpg'),
  apple: require('../../assets/food/apple.jpg'),
  banana: require('../../assets/food/banana.jpg'),
  bread: require('../../assets/food/bread.jpg'),
  broccoli: require('../../assets/food/broccoli.jpg'),
  burger: require('../../assets/food/burger.jpg'),
  carrot: require('../../assets/food/carrot.jpg'),
  chicken_breast: require('../../assets/food/chicken_breast.jpg'),
  chickpeas: require('../../assets/food/chickpeas.jpg'),
  chocolate: require('../../assets/food/chocolate.jpg'),
  coffee: require('../../assets/food/coffee.jpg'),
  curd: require('../../assets/food/curd.jpg'),
  dal: require('../../assets/food/dal.jpg'),
  dosa: require('../../assets/food/dosa.jpg'),
  egg: require('../../assets/food/egg.jpg'),
  grapes: require('../../assets/food/grapes.jpg'),
  idli: require('../../assets/food/idli.jpg'),
  mango: require('../../assets/food/mango.jpg'),
  milk: require('../../assets/food/milk.jpg'),
  oats: require('../../assets/food/oats.jpg'),
  orange: require('../../assets/food/orange.jpg'),
  paneer: require('../../assets/food/paneer.jpg'),
  pasta: require('../../assets/food/pasta.jpg'),
  pizza: require('../../assets/food/pizza.jpg'),
  potato: require('../../assets/food/potato.jpg'),
  rice: require('../../assets/food/rice.jpg'),
  roti: require('../../assets/food/roti.jpg'),
  salmon: require('../../assets/food/salmon.jpg'),
  samosa: require('../../assets/food/samosa.jpg'),
  spinach: require('../../assets/food/spinach.jpg'),
  strawberry: require('../../assets/food/strawberry.jpg'),
  tea: require('../../assets/food/tea.jpg'),
  tomato: require('../../assets/food/tomato.jpg'),
  watermelon: require('../../assets/food/watermelon.jpg'),
};

export const FoodImage = memo(function FoodImage({
  foodId,
  category,
  prominent = false,
}: {
  foodId: string | null;
  category?: string;
  prominent?: boolean;
}) {
  const { theme: t } = useTheme();
  const [failedId, setFailedId] = useState<string | null>(null);
  const key = foodImageKey(foodId, failedId === foodId);
  const icon = categoryIcon(category);

  return (
    <View
      accessible
      accessibilityLabel={
        key
          ? 'Illustrative food photo; not a serving measurement'
          : `${category || 'Food'} badge`
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
            name={icon}
            size={prominent ? 48 : 28}
            color={t.colors.secondary}
          />
          {prominent ? (
            <Text
              style={{
                ...t.typography.label,
                color: t.colors.secondary,
                textTransform: 'uppercase',
                letterSpacing: 0.5,
              }}
            >
              {category || 'Food'}
            </Text>
          ) : null}
        </>
      )}
    </View>
  );
});
