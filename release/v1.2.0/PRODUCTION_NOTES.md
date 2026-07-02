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
  **Update from real-world testing during this release-verification
  pass:** the reopen condition is now satisfied with strong evidence,
  from two structurally different real-world repos volunteered for
  testing (generic labels used here — internal business names withheld):
  **Repo A**, a CakePHP monorepo (~217k files), and **Repo B**, a
  Laravel + Next.js monorepo managed with Turborepo (~61k files). On
  Repo A, the plan doc's original
  `≥3 of {Controller,Model,View,webroot}` heuristic correctly identified
  all 5 real app instances with zero false positives among 4 plausible
  name-alike decoy directories (one had only `webroot`, one was the
  vendored framework source itself with only a stray `Model` dir, two
  were documentation/script directories merely *named* after the real
  apps without containing their internal structure). On Repo B, 4
  top-level app directories are structurally identical Next.js
  siblings — a second, framework-different case of the same topology
  pattern, currently invisible to `--llm` output entirely (no
  CakePHP-shaped dirs to match). This also confirms topology and
  tooling are genuinely orthogonal in practice: Repo A is a monorepo by
  structure alone with zero tooling signal, while Repo B is currently
  only detected as a monorepo via `turbo.json` (tooling), with its real
  Next.js topology undetected. Evidence-sufficient; still correctly not
  implemented in v1.2.0 per Release Verification Mode's no-new-features
  scope — target v1.3.0 development.
  **Further refinement from a third repo (PleasePo, personal project):**
  its `admin/` and `website/` directories share 14 nearly-identical
  structural elements (a Vite+TypeScript+shadcn scaffold —
  `components.json`, `vite.config.ts`, `tsconfig.*.json`, `src`,
  `public`, etc.) — an unmistakable multi-app topology case. But the
  CakePHP-specific `{Controller,Model,View,webroot}` heuristic returns
  zero overlap for both directories — it would completely miss this
  monorepo. This is a different kind of finding than Repo A/B: those
  confirmed the *concept* of topology detection is sound; this shows the
  plan doc's *specific implementation* (a fixed CakePHP-shaped pattern)
  is too narrow. Three real repos, three frameworks (CakePHP MVC dirs,
  Next.js app dirs, Vite+shadcn scaffold dirs), and a single hardcoded
  set of directory names only catches one of the three. The v1.3.0
  design should likely detect structural self-similarity across sibling
  directories generically (e.g. "N≥2 top-level dirs share a large
  overlapping subset of children") rather than pattern-match one
  framework's known layout.
- **`Console` as a CakePHP stack signal** — explicitly rejected (not
  merely deferred) during item 3's pressure test; insufficient evidence
  of real-world value versus the ambiguity risk.
- **Generalizing `on_progress` into a broader `events`/`observer` hook**
  — one motivating use case (CLI progress) doesn't yet justify the
  abstraction, per this project's Phase 3 discipline (extract rules only
  after repetition).

## Real-World Testing Results (Release Verification Mode)

Tested against five real repositories, not synthetic fixtures (Repo A
and Repo B are business-owned — generic labels used, internal names
withheld; PleasePo, CheckMe, and SafeTrack are the developer's own
personal projects, named directly):

- **Repo A** — CakePHP monorepo, 216,612 files / 19,321 dirs
- **Repo B** — Laravel + Next.js, Turborepo-managed, 60,884 files / 6,817 dirs
- **PleasePo** — Vite+TypeScript admin/website pair, Python/FastAPI
  backend, Flutter mobile app (monorepo)
- **CheckMe** — React Native/Expo mobile app + Python Raspberry Pi
  scanner code, 43,960 files / 9,754 dirs, 8,170 symlinks
- **SafeTrack** — Flutter mobile app + Python/FastAPI server +
  ESP32 Arduino firmware, 17,279 files / 7,154 dirs

This distinguishes two different claims that must not be collapsed into
one — the implementation can execute correctly while a heuristic it
executes is still wrong:

```
Implementation
--------------
PASS, with one bug found and fixed — scan awareness, progress callback
architecture, --no-progress, number formatting, AI tooling notable
flags, path-aware _STACK_SIGNALS matching mechanism, PHP MVC structure
detection, real-repo performance (up to ~217k files), backward
compatibility. All exercised against real data, not just the 100
passing unit tests. Correctly identified React Native/Expo, Flutter,
Python/FastAPI, and Arduino/ESP32 firmware stacks with no other issues
found. The one bug (progress miscounting symlinks) is documented below,
fixed, and covered by a new regression test.

Heuristic Validation
---------------------
PASS, with one known false positive.
```

### Bug found and fixed: progress/summary count mismatch on symlinks

```
Title:    Scan progress counted symlinks; final summary didn't
Status:   Fixed
Evidence: CheckMe — 8,170 symlinks (Python venv + node_modules/.bin).
          Progress reported "51,964 files, 9,728 dirs" on its last
          tick; the final summary reported "Files: 43,960,
          Directories: 9,754" — a real discrepancy, not rounding.
          Root cause: the progress counter in scanner.py incremented
          on every appended node with no symlink check, while
          cli.py's _count_tree() and llm.py's _count_entries() (the
          latter unchanged since v1.0.0, confirmed via
          `git show v1.0.0:src/tree2guide/llm.py`) both explicitly
          skip symlinks. Verified before fixing that symlink-exclusion
          is the correct, established invariant (used consistently
          in _count_entries, _count_tree, _collect_all_names, and
          _collect_all_paths — the progress counter was the sole
          outlier, not one of two valid conventions).
Fix:      One-line change in scanner.py — skip the counts increment
          when the node is a symlink, matching every other counting
          function in the codebase. Re-verified against CheckMe:
          progress, final summary, and --llm's SIZE section now all
          agree (43,960 / 9,754).
Impact:   Any project with many symlinks (venvs, node_modules/.bin,
          etc.) would see live progress numbers run ahead of the true
          final count. No impact on file/dir counts anywhere else —
          those were always correct.
Test:     tests/test_scanner.py::TestBuildNodeTreeProgress::
          test_on_progress_excludes_symlinks_matching_final_count_convention
Release:  v1.2.0 — this release, not deferred.
```

### Known heuristic limitation

```
Title:    config/app.php ambiguity
Status:   Open
Evidence: Repo B — its single Laravel service directory is unambiguously
          Laravel (artisan, bootstrap/app.php, resources/views all
          present; zero webroot/Controller/bin-cake anywhere in the
          entire repo), yet `config/app.php` alone (score 5) still adds
          "CakePHP" as a secondary label, because Laravel and CakePHP
          both use that filename for their primary app config. Laravel
          still ranks first correctly (score 14 vs 5).
Impact:   Any Laravel project may receive a spurious secondary
          "CakePHP" label in --llm detected stack output.
Priority: Medium
Release:  Target v1.3.0 — not a v1.2.0 release blocker; deferred by
          explicit decision, not by oversight.
```

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
  correct source and passes (99/99 at that point; now 100/100 after adding a symlink-counting regression test — see "Real-World Testing Results" above). Noted here so a future session
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

- **3.12.7** — Confirmed: all 100 tests pass, fresh-venv wheel install
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
  at any depth" semantics. Since written, this was validated against two
  real repos (see "Real-World Testing Results" above) — correct for
  CakePHP (Repo A) and Laravel/Next.js/Turborepo (Repo B), with one
  confirmed cross-framework ambiguity (`config/app.php`). Still not
  validated against real-world Symfony, Rails, Java/Kotlin, or Flutter
  repos — those frameworks' path signals remain reasoned-about, not
  field-tested.

---
Prepared by: Claude
Date: 2026-07-02
Reviewed by: Lawrence Roble
