/**
 * AI Food Recognition & Logging Modal for Bites2Go.
 *
 * Provides:
 * - Image selection via camera or library.
 * - In-memory image preview.
 * - Loading indicator during Gemini analysis.
 * - User-editable candidates (name, grams, calories, protein, carbs, fat).
 * - Real-time recalculated meal nutrition totals.
 * - Item removal.
 * - Cancellation without saving.
 * - Explicit confirmation before committing to local SQLite diary.
 */

import React, { useState, useMemo } from 'react';
import {
  ActivityIndicator,
  Alert,
  Image,
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
import * as ImagePicker from 'expo-image-picker';
import { randomUUID } from 'expo-crypto';

import { useUI } from './dashboard';
import { Action } from './FoodControls';
import { useDiary } from '../state/DiaryProvider';
import {
  createAIDiaryEntry,
  localDateKey,
  validDateKey,
} from '../domain/diary';
import { scaleNutrients, type FoodNutrients, type Meal } from '../domain/food';
import {
  recognizeFoodFromImage,
  type RecognizedFoodItem,
} from '../services/aiFoodRecognition';

export type AIFoodScannerModalProps = {
  visible: boolean;
  meal: Meal;
  date?: string | null;
  onClose: () => void;
  onSuccess?: () => void;
};

type EditableCandidate = RecognizedFoodItem & {
  id: string;
  stableEntryId: string;
  stableCreatedAt: string;
  reference: FoodNutrients;
};

export function AIFoodScannerModal({
  visible,
  meal,
  date,
  onClose,
  onSuccess,
}: AIFoodScannerModalProps) {
  const { t } = useUI();
  const diary = useDiary();

  const [imageUri, setImageUri] = useState<string | null>(null);
  const [imageBase64, setImageBase64] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [mealSummary, setMealSummary] = useState<string>('');
  const [candidates, setCandidates] = useState<EditableCandidate[]>([]);

  const targetDate = useMemo(() => {
    return date && validDateKey(date) ? date : localDateKey();
  }, [date]);

  const resetState = () => {
    setImageUri(null);
    setImageBase64(null);
    setLoading(false);
    setSaving(false);
    setError(null);
    setMealSummary('');
    setCandidates([]);
  };

  const handleClose = () => {
    if (loading || saving) return;
    resetState();
    onClose();
  };

  const pickImage = async (useCamera: boolean) => {
    setError(null);
    try {
      let result: ImagePicker.ImagePickerResult;
      const options: ImagePicker.ImagePickerOptions = {
        mediaTypes: ['images'],
        allowsEditing: true,
        quality: 0.8,
        base64: true,
      };

      if (useCamera) {
        const { status } = await ImagePicker.requestCameraPermissionsAsync();
        if (status !== 'granted') {
          Alert.alert(
            'Camera Permission Needed',
            'Please enable camera permissions to take a photo of your meal.',
          );
          return;
        }
        result = await ImagePicker.launchCameraAsync(options);
      } else {
        const { status } =
          await ImagePicker.requestMediaLibraryPermissionsAsync();
        if (status !== 'granted') {
          Alert.alert(
            'Gallery Permission Needed',
            'Please enable photo gallery access to select a meal photo.',
          );
          return;
        }
        result = await ImagePicker.launchImageLibraryAsync(options);
      }

      if (result.canceled || !result.assets || result.assets.length === 0) {
        return;
      }

      const asset = result.assets[0];
      setImageUri(asset.uri);
      setImageBase64(asset.base64 || null);

      // Immediately trigger recognition
      await analyzeImage(asset.uri, asset.base64 || undefined);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : String(err);
      setError(`Failed to pick image: ${msg}`);
    }
  };

  const analyzeImage = async (uri: string, b64?: string) => {
    setLoading(true);
    setError(null);
    try {
      const result = await recognizeFoodFromImage(uri, b64);
      setMealSummary(result.summary || '');

      const editable: EditableCandidate[] = result.items.map((item) => {
        const grams =
          Number.isFinite(item.estimated_grams) && item.estimated_grams > 0
            ? item.estimated_grams
            : 100;
        const portion: FoodNutrients = {
          calories: item.calories,
          protein: item.protein,
          carbs: item.carbohydrates,
          fat: item.fat,
          fiber: 0,
        };
        const reference = scaleNutrients(portion, 10000 / grams);
        return {
          ...item,
          id: randomUUID(),
          stableEntryId: randomUUID(),
          stableCreatedAt: new Date().toISOString(),
          estimated_grams: grams,
          reference,
        };
      });

      setCandidates(editable);
      if (editable.length === 0) {
        setMealSummary(
          result.summary ||
            'No food items recognized in this photo. Try another angle or log manually.',
        );
      }
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : String(err);
      setError(
        msg.includes('Cannot connect') || msg.includes('Failed to fetch')
          ? 'Cannot reach local AI backend. Ensure backend is running. Manual search remains available offline.'
          : msg,
      );
    } finally {
      setLoading(false);
    }
  };

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
        // Recalculate nutrients from reference density per 100g
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

  const updateCandidateCalories = (id: string, text: string) => {
    const val = parseFloat(text.replace(',', '.'));
    setCandidates((prev) =>
      prev.map((item) => {
        if (item.id !== id) return item;
        const newCalories = isNaN(val) ? 0 : Math.max(0, val);
        const grams = item.estimated_grams > 0 ? item.estimated_grams : 100;
        return {
          ...item,
          calories: newCalories,
          reference: {
            ...item.reference,
            calories: (newCalories / grams) * 100,
          },
        };
      }),
    );
  };

  const updateCandidateProtein = (id: string, text: string) => {
    const val = parseFloat(text.replace(',', '.'));
    setCandidates((prev) =>
      prev.map((item) => {
        if (item.id !== id) return item;
        const newProtein = isNaN(val) ? 0 : Math.max(0, val);
        const grams = item.estimated_grams > 0 ? item.estimated_grams : 100;
        return {
          ...item,
          protein: newProtein,
          reference: {
            ...item.reference,
            protein: (newProtein / grams) * 100,
          },
        };
      }),
    );
  };

  const updateCandidateCarbs = (id: string, text: string) => {
    const val = parseFloat(text.replace(',', '.'));
    setCandidates((prev) =>
      prev.map((item) => {
        if (item.id !== id) return item;
        const newCarbs = isNaN(val) ? 0 : Math.max(0, val);
        const grams = item.estimated_grams > 0 ? item.estimated_grams : 100;
        return {
          ...item,
          carbohydrates: newCarbs,
          reference: {
            ...item.reference,
            carbs: (newCarbs / grams) * 100,
          },
        };
      }),
    );
  };

  const updateCandidateFat = (id: string, text: string) => {
    const val = parseFloat(text.replace(',', '.'));
    setCandidates((prev) =>
      prev.map((item) => {
        if (item.id !== id) return item;
        const newFat = isNaN(val) ? 0 : Math.max(0, val);
        const grams = item.estimated_grams > 0 ? item.estimated_grams : 100;
        return {
          ...item,
          fat: newFat,
          reference: {
            ...item.reference,
            fat: (newFat / grams) * 100,
          },
        };
      }),
    );
  };

  const removeCandidate = (id: string) => {
    setCandidates((prev) => prev.filter((item) => item.id !== id));
  };

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

  const confirmLogToDiary = async () => {
    if (saving || candidates.length === 0) return;

    // Validate candidates first before modifying storage
    for (const item of candidates) {
      if (!item.food_name.trim()) {
        Alert.alert(
          'Invalid Food Name',
          'Please provide a name for all food items.',
        );
        return;
      }
      if (!Number.isFinite(item.estimated_grams) || item.estimated_grams <= 0) {
        Alert.alert(
          'Invalid Portion',
          `Please enter a positive weight in grams for "${item.food_name}".`,
        );
        return;
      }
      if (
        !Number.isFinite(item.calories) ||
        item.calories < 0 ||
        !Number.isFinite(item.protein) ||
        item.protein < 0 ||
        !Number.isFinite(item.carbohydrates) ||
        item.carbohydrates < 0 ||
        !Number.isFinite(item.fat) ||
        item.fat < 0
      ) {
        Alert.alert(
          'Invalid Nutrition',
          `Nutritional values for "${item.food_name}" must be non-negative numbers.`,
        );
        return;
      }
    }

    setSaving(true);
    try {
      const entriesToSave = candidates.map((item) =>
        createAIDiaryEntry({
          id: item.stableEntryId,
          foodName: item.food_name,
          meal,
          date: targetDate,
          grams: item.estimated_grams,
          calories: item.calories,
          protein: item.protein,
          carbs: item.carbohydrates,
          fat: item.fat,
          fiber: 0,
          preparation: item.uncertainty.notes || 'Recognized by Gemini AI',
          source: 'Gemini AI',
          now: item.stableCreatedAt,
        }),
      );

      await diary.saveAll(entriesToSave);

      resetState();
      onClose();
      if (onSuccess) onSuccess();
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : String(err);
      Alert.alert('Save Failed', `Could not save AI foods to diary: ${msg}`);
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
            AI Meal Recognition
          </Text>
          <Pressable
            accessibilityRole="button"
            accessibilityLabel="Close AI Scanner"
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
            { paddingBottom: t.spacing.xxl * 2 },
          ]}
          keyboardShouldPersistTaps="handled"
        >
          {/* Target Meal & Date notice */}
          <View
            style={[styles.metaBadge, { backgroundColor: t.colors.accent }]}
          >
            <Text style={[styles.metaText, { color: t.colors.primary }]}>
              Logging to {meal} · {targetDate}
            </Text>
          </View>

          {/* Action buttons if no image yet */}
          {!imageUri && (
            <View
              style={[
                styles.emptyPickerCard,
                {
                  backgroundColor: t.colors.surface,
                  borderColor: t.colors.border,
                },
              ]}
            >
              <Text style={[styles.pickerTitle, { color: t.colors.text }]}>
                Snap or Pick a Food Photo
              </Text>
              <Text style={[styles.pickerSubtitle, { color: t.colors.muted }]}>
                Your photo is sent securely to your local Bites2Go backend.
                Gemini analyzes portion sizes, calories, and macros without
                cloud sync.
              </Text>

              <View style={styles.pickerBtnRow}>
                <Action
                  label="Take Photo"
                  onPress={() => pickImage(true)}
                  variant="primary"
                />
                <Action
                  label="Choose from Gallery"
                  onPress={() => pickImage(false)}
                  variant="secondary"
                />
              </View>
            </View>
          )}

          {/* Image Preview */}
          {imageUri && (
            <View
              style={[
                styles.previewCard,
                {
                  backgroundColor: t.colors.surface,
                  borderColor: t.colors.border,
                },
              ]}
            >
              <Image source={{ uri: imageUri }} style={styles.previewImage} />
              <View style={styles.repickRow}>
                <Pressable
                  accessibilityRole="button"
                  onPress={() => pickImage(true)}
                  style={styles.repickBtn}
                >
                  <Text
                    style={[styles.repickText, { color: t.colors.primary }]}
                  >
                    Retake Photo
                  </Text>
                </Pressable>
                <Pressable
                  accessibilityRole="button"
                  onPress={() => pickImage(false)}
                  style={styles.repickBtn}
                >
                  <Text
                    style={[styles.repickText, { color: t.colors.primary }]}
                  >
                    Choose Other
                  </Text>
                </Pressable>
              </View>
            </View>
          )}

          {/* Loading Indicator */}
          {loading && (
            <View style={styles.loadingContainer}>
              <ActivityIndicator size="large" color={t.colors.primary} />
              <Text style={[styles.loadingText, { color: t.colors.text }]}>
                Analyzing meal with Gemini AI...
              </Text>
              <Text style={[styles.loadingSubtext, { color: t.colors.muted }]}>
                Detecting food items, portion sizes, and macronutrients
              </Text>
            </View>
          )}

          {/* Error Notice */}
          {error && !loading && (
            <View
              style={[
                styles.errorCard,
                { backgroundColor: t.colors.highlight },
              ]}
            >
              <Text style={[styles.errorText, { color: t.colors.error }]}>
                {error}
              </Text>
              <View style={{ marginTop: t.spacing.sm }}>
                <Action
                  label="Try Again"
                  onPress={() =>
                    imageUri
                      ? analyzeImage(imageUri, imageBase64 || undefined)
                      : pickImage(false)
                  }
                  variant="secondary"
                />
              </View>
            </View>
          )}

          {/* Meal Summary */}
          {mealSummary.length > 0 && !loading && (
            <View
              style={[
                styles.summaryCard,
                {
                  backgroundColor: t.colors.elevated,
                  borderColor: t.colors.border,
                },
              ]}
            >
              <Text style={[styles.summaryTitle, { color: t.colors.text }]}>
                Meal Assessment
              </Text>
              <Text style={[styles.summaryBody, { color: t.colors.muted }]}>
                {mealSummary}
              </Text>
            </View>
          )}

          {/* Empty State when photo has no recognized food */}
          {!loading && imageUri && candidates.length === 0 && !error && (
            <View
              style={[
                styles.emptyPickerCard,
                {
                  backgroundColor: t.colors.surface,
                  borderColor: t.colors.border,
                },
              ]}
            >
              <Text style={[styles.pickerTitle, { color: t.colors.text }]}>
                No Food Items Detected
              </Text>
              <Text style={[styles.pickerSubtitle, { color: t.colors.muted }]}>
                We could not clearly distinguish food items in this photo. The
                image may be blurry, under low lighting, or show an empty plate.
              </Text>
              <View style={styles.pickerBtnRow}>
                <Action
                  label="Retake Photo"
                  onPress={() => pickImage(true)}
                  variant="primary"
                />
                <Action
                  label="Choose from Gallery"
                  onPress={() => pickImage(false)}
                  variant="secondary"
                />
              </View>
            </View>
          )}

          {/* Recognized Candidates List */}
          {candidates.length > 0 && !loading && (
            <View style={styles.candidatesSection}>
              <Text style={[styles.sectionHeading, { color: t.colors.text }]}>
                Recognized Foods ({candidates.length})
              </Text>
              <Text
                style={[styles.sectionSubheading, { color: t.colors.muted }]}
              >
                Review or edit portion sizes and values before adding to your
                diary.
              </Text>

              {candidates.map((item, index) => {
                const confColor =
                  item.uncertainty.confidence_level === 'high'
                    ? t.colors.success
                    : item.uncertainty.confidence_level === 'medium'
                      ? t.colors.warning
                      : t.colors.error;

                return (
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
                    {/* Item Title & Confidence Badge */}
                    <View style={styles.cardHeaderRow}>
                      <TextInput
                        style={[
                          styles.nameInput,
                          {
                            color: t.colors.text,
                            borderColor: t.colors.border,
                            backgroundColor: t.colors.input,
                          },
                        ]}
                        value={item.food_name}
                        onChangeText={(txt) =>
                          updateCandidateName(item.id, txt)
                        }
                        placeholder="Food name"
                        placeholderTextColor={t.colors.muted}
                      />
                      <Pressable
                        accessibilityRole="button"
                        accessibilityLabel={`Remove ${item.food_name}`}
                        onPress={() => removeCandidate(item.id)}
                        style={styles.deleteBtn}
                      >
                        <Text
                          style={[
                            styles.deleteBtnText,
                            { color: t.colors.error },
                          ]}
                        >
                          ✕
                        </Text>
                      </Pressable>
                    </View>

                    {/* Uncertainty / Confidence Info */}
                    <View style={styles.confidenceRow}>
                      <View
                        style={[
                          styles.confidenceBadge,
                          { backgroundColor: confColor + '20' },
                        ]}
                      >
                        <Text
                          style={[styles.confidenceText, { color: confColor }]}
                        >
                          Confidence:{' '}
                          {item.uncertainty.confidence_level.toUpperCase()} (
                          {Math.round(item.uncertainty.confidence_score * 100)}
                          %)
                        </Text>
                      </View>
                      {item.uncertainty.notes ? (
                        <Text
                          style={[styles.notesText, { color: t.colors.muted }]}
                        >
                          Note: {item.uncertainty.notes}
                        </Text>
                      ) : null}
                    </View>

                    {/* Ambiguity Alternatives Chips */}
                    {item.uncertainty.alternatives &&
                      item.uncertainty.alternatives.length > 0 && (
                        <View style={styles.alternativesSection}>
                          <Text
                            style={[
                              styles.alternativesLabel,
                              { color: t.colors.muted },
                            ]}
                          >
                            Suggested alternatives (tap to switch):
                          </Text>
                          <View style={styles.alternativesList}>
                            {item.uncertainty.alternatives.map((alt) => (
                              <Pressable
                                key={alt}
                                accessibilityRole="button"
                                accessibilityLabel={`Switch dish name to ${alt}`}
                                onPress={() =>
                                  updateCandidateName(item.id, alt)
                                }
                                style={({ pressed }) => [
                                  styles.altChip,
                                  {
                                    backgroundColor: t.colors.elevated,
                                    borderColor: t.colors.border,
                                  },
                                  pressed && { opacity: 0.6 },
                                ]}
                              >
                                <Text
                                  style={[
                                    styles.altChipText,
                                    { color: t.colors.primary },
                                  ]}
                                >
                                  + {alt}
                                </Text>
                              </Pressable>
                            ))}
                          </View>
                        </View>
                      )}

                    {/* Portion Controls */}
                    <View style={styles.portionRow}>
                      <View style={styles.portionField}>
                        <Text
                          style={[styles.fieldLabel, { color: t.colors.muted }]}
                        >
                          Weight (grams)
                        </Text>
                        <TextInput
                          style={[
                            styles.numericInput,
                            {
                              color: t.colors.text,
                              borderColor: t.colors.border,
                              backgroundColor: t.colors.input,
                            },
                          ]}
                          keyboardType="numeric"
                          value={
                            item.estimated_grams
                              ? String(item.estimated_grams)
                              : ''
                          }
                          onChangeText={(txt) =>
                            updateCandidateGrams(item.id, txt)
                          }
                        />
                      </View>
                      <View style={styles.portionField}>
                        <Text
                          style={[styles.fieldLabel, { color: t.colors.muted }]}
                        >
                          Serving Scale
                        </Text>
                        <Text
                          style={[styles.unitText, { color: t.colors.text }]}
                        >
                          {item.estimated_quantity} {item.unit}
                        </Text>
                      </View>
                    </View>

                    {/* Approximate Notice */}
                    <Text
                      style={[styles.approxNotice, { color: t.colors.muted }]}
                    >
                      ~{item.estimated_grams}g ({item.estimated_quantity}{' '}
                      {item.unit}) · Approximate visual estimate
                    </Text>

                    {/* Macro Grid */}
                    <View style={styles.macroGrid}>
                      <View
                        style={[
                          styles.macroBox,
                          { backgroundColor: t.colors.elevated },
                        ]}
                      >
                        <Text
                          style={[styles.macroLabel, { color: t.colors.muted }]}
                        >
                          Calories
                        </Text>
                        <TextInput
                          style={[
                            styles.macroValueInput,
                            { color: t.colors.text },
                          ]}
                          keyboardType="numeric"
                          value={String(Math.round(item.calories))}
                          onChangeText={(txt) =>
                            updateCandidateCalories(item.id, txt)
                          }
                        />
                        <Text
                          style={[styles.macroUnit, { color: t.colors.muted }]}
                        >
                          kcal
                        </Text>
                      </View>

                      <View
                        style={[
                          styles.macroBox,
                          { backgroundColor: t.colors.elevated },
                        ]}
                      >
                        <Text
                          style={[
                            styles.macroLabel,
                            { color: t.colors.protein },
                          ]}
                        >
                          Protein
                        </Text>
                        <TextInput
                          style={[
                            styles.macroValueInput,
                            { color: t.colors.text },
                          ]}
                          keyboardType="numeric"
                          value={String(item.protein)}
                          onChangeText={(txt) =>
                            updateCandidateProtein(item.id, txt)
                          }
                        />
                        <Text
                          style={[styles.macroUnit, { color: t.colors.muted }]}
                        >
                          g
                        </Text>
                      </View>

                      <View
                        style={[
                          styles.macroBox,
                          { backgroundColor: t.colors.elevated },
                        ]}
                      >
                        <Text
                          style={[styles.macroLabel, { color: t.colors.carbs }]}
                        >
                          Carbs
                        </Text>
                        <TextInput
                          style={[
                            styles.macroValueInput,
                            { color: t.colors.text },
                          ]}
                          keyboardType="numeric"
                          value={String(item.carbohydrates)}
                          onChangeText={(txt) =>
                            updateCandidateCarbs(item.id, txt)
                          }
                        />
                        <Text
                          style={[styles.macroUnit, { color: t.colors.muted }]}
                        >
                          g
                        </Text>
                      </View>

                      <View
                        style={[
                          styles.macroBox,
                          { backgroundColor: t.colors.elevated },
                        ]}
                      >
                        <Text
                          style={[styles.macroLabel, { color: t.colors.fat }]}
                        >
                          Fat
                        </Text>
                        <TextInput
                          style={[
                            styles.macroValueInput,
                            { color: t.colors.text },
                          ]}
                          keyboardType="numeric"
                          value={String(item.fat)}
                          onChangeText={(txt) =>
                            updateCandidateFat(item.id, txt)
                          }
                        />
                        <Text
                          style={[styles.macroUnit, { color: t.colors.muted }]}
                        >
                          g
                        </Text>
                      </View>
                    </View>
                  </View>
                );
              })}
            </View>
          )}
        </ScrollView>

        {/* Bottom Confirmation Bar */}
        {candidates.length > 0 && !loading && (
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
              <Text
                style={[styles.footerTotalsTitle, { color: t.colors.text }]}
              >
                Meal Total: {Math.round(totals.calories)} kcal
              </Text>
              <Text style={[styles.footerTotalsSub, { color: t.colors.muted }]}>
                P: {Math.round(totals.protein)}g · C: {Math.round(totals.carbs)}
                g · F: {Math.round(totals.fat)}g
              </Text>
            </View>

            <View style={styles.footerActionRow}>
              <Action
                label={
                  saving
                    ? 'Saving...'
                    : `Log ${candidates.length} Items to ${meal}`
                }
                onPress={confirmLogToDiary}
                disabled={saving}
                variant="primary"
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
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 14,
    borderBottomWidth: StyleSheet.hairlineWidth,
  },
  headerTitle: {
    fontSize: 20,
    fontWeight: '700',
  },
  closeBtn: {
    padding: 6,
  },
  closeBtnText: {
    fontSize: 16,
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
    borderRadius: 8,
  },
  metaText: {
    fontSize: 13,
    fontWeight: '600',
  },
  emptyPickerCard: {
    borderWidth: 1,
    borderRadius: 16,
    padding: 24,
    alignItems: 'center',
    gap: 12,
  },
  pickerTitle: {
    fontSize: 18,
    fontWeight: '700',
    textAlign: 'center',
  },
  pickerSubtitle: {
    fontSize: 14,
    lineHeight: 20,
    textAlign: 'center',
    marginBottom: 8,
  },
  pickerBtnRow: {
    flexDirection: 'row',
    gap: 12,
    flexWrap: 'wrap',
    justifyContent: 'center',
  },
  previewCard: {
    borderWidth: 1,
    borderRadius: 16,
    overflow: 'hidden',
  },
  previewImage: {
    width: '100%',
    height: 220,
    resizeMode: 'cover',
  },
  repickRow: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    paddingVertical: 10,
  },
  repickBtn: {
    paddingVertical: 4,
    paddingHorizontal: 12,
  },
  repickText: {
    fontSize: 14,
    fontWeight: '600',
  },
  loadingContainer: {
    padding: 32,
    alignItems: 'center',
    gap: 10,
  },
  loadingText: {
    fontSize: 16,
    fontWeight: '600',
    marginTop: 8,
  },
  loadingSubtext: {
    fontSize: 13,
    textAlign: 'center',
  },
  errorCard: {
    padding: 16,
    borderRadius: 12,
  },
  errorText: {
    fontSize: 14,
    lineHeight: 20,
    fontWeight: '500',
  },
  summaryCard: {
    borderWidth: 1,
    borderRadius: 12,
    padding: 14,
    gap: 4,
  },
  summaryTitle: {
    fontSize: 14,
    fontWeight: '700',
  },
  summaryBody: {
    fontSize: 13,
    lineHeight: 18,
  },
  candidatesSection: {
    gap: 12,
  },
  sectionHeading: {
    fontSize: 18,
    fontWeight: '700',
  },
  sectionSubheading: {
    fontSize: 13,
    marginBottom: 4,
  },
  candidateCard: {
    borderWidth: 1,
    borderRadius: 14,
    padding: 14,
    gap: 10,
  },
  cardHeaderRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  nameInput: {
    flex: 1,
    fontSize: 16,
    fontWeight: '600',
    borderWidth: 1,
    borderRadius: 8,
    paddingHorizontal: 10,
    paddingVertical: 6,
  },
  deleteBtn: {
    padding: 8,
  },
  deleteBtnText: {
    fontSize: 18,
    fontWeight: '700',
  },
  confidenceRow: {
    gap: 4,
  },
  confidenceBadge: {
    alignSelf: 'flex-start',
    paddingHorizontal: 8,
    paddingVertical: 3,
    borderRadius: 6,
  },
  confidenceText: {
    fontSize: 11,
    fontWeight: '700',
  },
  notesText: {
    fontSize: 12,
    fontStyle: 'italic',
  },
  alternativesSection: {
    gap: 6,
    marginTop: 2,
  },
  alternativesLabel: {
    fontSize: 12,
    fontWeight: '500',
  },
  alternativesList: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 6,
  },
  altChip: {
    borderWidth: 1,
    borderRadius: 6,
    paddingHorizontal: 8,
    paddingVertical: 4,
  },
  altChipText: {
    fontSize: 12,
    fontWeight: '600',
  },
  portionRow: {
    flexDirection: 'row',
    gap: 12,
  },
  portionField: {
    flex: 1,
    gap: 4,
  },
  fieldLabel: {
    fontSize: 12,
    fontWeight: '500',
  },
  numericInput: {
    borderWidth: 1,
    borderRadius: 8,
    paddingHorizontal: 10,
    paddingVertical: 6,
    fontSize: 15,
    fontWeight: '600',
  },
  unitText: {
    fontSize: 14,
    paddingVertical: 8,
    fontWeight: '500',
  },
  approxNotice: {
    fontSize: 11,
    fontStyle: 'italic',
    marginTop: 2,
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
    fontWeight: '600',
  },
  macroValueInput: {
    fontSize: 15,
    fontWeight: '700',
    textAlign: 'center',
    paddingVertical: 2,
    minWidth: 40,
  },
  macroUnit: {
    fontSize: 10,
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
