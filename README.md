# tree2guide

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/law4percent/tree2guide/blob/main/LICENSE)
[![Python](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/)
[![CI](https://github.com/law4percent/tree2guide/actions/workflows/ci.yml/badge.svg)](https://github.com/law4percent/tree2guide/actions)
[![PyPI](https://img.shields.io/pypi/v/tree2guide)](https://pypi.org/project/tree2guide/)

**Understand your project's structure in seconds.**

Generate clean project trees, AI-ready summaries, and reusable documentation from any directory — all with zero dependencies.

**Author:** Lawrence Roble ([@law4percent](https://github.com/law4percent))
Open-source, MIT licensed. Contributions, issues, and pull requests are welcome.

---

## Why this exists

I'm a solo developer and self-learner. I don't always have time to study every architectural principle before I start building. What I *can* do is look at the shape of my own project.

**tree2guide** is the tool I built for that — a quick way to visualize my folder structure, notice when something's drifting into spaghetti, and decide for myself whether I'm actually following good separation of concerns, or just telling myself I am.

It turned out to be genuinely useful for other things too — documentation, onboarding, PR descriptions, AI prompts — so it grew into a general-purpose tool. But that's not why it exists. It exists to help developers like me catch bad structure early, without needing to be an expert first.

> tree2guide starts as a project structure generator, but its long-term vision is to become the foundation for project understanding — providing structured representations that can power documentation, analysis, automation, and intelligent developer tools.

---

## Why not just use `tree`?

| Feature | `tree` | tree2guide |
|---|:---:|:---:|
| Markdown output | ❌ | ✅ |
| HTML output (collapsible) | ❌ | ✅ |
| JSON output | ❌ | ✅ |
| YAML output | ❌ | ✅ |
| AI-ready summary | ❌ | ✅ |
| `.tree2ignore` (gitignore-style) | ❌ | ✅ |
| Python library API | ❌ | ✅ |
| Cross-platform | ⚠️ | ✅ |
| Zero dependencies | N/A | ✅ |

---

## Example Output

Running `tree2guide src --stdout`:

```
src/
├── tree2guide/
│   ├── renderers/
│   │   ├── __init__.py
│   │   ├── html.py
│   │   ├── json_renderer.py
│   │   ├── llm.py
│   │   ├── markdown.py
│   │   ├── text.py
│   │   └── yaml_renderer.py
│   ├── __init__.py
│   ├── cli.py
│   ├── ignore.py
│   ├── llm.py
│   └── scanner.py
```

Running `tree2guide . --llm --stdout`:

```
============================================================
PROJECT STRUCTURE SUMMARY: tree2guide
============================================================

DETECTED STACK / LANGUAGE:
  - Python (pyproject.toml)

SIZE:
  Files      : 18
  Directories: 4

TOP-LEVEL LAYOUT:
  Directories:
    src/
    tests/
    docs/
  Files:
    pyproject.toml
    README.md
    LICENSE

NOTABLE FLAGS:
  - Tests directory present
  - GitHub Actions / workflows present
  - LICENSE file present
  - CHANGELOG present
```

---

## Philosophy

tree2guide follows a few simple principles:

- **One scan, many outputs.** The filesystem is walked once; any renderer can consume the result.
- **Zero third-party dependencies.** Always. `pip install tree2guide` is instant.
- **Human-readable first.** Markdown is the default because humans read it everywhere.
- **AI-ready by design.** The `--llm` flag produces structured output optimised for AI context windows.
- **CLI and library.** Every feature available on the command line is also available as a Python API.
- **Never reads file contents.** Only structure and filenames — your code stays on your machine.

---

## Privacy

tree2guide operates entirely on your local machine.

It **does**:
- ✅ Read directory structure and filenames
- ✅ Apply ignore rules
- ✅ Generate output locally

It **does not**:
- ❌ Read file contents
- ❌ Upload anything
- ❌ Require an internet connection
- ❌ Collect telemetry
- ❌ Send data to any AI service

---

## Installation

```bash
pip install tree2guide
```

Requires Python 3.9+, no other dependencies. Installs a `tree2guide` command directly — no `python` prefix needed.

### Development setup (for contributors)

**macOS / Linux**
```bash
cd tree2guide
python3 -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
```

**Windows**
```bat
cd tree2guide
python -m venv venv
venv\Scripts\activate
pip install -e ".[dev]"
```

---

## Quick Start

```bash
# Markdown output (default) — writes docs_tree.md
tree2guide docs

# Plain text
tree2guide . --format text

# JSON
tree2guide . --format json

# Self-contained HTML with collapsible folders
tree2guide . --format html

# AI-ready project summary (no network call, no API key)
tree2guide . --llm

# Print to stdout instead of writing a file
tree2guide . --stdout

# Pipe to clipboard
tree2guide . --stdout | pbcopy      # macOS
tree2guide . --stdout | clip        # Windows
```

---

## Command Reference

```bash
tree2guide <target_folder> [options]
```

| Flag | Description |
|---|---|
| `-o`, `--output` | Output file path (default: `<folder>_tree.<ext>` based on format) |
| `--exclude-file` | Use a specific exclude file instead of auto-detecting `.tree2ignore` |
| `--title` | Add a heading above the tree |
| `--no-footer` | Omit the author/license footer (markdown and html only) |
| `--stdout` | Print to stdout instead of writing a file |
| `--format {markdown,text,json,yaml,html,llm}` | Output format (default: `markdown`) |
| `--llm` | Shorthand for `--format llm` — AI-friendly project summary |
| `--max-depth N` | Limit recursion depth |
| `--dirs-only` | Only show directories |
| `--files-only` | Only show files (directories shown as scaffolding only) |
| `--no-hidden` | Skip dotfiles/dotfolders without needing `.tree2ignore` entries |
| `--sort {dirs-first,files-first,alpha}` | Sort order within each folder (default: `dirs-first`) |

Symlinks are rendered as `name -> target` and never followed — avoids infinite loops.

### Default output filenames

| Format | Output file |
|---|---|
| `markdown` | `<folder>_tree.md` |
| `text` | `<folder>_tree.txt` |
| `json` | `<folder>_tree.json` |
| `yaml` | `<folder>_tree.yaml` |
| `html` | `<folder>_tree.html` |
| `llm` | `<folder>_llm.txt` |

---

## The `.tree2ignore` file

### The #1 rule: where it goes

**`.tree2ignore` must sit directly inside the folder you pass as the target.**
Patterns are written relative to that folder — never include the target folder's name as a prefix.

```bash
# .tree2ignore lives at docs/.tree2ignore
tree2guide docs
```

```
# correct — relative to docs/
api
_drafts

# wrong — only correct if you ran: tree2guide .
docs/api
docs/_drafts
```

### Pattern syntax (real `.gitignore` rules)

| Pattern | Meaning |
|---|---|
| `build` | Matches a file or folder named `build` at any depth |
| `build/` | Same, but only matches directories |
| `/build` | Matches `build` only at the root of the target (anchored) |
| `*.log` | Matches all files ending in `.log`, anywhere |
| `**/android/key.properties` | Matches that exact path at any depth |
| `!keep-this` | Negates — re-includes something an earlier rule excluded |
| `# comment` | Ignored |

Patterns evaluate top to bottom — later rules override earlier ones, same as Git.

### Whitelist example

Show only `admin/`, hide everything else:

```
*
!admin
!admin/**
```

### Copy your `.gitignore` directly

The matching engine reimplements Git's rules exactly — copy your `.gitignore` into `.tree2ignore` and it will behave identically.

---

## Defaults (always excluded, no setup needed)

- `.git`
- `.tree2ignore`
- `__pycache__`
- `*.pyc`
- `.DS_Store`

---

## Library API

`tree2guide` works as an importable library, not just a CLI:

```python
import tree2guide
from pathlib import Path

root = Path("./my-project").resolve()
patterns = tree2guide.load_exclude_patterns(root / tree2guide.EXCLUDE_FILENAME)
matcher = tree2guide.ExcludeMatcher(patterns)

# Build the tree once
tree = tree2guide.build_node_tree(root, matcher)

# Render to any format
print(tree2guide.render_markdown(tree, title="My Project"))
print(tree2guide.render_text(tree))
print(tree2guide.render_json(tree))
print(tree2guide.render_yaml(tree))
print(tree2guide.render_html(tree, title="My Project"))
print(tree2guide.render_llm(tree, title="My Project"))

# Get the heuristic summary directly
summary = tree2guide.analyze(tree)
print(summary.detected_stack)
print(summary.file_count, summary.dir_count)
print(summary.notable_flags)
```

### Public API surface

| Name | Description |
|---|---|
| `build_node_tree(root, matcher, options=None)` | Scan filesystem → `TreeNode` |
| `build_tree(root, matcher, options=None)` | Backward-compatible wrapper → `list[str]` |
| `TreeNode` | Internal tree model (dataclass) |
| `TreeOptions` | Scanner options (max_depth, dirs_only, sort, etc.) |
| `ExcludeMatcher` | Evaluates `.tree2ignore` patterns |
| `GitignoreRule` | Single compiled pattern rule |
| `load_exclude_patterns(path)` | Parse a `.tree2ignore` file |
| `analyze(node)` | Heuristic analysis → `LlmSummary` |
| `LlmSummary` | Detected stack, file/dir counts, notable flags |
| `render_markdown(tree, ...)` | Markdown string |
| `render_text(tree, ...)` | Plain text string |
| `render_json(tree)` | JSON string |
| `render_yaml(tree)` | YAML string |
| `render_html(tree, ...)` | Self-contained HTML string |
| `render_llm(tree, ...)` | LLM-optimised plain text string |

---

## Project Structure

```
tree2guide/
├── .github/
│   └── workflows/
│       └── ci.yml
├── docs/                        # GitHub Pages docs site
│   ├── _config.yml
│   ├── index.md
│   ├── installation.md
│   ├── quickstart.md
│   ├── tree2ignore.md
│   ├── cli.md
│   ├── examples.md
│   ├── api.md
│   └── contributing.md
├── src/
│   └── tree2guide/
│       ├── __init__.py          # public API surface
│       ├── cli.py               # argparse + entry point
│       ├── ignore.py            # GitignoreRule, ExcludeMatcher
│       ├── llm.py               # analyze(), LlmSummary
│       ├── scanner.py           # build_node_tree(), TreeNode, TreeOptions
│       └── renderers/
│           ├── __init__.py
│           ├── html.py
│           ├── json_renderer.py
│           ├── llm.py
│           ├── markdown.py
│           ├── text.py
│           └── yaml_renderer.py
├── tests/
│   ├── test_ignore.py
│   ├── test_llm.py
│   ├── test_markdown_renderer.py
│   ├── test_renderers.py
│   └── test_scanner.py
├── CHANGELOG.md
├── LICENSE
├── README.md
└── pyproject.toml
```

Architecture: **Scanner → Tree Model → Renderer**. The scanner builds a `TreeNode` once; each renderer transforms the same object into a different format. Adding a new output format means writing a new renderer — no changes to the scanner or CLI needed.

---

## Troubleshooting

**"No exclude file found at .../.tree2ignore"**
→ `.tree2ignore` must be directly inside the folder you passed as the target.

**Patterns aren't excluding anything**
→ Check for a stray prefix. If you ran `tree2guide docs`, write `api` not `docs/api`.

**I want to exclude everything except one folder**
```
*
!keepme
!keepme/**
```

**`--stdout` produces garbled characters on Windows**
→ Pipe directly to clipboard instead: `tree2guide . --stdout | clip`

---

## Contributing

Pull requests, feature ideas, and bug reports are welcome.
See [CONTRIBUTING](https://github.com/law4percent/tree2guide?tab=contributing-ov-file) for the full guide, architecture walkthrough, and how to add a new renderer or stack signal.

Open stretch goals:
- Browser playground (Pyodide/WASM)
- Interactive HTML viewer from JSON output
- `--format csv` — flat path list with type column
- File size annotations
- Character class patterns in `.tree2ignore` (`[abc]`, `[!abc]`)
- Windows CI in the test matrix

---

## License

MIT — see [LICENSE](LICENSE) for details.

---

*Built and maintained by [Lawrence Roble](https://github.com/law4percent).*