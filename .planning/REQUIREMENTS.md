# Requirements: Bites2Go

**Defined:** 2026-10-30
**Core Value:** Deterministic, trustworthy nutritional tracking with immutable historical meal snapshots and zero mandatory cloud dependencies.

## v1 Requirements

Requirements for current mobile app foundation and release readiness.

### Core Tracking & Diary

- [x] **DIARY-01**: User can log foods into Breakfast, Lunch, Snacks, and Dinner with portion scaling.
- [x] **DIARY-02**: User can navigate past dates and edit or delete existing entries with confirmation.
- [x] **DIARY-03**: Diary entries preserve immutable nutritional snapshots at the moment of creation.
- [x] **DIARY-04**: Monthly calendar displays entry indicators and inline historical day logs.

### Health, Goals & BMI

- [x] **HEALTH-01**: User can log dated weight measurements and view chronological progress.
- [x] **HEALTH-02**: Adult BMI is calculated with one-decimal precision and medical screening caveats.
- [x] **HEALTH-03**: User can configure effective-dated calorie and macronutrient targets.
- [x] **HEALTH-04**: Daily nutrition dashboard shows signed remaining amounts and progress indicators.

### Food Library & Recipes

- [x] **LIB-01**: User can create custom foods with per-serving nutrition and optional description.
- [x] **LIB-02**: User can assemble multi-ingredient recipes with calculated yield and serving counts.
- [x] **LIB-03**: User can favourite foods and quick-add recent items directly into the diary.
- [x] **LIB-04**: My Meals separates multi-ingredient recipes from single custom foods with log actions.

### Insights & Analysis

- [x] **INSIGHT-01**: User can view rolling 7-day, 30-day, and custom 1–92 day nutritional trends.
- [x] **INSIGHT-02**: Insights excludes today-in-progress and incomplete meal days from average calculations.
- [x] **INSIGHT-03**: Nutrient observations highlight target consistency and actual in-range weight history.

### Release Readiness & Security

- [ ] **REL-01**: Physical Android device acceptance checklist (TalkBack, keyboard, system navigation).
- [ ] **REL-02**: Upstream Expo CLI vulnerability remediation (resolve 3 high / 5 low advisories when patched).
- [x] **REL-03**: Credential scanner and static analysis report zero leaked secrets or tokens.

## v2 Requirements

Deferred to future releases.

### Cloud Synchronization

- **SYNC-01**: User can create a Supabase account with email/password or magic link.
- **SYNC-02**: User can opt-in to encrypt and synchronize diary records across multiple Android devices.
- **SYNC-03**: Conflict resolution interface prompts user on desynchronized edits.

### AI Assistance

- **AI-01**: User can photograph a meal to receive estimated food mapping suggestions.
- **AI-02**: AI suggestions require explicit manual user confirmation before writing to the diary.

## Out of Scope

| Feature | Reason |
|---------|--------|
| Automatic Calorie Prescriptions | Medical liability; app supports user-configured goals only |
| Pediatric / Pregnancy BMI | Specialized clinical domain outside general adult wellness |
| Cloud Sync in Current Client | Preserves 100% offline privacy and zero-account simplicity |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| DIARY-01..04 | Shipped (Stages 4-6) | Complete |
| HEALTH-01..04 | Shipped (Stage 7) | Complete |
| LIB-01..04 | Shipped (Stage 8 & My Meals) | Complete |
| INSIGHT-01..03 | Shipped (Stage 10) | Complete |
| REL-01 | Phase 1 | Pending |
| REL-02 | Phase 2 | Pending |
| REL-03 | Shipped (Stage 11) | Complete |
| SYNC-01..03 | Phase 3 | Deferred |
| AI-01..02 | Phase 4 | Deferred |

---
*Requirements defined: 2026-10-30*
