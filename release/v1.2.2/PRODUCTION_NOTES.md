# v1.2.2 Production Notes

Release engineer's notebook — internal record, not user-facing
documentation.

---

## What this release is

A single-bug PATCH release. No new features, no API changes, no
behavior changes outside the fix below.

## Bug fixed: excluded directories resurrected by unrelated nested-name matches

```
Title:    An excluded directory (e.g. `build/`) still appeared in
          tree2guide output, with contents, despite no rule in
          .tree2ignore whitelisting it
Status:   Fixed
Evidence: Reported against a real project's `mobile/.tree2ignore`:
              *
              !android
              !assets
              ...
              !reports
          `build/` matches no `!` rule, yet appeared fully in the
          generated MOBILE_DIR_STRUCTURE.md. Root-caused by reading
          src/tree2guide/ignore.py and src/tree2guide/scanner.py, then
          confirmed on the real filesystem:
              /mobile/build/reports              (matches `!reports`)
              /mobile/build/unit_test_assets/assets  (matches `!assets`)
          both exist on disk, exactly as the code-level analysis
          predicted.
Root cause: Two independent, individually-reasonable behaviors combined
          into an incorrect result:
          1. `ignore.py:42-44` — a pattern with no `/` is intentionally
             unanchored, so `!reports` matches a folder named `reports`
             at ANY depth, not just at the target root. This is
             documented, working-as-designed gitignore-style behavior.
          2. `scanner.py`'s `build_node_tree()` (old code) recursed into
             every directory unconditionally, before checking whether
             it was excluded, then kept an excluded directory visible
             if any descendant survived exclusion. So `build/reports`
             surviving (via the unanchored `!reports` match) kept
             `build/unit_test_assets` visible, which kept `build/`
             itself visible — even though `build/` was never
             whitelisted.
          This diverges from real Git: Git never descends into an
          already-excluded directory, so a nested `!pattern` elsewhere
          in the tree can never resurrect an ignored ancestor that way.
          `docs/tree2ignore.md` explicitly (and, prior to this release,
          incorrectly) claimed tree2guide's behavior here was "exactly
          the same behaviour as Git."
Fix:      `build_node_tree()` in scanner.py now checks exclusion first
          and skips (does not recurse into) an excluded directory
          immediately — matching Git's actual traversal behavior.
          `docs/tree2ignore.md` troubleshooting section updated to
          describe the real cause (unanchored pattern name collisions)
          and the real limitation (once a directory is excluded,
          nothing inside it can be re-included, matching Git — every
          level of a nested whitelist path must be un-excluded
          explicitly, e.g. `!node_modules`, `!node_modules/keep-me`,
          `!node_modules/keep-me/**`).
Impact:   Any `.tree2ignore` using the common "exclude everything, `!`
          whitelist specific top-level folders" pattern (documented in
          tree2guide's own docs as the recommended whitelist idiom) was
          at risk of silently leaking excluded directories into output
          whenever an excluded directory happened to contain a
          nested folder sharing a name with any whitelisted folder.
          This is a plausible, not rare, collision — `reports`,
          `assets`, `build`, `test`, `lib`, `dist` are all common names
          that show up as both top-level project folders and nested
          build-tool output folders.
Test:     No existing scanner test exercised the
          "excluded-directory-with-nested-name-collision" scenario
          before this fix (checked tests/test_scanner.py — none of the
          existing exclude-related coverage there). Not added as an
          automated regression test in this pass — flagging as a real
          gap. The existing 100 tests were re-run against the fix and
          all pass, confirming no behavioral regression to already-
          covered scanner paths (max_depth, dirs_only, files_only,
          no_hidden, sort, symlinks, progress reporting).
Release:  v1.2.2
```

## Known Limitations

- All limitations listed in the v1.2.1 `PRODUCTION_NOTES.md` are
  unchanged — this release touches nothing else.
- No new automated test added for this exact bug (see Test note above).
- The fix changes recursion order: an excluded directory's contents are
  no longer walked at all. If any caller depended on `on_progress`
  counting entries inside excluded-but-formerly-resurrected directories,
  those counts will now be lower (this is the correct behavior, but is
  a visible behavior change in progress-reporting numbers for affected
  trees).

## Risk Areas

- **No automated regression test for this exact bug.** Verified by
  direct reproduction against a real project's `.tree2ignore` and the
  real filesystem, plus the full existing suite (100/100 passing), not
  by a new unit test targeting this scenario specifically.
- **Behavior change, not purely additive.** Any user who was
  (knowingly or not) relying on the old resurrection behavior to expose
  nested files inside an otherwise-excluded directory will see those
  files disappear after upgrading. This is the intended fix, but is a
  visible output change for that edge case, not just a bug going away
  invisibly.
- **`docs/tree2ignore.md` correction changes documented guidance**,
  not just code — worth a second read before publishing, since it
  reverses a previous (incorrect) claim about Git-equivalence.

## Rollback Notes

- **If PyPI upload fails partway:** nothing is live yet at that point —
  safe to fix and re-run `twine upload`.
- **If a problem is found after this ships:** version numbers are
  permanent on PyPI — the fix would be `v1.2.3`, not a re-upload of
  `1.2.2`.

## Things to Verify After PyPI Publish

- `pip install tree2guide` in a fresh environment resolves to `1.2.2`
- `tree2guide --version` → `tree2guide 1.2.2`
- Against a `.tree2ignore` using the `*` + `!whitelist` idiom, an
  excluded directory containing a nested folder that shares a name with
  a whitelisted folder no longer appears in output.

## Python Versions Tested

- **3.12.7** — Confirmed: all 100 tests pass, fix reproduced and
  verified fixed via editable install (`pip install -e .`), both the
  `tree2guide` console script and `python -m tree2guide.cli` confirmed
  to resolve to local `src/` after the editable install.
- **3.9, 3.10, 3.11** — Not tested this cycle. The fix is a pure
  control-flow reordering in `scanner.py` with no new syntax, so no
  version-specific risk is expected, but this has not been
  independently confirmed.

---
Prepared by: Claude
Date: 2026-07-11
Reviewed by: Lawrence Roble
