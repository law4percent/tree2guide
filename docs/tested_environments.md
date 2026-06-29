# Tested Environments

This document tracks verified platforms, known issues, and workarounds
for `tree2guide`. If you successfully run tree2guide on a platform not
listed here, please [open an issue](https://github.com/law4percent/tree2guide/issues)
or submit a PR to add it.

---

## Verified Platforms

| OS | OS Version | Python | pyenv | Shell | Status |
|---|---|---|---|---|---|
| Windows | 11 (pyenv-win) | 3.12.7 | pyenv-win | PowerShell / cmd | ✅ Verified |
| macOS | 26.2 | 3.12.7 | pyenv + Homebrew | zsh | ✅ Verified |
| Ubuntu | 22.04+ (GitHub Actions) | 3.9 | — | bash | ✅ CI passing |
| Ubuntu | 22.04+ (GitHub Actions) | 3.10 | — | bash | ✅ CI passing |
| Ubuntu | 22.04+ (GitHub Actions) | 3.11 | — | bash | ✅ CI passing |
| Ubuntu | 22.04+ (GitHub Actions) | 3.12 | — | bash | ✅ CI passing |

> CI runs on every push and pull request via GitHub Actions.
> See [ci.yml](../.github/workflows/ci.yml) for the full matrix.

---

## Not Yet Verified

| OS | Notes |
|---|---|
| Windows 10 | Likely works — not formally tested |
| macOS (Intel) | Likely works — only tested on Apple Silicon so far |
| macOS (older versions) | Unknown |
| Linux (non-Ubuntu distros) | Likely works — CI uses Ubuntu only |
| FreeBSD | Unknown |
| Windows (without pyenv) | Unknown — standard Python installer untested |

If you test on any of these, please report back via
[GitHub Issues](https://github.com/law4percent/tree2guide/issues).

---

## Known Platform-Specific Issues

### 1. Windows — `--stdout` Garbled Characters When Piping

**Platform:** Windows (all versions)
**Affected command:** `tree2guide . --stdout | clip`
**Symptom:**

```
UnicodeEncodeError: 'charmap' codec can't encode characters in position 18-20:
character maps to <undefined>
```

**Cause:** Windows default terminal encoding (`cp1252`) cannot encode
box-drawing characters (`├`, `└`, `│`) when piping output.

**Workaround (already fixed in v1.0.0):**
The CLI writes raw UTF-8 bytes directly to `sys.stdout.buffer` when
`--stdout` is used, bypassing the codec. If you encounter this on an
older version, upgrade:

```bash
pip install --upgrade tree2guide
```

---

### 2. macOS — pyenv Shim Lock After `pip install`

**Platform:** macOS with pyenv + zsh
**Affected command:** `tree2guide --help` (after fresh install)
**Symptom:**

```bash
pyenv: cannot rehash: couldn't acquire lock
/pyenv/shims/.pyenv-shim: cannot overwrite existing file
zsh: command not found: tree2guide
```

**Cause:** A stale pyenv lock file prevents pyenv from registering
the new `tree2guide` shim after installation. This is a pyenv
environment issue, not a tree2guide bug — the package installed
correctly.

**Fix:**

```bash
rm ~/.pyenv/shims/.pyenv-shim
pyenv rehash
```

Then verify:

```bash
which tree2guide
tree2guide --help
```

**Prevention:** This sometimes happens when multiple pip installs run
close together. If it recurs, the same fix applies.

---

### 3. Windows — `tree2guide` Command Not Found After Install (pyenv-win)

**Platform:** Windows with pyenv-win
**Affected command:** `tree2guide --help` (after fresh install)
**Symptom:**

```bash
'tree2guide' is not recognized as an internal or external command
```

**Cause:** pyenv-win shims not on PATH, or rehash needed.

**Fix:**

```bash
pyenv rehash
```

If still not found, verify pyenv shims are on PATH:

```bash
echo %PATH%
```

You should see `...\.pyenv\shims` in the output. If missing, add
to your system PATH or add to your shell profile:

```bash
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/shims:$PYENV_ROOT/bin:$PATH"
```

---

### 4. macOS / Linux — pyenv PATH Not Configured

**Platform:** macOS or Linux with pyenv
**Symptom:** `command not found: tree2guide` even after successful install
**Cause:** pyenv shims directory not on PATH.

**Fix:** Add to `~/.zshrc` (zsh) or `~/.bashrc` (bash):

```bash
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/shims:$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"
```

Then reload:

```bash
source ~/.zshrc   # or source ~/.bashrc
pyenv rehash
tree2guide --help
```

---

## How to Report a New Environment

If you test tree2guide on a platform not listed here:

1. Run these commands and note the output:

```bash
# Python version
python --version

# OS info (macOS/Linux)
sw_vers        # macOS
uname -a       # Linux

# OS info (Windows)
winver         # run in cmd or PowerShell

# tree2guide version
python -c "import tree2guide; print(tree2guide.__version__)"

# Basic test
tree2guide . --stdout
```

2. Open an issue at:
`https://github.com/law4percent/tree2guide/issues`

Use the title format: `[Environment] Verified on <OS> <version> Python <version>`
or `[Environment] Issue on <OS> <version>`

Include the output from the commands above and a description of
any issues encountered.

---

## CI Matrix

The full test suite runs automatically on every push and PR:

```yaml
os: ubuntu-latest
python: ["3.9", "3.10", "3.11", "3.12"]
```

View live CI status:
`https://github.com/law4percent/tree2guide/actions`

Windows and macOS CI will be added in a future release.
See [contributing](contributing.md) if you'd like to help expand the matrix.