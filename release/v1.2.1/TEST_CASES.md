# v1.2.1 Test Cases

Human QA checklist. Claude drafts this checklist but never marks
PASS/FAIL itself — that's a human observation of running software, not
something inferable from reading a diff (see `CLAUDE.md`'s Approval vs.
Acceptance distinction and `RELEASE_NOTE.md`'s AI/human boundary). All
boxes below are intentionally left unchecked.

---

## Bug fixed in v1.2.1

```
[x] tree2guide <target>   (default mode, no --stdout, on a real Windows
    terminal using a non-UTF-8 codepage, e.g. cmd.exe or PowerShell with
    the default cp1252/cp437 console)
      → completes with exit code 0
      → prints "✅ Tree written to: <path>" without a UnicodeEncodeError
        traceback
      → the written file's contents are correct (this part already
        worked before the fix — only the success message crashed)

[x] Same command on a UTF-8-native terminal (Windows Terminal with UTF-8
    codepage, macOS, Linux)
      → unchanged behavior, no regression
```

## Regression (existing behavior, must be unaffected)

```
[x] tree2guide . --stdout
      → still writes raw UTF-8 bytes directly to stdout, unaffected by
        the new stdout/stderr reconfigure call in main()

[x] tree2guide . --stdout   (piped into another program, e.g. `clip` on
    Windows or `| cat` elsewhere)
      → box-drawing characters (├, └, │) still render correctly — this
        is the pre-existing v1.0.0 fix, should be untouched

[x] tree2guide --version
      → still prints version and exits 0

[x] tree2guide . --no-progress
      → stderr still fully suppressed

[x] tree2guide .   (on a large-enough directory to trigger progress)
      → "Scanning... N files, N dirs" and "Scan complete." still appear
        on stderr, unaffected by the stdout/stderr reconfigure

[x] tree2guide --format {markdown,text,json,yaml,html,llm}
      → all six still work
```

## Python API

```
[x] import tree2guide; tree2guide.__version__ == "1.2.1"
```

## Platform

```
[x] Windows (cmd.exe): default file-writing mode, non-UTF-8 codepage
      → this is the exact failure mode this release fixes; needs real
        human verification on real Windows hardware, not just the
        editable-install repro from this session
[x] Windows (PowerShell)
[ ] macOS
[ ] Linux
```

---

Result:  PASSED
Tester: Lawrence Roble
Date: 2026-07-11
