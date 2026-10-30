# Agent entrypoint

Read [RULES.md](RULES.md), [docs/MEMORY.md](docs/MEMORY.md), and [TASKS.md](TASKS.md) before working. Read the relevant requirements, architecture, design, testing and security documents before implementing a task.

## Default Git workflow

- Work directly on `master` by default. Before editing, inspect Git status, branch, remote and relevant history; preserve existing user changes and never include them unintentionally.
- Implement only the explicitly requested stage or task. Do not start the next stage automatically.
- Run relevant tests and quality checks, update `TASKS.md` and `docs/MEMORY.md` at the end of each stage, and review the final diff before committing.
- Commit meaningful, completed changes with conventional commit messages. Push verified commits directly to `origin/master`, then verify the actual remote branch and commit hash with Git output.
- Do not create a feature branch or pull request unless the user explicitly requests one or repository policy requires it. Respect branch protection; never bypass it.
- Never force-push, rewrite shared history, or commit secrets, API keys, credentials, private data, generated build artifacts or unintended files.
- If tests fail, a merge conflict occurs, or authentication/permissions prevent pushing, stop and report the problem accurately. Preserve changes; never claim success without confirming command output.
- Do not create meaningless commits, backdate work or split changes merely to manipulate the GitHub contribution graph.

The mobile app lives in `apps/mobile/`. Stage 4 Android verification was reported by the user. Stage 5 local diary persistence is authorized by the current user request. Stop before Stage 6; physical Stage 5 restart verification remains pending. See Memory for current evidence and limitations.
