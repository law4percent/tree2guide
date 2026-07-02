# v1.2.0 Test Cases

Human QA checklist. Claude drafts this checklist but never marks
PASS/FAIL itself — that's a human observation of running software, not
something inferable from reading a diff (see `CLAUDE.md`'s Approval vs.
Acceptance distinction and `RELEASE_NOTE.md`'s AI/human boundary). All
boxes below are intentionally left unchecked.

---

## CLI — new in v1.2.0

```
[x] tree2guide --version
      → prints "tree2guide 1.2.0" and exits 0

[x] tree2guide . --no-progress   (on a large directory)
      → suppresses all stderr output (no progress lines, no summary)

[x] tree2guide . --llm   (on a directory with 1000+ files)
      → SIZE section shows comma-formatted counts (e.g. "1,234", not "1234")

[x] tree2guide . --llm   (on a project containing .claude/, .cursor/, etc.)
      → NOTABLE FLAGS lists the new AI-tooling entries, no duplicates

[x] tree2guide .   (on a project with only Controller/, Model/, View/ —
    no bin/cake, no config/app.php)
      → detected stack shows "PHP MVC structure", NOT "CakePHP"

[x] tree2guide .   (on a real CakePHP project with bin/cake present)
      → detected stack shows "CakePHP"
```

## CLI — regression (existing behavior, must be unaffected)

```
[x] tree2guide . --stdout
      → output unaffected by scan progress; stdout stays clean even when
        progress fires on stderr

[x] tree2guide . --format {markdown,text,json,yaml,html}
      → all five still work as before

[x] --dirs-only / --files-only
      → mutual exclusivity still enforced

[x] --exclude-file / .tree2ignore
      → pattern handling unchanged

[x] Symlinks
      → still rendered as "name -> target", never followed
```

## Scan awareness (needs a real large tree — e.g. node_modules, a big monorepo)

```
[x] Progress lines ("Scanning... N files, N dirs") appear on a scan
    taking more than ~1 second

[x] Final line ("Scan complete. Files: N, Directories: N, Elapsed: X.Xs")
    appears once, after the scan finishes

[x] A fast scan of a small project prints no progress/telemetry at all

[x] tree2guide . --stdout 2>/dev/null
      → stdout output is clean tree/summary content only

[x] tree2guide . --stdout 1>/dev/null
      → progress/telemetry still visible on stderr
```

## Python API

```
[ ] import tree2guide; tree2guide.__version__ == "1.2.0"

[ ] tree2guide.build_node_tree(root, matcher)   — no on_progress arg
      → behaves exactly as pre-v1.2.0

[ ] tree2guide.build_node_tree(root, matcher, on_progress=callback)
      → callback receives (files, dirs), fires periodically on a large scan

[ ] tree2guide.analyze(node)
      → CakePHP/Laravel/Symfony/Rails/Java/Kotlin/Flutter path-based
        signals fire correctly on REAL project layouts, not just the
        synthetic test fixtures used in tests/test_llm.py
```

## Platform

```
[ ] Windows: --stdout piping still works without UnicodeEncodeError
      (existing fix, unchanged this release — NOT independently
      re-verified this cycle, no Windows environment available)

[ ] Windows: progress/telemetry lines render correctly in cmd.exe /
    PowerShell / Windows Terminal
      (plain print(), no \r tricks — should be safe by design, not yet
      human-verified on real Windows)

[x] macOS: verified during evidence generation (fresh venv install, all
    commands ran cleanly) — independent human re-verification still
    recommended

[ ] Linux: relies on CI — NOT yet run, see CI Gap in RELEASE_CHECKLIST.md
```

## Performance

```
[x] Scan a 100k+ file directory
      → progress appears, final summary counts match reality, no crash,
        elapsed time is reasonable
```

## Packaging

```
[x] Fresh venv install from the built wheel
      (already done once during evidence generation — human should
      independently re-verify)

[ ] pip install tree2guide   (from TestPyPI, once uploaded — not yet uploaded)

[ ] pip install tree2guide   (from real PyPI, once uploaded — not yet uploaded)
```

---

Result:  PASS / FAIL / NOT TESTED
Tester: Lawrence Roble
Date: July 2, 2026
