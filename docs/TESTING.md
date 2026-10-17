# Verification and submission readiness

## Fast checks (offline)

```powershell
python scripts/verify_repo.py
python scripts/check_readiness.py
python -m unittest discover -s tests -p 'test_*.py'
```

The first checks tracked files/safeguards, the second checks R01-R36 coverage,
and the third tests the gate itself. **None proves jukebox functionality.** CI
job `test` runs these. Keep it stable when adding the chosen app's offline suite.
Check that new tests are actually collected by the default command; missing
markers previously hid A2 tests. Verify media fixtures decode/render, not just
that a path or header exists. New app tests must not call class services in CI.

Match checks to changes: docs -> diff/links; logic -> focused behavior/failure
tests; wiring -> contract/smoke tests; features -> real normal-launch browser
and class-service cases. Use a locked runtime/dependency set and verify supported
Windows behavior. Repeat passing tests only for relevant changes or open risks.

## Deliberate service contract probes

The four live requests are frozen in [SERVICE_CONTRACTS.md](SERVICE_CONTRACTS.md)
and [service-probes.json](../contracts/service-probes.json). Reuse them when
an assigned task needs a live compatibility check; generation is opt-in and
bounded, never triggered by offline checks, CI or app startup. Record new
expected/actual results and schema changes together. Do not treat schema-only
reference upload support or decoded smoke media as completed browser features.

## Acceptance evidence

[acceptance.json](acceptance.json) is the requirement/task/case index;
[ISSUES.md](ISSUES.md) contains scope and closure criteria. AT-01-AT-19 cover the
whole brief, including both reference formats, playback transitions, samples,
documentation, teamwork and the independent ZIP. Missing/blocked/skipped is not
pass. A models-list request is not a successful feature request. A fake provider
is only offline evidence, even if its screenshots look convincing.

As each flow works, record date, tester, environment, commit, exact safe inputs,
expected/actual results and evidence in TEST_RESULTS.md and results/. Listen to
the output, inspect new cover/track pairing and observe speech/music without
overlap. Include progress/error/recovery and stage timings before diagnosing
slowness. Keep course keys, uploads, voice references and unsafe logs out of Git.

Reconcile the full requirement list at each PLAN milestone. Rehearse independent
installation after the three core features first work; fix the gaps then. Any
local pre-publication rehearsal is useful but cannot satisfy the GitHub ZIP rule.

## Final candidate and ZIP

1. Commit reviewed code, assets, dependencies, README and earlier evidence to main.
   Select the full candidate SHA. No missing mandatory requirements may be waived.
2. Download GitHub's source ZIP for that SHA, not a local build/working-tree ZIP.
   A different teammate installs it using only README and class credentials and
   exercises all required flows, references, controls and three actual samples.
3. Keep the final verification record outside the frozen candidate (an external
   path or ignored results/raw/). This avoids changing the tested commit merely
   to record its own SHA. Generate a blank record, then fill only observed results:

```powershell
python scripts/check_readiness.py --template results/raw/release-record.json
# Fill the record after independent checks. Do not change not-run to pass by assumption.
python scripts/check_readiness.py --release --evidence results/raw/release-record.json --archive C:/path/to/GitHub-source.zip
```

The record identifies the full tested SHA, GitHub repo/archive URLs, archive
SHA-256, preparer, different installer, environment, normal launch command, all teammates'
contribution/review evidence, and AT cases with required modes/variants and
evidence paths already committed in the candidate. Live/browser labels must
describe what actually ran. Share the final record with the team; after publication
authorization it may be attached to the release/acceptance issue without a new
code commit. Do not put secrets in the record or count it as an app feature test.

The release check refuses incomplete evidence, missing sample media/provenance,
a candidate not on main, wrong ZIP inventory/bytes or prohibited archive paths.
It validates the record and archive identity, not the truth of human observations,
audio/image quality or ongoing GitHub access. Teammate review is still essential.
Keep the public repo accessible through grading. Submit its URL, that SHA and
that exact GitHub ZIP per team on Canvas; the checker does not submit anything.

Code, assets or dependency changes after testing create a new candidate: rerun
affected checks and independent ZIP installation. Documentation fixes that alter
the candidate also change its SHA; recheck the final ZIP rather than submitting
an archive that no longer matches the recorded version.
