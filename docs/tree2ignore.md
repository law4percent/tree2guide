# The `.tree2ignore` Guide

`.tree2ignore` is the exclusion file for `tree2guide`. It follows the **exact same syntax as `.gitignore`** — the matching engine is reimplemented in pure Python so every rule that works in Git works here too, with no third-party dependencies.

## The #1 rule: where it lives

**`.tree2ignore` must sit directly inside the folder you pass as the target.**

```bash
tree2guide docs        # .tree2ignore goes inside docs/
tree2guide .           # .tree2ignore goes inside the current directory
tree2guide src/app     # .tree2ignore goes inside src/app/
```

Patterns inside it are written **relative to that folder** — the same way a `.gitignore` never includes its own folder's name as a prefix.

## Pattern syntax

| Pattern | Meaning |
|---|---|
| `build` | Matches a file or folder named `build` at **any depth** |
| `build/` | Same, but **only matches directories** |
| `/build` | Matches `build` **only at the root** of the target (anchored) |
| `*.log` | Matches all files ending in `.log`, at any depth |
| `**/android/key.properties` | Matches that path at **any depth** |
| `app.*.symbols` | Wildcard anywhere in the filename |
| `!keep-this` | **Negates** — re-includes something an earlier rule excluded |
| `# comment` | Ignored |
| *(blank line)* | Ignored |

Rules are evaluated **top to bottom** — later rules override earlier ones, including un-excluding things with `!`.

## Common patterns

### Exclude build artifacts

```gitignore
/build
/dist
/out
*.pyc
__pycache__
*.class
```

### Exclude dependencies

```gitignore
node_modules
.venv
venv
vendor
```

### Exclude generated files

```gitignore
*.lock
*.log
*.map
coverage/
.cache/
```

### Whitelist — show only one folder

Show **only** `src/` and hide everything else:

```gitignore
*
!src
!src/**
```

### Copy your `.gitignore` directly

This is the intended workflow. A real Flutter `.gitignore` works as-is:

```gitignore
logs
**/android/app/keystore/*.jks
**/android/key.properties
*.class
*.log
*.pyc
*.swp
.DS_Store
.idea/
.dart_tool/
.flutter-plugins-dependencies
.pub-cache/
.pub/
/build/
/coverage/
/android/app/debug
/android/app/profile
/android/app/release
```

## Always-excluded defaults

These are excluded automatically, without any `.tree2ignore` needed:

| Entry | Reason |
|---|---|
| `.git` | Version control internals |
| `.tree2ignore` | The exclude file itself |
| `__pycache__` | Python bytecode cache |
| `*.pyc` | Python compiled files |
| `.DS_Store` | macOS metadata |

## Troubleshooting

**"No exclude file found at .../.tree2ignore"**
Your `.tree2ignore` is in the wrong folder. It must be directly inside the target folder you passed, not in its parent or a subfolder.

**Patterns aren't excluding anything**
Check for a stray prefix. If you ran `tree2guide docs`, don't write `docs/api` — just write `api`. Use `/api` only if you want it anchored to the root of `docs/`.

**I want to exclude everything except one folder**
Use the whitelist pattern:
```gitignore
*
!keepme
!keepme/**
```

**A directory is still showing even though I excluded it**
Check whether an unanchored `!pattern` elsewhere in the file happens to match a folder of the same name nested inside it (e.g. `!reports` also matches `build/reports`). Anchor the pattern with a leading `/` (`!/reports`) to restrict it to the root.

**I excluded a directory, so why can't `!` bring back a file inside it?**
Same as Git: once a directory is excluded, `tree2guide` never descends into it, so nothing inside can be re-included — not even with `!`. You must un-exclude every level of the path, e.g. `!node_modules`, `!node_modules/keep-me`, `!node_modules/keep-me/**`.