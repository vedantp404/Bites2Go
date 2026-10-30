# Bites2Go

## What This Is

Bites2Go is a privacy-first, offline-first mobile nutrition and weight tracking application built with React Native and Expo. It provides deterministic macronutrient and calorie scaling, immutable diary snapshots, adult BMI and weight goal progress, custom foods and multi-ingredient recipes, and rolling nutritional insights without requiring an account or internet connectivity.

## Core Value

Deterministic, trustworthy nutritional tracking with immutable historical meal snapshots and zero mandatory cloud dependencies.

## Business Context

- **Customer**: Adults (20+) seeking reliable personal nutrition awareness, macro tracking, and weight management.
- **Revenue model**: Offline-first standalone mobile app; cloud backup/sync is optional.
- **Success metric**: 100% data integrity, sub-200ms screen transitions, and zero historical record drift.
- **Strategy notes**: See `docs/PRD.md` and `docs/MEMORY.md`.

## Requirements

### Validated

- [x] Local SQLite-backed food diary with portion scaling, meal categories, and date navigation.
- [x] Curated Indian and standard food database with immutable reference snapshots.
- [x] Monthly calendar with inline historical diary inspection and entry markers.
- [x] Dated weight logs, adult BMI screening calculations, and effective-dated calorie/macro goals.
- [x] Custom food creation, recipe builder with yield scaling, favourites, and recents.
- [x] Rolling 7/30/custom-day nutrition insights, target consistency, and observations.
- [x] Fail-closed Supabase backend foundation with RLS policies (cloud disabled by default).
- [x] Stage 11 development acceptance (98 automated unit/integration tests passing).

### Active

- [ ] Physical Android device acceptance testing (TalkBack, touch targets, keyboard handling, system bars).
- [ ] Upstream Expo CLI dependency vulnerability remediation (3 high / 5 low audit items).

### Out of Scope

- Automatic AI food recognition — deferred until manual tracking foundation is certified.
- Cloud synchronization in current build — intentionally disabled to preserve offline privacy.
- Clinical or pediatric dietary prescriptions — general adult wellness scope only.

## Context

Built on React Native 0.88.1, React 19.3.0, and Expo SDK 58.0.21 targeting Android. Persists data locally via `expo-sqlite/kv-store` with serialized queues. All calculation engines (`scaleNutrients`, `diaryTotals`, `insightView`) are pure TypeScript functions.

## Constraints

- **Storage**: Single-writer serialized local SQLite KV documents (`bites2go.*.v1`).
- **Dates**: Local `YYYY-MM-DD` evaluated at noon; no UTC timestamp slicing for calendar dates.
- **Security**: Strict zero-secret policy in mobile code; cloud sync must remain fail-closed offline by default.
- **Platform**: Android primary platform with strict WCAG AA contrast compliance.

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Offline-First Local SQLite | Immediate user utility without mandatory registration or network | ✓ Good |
| Immutable Meal Snapshots | Editing source foods never mutates historical diary records | ✓ Good |
| Injected Repository Interfaces | Decouples storage from domain logic, enabling fast in-memory test suites | ✓ Good |
| Supabase RLS & RPC Foundation | Prepared cloud sync contract without activating live client traffic | ✓ Good |

---
*Last updated: 2026-10-30 after /gsd-ingest-docs*
