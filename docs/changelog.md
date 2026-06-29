# Changelog

All notable changes to tree2guide are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
Versioning follows [Semantic Versioning](https://semver.org/).

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