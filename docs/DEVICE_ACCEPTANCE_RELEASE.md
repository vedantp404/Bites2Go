# Photo device-acceptance preview

Prepared locally from ac2af3d (includes R1 5bcb1ce and Phase1A 0933fa2). No cloud build, push or deploy authorized/performed. This is an internal acceptance candidate, not public release; dependency-audit blocker remains.

## Prepared settings and verification

Package com.bites2go and EAS project1e504316-51f2-4b43-ab54-ffcd26d92eba retained. User-facing version1.0.0; Android versionCode3 (latest known preview code2). EAS local version source makes this value explicit. Preview remains internal APK, now explicitly using remote credentials, preview environment, and the public URL https://bites2go-api.onrender.com in its profile. Excluded local .env.local is no longer the only URL configuration. No secret belongs in EXPO_PUBLIC variables or profile env.

186 mobile tests, types/lint/format, Doctor20/20, public Expo config and local Android export passed on the current working environment. Resolved config confirms package/code. Export contains the expected URL; scoped credential-pattern scan reports zero findings. This is not proof about an APK that has not yet been built. Review actual EAS environment names/settings and final artifact before distribution; never print secret values.

Historical preparation checkpoint a5961d8: all23 preexisting modified files were preserved, with package.json/lockfile excluded at that point. The final blocker resolution below now includes this reviewed pair unchanged. Tests used that installed dependency state. **Before cloud build, review these dependency edits and select a reproducible source archive containing the approved matching manifests/lockfile. Do not silently build all dirty work or assume a clean checkout recreates the tested environment.** Exclude unrelated planning/catalogue/evaluation edits. Re-run relevant checks if the selected dependency state differs.

## Signing and installation gate

Latest known FINISHED preview6447f478-40b6-4ff0-9b78-ed5cada2fbbf:1.0.0/code2, source1f8a11c, November11. No adb device connected. Installed version, installed certificate and EAS remote signing-certificate continuity are unverified. EAS fingerprint metadata is a source/runtime fingerprint, NOT an APK signing certificate.

Reuse the existing EAS remote Android keystore for com.bites2go. Never generate/rotate keys to overcome a mismatch. Before upgrade compare old installed APK certificate with new APK using Android SDK `apksigner verify --print-certs <apk>` and compare signer SHA-256 certificates. With an authorized connected phone obtain version via `adb shell dumpsys package com.bites2go`; `adb shell pm path com.bites2go` identifies the installed base.apk that can be pulled to a temporary operator folder for certificate inspection. Do not copy private diary files. Record new APK SHA-256, EAS build ID, exact source archive/commit and versionCode.

After package and certificate match and installed versionCode is below3, use `adb install -r <preview.apk>` or open the downloaded APK and choose Update. Never uninstall, clear storage or use downgrade flags. On signature/version errors STOP and investigate; preserve the app and SQLite data. If the installed code is3 or higher, allocate a higher code before building.

## Backend and build

The mobile fixes use existing recognition endpoints; no backend API/provider change is required to exercise them. R1 backend request tracing needs an approved deployment for end-to-end reference correlation if it is not deployed already. Current deployed revision is unknown. A read-only health probe timed out after15s in this run; availability must be checked again before device inference. This may reflect a cold start or connectivity; no root cause is established. Health availability alone would not prove inference. Coordinate any push carefully because Render may auto-deploy; no push is implied by approval to build.

After explicit cloud-build approval AND source/signing gates above, from apps/mobile:

```text
eas build --platform android --profile preview
```

Use the existing authenticated CLI; do not change credentials. No production deploy is part of this command. Save the resulting build ID and artifact provenance. Before distribution, verify manifest package/versionCode, certificate and an APK credential scan; the local export is not the APK. Install only over the matching existing app.

## Physical acceptance (pending)

1. Before update record diary dates/counts and one saved recipe; use any existing app export capability if available, without clearing data. After update verify those records and offline startup.
2. With explicit consent for one nonprivate food image, choose gallery then camera. Expect editable review, correct selected date/category and no save before confirmation. Record build ID, UTC time, backend revision and request reference where available.
3. Cancel while processing; immediately reopen. Dismiss picker; rapidly tap picker/retry. Expect no stale result/error, no unintended save and fresh state on reopen.
4. Disconnect network for an attempt: expect friendly error and retained image. Restore connectivity and retry. Verify review and exactly one save on explicit confirmation; restart offline and inspect diary totals/history. Use a mocked delayed service to test timeout without overloading production.
5. Check light/dark/system, readable/selectable error reference and 48dp controls. Correlate any failed request with server logs, never meal content/media. Report observed pass/fail for each step.

Recommendation: GO for local preparation; conditional GO for an approved internal build after dependency-source and existing-credential review; NO-GO for distribution until APK certificate/manifest/secrets gates pass. Physical acceptance and existing audit findings block any public-release claim.

References: [Expo versions](https://docs.expo.dev/build-reference/app-versions/), [EAS variables](https://docs.expo.dev/eas/environment-variables), [Android signing](https://developer.android.com/studio/publish/app-signing).

## Final blocker resolution — 2026-11-14

Dependency decision: include the preserved package.json/package-lock.json pair unchanged in this release. Their origin is preexisting uncommitted work (Git cannot establish author/command); intent is evidenced by exact alignment with Expo58.0.25 bundledNativeModules recommendations: crypto.8, dev-client.20, gradient.4, linking.17, router.31, splash.14, sqlite.17, status-bar.5, safe-area5.11.1. Expo range narrows from caret58.0.21 to tilde58.0.25. No React/RN/TS change. Lock review:9 added/18 removed/58 changed package records, primarily Expo/transitive patch/tooling/native optional package updates. Do not independently cherry-pick just the manifest.

Clean offline `npm ci --offline --no-audit --no-fund` succeeded in an isolated temporary directory:800 packages installed, lifecycle scripts enabled, no mutation of app node_modules. `expo install --check` reports up-to-date; npm ls --depth=0 passes. Existing186-test/type/lint/format/Doctor/export results were on this exact dependency pair, so committing it resolves the tested-vs-committed mismatch. No package contents were rewritten. Remaining21 preexisting dirty files are excluded; all23 original file contents remain checksum-identical. ESLint deprecation warning persists; audit blocker remains unresolved. This is reproducible dependency installation, not proof of a native cloud build or unlimited future registry availability.

Signing: successful authenticated read-only EAS query for com.bites2go returns ONE default build credential, keystore ID1b5ccdc1-ccac-4867-a026-3545d3a49f0f, updated2026-10-31T14:31:12.566Z. Public certificate SHA-256:
`FC4AE2E21063D5232889B4E7CDC1C39959B1D9C6089A81A52DD49B0F83ED05E5`
Remote preview credentials should select this default unchanged. Metadata predates the known November11 APKs, supporting continuity, but does not prove which certificate signed the installed/distributed APK. No keys/passwords or keystore data were fetched. Before install compare this fingerprint, the newly produced APK signer and the phone's existing base.apk signer; all must match. If not, STOP without uninstalling or changing credentials. Future credential changes invalidate this expectation.

Backend: two bounded health probes now returned200 in0.39s/0.80s; earlier15s timeout is no longer reproduced (cause unknown). Health self-reports commit1f8a11cf and version1.0.0; neither response includes X-Request-ID. Thus R1 tracing is not observed and reported revision predates R1. Existing endpoints suffice for mobile fixes. Approved R1 backend deployment is needed for request-ID acceptance; availability alone is not inference validation. No live AI or deploy performed.

Configuration remains1.0.0/code3, com.bites2go, same EAS project, preview/internal APK, local version source, remote existing credentials, explicit HTTPS backend URL. Device not connected; installed code/certificate remain human-device gates. Conditional GO for approved internal build from the focused committed source; NO-GO for unverified installation/public release. Distribution requires final APK certificate/package/version/secrets verification.

### Exact safe sequence (execute only after explicit approval)

Record RELEASE_SHA as the full hash of the focused dependency-resolution commit containing this section (`git log -1 --format=%H -- apps/mobile/package-lock.json`). Never use the dirty workspace as the upload source.

1. Review all commits from origin/master through RELEASE_SHA. Confirm approval covers push AND any Render automatic deployment it may trigger. If automatic deployment is not approved, hold the push; EAS can build from an approved local source without pushing.
2. `git fetch origin master`; `git merge-base --is-ancestor origin/master RELEASE_SHA`. STOP on nonzero; do not rebase/reset/force-push. With push approval: `git push origin RELEASE_SHA:refs/heads/master`. Verify `git ls-remote origin refs/heads/master` equals RELEASE_SHA. Do not bypass protection.
3. Create a new, previously nonexistent operator-chosen clean checkout: `git worktree add --detach C:/Users/Asus/Music/Bites2Go-preview-release RELEASE_SHA`. This leaves all dirty files in the original repository intact. Substitute a new path if it exists; never delete an existing checkout. Verify checkout HEAD and clean status.
4. In that checkout's apps/mobile, `npm ci`, `npx expo install --check`, `npm test`, `npm run typecheck`. If any gate fails, STOP. The committed preview profile supplies the backend URL; do not copy backend/.env, local credentials or unrelated dirty files.
5. After cloud-build approval, `eas build --platform android --profile preview --non-interactive`. Reuse existing remote credentials; do not generate replacements on failure. Save build ID/source hash/artifact hash and inspect APK signer, manifest and secret exposure before sharing.
6. Recheck health and coordinate separately approved backend deployment for tracing. Run the physical acceptance/upgrade steps above. No uninstall, data clear, migration or downgrade flags. If installed versionCode>=3, prepare a higher version and repeat review before building.

No push, production change or cloud build was executed by this resolution. Rollback: revert the focused dependency commit via a new commit; no data migration is involved.
