# Project memory

Updated: 2026-10-30, Asia/Calcutta. Stage 1 documentation completed; awaiting user review and explicit approval before Stage 2.

## Verified workspace inspection

- Root: `C:\Users\Asus\OneDrive\Documents\ChatGPT\bites2go`.
- Full initial workspace listing contained only `.git` and its metadata/sample hooks. No source, dependencies, configuration, documentation or pre-existing uncommitted project files. Root is already the Git top-level; no nested repository initialized.
- Initial `git status --short --branch`: no commits yet on `master`; `git log` reports unborn branch. `git remote -v`: no output/remotes. Git 2.55.0.windows.3.
- Git author name/email configuration is accessible and nonempty; account ownership and GitHub attribution were not verified. Personal email is intentionally not copied into this public-facing document.
- `gh` missing on PATH; attempted `gh auth status` could not execute. No other GitHub authentication test or remote access was performed. No remote added, branch renamed, commit made or push attempted.
- Node v22.23.2, npm 10.9.8, Python 3.13.13 and Java 21.0.8 are executable. Java printed shared archive warnings and a VM build-version difference; no Android/Gradle compatibility check exists yet.
- `adb`, `emulator`, `eas`, `supabase`, `docker` and `gh` unavailable on PATH. This does not establish whether a GUI app or tool exists elsewhere. `JAVA_HOME` points to JDK 21; `ANDROID_HOME` and `ANDROID_SDK_ROOT` were unset. No connected-device or emulator test performed.
- Parent directories checked for AGENTS.md at ChatGPT, Documents and user home contained none. Root AGENTS.md was created as a short entrypoint to RULES and status.

## Completed milestone and current task

Created the seven required docs (PRD, Architecture, Design, Test Plan, Security, Decisions, Memory), root RULES/TASKS/README/.env.example/.gitignore, plus AGENTS.md and dedicated Research/GitHub Workflow docs. Researched official food-data rights, AI capabilities/pricing/privacy, Supabase, Expo/EAS and preview hosting. No application code or datasets were imported.

Important decisions: manual-first; source-based deterministic calculations; immutable food versions and diary snapshots; effective-dated goals; explicit local dates; server authorization and RLS; no photo retention by default; AI provider undecided pending evaluation. Read Decisions for confirmed versus provisional status.

## Known issues and unresolved choices

IFCT electronic product rights require written permission; Indian prepared-food coverage is not yet validated. SDK transition and local Android runtime compatibility need verification. No remote or CLI authentication, app license, service accounts, backend packages, deployment or test runners configured. Supabase write-function privilege design requires integration proof before private logging. Monitoring price retrieval failed; no monitoring price is claimed. Full offline sync is deferred, not promised.

## Latest validation

Stage 1 validation passed: 15 required/foundation files present, 17 local Markdown links resolve, Markdown code fences balanced, no trailing whitespace, all environment placeholders empty, and 19 Git ignore probes behave as expected (12 secret/cache/build/data paths excluded; seven source/example/migration/test/lockfile paths retained). Requirements, roadmap dependencies, MVP boundaries and provisional decisions were reviewed for consistency. `git diff --check` returned success but has no tracked diff on this unborn repository; the separate Python checks inspected every new file. Final status confirms only the new foundation files are untracked and no remotes exist. No application tests, lint/type checks, API inference or Android build/run can be reported; no application exists.

Last meaningful commit: none (unborn `master`). Stage 1 changes remain untracked/uncommitted; nothing pushed.

## Exact next step

Wait for the user's approval of Stage 1. Then execute only the Stage 2 minimal Expo task in TASKS, first rechecking SDK/device support and Git state. No credentials or paid resources are required to review this foundation. User should later choose Android test route, confirm GitHub account/email and repository visibility/URL, and choose license before public connection/publication. Do not start Stage 2 automatically.
