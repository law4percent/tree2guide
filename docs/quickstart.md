# Quick Start

## The basics

Point `tree2guide` at any folder:

```bash
tree2guide my-project
```

A file called `my-project_tree.md` is written to your current directory. Open it, paste it into a README, or feed it to an AI — it's ready to go.

## Scan your whole project

Run it from inside the project root, targeting `.` (the current directory):

```bash
cd my-project
tree2guide .
```

This scans everything under `my-project/`. Put a `.tree2ignore` file at `my-project/.tree2ignore` to exclude what you don't need.

## Print to stdout instead of a file

Pipe directly to your clipboard:

```bash
# macOS
tree2guide . --stdout | pbcopy

# Windows
tree2guide . --stdout | clip

# Linux (X11)
tree2guide . --stdout | xclip -selection clipboard
```

Or pipe into another tool:

```bash
tree2guide . --stdout | grep "\.py"
```

## Choose an output format

`tree2guide` supports six formats. Markdown is the default:

```bash
tree2guide . --format markdown   # default — fenced code block, ready to paste
tree2guide . --format text       # plain text, no fences
tree2guide . --format json       # structured {name, type, children} JSON
tree2guide . --format yaml       # same shape as JSON, hand-serialized
tree2guide . --format html       # self-contained page with collapsible folders
tree2guide . --format llm        # AI-friendly summary with stack detection
```

## Get an AI-ready project summary

The `--llm` flag (shorthand for `--format llm`) produces a structured plain-text summary designed for pasting into an AI prompt:

```bash
tree2guide . --llm
```

Output includes:
- Detected language/framework stack (Python, Node.js, Go, Rust, Flutter, Docker, and more)
- Total file and directory counts
- Top-level layout at a glance
- Notable flags (tests directory, CI config, `.env.example`, `LICENSE`, `CHANGELOG`, etc.)
- The full directory tree

No API key, no network call, no cost — all rule-based and instant.

## Add a title heading

```bash
tree2guide . --title "My Project Structure"
```

Adds `# My Project Structure` above the tree in markdown/html, or a plain label in text/llm output.

## Limit depth for large repos

```bash
tree2guide . --max-depth 3
```

Stops recursion after 3 levels — useful for getting a high-level overview of a large monorepo without drowning in detail.

## Skip hidden files

```bash
tree2guide . --no-hidden
```

Skips any file or folder whose name starts with `.` without needing `.tree2ignore` entries for them.

## Show only directories (or only files)

```bash
tree2guide . --dirs-only    # folder skeleton only
tree2guide . --files-only   # files only (parent dirs shown as scaffolding)
```

## Control sort order

```bash
tree2guide . --sort dirs-first    # default
tree2guide . --sort files-first
tree2guide . --sort alpha         # strict alphabetical, ignores type
```

## Use a custom output path

```bash
tree2guide . -o ./docs/structure.md
```

## Use a custom exclude file

```bash
tree2guide . --exclude-file ./ci/scan-rules.ignore
```

## Omit the footer

```bash
tree2guide . --no-footer
```

Removes the attribution line from markdown and HTML output.