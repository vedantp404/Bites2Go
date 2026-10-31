/**
 * Voice Food Logging Modal for Bites2Go.
 *
 * Provides:
 * - Natural language voice speech capture using expo-speech-recognition.
 * - Live volume meter and listening/processing/review visual states.
 * - Editable speech transcript (support for typing or editing misrecognized words).
 * - Multi-item interpretation, colloquial portions, and in-flight self-correction via Gemini.
 * - Catalogue matching against 1,411 unified foods (dataset-first priority).
 * - Toggle between Catalogue-matched verified nutrition and Gemini AI estimates.
 * - Editable portions, live scaled macros, and meal totals.
 * - Atomic persistence to local SQLite diary via diary.saveAll().
 */

import React, { useState, useMemo } from 'react';
import {
  Alert,
  KeyboardAvoidingView,
  Modal,
  Platform,
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  View,
} from 'react-native';
import { randomUUID } from 'expo-crypto';

import {
  isNativeSpeechModuleAvailable,
  useSafeSpeechRecognitionEvent,
  isSpeechRecognitionServiceAvailable,
  requestSpeechPermissions,
  startSpeechRecognition,
  stopSpeechRecognition,
  abortSpeechRecognition,
} from '../services/speechRecognitionService';
import { useUI } from './dashboard';
import { Action } from './FoodControls';
import { useDiary } from '../state/DiaryProvider';
import { useLibrary } from '../state/LibraryProvider';
import { localDateKey, validDateKey } from '../domain/diary';
import { scaleNutrients, type Food, type Meal } from '../domain/food';
import { unifiedFoods } from '../data/unifiedFoods';
import {
  parseVoiceMeal,
  matchVoiceItemsToCatalogue,
  buildAvailableFoodPool,
  buildDiaryEntriesFromVoiceCandidates,
  type MatchedVoiceFoodCandidate,
} from '../services/voiceFoodLogging';

export type VoiceFoodLoggingModalProps = {
  visible: boolean;
  meal: Meal;
  date?: string | null;
  onClose: () => void;
  onSuccess?: () => void;
};

type ModalFlowStep = 'capture' | 'review';

export function VoiceFoodLoggingModal({
  visible,
  meal,
  date,
  onClose,
  onSuccess,
}: VoiceFoodLoggingModalProps) {
  const { t } = useUI();
  const diary = useDiary();
  const library = useLibrary();

  const [step, setStep] = useState<ModalFlowStep>('capture');
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [interimText, setInterimText] = useState('');
  const [volume, setVolume] = useState(0);
  const [interpreting, setInterimInterpreting] = useState(false);
  const [saving, setSaving] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const [mealSummary, setMealSummary] = useState('');
  const [warnings, setWarnings] = useState<string[]>([]);
  const [clarifyingQuestions, setClarifyingQuestions] = useState<string[]>([]);
  const [candidates, setCandidates] = useState<MatchedVoiceFoodCandidate[]>([]);

  const targetDate = useMemo(() => {
    return date && validDateKey(date) ? date : localDateKey();
  }, [date]);

  // Speech recognition event hooks
  useSafeSpeechRecognitionEvent('start', () => {
    setIsListening(true);
    setErrorMessage(null);
  });

  useSafeSpeechRecognitionEvent('end', () => {
    setIsListening(false);
  });

  useSafeSpeechRecognitionEvent('result', (event) => {
    const results = event.results || [];
    if (results.length > 0) {
      const top = results[0]?.transcript || '';
      if (event.isFinal) {
        setTranscript((prev) => (prev ? `${prev} ${top}`.trim() : top));
        setInterimText('');
      } else {
        setInterimText(top);
      }
    }
  });

  useSafeSpeechRecognitionEvent('error', (event) => {
    setIsListening(false);
    const errText =
      event.message ||
      event.error ||
      'Speech recognition encountered an issue.';
    setErrorMessage(errText);
  });

  useSafeSpeechRecognitionEvent('volumechange', (event) => {
    if (typeof event.value === 'number') {
      setVolume(Math.max(0, Math.min(100, Math.round(event.value * 10))));
    }
  });

  const isNativeSupported = isNativeSpeechModuleAvailable();

  const resetState = () => {
    if (isListening) {
      try {
        abortSpeechRecognition();
      } catch {
        // ignore
      }
    }
    setStep('capture');
    setIsListening(false);
    setTranscript('');
    setInterimText('');
    setVolume(0);
    setInterimInterpreting(false);
    setSaving(false);
    setErrorMessage(null);
    setMealSummary('');
    setWarnings([]);
    setClarifyingQuestions([]);
    setCandidates([]);
  };

  const handleClose = () => {
    if (interpreting || saving) return;
    resetState();
    onClose();
  };

  // Start audio capture
  const handleStartListening = async () => {
    setErrorMessage(null);

    if (!isNativeSupported) {
      setErrorMessage(
        'Native microphone speech recognition is unavailable in stock Expo Go. You can dictate using your mobile keyboard microphone or type your meal below.',
      );
      Alert.alert(
        'Development Build Required',
        'Direct microphone speech recognition requires a native development build because third-party native code is not bundled into stock Expo Go.\n\nYou can still use voice logging right now: tap the microphone button on your keyboard to speak into the text box, or type your meal description directly!',
        [{ text: 'OK' }],
      );
      return;
    }

    try {
      const isAvailable = isSpeechRecognitionServiceAvailable();
      if (!isAvailable) {
        setErrorMessage(
          'Native speech recognizer is unavailable on this device. You can type your meal description directly into the text box below.',
        );
        return;
      }

      const perm = await requestSpeechPermissions();
      if (!perm.granted) {
        setErrorMessage(
          'Microphone permission is required for voice input. Please enable it in Settings or type your meal description below.',
        );
        return;
      }

      startSpeechRecognition({
        lang: 'en-US',
        interimResults: true,
        continuous: true,
        volumeChangeEventOptions: {
          enabled: true,
          intervalMillis: 100,
        },
      });
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : String(err);
      setErrorMessage(`Could not start speech recognition: ${msg}`);
      setIsListening(false);
    }
  };

  const handleStopListening = () => {
    try {
      stopSpeechRecognition();
    } catch {
      // ignore
    }
    setIsListening(false);
  };

  // Interpret spoken meal description via Gemini backend
  const handleInterpretMeal = async () => {
    const textToInterpret = transcript.trim() || interimText.trim();
    if (!textToInterpret) {
      Alert.alert(
        'Empty Description',
        'Please speak or type a food description first (e.g. "two rotis with ghee and a bowl of dal").',
      );
      return;
    }

    if (isListening) {
      handleStopListening();
    }

    setInterimInterpreting(true);
    setErrorMessage(null);

    try {
      const response = await parseVoiceMeal(textToInterpret, meal, targetDate);
      if (!response.items || response.items.length === 0) {
        setErrorMessage(
          'Could not detect any food items in the description. Please try again with specific dishes or foods.',
        );
        setInterimInterpreting(false);
        return;
      }

      const availablePool = buildAvailableFoodPool(library.data, unifiedFoods);
      const matched = matchVoiceItemsToCatalogue(response.items, availablePool);

      setMealSummary(response.summary || textToInterpret);
      setWarnings(response.warnings || []);
      setClarifyingQuestions(response.clarifying_questions || []);
      setCandidates(matched);
      setStep('review');
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : String(err);
      setErrorMessage(msg);
    } finally {
      setInterimInterpreting(false);
    }
  };

  // Candidate adjustments
  const updateCandidateGrams = (id: string, text: string) => {
    const nextGrams = parseFloat(text.replace(',', '.'));
    setCandidates((prev) =>
      prev.map((item) => {
        if (item.id !== id) return item;
        if (isNaN(nextGrams) || nextGrams <= 0) {
          return {
            ...item,
            estimated_grams: 0,
            calories: 0,
            protein: 0,
            carbohydrates: 0,
            fat: 0,
          };
        }
        const scaled = scaleNutrients(item.reference, nextGrams);
        return {
          ...item,
          estimated_grams: Math.round(nextGrams * 10) / 10,
          calories: Math.round((scaled.calories ?? 0) * 10) / 10,
          protein: Math.round((scaled.protein ?? 0) * 10) / 10,
          carbohydrates: Math.round((scaled.carbs ?? 0) * 10) / 10,
          fat: Math.round((scaled.fat ?? 0) * 10) / 10,
        };
      }),
    );
  };

  const updateCandidateName = (id: string, name: string) => {
    setCandidates((prev) =>
      prev.map((item) =>
        item.id === id ? { ...item, food_name: name } : item,
      ),
    );
  };

  const toggleCandidateSourceMode = (id: string) => {
    setCandidates((prev) =>
      prev.map((item) => {
        if (item.id !== id) return item;
        if (!item.matchedCatalogueFood) return item;

        const nextMode = item.sourceMode === 'catalogue' ? 'ai' : 'catalogue';
        const grams = item.estimated_grams > 0 ? item.estimated_grams : 100;

        if (nextMode === 'catalogue') {
          const scaled = scaleNutrients(
            item.matchedCatalogueFood.nutrients,
            grams,
          );
          return {
            ...item,
            sourceMode: 'catalogue',
            food_name: item.matchedCatalogueFood.name,
            reference: { ...item.matchedCatalogueFood.nutrients },
            calories: Math.round((scaled.calories ?? 0) * 10) / 10,
            protein: Math.round((scaled.protein ?? 0) * 10) / 10,
            carbohydrates: Math.round((scaled.carbs ?? 0) * 10) / 10,
            fat: Math.round((scaled.fat ?? 0) * 10) / 10,
          };
        } else {
          // Revert to original AI estimate
          const aiRef = scaleNutrients(
            {
              calories: item.originalParsedItem.calories,
              protein: item.originalParsedItem.protein,
              carbs: item.originalParsedItem.carbohydrates,
              fat: item.originalParsedItem.fat,
              fiber: 0,
            },
            10000 / (item.originalParsedItem.estimated_grams || 100),
          );
          const scaled = scaleNutrients(aiRef, grams);
          return {
            ...item,
            sourceMode: 'ai',
            food_name: item.originalParsedItem.food_description,
            reference: aiRef,
            calories: Math.round((scaled.calories ?? 0) * 10) / 10,
            protein: Math.round((scaled.protein ?? 0) * 10) / 10,
            carbohydrates: Math.round((scaled.carbs ?? 0) * 10) / 10,
            fat: Math.round((scaled.fat ?? 0) * 10) / 10,
          };
        }
      }),
    );
  };

  const selectAlternativeFood = (candidateId: string, food: Food) => {
    setCandidates((prev) =>
      prev.map((item) => {
        if (item.id !== candidateId) return item;
        const grams = item.estimated_grams > 0 ? item.estimated_grams : 100;
        const scaled = scaleNutrients(food.nutrients, grams);
        return {
          ...item,
          matchedCatalogueFood: food,
          sourceMode: 'catalogue',
          food_name: food.name,
          preparation: food.preparation,
          reference: { ...food.nutrients },
          calories: Math.round((scaled.calories ?? 0) * 10) / 10,
          protein: Math.round((scaled.protein ?? 0) * 10) / 10,
          carbohydrates: Math.round((scaled.carbs ?? 0) * 10) / 10,
          fat: Math.round((scaled.fat ?? 0) * 10) / 10,
        };
      }),
    );
  };

  const deleteCandidate = (id: string) => {
    setCandidates((prev) => prev.filter((item) => item.id !== id));
  };

  const addBlankCandidate = () => {
    const newId = `voice-manual-${Date.now()}`;
    const newCandidate: MatchedVoiceFoodCandidate = {
      id: newId,
      stableEntryId: randomUUID(),
      originalParsedItem: {
        food_description: 'Custom Item',
        quantity: 1,
        unit: 'serving',
        state: 'cooked',
        estimated_grams: 100,
        calories: 100,
        protein: 5,
        carbohydrates: 15,
        fat: 2,
        confidence: 1,
        confidence_level: 'high',
        alternatives: [],
      },
      food_name: 'Custom Food Item',
      quantity: 1,
      unit: 'serving',
      estimated_grams: 100,
      calories: 100,
      protein: 5,
      carbohydrates: 15,
      fat: 2,
      state: 'cooked',
      preparation: 'User added item',
      notes: '',
      confidence: 1,
      confidence_level: 'high',
      matchedCatalogueFood: null,
      availableMatches: [],
      sourceMode: 'ai',
      reference: { calories: 100, protein: 5, carbs: 15, fat: 2, fiber: 0 },
    };
    setCandidates((prev) => [...prev, newCandidate]);
  };

  // Total meal nutrition calculation
  const totals = useMemo(() => {
    return candidates.reduce(
      (acc, item) => ({
        calories: acc.calories + item.calories,
        protein: acc.protein + item.protein,
        carbs: acc.carbs + item.carbohydrates,
        fat: acc.fat + item.fat,
        grams: acc.grams + item.estimated_grams,
      }),
      { calories: 0, protein: 0, carbs: 0, fat: 0, grams: 0 },
    );
  }, [candidates]);

  // Confirm and log to diary atomically
  const handleConfirmLog = async () => {
    if (saving || candidates.length === 0) {
      if (!saving) {
        Alert.alert('No Items', 'There are no items in this meal to log.');
      }
      return;
    }

    try {
      const entriesToSave = buildDiaryEntriesFromVoiceCandidates(
        candidates,
        meal,
        targetDate,
      );

      setSaving(true);
      await diary.saveAll(entriesToSave);

      resetState();
      onClose();
      if (onSuccess) onSuccess();
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : String(err);
      Alert.alert('Save Failed', `Could not save meal to diary: ${msg}`);
    } finally {
      setSaving(false);
    }
  };

  return (
    <Modal
      visible={visible}
      animationType="slide"
      transparent={false}
      onRequestClose={handleClose}
    >
      <KeyboardAvoidingView
        style={[styles.container, { backgroundColor: t.colors.background }]}
        behavior={Platform.OS === 'ios' ? 'padding' : undefined}
      >
        {/* Header */}
        <View style={[styles.header, { borderBottomColor: t.colors.border }]}>
          <Text style={[styles.headerTitle, { color: t.colors.text }]}>
            Voice Food Logging
          </Text>
          <Pressable
            accessibilityRole="button"
            accessibilityLabel="Close Voice Logging"
            onPress={handleClose}
            style={({ pressed }) => [
              styles.closeBtn,
              pressed && { opacity: 0.6 },
            ]}
          >
            <Text style={[styles.closeBtnText, { color: t.colors.secondary }]}>
              Cancel
            </Text>
          </Pressable>
        </View>

        <ScrollView
          contentContainerStyle={[
            styles.scrollContent,
            { paddingBottom: t.spacing.xxl * 3 },
          ]}
          keyboardShouldPersistTaps="handled"
        >
          {/* Target Meal & Date banner */}
          <View
            style={[styles.metaBadge, { backgroundColor: t.colors.accent }]}
          >
            <Text style={[styles.metaText, { color: t.colors.primary }]}>
              Logging to {meal} · {targetDate}
            </Text>
          </View>

          {/* Error notice */}
          {errorMessage ? (
            <View
              style={[
                styles.errorCard,
                {
                  backgroundColor: '#FDEDEC',
                  borderColor: '#E74C3C',
                },
              ]}
            >
              <Text
                style={{ color: '#922B21', fontSize: 13, fontWeight: '500' }}
              >
                {errorMessage}
              </Text>
            </View>
          ) : null}

          {/* STEP 1: CAPTURE VOICE / TEXT */}
          {step === 'capture' && (
            <View style={{ gap: t.spacing.lg }}>
              {/* Mic action area */}
              <View
                style={[
                  styles.micAreaCard,
                  {
                    backgroundColor: t.colors.surface,
                    borderColor: t.colors.border,
                  },
                ]}
              >
                <Text
                  style={[styles.micInstructions, { color: t.colors.muted }]}
                >
                  {isListening
                    ? 'Listening... Speak naturally (dishes, portions, or preparations):'
                    : isNativeSupported
                      ? 'Tap the microphone to speak your meal, or type directly below:'
                      : 'Type your meal description below, or use your keyboard microphone:'}
                </Text>

                {!isNativeSupported && (
                  <View
                    style={[
                      styles.devBuildNotice,
                      {
                        backgroundColor: t.colors.accent,
                        borderColor: t.colors.border,
                      },
                    ]}
                  >
                    <Text
                      style={[
                        styles.devBuildNoticeTitle,
                        { color: t.colors.primary },
                      ]}
                    >
                      💡 Development Build Feature
                    </Text>
                    <Text
                      style={[
                        styles.devBuildNoticeText,
                        { color: t.colors.text },
                      ]}
                    >
                      Direct microphone recording requires a native development
                      build because third-party native code is not bundled into
                      stock Expo Go.
                      {'\n\n'}
                      You can still log meals with your voice: tap the
                      microphone icon on your mobile keyboard to dictate into
                      the box below, or type your food description!
                    </Text>
                  </View>
                )}

                {/* Big pulse mic button */}
                <View style={styles.micButtonContainer}>
                  <Pressable
                    accessibilityRole="button"
                    accessibilityLabel={
                      isListening
                        ? 'Stop recording voice'
                        : 'Start recording voice'
                    }
                    onPress={
                      isListening ? handleStopListening : handleStartListening
                    }
                    style={({ pressed }) => [
                      styles.micButton,
                      {
                        backgroundColor: isListening
                          ? '#E74C3C'
                          : t.colors.primary,
                        transform: [{ scale: pressed ? 0.94 : 1.0 }],
                      },
                    ]}
                  >
                    <Text style={styles.micButtonText}>
                      {isListening
                        ? '⏹ Stop'
                        : isNativeSupported
                          ? '🎙 Speak'
                          : '🎙 Speak (Dev Build Required)'}
                    </Text>
                  </Pressable>
                </View>

                {/* Visual Audio meter while listening */}
                {isListening && (
                  <View style={styles.meterContainer}>
                    <View
                      style={[
                        styles.meterBar,
                        {
                          width: `${Math.max(10, Math.min(100, volume * 10))}%`,
                          backgroundColor: '#E74C3C',
                        },
                      ]}
                    />
                    <Text
                      style={[styles.meterLabel, { color: t.colors.muted }]}
                    >
                      {'Recording audio... Tap "Stop" when done'}
                    </Text>
                  </View>
                )}

                {/* Suggestions chips */}
                <View style={styles.suggestionsContainer}>
                  <Text
                    style={[
                      styles.suggestionHeading,
                      { color: t.colors.muted },
                    ]}
                  >
                    Try saying:
                  </Text>
                  <Text
                    style={[styles.suggestionExample, { color: t.colors.text }]}
                  >
                    {'• "Two rotis with ghee and a bowl of dal tadka"'}
                  </Text>
                  <Text
                    style={[styles.suggestionExample, { color: t.colors.text }]}
                  >
                    {
                      '• "Two scrambled eggs, a slice of sourdough toast with butter, and black coffee"'
                    }
                  </Text>
                  <Text
                    style={[styles.suggestionExample, { color: t.colors.text }]}
                  >
                    {
                      '• "One banana, actually make that two bananas and a scoop of whey protein"'
                    }
                  </Text>
                </View>
              </View>

              {/* Editable Transcript Area */}
              <View
                style={[
                  styles.transcriptCard,
                  {
                    backgroundColor: t.colors.surface,
                    borderColor: t.colors.border,
                  },
                ]}
              >
                <View style={styles.transcriptHeaderRow}>
                  <Text
                    style={[styles.transcriptHeading, { color: t.colors.text }]}
                  >
                    Meal Transcript (Editable)
                  </Text>
                  {transcript.length > 0 && (
                    <Pressable
                      accessibilityRole="button"
                      accessibilityLabel="Clear transcript text"
                      onPress={() => {
                        setTranscript('');
                        setInterimText('');
                      }}
                      style={styles.clearBtn}
                    >
                      <Text
                        style={{
                          color: t.colors.secondary,
                          fontSize: 12,
                          fontWeight: '600',
                        }}
                      >
                        Clear
                      </Text>
                    </Pressable>
                  )}
                </View>

                <TextInput
                  style={[
                    styles.transcriptInput,
                    {
                      color: t.colors.text,
                      backgroundColor: t.colors.background,
                      borderColor: t.colors.border,
                    },
                  ]}
                  multiline
                  numberOfLines={4}
                  placeholder="Your transcribed meal will appear here. You can also type or edit anytime..."
                  placeholderTextColor={t.colors.muted}
                  value={
                    isListening && interimText
                      ? `${transcript} ${interimText}`.trim()
                      : transcript
                  }
                  onChangeText={setTranscript}
                  editable={!interpreting}
                />

                <View style={{ marginTop: 12 }}>
                  <Action
                    variant="primary"
                    label={
                      interpreting
                        ? 'Analyzing Speech with Gemini...'
                        : 'Interpret Spoken Meal'
                    }
                    onPress={handleInterpretMeal}
                    disabled={
                      interpreting ||
                      (!transcript.trim() && !interimText.trim())
                    }
                  />
                </View>
              </View>
            </View>
          )}

          {/* STEP 2: REVIEW CANDIDATES & NUTRITION */}
          {step === 'review' && (
            <View style={{ gap: t.spacing.md }}>
              {/* Summary and warnings */}
              <View
                style={[
                  styles.summaryCard,
                  {
                    backgroundColor: t.colors.surface,
                    borderColor: t.colors.border,
                  },
                ]}
              >
                <Text style={[styles.summaryTitle, { color: t.colors.text }]}>
                  Parsed Meal Summary
                </Text>
                <Text style={[styles.summaryText, { color: t.colors.muted }]}>
                  {mealSummary || transcript}
                </Text>

                {warnings.length > 0 && (
                  <View style={styles.warningsList}>
                    {warnings.map((w, i) => (
                      <Text key={i} style={styles.warningItem}>
                        💡 {w}
                      </Text>
                    ))}
                  </View>
                )}

                {clarifyingQuestions.length > 0 && (
                  <View style={styles.questionsList}>
                    {clarifyingQuestions.map((q, i) => (
                      <Text key={i} style={styles.questionItem}>
                        ❓ {q}
                      </Text>
                    ))}
                  </View>
                )}

                <Pressable
                  accessibilityRole="button"
                  accessibilityLabel="Re-record or edit transcript"
                  onPress={() => setStep('capture')}
                  style={styles.reRecordBtn}
                >
                  <Text
                    style={[styles.reRecordText, { color: t.colors.primary }]}
                  >
                    ✏️ Re-record or edit spoken text
                  </Text>
                </Pressable>
              </View>

              {/* Food Items List */}
              <View style={styles.candidatesHeaderRow}>
                <Text
                  style={[styles.candidatesHeading, { color: t.colors.text }]}
                >
                  Detected Food Items ({candidates.length})
                </Text>
                <Pressable
                  accessibilityRole="button"
                  accessibilityLabel="Add an extra food item"
                  onPress={addBlankCandidate}
                  style={styles.addCandidateBtn}
                >
                  <Text
                    style={{
                      color: t.colors.primary,
                      fontWeight: '700',
                      fontSize: 13,
                    }}
                  >
                    + Add Item
                  </Text>
                </Pressable>
              </View>

              {candidates.map((item, idx) => (
                <View
                  key={item.id}
                  style={[
                    styles.candidateCard,
                    {
                      backgroundColor: t.colors.surface,
                      borderColor: t.colors.border,
                    },
                  ]}
                >
                  {/* Card top row: Name + Delete */}
                  <View style={styles.candidateHeaderRow}>
                    <View style={{ flex: 1 }}>
                      <TextInput
                        style={[
                          styles.candidateNameInput,
                          {
                            color: t.colors.text,
                            borderBottomColor: t.colors.border,
                          },
                        ]}
                        value={item.food_name}
                        onChangeText={(name) =>
                          updateCandidateName(item.id, name)
                        }
                        placeholder="Food name"
                        placeholderTextColor={t.colors.muted}
                      />
                    </View>
                    <Pressable
                      accessibilityRole="button"
                      accessibilityLabel={`Delete ${item.food_name}`}
                      onPress={() => deleteCandidate(item.id)}
                      style={styles.deleteBtn}
                    >
                      <Text style={styles.deleteBtnText}>✕ Remove</Text>
                    </Pressable>
                  </View>

                  {/* Metadata tags: State & Catalogue match */}
                  <View style={styles.tagsRow}>
                    {item.state !== 'unspecified' && (
                      <View
                        style={[
                          styles.stateBadge,
                          {
                            backgroundColor:
                              item.state === 'raw' ? '#FADBD8' : '#D4EFDF',
                          },
                        ]}
                      >
                        <Text
                          style={[
                            styles.stateBadgeText,
                            {
                              color:
                                item.state === 'raw' ? '#78281F' : '#145A32',
                            },
                          ]}
                        >
                          {item.state === 'raw' ? '🥩 Raw weight' : '🍳 Cooked'}
                        </Text>
                      </View>
                    )}

                    {item.matchedCatalogueFood ? (
                      <Pressable
                        accessibilityRole="button"
                        accessibilityLabel={`Switch nutrition source for ${item.food_name}`}
                        onPress={() => toggleCandidateSourceMode(item.id)}
                        style={[
                          styles.sourceModeChip,
                          {
                            backgroundColor:
                              item.sourceMode === 'catalogue'
                                ? '#E8F8F5'
                                : '#FEF9E7',
                            borderColor:
                              item.sourceMode === 'catalogue'
                                ? '#1ABC9C'
                                : '#F1C40F',
                          },
                        ]}
                      >
                        <Text
                          style={[
                            styles.sourceModeText,
                            {
                              color:
                                item.sourceMode === 'catalogue'
                                  ? '#0E6251'
                                  : '#7D6608',
                            },
                          ]}
                        >
                          {item.sourceMode === 'catalogue'
                            ? `✓ Catalogue (${item.matchedCatalogueFood.status}): ${item.matchedCatalogueFood.name}`
                            : 'AI Estimate (tap to use catalogue)'}
                        </Text>
                      </Pressable>
                    ) : (
                      <View
                        style={[
                          styles.sourceModeChip,
                          {
                            backgroundColor: '#FEF9E7',
                            borderColor: '#F1C40F',
                          },
                        ]}
                      >
                        <Text
                          style={[styles.sourceModeText, { color: '#7D6608' }]}
                        >
                          AI-derived estimate
                        </Text>
                      </View>
                    )}
                  </View>

                  {/* Alternative Catalogue Matches selector */}
                  {item.availableMatches.length > 1 && (
                    <View style={styles.alternativesSection}>
                      <Text
                        style={[
                          styles.alternativesLabel,
                          { color: t.colors.muted },
                        ]}
                      >
                        Match alternative:
                      </Text>
                      <ScrollView
                        horizontal
                        showsHorizontalScrollIndicator={false}
                        contentContainerStyle={styles.alternativesScroll}
                      >
                        {item.availableMatches.map((altFood) => {
                          const isCurrent =
                            item.matchedCatalogueFood?.id === altFood.id &&
                            item.sourceMode === 'catalogue';
                          return (
                            <Pressable
                              key={altFood.id}
                              accessibilityRole="button"
                              accessibilityLabel={`Select ${altFood.name}`}
                              onPress={() =>
                                selectAlternativeFood(item.id, altFood)
                              }
                              style={[
                                styles.altChip,
                                {
                                  backgroundColor: isCurrent
                                    ? t.colors.primary
                                    : t.colors.background,
                                  borderColor: isCurrent
                                    ? t.colors.primary
                                    : t.colors.border,
                                },
                              ]}
                            >
                              <Text
                                style={[
                                  styles.altChipText,
                                  {
                                    color: isCurrent
                                      ? '#FFFFFF'
                                      : t.colors.text,
                                  },
                                ]}
                              >
                                {altFood.name}
                              </Text>
                            </Pressable>
                          );
                        })}
                      </ScrollView>
                    </View>
                  )}

                  {/* Portion editor row */}
                  <View style={styles.portionRow}>
                    <View style={styles.portionInputGroup}>
                      <Text
                        style={[styles.fieldLabel, { color: t.colors.muted }]}
                      >
                        Portion (grams):
                      </Text>
                      <TextInput
                        style={[
                          styles.gramsInput,
                          {
                            color: t.colors.text,
                            backgroundColor: t.colors.background,
                            borderColor: t.colors.border,
                          },
                        ]}
                        keyboardType="decimal-pad"
                        value={String(item.estimated_grams)}
                        onChangeText={(txt) =>
                          updateCandidateGrams(item.id, txt)
                        }
                      />
                    </View>

                    <View style={styles.spokenUnitBadge}>
                      <Text
                        style={[
                          styles.spokenUnitText,
                          { color: t.colors.muted },
                        ]}
                      >
                        {item.quantity} {item.unit}
                      </Text>
                    </View>
                  </View>

                  {/* Macro chips */}
                  <View style={styles.macroGrid}>
                    <View
                      style={[
                        styles.macroBox,
                        { backgroundColor: t.colors.background },
                      ]}
                    >
                      <Text
                        style={[styles.macroLabel, { color: t.colors.muted }]}
                      >
                        Calories
                      </Text>
                      <Text
                        style={[styles.macroValue, { color: t.colors.text }]}
                      >
                        {Math.round(item.calories)} kcal
                      </Text>
                    </View>

                    <View
                      style={[
                        styles.macroBox,
                        { backgroundColor: t.colors.background },
                      ]}
                    >
                      <Text
                        style={[styles.macroLabel, { color: t.colors.muted }]}
                      >
                        Protein
                      </Text>
                      <Text
                        style={[styles.macroValue, { color: t.colors.text }]}
                      >
                        {item.protein.toFixed(1)}g
                      </Text>
                    </View>

                    <View
                      style={[
                        styles.macroBox,
                        { backgroundColor: t.colors.background },
                      ]}
                    >
                      <Text
                        style={[styles.macroLabel, { color: t.colors.muted }]}
                      >
                        Carbs
                      </Text>
                      <Text
                        style={[styles.macroValue, { color: t.colors.text }]}
                      >
                        {item.carbohydrates.toFixed(1)}g
                      </Text>
                    </View>

                    <View
                      style={[
                        styles.macroBox,
                        { backgroundColor: t.colors.background },
                      ]}
                    >
                      <Text
                        style={[styles.macroLabel, { color: t.colors.muted }]}
                      >
                        Fat
                      </Text>
                      <Text
                        style={[styles.macroValue, { color: t.colors.text }]}
                      >
                        {item.fat.toFixed(1)}g
                      </Text>
                    </View>
                  </View>
                </View>
              ))}
            </View>
          )}
        </ScrollView>

        {/* Footer Bar for Review Step */}
        {step === 'review' && (
          <View
            style={[
              styles.footerBar,
              {
                backgroundColor: t.colors.surface,
                borderTopColor: t.colors.border,
              },
            ]}
          >
            <View style={styles.footerTotals}>
              <View>
                <Text
                  style={[styles.footerTotalsTitle, { color: t.colors.text }]}
                >
                  Meal Total: {Math.round(totals.calories)} kcal
                </Text>
                <Text
                  style={[styles.footerTotalsSub, { color: t.colors.muted }]}
                >
                  P: {totals.protein.toFixed(1)}g · C: {totals.carbs.toFixed(1)}
                  g · F: {totals.fat.toFixed(1)}g ({Math.round(totals.grams)}g
                  total)
                </Text>
              </View>
            </View>

            <View style={styles.footerActionRow}>
              <Action
                variant="primary"
                label={saving ? 'Logging Meal...' : 'Confirm & Log to Diary'}
                onPress={handleConfirmLog}
                disabled={saving || candidates.length === 0}
              />
            </View>
          </View>
        )}
      </KeyboardAvoidingView>
    </Modal>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 16,
    paddingVertical: 14,
    borderBottomWidth: 1,
  },
  headerTitle: {
    fontSize: 18,
    fontWeight: '700',
  },
  closeBtn: {
    padding: 8,
    minHeight: 44,
    minWidth: 44,
    justifyContent: 'center',
    alignItems: 'center',
  },
  closeBtnText: {
    fontSize: 15,
    fontWeight: '600',
  },
  scrollContent: {
    padding: 16,
    gap: 16,
  },
  metaBadge: {
    paddingVertical: 8,
    paddingHorizontal: 12,
    borderRadius: 8,
    alignSelf: 'flex-start',
  },
  metaText: {
    fontSize: 13,
    fontWeight: '600',
  },
  errorCard: {
    padding: 12,
    borderRadius: 8,
    borderWidth: 1,
  },
  micAreaCard: {
    padding: 18,
    borderRadius: 12,
    borderWidth: 1,
    alignItems: 'center',
    gap: 16,
  },
  micInstructions: {
    fontSize: 14,
    textAlign: 'center',
    lineHeight: 20,
  },
  devBuildNotice: {
    padding: 12,
    borderRadius: 8,
    borderWidth: 1,
    gap: 4,
    width: '100%',
  },
  devBuildNoticeTitle: {
    fontSize: 13,
    fontWeight: '700',
  },
  devBuildNoticeText: {
    fontSize: 12,
    lineHeight: 18,
  },
  micButtonContainer: {
    marginVertical: 4,
  },
  micButton: {
    width: 110,
    height: 110,
    borderRadius: 55,
    justifyContent: 'center',
    alignItems: 'center',
    elevation: 3,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.2,
    shadowRadius: 4,
  },
  micButtonText: {
    color: '#FFFFFF',
    fontSize: 18,
    fontWeight: '700',
  },
  meterContainer: {
    width: '100%',
    alignItems: 'center',
    gap: 6,
  },
  meterBar: {
    height: 6,
    borderRadius: 3,
  },
  meterLabel: {
    fontSize: 12,
    fontStyle: 'italic',
  },
  suggestionsContainer: {
    width: '100%',
    marginTop: 8,
    paddingTop: 12,
    borderTopWidth: StyleSheet.hairlineWidth,
    borderTopColor: '#E0E0E0',
    gap: 4,
  },
  suggestionHeading: {
    fontSize: 12,
    fontWeight: '700',
    marginBottom: 2,
  },
  suggestionExample: {
    fontSize: 13,
    lineHeight: 18,
  },
  transcriptCard: {
    padding: 16,
    borderRadius: 12,
    borderWidth: 1,
    gap: 8,
  },
  transcriptHeaderRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  transcriptHeading: {
    fontSize: 15,
    fontWeight: '700',
  },
  clearBtn: {
    padding: 6,
    minHeight: 44,
    justifyContent: 'center',
  },
  transcriptInput: {
    borderWidth: 1,
    borderRadius: 8,
    padding: 12,
    fontSize: 15,
    minHeight: 90,
    textAlignVertical: 'top',
  },
  summaryCard: {
    padding: 14,
    borderRadius: 12,
    borderWidth: 1,
    gap: 8,
  },
  summaryTitle: {
    fontSize: 15,
    fontWeight: '700',
  },
  summaryText: {
    fontSize: 14,
    lineHeight: 20,
  },
  warningsList: {
    marginTop: 4,
    gap: 4,
  },
  warningItem: {
    fontSize: 12,
    color: '#D35400',
    lineHeight: 16,
  },
  questionsList: {
    marginTop: 4,
    gap: 4,
  },
  questionItem: {
    fontSize: 12,
    color: '#2980B9',
    lineHeight: 16,
  },
  reRecordBtn: {
    alignSelf: 'flex-start',
    marginTop: 4,
    minHeight: 44,
    justifyContent: 'center',
  },
  reRecordText: {
    fontSize: 13,
    fontWeight: '600',
  },
  candidatesHeaderRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginTop: 4,
  },
  candidatesHeading: {
    fontSize: 16,
    fontWeight: '700',
  },
  addCandidateBtn: {
    padding: 8,
    minHeight: 44,
    justifyContent: 'center',
  },
  candidateCard: {
    padding: 14,
    borderRadius: 12,
    borderWidth: 1,
    gap: 12,
  },
  candidateHeaderRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  candidateNameInput: {
    fontSize: 16,
    fontWeight: '700',
    borderBottomWidth: 1,
    paddingVertical: 4,
  },
  deleteBtn: {
    paddingHorizontal: 8,
    paddingVertical: 6,
    minHeight: 44,
    justifyContent: 'center',
  },
  deleteBtnText: {
    color: '#E74C3C',
    fontSize: 13,
    fontWeight: '600',
  },
  tagsRow: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
    alignItems: 'center',
  },
  stateBadge: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 6,
  },
  stateBadgeText: {
    fontSize: 11,
    fontWeight: '700',
  },
  sourceModeChip: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 6,
    borderWidth: 1,
    minHeight: 30,
    justifyContent: 'center',
  },
  sourceModeText: {
    fontSize: 11,
    fontWeight: '600',
  },
  alternativesSection: {
    gap: 6,
  },
  alternativesLabel: {
    fontSize: 12,
    fontWeight: '500',
  },
  alternativesScroll: {
    gap: 8,
  },
  altChip: {
    paddingHorizontal: 10,
    paddingVertical: 6,
    borderRadius: 16,
    borderWidth: 1,
    minHeight: 36,
    justifyContent: 'center',
  },
  altChipText: {
    fontSize: 12,
    fontWeight: '600',
  },
  portionRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    gap: 12,
  },
  portionInputGroup: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  fieldLabel: {
    fontSize: 13,
    fontWeight: '500',
  },
  gramsInput: {
    borderWidth: 1,
    borderRadius: 8,
    paddingHorizontal: 10,
    paddingVertical: 6,
    fontSize: 15,
    fontWeight: '700',
    minWidth: 70,
    textAlign: 'center',
    minHeight: 44,
  },
  spokenUnitBadge: {
    paddingVertical: 4,
    paddingHorizontal: 8,
  },
  spokenUnitText: {
    fontSize: 12,
    fontStyle: 'italic',
  },
  macroGrid: {
    flexDirection: 'row',
    gap: 8,
  },
  macroBox: {
    flex: 1,
    padding: 8,
    borderRadius: 8,
    alignItems: 'center',
  },
  macroLabel: {
    fontSize: 11,
    fontWeight: '500',
    marginBottom: 2,
  },
  macroValue: {
    fontSize: 13,
    fontWeight: '700',
  },
  footerBar: {
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
    borderTopWidth: StyleSheet.hairlineWidth,
    padding: 16,
    gap: 12,
  },
  footerTotals: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'baseline',
  },
  footerTotalsTitle: {
    fontSize: 16,
    fontWeight: '700',
  },
  footerTotalsSub: {
    fontSize: 13,
  },
  footerActionRow: {
    width: '100%',
  },
});
