export type CloudConfig = {
  state: 'missing' | 'invalid' | 'configured';
  message: string;
};
// Configuration alone never enables network access in this integration-boundary release.
export function cloudConfiguration(url?: string, key?: string): CloudConfig {
  if (!url?.trim() && !key?.trim())
    return {
      state: 'missing',
      message: 'Cloud is not configured. Your data stays on this device.',
    };
  try {
    const parsed = new URL(url ?? '');
    if (
      parsed.protocol !== 'https:' ||
      !/^[a-z0-9-]+\.supabase\.co$/.test(parsed.hostname) ||
      parsed.username ||
      parsed.password ||
      parsed.port ||
      parsed.pathname !== '/' ||
      parsed.search ||
      parsed.hash ||
      !/^sb_publishable_[A-Za-z0-9_-]+$/.test(key ?? '')
    )
      throw Error();
    return {
      state: 'configured',
      message:
        'Public configuration is present. Authentication and cloud sync are not enabled in this build.',
    };
  } catch {
    return {
      state: 'invalid',
      message:
        'Cloud configuration is incomplete or unsupported. Offline features remain available.',
    };
  }
}
