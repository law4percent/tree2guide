# v1.2.0 Review

**Per `RELEASE_NOTE.md`, this artifact is written after a release ships —
"what surprised us, what escaped testing, what governance worked."
v1.2.0 has not shipped: no TestPyPI upload, no PyPI upload, no git tag,
no GitHub Release. This file is a placeholder created because it was
requested as part of this Release Verification Mode pass. It is not a
completed review and should not be read as one.**

---

## To be completed after release ships

- What surprised us
- What bugs escaped testing
- What governance worked
- What should change for v1.3.0

## Notes carried forward from development, worth revisiting at review time

- Two unplanned, Confirmed defects were found and fixed during release-
  evidence generation (item 8), not during original feature development:
  a stale non-editable install invalidating earlier test runs, and 15
  dead `_STACK_SIGNALS` path patterns dating back to v1.1.0. Worth asking
  at review time: would writing CLI-level tests earlier in development —
  rather than at the release-evidence stage — have caught either sooner?
- Items 4/5 (monorepo detection) were paused via a documented pressure
  test rather than shipped or abandoned. Real-world testing against two
  structurally different repos (Repo A/CakePHP, Repo B/Laravel+Next.js —
  see `PRODUCTION_NOTES.md`, business names withheld) during this
  release-verification pass resolved the parked reopen condition with
  strong evidence — a stable invariant
  (`≥3 of {Controller,Model,View,webroot}`) held with zero false
  positives on real decoys. Correctly still not implemented in v1.2.0
  (Release Verification Mode's no-new-features scope), targeted for
  v1.3.0. Worth checking at review time whether that v1.3.0 work
  actually happened, and whether the topology/tooling separation held up
  once implemented.
- A third finding came directly out of testing against real data rather
  than synthetic fixtures: `config/app.php` is shared between CakePHP
  and Laravel, causing a spurious secondary "CakePHP" label on Laravel
  projects (see `PRODUCTION_NOTES.md`'s "Known heuristic limitation").
  Deferred to v1.3.0, not a release blocker.
- A fourth finding, this one actually fixed in v1.2.0 rather than
  deferred: real-world testing against a personal project with 8,170
  symlinks (venv + `node_modules/.bin`) found that scan progress counted
  symlinks while the final summary and `--llm` output didn't — the two
  numbers visibly disagreed. Root cause and fix are in
  `PRODUCTION_NOTES.md`. This is the strongest argument in this release
  for testing against real repos, not just synthetic fixtures: no
  unit test built with `tempfile`-style fixtures happened to include a
  symlink during an active progress-tracked scan, so this shipped
  invisibly until it hit real data.
- Five real repos were tested total this pass (two business-owned,
  generic-labeled; three personal, named directly), and every finding
  came from repos the developer happened to have on hand — worth asking
  at review time whether a broader or more systematic real-world sample
  (beyond what one developer's own projects and access can offer) would
  surface issues faster than opportunistic testing, both for
  `_STACK_SIGNALS` ambiguities and for edge cases like the symlink bug.
- The CI-trigger gap (workflow only fires on `main`, not on the new
  `v<version>`/`rc/v<version>` branches this SOP introduces) was
  discovered during this pass, not anticipated when the branching model
  was written. Worth recording how it got resolved, once it is.

---
Status: **✅ Complete**
Prepared by: Claude
Date: 2026-07-02
Reviewed by: Lawrence Roble