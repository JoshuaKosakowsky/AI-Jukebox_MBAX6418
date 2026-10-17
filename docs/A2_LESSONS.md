# Assignment 2 audit -> Assignment 3 changes

Read-only audit on 2026-10-17 America/Denver. GitHub main snapshot:
`dfc0fc41498bf0ae3ab327e1b8d15384b397ce3c`. Reviewed both full assignment briefs,
20 PRs, issue scopes, late reviews, README, normal UI wiring and final follow-ups.
No A2 code or remote settings changed; its app was not re-run in this audit.

## Findings with evidence

- **Required details were lost in summary issues.** The A2 brief required 5-10
  course questions, two visual questions including the meme, an unanswerable
  question, paired answer/source/latency evaluation, an embedded SVG, and specific
  answer/quiz screenshots. Issue #8 reduced evaluation to one generic design
  comparison. The synthetic BM25 comparison did not cover that complete requirement.
  [Issue #8](https://github.com/JoshuaKosakowsky/Course-Assistant_MBAX6418/issues/8),
  [PR #20](https://github.com/JoshuaKosakowsky/Course-Assistant_MBAX6418/pull/20),
  [late evaluation PR #31](https://github.com/JoshuaKosakowsky/Course-Assistant_MBAX6418/pull/31).
- **Backend success did not prove normal startup.** The merged final README and
  approved incremental UI PR explicitly retained a placeholder Q&A tab and an
  unwired quiz provider. Late PR #30 connected them and added the SVG/screenshots.
  [PR #19](https://github.com/JoshuaKosakowsky/Course-Assistant_MBAX6418/pull/19),
  [PR #27](https://github.com/JoshuaKosakowsky/Course-Assistant_MBAX6418/pull/27),
  [PR #30](https://github.com/JoshuaKosakowsky/Course-Assistant_MBAX6418/pull/30).
- **Green checks could miss important boundaries.** PR #19 review found smoke
  tests deselected by the default marker command and image fixtures that did not
  decode. Live PR #23 corrected JSON mode; PR #25 corrected the actual multimodal
  embedding payload. Mocked success was not sufficient service/media evidence.
  [PR #23](https://github.com/JoshuaKosakowsky/Course-Assistant_MBAX6418/pull/23),
  [PR #25](https://github.com/JoshuaKosakowsky/Course-Assistant_MBAX6418/pull/25).
- **Review helped, but delivery remained a separate gate.** Data-loss, provenance,
  identity, UI ordering and rendering fixes were valuable. The error was treating
  merged components, test counts or an honest limitations list as an assignment
  completion signal. Preserve reviews, and explicitly verify required user flows.

## Final-state caveat

At snapshot, PR #30 (UI integration), #31 (evaluation workflow), and #29 (removal
fix) were open; #7/#8/#9 also remained open. PR #30/31 describe live course-material
acceptance, human evaluation and independent installation as still outstanding.
These findings are bounded to that snapshot; later fixes may change A2's outcome.
The local A2 checkout was older and reported a missing Git object during log
traversal, so it was not used to assert final correctness or repaired by this audit.

## Implemented response in A3

1. Full-brief R01-R36 coverage, each mapped to an issue brief and acceptance case.
2. Actual normal-launch browser/service checks for core features; no fixture-only pass.
3. Concrete tasks for integration, samples, failure recovery and independent ZIP use.
4. Continuous evidence plus a rehearsal as soon as core flows first work.
5. A frozen-candidate release check validates recorded cases, sample presence and
   exact ZIP contents. Structure-only CI stays explicitly separate from readiness.
6. Preserve focused commits/reviews and small in-task fixes. No A2-specific SVG or
   RAG experiment is imported as an A3 requirement; optional polish waits for core work.
