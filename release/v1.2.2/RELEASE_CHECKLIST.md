# v1.2.2 Release Checklist

Dated record of which `RELEASE_NOTE.md` (Release SOP) steps were actually
followed for this specific release. Not a restatement of the SOP itself —
see `.ignoredthis/tree2guide-test/RELEASE_NOTE.md` for the reusable
procedure this instantiates.

Branch: `v1.2.2` (local only — not pushed to origin)
Base: `main` @ current tip, plus the scanner fix from this session

This is a single-bug PATCH release. No new features, no API changes.

---

## Pre-flight Check

| Item | Status | Notes |
|---|---|---|
| All tests pass locally (pytest) | ✅ Confirmed | 100 passed, 2026-07-11, run against the editable install (`tree2guide.scanner.__file__` verified to resolve into `src/`, not the stale non-editable site-packages copy that existed at the start of this session) |
| No uncommitted changes (git status) | ✅ Confirmed | fix + version bump + changelog + these artifacts committed together on this branch |
| Version number correct in pyproject.toml | ✅ Confirmed | `1.2.2` |
| `__version__` in `__init__.py` matches | ✅ Confirmed | `1.2.2` |
| CHANGELOG has entry with real date | ✅ Confirmed | `docs/changelog.md` — `## [1.2.2] — 2026-07-11` |
| README examples match current CLI/API | ✅ Confirmed | no CLI surface changed this release |
| README installation section accurate | ✅ Confirmed | unchanged from v1.2.1 |
| No internal/planning docs in docs/ | ✅ Confirmed | only `docs/tree2ignore.md` touched, a public troubleshooting correction, not a planning doc |
| LICENSE file exists, matches pyproject.toml license field | ✅ Confirmed | unchanged from v1.2.1 |
| CI is passing on GitHub | ⏳ Not run | branch not pushed yet — see Source Control below |
| No `__pycache__`/`.pytest_cache`/`*.egg-info` committed | ✅ Confirmed | `git status` shows none; `.gitignore` covers all three |

---

## Level 1 — Phase 1: Documentation

| Item | Status |
|---|---|
| CHANGELOG updated, user-facing language, real date | ✅ Confirmed |
| No internal planning docs inside docs/ | ✅ Confirmed |
| `docs/tree2ignore.md` troubleshooting section corrected to match new (Git-faithful) behavior | ✅ Confirmed |

## Level 1 — Phase 2: Metadata

| Item | Status |
|---|---|
| pyproject.toml version bumped | ✅ Confirmed — `1.2.2` |
| Other pyproject.toml fields | N/A — unchanged from v1.2.1, already audited then |

## Level 1 — Phase 3: Build

| Item | Status |
|---|---|
| `python -m build` | ⏳ Not run this pass — deferred until you confirm you want to proceed to a real build/publish cycle |
| `python -m twine check dist/*` | ⏳ Not run — depends on above |
| Wheel/sdist contents inspected | ⏳ Not run — depends on above |

## Level 1 — Phase 4: Installation Verification

| Item | Status |
|---|---|
| Fresh venv install from built wheel | ⏳ Not run — no wheel built yet this pass |

## Level 1 — Phase 5: Source Control

| Item | Status |
|---|---|
| Repo structure standard | ✅ Confirmed (unchanged) |
| Commit | ✅ Confirmed — committed on branch `v1.2.2`, no `main` history rewritten |
| Tag `v1.2.2` | ⏳ Not created — requires explicit instruction |
| Push `v1.2.2` | ⏳ Not pushed — requires explicit instruction |
| CI verified green on all 4 Python versions | ⏳ Not run — CI only triggers on push/PR; branch is local-only this pass |

## Level 1 — Phase 6: Publish

Not started. Requires PyPI/TestPyPI credentials and explicit, separate
authorization for each upload — an irreversible action not performed as
part of this pass.

## Level 1 — Phase 7: Post Release

Not started — depends on Phase 6.

---

## What this release fixes

`build_node_tree()` in `src/tree2guide/scanner.py` used to recurse into
every directory, excluded or not, and only decided afterward whether to
hide it — keeping an excluded parent visible if any descendant survived.
Combined with unanchored `!pattern` rules matching a folder name at any
depth (by design, documented in `docs/tree2ignore.md`), a whitelist rule
meant for one top-level folder (e.g. `!reports`) could resurrect an
unrelated excluded directory elsewhere (e.g. `build/`) if it happened to
contain a same-named nested folder (`build/reports`). Fixed by skipping
excluded directories immediately, without recursing into them — matching
Git's actual behavior of never descending into an ignored directory.

Full finding, evidence, and fix detail: `release/v1.2.2/PRODUCTION_NOTES.md`.

---

Note on the marks above: ✅ items are objective, reproducible results
from commands actually executed during this pass. This is evidence
generation only, not a release-readiness or "production ready"
declaration — that determination belongs to a human, per
`RELEASE_NOTE.md`'s AI/human boundary.

Prepared by: Claude (evidence generation only)
Date: 2026-07-11
Reviewed by: Lawrence Roble
