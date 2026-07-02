# v1.2.0 Release Checklist

Dated record of which `RELEASE_NOTE.md` (Release SOP) steps were actually
followed for this specific release. Not a restatement of the SOP itself —
see `.ignored/RELEASE_NOTE.md` for the reusable procedure this instantiates.

Branch: `rc/v1.2.0` (local only — not yet pushed to origin)
Base commit: `076c21e` "IN DEV: v.1.2.0" (pushed to `origin/v1.2.0`)

---

## Pre-flight Check

| Item | Status | Notes |
|---|---|---|
| All tests pass locally (pytest) | ✅ Confirmed | 99 passed, 2026-07-02 |
| No uncommitted changes (git status) | ✅ Confirmed | clean except untracked `.ignored/` (not part of the package) |
| Version number correct in pyproject.toml | ✅ Confirmed | `1.2.0` |
| `__version__` in `__init__.py` matches | ✅ Confirmed | `1.2.0` |
| CHANGELOG has entry with real date | ✅ Confirmed | `docs/changelog.md` — `## [1.2.0] — 2026-07-01` |
| README examples match current CLI/API | ✅ Confirmed | `--version`, `--no-progress` documented; Command Reference and Public API tables updated |
| README installation section accurate | ✅ Confirmed | `pip install tree2guide`; dev setup via `pip install -e ".[dev]"` |
| No internal/planning docs in docs/ | ✅ Confirmed | grepped for plan/draft/todo/internal/scratch — none found |
| LICENSE file exists, matches pyproject.toml license field | ✅ Confirmed | `LICENSE` present; `license = { file = "LICENSE" }` |
| CI is passing on GitHub | ⛔ **BLOCKED** | see "CI Gap" below |
| No `__pycache__`/`.pytest_cache`/`*.egg-info` committed | ✅ Confirmed | `git ls-files` shows none tracked; `.gitignore` covers all three |

## CI Gap — release blocker

`.github/workflows/ci.yml` triggers only on push/PR to `main`:
```yaml
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
```
Confirmed via `gh run list --branch v1.2.0`: **zero CI runs exist** for
this branch's commit. This means the Python 3.9 compatibility fix
(`from __future__ import annotations` added to `cli.py`) — the exact
defect class this project's own SOP calls out as something "only CI
catches" — has **not** been verified against a real Python 3.9
interpreter. Local verification this session only covers Python 3.12.7.

This needs a decision before Phase 5 (Source Control) can be honestly
marked complete: open a PR from `rc/v1.2.0` (or `v1.2.0`) into `main` to
get real CI signal, or extend the workflow's branch triggers. Not
resolved unilaterally — pending your decision.

---

## Level 1 — Phase 1: Documentation

| Item | Status |
|---|---|
| README answers what/why/install/usage/output/docs | ✅ Confirmed (pre-existing, verified still accurate) |
| Absolute GitHub URLs for all docs/ links in README | ✅ Confirmed — grepped, zero relative links found |
| CHANGELOG updated, user-facing language, real date | ✅ Confirmed |
| No internal planning docs inside docs/ | ✅ Confirmed |

## Level 1 — Phase 2: Metadata

| Item | Status |
|---|---|
| pyproject.toml fields audited | ✅ Confirmed — name/version/description/readme/license/authors/requires-python/dependencies/keywords/classifiers/urls/scripts all present |
| LICENSE file exists at repo root | ✅ Confirmed |
| PyPI name availability | N/A — not a first release; `tree2guide` is already live on PyPI at v1.1.0 |

## Level 1 — Phase 3: Build

| Item | Status |
|---|---|
| Upgrade build/twine | ✅ Confirmed already current — build 1.5.0, twine 6.2.0 |
| `python -m build` | ✅ Confirmed — built `tree2guide-1.2.0.tar.gz` and `tree2guide-1.2.0-py3-none-any.whl` |
| `python -m twine check dist/*` | ✅ Confirmed — both **PASSED** |
| Wheel contents inspected | ✅ Confirmed — all source files, LICENSE, `entry_points.txt`, METADATA (16KB) present |
| Sdist contents inspected | ✅ Confirmed — LICENSE, README.md, pyproject.toml, `src/`, `tests/` (incl. new `test_cli.py`) present |

## Level 1 — Phase 4: Installation Verification

| Item | Status |
|---|---|
| Fresh venv created | ✅ Confirmed — `.venv-test`, deleted after |
| Installed from built wheel | ✅ Confirmed |
| `tree2guide --version` | ✅ Confirmed — printed `tree2guide 1.2.0` |
| Real commands (`--stdout`, `--llm`, `--no-progress`) | ✅ Confirmed — all ran successfully |
| Python import + `__version__` | ✅ Confirmed — `1.2.0` |
| Test venv deleted | ✅ Confirmed |

## Level 1 — Phase 5: Source Control

| Item | Status |
|---|---|
| Repo structure standard (src/ layout, no wrapper folder) | ✅ Confirmed (pre-existing) |
| CI workflow references correct working directory | N/A — no `working-directory:` override, runs from repo root |
| Python 3.9 compatibility (`from __future__ import annotations`) | ⚠️ Fixed in source; **not yet verified on a real 3.9 interpreter** — see CI Gap |
| Commit | ✅ Already committed (`076c21e`, outside this session) |
| Tag `v1.2.0` | ⛔ Not done — requires explicit instruction |
| Push `rc/v1.2.0` | ⛔ Not done — requires explicit instruction |
| CI verified green on all 4 Python versions before publishing | ⛔ Not done — blocked, see CI Gap |

## Level 1 — Phase 6: Publish

Not started. Requires PyPI/TestPyPI credentials and explicit, separate
authorization for each upload — an irreversible action not performed as
part of generating this evidence.

## Level 1 — Phase 7: Post Release

Not started — depends on Phase 6.

---

Note on the ✅ marks above: these are objective, reproducible check
results from commands actually executed during this evidence-generation
pass (test runs, `twine check`, wheel/sdist inspection, fresh-venv
install) — not a release-readiness or "production ready" declaration.
That determination belongs to a human, per `RELEASE_NOTE.md`'s AI/human
boundary.

Prepared by: Claude (evidence generation only)
Date: 2026-07-02
