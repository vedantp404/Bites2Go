import { ScrollView, Text } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Card, ui } from '../components/dashboard';
export default function ComingSoonScreen({
  title,
  description,
}: {
  title: string;
  description: string;
}) {
  return (
    <SafeAreaView edges={['top', 'left', 'right']} style={ui.page}>
      <ScrollView contentContainerStyle={ui.content}>
        <Text accessibilityRole="header" style={ui.title}>
          {title}
        </Text>
        <Card>
          <Text style={ui.label}>COMING LATER</Text>
          <Text style={ui.body}>{description}</Text>
          <Text style={ui.body}>
            This section is not available in the dashboard preview.
          </Text>
        </Card>
      </ScrollView>
    </SafeAreaView>
  );
}
