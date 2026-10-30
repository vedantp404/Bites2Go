import { useCallback, useRef, useState, type PropsWithChildren } from 'react';
import {
  BackHandler,
  Keyboard,
  KeyboardAvoidingView,
  Modal,
  Platform,
  ScrollView,
  Text,
  TextInput,
  View,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { router, useFocusEffect } from 'expo-router';
import { Action, useFoodStyles } from './FoodControls';
import { Card, useUI } from './dashboard';
import { useHealth } from '../state/HealthProvider';
import type { Health } from '../domain/health';
import { bmi } from '../domain/health';
export function HealthStatus() {
  const { data, error, reload } = useHealth();
  const { ui, t } = useUI();
  if (data) return null;
  return (
    <Card>
      <Text
        accessibilityRole={error ? 'alert' : undefined}
        style={[ui.body, { color: error ? t.colors.error : t.colors.muted }]}
      >
        {error || 'Loading saved progress and goals...'}
      </Text>
      {error ? (
        <Action label="Retry loading progress" onPress={reload} />
      ) : null}
    </Card>
  );
}
export function HealthPage({
  title,
  children,
}: PropsWithChildren<{ title: string }>) {
  const { ui } = useUI();
  return (
    <SafeAreaView edges={['top', 'left', 'right', 'bottom']} style={ui.page}>
      <KeyboardAvoidingView
        style={{ flex: 1 }}
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      >
        <ScrollView
          keyboardShouldPersistTaps="handled"
          keyboardDismissMode="on-drag"
          contentContainerStyle={ui.content}
        >
          <Text accessibilityRole="header" style={ui.title}>
            {title}
          </Text>
          {children}
        </ScrollView>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}
export function Field({
  label,
  value,
  onChangeText,
  disabled = false,
  date = false,
}: {
  label: string;
  value: string;
  onChangeText: (v: string) => void;
  disabled?: boolean;
  date?: boolean;
}) {
  const { ui, t } = useUI();
  const styles = useFoodStyles();
  return (
    <View style={{ gap: t.spacing.sm }}>
      <Text style={ui.label}>{label}</Text>
      <TextInput
        accessibilityLabel={label}
        value={value}
        onChangeText={onChangeText}
        editable={!disabled}
        keyboardType={date ? 'default' : 'decimal-pad'}
        autoCapitalize="none"
        autoCorrect={false}
        selectionColor={t.colors.primary}
        style={styles.input}
      />
    </View>
  );
}
export function ConfirmDelete({
  visible,
  onCancel,
  onConfirm,
}: {
  visible: boolean;
  onCancel: () => void;
  onConfirm: () => void;
}) {
  const { ui, t } = useUI();
  return (
    <Modal
      visible={visible}
      transparent
      animationType="none"
      onRequestClose={onCancel}
    >
      <SafeAreaView style={{ flex: 1, backgroundColor: t.colors.overlay }}>
        <ScrollView
          contentContainerStyle={{
            flexGrow: 1,
            justifyContent: 'center',
            padding: t.spacing.lg,
          }}
        >
          <View accessibilityViewIsModal style={ui.card}>
            <Text accessibilityRole="header" style={ui.heading}>
              Delete this measurement?
            </Text>
            <Text style={ui.body}>
              This removes the weight record from this device. A saved goal
              starting point remains unchanged.
            </Text>
            <Action label="Cancel" variant="secondary" onPress={onCancel} />
            <Action
              label="Delete measurement"
              variant="danger"
              onPress={onConfirm}
            />
          </View>
        </ScrollView>
      </SafeAreaView>
    </Modal>
  );
}
export function useHealthForm(original: Health) {
  const health = useHealth();
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const [attempted, setAttempted] = useState(false);
  const pending = useRef<Health | null>(null);
  const locked = useRef(false);
  const back = useCallback(() => {
    if (locked.current) return;
    Keyboard.dismiss();
    if (pending.current) health.reload();
    if (router.canGoBack()) router.back();
    else router.replace('/progress');
  }, [health]);
  useFocusEffect(
    useCallback(() => {
      const sub = BackHandler.addEventListener('hardwareBackPress', () => {
        back();
        return true;
      });
      return () => sub.remove();
    }, [back]),
  );
  async function submit(build: () => Health) {
    if (locked.current) return;
    locked.current = true;
    setBusy(true);
    setError('');
    Keyboard.dismiss();
    try {
      pending.current ??= build();
      setAttempted(true);
      await health.save(pending.current, original);
      pending.current = null;
      if (router.canGoBack()) router.back();
      else router.replace('/progress');
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Save failed. Retry.');
    } finally {
      locked.current = false;
      setBusy(false);
    }
  }
  return {
    busy,
    error,
    back,
    submit,
    disabled: busy || attempted,
    pending: attempted,
  };
}
export function BmiCard() {
  const { data } = useHealth();
  const { ui } = useUI();
  if (!data) return null;
  const latest = data.weights.at(-1);
  const value = bmi(data.heightCm, latest?.kg ?? null);
  return (
    <Card>
      <Text accessibilityRole="header" style={ui.heading}>
        BMI / adult screening measure
      </Text>
      {value === null ? (
        <Text style={ui.body}>
          Add your height in Profile settings and a weight measurement to see
          BMI.
        </Text>
      ) : (
        <>
          <Text style={ui.title}>{value.toFixed(1)} kg/m²</Text>
          <Text style={ui.body}>
            Using {data.heightCm} cm and {latest!.kg} kg recorded on{' '}
            {latest!.date}.
          </Text>
        </>
      )}
      <Text style={ui.body}>
        For adults aged 20 and over. BMI is a screening measure, not a diagnosis
        or a complete measure of health or body composition. No adult categories
        or interpretation are applied to children or teenagers.
      </Text>
    </Card>
  );
}
