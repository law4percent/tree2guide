# tree2guide

**See your project structure clearly enough to catch spaghetti code before it compounds.**

`tree2guide` scans any folder and outputs a clean, structured view of its contents — in Markdown, plain text, JSON, YAML, HTML, or an AI-ready summary. It uses a `.tree2ignore` file that follows the **exact same rules as `.gitignore`**, reimplemented in pure Python with zero third-party dependencies.

```bash
pip install tree2guide
tree2guide .
```

That's it. A `project_tree.md` appears in your current directory, ready to paste into a README, a design doc, or an AI prompt.

---

## Why it exists

I'm a solo developer and self-learner. I don't always have time to sit down and study every "Core Principle" or "Golden Rule" of software architecture before I start building.

What I *can* do is look at the shape of my own project. `tree2guide` is the tool I built for that — a quick way to visualize my folder structure, notice when something's drifting into spaghetti, and decide for myself whether I'm actually following good separation of concerns, or just telling myself I am.

It turned out to also be genuinely useful for documentation, onboarding, and PR descriptions — so it grew into a general-purpose tool. But that's not why it exists. It exists to help developers like me catch bad structure early, without needing to be an expert first.

**Author:** Lawrence Roble ([@law4percent](https://github.com/law4percent))
**License:** MIT — open source, contributions welcome.

---

## Highlights

- **Zero dependencies** — pure Python 3.9+, nothing to install beyond the package itself
- **Real `.gitignore` syntax** — copy your `.gitignore` straight into `.tree2ignore` and it works identically (`**`, anchoring, dir-only, negation)
- **Six output formats** — `markdown`, `text`, `json`, `yaml`, `html`, `llm`
- **`--llm` mode** — AI-friendly project summary with stack detection, file counts, and notable flags, no API key required
- **All the flags you'd expect** — `--max-depth`, `--dirs-only`, `--files-only`, `--no-hidden`, `--sort`, `--stdout`
- **Library API** — importable as `import tree2guide`, not just a CLI

---

## Quick links

- [Installation](installation.md)
- [Quick Start](quickstart.md)
- [`.tree2ignore` Guide](tree2ignore.md)
- [CLI Reference](cli.md)
- [Examples](examples.md)
- [API Reference](api.md)
- [Contributing](contributing.md)
- [Changelog](../CHANGELOG.md)