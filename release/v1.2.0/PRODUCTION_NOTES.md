# v1.2.0 Production Notes

Release engineer's notebook — internal record, not user-facing
documentation.

---

## Known Limitations

- `_matches_pattern` supports only leading/trailing `*` wildcards, not
  full glob syntax — pre-existing, unchanged this release.
- Path-aware `_STACK_SIGNALS` matching (new this release) only covers
  `_STACK_SIGNALS`. `_NOTABLE_FLAGS` matching was **not** changed and
  still only compares bare names — if a future notable-flag pattern is
  added containing `/`, it will silently never match, the same way the
  15 dead `_STACK_SIGNALS` patterns did before this release's fix. Worth
  checking `_NOTABLE_FLAGS` for slash patterns before adding new ones.
- Scan-progress cadence is fixed at ~1 second, not configurable — no
  `--progress-interval` flag exists.
- `--no-progress` is all-or-nothing — it suppresses both the periodic
  progress lines and the final completion summary; there is no way to
  keep the summary while suppressing only the periodic lines.
- `on_progress` callback signature is fixed at `(files, dirs)` — not
  generalized into a broader event/observer system (deliberately
  deferred, see below).

## Things Intentionally Deferred

- **Monorepo detection** (planned v1.2.0 items 4/5) — paused
  mid-development, not shipped in any form. Pressure testing found the
  original `monorepo_signals` field proposal conflated repository
  topology (multi-app/workspace structure) with build/tooling ecosystem
  (Nx/Turbo/Lerna, already covered by `_STACK_SIGNALS`). Held open
  pending either a framework-independent semantic contract or additional
  real-world examples revealing a stable invariant. No `MONOREPO SIGNALS`
  section exists in `--llm` output.
- **`Console` as a CakePHP stack signal** — explicitly rejected (not
  merely deferred) during item 3's pressure test; insufficient evidence
  of real-world value versus the ambiguity risk.
- **Generalizing `on_progress` into a broader `events`/`observer` hook**
  — one motivating use case (CLI progress) doesn't yet justify the
  abstraction, per this project's Phase 3 discipline (extract rules only
  after repetition).

## Risk Areas

- **Python 3.9 compatibility is unverified on a real interpreter.** The
  `from __future__ import annotations` fix in `cli.py` was reasoned about
  and tested only on Python 3.12.7 locally (no 3.9 interpreter available
  in this environment). No CI run exists yet for this branch's commits —
  see the CI Gap documented in `RELEASE_CHECKLIST.md`. This is the single
  highest-risk item blocking confident release.
- **`_detect_stack()`'s signature changed** (now takes `all_names,
  all_paths` instead of just `all_names`). It's private/underscore-
  prefixed, so no public API contract is broken, but any external code
  that imported it directly (unlikely, but technically possible) would
  break.
- **Process risk, not a code risk:** this session's earlier "tests pass"
  self-checks for several features were initially invalid — `pytest` was
  resolving to a stale, non-editable, version-1.1.0 site-packages install
  rather than local source, until caught and fixed via
  `pip install -e ".[dev]"`. Every test has since been re-run against the
  correct source and passes (99/99). Noted here so a future session
  verifies `python -c "import tree2guide; print(tree2guide.__file__)"`
  resolves into `src/` before trusting any test run.
- Number-formatting test creates 1,500 real files in a temp directory —
  not a runtime risk, but slightly slower than the rest of the suite;
  noted in case it's ever flagged as a CI performance outlier.

## Rollback Notes

- **If PyPI upload fails partway:** nothing is live yet at that point
  (PyPI rejects incomplete/duplicate uploads) — safe to fix and re-run
  `twine upload`.
- **If the wheel is discovered broken after upload:** version numbers are
  permanent on PyPI and cannot be deleted or overwritten (per
  `RELEASE_NOTE.md`'s Version Immutability Rule) — the fix is a new
  `v1.2.1` patch release, not a re-upload of `1.2.0`.
- **If docs are wrong on the PyPI project page:** README rendering is
  fixed at upload time; corrections require a new version's README. The
  GitHub Pages docs site (served from `docs/` on `main`) can be corrected
  independently of PyPI, since it doesn't share PyPI's immutability
  constraint.
- **If GitHub Pages shows wrong content post-merge:** fixable directly by
  pushing a correction to `main`.

## Things to Verify After PyPI Publish

- `pip install tree2guide` in a fresh environment resolves to `1.2.0`
- `tree2guide --version` → `tree2guide 1.2.0`
- README renders correctly on the real PyPI project page (structurally
  confirmed via `twine check` locally; the actual rendered page should
  still be eyeballed)
- All README links resolve (absolute GitHub URLs confirmed present, not
  yet click-tested post-publish)
- `pypi.org/project/tree2guide/1.2.0/` metadata matches `pyproject.toml`

## Python Versions Tested

- **3.12.7** — Confirmed: all 99 tests pass, fresh-venv wheel install
  verified, all new CLI behavior smoke-tested.
- **3.9, 3.10, 3.11** — Not independently tested this cycle. CI's matrix
  covers all four, but CI has not run against this branch's commits (see
  CI Gap in `RELEASE_CHECKLIST.md`). This is a real gap, not an
  assumption of correctness.

## CI Expectations

`.github/workflows/ci.yml` runs `pytest --tb=short` across Python
3.9–3.12, triggered only on push/PR to `main`. Must go green on all four
versions before publishing, per the SOP's own Phase 5 gate — **not yet
satisfied for this release.**

## Windows Notes

- The existing `--stdout` raw-UTF-8-bytes fix (`sys.stdout.buffer.write`)
  is untouched this release — still in place, still necessary.
- New progress/telemetry output uses plain `print(..., file=sys.stderr)`
  with no carriage-return (`\r`) tricks, specifically to avoid the
  Windows-terminal-differences risk (cmd/PowerShell/Windows Terminal)
  called out in the original v1.2.0 plan doc's decision points — a
  deliberate design choice, not an oversight.
- Not independently verified on real Windows hardware this cycle — no
  Windows environment was available during development.

## Known Assumptions

- Dev setup assumes `pip install -e ".[dev]"`. A non-editable install
  (`pip install .`) causes `pytest` to silently test a stale copy instead
  of local source — exactly what happened earlier in this session.
- Path-aware signal matching uses "exact match at root, or suffix match
  at any depth" semantics — validated against the single motivating
  CakePHP case (`bin/cake` at root, and nested under a monorepo app dir),
  not against a broad sample of real-world repos for every affected
  framework (Laravel, Symfony, Rails, Java/Kotlin, Flutter).

---
Prepared by: Claude
Date: 2026-07-02
