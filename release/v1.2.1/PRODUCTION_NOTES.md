# v1.2.1 Production Notes

Release engineer's notebook — internal record, not user-facing
documentation.

---

## What this release is

A single-bug PATCH release. No new features, no API changes, no
behavior changes outside the one fix below.

## Bug fixed: UnicodeEncodeError crash in default (file-writing) mode on Windows

```
Title:    tree2guide <target> crashes after writing the file, on a
          non-UTF-8 Windows console
Status:   Fixed
Evidence: Reproduced on this machine — cmd.exe / PowerShell resolve to
          cp1252 by default. Running `tree2guide sample` (no --stdout)
          wrote sample_tree.md correctly, then raised:
              UnicodeEncodeError: 'charmap' codec can't encode
              character '✅' in position 0
          on cli.py's `print(f"✅ Tree written to: {output_path}")`,
          returning exit code 1 and a traceback instead of the success
          message.
Root cause: print() uses the interpreter's default stdout text encoding,
          which on Windows follows the active console codepage — not
          UTF-8 unless the user has opted into UTF-8 mode (`chcp 65001`
          or PYTHONUTF8=1). The ✅ emoji (U+2705) has no cp1252/cp437
          mapping.
Distinction from the v1.0.0 fix: v1.0.0 fixed the same underlying class
          of error, but only for `--stdout` piping (box-drawing
          characters written via `sys.stdout.buffer.write(...utf-8...)`
          bytes). That fix does not cover the default file-writing
          path's plain `print()` calls, which is the path this release
          fixes.
Fix:      `main()` now reconfigures `sys.stdout` and `sys.stderr` to
          UTF-8 (`errors="replace"`) at startup, guarded by
          `hasattr(stream, "reconfigure")` for interpreter
          compatibility. This covers every print() call in the module
          going forward, not just the one that crashed.
Impact:   Any Windows user not running in UTF-8 console mode who used
          the default (non---stdout) CLI invocation would hit this on
          every run. The tree file itself was always written correctly
          — only the success/status messages after it crashed. Users
          may not have realized the file was fine, since the traceback
          looks like total failure.
Test:     Not yet covered by an automated regression test — pytest's
          capsys/capsysbinary fixtures replace stdout with objects that
          don't reproduce Windows console codepage behavior, so this
          class of bug is invisible to the existing test suite (same
          gap the v1.0.0 stdout fix likely had). Worth a follow-up: a
          test that patches sys.stdout to a stream with a restrictive
          encoding and asserts main() doesn't raise. Not added in this
          pass — flagging as a real gap rather than skipping silently.
Release:  v1.2.1
```

## Known Limitations

- All limitations listed in the v1.2.0 `PRODUCTION_NOTES.md` are
  unchanged — this release touches nothing else.

## Risk Areas

- **No automated regression test for this exact crash** (see Test note
  above). Verified by direct reproduction and re-verification on this
  machine only, not by CI or a new unit test.
- **`errors="replace"` on stderr/stdout is new global behavior** — any
  future print() call containing a character unsupported by the
  console's codepage will now silently render as `?` (or similar)
  instead of crashing. This is a deliberate tradeoff (never crash on
  encoding) but means such issues would need to be caught by
  visually reviewing output, not by the interpreter erroring loudly.
- **Not tested on real Windows hardware in a fresh venv** — this pass
  reproduced and fixed the bug using an existing local dev environment
  (editable install), not a clean install-from-wheel verification.

## Rollback Notes

- **If PyPI upload fails partway:** nothing is live yet at that point —
  safe to fix and re-run `twine upload`.
- **If a problem is found after this ships:** version numbers are
  permanent on PyPI — the fix would be `v1.2.2`, not a re-upload of
  `1.2.1`.

## Things to Verify After PyPI Publish

- `pip install tree2guide` in a fresh environment resolves to `1.2.1`
- `tree2guide --version` → `tree2guide 1.2.1`
- On a real Windows machine, `tree2guide <target>` (default mode, no
  `--stdout`) exits 0 and prints the ✅ success line without a
  traceback, in both cmd.exe and PowerShell, with the console left at
  its default (non-UTF-8) codepage.

## Python Versions Tested

- **3.12.7** — Confirmed: all 100 tests pass, fix reproduced and
  verified fixed via editable install.
- **3.9, 3.10, 3.11** — Not tested this cycle. `sys.stdout.reconfigure`
  exists on all of Python 3.9+ (added in 3.7), so no version-specific
  risk is expected, but this has not been independently confirmed.

---
Prepared by: Claude
Date: 2026-07-11
Reviewed by: Lawrence Roble
