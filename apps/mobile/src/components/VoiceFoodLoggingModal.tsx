/**
 * Audio-Native Voice Food Logging Modal for Bites2Go.
 *
 * Clean 5-stage meal logging flow:
 * 1. Tap to speak (direct microphone audio capture via expo-audio)
 * 2. Stop recording (enforces duration <=90s, size <=10MB, and cancellation)
 * 3. AI interprets meal (uploads audio securely over HTTPS; server processes in memory)
 * 4. Review & edit items (honest uncertainty, modifiers without invented weights, catalogue switching)
 * 5. Confirm and log atomically to SQLite via DiaryProvider
 *
 * Privacy & Hygiene:
 * - Audio is captured locally to a temporary cache file ONLY when recording starts.
 * - Audio leaves the device over HTTPS only after Stop is tapped (or explicit retry).
 * - Temporary local audio files are deleted immediately on success, cancel, retry switch, close, or unmount.
 */

import React, {
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
} from 'react';
import {
  ActivityIndicator,
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

import { useUI } from './dashboard';
import { Action } from './FoodControls';
import { useDiary } from '../state/DiaryProvider';
import { useLibrary } from '../state/LibraryProvider';
import { localDateKey, validDateKey } from '../domain/diary';
import {
  formatNutrient,
  scaleNutrients,
  sumNutrients,
  type Food,
  type Meal,
} from '../domain/food';
import { unifiedFoods } from '../data/unifiedFoods';
import {
  MAX_AUDIO_DURATION_MS,
  buildAvailableFoodPool,
  buildDiaryEntriesFromVoiceCandidates,
  matchVoiceItemsToCatalogue,
  parseVoiceAudio,
  parseVoiceMeal,
  scaleFoodNutrientsNullable,
  type MatchedVoiceFoodCandidate,
  VoiceCloudError,
} from '../services/voiceFoodLogging';
import {
  buildMealRecordingOptions,
  configureRecordingAudioMode,
  deleteTempAudioFile,
  getSafeExpoAudioModule,
  inspectTempAudioFileSize,
  isAudioCaptureAvailable,
  requestMicrophonePermission,
  validateRecordedAudioMetadata,
} from '../services/audioRecordingService';

export type VoiceFoodLoggingModalProps = {
  visible: boolean;
  meal: Meal;
  date?: string | null;
  onClose: () => void;
  onSuccess?: () => void;
  onOpenFoodSearch?: () => void;
};

type VoiceModalStage = 'idle' | 'recording' | 'analyzing' | 'review';

function formatTimer(durationMs: number): string {
  const totalSec = Math.max(0, Math.floor(durationMs / 1000));
  const mins = Math.floor(totalSec / 60);
  const secs = totalSec % 60;
  return `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
}

type NativeRecorderSessionProps = {
  stage: VoiceModalStage;
  disabled: boolean;
  t: ReturnType<typeof useUI>['t'];
  onRecordingStarted: () => void;
  onRecordingFinished: (uri: string, durationMillis: number) => void;
  onRecordingError: (msg: string) => void;
  onRecordingCancelled: () => void;
};

/**
 * Isolated child component calling expo-audio hooks cleanly only when ExpoAudio exists natively.
 */
function NativeAudioRecorderPanel({
  stage,
  disabled,
  t,
  onRecordingStarted,
  onRecordingFinished,
  onRecordingError,
  onRecordingCancelled,
}: NativeRecorderSessionProps) {
  const audioMod = useMemo(() => getSafeExpoAudioModule(), []);
  const options = useMemo(() => buildMealRecordingOptions(), []);

  if (!audioMod || !options) {
    return null;
  }

  return (
    <InnerNativeAudioRecorder
      audioMod={audioMod}
      options={options}
      stage={stage}
      disabled={disabled}
      t={t}
      onRecordingStarted={onRecordingStarted}
      onRecordingFinished={onRecordingFinished}
      onRecordingError={onRecordingError}
      onRecordingCancelled={onRecordingCancelled}
    />
  );
}

type InnerNativeRecorderProps = NativeRecorderSessionProps & {
  audioMod: NonNullable<ReturnType<typeof getSafeExpoAudioModule>>;
  options: NonNullable<ReturnType<typeof buildMealRecordingOptions>>;
};

function InnerNativeAudioRecorder({
  audioMod,
  options,
  stage,
  disabled,
  t,
  onRecordingStarted,
  onRecordingFinished,
  onRecordingError,
  onRecordingCancelled,
}: InnerNativeRecorderProps) {
  const recorder = audioMod.useAudioRecorder(options);
  const recorderState = audioMod.useAudioRecorderState(recorder, 200);
  const stoppingRef = useRef(false);
  const autoStoppedRef = useRef(false);

  const handleStopAndSend = useCallback(async () => {
    if (stoppingRef.current) return;
    stoppingRef.current = true;
    const measuredDuration = recorderState.durationMillis;
    try {
      await recorder.stop();
      await configureRecordingAudioMode(false);
      const uri = recorder.uri || recorderState.url || '';
      onRecordingFinished(uri, measuredDuration);
    } catch {
      await configureRecordingAudioMode(false);
      deleteTempAudioFile(recorder.uri || recorderState.url);
      onRecordingError(
        'Could not finalize the audio recording. Please try speaking again or type your meal below.',
      );
    } finally {
      stoppingRef.current = false;
      autoStoppedRef.current = false;
    }
  }, [
    onRecordingError,
    onRecordingFinished,
    recorder,
    recorderState.durationMillis,
    recorderState.url,
  ]);

  const handleCancelRecording = useCallback(async () => {
    if (stoppingRef.current) return;
    stoppingRef.current = true;
    try {
      await recorder.stop();
    } catch {
      // ignore if already stopped
    } finally {
      await configureRecordingAudioMode(false);
      deleteTempAudioFile(recorder.uri || recorderState.url);
      stoppingRef.current = false;
      autoStoppedRef.current = false;
      onRecordingCancelled();
    }
  }, [onRecordingCancelled, recorder, recorderState.url]);

  const handleStartRecording = useCallback(async () => {
    if (disabled || stoppingRef.current) return;
    const perm = await requestMicrophonePermission();
    if (!perm.granted) {
      onRecordingError(
        perm.canAskAgain
          ? 'Microphone access is needed to record your meal. Tap Speak to allow permission, type your meal below, or open Food Search.'
          : 'Microphone access is disabled for Bites2Go. Enable Microphone in Android Settings, type your meal below, or open Food Search.',
      );
      return;
    }

    try {
      autoStoppedRef.current = false;
      await configureRecordingAudioMode(true);
      await recorder.prepareToRecordAsync();
      recorder.record();
      onRecordingStarted();
    } catch {
      await configureRecordingAudioMode(false);
      onRecordingError(
        'Unable to access the microphone right now. Ensure no other app is recording or type your meal below.',
      );
    }
  }, [disabled, onRecordingError, onRecordingStarted, recorder]);

  // Automatically finalize recording if user reaches maximum 90-second limit
  useEffect(() => {
    if (
      stage === 'recording' &&
      recorderState.durationMillis >= MAX_AUDIO_DURATION_MS &&
      !autoStoppedRef.current
    ) {
      autoStoppedRef.current = true;
      void handleStopAndSend();
    }
  }, [handleStopAndSend, recorderState.durationMillis, stage]);

  const isRec = stage === 'recording';
  // dB metering typically ranges roughly -60dB (quiet) to 0dB (loud)
  const meterPercent =
    typeof recorderState.metering === 'number'
      ? Math.max(
          12,
          Math.min(100, Math.round(((recorderState.metering + 60) / 60) * 100)),
        )
      : 40;

  return (
    <View style={{ alignItems: 'center', gap: 14 }}>
      <Pressable
        accessibilityRole="button"
        accessibilityLabel={
          isRec ? 'Stop recording and analyze meal' : 'Start speaking meal'
        }
        disabled={disabled && !isRec}
        onPress={isRec ? handleStopAndSend : handleStartRecording}
        style={({ pressed }) => [
          styles.micButton,
          {
            backgroundColor: isRec ? '#E74C3C' : t.colors.primary,
            opacity: disabled && !isRec ? 0.5 : pressed ? 0.88 : 1,
          },
        ]}
      >
        <Text style={styles.micButtonText}>
          {isRec ? '⏹ Stop & Analyze' : '🎙 Speak Meal'}
        </Text>
      </Pressable>

      {isRec && (
        <View style={styles.recordingStatusBox}>
          <Text style={[styles.timerText, { color: '#C0392B' }]}>
            ● Recording {formatTimer(recorderState.durationMillis)} /{' '}
            {formatTimer(MAX_AUDIO_DURATION_MS)}
          </Text>
          <View
            style={[styles.meterTrack, { backgroundColor: t.colors.border }]}
          >
            <View
              style={[
                styles.meterBar,
                {
                  width: `${meterPercent}%`,
                  backgroundColor: '#E74C3C',
                },
              ]}
            />
          </View>
          <Pressable
            accessibilityRole="button"
            accessibilityLabel="Cancel voice recording"
            onPress={handleCancelRecording}
            style={styles.cancelRecordingBtn}
          >
            <Text
              style={{
                color: t.colors.secondary,
                fontSize: 13,
                fontWeight: '600',
              }}
            >
              Discard Recording
            </Text>
          </Pressable>
        </View>
      )}
    </View>
  );
}

export function VoiceFoodLoggingModal({
  visible,
  meal,
  date,
  onClose,
  onSuccess,
  onOpenFoodSearch,
}: VoiceFoodLoggingModalProps) {
  const { t } = useUI();
  const diary = useDiary();
  const library = useLibrary();

  const [stage, setStage] = useState<VoiceModalStage>('idle');
  const [transcript, setTranscript] = useState('');
  const [lastAudioUri, setLastAudioUri] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  const [mealSummary, setMealSummary] = useState('');
  const [warnings, setWarnings] = useState<string[]>([]);
  const [clarifyingQuestions, setClarifyingQuestions] = useState<string[]>([]);
  const [candidates, setCandidates] = useState<MatchedVoiceFoodCandidate[]>([]);

  const activeAudioUriRef = useRef<string | null>(null);
  const uploadAbortRef = useRef<AbortController | null>(null);
  const savingRef = useRef(false);

  const nativeAudioSupported = useMemo(() => isAudioCaptureAvailable(), []);

  const targetDate = useMemo(() => {
    return date && validDateKey(date) ? date : localDateKey();
  }, [date]);

  const cleanupTempAudio = useCallback(() => {
    if (activeAudioUriRef.current) {
      deleteTempAudioFile(activeAudioUriRef.current);
      activeAudioUriRef.current = null;
    }
    setLastAudioUri(null);
  }, []);

  const abortOngoingUpload = useCallback(() => {
    if (uploadAbortRef.current) {
      uploadAbortRef.current.abort();
      uploadAbortRef.current = null;
    }
  }, []);

  const resetState = useCallback(() => {
    abortOngoingUpload();
    cleanupTempAudio();
    void configureRecordingAudioMode(false);
    savingRef.current = false;
    setSaving(false);
    setStage('idle');
    setTranscript('');
    setErrorMessage(null);
    setMealSummary('');
    setWarnings([]);
    setClarifyingQuestions([]);
    setCandidates([]);
  }, [abortOngoingUpload, cleanupTempAudio]);

  useEffect(() => {
    return () => {
      if (uploadAbortRef.current) {
        uploadAbortRef.current.abort();
      }
      if (activeAudioUriRef.current) {
        deleteTempAudioFile(activeAudioUriRef.current);
        activeAudioUriRef.current = null;
      }
    };
  }, []);

  const handleClose = () => {
    if (saving) return;
    resetState();
    onClose();
  };

  const handleGoToFoodSearch = () => {
    if (saving) return;
    resetState();
    if (onOpenFoodSearch) {
      onOpenFoodSearch();
    } else {
      onClose();
    }
  };

  const submitAudioUriForAnalysis = useCallback(
    async (uri: string) => {
      abortOngoingUpload();
      const abortCtrl = new AbortController();
      uploadAbortRef.current = abortCtrl;
      setStage('analyzing');
      setErrorMessage(null);

      try {
        const response = await parseVoiceAudio(uri, meal, targetDate, {
          signal: abortCtrl.signal,
        });

        // Audio analyzed — delete local cache file immediately
        deleteTempAudioFile(uri);
        if (activeAudioUriRef.current === uri) {
          activeAudioUriRef.current = null;
        }
        setLastAudioUri(null);

        if (response.transcript?.trim()) {
          setTranscript(response.transcript.trim());
        }

        if (!response.items || response.items.length === 0) {
          setErrorMessage(
            response.warnings?.[0] ||
              'No food items were detected clearly. Try speaking closer to the mic, type your meal below, or open Food Search.',
          );
          setStage('idle');
          return;
        }

        const availablePool = buildAvailableFoodPool(
          library.data,
          unifiedFoods,
        );
        const matched = matchVoiceItemsToCatalogue(
          response.items,
          availablePool,
        );

        setMealSummary(
          response.summary || response.transcript || 'Voice Meal Summary',
        );
        setWarnings(response.warnings || []);
        setClarifyingQuestions(response.clarifying_questions || []);
        setCandidates(matched);
        setStage('review');
      } catch (err: unknown) {
        if (
          err instanceof VoiceCloudError &&
          err.errorCategory === 'upload_canceled'
        ) {
          deleteTempAudioFile(uri);
          if (activeAudioUriRef.current === uri) {
            activeAudioUriRef.current = null;
          }
          setLastAudioUri(null);
          setStage('idle');
          return;
        }
        const rawMsg =
          err instanceof Error
            ? err.message
            : 'Unable to analyze your voice recording right now.';
        setErrorMessage(rawMsg);
        setStage('idle');
      } finally {
        if (uploadAbortRef.current === abortCtrl) {
          uploadAbortRef.current = null;
        }
      }
    },
    [abortOngoingUpload, library.data, meal, targetDate],
  );

  const handleRecordingStarted = useCallback(() => {
    cleanupTempAudio();
    setErrorMessage(null);
    setStage('recording');
  }, [cleanupTempAudio]);

  const handleRecordingFinished = useCallback(
    async (uri: string, durationMillis: number) => {
      const sizeBytes = inspectTempAudioFileSize(uri);
      const validation = validateRecordedAudioMetadata({
        uri,
        durationMillis,
        sizeBytes,
      });

      if (!validation.valid) {
        deleteTempAudioFile(uri);
        setLastAudioUri(null);
        setErrorMessage(
          validation.error ||
            'Could not capture usable audio. Please try again.',
        );
        setStage('idle');
        return;
      }

      if (activeAudioUriRef.current && activeAudioUriRef.current !== uri) {
        deleteTempAudioFile(activeAudioUriRef.current);
      }
      activeAudioUriRef.current = uri;
      setLastAudioUri(uri);
      await submitAudioUriForAnalysis(uri);
    },
    [submitAudioUriForAnalysis],
  );

  const handleRecordingError = useCallback((msg: string) => {
    setErrorMessage(msg);
    setStage('idle');
  }, []);

  const handleRecordingCancelled = useCallback(() => {
    cleanupTempAudio();
    setStage('idle');
  }, [cleanupTempAudio]);

  const handleCancelUpload = () => {
    abortOngoingUpload();
    cleanupTempAudio();
    setStage('idle');
    setErrorMessage(null);
  };

  const handleInterpretEditedTranscript = async () => {
    const cleaned = transcript.trim();
    if (!cleaned) {
      Alert.alert(
        'Empty Meal Description',
        'Please speak a meal or enter food details before interpreting.',
      );
      return;
    }

    abortOngoingUpload();
    const abortCtrl = new AbortController();
    uploadAbortRef.current = abortCtrl;
    setStage('analyzing');
    setErrorMessage(null);

    try {
      const response = await parseVoiceMeal(cleaned, meal, targetDate, {
        signal: abortCtrl.signal,
      });
      if (!response.items || response.items.length === 0) {
        setErrorMessage(
          'Could not detect specific food items in that text. Edit the description or open Food Search.',
        );
        setStage('idle');
        return;
      }

      cleanupTempAudio();
      const availablePool = buildAvailableFoodPool(library.data, unifiedFoods);
      const matched = matchVoiceItemsToCatalogue(response.items, availablePool);

      setTranscript(response.transcript || cleaned);
      setMealSummary(response.summary || cleaned);
      setWarnings(response.warnings || []);
      setClarifyingQuestions(response.clarifying_questions || []);
      setCandidates(matched);
      setStage('review');
    } catch (err: unknown) {
      if (
        err instanceof VoiceCloudError &&
        err.errorCategory === 'upload_canceled'
      ) {
        setStage('idle');
        return;
      }
      setErrorMessage(
        err instanceof Error
          ? err.message
          : 'Unable to interpret meal text right now.',
      );
      setStage('idle');
    } finally {
      if (uploadAbortRef.current === abortCtrl) {
        uploadAbortRef.current = null;
      }
    }
  };

  // Candidate adjustments in review stage
  const updateCandidateGrams = (id: string, text: string) => {
    const trimmed = text.trim();
    if (!trimmed) {
      setCandidates((prev) =>
        prev.map((item) =>
          item.id === id
            ? {
                ...item,
                estimated_grams: null,
                calories: null,
                protein: null,
                carbohydrates: null,
                fat: null,
                fiber: null,
              }
            : item,
        ),
      );
      return;
    }

    const nextGrams = parseFloat(trimmed.replace(',', '.'));
    setCandidates((prev) =>
      prev.map((item) => {
        if (item.id !== id) return item;
        if (!Number.isFinite(nextGrams) || nextGrams <= 0) {
          return {
            ...item,
            estimated_grams: 0,
            calories: null,
            protein: null,
            carbohydrates: null,
            fat: null,
            fiber: null,
          };
        }
        const scaled = scaleFoodNutrientsNullable(item.reference, nextGrams);
        return {
          ...item,
          estimated_grams: Math.round(nextGrams * 10) / 10,
          calories: scaled.calories,
          protein: scaled.protein,
          carbohydrates: scaled.carbohydrates,
          fat: scaled.fat,
          fiber: scaled.fiber,
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
        if (item.id !== id || !item.matchedCatalogueFood) return item;

        const nextMode = item.sourceMode === 'catalogue' ? 'ai' : 'catalogue';
        const grams =
          item.estimated_grams !== null && item.estimated_grams > 0
            ? item.estimated_grams
            : null;

        if (nextMode === 'catalogue') {
          const ref = { ...item.matchedCatalogueFood.nutrients };
          const scaled =
            grams !== null
              ? scaleFoodNutrientsNullable(ref, grams)
              : {
                  calories: null,
                  protein: null,
                  carbohydrates: null,
                  fat: null,
                  fiber: null,
                };
          return {
            ...item,
            sourceMode: 'catalogue',
            food_name: item.matchedCatalogueFood.name,
            reference: ref,
            calories: scaled.calories,
            protein: scaled.protein,
            carbohydrates: scaled.carbohydrates,
            fat: scaled.fat,
            fiber: scaled.fiber,
          };
        }

        const orig = item.originalParsedItem;
        const origGrams = orig.estimated_grams;
        let aiRef = item.reference;
        if (
          origGrams &&
          origGrams > 0 &&
          orig.calories !== null &&
          orig.protein !== null &&
          orig.carbohydrates !== null &&
          orig.fat !== null
        ) {
          aiRef = scaleNutrients(
            {
              calories: orig.calories,
              protein: orig.protein,
              carbs: orig.carbohydrates,
              fat: orig.fat,
              fiber: 0,
            },
            10000 / origGrams,
          );
        }
        const scaled =
          grams !== null
            ? scaleFoodNutrientsNullable(aiRef, grams)
            : {
                calories: null,
                protein: null,
                carbohydrates: null,
                fat: null,
                fiber: null,
              };
        return {
          ...item,
          sourceMode: 'ai',
          food_name: orig.food_description,
          reference: aiRef,
          calories: scaled.calories,
          protein: scaled.protein,
          carbohydrates: scaled.carbohydrates,
          fat: scaled.fat,
          fiber: scaled.fiber,
        };
      }),
    );
  };

  const selectAlternativeFood = (candidateId: string, food: Food) => {
    setCandidates((prev) =>
      prev.map((item) => {
        if (item.id !== candidateId) return item;
        const grams =
          item.estimated_grams !== null && item.estimated_grams > 0
            ? item.estimated_grams
            : null;
        const scaled =
          grams !== null
            ? scaleFoodNutrientsNullable(food.nutrients, grams)
            : {
                calories: null,
                protein: null,
                carbohydrates: null,
                fat: null,
                fiber: null,
              };
        return {
          ...item,
          matchedCatalogueFood: food,
          sourceMode: 'catalogue',
          food_name: food.name,
          preparation: food.preparation,
          reference: { ...food.nutrients },
          calories: scaled.calories,
          protein: scaled.protein,
          carbohydrates: scaled.carbohydrates,
          fat: scaled.fat,
          fiber: scaled.fiber,
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
        food_description: 'Custom Food Item',
        quantity: 1,
        unit: 'serving',
        state: 'cooked',
        modifiers: [],
        portion_specified: true,
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
      fiber: 0,
      state: 'cooked',
      preparation: 'User added item',
      modifiers: [],
      portionSpecified: true,
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

  // Meal totals calculation (honestly retains Unknown when macros/portions are null)
  const totals = useMemo(() => {
    const summed = sumNutrients(
      candidates.map((c) => ({
        calories: c.calories,
        protein: c.protein,
        carbs: c.carbohydrates,
        fat: c.fat,
        fiber: c.fiber ?? null,
      })),
    );
    const grams = candidates.reduce(
      (acc, item) => acc + (item.estimated_grams ?? 0),
      0,
    );
    const missingGramsCount = candidates.filter(
      (c) => c.estimated_grams === null || c.estimated_grams <= 0,
    ).length;
    return {
      calories: summed.values.calories,
      protein: summed.values.protein,
      carbs: summed.values.carbs,
      fat: summed.values.fat,
      partial: summed.partial,
      grams,
      missingGramsCount,
    };
  }, [candidates]);

  const handleConfirmLog = async () => {
    if (savingRef.current || saving || candidates.length === 0) {
      if (!savingRef.current && !saving) {
        Alert.alert('No Items', 'There are no items in this meal to log.');
      }
      return;
    }

    const missingPortion = candidates.find(
      (c) => c.estimated_grams === null || c.estimated_grams <= 0,
    );
    if (missingPortion) {
      Alert.alert(
        'Enter Portion Weight',
        `Please enter a weight in grams for "${missingPortion.food_name}" or remove it before saving.`,
      );
      return;
    }

    savingRef.current = true;
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
      savingRef.current = false;
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
          {/* Target Meal & Date badge */}
          <View
            style={[styles.metaBadge, { backgroundColor: t.colors.accent }]}
          >
            <Text style={[styles.metaText, { color: t.colors.primary }]}>
              Logging to {meal} · {targetDate}
            </Text>
          </View>

          {/* Failure Recovery Card */}
          {errorMessage ? (
            <View
              style={[
                styles.errorCard,
                { backgroundColor: '#FDEDEC', borderColor: '#E74C3C' },
              ]}
            >
              <Text
                style={{ color: '#922B21', fontSize: 13, fontWeight: '600' }}
              >
                {errorMessage}
              </Text>
              <View style={styles.recoveryActionsRow}>
                {lastAudioUri && stage === 'idle' ? (
                  <Pressable
                    accessibilityRole="button"
                    accessibilityLabel="Retry voice audio analysis"
                    onPress={() => void submitAudioUriForAnalysis(lastAudioUri)}
                    style={[
                      styles.recoveryBtn,
                      {
                        backgroundColor: t.colors.primary,
                        borderColor: t.colors.primary,
                      },
                    ]}
                  >
                    <Text
                      style={{
                        color: '#FFFFFF',
                        fontSize: 13,
                        fontWeight: '700',
                      }}
                    >
                      Retry Audio
                    </Text>
                  </Pressable>
                ) : null}
                <Pressable
                  accessibilityRole="button"
                  accessibilityLabel="Open regular food search"
                  onPress={handleGoToFoodSearch}
                  style={[
                    styles.recoveryBtn,
                    {
                      backgroundColor: t.colors.surface,
                      borderColor: t.colors.border,
                    },
                  ]}
                >
                  <Text
                    style={{
                      color: t.colors.text,
                      fontSize: 13,
                      fontWeight: '600',
                    }}
                  >
                    Open Food Search
                  </Text>
                </Pressable>
              </View>
            </View>
          ) : null}

          {/* STAGES 1–3: RECORD AUDIO -> STOP -> ANALYZE */}
          {(stage === 'idle' ||
            stage === 'recording' ||
            stage === 'analyzing') && (
            <View style={{ gap: t.spacing.lg }}>
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
                  {stage === 'recording'
                    ? 'Speak naturally in English, Hindi, or Hinglish. Self-corrections like "actually make that two" are understood automatically.'
                    : stage === 'analyzing'
                      ? 'Listening to your recording and building editable meal items...'
                      : nativeAudioSupported
                        ? 'Tap Speak Meal and describe what you ate, including portions or corrections.'
                        : 'Microphone recording is unavailable in this runtime. Type your meal below or open Food Search.'}
                </Text>

                {stage === 'analyzing' ? (
                  <View style={styles.analyzingBox}>
                    <ActivityIndicator size="large" color={t.colors.primary} />
                    <Text
                      style={[styles.analyzingLabel, { color: t.colors.text }]}
                    >
                      AI is interpreting your spoken meal...
                    </Text>
                    <Pressable
                      accessibilityRole="button"
                      accessibilityLabel="Cancel AI voice analysis"
                      onPress={handleCancelUpload}
                      style={[
                        styles.cancelUploadBtn,
                        { borderColor: t.colors.border },
                      ]}
                    >
                      <Text
                        style={{
                          color: t.colors.secondary,
                          fontSize: 13,
                          fontWeight: '600',
                        }}
                      >
                        Cancel Upload
                      </Text>
                    </Pressable>
                  </View>
                ) : nativeAudioSupported ? (
                  <NativeAudioRecorderPanel
                    stage={stage}
                    disabled={false}
                    t={t}
                    onRecordingStarted={handleRecordingStarted}
                    onRecordingFinished={(uri, dur) =>
                      void handleRecordingFinished(uri, dur)
                    }
                    onRecordingError={handleRecordingError}
                    onRecordingCancelled={handleRecordingCancelled}
                  />
                ) : (
                  <View
                    style={[
                      styles.devNoticeBox,
                      {
                        backgroundColor: t.colors.accent,
                        borderColor: t.colors.border,
                      },
                    ]}
                  >
                    <Text
                      style={[styles.devNoticeText, { color: t.colors.text }]}
                    >
                      Audio recording requires the updated Android APK build
                      with expo-audio. You can still type your meal description
                      below or open Food Search.
                    </Text>
                  </View>
                )}

                {stage === 'idle' && (
                  <View style={styles.suggestionsContainer}>
                    <Text
                      style={[
                        styles.suggestionHeading,
                        { color: t.colors.muted },
                      ]}
                    >
                      Natural examples:
                    </Text>
                    <Text
                      style={[
                        styles.suggestionExample,
                        { color: t.colors.text },
                      ]}
                    >
                      {
                        '• "Two scrambled eggs, a slice of sourdough toast with butter, black coffee, one banana — actually two bananas, and a scoop of whey protein"'
                      }
                    </Text>
                    <Text
                      style={[
                        styles.suggestionExample,
                        { color: t.colors.text },
                      ]}
                    >
                      {
                        '• "Do roti, no wait three rotis, and 150 grams cooked rice with dal"'
                      }
                    </Text>
                  </View>
                )}

                <Text style={[styles.privacyNote, { color: t.colors.muted }]}>
                  Audio uploads over HTTPS only when you tap Stop, is analyzed
                  transiently in memory, and temporary recordings are cleared
                  automatically.
                </Text>
              </View>

              {/* Secondary Editable Text / Recovery Box (no offline catalogue guesser) */}
              {stage === 'idle' && (
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
                      style={[
                        styles.transcriptHeading,
                        { color: t.colors.text },
                      ]}
                    >
                      {transcript.trim()
                        ? 'Transcript (Edit & Re-interpret)'
                        : 'Or Type Meal Description'}
                    </Text>
                    {transcript.length > 0 && (
                      <Pressable
                        accessibilityRole="button"
                        accessibilityLabel="Clear text"
                        onPress={() => setTranscript('')}
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
                    numberOfLines={3}
                    placeholder="Type or refine a meal description (e.g. 2 scrambled eggs, 1 slice sourdough toast with butter)..."
                    placeholderTextColor={t.colors.muted}
                    value={transcript}
                    onChangeText={setTranscript}
                  />

                  <View style={{ marginTop: 10, gap: 8 }}>
                    {transcript.trim().length > 0 && (
                      <Action
                        variant="secondary"
                        label="Interpret Text Description"
                        onPress={handleInterpretEditedTranscript}
                      />
                    )}
                    <Pressable
                      accessibilityRole="button"
                      accessibilityLabel="Open Food Search"
                      onPress={handleGoToFoodSearch}
                      style={[
                        styles.searchFallbackLink,
                        { borderColor: t.colors.border },
                      ]}
                    >
                      <Text
                        style={{
                          color: t.colors.primary,
                          fontSize: 13,
                          fontWeight: '600',
                        }}
                      >
                        Open Regular Food Search
                      </Text>
                    </Pressable>
                  </View>
                </View>
              )}
            </View>
          )}

          {/* STAGE 4: REVIEW & EDIT CANDIDATES */}
          {stage === 'review' && (
            <View style={{ gap: t.spacing.md }}>
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
                  Heard Meal Summary
                </Text>
                {transcript ? (
                  <Text
                    style={[
                      styles.heardTranscriptText,
                      { color: t.colors.text },
                    ]}
                  >
                    {`"${transcript}"`}
                  </Text>
                ) : null}
                <Text style={[styles.summaryText, { color: t.colors.muted }]}>
                  {mealSummary}
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

                <View style={styles.reviewTopActions}>
                  <Pressable
                    accessibilityRole="button"
                    accessibilityLabel="Re-record meal audio"
                    onPress={() => setStage('idle')}
                    style={styles.reRecordBtn}
                  >
                    <Text
                      style={[styles.reRecordText, { color: t.colors.primary }]}
                    >
                      🎙 Re-record or edit text
                    </Text>
                  </Pressable>
                  <Pressable
                    accessibilityRole="button"
                    accessibilityLabel="Open Food Search instead"
                    onPress={handleGoToFoodSearch}
                    style={styles.reRecordBtn}
                  >
                    <Text
                      style={[
                        styles.reRecordText,
                        { color: t.colors.secondary },
                      ]}
                    >
                      🔍 Food Search
                    </Text>
                  </Pressable>
                </View>
              </View>

              <View style={styles.candidatesHeaderRow}>
                <Text
                  style={[styles.candidatesHeading, { color: t.colors.text }]}
                >
                  Review Items ({candidates.length})
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

              {candidates.map((item) => {
                const missingGrams =
                  item.estimated_grams === null || item.estimated_grams <= 0;
                return (
                  <View
                    key={item.id}
                    style={[
                      styles.candidateCard,
                      {
                        backgroundColor: t.colors.surface,
                        borderColor: missingGrams ? '#E67E22' : t.colors.border,
                      },
                    ]}
                  >
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
                        accessibilityLabel={`Remove ${item.food_name}`}
                        onPress={() => deleteCandidate(item.id)}
                        style={styles.deleteBtn}
                      >
                        <Text style={styles.deleteBtnText}>✕ Remove</Text>
                      </Pressable>
                    </View>

                    {/* Preparation & modifiers */}
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
                            {item.state === 'raw' ? '🥩 Raw' : '🍳 Cooked'}
                          </Text>
                        </View>
                      )}

                      {item.modifiers?.map((mod, idx) => (
                        <View
                          key={`${item.id}-mod-${idx}`}
                          style={[
                            styles.modifierBadge,
                            {
                              backgroundColor: '#FEF5E7',
                              borderColor: '#F39C12',
                            },
                          ]}
                        >
                          <Text style={styles.modifierBadgeText}>
                            + {mod} (weight unstated)
                          </Text>
                        </View>
                      ))}

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
                                  : '#EBF5FB',
                              borderColor:
                                item.sourceMode === 'catalogue'
                                  ? '#1ABC9C'
                                  : '#3498DB',
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
                                    : '#1B4F72',
                              },
                            ]}
                          >
                            {item.sourceMode === 'catalogue'
                              ? `✓ Catalogue (${item.matchedCatalogueFood.status})`
                              : '✦ AI Audio Estimate · Tap for Catalogue'}
                          </Text>
                        </Pressable>
                      ) : (
                        <View
                          style={[
                            styles.sourceModeChip,
                            {
                              backgroundColor: '#EBF5FB',
                              borderColor: '#3498DB',
                            },
                          ]}
                        >
                          <Text
                            style={[
                              styles.sourceModeText,
                              { color: '#1B4F72' },
                            ]}
                          >
                            {item.confidence_level === 'high'
                              ? '✦ AI Audio Estimate'
                              : `✦ AI Estimate (${item.confidence_level} confidence)`}
                          </Text>
                        </View>
                      )}
                    </View>

                    {item.notes ? (
                      <Text
                        style={[styles.itemNoteText, { color: t.colors.muted }]}
                      >
                        {item.notes}
                      </Text>
                    ) : null}

                    {/* Alternative catalogue matches */}
                    {item.availableMatches.length > 0 && (
                      <View style={styles.alternativesSection}>
                        <Text
                          style={[
                            styles.alternativesLabel,
                            { color: t.colors.muted },
                          ]}
                        >
                          Catalogue matches:
                        </Text>
                        <ScrollView
                          horizontal
                          showsHorizontalScrollIndicator={false}
                          contentContainerStyle={styles.alternativesScroll}
                        >
                          {item.availableMatches.slice(0, 5).map((alt) => {
                            const selected =
                              item.sourceMode === 'catalogue' &&
                              item.matchedCatalogueFood?.id === alt.id;
                            return (
                              <Pressable
                                key={alt.id}
                                onPress={() =>
                                  selectAlternativeFood(item.id, alt)
                                }
                                style={[
                                  styles.altChip,
                                  {
                                    borderColor: selected
                                      ? t.colors.primary
                                      : t.colors.border,
                                    backgroundColor: selected
                                      ? t.colors.accent
                                      : t.colors.background,
                                  },
                                ]}
                              >
                                <Text
                                  style={[
                                    styles.altChipText,
                                    {
                                      color: selected
                                        ? t.colors.primary
                                        : t.colors.text,
                                    },
                                  ]}
                                  numberOfLines={1}
                                >
                                  {alt.name}
                                </Text>
                              </Pressable>
                            );
                          })}
                        </ScrollView>
                      </View>
                    )}

                    {/* Portion editor */}
                    <View style={styles.portionRow}>
                      <View style={styles.portionInputGroup}>
                        <Text
                          style={[
                            styles.fieldLabel,
                            {
                              color: missingGrams ? '#D35400' : t.colors.muted,
                            },
                          ]}
                        >
                          {missingGrams ? 'Enter Grams:' : 'Grams:'}
                        </Text>
                        <TextInput
                          style={[
                            styles.gramsInput,
                            {
                              color: t.colors.text,
                              borderColor: missingGrams
                                ? '#E67E22'
                                : t.colors.border,
                              backgroundColor: t.colors.background,
                            },
                          ]}
                          keyboardType="numeric"
                          placeholder="g"
                          placeholderTextColor={t.colors.muted}
                          value={
                            item.estimated_grams === null ||
                            item.estimated_grams === 0
                              ? ''
                              : String(item.estimated_grams)
                          }
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
                          {item.preparation ? ` · ${item.preparation}` : ''}
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
                          {formatNutrient(item.calories, 'kcal')}
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
                          {item.protein === null
                            ? 'Unknown'
                            : `${item.protein.toFixed(1)}g`}
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
                          {item.carbohydrates === null
                            ? 'Unknown'
                            : `${item.carbohydrates.toFixed(1)}g`}
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
                          {item.fat === null
                            ? 'Unknown'
                            : `${item.fat.toFixed(1)}g`}
                        </Text>
                      </View>
                    </View>
                  </View>
                );
              })}
            </View>
          )}
        </ScrollView>

        {/* STAGE 5: CONFIRM & LOG FOOTER */}
        {stage === 'review' && (
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
                  Meal Total:{' '}
                  {totals.calories === null
                    ? 'Unknown'
                    : `${Math.round(totals.calories)} kcal`}
                  {totals.partial.calories ? ' (partial)' : ''}
                </Text>
                <Text
                  style={[styles.footerTotalsSub, { color: t.colors.muted }]}
                >
                  P:{' '}
                  {totals.protein === null
                    ? 'Unknown'
                    : `${totals.protein.toFixed(1)}g`}{' '}
                  · C:{' '}
                  {totals.carbs === null
                    ? 'Unknown'
                    : `${totals.carbs.toFixed(1)}g`}{' '}
                  · F:{' '}
                  {totals.fat === null
                    ? 'Unknown'
                    : `${totals.fat.toFixed(1)}g`}{' '}
                  ({Math.round(totals.grams)}g total)
                </Text>
              </View>
            </View>

            <View style={styles.footerActionRow}>
              <Action
                variant="primary"
                label={
                  saving
                    ? 'Logging Meal...'
                    : totals.missingGramsCount > 0
                      ? `Enter Grams (${totals.missingGramsCount} item${totals.missingGramsCount === 1 ? '' : 's'})`
                      : 'Confirm & Log to Diary'
                }
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
    alignSelf: 'flex-start',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 16,
  },
  metaText: {
    fontSize: 13,
    fontWeight: '600',
  },
  errorCard: {
    padding: 14,
    borderRadius: 12,
    borderWidth: 1,
    gap: 10,
  },
  recoveryActionsRow: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
  },
  recoveryBtn: {
    paddingHorizontal: 14,
    paddingVertical: 10,
    borderRadius: 8,
    borderWidth: 1,
    minHeight: 40,
    justifyContent: 'center',
    alignItems: 'center',
  },
  micAreaCard: {
    padding: 20,
    borderRadius: 14,
    borderWidth: 1,
    alignItems: 'center',
    gap: 16,
  },
  micInstructions: {
    fontSize: 14,
    textAlign: 'center',
    lineHeight: 20,
  },
  micButton: {
    paddingHorizontal: 30,
    paddingVertical: 18,
    borderRadius: 36,
    minWidth: 210,
    minHeight: 56,
    alignItems: 'center',
    justifyContent: 'center',
    elevation: 2,
  },
  micButtonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '700',
  },
  recordingStatusBox: {
    width: '100%',
    alignItems: 'center',
    gap: 8,
  },
  timerText: {
    fontSize: 14,
    fontWeight: '700',
  },
  meterTrack: {
    width: '100%',
    height: 8,
    borderRadius: 4,
    overflow: 'hidden',
  },
  meterBar: {
    height: 8,
    borderRadius: 4,
  },
  cancelRecordingBtn: {
    paddingVertical: 8,
    paddingHorizontal: 14,
    minHeight: 40,
    justifyContent: 'center',
  },
  analyzingBox: {
    alignItems: 'center',
    gap: 12,
    paddingVertical: 8,
  },
  analyzingLabel: {
    fontSize: 14,
    fontWeight: '600',
    textAlign: 'center',
  },
  cancelUploadBtn: {
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 8,
    borderWidth: 1,
    minHeight: 40,
    justifyContent: 'center',
  },
  devNoticeBox: {
    width: '100%',
    padding: 12,
    borderRadius: 10,
    borderWidth: 1,
  },
  devNoticeText: {
    fontSize: 13,
    lineHeight: 18,
    textAlign: 'center',
  },
  suggestionsContainer: {
    width: '100%',
    paddingTop: 10,
    borderTopWidth: StyleSheet.hairlineWidth,
    borderTopColor: '#DDDDDD',
    gap: 6,
  },
  suggestionHeading: {
    fontSize: 12,
    fontWeight: '600',
  },
  suggestionExample: {
    fontSize: 13,
    fontStyle: 'italic',
    lineHeight: 18,
  },
  privacyNote: {
    fontSize: 11,
    textAlign: 'center',
    lineHeight: 16,
  },
  transcriptCard: {
    padding: 16,
    borderRadius: 14,
    borderWidth: 1,
    gap: 8,
  },
  transcriptHeaderRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  transcriptHeading: {
    fontSize: 14,
    fontWeight: '600',
  },
  clearBtn: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    minHeight: 36,
    justifyContent: 'center',
  },
  transcriptInput: {
    borderWidth: 1,
    borderRadius: 10,
    padding: 12,
    fontSize: 15,
    minHeight: 80,
    textAlignVertical: 'top',
  },
  searchFallbackLink: {
    paddingVertical: 11,
    borderRadius: 10,
    borderWidth: 1,
    alignItems: 'center',
    justifyContent: 'center',
    minHeight: 44,
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
  heardTranscriptText: {
    fontSize: 13,
    fontStyle: 'italic',
    lineHeight: 19,
  },
  summaryText: {
    fontSize: 13,
    lineHeight: 18,
  },
  warningsList: {
    marginTop: 2,
    gap: 4,
  },
  warningItem: {
    fontSize: 12,
    color: '#D35400',
    lineHeight: 16,
  },
  questionsList: {
    marginTop: 2,
    gap: 4,
  },
  questionItem: {
    fontSize: 12,
    color: '#2980B9',
    lineHeight: 16,
  },
  reviewTopActions: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 16,
  },
  reRecordBtn: {
    minHeight: 40,
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
    gap: 10,
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
  modifierBadge: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 6,
    borderWidth: 1,
  },
  modifierBadgeText: {
    fontSize: 11,
    fontWeight: '600',
    color: '#9A6700',
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
  itemNoteText: {
    fontSize: 12,
    lineHeight: 16,
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
    flex: 1,
    alignItems: 'flex-end',
    paddingVertical: 4,
    paddingHorizontal: 6,
  },
  spokenUnitText: {
    fontSize: 12,
    fontStyle: 'italic',
    textAlign: 'right',
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
