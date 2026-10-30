# Stage 11 release-readiness review

## Final development acceptance — 2026-10-30

**Accepted for continued development under the user's explicit Stage 11 Final Acceptance, Commit and Push instruction. Production release remains blocked.** This decision supersedes earlier investigation-only/no-commit statements below; those describe the historical review, not current authorization. It accepts the documented audit exception for this development commit only, not a security clearance or public-release risk waiver.

Final review found only intended Stage 11 application/test/scanner/documentation changes; no new regression or data-integrity issue was identified. Diary reconciliation is read-only, pending writes remain guarded, original snapshot/order validation is retained, checkpoint rejection occurs before writes, and schemas/lockfile/dependencies are unchanged. Native interaction is not proven by code review.

Codex reran the actual scripts: `npm test` 96/96; `npm run typecheck`, `npm run lint`, `npm run format:check`, `npm run doctor` (20/20), `npx expo config --type public`, Android export with source maps, and `./scripts/test-cloud-sql.ps1` all passed. PostgreSQL was local/disposable with synthetic identities and stopped after the test. `python scripts/security-scan.py --artifact "$env:TEMP/bites2go-acceptance-android"` passed: 444 files/blobs, including 298 historical blobs and 31 export files, zero pattern findings. Synthetic scanner checks passed; the scanner is bounded and does not certify absence of every secret.

`npm audit --json` **FAILED, exit 1: 3 high / 5 low**. All vulnerability rows are identical to the previous investigation. No forced fix, override, suppression or dependency change. Zod/deepmerge risks and mitigations below remain applicable. The fresh 1,334-module Android source map excludes both libraries; this does not make tooling risk zero. Export is a 2.4 MB Hermes bundle, not an installed signed APK/AAB. Acceptance logs/export are in system TEMP with the `bites2go-acceptance-` prefix, outside Git.

User reports regular physical Android testing after stages; explicit earlier reports include Stage 4 Android verification and the recorded Stage 5 save/restart/edit/delete acceptance. There is no specific Stage 11 manual-test confirmation in this acceptance request. Codex performed no device/emulator tests, signed build/install or live Supabase tests. Stage 11 Back/retry/restart, theme/TalkBack/large-text and native release checks remain on the checklist. Cloud remains disabled.

Commit/push to master is authorized after this review; the final chat report records actual local/remote hashes and clean-tree verification after commands run. Do not infer push success from this pre-commit document. Stop after Stage 11; no next feature is authorized.

Reviewed 2026-10-30 on master, starting from clean local/fetched origin commit `369d562b7bfeee014810d9236f1097bef2d2ce85`. **Production release is not cleared.** No dependency or schema changes and no cloud activation. The final development acceptance above supersedes the original audit-based commit hold.

## Dependency findings

Fresh baseline and final `npm audit --json` both exit 1: **3 high, 5 low affected-package rows, two root advisories**. Installed Expo 58.0.21, React Native 0.88.1, React 19.3.0, TypeScript 6.0.3 remain unchanged. npm/package-lock are authoritative.

| Severity / affected installed package | Cause and status |
| --- | --- |
| High: zod 3.25.76 | GHSA-mrhx-c7xc-m3w5, CVE-2023-54404; unresolved |
| High: @expo/cli 58.1.17 | Propagated Zod advisory; unresolved |
| High: expo 58.0.21 | Propagated CLI/Zod advisory; unresolved |
| Low: deepmerge 4.3.1 | GHSA-gcqx-w48m-w2h4, CVE-2026-93753; unresolved |
| Low: @expo/config 58.0.9 | Propagated deepmerge advisory; unresolved |
| Low: @expo/local-build-cache-provider 58.0.9 | Propagated config/deepmerge advisory; unresolved |
| Low: @expo/metro-config 58.0.19 | Propagated config/deepmerge advisory; unresolved |
| Low: @expo/prebuild-config 58.0.17 | Propagated config/deepmerge advisory; unresolved |

**Zod:** [official advisory](https://github.com/advisories/GHSA-mrhx-c7xc-m3w5) identifies unbounded issue accumulation on invalid large collections, potentially exhausting memory; affected <4.6.6, patched 4.6.6. Actual path: expo → @expo/cli → zod. Dev lint also reaches Zod through eslint-config-expo → eslint-plugin-react-hooks. CLI 58.1.17 requires `^3.25.76`; registry queries found latest SDK-58 Expo 58.0.21, CLI 58.1.17 and Zod-3 3.25.76, all already installed. [Zod 4 migration](https://zod.dev/v4/changelog) documents breaking APIs; forcing 4.6.6 outside CLI's supported range is not a verified fix. npm's proposed Expo 51.0.39 downgrade is incompatible with this SDK/RN baseline and is rejected. Follow [Expo's supported upgrade process](https://docs.expo.dev/workflow/upgrading-expo-sdk-walkthrough/) when a compatible release exists, then rerun all checks.

Verified CLI call sites in its `build/src/start/server/`: DevToolsPlugin.schema.js (plugin command/parameter/output arrays); DevToolsPlugin.js, DevToolsPluginCliExtensionResults.js and MCPDevToolsPluginCLIExtensions.js (`safeParse`); createMCPDevToolsExtensionSchema.js (schema generation). Use trusted plugins, plugin outputs and project configuration; keep the development server on localhost or a trusted network. This reduces exposure, not a security fix.

**deepmerge:** [official advisory](https://github.com/advisories/GHSA-gcqx-w48m-w2h4) identifies prototype poisoning in returned merge objects for 4.2.0–4.3.1, with no patched release. Registry latest is 4.3.1; @expo/config requires `^4.3.1`. Verified `@expo/config/build/Config.js` merge paths combine configuration/modifications and plugin properties. Do not consume untrusted configuration/plugins. Downgrading outside the required range or forcing unrelated dependency updates is not remediation.

No app source imports either package. Final Android source map has 1,334 sources and zero zod/deepmerge module paths; this is evidence for this export, not every build or execution path. Tooling remains vulnerable and the audit gate remains failed. Recheck upstream releases/advisories before release; do not suppress the findings.

## Changes and integrity review

- Diary add/edit/delete failures can mean the write committed but its acknowledgement failed. Back/Cancel after an uncertain mutation now reloads the authoritative repository, clearing stale displayed entries/notices while loading. Hardware Back uses the same exit path. Pending writes still block exit; retries retain their original snapshots. Repository tests reproduce all three committed-but-unacknowledged outcomes. Native button/Back interaction remains manual.
- Diary document validation previously filtered the full history once per distinct date. It now groups once, retaining original entry order, identity checks, unknown nutrient semantics and per-day overflow validation. Synthetic 10,000 entries on distinct dates: three before runs 1,859/986/1,072 ms; after 93/68/61 ms on this host. This is a focused Node benchmark, not a phone startup guarantee. Regression test covers 5,000 dates and same-day versus cross-day numeric overflow.
- Optional, unmounted sync checkpoint persistence now rejects removal/rewind of acknowledged rows, including tombstones, and different payloads at the same revision. Tests verify rejected saves preserve bytes, forward revisions work and identical retries remain idempotent. No live sync enabled.
- Splash warnings retain fixed diagnostic text but no longer log raw native error objects. No observed credential leak is claimed.
- Extended existing Light/Dark contrast assertions to input, selected/elevated, primary/secondary/warning/error surface pairs. Existing chart text alternatives and 48 dp shared controls retained.

Diary, health and library use versioned documents in parameterized Expo SQLite KV storage. Absent keys initialize without replacing other domains; invalid/unsupported bytes block mutations and remain intact. Tests cover serialized writes, stale edits, failed acknowledgements, exact historical snapshots, recipe source deletion, favourites cleanup, unknown nutrients, effective-dated goals, local-date/DST boundaries and read-only insights. Temporary real SQLite close/reopen tests pass. There are no local relational foreign keys between JSON snapshots; references are validated in domain code and historical snapshots intentionally survive source deletion. Single-document writes are atomic; cross-document transactions/multi-process writers are not promised. Appearance persists separately; recents derive from real diary records. No schema migration was needed. Android native SQLite upgrade/restart acceptance still requires a device.

## Security and privacy boundary

Local PostgreSQL tests use the actual migration with synthetic auth roles and two identities: forced RLS, owner-only SELECT, anonymous/direct-write denial, owner-scoped revision RPC, retries/tombstones and account-deletion cascade pass. RPC derives owner from auth.uid(), fixes search_path and checks revisions; there are intentionally no direct INSERT/UPDATE policies granting client writes. Changing another owner's ID cannot access that owner's row. This is **not** a hosted Supabase Auth/JWT/PostgREST test. Backend payload shape/size checks do not replace full server-side nutrition validation; secure session storage, real transport/consent/conflict UI and transactional coordination remain prerequisites in BACKEND.md.

No live authentication/session storage, cloud client, uploads or app-source network/external URL calls are active. Config validates a public Supabase URL/publishable key and reports offline status; it cannot enable sync. No service credential belongs in EXPO_PUBLIC variables. Bundled food images have stable IDs/placeholders; no user file/photo import or arbitrary remote image URL is implemented. Existing route/date/identity inputs are validated before writes. Error paths preserve data and use safe messages; no raw nutrition document logging was found.

`scripts/security-scan.py` checks current tracked/unignored files, all reachable Git blobs and an optional export for private keys, AWS identifiers, GitHub tokens, Supabase secret keys and JWT-shaped credentials, reporting location/type only. It also flags unignored env files, database/signing/build files. Synthetic positive/negative probes passed. Final scan: 298 historical blobs and 31 export files, zero pattern findings. This bounded pattern scan does not prove absence of every secret, ignored local file, entropy-based credential or personal value; unreachable/deleted Git objects and remote server storage are outside scope. Source maps/build output remain in the system temporary directory, not Git or a published server.

Local nutrition/weight data is not app-encrypted, and there is no implemented export/backup/account deletion UI. Device sharing, OS backups, uninstall/data-clear loss and retention/privacy disclosures require a public-release decision. Do not test destructive uninstall with irreplaceable records. No real personal database was opened for this review.

## Accessibility and performance review

| Area | Code-level evidence / remaining device check |
| --- | --- |
| Home | Labelled calorie/macronutrient values and progress; loading/error/empty states; verify TalkBack and narrow-screen scaling |
| Search/details/My foods | Labelled query/portion controls, radio states, actual source labels and scrollable content; verify keyboard, long names, Back and uncertain-write exit |
| Diary/editor/calendar | Date/meal labels, explicit delete confirmation and calendar selection/count labels; verify modal focus restoration, day scrolling and Back |
| Profile/settings | Labelled theme choices/selected state, offline cloud disclosure; verify live System switching and startup bars |
| Progress/weight/goals | Labelled numeric/date fields, chart text/history equivalents; verify large text, keyboard, modal dismissal and date-bound errors |
| Custom foods/recipes | Shared keyboard-aware pages and accessible fields, explicit snapshots/errors; verify long ingredient lists and delete/retry flows |
| Insights | Labelled range/metric controls, distinct dot/dash encodings and exact daily text alternative; verify chart scrolling/TalkBack and 92-day range |

Contrast tests measure opaque token pairs, not rendered alpha overlays or native system bars. Screen-reader focus, clipping, font scaling and touch geometry need native testing; no device/emulator pass is claimed. Lists use ScrollView and can mount many custom foods/weights; profile realistic long histories on Android before choosing virtualization. No speculative list rewrite. Providers load shared snapshots; date indexing and insights are memoized. Small bundled images avoid uncontrolled remote image memory. Error/retry states exist, but no new global crash-recovery boundary or crash analytics was added. Remaining native crash/startup behavior is unverified.

## Validation and reproduction

From `apps/mobile`:

```powershell
npm test
npm run typecheck
npm run lint
npm run format:check
npm run doctor
npx expo config --type public
npx expo export --platform android --source-maps --output-dir "$env:TEMP/bites2go-stage11-final-android"
npm audit --json
npm ls expo react-native react typescript zod deepmerge
```

From repository root:

```powershell
./scripts/test-cloud-sql.ps1
python scripts/security-scan.py --artifact "$env:TEMP/bites2go-stage11-final-android"
git diff --check
git status --short --branch
```

| Check | Actual result |
| --- | --- |
| Baseline unit/integration suite | PASS 93/93 |
| Final unit/integration suite | PASS 96/96; existing tests retained, three added |
| Types, lint, formatting | PASS; initial set-state-in-effect lint regression corrected and rerun |
| Expo Doctor | PASS 20/20 |
| Public configuration | PASS |
| Android export | PASS, Hermes bundle plus source map; not an APK/AAB or installed device |
| Local PostgreSQL policy integration | PASS; disposable server stopped/removed |
| Dependency audit | FAIL, exit 1: 3 high / 5 low, unchanged |
| Credential-pattern scan | PASS, zero matches in scoped current/history/export inputs |
| Hosted Supabase | NOT RUN; disabled/unconfigured |
| Native Android acceptance, signed build/install | NOT RUN; requires device/build setup |

Existing Node experimental SQLite/module-type and terminal NO_COLOR/FORCE_COLOR warnings are not suppressed. No dependency changes or forced audit fixes. Final export basename: `entry-d71e36f6e25981908dcf9510f40157af.hbc` (2.4 MB). Temporary audit/test/export logs are development evidence only and are not committed.

## Release checklist (unchecked means pending)

- [x] Unit/storage/calculation/ownership checks and static/Expo validation above.
- [x] Review scoped diff and tracked/history/export credential patterns; preserve SDK, schemas and user data.
- [ ] Resolve high/low upstream advisories safely (or separately record a formal production security decision), repeat audit and full checks; production release remains blocked. The final user-authorized exception permits this development commit only.
- [ ] Fresh install on a spare/test Android profile: empty diary/health/library, no demo meals, offline mode without credentials.
- [ ] Upgrade an existing test installation without clearing data: record diary totals, custom food, recipe/favourite, dated goals, weight and appearance first; compare after upgrade.
- [ ] Save/edit/delete each domain, force-stop/reopen and restart phone; verify exact values and history, no duplicates. For fault-injected uncertain writes, exit via button and Android Back and confirm persisted outcome/retry state.
- [ ] Airplane-mode startup and logging; no dependency on cloud; invalid config still leaves local app usable.
- [ ] Light/Dark/System, OS theme switch and cold start; verify status/navigation bars and contrast visually.
- [ ] Every screen at large font/display scale, narrow width, long food/recipe names: scroll to final action, open keyboard, dismiss modal with Back, preserve unsaved/cancel semantics.
- [ ] TalkBack: ordered labels/values/selected states, charts' exact text alternatives, delete modal focus and restoration, no colour-only meaning.
- [ ] Date boundary, effective goal revisions, unknown nutrient, deleted source snapshots, 92-day insights and long-list responsiveness on Android.
- [ ] Configure Android application identity/signing/build profile; build/install a signed release APK/AAB and verify native dependencies/permissions/startup. Export alone is insufficient.
- [ ] Agree privacy/retention/backup/encryption and data-loss disclosures; verify release credential handling and actual package permissions/backup behavior.
- [ ] If cloud is later authorized, complete separate BACKEND.md rollout gates and two-account hosted security tests before activation.

For current Expo Go testing: `cd C:\Users\Asus\Music\Bites2Go\apps\mobile`, then `npx expo start --clear`; use the compatible SDK-58 Android Expo Go on the same trusted Wi-Fi and scan the QR code. For local emulator/USB development, prefer `npx expo start --localhost` with the appropriate device connection. This review did not launch either.

## Historical follow-up dependency investigation (2026-10-30; commit restriction superseded by final acceptance)

User explicitly requests investigation only: **no commit or push**. Existing Stage 11 content was hashed before investigation; every existing file was byte-identical after all commands and before these documentation additions. Code, tests, package.json and package-lock.json remain unchanged. No next phase, account creation or cloud activation. This investigation does not silently redefine audit acceptance criteria or declare continued-development/public-release risk accepted; that decision remains for user review.

Fresh audit still exits 1 with 3 high / 5 low. The following are eight affected-package rows, not eight independent vulnerabilities. Parent/version edges come from the lockfile and installed manifests; affected propagation ranges below are npm's metadata, not independent package advisories.

| Installed package | Severity / relationship | Introducing parent(s) | npm affected-package range | Advisory / fix status |
| --- | --- | --- | --- | --- |
| zod 3.25.76 | high / transitive | @expo/cli ^3.25.76; also eslint-plugin-react-hooks via eslint-config-expo | `<4.6.6` | Z; unresolved |
| @expo/cli 58.1.17 | high / transitive | expo ^58.1.17 | `>=0.19.0-canary-20240625-2333e70` | Z; unresolved |
| expo 58.0.21 | high / direct | Application (direct dependency) | `>=52.0.0-canary-20240625-2333e70` | Z; unresolved |
| deepmerge 4.3.1 | low / transitive | @expo/config ^4.3.1 | `>=4.2.0` | D; unresolved |
| @expo/config 58.0.9 | low / transitive | expo/CLI/metro/prebuild/cache-provider ~58.0.9 | `>=9.1.0-canary-20240628-1ba8152` | D; unresolved |
| @expo/local-build-cache-provider 58.0.9 | low / transitive | expo ^58.0.9 | `*` | D; unresolved |
| @expo/metro-config 58.0.19 | low / transitive | expo ~58.0.19; CLI 58.0.19 | `>=0.19.0-canary-20240625-2333e70` | D; unresolved |
| @expo/prebuild-config 58.0.17 | low / transitive | CLI ^58.0.17 | `>=7.1.0-canary-20240904-69100c1` | D; unresolved |

**Z:** [GHSA-mrhx-c7xc-m3w5](https://github.com/advisories/GHSA-mrhx-c7xc-m3w5), CVE-2023-54404; root range <4.6.6, patched 4.6.6. CLI and Expo high rows inherit this advisory and also have low-severity deepmerge paths. Residual risk is validation memory exhaustion in development/plugin tooling. Actual CLI schema/call sites are listed above. A bounded probe loaded the installed DevToolsPluginOutputSchema and passed arrays of 10/100/1,000 null items; safeParse returned 10/100/1,000 issues. This demonstrates issue growth in the installed schema, not a remotely exploitable end-to-end attack or out-of-memory test. No user data or network listener was involved.

**D:** [GHSA-gcqx-w48m-w2h4](https://github.com/advisories/GHSA-gcqx-w48m-w2h4), CVE-2026-93753; root range >=4.2.0 <=4.3.1, no patched version listed. The root npm row reports the broader >=4.2.0 range; keep that distinction. Residual risk is poisoned returned merge-object prototypes when hostile objects reach Expo config/plugin merges. Installed Config.js call sites were rechecked. Project config is static app.json; no app-user input path into these merges was found. This is not proof against a compromised plugin/build dependency. The cache/metro/prebuild rows inherit this same root risk.

### Safe options evaluated in requested order

1. **Compatible patch/minor:** fresh official npm metadata reports Expo 58.0.21, CLI 58.1.17, config 58.0.9, metro-config 58.0.19, prebuild-config 58.0.17 and cache-provider 58.0.9 as latest matching SDK-58 releases, all already installed. Latest Zod-3 is 3.25.76; latest deepmerge is 4.3.1. No compatible patched candidate found.
2. **Supported SDK/CLI update:** Expo and CLI `dist-tags.latest` match those installed versions. No later stable SDK/CLI candidate exists in queried metadata. Canary/next tags are not evidence of a supported security fix. npm proposes Expo 51.0.39 as a semver-major change; this is a downgrade incompatible with the established SDK-58/RN-0.88.1 baseline, not an acceptable remediation.
3. **Transitive resolution:** registry dependencies confirm CLI requires Zod `^3.25.76`, config requires deepmerge `^4.3.1`. A Zod-4 override crosses the declared major range and documented breaking APIs. A deepmerge downgrade below 4.2 crosses its parent's range; changing the reported affected tree would not establish compatibility or security. No overrides, resolutions, installs, lockfile deletion or manual lock edits applied. npm's `fixAvailable: true` on metro/prebuild alone does not identify a safe patched root; both latest parents still resolve the affected config/deepmerge chain.
4. **Exposure mitigation, not a fix:** use reviewed local config, trusted plugins and plugin output; avoid processing arbitrary third-party schemas/configuration or enabling unneeded DevTools/MCP extensions. Installed `npx expo start --help` confirms `--localhost` as a supported hosting option (default is LAN). Prefer localhost with a configured emulator/USB connection; localhost QR access alone does not work from a separate Wi-Fi phone. If LAN is required, use a trusted private network and no tunnel/public port exposure. `--offline` skips outbound requests but does not replace host restriction. These controls cannot neutralize malicious local plugins or remove the advisory.

Fresh export map: 1,334 source modules, zero zod/deepmerge paths; no imports in app/src. This supports absence from this Android JS export only, not a guarantee for every future native build or dev server. Both dependencies remain in Expo's tooling installation, and the audit is not suppressed or reclassified.

Before public release: obtain supported upstream fixes (or separately review an explicit risk exception with compensating controls and ownership), rerun audit/full validation and inspect the actual signed artifact. Existing physical-device, privacy and signed-build checklist remains pending. Tests/build success alone cannot accept the vulnerabilities. A decision to allow development commits with documented findings needs explicit acceptance criteria and user authorization; none is inferred here.

### Commands and actual results in this follow-up

- `git status --short --branch`, `git rev-parse HEAD`, `git diff --stat`, `git diff -- apps/mobile`: master at 369d562b7bfeee014810d9236f1097bef2d2ce85; pre-existing Stage 11 changes preserved.
- `npm audit --json`: exit 1, 3 high / 5 low; fresh evidence in system TEMP/bites2go-investigation-audit.json. No dependency edits followed, so there is no post-install audit claim.
- `npm ls expo react-native react typescript zod deepmerge --all --json`: exit 0; tree recorded in TEMP/bites2go-investigation-tree.json. Lockfile affected versions match installed package manifests.
- `npm view <package>@58 version --json` for Expo/CLI/config/metro/prebuild/cache-provider, `npm view zod@3 version --json`, `npm view deepmerge version --json`, Expo/CLI `dist-tags`, and CLI/config `dependencies`: queries succeeded; versions/ranges reported above.
- `rg` of app imports and installed CLI/config code; `npx expo start --help`; bounded schema probe: reachability/control evidence above, no server started.
- `npm test`: exit 0, 96/96. `npm run typecheck`, `npm run lint`, `npm run format:check`: all exit 0.
- `npm run doctor`: exit 0, 20/20. `npx expo config --type public`: exit 0.
- `npx expo export --platform android --source-maps --output-dir "$env:TEMP/bites2go-investigation-android"`: exit 0. Same Hermes bundle basename as Stage 11: entry-d71e36f6e25981908dcf9510f40157af.hbc, 2.4 MB. Not a signed APK/device launch.
- SHA-256 comparison of all pre-existing tracked/unignored files: no changes before documentation; final comparison permits only appended investigation notes in this file, TASKS.md and MEMORY.md.
- Local PostgreSQL/credential scan were not repeated in this dependency-only follow-up; prior Stage 11 results remain recorded above and their inputs were preserved. Physical Android/emulator and live Supabase remain untested; cloud remains disabled.

No commit, push or dependency changes. Stop for review.
