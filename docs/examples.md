# Examples

## Document a project's structure in a README

```bash
cd my-project
tree2guide . --stdout | pbcopy   # macOS — paste straight into your README
```

Or write a file and embed it:

```bash
tree2guide . -o docs/structure.md
```

## Scan only the source tree, skip everything else

`.tree2ignore` at `my-project/.tree2ignore`:

```gitignore
node_modules
.venv
dist
build
*.log
*.pyc
__pycache__
```

Then:

```bash
tree2guide .
```

## Show only the folder skeleton

Useful for getting a high-level architecture view without file noise:

```bash
tree2guide . --dirs-only
```

## Cap depth for a large monorepo

```bash
tree2guide . --max-depth 2
```

## Feed a project summary to an AI

```bash
tree2guide . --llm --stdout
# paste the output at the top of your AI prompt
```

Example output:

```
============================================================
PROJECT STRUCTURE SUMMARY: my-api
============================================================

DETECTED STACK / LANGUAGE:
  - Python (pyproject.toml)
  - Docker

SIZE:
  Files      : 34
  Directories: 8

TOP-LEVEL LAYOUT:
  Directories:
    src/
    tests/
    docs/
  Files:
    pyproject.toml
    Dockerfile
    README.md

NOTABLE FLAGS:
  - Tests directory present
  - Docker present
  - LICENSE file present
  - CHANGELOG present

============================================================
FULL DIRECTORY TREE:
============================================================

my-api/
├── src/
│   ├── api/
│   │   ├── routes.py
│   │   └── models.py
│   └── main.py
├── tests/
│   └── test_routes.py
...
```

## Generate an interactive HTML tree to share with your team

```bash
tree2guide . --format html --title "Project Structure" -o share/structure.html
```

Open `structure.html` in any browser — folders are collapsible, no server needed.

## Whitelist — show only one folder

Show **only** `src/` and exclude everything else, using `.tree2ignore`:

```gitignore
*
!src
!src/**
```

```bash
tree2guide .
```

## Use as a library in a script

```python
import tree2guide
from pathlib import Path

root = Path("./my-project").resolve()
patterns = tree2guide.load_exclude_patterns(root / tree2guide.EXCLUDE_FILENAME)
matcher = tree2guide.ExcludeMatcher(patterns)
options = tree2guide.TreeOptions(max_depth=3, no_hidden=True)

node = tree2guide.build_node_tree(root, matcher, options)

# Render to different formats from the same scan
print(tree2guide.render_markdown(node, title="My Project"))
print(tree2guide.render_json(node))

# Get heuristic analysis without re-scanning
summary = tree2guide.analyze(node)
print(f"Detected: {summary.detected_stack}")
print(f"Files: {summary.file_count}, Dirs: {summary.dir_count}")
```

## Copy your `.gitignore` as a starting point

```bash
cp .gitignore .tree2ignore
tree2guide .
```

Both files use identical syntax — anything that works in `.gitignore` works in `.tree2ignore`.

## Output JSON for downstream tooling

```bash
tree2guide . --format json --stdout | jq '.children[].name'
```

## Sort strictly alphabetically

```bash
tree2guide . --sort alpha
```

## Skip dotfiles without editing `.tree2ignore`

```bash
tree2guide . --no-hidden
```

## Point to a different exclude file

```bash
tree2guide . --exclude-file ./ci/scan.ignore
```

Useful when you want different exclusion rules for CI versus local use, without touching the default `.tree2ignore`.