# Git and GitHub workflow

## Observed Stage 1 state

Git 2.55.0.windows.3 is installed. Workspace is the repository root; current unborn branch is `master`; no HEAD commit exists. Initial working tree had no project files or user changes. No remotes are configured. Git author name and email are configured; their association with a GitHub account is unverified. GitHub CLI is unavailable on PATH, so `gh auth status` could not execute. Browser, connector or Git credential authentication was not tested. A local `.git` directory is not evidence of a GitHub repository.

## Safe connection plan (not executed)

1. Review Stage 1 files and approve the first meaningful documentation commit. Verify configured email belongs to the intended GitHub account or choose its eligible no-reply address. Do not change global identity automatically.
2. Existing Git needs no initialization. Optionally rename the unborn default branch to `main` after agreement; otherwise retain `master` and make the GitHub default branch match.
3. When authorized, create or select a GitHub repository with explicit owner, name and visibility. For an empty remote, avoid separately generating a README/license that would create divergent history. Choose a code license intentionally.
4. Authenticate with Git Credential Manager/SSH or install and sign in to `gh` if desired. Never paste a token into a remote URL, document or chat.
5. Once the actual repository URL is known and authorized, add it as `origin`; inspect `git remote -v`. No invented URL is supplied here.
6. Inspect remote refs with `git ls-remote origin`. If remote history already exists, fetch and review before choosing a reconciliation strategy; never overwrite it or force-push.
7. Explicitly stage reviewed project files, review `git diff --cached` and its summary, then commit, for example `docs: define nutrition tracker foundation`. Push with upstream only after verifying branch/remote/auth. Verify remote branch hash matches local HEAD. Report actual hash and branch.

No commands above have changed the repository in Stage 1.

## Ongoing task workflow

Inspect status → read relevant docs/code → implement a bounded task → run applicable tests/lint/type checks → review for secrets and unrelated edits → update docs → review diff → stage explicit related files → meaningful commit → safe authorized push → verify remote result → report evidence and update Memory. Missing tools/auth/remotes leave changes local; report the exact blocker. Never commit pre-existing user changes automatically. Never force-push, backdate work, rewrite shared history or manufacture contributions.

Use the default branch for initial setup; larger work uses `codex/dashboard`, `codex/food-database` or similarly descriptive branches, with PRs explaining behavior and validation. A branch per trivial edit is unnecessary. Conventional prefixes: `docs`, `chore`, `feat`, `test`, `fix`, `refactor`, `security`. Keep independent changes separate, but do not split mechanically to increase contribution counts.

GitHub contribution credit requires eligible author email, repository and branch conditions; feature-branch commits generally contribute when merged into the default branch. See [GitHub's contribution criteria](https://docs.github.com/en/account-and-profile/reference/profile-contributions-reference). Public visibility alone does not guarantee attribution.

## Future CI

Stage 2 establishes mobile lint/type scripts; add a small GitHub Actions workflow once commands and GitHub repository exist. Stage 4 adds backend pytest/lint; Stage 5 adds disposable database/RLS integration checks. Stage 11/12 add appropriate build/security checks. Use pinned supported runtimes, lockfiles, least-privilege workflow permissions and no paid EAS builds triggered by every untrusted PR. No CI workflow exists in Stage 1.
