# Development rules

## Default Git workflow

- Work directly on `master` by default. Before editing, inspect Git status, branch, remote and relevant history; preserve existing user changes and never include them unintentionally.
- Implement only the explicitly requested stage or task. Do not start the next stage automatically.
- Run relevant tests and quality checks, update `TASKS.md` and `docs/MEMORY.md` at the end of each stage, and review the final diff before committing.
- Commit meaningful, completed changes with conventional commit messages. Push verified commits directly to `origin/master`, then verify the actual remote branch and commit hash with Git output.
- Do not create a feature branch or pull request unless the user explicitly requests one or repository policy requires it. Respect branch protection; never bypass it.
- Never force-push, rewrite shared history, or commit secrets, API keys, credentials, private data, generated build artifacts or unintended files.
- If tests fail, a merge conflict occurs, or authentication/permissions prevent pushing, stop and report the problem accurately. Preserve changes; never claim success without confirming command output.
- Do not create meaningless commits, backdate work or split changes merely to manipulate the GitHub contribution graph.


1. Read relevant project documentation and current Memory before each task.
2. Inspect existing code, callers, tests and Git status before modifying it.
3. Plan substantial changes and record material decisions before implementation.
4. Implement one clearly defined task at a time; never generate the entire application in one task.
5. Modify only related files. Preserve user changes; do not commit unrelated existing edits.
6. Reuse existing functionality. Keep components and services focused.
7. Separate presentation, deterministic business logic and persistence.
8. Follow Design tokens and accessibility requirements.
9. Add meaningful tests for important business logic, authorization and failure handling.
10. Run relevant tests, lint and type checks when configured. Investigate failures; never hide them or claim unexecuted checks passed.
11. Never expose secrets or privileged credentials in the app, logs, screenshots or Git.
12. Review diffs and sensitive-data risks before meaningful conventional commits.
13. Push completed work only when authorized, configured and safe; verify and report the result.
14. Update documentation after meaningful decisions and milestones. Do not silently change the agreed stack.
15. Explain significant technical decisions in plain language. Prefer simple, maintainable solutions.
16. Obtain approval before expensive, irreversible, destructive or externally consequential actions. Do not create services, subscriptions or remotes during Stage 1.
17. Keep nutrition calculations deterministic; missing values are not zero. AI proposes; the user confirms; structured data determines totals.
18. Preserve diary snapshots and explicit local dates. Do not rewrite historical nutrition or goals silently.

Loop: **READ → UNDERSTAND → PLAN → IMPLEMENT → TEST → REVIEW → FIX → COMMIT → PUSH → DOCUMENT**. Update docs before committing as needed; record actual commit/push outcomes afterward without manufacturing a follow-up commit solely to record its own hash.

Historical Stage 1 exception (superseded for current Git workflow): documentation and reversible foundation files only; no automatic commits, pushes, dependency installation, app initialization, or external resources. Stop and await approval before Stage 2. Later stages do not authorize spending or destructive actions merely by appearing in the roadmap.
