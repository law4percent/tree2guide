# API Reference

`tree2guide` is usable as a library, not just a CLI. Import it and call the same functions the CLI uses internally.

```python
import tree2guide
```

---

## Scanner

### `build_node_tree(root, matcher, options=None) -> TreeNode`

The primary scanner function. Walks the filesystem once and returns a `TreeNode` tree. All renderers consume this.

```python
from pathlib import Path
import tree2guide

root = Path("./my-project").resolve()
patterns = tree2guide.load_exclude_patterns(root / tree2guide.EXCLUDE_FILENAME)
matcher = tree2guide.ExcludeMatcher(patterns)
options = tree2guide.TreeOptions(max_depth=3, no_hidden=True)

node = tree2guide.build_node_tree(root, matcher, options)
```

### `build_tree(root, matcher, options=None) -> list[str]`

Backward-compatible wrapper. Returns the same connector-prefixed display lines the old API produced. Internally calls `build_node_tree()` and `render_lines()`.

---

## TreeNode

```python
@dataclass
class TreeNode:
    name: str
    is_dir: bool
    is_symlink: bool = False
    symlink_target: str | None = None
    children: list[TreeNode] = ...
```

The internal tree model. One node per filesystem entry. Renderers walk this structure — they never touch the filesystem themselves.

---

## TreeOptions

```python
@dataclass
class TreeOptions:
    max_depth: int | None = None      # None = unlimited
    dirs_only: bool = False
    files_only: bool = False
    no_hidden: bool = False
    sort: str = "dirs-first"          # "dirs-first" | "files-first" | "alpha"
```

---

## Ignore / exclusion

### `load_exclude_patterns(exclude_file: Path) -> list[str]`

Reads a `.tree2ignore`-style file and returns a list of pattern strings, prefixed with the built-in defaults. Safe to call when the file doesn't exist — returns only the defaults.

### `ExcludeMatcher(patterns: list[str])`

Compiles a list of pattern strings into `GitignoreRule` objects.

```python
matcher = tree2guide.ExcludeMatcher(["node_modules", "*.pyc", "!keep.pyc"])
matcher.is_excluded("node_modules", is_dir=True)   # True
matcher.is_excluded("keep.pyc", is_dir=False)       # False
```

#### `matcher.is_excluded(rel_path: str, is_dir: bool) -> bool`

Returns `True` if the relative path should be excluded. `rel_path` uses forward slashes regardless of OS.

### `GitignoreRule(raw: str)`

A single compiled rule. Exposed for advanced use; most callers use `ExcludeMatcher` directly.

### `EXCLUDE_FILENAME`

The string `".tree2ignore"` — the default exclude filename.

### `DEFAULT_EXCLUDES`

The list of patterns always applied before any `.tree2ignore` content:
```python
[".git", ".tree2ignore", "__pycache__", "*.pyc", ".DS_Store"]
```

---

## Renderers

All renderers accept a `TreeNode` and return a `str` with a trailing newline.

### `render_markdown(tree, title=None, include_footer=True) -> str`

Fenced code block, optional `# Title` heading, optional attribution footer.

Also accepts a `list[str]` for backward compatibility.

### `render_text(tree, title=None) -> str`

Plain text, no fences, title as a plain line (no `#` prefix).

### `render_json(tree, indent=2) -> str`

Pretty-printed JSON. Shape:
```json
{
  "name": "src",
  "type": "directory",
  "children": [
    { "name": "main.py", "type": "file" },
    { "name": "link", "type": "symlink", "target": "/some/path" }
  ]
}
```

### `render_yaml(tree) -> str`

Same structure as JSON, output as YAML. No PyYAML dependency.

### `render_html(tree, title=None, include_footer=True) -> str`

Self-contained HTML page. Collapsible folders, expand/collapse all, dark theme, works offline.

### `render_llm(tree, title=None) -> str`

AI-friendly plain-text summary. Calls `analyze()` internally. No network call, no API key.

---

## LLM analysis

### `analyze(node: TreeNode) -> LlmSummary`

Inspects a `TreeNode` tree and returns a structured heuristic summary. Single pass over the already-built tree — no extra filesystem I/O.

```python
node = tree2guide.build_node_tree(root, matcher)
summary = tree2guide.analyze(node)

print(summary.detected_stack)   # ["Python (pyproject.toml)", "Docker"]
print(summary.file_count)       # 34
print(summary.dir_count)        # 8
print(summary.notable_flags)    # ["Tests directory present", ...]
print(summary.top_level_dirs)   # ["src/", "tests/", "docs/"]
print(summary.top_level_files)  # ["pyproject.toml", "README.md"]
```

### `LlmSummary`

```python
@dataclass
class LlmSummary:
    detected_stack: list[str]    # detected language/framework labels
    file_count: int              # total files (recursive)
    dir_count: int               # total directories (recursive)
    notable_flags: list[str]     # human-readable flag messages
    top_level_dirs: list[str]    # immediate child directories (with trailing /)
    top_level_files: list[str]   # immediate child files
```

---

## Version

```python
tree2guide.__version__   # "4.0.0"
```