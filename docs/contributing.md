# Contributing

Contributions, issues, and pull requests are welcome. This is an open-source project under the MIT license.

## Getting started

```bash
git clone https://github.com/law4percent/tree2guide.git
cd tree2guide/tree2guide_pkg
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -e ".[dev]"
```

Run the tests:

```bash
pytest
```

All 80 tests should pass. If any fail before you've changed anything, please open an issue.

## Project structure

```
tree2guide_pkg/
├── src/
│   └── tree2guide/
│       ├── __init__.py        # public API surface
│       ├── cli.py             # argument parsing, entry point
│       ├── ignore.py          # GitignoreRule, ExcludeMatcher
│       ├── scanner.py         # build_node_tree(), TreeNode, TreeOptions
│       ├── llm.py             # analyze(), LlmSummary — heuristic detection
│       └── renderers/
│           ├── markdown.py    # --format markdown (default)
│           ├── text.py        # --format text
│           ├── json_renderer.py
│           ├── yaml_renderer.py
│           ├── html.py        # --format html — collapsible page
│           └── llm.py         # --format llm / --llm
├── tests/
│   ├── test_ignore.py
│   ├── test_scanner.py
│   ├── test_markdown_renderer.py
│   ├── test_renderers.py      # text, json, yaml, html
│   └── test_llm.py            # analyze() + render_llm()
├── docs/                      # this documentation
├── pyproject.toml
├── CHANGELOG.md
└── README.md
```

The architecture follows a **Scanner → Tree Model → Renderer** pipeline:

1. `ignore.py` compiles exclusion patterns
2. `scanner.py` walks the filesystem **once** and builds a `TreeNode` tree
3. Any renderer transforms that same `TreeNode` into its output format
4. `llm.py` inspects the `TreeNode` for heuristics — no second filesystem pass

## Adding a new output format

1. Create `src/tree2guide/renderers/myformat.py` with a `render_myformat(tree: TreeNode) -> str` function
2. Add it to `_FORMAT_EXTENSIONS` and `_render()` in `cli.py`
3. Export it from `__init__.py`
4. Add tests in `tests/test_renderers.py`
5. Document it in `docs/cli.md` and `docs/api.md`

## Adding new `--llm` stack signals

Open `src/tree2guide/llm.py` and add entries to `_STACK_SIGNALS` or `_NOTABLE_FLAGS`:

```python
_STACK_SIGNALS: list[tuple[str, str]] = [
    ...
    ("deno.json", "Deno / TypeScript"),   # new entry
]
```

Pattern matching supports `*` wildcards at the start or end (e.g. `"*.csproj"`).

## Code style

- Type hints throughout (`list[str]`, `str | None`, etc.)
- Docstrings on all public functions and classes
- No third-party dependencies — the package must stay zero-dep for users
- Dev dependencies (`pytest`) go in `[project.optional-dependencies] dev`

## Running a subset of tests

```bash
pytest tests/test_llm.py           # just the LLM tests
pytest tests/test_ignore.py -v     # verbose
pytest -k "test_detects"           # by name pattern
```

## Ideas for contributions

- Additional stack signals in `_STACK_SIGNALS` (new languages, frameworks, build tools)
- Additional notable flags in `_NOTABLE_FLAGS`
- Broader `.gitignore` edge-case coverage (character classes `[abc]`, escaped special characters)
- File size or entry count annotations per folder
- `--format csv` renderer
- Windows CI coverage
- A browser playground (Pyodide/WASM) — see the roadmap's Phase 5 stretch goal

## Submitting a PR

1. Fork the repo and create a branch: `git checkout -b feat/my-thing`
2. Make your changes and add tests
3. Run `pytest` — all tests must pass
4. Open a pull request with a clear description of what changed and why

## Reporting a bug

Open an issue at [github.com/law4percent/tree2guide/issues](https://github.com/law4percent/tree2guide/issues) with:
- Your Python version (`python --version`)
- Your OS
- The command you ran
- What you expected vs what happened