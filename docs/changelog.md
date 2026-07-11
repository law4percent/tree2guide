# Changelog

All notable changes to tree2guide are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
Versioning follows [Semantic Versioning](https://semver.org/).

---

## [1.2.2] — 2026-07-11

### Fixed
- `.tree2ignore` whitelist rules meant to re-include one top-level folder
  (e.g. `!reports`, `!assets`) could unintentionally resurrect an unrelated
  *excluded* directory elsewhere in the tree if any of its descendants
  happened to share that folder's name (e.g. an excluded `build/` was
  still shown because it contained `build/reports` and
  `build/unit_test_assets/assets`). The scanner recursed into every
  directory before checking exclusion, then kept an excluded parent
  visible whenever a descendant survived — diverging from Git's actual
  behavior, which never descends into an already-excluded directory.
  `build_node_tree()` now skips excluded directories immediately,
  matching Git.

---

## [1.2.1] — 2026-07-11

### Fixed
- `tree2guide <target>` (the default, file-writing mode — i.e. without
  `--stdout`) crashed with `UnicodeEncodeError` on Windows terminals
  using a non-UTF-8 codepage (e.g. `cp1252`), because the `✅ Tree
  written to: ...` success message was printed without an explicit
  encoding. The tree file itself was already written correctly at that
  point, so the crash only obscured a successful run — but it returned
  exit code 1 and dumped a traceback instead of the success message.
  This is distinct from the `--stdout` `UnicodeEncodeError` fixed in
  v1.0.0 (which only covered piped stdout, not the default file-writing
  path). `main()` now reconfigures `sys.stdout`/`sys.stderr` to UTF-8 on
  startup so this can't happen regardless of console codepage.

---

## [1.2.0] — 2026-07-02

### Added
- `--version` flag — `tree2guide --version` now prints the version instead
  of crashing with a missing-argument error
- AI tooling notable flags — detects `.claude/`, `.cursor/`, `.windsurf/`,
  `.roo/`, `.specify/`, `.roomodes`, `.maestro/`, `.githooks/` in addition
  to the previously-existing `CLAUDE.md`, `AGENTS.md`, `.cursorrules`
- Generic `PHP MVC structure` stack signal — `Controller/`, `Model/`,
  `View/` are recognized as a weak, generic MVC-framework signal without
  being misattributed to CakePHP specifically, since these directory names
  are shared by CodeIgniter, Yii, and other PHP MVC frameworks
- Scan progress and completion telemetry for large directories — periodic
  `Scanning... N files, N dirs` and a final `Scan complete.` summary,
  printed to stderr only (never stdout, so `--stdout` piping is
  unaffected). Gated on elapsed wall-clock time, not entry count, so fast
  scans of small projects print nothing extra. `--no-progress` suppresses
  this entirely. `build_node_tree()` gained an optional `on_progress`
  callback parameter (`None` by default, zero effect on existing callers)
- Number formatting — file and directory counts in `--llm` output now use
  comma separators for readability on large projects (`227886` → `227,886`)

### Fixed
- `_STACK_SIGNALS` patterns containing a path separator (e.g. `bin/cake`,
  `config/app.php`, `bootstrap/app.php`, `bin/console`, `config/routes.rb`,
  `src/main/java`, and 9 others) could never match anything, because stack
  detection only ever compared against bare file/directory names, never
  relative paths. These are now matched against each entry's actual
  relative path, restoring the CakePHP, Laravel, Symfony, Ruby on Rails,
  Java/Kotlin, and Flutter signals that depend on them — several of which
  are the highest-confidence (weight 5) signal for their framework
- `cli.py` used `str | None` / `list[str] | None` type-hint syntax without
  `from __future__ import annotations`, which would raise `TypeError` on
  Python 3.9 the moment the module was imported. No test previously
  imported `tree2guide.cli`, so this went undetected by CI despite the 3.9
  job reporting green; new CLI tests now cover this module directly
- Scan progress counts (added in this release) included symlinks, while
  the final completion summary and `--llm`'s SIZE section both excluded
  them — the same long-standing convention used since v1.0.0. On a
  project with many symlinks (e.g. Python venvs, `node_modules/.bin`),
  the live progress numbers could run noticeably ahead of the final
  count. Progress now excludes symlinks, matching every other counting
  function in the codebase

---

## [1.1.0] — 2026-06-29

### Added
- Weighted stack detection in `--llm` mode — primary language now ranks
  correctly in polyglot monorepos instead of first-match-wins
- Expanded framework signals: CakePHP, Laravel, Symfony, WordPress,
  Django, FastAPI, Flask, Celery, Ruby on Rails, Spring Boot, NestJS,
  Remix, Gatsby, Astro, React Native, Expo, Prisma, Drizzle, Knex,
  Nx, Lerna, Turborepo, Kubernetes, Helm, Terraform, Ansible, and more
- New notable flags: e2e/, SECURITY.md, CLAUDE.md, AGENTS.md,
  .cursorrules, .nvmrc, .python-version, CODEOWNERS, migrations/,
  seeds/, docs/, scripts/, infra/, Terraform, Kubernetes, Helm

### Fixed
- PHP/CakePHP projects no longer misidentified as Python when a
  stray requirements.txt exists deep in the codebase

---

## [1.0.0] — 2026-06-28

### Added
- `.gitignore`-compatible exclusion via hand-written `GitignoreRule` / `ExcludeMatcher` — zero dependencies
- Multi-format output: `--format {markdown,text,json,yaml,html,llm}`
- `--llm` shorthand flag — AI-ready project summary with stack detection, file counts, notable flags
- `--stdout`, `--max-depth`, `--dirs-only`, `--files-only`, `--no-hidden`, `--sort` CLI flags
- Symlink detection — renders `name -> target`, never followed
- Scanner → Tree Model → Renderer architecture (`TreeNode`, `TreeOptions`, `build_node_tree()`)
- Full library API — importable, not just CLI
- `render_markdown`, `render_text`, `render_json`, `render_yaml`, `render_html`, `render_llm`
- `analyze(node) -> LlmSummary` — rule-based heuristic project analysis
- 80 tests across `test_ignore`, `test_scanner`, `test_markdown_renderer`, `test_renderers`, `test_llm`
- GitHub Actions CI across Python 3.9–3.12
- Docs site under `docs/` ready for GitHub Pages

### Fixed
- `--stdout` on Windows raised `UnicodeEncodeError` when piping output containing
  box-drawing characters (`├`, `└`, `│`) to `clip` or other programs. Fixed by
  writing raw UTF-8 bytes directly to `sys.stdout.buffer`.
