import { FoodImage } from '../components/FoodImage';
import { useCallback, useRef, useState } from 'react';
import { router, useFocusEffect, useLocalSearchParams } from 'expo-router';
import {
  Modal,
  View,
  BackHandler,
  Keyboard,
  KeyboardAvoidingView,
  Platform,
  ScrollView,
  Text,
  TextInput,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Action, Nutrition, useFoodStyles } from '../components/FoodControls';
import { Card, useUI } from '../components/dashboard';
import { DiaryStatus } from '../components/DiaryViews';
import { useDiary } from '../state/DiaryProvider';
import { editPortion } from '../domain/diary';
import type { DiaryEntry } from '../domain/diary';
import { parseGrams } from '../domain/food';
const back = () => {
  if (router.canGoBack()) router.back();
  else router.replace('/diary');
};
export default function DiaryEntryScreen() {
  const { ui } = useUI();
  const { id } = useLocalSearchParams<{ id?: string }>();
  const diary = useDiary();
  const entry = diary.entries?.find((e) => e.id === id);
  if (!entry)
    return (
      <SafeAreaView style={ui.page}>
        <ScrollView contentContainerStyle={ui.content}>
          <DiaryStatus />
          {diary.entries ? <Text style={ui.body}>Entry not found.</Text> : null}
          <Action label="Back" onPress={back} />
        </ScrollView>
      </SafeAreaView>
    );
  return <EntryEditor key={entry.id} original={entry} />;
}
function EntryEditor({ original }: { original: DiaryEntry }) {
  const [confirmDelete, setConfirmDelete] = useState(false);
  const styles = useFoodStyles();
  const { ui, t } = useUI();
  const [entry] = useState(original);
  const [portion, setPortion] = useState(String(entry.grams));
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const locked = useRef(false);
  const pending = useRef<DiaryEntry | null>(null);
  const [failedAction, setFailedAction] = useState<'edit' | 'delete' | null>(
    null,
  );
  const diary = useDiary();
  useFocusEffect(
    useCallback(() => {
      const sub = BackHandler.addEventListener(
        'hardwareBackPress',
        () => locked.current,
      );
      return () => sub.remove();
    }, []),
  );
  const grams = parseGrams(portion);
  let preview: DiaryEntry | null = null;
  if (grams !== null) {
    try {
      preview = editPortion(entry, grams, entry.updatedAt);
    } catch {
      /* Invalid numeric range is shown below. */
    }
  }
  async function commit(remove = false) {
    if (locked.current || (!remove && !preview)) return;
    locked.current = true;
    setBusy(true);
    setError('');
    Keyboard.dismiss();
    try {
      if (remove) await diary.remove(entry);
      else {
        pending.current ??= editPortion(
          entry,
          grams!,
          new Date().toISOString(),
        );
        await diary.update(pending.current, entry);
      }
      back();
    } catch (error) {
      setFailedAction(remove ? 'delete' : 'edit');
      setError(
        error instanceof Error
          ? error.message
          : 'Storage action failed. Retry.',
      );
    } finally {
      locked.current = false;
      setBusy(false);
    }
  }
  return (
    <SafeAreaView style={ui.page}>
      <KeyboardAvoidingView
        style={{ flex: 1 }}
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      >
        <ScrollView
          keyboardShouldPersistTaps="handled"
          contentContainerStyle={ui.content}
        >
          <Action
            variant="secondary"
            label="Cancel / Back"
            disabled={busy}
            onPress={back}
          />
          <Text accessibilityRole="header" style={ui.title}>
            Review entry
          </Text>
          <Card>
            <FoodImage foodId={entry.foodId} prominent />
            <Text style={ui.heading}>{entry.foodName}</Text>
            <Text style={ui.label}>
              {entry.date} / {entry.meal}
            </Text>
            <Text style={ui.body}>
              {entry.preparation} / {entry.status} nutrition
            </Text>
            <Text style={ui.body}>{entry.source}</Text>
            <Text style={ui.label}>Recorded reference per 100 g</Text>
            <Nutrition values={entry.reference} />
            <Text style={ui.label}>Saved portion: {entry.grams} g</Text>
            <Nutrition values={entry.nutrients} />
          </Card>
          <Card>
            <Text style={ui.heading}>Edit portion</Text>
            <Text style={ui.body}>Grams</Text>
            <TextInput
              selectionColor={t.colors.primary}
              style={styles.input}
              accessibilityLabel="Edit portion in grams"
              keyboardType="decimal-pad"
              value={portion}
              editable={!busy && !failedAction}
              onChangeText={setPortion}
            />
            {preview ? (
              <Nutrition values={preview.nutrients} />
            ) : (
              <Text accessibilityRole="alert" style={ui.body}>
                Enter a positive, finite amount within the supported range.
              </Text>
            )}
            {error ? (
              <Text accessibilityRole="alert" style={ui.body}>
                {error}
              </Text>
            ) : null}
            <Action
              label={
                busy
                  ? 'Working...'
                  : failedAction === 'edit'
                    ? 'Retry saving portion'
                    : 'Confirm portion change'
              }
              disabled={busy || !preview || failedAction === 'delete'}
              onPress={() => {
                void commit();
              }}
            />
            <Action
              label={
                failedAction === 'delete' ? 'Retry deletion' : 'Delete entry'
              }
              disabled={busy || failedAction === 'edit'}
              variant="danger"
              onPress={() => setConfirmDelete(true)}
            />
          </Card>
        </ScrollView>
      </KeyboardAvoidingView>
      <Modal
        visible={confirmDelete}
        transparent
        animationType="fade"
        onRequestClose={() => {
          if (!busy) setConfirmDelete(false);
        }}
      >
        <SafeAreaView
          style={{
            flex: 1,
            backgroundColor: t.colors.overlay,
            justifyContent: 'center',
          }}
        >
          <ScrollView
            contentContainerStyle={{
              flexGrow: 1,
              justifyContent: 'center',
              padding: t.spacing.lg,
            }}
          >
            <View accessibilityViewIsModal style={ui.card}>
              <Text accessibilityRole="header" style={ui.heading}>
                Delete diary entry?
              </Text>
              <Text style={ui.body}>
                Remove {entry.foodName} from {entry.meal} on {entry.date}?
              </Text>
              <Action
                label="Cancel"
                variant="secondary"
                onPress={() => setConfirmDelete(false)}
              />
              <Action
                label="Delete"
                variant="danger"
                onPress={() => {
                  setConfirmDelete(false);
                  void commit(true);
                }}
              />
            </View>
          </ScrollView>
        </SafeAreaView>
      </Modal>
    </SafeAreaView>
  );
}
