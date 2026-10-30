# Roadmap: Bites2Go

## Overview

Bites2Go has implemented its core offline tracking foundation (Stages 4 through 11 and My Meals & Recipes), including local SQLite diary persistence, health/weight goals, custom foods, recipes, and read-only nutrition insights. This roadmap outlines the active release gates, security patching, and future cloud/AI milestones.

## Phases

- [ ] **Phase 1: Physical Android Acceptance & Verification** - Complete on-device validation of TalkBack, keyboard avoidance, hardware Back, and high-density layouts.
- [ ] **Phase 2: Upstream Tooling Security Remediation** - Resolve upstream Expo CLI/Zod (3 high / 5 low) audit advisories once compatible vendor patches release.
- [ ] **Phase 3: Production Cloud Authentication & Sync UI** - Implement Supabase Auth, SecureStore session persistence, and transactional coordinator.
- [ ] **Phase 4: AI Food Recognition & Image Assistance** - Integrate multimodal food estimation with strict user confirmation and manual fallbacks.

## Phase Details

### Phase 1: Physical Android Acceptance & Verification
**Goal**: Verify all delivered mobile features on a real Android device according to `docs/TEST_PLAN.md`.
**Depends on**: Shipped Stage 11 codebase
**Requirements**: [REL-01]
**Success Criteria**:
  1. TalkBack screen reader cleanly announces all nutrient progress, buttons, and chart alternatives.
  2. Keyboard avoidance functions reliably across all custom food and recipe entry screens.
  3. Hardware Back button respects the uncertain-write exit reconciliation without leaking stale records.
**Plans**: 2 plans

Plans:
- [ ] 01-01: Execute Android device acceptance tests for Home, Diary, Calendar, and Profile.
- [ ] 01-02: Execute Android device acceptance tests for Custom Foods, Recipes, Weight, and Insights.

### Phase 2: Upstream Tooling Security Remediation
**Goal**: Clear `npm audit` exit 1 status by updating Expo CLI and transitive dependencies once supported.
**Depends on**: Phase 1
**Requirements**: [REL-02]
**Success Criteria**:
  1. `npm audit` exits 0 with zero high-severity vulnerabilities.
  2. Android Hermes bundle export and all 98 automated unit/integration tests remain passing.
**Plans**: 1 plan

Plans:
- [ ] 02-01: Apply compatible Expo CLI patch upgrades and re-verify full test suite.

### Phase 3: Production Cloud Authentication & Sync UI
**Goal**: Enable secure opt-in cloud synchronization backed by Supabase PostgreSQL.
**Depends on**: Phase 2
**Requirements**: [SYNC-01, SYNC-02, SYNC-03]
**Success Criteria**:
  1. User can authenticate with Supabase Auth using secure local session token storage.
  2. Transactional sync coordinator syncs `bites2go.diary.v1` records with cloud RPC.
**Plans**: 3 plans

Plans:
- [ ] 03-01: Implement Supabase Auth UI and Expo SecureStore session manager.
- [ ] 03-02: Wire client sync coordinator to `sync_diary_record` RPC.
- [ ] 03-03: Implement conflict resolution and account switching flows.

### Phase 4: AI Food Recognition & Image Assistance
**Goal**: Provide optional photo-based meal suggestions with manual review.
**Depends on**: Phase 3
**Requirements**: [AI-01, AI-02]
**Success Criteria**:
  1. Camera / photo picker captures meal image with local EXIF stripping.
  2. Suggested ingredients and portions require explicit user confirmation before diary entry creation.
**Plans**: 2 plans

Plans:
- [ ] 04-01: Implement camera capture, image privacy sanitization, and estimation client.
- [ ] 04-02: Build confirmation dialog and food catalogue mapping interface.

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2 → 3 → 4

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Physical Android Acceptance | 0/2 | Ready to plan | - |
| 2. Security Remediation | 0/1 | Blocked on upstream | - |
| 3. Cloud Auth & Sync | 0/3 | Deferred | - |
| 4. AI Recognition | 0/2 | Deferred | - |
