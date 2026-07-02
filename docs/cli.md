# CLI Reference

## Usage

```bash
tree2guide <target> [options]
```

`<target>` is the path to the folder you want to scan. It can be relative or absolute.

---

## Flags

### Output

| Flag | Default | Description |
|---|---|---|
| `-o`, `--output <path>` | `<folder>_tree.<ext>` | Write output to a specific file path |
| `--stdout` | off | Print to stdout instead of writing a file |
| `--format <fmt>` | `markdown` | Output format — see [Formats](#formats) below |
| `--llm` | off | Shorthand for `--format llm` |
| `--title <text>` | none | Add a title above the tree |
| `--no-footer` | off | Omit the attribution footer (markdown and html only) |

### Filtering

| Flag | Default | Description |
|---|---|---|
| `--exclude-file <path>` | `<target>/.tree2ignore` | Use a specific exclude file |
| `--max-depth <N>` | unlimited | Stop recursing after N directory levels |
| `--dirs-only` | off | Show only directories, no files |
| `--files-only` | off | Show only files (parent dirs shown as scaffolding) |
| `--no-hidden` | off | Skip dotfiles and dotfolders |

`--dirs-only` and `--files-only` are mutually exclusive.

### Display

| Flag | Default | Description |
|---|---|---|
| `--sort <mode>` | `dirs-first` | Sort order within each folder |

Sort modes:

| Mode | Behaviour |
|---|---|
| `dirs-first` | Directories before files, each group alphabetical (default) |
| `files-first` | Files before directories, each group alphabetical |
| `alpha` | Strict alphabetical — ignores whether an entry is a file or directory |

### Other

| Flag | Default | Description |
|---|---|---|
| `--no-progress` | off | Suppress scan progress and completion telemetry on large directories |
| `--version` | — | Print the installed version and exit |

---

## Scan awareness

On large directories, `tree2guide` prints periodic progress and a completion
summary — always to **stderr**, never stdout, so `--stdout | your-tool`
piping is never affected:

```
Scanning... 12,430 files, 2,105 dirs
Scanning... 91,202 files, 8,340 dirs
Scan complete. Files: 227,886, Directories: 13,415, Elapsed: 18.2s
```

Progress is gated on elapsed wall-clock time (roughly once per second), not
entry count — a fast scan of a small project prints nothing extra at all.
Pass `--no-progress` to suppress this entirely, including the final summary.

---

## Formats

### `markdown` (default)

Wraps the tree in a fenced code block. Includes an optional title heading and attribution footer. Output file extension: `.md`.

```bash
tree2guide . --format markdown
tree2guide . --format markdown --title "Project Layout" --no-footer
```

### `text`

Plain text — same connector characters as markdown but no code fences, no heading syntax, no footer. Useful for terminal output and non-markdown tools. Extension: `.txt`.

```bash
tree2guide . --format text
tree2guide . --format text --stdout
```

### `json`

Structured JSON with a stable, machine-readable shape. Extension: `.json`.

```json
{
  "name": "src",
  "type": "directory",
  "children": [
    { "name": "main.py", "type": "file" },
    { "name": "api", "type": "directory", "children": [] }
  ]
}
```

Symlinks have `"type": "symlink"` and a `"target"` key. Zero third-party dependencies — serialized with the standard `json` module.

```bash
tree2guide . --format json
tree2guide . --format json --stdout | python -m json.tool
```

### `yaml`

Same structure as JSON, output as YAML. Hand-serialized — no PyYAML or other dependency required. Extension: `.yaml`.

```bash
tree2guide . --format yaml
```

### `html`

Self-contained HTML page with:
- Collapsible folder nodes (click to expand/collapse)
- "Expand all" / "Collapse all" buttons
- Dark theme, monospace tree, works fully offline
- Optional title `<h1>` and attribution footer

Extension: `.html`. No external resources — the file works without an internet connection.

```bash
tree2guide . --format html
tree2guide . --format html --title "My Project" -o ./docs/structure.html
```

### `llm`

AI-consumption-friendly plain-text summary. Designed for pasting into an LLM context window. No markdown fences, no ambiguity. Extension: `_llm.txt`.

Includes:
- **Detected stack** — language/framework signals found in filenames (`pyproject.toml`, `package.json`, `go.mod`, `Cargo.toml`, `pubspec.yaml`, `Dockerfile`, and 30+ more)
- **Size** — total file and directory counts
- **Top-level layout** — immediate children of the root at a glance
- **Notable flags** — tests directory, CI config, `.env.example`, `LICENSE`, `CHANGELOG`, pre-commit hooks, and more
- **Full directory tree** — same tree as all other formats

No network call, no API key, no cost.

```bash
tree2guide . --llm
tree2guide . --llm --stdout   # pipe directly into an AI prompt
```

---

## Default output filenames

| Format | Default output filename |
|---|---|
| `markdown` | `<folder>_tree.md` |
| `text` | `<folder>_tree.txt` |
| `json` | `<folder>_tree.json` |
| `yaml` | `<folder>_tree.yaml` |
| `html` | `<folder>_tree.html` |
| `llm` | `<folder>_llm.txt` |

All files are written to the **current working directory**, not the target folder.

---

## Symlinks

Symlinks are detected automatically and rendered as `name -> target` instead of being followed or recursed into. This avoids infinite loops and keeps the tree honest about what's a link versus a real directory.

---

## Exit codes

| Code | Meaning |
|---|---|
| `0` | Success |
| `1` | Error (invalid target path, etc.) |