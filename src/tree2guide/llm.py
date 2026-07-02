"""
tree2guide.llm — rule-based project heuristics for --llm mode.

Zero dependencies, zero network calls. All detection is done by inspecting
the names present in the TreeNode tree that the scanner already built —
no second filesystem pass is needed.

Produces a structured LlmSummary dataclass that the LLM renderer uses to
build its output.

v1.1.0 changes:
- Weighted scoring replaces first-match-wins stack detection
- Expanded framework signals (CakePHP, Laravel, Symfony, Django, Flask,
  FastAPI, Express, NestJS, Spring Boot, Rails, and more)
- Primary language now ranks correctly even in polyglot monorepos
"""

from __future__ import annotations
from dataclasses import dataclass, field
from tree2guide.scanner import TreeNode


# ---------------------------------------------------------------------------
# Detection tables
# ---------------------------------------------------------------------------

# Each entry: (pattern, label, weight)
# Weight reflects how strongly this signal identifies the stack.
# Higher weight = more specific / more authoritative signal.
#
# Scoring rules:
#   5 = framework-specific config (almost certain identification)
#   4 = primary language config or lockfile
#   3 = well-known framework directory or entry point
#   2 = supporting file (common but not exclusive)
#   1 = weak signal (present in many stacks)
#
# Final detected stack is sorted by total score descending.
# Labels are deduplicated — highest score wins per label.

_STACK_SIGNALS: list[tuple[str, str, int]] = [

    # -------------------------------------------------------------------------
    # PHP Frameworks (specific → generic)
    # -------------------------------------------------------------------------
    ("bin/cake",              "CakePHP",                  5),
    ("config/app.php",        "CakePHP",                  5),
    ("webroot",               "CakePHP",                  3),
    ("artisan",               "Laravel",                  5),
    ("bootstrap/app.php",     "Laravel",                  5),
    ("resources/views",       "Laravel",                  4),
    ("symfony.lock",          "Symfony",                  5),
    ("bin/console",           "Symfony",                  5),
    ("config/bundles.php",    "Symfony",                  5),
    ("wp-config.php",         "WordPress",                5),
    ("wp-content",            "WordPress",                4),
    ("wp-includes",           "WordPress",                4),
    ("index.php",             "PHP",                      2),
    ("composer.json",         "PHP / Composer",           4),
    ("composer.lock",         "PHP / Composer",           3),
    ("Controller",            "PHP MVC structure",        1),
    ("Model",                 "PHP MVC structure",        1),
    ("View",                  "PHP MVC structure",        1),

    # -------------------------------------------------------------------------
    # Python Frameworks (specific → generic)
    # -------------------------------------------------------------------------
    ("manage.py",             "Django",                   5),
    ("django",                "Django",                   4),
    ("settings.py",           "Django",                   3),
    ("wsgi.py",               "Django / WSGI",            3),
    ("asgi.py",               "Django / ASGI",            3),
    ("main.py",               "FastAPI",                  2),
    ("fastapi",               "FastAPI",                  4),
    ("app.py",                "Flask",                    2),
    ("flask",                 "Flask",                    4),
    ("celery.py",             "Celery",                   4),
    ("celeryconfig.py",       "Celery",                   4),
    ("alembic.ini",           "SQLAlchemy / Alembic",     4),
    ("pyproject.toml",        "Python",                   4),
    ("setup.py",              "Python",                   3),
    ("requirements.txt",      "Python",                   2),
    ("Pipfile",               "Python / Pipenv",          3),
    ("Pipfile.lock",          "Python / Pipenv",          3),
    ("poetry.lock",           "Python / Poetry",          4),

    # -------------------------------------------------------------------------
    # JavaScript / TypeScript Frameworks (specific → generic)
    # -------------------------------------------------------------------------
    ("next.config.js",        "Next.js",                  5),
    ("next.config.ts",        "Next.js (TypeScript)",     5),
    ("next.config.mjs",       "Next.js",                  5),
    ("nuxt.config.ts",        "Nuxt.js",                  5),
    ("nuxt.config.js",        "Nuxt.js",                  5),
    ("angular.json",          "Angular",                  5),
    ("svelte.config.js",      "SvelteKit",                5),
    ("svelte.config.ts",      "SvelteKit",                5),
    ("remix.config.js",       "Remix",                    5),
    ("gatsby-config.js",      "Gatsby",                   5),
    ("gatsby-config.ts",      "Gatsby",                   5),
    ("nest-cli.json",         "NestJS",                   5),
    ("vite.config.ts",        "Vite",                     4),
    ("vite.config.js",        "Vite",                     4),
    ("astro.config.mjs",      "Astro",                    5),
    ("astro.config.ts",       "Astro",                    5),
    ("expo",                  "Expo (React Native)",      4),
    ("app.json",              "React Native / Expo",      3),
    ("metro.config.js",       "React Native",             5),
    ("tsconfig.json",         "TypeScript",               4),
    ("package.json",          "Node.js / JavaScript",     3),
    ("package-lock.json",     "Node.js / npm",            2),
    ("yarn.lock",             "Node.js / Yarn",           3),
    ("pnpm-lock.yaml",        "Node.js / pnpm",           3),

    # -------------------------------------------------------------------------
    # Ruby / Rails
    # -------------------------------------------------------------------------
    ("Gemfile",               "Ruby",                     3),
    ("Gemfile.lock",          "Ruby",                     3),
    ("Rakefile",              "Ruby / Rake",              3),
    ("config/routes.rb",      "Ruby on Rails",            5),
    ("app/controllers",       "Ruby on Rails",            5),
    ("db/schema.rb",          "Ruby on Rails",            5),

    # -------------------------------------------------------------------------
    # Java / Kotlin / JVM
    # -------------------------------------------------------------------------
    ("pom.xml",               "Java / Maven",             4),
    ("build.gradle",          "Java / Gradle",            4),
    ("build.gradle.kts",      "Kotlin / Gradle",          5),
    ("gradlew",               "Java / Gradle",            3),
    ("src/main/java",         "Java",                     4),
    ("src/main/kotlin",       "Kotlin",                   4),
    ("src/main/resources",    "Java / Spring",            3),
    ("application.properties","Spring Boot",              5),
    ("application.yml",       "Spring Boot",              4),

    # -------------------------------------------------------------------------
    # Go
    # -------------------------------------------------------------------------
    ("go.mod",                "Go",                       5),
    ("go.sum",                "Go",                       4),
    ("main.go",               "Go",                       3),

    # -------------------------------------------------------------------------
    # Rust
    # -------------------------------------------------------------------------
    ("Cargo.toml",            "Rust / Cargo",             5),
    ("Cargo.lock",            "Rust / Cargo",             4),

    # -------------------------------------------------------------------------
    # C / C++
    # -------------------------------------------------------------------------
    ("CMakeLists.txt",        "C/C++ / CMake",            5),
    ("Makefile",              "C/C++ / Make",             2),
    ("configure.ac",          "C/C++ / Autotools",        5),
    ("conanfile.txt",         "C/C++ / Conan",            5),
    ("conanfile.py",          "C/C++ / Conan",            5),

    # -------------------------------------------------------------------------
    # Swift / iOS / macOS
    # -------------------------------------------------------------------------
    ("Package.swift",         "Swift / SPM",              5),
    ("*.xcodeproj",           "Xcode Project",            5),
    ("*.xcworkspace",         "Xcode Workspace",          5),
    ("Podfile",               "iOS / CocoaPods",          5),

    # -------------------------------------------------------------------------
    # Dart / Flutter
    # -------------------------------------------------------------------------
    ("pubspec.yaml",          "Dart / Flutter",           5),
    ("pubspec.lock",          "Dart / Flutter",           4),
    ("lib/main.dart",         "Flutter",                  5),
    ("android/app",           "Flutter (Android)",        4),
    ("ios/Runner",            "Flutter (iOS)",            4),

    # -------------------------------------------------------------------------
    # .NET / C# / F#
    # -------------------------------------------------------------------------
    ("*.csproj",              ".NET / C#",                5),
    ("*.fsproj",              ".NET / F#",                5),
    ("*.sln",                 ".NET Solution",            5),
    ("appsettings.json",      ".NET / ASP.NET Core",      4),
    ("Program.cs",            ".NET / C#",                4),

    # -------------------------------------------------------------------------
    # Elixir / Erlang
    # -------------------------------------------------------------------------
    ("mix.exs",               "Elixir / Mix",             5),
    ("mix.lock",              "Elixir / Mix",             4),
    ("rebar.config",          "Erlang / Rebar",           5),

    # -------------------------------------------------------------------------
    # Haskell
    # -------------------------------------------------------------------------
    ("stack.yaml",            "Haskell / Stack",          5),
    ("*.cabal",               "Haskell / Cabal",          5),

    # -------------------------------------------------------------------------
    # Scala
    # -------------------------------------------------------------------------
    ("build.sbt",             "Scala / SBT",              5),

    # -------------------------------------------------------------------------
    # Clojure
    # -------------------------------------------------------------------------
    ("project.clj",           "Clojure / Leiningen",      5),
    ("deps.edn",              "Clojure / deps.edn",       5),

    # -------------------------------------------------------------------------
    # Docker / Infrastructure
    # -------------------------------------------------------------------------
    ("Dockerfile",            "Docker",                   4),
    ("docker-compose.yml",    "Docker Compose",           4),
    ("docker-compose.yaml",   "Docker Compose",           4),
    ("docker-compose.prod.yml","Docker Compose",          4),
    ("k8s",                   "Kubernetes",               4),
    ("kubernetes",            "Kubernetes",               4),
    ("helm",                  "Helm (Kubernetes)",        5),
    ("Chart.yaml",            "Helm (Kubernetes)",        5),
    ("terraform",             "Terraform",                4),
    ("*.tf",                  "Terraform",                4),
    ("ansible",               "Ansible",                  4),
    ("playbook.yml",          "Ansible",                  4),

    # -------------------------------------------------------------------------
    # Mobile
    # -------------------------------------------------------------------------
    ("AndroidManifest.xml",   "Android (Native)",         5),
    ("build.gradle",          "Android / Gradle",         3),
    ("Info.plist",            "iOS (Native)",             5),

    # -------------------------------------------------------------------------
    # Database / ORM
    # -------------------------------------------------------------------------
    ("prisma",                "Prisma ORM",               5),
    ("schema.prisma",         "Prisma ORM",               5),
    ("drizzle.config.ts",     "Drizzle ORM",              5),
    ("knexfile.js",           "Knex.js",                  5),
    ("knexfile.ts",           "Knex.js",                  5),
    ("migrations",            "Database Migrations",      2),

    # -------------------------------------------------------------------------
    # Testing frameworks (notable but not primary stack)
    # -------------------------------------------------------------------------
    ("jest.config.js",        "Jest (Testing)",           3),
    ("jest.config.ts",        "Jest (Testing)",           3),
    ("vitest.config.ts",      "Vitest (Testing)",         3),
    ("vitest.config.js",      "Vitest (Testing)",         3),
    ("cypress.config.ts",     "Cypress (E2E Testing)",    3),
    ("cypress.config.js",     "Cypress (E2E Testing)",    3),
    ("playwright.config.ts",  "Playwright (E2E Testing)", 3),
    ("playwright.config.js",  "Playwright (E2E Testing)", 3),
    ("pytest.ini",            "pytest (Testing)",         3),
    ("conftest.py",           "pytest (Testing)",         3),

    # -------------------------------------------------------------------------
    # CI / CD
    # -------------------------------------------------------------------------
    (".github",               "GitHub Actions",           3),
    (".gitlab-ci.yml",        "GitLab CI",                4),
    ("Jenkinsfile",           "Jenkins CI",               4),
    (".circleci",             "CircleCI",                 4),
    ("azure-pipelines.yml",   "Azure Pipelines",          4),
    (".travis.yml",           "Travis CI",                4),

    # -------------------------------------------------------------------------
    # Monorepo tooling
    # -------------------------------------------------------------------------
    ("nx.json",               "Nx (Monorepo)",            5),
    ("lerna.json",            "Lerna (Monorepo)",         5),
    ("turbo.json",            "Turborepo (Monorepo)",     5),
    ("pnpm-workspace.yaml",   "pnpm Workspaces (Monorepo)", 5),
]

# Files/dirs whose presence is worth flagging
_NOTABLE_FLAGS: list[tuple[str, str]] = [
    (".env.example",            "Environment template (.env.example) present"),
    (".env",                    "Live .env file present (check it's gitignored!)"),
    ("tests",                   "Tests directory present"),
    ("test",                    "Test directory present"),
    ("__tests__",               "Jest-style __tests__ directory present"),
    ("spec",                    "Spec directory present"),
    ("e2e",                     "End-to-end tests directory present"),
    (".github",                 "GitHub Actions / workflows present"),
    (".gitlab-ci.yml",          "GitLab CI config present"),
    ("Jenkinsfile",             "Jenkins CI config present"),
    (".circleci",               "CircleCI config present"),
    ("azure-pipelines.yml",     "Azure Pipelines config present"),
    ("LICENSE",                 "LICENSE file present"),
    ("LICENSE.md",              "LICENSE file present"),
    ("CHANGELOG.md",            "CHANGELOG present"),
    ("CONTRIBUTING.md",         "CONTRIBUTING guide present"),
    ("SECURITY.md",             "SECURITY policy present"),
    ("Makefile",                "Makefile present (build/task automation)"),
    ("docker-compose.yml",      "Docker Compose present"),
    ("docker-compose.yaml",     "Docker Compose present"),
    (".pre-commit-config.yaml", "Pre-commit hooks configured"),
    ("renovate.json",           "Renovate dependency-update bot configured"),
    (".editorconfig",           "EditorConfig present"),
    (".nvmrc",                  "Node.js version pinned (.nvmrc)"),
    (".python-version",         "Python version pinned (.python-version)"),
    ("CODEOWNERS",              "CODEOWNERS file present"),
    ("CLAUDE.md",               "Claude AI context file present (CLAUDE.md)"),
    ("AGENTS.md",               "AI agent instructions present (AGENTS.md)"),
    (".cursorrules",            "Cursor AI rules present"),
    (".claude",                 "Claude AI context present (.claude/)"),
    (".cursor",                 "Cursor IDE rules/agents present (.cursor/)"),
    (".windsurf",               "Windsurf IDE rules present (.windsurf/)"),
    (".roo",                    "Roo AI rules present (.roo/)"),
    (".specify",                "Spec Kit metadata directory"),
    (".roomodes",               "Roo AI modes config present (.roomodes)"),
    (".maestro",                "Maestro mobile E2E testing present"),
    (".githooks",               "Custom Git hooks present (.githooks/)"),
    ("migrations",              "Database migrations directory present"),
    ("seeds",                   "Database seeds directory present"),
    ("docs",                    "Documentation directory present"),
    ("scripts",                 "Scripts directory present"),
    ("infra",                   "Infrastructure directory present"),
    ("terraform",               "Terraform infrastructure present"),
    ("k8s",                     "Kubernetes manifests present"),
    ("helm",                    "Helm charts present"),
]


# ---------------------------------------------------------------------------
# Summary dataclass
# ---------------------------------------------------------------------------

@dataclass
class LlmSummary:
    """Structured heuristic summary of the project."""
    detected_stack: list[str] = field(default_factory=list)
    file_count: int = 0
    dir_count: int = 0
    notable_flags: list[str] = field(default_factory=list)
    top_level_dirs: list[str] = field(default_factory=list)
    top_level_files: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Detection logic
# ---------------------------------------------------------------------------

def _collect_all_names(node: TreeNode) -> tuple[set[str], set[str]]:
    """
    Walk the entire TreeNode tree and collect every file name and dir name
    into two flat sets. Used for stack/flag detection without a second
    filesystem pass.
    """
    files: set[str] = set()
    dirs: set[str] = set()

    def _walk(n: TreeNode) -> None:
        for child in n.children:
            if child.is_symlink:
                continue
            if child.is_dir:
                dirs.add(child.name)
                _walk(child)
            else:
                files.add(child.name)

    _walk(node)
    return files, dirs


def _collect_all_paths(node: TreeNode) -> set[str]:
    """
    Walk the entire TreeNode tree and collect every entry's path relative
    to `node`, posix-style ("bin/cake"). Used only for `_STACK_SIGNALS`
    patterns that contain '/' — bare-name patterns never need this.
    """
    paths: set[str] = set()

    def _walk(n: TreeNode, prefix: str) -> None:
        for child in n.children:
            if child.is_symlink:
                continue
            rel = f"{prefix}{child.name}"
            paths.add(rel)
            if child.is_dir:
                _walk(child, rel + "/")

    _walk(node, "")
    return paths


def _count_entries(node: TreeNode) -> tuple[int, int]:
    """Return (total_files, total_dirs) recursively."""
    files = dirs = 0
    for child in node.children:
        if child.is_symlink:
            continue
        if child.is_dir:
            dirs += 1
            f, d = _count_entries(child)
            files += f
            dirs += d
        else:
            files += 1
    return files, dirs


def _matches_pattern(name: str, pattern: str) -> bool:
    """Simple glob-style match: supports leading/trailing '*' wildcards only."""
    if pattern.startswith("*") and pattern.endswith("*"):
        return pattern[1:-1] in name
    if pattern.startswith("*"):
        return name.endswith(pattern[1:])
    if pattern.endswith("*"):
        return name.startswith(pattern[:-1])
    return name == pattern


def _detect_stack(all_names: set[str], all_paths: set[str]) -> list[str]:
    """
    Weighted stack detection.

    Each matching signal contributes its weight to that label's score.
    Labels are sorted by total score descending, so the most strongly
    signalled stack appears first — even in polyglot monorepos where
    a secondary language has more signal files.

    Example: a PHP/CakePHP project with a stray requirements.txt will
    correctly rank CakePHP first because bin/cake (weight 5) +
    composer.json (weight 4) outscores requirements.txt (weight 2).

    Patterns containing '/' (e.g. "bin/cake") are matched against full
    relative paths — exact match at the root, or as a path suffix at
    any depth (consistent with how bare-name patterns match anywhere
    in the tree). Patterns without '/' match bare names only, unchanged.
    """
    scores: dict[str, int] = {}

    for pattern, label, weight in _STACK_SIGNALS:
        if "/" in pattern:
            matched = any(
                path == pattern or path.endswith("/" + pattern)
                for path in all_paths
            )
        else:
            matched = any(_matches_pattern(name, pattern) for name in all_names)
        if matched:
            scores[label] = scores.get(label, 0) + weight

    # Sort by score descending, return labels only
    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return [label for label, _ in ranked]


def analyze(node: TreeNode) -> LlmSummary:
    """
    Inspect a TreeNode tree and return an LlmSummary with detected stack,
    counts, flags, and top-level structure. Pure rule-based, zero deps,
    no filesystem access beyond the already-built tree.
    """
    summary = LlmSummary()

    all_files, all_dirs = _collect_all_names(node)
    all_names = all_files | all_dirs
    all_paths = _collect_all_paths(node)

    # Weighted stack detection — sorted by score, not insertion order
    summary.detected_stack = _detect_stack(all_names, all_paths)

    # Notable flags
    seen_flags: set[str] = set()
    for pattern, message in _NOTABLE_FLAGS:
        for name in all_names:
            if _matches_pattern(name, pattern) and message not in seen_flags:
                summary.notable_flags.append(message)
                seen_flags.add(message)
                break

    # Counts
    summary.file_count, summary.dir_count = _count_entries(node)

    # Top-level structure
    for child in node.children:
        if child.is_symlink:
            continue
        if child.is_dir:
            summary.top_level_dirs.append(child.name + "/")
        else:
            summary.top_level_files.append(child.name)

    return summary