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
  test rather than shipped or abandoned. Worth revisiting at review time
  whether that parked state resolved (new evidence found) or is still
  open as v1.3.0 planning starts.
- The CI-trigger gap (workflow only fires on `main`, not on the new
  `v<version>`/`rc/v<version>` branches this SOP introduces) was
  discovered during this pass, not anticipated when the branching model
  was written. Worth recording how it got resolved, once it is.

---
Status: **STUB — not a completed review**
Prepared by: Claude
Date: 2026-07-02
