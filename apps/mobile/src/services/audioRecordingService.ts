/**
 * Safe Native Audio Recording Service & File Hygiene Adapter (Expo SDK 58 expo-audio).
 *
 * Responsibilities:
 * - Safely detects whether the native 'ExpoAudio' module exists in the host binary
 *   (preventing startup/render crashes on older APK shells lacking native audio modules).
 * - Requests OS microphone permissions safely via requestRecordingPermissionsAsync.
 * - Configures recording audio mode cleanly and releases audio focus afterward.
 * - Inspects file size and cleans up temporary local audio cache files immediately
 *   after upload success, cancellation, modal close, or unmount.
 */

import { Platform } from 'react-native';
import { requireOptionalNativeModule } from 'expo-modules-core';
import type {
  AudioRecorder,
  RecorderState,
  RecordingOptions,
} from 'expo-audio';

import {
  MAX_AUDIO_FILE_BYTES,
  MAX_AUDIO_DURATION_MS,
  MIN_AUDIO_DURATION_MS,
  MIN_AUDIO_FILE_BYTES,
  validateRecordedAudioMetadata,
} from './voiceFoodLogging';

export {
  MAX_AUDIO_FILE_BYTES,
  MAX_AUDIO_DURATION_MS,
  MIN_AUDIO_DURATION_MS,
  MIN_AUDIO_FILE_BYTES,
  validateRecordedAudioMetadata,
};

let _cachedExpoAudioModule: typeof import('expo-audio') | null | undefined =
  undefined;
let _cachedExpoFileSystem:
  typeof import('expo-file-system') | null | undefined = undefined;

/**
 * Checks whether native microphone recording via expo-audio is compiled into this binary.
 */
export function isAudioCaptureAvailable(): boolean {
  if (Platform.OS === 'web') {
    return false;
  }
  try {
    const native = requireOptionalNativeModule('ExpoAudio');
    return native !== null && native !== undefined;
  } catch {
    return false;
  }
}

export function getSafeExpoAudioModule(): typeof import('expo-audio') | null {
  if (_cachedExpoAudioModule !== undefined) {
    return _cachedExpoAudioModule;
  }
  if (!isAudioCaptureAvailable()) {
    _cachedExpoAudioModule = null;
    return null;
  }
  try {
    // eslint-disable-next-line @typescript-eslint/no-require-imports
    _cachedExpoAudioModule = require('expo-audio');
  } catch {
    _cachedExpoAudioModule = null;
  }
  return _cachedExpoAudioModule ?? null;
}

function getSafeFileSystemModule(): typeof import('expo-file-system') | null {
  if (_cachedExpoFileSystem !== undefined) {
    return _cachedExpoFileSystem;
  }
  try {
    // eslint-disable-next-line @typescript-eslint/no-require-imports
    _cachedExpoFileSystem = require('expo-file-system');
  } catch {
    _cachedExpoFileSystem = null;
  }
  return _cachedExpoFileSystem ?? null;
}

export type MicrophonePermissionResult = {
  granted: boolean;
  canAskAgain: boolean;
  status: string;
};

/**
 * Requests Android/iOS runtime microphone recording permission cleanly.
 */
export async function requestMicrophonePermission(): Promise<MicrophonePermissionResult> {
  const mod = getSafeExpoAudioModule();
  if (!mod || typeof mod.requestRecordingPermissionsAsync !== 'function') {
    return { granted: false, canAskAgain: false, status: 'unavailable' };
  }
  try {
    const res = await mod.requestRecordingPermissionsAsync();
    return {
      granted: Boolean(res?.granted),
      canAskAgain: res?.canAskAgain !== false,
      status: String(res?.status || (res?.granted ? 'granted' : 'denied')),
    };
  } catch {
    return { granted: false, canAskAgain: false, status: 'error' };
  }
}

/**
 * Configures OS audio focus/session cleanly for active speech capture vs idle.
 */
export async function configureRecordingAudioMode(
  allowsRecording: boolean,
): Promise<void> {
  const mod = getSafeExpoAudioModule();
  if (!mod || typeof mod.setAudioModeAsync !== 'function') {
    return;
  }
  try {
    await mod.setAudioModeAsync({
      allowsRecording,
      playsInSilentMode: true,
      shouldPlayInBackground: false,
      interruptionMode: allowsRecording ? 'doNotMix' : 'mixWithOthers',
    });
  } catch {
    // Non-fatal on devices restricting audio mode overrides
  }
}

/**
 * Builds Android-compatible compressed .m4a (MPEG-4 AAC) recording options with bounded file size.
 */
export function buildMealRecordingOptions(): RecordingOptions | null {
  const mod = getSafeExpoAudioModule();
  if (!mod || !mod.RecordingPresets?.HIGH_QUALITY) {
    return null;
  }
  const base = mod.RecordingPresets.HIGH_QUALITY;
  return {
    ...base,
    isMeteringEnabled: true,
    android: {
      ...base.android,
      extension: '.m4a',
      outputFormat: 'mpeg4',
      audioEncoder: 'aac',
      maxFileSize: MAX_AUDIO_FILE_BYTES,
    },
  };
}

/**
 * Reads temporary recorded file byte size synchronously/safely via expo-file-system File API.
 */
export function inspectTempAudioFileSize(
  uri: string | null | undefined,
): number | null {
  if (!uri) return null;
  const fsMod = getSafeFileSystemModule();
  if (!fsMod?.File) return null;
  try {
    const file = new fsMod.File(uri);
    if (!file.exists) return 0;
    return typeof file.size === 'number' ? file.size : null;
  } catch {
    return null;
  }
}

/**
 * Immediately deletes temporary local audio files on success, cancellation, or unmount.
 */
export function deleteTempAudioFile(uri: string | null | undefined): void {
  if (!uri) return;
  const fsMod = getSafeFileSystemModule();
  if (!fsMod?.File) return;
  try {
    const file = new fsMod.File(uri);
    if (file.exists) {
      file.delete();
    }
  } catch {
    // Best-effort cleanup; cache files should never crash UI teardown
  }
}

export type NativeAudioRecorderHandle = {
  recorder: AudioRecorder;
  state: RecorderState;
};
