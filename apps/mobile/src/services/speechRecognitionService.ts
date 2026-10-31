/**
 * Safe Speech Recognition Service & Platform Adapter.
 *
 * Prevents "Cannot find native module 'ExpoSpeechRecognition'" runtime crashes when
 * running in environments where the native module is not compiled into the host binary
 * (such as stock Expo Go, web browsers, or development shells prior to native rebuild).
 *
 * Responsibilities:
 * - Runtime detection of native module availability using requireOptionalNativeModule.
 * - Distinguishing stock Expo Go from custom development builds or standalone APKs.
 * - Safe event listener hook (useSafeSpeechRecognitionEvent) that conforms to React Rules
 *   of Hooks and never crashes if the module is unlinked.
 * - Safe lifecycle methods (start, stop, abort, requestPermissions) with clear fallback behavior.
 */

import { useEffect, useRef } from 'react';
import { Platform } from 'react-native';
import { isRunningInExpoGo } from 'expo';
import { requireOptionalNativeModule } from 'expo-modules-core';

let _cachedSpeechModule: any = undefined;

/**
 * Returns whether the native speech recognition module is compiled and available
 * in the current running application binary.
 */
export function isNativeSpeechModuleAvailable(): boolean {
  if (Platform.OS === 'web') {
    return false;
  }
  // Stock Expo Go client does not bundle custom third-party native modules
  if (isRunningInExpoGo()) {
    return false;
  }
  try {
    const native = requireOptionalNativeModule('ExpoSpeechRecognition');
    return native !== null && native !== undefined;
  } catch {
    return false;
  }
}

/**
 * Lazily and safely retrieves the ExpoSpeechRecognitionModule wrapper.
 * Returns null if the native module is not present in the runtime binary.
 */
export function getSafeSpeechRecognitionModule(): any | null {
  if (_cachedSpeechModule !== undefined) {
    return _cachedSpeechModule;
  }

  if (!isNativeSpeechModuleAvailable()) {
    _cachedSpeechModule = null;
    return null;
  }

  try {
    // Only load the module at runtime if the underlying native module exists in JSI
    // eslint-disable-next-line @typescript-eslint/no-require-imports
    const expSpeech = require('expo-speech-recognition');
    _cachedSpeechModule = expSpeech.ExpoSpeechRecognitionModule || null;
  } catch {
    _cachedSpeechModule = null;
  }

  return _cachedSpeechModule;
}

/**
 * Safe hook that listens to native speech recognition events.
 * Conforms to Rules of Hooks by running unconditionally, but safely skips subscription
 * if the native module is not present in the current runtime environment.
 */
export function useSafeSpeechRecognitionEvent(
  eventName: string,
  listener: (event: any) => void,
) {
  const listenerRef = useRef(listener);

  useEffect(() => {
    listenerRef.current = listener;
  }, [listener]);

  useEffect(() => {
    const mod = getSafeSpeechRecognitionModule();
    if (!mod || typeof mod.addListener !== 'function') {
      return;
    }

    const callback = (event: any) => {
      listenerRef.current?.(event);
    };

    const subscription = mod.addListener(eventName, callback);
    return () => {
      subscription?.remove?.();
    };
  }, [eventName]);
}

/**
 * Checks whether the native speech recognition service is operational on device.
 */
export function isSpeechRecognitionServiceAvailable(): boolean {
  const mod = getSafeSpeechRecognitionModule();
  if (!mod || typeof mod.isRecognitionAvailable !== 'function') {
    return false;
  }
  try {
    return Boolean(mod.isRecognitionAvailable());
  } catch {
    return false;
  }
}

/**
 * Requests microphone and speech permissions from the host OS if the native module is present.
 */
export async function requestSpeechPermissions(): Promise<{
  granted: boolean;
}> {
  const mod = getSafeSpeechRecognitionModule();
  if (!mod || typeof mod.requestPermissionsAsync !== 'function') {
    return { granted: false };
  }
  try {
    const result = await mod.requestPermissionsAsync();
    return { granted: Boolean(result?.granted) };
  } catch {
    return { granted: false };
  }
}

/**
 * Starts speech recognition session if native module is present.
 */
export function startSpeechRecognition(options: {
  lang?: string;
  interimResults?: boolean;
  continuous?: boolean;
  volumeChangeEventOptions?: {
    enabled?: boolean;
    intervalMillis?: number;
  };
}): void {
  const mod = getSafeSpeechRecognitionModule();
  if (!mod || typeof mod.start !== 'function') {
    throw new Error(
      'Native speech recognition is not supported in Expo Go. Please use a development build or type your meal description.',
    );
  }
  mod.start(options);
}

/**
 * Stops speech recognition session.
 */
export function stopSpeechRecognition(): void {
  const mod = getSafeSpeechRecognitionModule();
  if (mod && typeof mod.stop === 'function') {
    try {
      mod.stop();
    } catch {
      // ignore
    }
  }
}

/**
 * Aborts speech recognition session immediately.
 */
export function abortSpeechRecognition(): void {
  const mod = getSafeSpeechRecognitionModule();
  if (mod && typeof mod.abort === 'function') {
    try {
      mod.abort();
    } catch {
      // ignore
    }
  }
}
