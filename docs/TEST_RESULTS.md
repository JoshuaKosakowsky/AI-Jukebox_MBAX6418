# Test results and evidence

## Local setup - 2026-10-15 America/Denver

Scope: repository scaffold only. No service calls, generated samples, or app
tests. Validation runs `python scripts/verify_repo.py` after staging files,
checks local Git configuration/hooks, and verifies the preserved prompt.
Verified 2026-10-15 19:15 MDT (America/Denver) by the Codex setup agent on Windows, Git 2.55.0.windows.5.
Baseline commit: `9d8ee0e2139cdbe623cfef8706b91e5bdcd75a65`; final handoff commit is available via git log.

| Setup check | Expected | Actual |
|---|---|---|
| Offline verifier | Required files, valid links, tracked safeguards, exact policy | PASS, 23 files |
| Starter prompt vs PDF | Identical original wording | PASS after whitespace normalization |
| Main pre-commit guard | Block after initial commit | PASS, blocked |
| Local-only pre-push guard | Block without explicit enablement | PASS, blocked |
| Main ref update/deletion | Block even with per-command enablement | PASS, both blocked |
| Working-branch hooks | Permit commit; permit branch ref under test enablement | PASS |
| Remote/config inspection | No remote; allowPush=false | PASS |

Hook tests invoke hooks directly without any push. An initial piped-input probe
was invalid because git hook run does not forward piped stdin; it was corrected
to --to-stdin and ref-specific checks reran successfully. Remote protection and
CI execution remain untested until publication. Secret-pattern checks are a
basic guard, not proof against every form of credential; inspect diffs manually.

## Application and release evidence (not run)

The complete checklist is AT-01-AT-19 in [acceptance.json](acceptance.json).
All app cases remain **not run**. No sample media or application exists yet.
Record one short entry per executed case: date/tester/environment/commit,
inputs/command, expected, actual, result, evidence paths and unchecked scope.
Consolidate repeated fixes; never turn an unrun case into a pass from test counts.

## Protocol verification - 2026-10-17 America/Denver

Full brief was read and mapped to 36 requirements, 11 tasks and 19 acceptance
cases. Offline readiness-gate regressions cover dropped/unmapped requirements,
dependency cycles, skipped/stub-only claims, missing results/evidence, both
reference formats, independent installation, absent media and wrong ZIP contents.
Commands: python scripts/check_readiness.py (36/11/19 coverage PASS), and\npython -m unittest discover -s tests -p "test_*.py" (18 passed). The explicit\nrelease command without actual evidence correctly returned NOT READY. This is protocol
verification, not jukebox/live/browser acceptance. The release check must report
NOT READY until actual independent evidence and sample assets exist.

## Design judgment and investigated limitation

Pending app work. Explain one important choice supported by observed tests and
one investigated limitation/failure with the lesson learned, then summarize
verified findings in README in the team's own words. Do not import A2's SVG or
RAG question-set requirements as mandatory A3 work.
