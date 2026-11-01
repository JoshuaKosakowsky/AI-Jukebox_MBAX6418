# Submission Runbook — A3-10 (freeze + independent ZIP acceptance)

Companion to issue #10 and [docs/TESTING.md](TESTING.md). Two phases: a
**preflight** that is expected to fail (`NOT READY`) while acceptance work is
open, and the **final gate** that must PASS after the independent installation
and a completed external record. Lead: @jovi1214; backup: @MSpanny. Never
substitute a local archive for the GitHub source ZIP, waive a missing
requirement, or modify candidate code after the independent check.

## Phase 0 — Feature blocks (must be merged and green before a real freeze)

- Merge the feature/reference PRs whose AT-cases are being accepted BEFORE
  freezing; the frozen main must contain everything the record claims. The
  reference-voice PR (#26) is REQUIRED for AT-08, not optional; the cover
  prompt fix (#40) is required for the cover-quality ask. The final record
  needs every case as `pass` with tester/inputs/expected/actual, required
  modes, variants, and evidence files that exist in the candidate tree
  (`docs/acceptance.json` is the case authority) — the gate refuses
  `blocked/skipped/not-run`.
- Three approved samples in `assets/samples/manifest.json`: distinct
  ids/audio/cover; title, generated_at, generation_notes, present assets;
  `generated_with` = ACE-Step 1.5 XL Turbo + FLUX.2 klein 4B (vocal samples
  also carry Qwen3.6-35B-A3B lyrics + provenance). (Issue #7.)

## Phase 1 — Pin, download, identity-check (PREFLIGHT; expect NOT READY)

```bash
SHA=$(git ls-remote origin main | cut -f1)   # full 40-char merged main SHA
curl -sL -o /tmp/candidate.zip \
  "https://github.com/JoshuaKosakowsky/AI-Jukebox_MBAX6418/archive/$SHA.zip"
ls -l /tmp/candidate.zip                      # byte size
shasum -a 256 /tmp/candidate.zip              # sha256
unzip -Z1 /tmp/candidate.zip | wc -l          # total entries
unzip -Z1 /tmp/candidate.zip | grep -c '/$'   # directory entries
git ls-tree -r --name-only main | wc -l       # tracked files (must equal: total − dirs)
unzip -Z1 /tmp/candidate.zip | grep -E '(^|/)\.git/'   # expect 0
unzip -Z1 /tmp/candidate.zip | grep -E '(^|/)\.env$'   # expect 0 (one .env.example is expected)
```

Generate the blank evidence record **outside the candidate** (Phase 3
explains the frozen-candidate rule):

```bash
python scripts/check_readiness.py --template /tmp/freeze-record.json
# "Blank evidence template written; every acceptance case remains not-run."
```

Run the preflight gate (NOT READY is the expected, correct outcome here — it
enumerates the open blockers):

```bash
python scripts/check_readiness.py --release \
  --evidence /tmp/freeze-record.json --archive /tmp/candidate.zip   # expect exit 1
```

## Phase 2 — Independent installation + acceptance (AT-16/17/18)

- Pick a teammate with **zero commits on the candidate PRs** (pool:
  mase7919 / prse4479 eligible; a contributor must not certify their own
  work). They install from the exact downloaded ZIP only, per README
  (`python scripts/dev.py`), on their own machine.
- The installer verifies all core features + the three approved samples
  through the normal entrypoint (AT-11/16/17): playback with controls,
  cover/music/lyrics/vocal flows from the shipped samples, four service roles
  configured, refresh/reload stability, safe error handling — recording
  actual inputs/results, screenshots, and the `public_access_checked_at`
  timestamp. They re-record the ZIP identity from their own download and
  confirm the samples load from the source ZIP **without regeneration**.

## Phase 3 — Complete the external record, then require PASS

1. Fill `/tmp/freeze-record.json` (or wherever it lives outside the
   candidate): `tested_commit` (exact SHA), `prepared_by` ≠ `installed_by`
   (the independent installer), `team` rows (≥2 distinct, each with
   contribution_evidence and review_evidence), every case's `checks` entry
   (tester/inputs/expected/actual, modes, variants, evidence paths that exist
   in the candidate), `public_access_checked_at`, archive identity.
2. Final gate — expect PASS:

   ```bash
   python scripts/check_readiness.py --release \
     --evidence /tmp/freeze-record.json --archive /tmp/candidate.zip
   # "PASS: recorded release gates and archive identity."
   ```

3. **Frozen-candidate rule** (docs/TESTING.md "Final candidate and ZIP"):
   keep the final verification record outside the frozen candidate so the
   tested SHA/ZIP stays the tested candidate. If the record is published in
   the repo, publish it as an **evidence-only commit that still cites the
   ORIGINAL tested SHA/ZIP** — a later main ZIP or tree is a different,
   untested candidate. Code/asset/dependency changes after testing create a
   NEW candidate: re-select its SHA and re-run the whole check.

## Phase 4 — Record + close out

1. Add the TEST_RESULTS section and handoff entry, and `CONTRIBUTIONS.md`
   rows with real review IDs (`gh api repos/.../pulls/N/reviews`).
2. Open the record PR normally (branch `codex/a3-10-freeze`); require a
   current eligible approval, green CI, up-to-date main; merge.
3. Close #10 only after the full freeze record is merged and the ZIP identity
   matches; update labels and state on the issue.

## Reference

- Issue #10 (lead/backup, completion checks, review pool); docs/TESTING.md
  "Final candidate and ZIP" (frozen-candidate rule).
- `results/windows-zip-startup.json` (#20, early Windows rehearsal);
  `results/a3-10-rehearsal-prep.json` (preflight mechanics + exact gate
  output on cb818ae).
- `scripts/check_readiness.py` (gate source incl. `--template`),
  `docs/acceptance.json` (case registry).
