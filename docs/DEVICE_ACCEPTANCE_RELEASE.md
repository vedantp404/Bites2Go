# Photo device-acceptance preview

Prepared locally from ac2af3d (includes R1 5bcb1ce and Phase1A 0933fa2). No cloud build, push or deploy authorized/performed. This is an internal acceptance candidate, not public release; dependency-audit blocker remains.

## Prepared settings and verification

Package com.bites2go and EAS project1e504316-51f2-4b43-ab54-ffcd26d92eba retained. User-facing version1.0.0; Android versionCode3 (latest known preview code2). EAS local version source makes this value explicit. Preview remains internal APK, now explicitly using remote credentials, preview environment, and the public URL https://bites2go-api.onrender.com in its profile. Excluded local .env.local is no longer the only URL configuration. No secret belongs in EXPO_PUBLIC variables or profile env.

186 mobile tests, types/lint/format, Doctor20/20, public Expo config and local Android export passed on the current working environment. Resolved config confirms package/code. Export contains the expected URL; scoped credential-pattern scan reports zero findings. This is not proof about an APK that has not yet been built. Review actual EAS environment names/settings and final artifact before distribution; never print secret values.

All23 preexisting modified files are preserved. In particular package.json/lockfile remain user edits and are NOT included in the preparation commit. Tests used that installed dependency state. **Before cloud build, review these dependency edits and select a reproducible source archive containing the approved matching manifests/lockfile. Do not silently build all dirty work or assume a clean checkout recreates the tested environment.** Exclude unrelated planning/catalogue/evaluation edits. Re-run relevant checks if the selected dependency state differs.

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
