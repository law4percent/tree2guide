# v1.2.2 Test Cases

Human QA checklist. Claude drafts this checklist but never marks
PASS/FAIL itself — that's a human observation of running software, not
something inferable from reading a diff (see `CLAUDE.md`'s Approval vs.
Acceptance distinction and `RELEASE_NOTE.md`'s AI/human boundary). All
boxes below are intentionally left unchecked.

---

## Bug fixed in v1.2.2

```
[x] .tree2ignore with `*` followed by unanchored `!name` whitelist rules
    (e.g. `!reports`, `!assets`), run against a tree containing an
    EXCLUDED top-level directory that has a nested folder sharing one of
    those whitelisted names (e.g. an excluded `build/` containing
    `build/reports` and `build/unit_test_assets/assets`)
      → the excluded top-level directory (`build/`) no longer appears in
        the output at all
      → the genuinely whitelisted top-level directories (`android/`,
        `assets/`, `reports/`, etc.) still render fully, unaffected

[x] Re-run against a real project's .tree2ignore (this bug was found and
    fixed using mobile/.tree2ignore) and confirm `build/` is absent from
    the regenerated output in every format (markdown, text, json, yaml,
    html, llm)
```

## Regression (existing behavior, must be unaffected)

```
[x] Whitelist-only-one-folder pattern from docs.md
    (`*` / `!src` / `!src/**`) still shows `src/` and its full contents

[x] Standard exclude patterns with no whitelist rules still work exactly
    as before (e.g. `node_modules`, `*.log`)

[x] DEFAULT_EXCLUDES still always apply: `.git`, `.tree2ignore`,
    `__pycache__`, `*.pyc`, `.DS_Store`

[x] --max-depth, --dirs-only, --files-only, --no-hidden still behave
    correctly

[x] Symlinks still rendered as `name -> target`, not followed/recursed

[x] All six output formats (markdown, text, json, yaml, html, llm)
    still produce correct, non-empty trees

[x] tree2guide --version → prints "tree2guide 1.2.2"
```

## Python API

```
[x] import tree2guide; tree2guide.__version__ == "1.2.2"

[x] build_node_tree(root, matcher) called directly still returns the
    correct TreeNode tree, with excluded directories (and only excluded
    directories with no whitelisted descendants) absent from
    node.children
```

## Platform

```
[x] Windows (cmd.exe) — this is where the bug was found and fixed
[x] Windows (PowerShell)
[ ] macOS
[ ] Linux
```

---

Result: PASSED
Tester: Lawrence Roble
Date: 2026/07/11
