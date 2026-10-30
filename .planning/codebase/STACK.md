---
last_mapped_commit: f54c1f195289ce4d54a79e7def2170fb84f20858
last_mapped_at: 2026-10-30
---
# Technology Stack

**Analysis Date:** 2026-10-30

## Languages

**Primary:**
- TypeScript 6.0.3 (`apps/mobile/tsconfig.json`, `apps/mobile/package.json`) - Core application language used across all mobile screens, domain modules, state providers, components, and storage adapters.
- JavaScript / Node ESM (`apps/mobile/eslint.config.js`, `apps/mobile/tests/*.test.mjs`) - ESLint flat configuration and Node test runner test suites.

**Secondary:**
- SQL / PostgreSQL (`supabase/migrations/202610300001_diary_sync.sql`, `supabase/tests/bootstrap-local.sql`, `supabase/tests/diary-access.sql`) - Backend database migration and isolation/RLS test scripts.
- PowerShell (`scripts/test-cloud-sql.ps1`) - Local PostgreSQL verification and database test automation.
- Python 3 (`scripts/security-scan.py`) - Scoped repository and build artifact credential/secret pattern scanner.

## Runtime

**Environment:**
- Node.js 22.13+ (utilizing `--experimental-strip-types` to execute TypeScript domain imports in tests directly without transpilation, matching Expo SDK 58 minimums).
- React Native 0.88.1 running on the Hermes JavaScript engine.
- Android OS target (configured with adaptive icon, splash screen, and system navigation bar settings in `apps/mobile/app.json`).

**Package Manager:**
- npm 10+ (`apps/mobile/package-lock.json`)
- Lockfile: present (`apps/mobile/package-lock.json`)

## Frameworks

**Core:**
- React 19.3.0 (`apps/mobile/package.json`) - Component-based user interface rendering.
- React Native 0.88.1 (`apps/mobile/package.json`) - Cross-platform mobile foundation.
- Expo SDK 58.0.21 (`apps/mobile/package.json`, `apps/mobile/app.json`) - Application platform, build system, and native device access.
- Expo Router 58.0.28 (`apps/mobile/app/`) - File-based routing and navigation structure with nested tabs and stack routes.

**Testing:**
- Node.js Built-in Test Runner (`node:test`, `node:assert/strict`) (`apps/mobile/tests/*.test.mjs`) - Fast, dependency-free test framework executed via `node --experimental-strip-types --test tests/*.test.mjs`.
- Disposable PostgreSQL Local Testing (`scripts/test-cloud-sql.ps1`) - Synthetic test environment validating Supabase Row Level Security (RLS) policies and RPC functions.

**Build/Dev:**
- TypeScript 6.0.3 (`apps/mobile/tsconfig.json`) - Strict type checking (`strict: true`, `allowImportingTsExtensions: true`).
- ESLint 9.39.5 (`apps/mobile/eslint.config.js`) - Flat configuration with `eslint-config-expo/flat`.
- Prettier 3.9.10 (`apps/mobile/.prettierrc.json`) - Formatter (`{ "singleQuote": true, "trailingComma": "all" }`).
- Expo Doctor 1.21.5 (`apps/mobile/package.json`) - Health checker ensuring dependency compatibility.
- Metro Bundler - Module bundler integrated with Expo CLI.

## Key Dependencies

**Critical:**
- `expo-sqlite` ~58.0.14 (`apps/mobile/package.json`, `apps/mobile/src/storage/localDiary.ts`) - Local key-value store (`expo-sqlite/kv-store`) powering the offline-first persistence layer for diaries, health, library, and appearance preferences.
- `expo-router` ~58.0.28 (`apps/mobile/package.json`, `apps/mobile/app/`) - Handles all app navigation, deep linking, tabs, and modals.
- `expo-crypto` ~58.0.7 (`apps/mobile/package.json`) - Used for generating RFC4122 v4 UUIDs for diary entries, custom food items, recipes, and weight entries.
- `react-native-svg` 15.16.0 (`apps/mobile/package.json`, `apps/mobile/src/components/InsightChart.tsx`, `apps/mobile/src/components/WeightChart.tsx`) - Renders vector charts for nutrient trends and weight progress.
- `react-native-safe-area-context` ~5.10.1 (`apps/mobile/package.json`) - Coordinates viewport boundaries, status bars, and notch padding.
- `react-native-screens` ~4.30.0 (`apps/mobile/package.json`) - Native navigation view primitive for memory management and performance.

**Infrastructure:**
- `expo-splash-screen` ~58.0.12 (`apps/mobile/package.json`, `apps/mobile/app/_layout.tsx`) - Holds native splash until theme preferences and data providers initialize.
- `expo-status-bar` ~58.0.4 (`apps/mobile/package.json`) - Dynamic theme-driven status bar appearance.
- `expo-navigation-bar` ~58.0.4 (`apps/mobile/package.json`) - Dynamic Android system bottom bar navigation theme styling.
- `expo-system-ui` ~58.0.7 (`apps/mobile/package.json`) - Android background color coordination.
- `expo-linear-gradient` ~58.0.3 (`apps/mobile/package.json`) - Aesthetic visual gradients on dashboard cards.
- `expo-constants` ~58.0.14 (`apps/mobile/package.json`) - Runtime configuration and project metadata.

## Configuration

**Environment:**
- Environment variables:
  - `EXPO_PUBLIC_SUPABASE_URL` (`apps/mobile/.env.example`, `.env.example`)
  - `EXPO_PUBLIC_SUPABASE_PUBLISHABLE_KEY` (`apps/mobile/.env.example`, `.env.example`)
- Fail-closed design: In Stage 9 backend foundation, cloud networking is completely disabled by default if public credentials are absent or blank (`apps/mobile/src/cloud/config.ts`).
- Public configs are bundled into the client build; secrets (service roles, private tokens) are strictly forbidden in client `.env` files.

**Build:**
- `apps/mobile/app.json` - Expo manifest configuring name (`Bites2Go`), slug (`bites2go`), scheme (`bites2go`), orientation, icons, and plugins.
- `apps/mobile/tsconfig.json` - Extends `expo/tsconfig.base` with `strict: true` and `allowImportingTsExtensions: true`.
- `apps/mobile/eslint.config.js` - Flat ESLint configuration.
- `apps/mobile/.prettierrc.json` - Single quotes and trailing commas.

## Platform Requirements

**Development:**
- Node.js 22.13+ with npm.
- PowerShell 7+ or Windows PowerShell (for PostgreSQL script execution).
- Python 3 (for security scan utility).
- Android SDK / Android Virtual Device or physical Android phone.

**Production:**
- Standalone Android APK / AAB built via signed EAS Build (`eas build --platform android`); `npx expo export --platform android` produces static JavaScript and asset bundles for export verification.
- Supabase PostgreSQL (prepared backend migration, cloud sync is offline-by-default in mobile client).

---

*Stack analysis: 2026-10-30*
