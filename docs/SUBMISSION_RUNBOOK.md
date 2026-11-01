# Submission Runbook — A3-10 (freeze + independent ZIP acceptance)

Companion to issue #10 and [docs/TESTING.md](TESTING.md). Execute ONLY when the
preconditions below are satisfied; the issue stays `blocked` and this runbook
is prep until then. Lead: @jovi1214; backup: @MSpanny. Never substitute a local
archive, waive a missing requirement, or modify candidate code after the
independent check.

## 1. Preconditions (all must be green first)

- [ ] **Every AT-case verified as `pass`** in the final evidence record with
      tester/inputs/expected/actual, required modes, variants, and evidence
      files that exist in the candidate tree (`docs/acceptance.json` cases are
      the authority). The release gate refuses any `blocked/skipped/not-run`.
      Today's known gaps: AT-04 (vocal live, #3), AT-08 (MP3/WAV Chatterbox
      live, #6), AT-11 (three approved samples, #7) — plus any case whose
      evidence is incomplete.
- [ ] **Three approved samples** in `assets/samples/manifest.json`: distinct
      ids/audio/cover; title, generated_at, generation_notes, assets present;
      `generated_with` = ACE-Step 1.5 XL Turbo + FLUX.2 klein 4B (vocal
      samples also carry Qwen3.6-35B-A3B lyrics + provenance). (Issue #7.)
- [ ] **Team records**: ≥2 distinct teammates, each with meaningful
      contribution_evidence and review_evidence; prepared_by and installed_by
      are listed members and **differ from each other**.
- [ ] Optional PRs merged (e.g. #26 references, #40 cover prompt) so the
      frozen main includes everything to be accepted.

## 2. Freeze the candidate

1. Merge the final PRs; note the **full 40-char** merged main SHA:
   `git rev-parse main` (remote) — every artifact must cite this exact SHA.
2. Download the exact GitHub source ZIP:
   `https://github.com/JoshuaKosakowsky/AI-Jukebox_MBAX6418/archive/<40-SHA>.zip`
3. Record identity — byte size, `shasum -a 256`, entry count
   (`unzip -Z1 | wc -l`), files (entries − dirs) vs
   `git ls-tree -r --name-only <sha> | wc -l` (must match), 0 `.git/` entries,
   0 bare `.env`, exactly 1 `.env.example`. The gate's archive comparison
   additionally verifies every tracked file byte-for-byte against the ZIP.

## 3. Run the release gate

```bash
python scripts/check_readiness.py --release \
  --evidence results/<final-record>.json --archive /tmp/<sha>.zip
# Expect: "PASS: recorded release gates and archive identity."
```

The gate verifies: record completeness (40-char tested_commit, prepared_by !=
installed_by, GitHub URL + exact archive_url, checks for EVERY case, team rows,
AT-16 tester == installer), manifest (3 distinct samples, required services),
and archive integrity (every tracked file byte-identical, no private files).

## 4. Independent installation + acceptance (AT-16/17/18)

- [ ] Pick a teammate with **zero commits on the candidate PRs** (per issue
      pool: mase7919 / prse4479 eligible; contributions must not certify
      themselves). They install from the downloaded GitHub ZIP only, per README
      (uv pinned, `python scripts/dev.py`), on their own machine.
- [ ] The installer verifies **all core features + the three approved samples**
      through the normal entrypoint (AT-11, AT-16, AT-17): playback with
      controls, cover/music/lyrics/vocal flows from the shipped samples, the
      four service roles configured, refresh/reload stability, safe error
      handling — recording actual inputs/results, screenshots, and the
      `public_access_checked_at` timestamp.
- [ ] The installer records the ZIP identity from their own download and
      confirms the shipped samples load from the source ZIP **without
      regeneration**.

## 5. Record + close out

1. Fill the evidence record (case checks, installed_by, team rows,
   public_access_checked_at, archive identity) and add it under `results/`;
   add the TEST_RESULTS section and handoff entry.
2. Update `CONTRIBUTIONS.md` with real review IDs
   (`gh api repos/.../pulls/N/reviews`); every teammate row needs
   contribution + review evidence links.
3. Open the record PR normally (branch `codex/a3-10-freeze`), require a
   current eligible approval, green CI, up-to-date main; merge.
4. Close #10 only after the full freeze record is merged and the ZIP identity
   matches; update labels and state on the issue.

## Reference

- Issue #10 (lead/backup, completion checks, review pool).
- `results/windows-zip-startup.json` (#20, early Windows rehearsal), `results/a3-10-rehearsal-prep.json` (gate mechanics on cb818ae).
- `scripts/check_readiness.py` (gate source), `docs/acceptance.json` (case registry), `docs/TESTING.md` (evidence conventions).
