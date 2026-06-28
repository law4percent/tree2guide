"""
tree2guide.llm — rule-based project heuristics for --llm mode.

Zero dependencies, zero network calls. All detection is done by inspecting
the names present in the TreeNode tree that the scanner already built —
no second filesystem pass is needed.

Produces a structured LlmSummary dataclass that the LLM renderer uses to
build its output.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from tree2guide.scanner import TreeNode


# ---------------------------------------------------------------------------
# Detection tables
# ---------------------------------------------------------------------------

# Maps a filename/pattern to (language_or_framework, display_label)
_STACK_SIGNALS: list[tuple[str, str]] = [
    # Python
    ("pyproject.toml",        "Python (pyproject.toml)"),
    ("setup.py",              "Python (setup.py)"),
    ("requirements.txt",      "Python (requirements.txt)"),
    ("Pipfile",               "Python (Pipfile)"),
    ("poetry.lock",           "Python / Poetry"),
    # JavaScript / TypeScript
    ("package.json",          "Node.js / JavaScript"),
    ("tsconfig.json",         "TypeScript"),
    ("next.config.js",        "Next.js"),
    ("next.config.ts",        "Next.js (TypeScript)"),
    ("nuxt.config.ts",        "Nuxt.js"),
    ("nuxt.config.js",        "Nuxt.js"),
    ("vite.config.ts",        "Vite"),
    ("vite.config.js",        "Vite"),
    ("angular.json",          "Angular"),
    ("svelte.config.js",      "SvelteKit"),
    # Go
    ("go.mod",                "Go"),
    # Rust
    ("Cargo.toml",            "Rust / Cargo"),
    # Ruby
    ("Gemfile",               "Ruby"),
    ("Rakefile",              "Ruby / Rake"),
    # Java / Kotlin / JVM
    ("pom.xml",               "Java / Maven"),
    ("build.gradle",          "Java / Gradle"),
    ("build.gradle.kts",      "Kotlin / Gradle"),
    # C / C++
    ("CMakeLists.txt",        "C/C++ / CMake"),
    ("Makefile",              "C/C++ / Make"),
    # PHP
    ("composer.json",         "PHP / Composer"),
    # Swift / iOS
    ("Package.swift",         "Swift / SPM"),
    # Dart / Flutter
    ("pubspec.yaml",          "Dart / Flutter"),
    # .NET
    ("*.csproj",              ".NET / C#"),
    ("*.fsproj",              ".NET / F#"),
    ("*.sln",                 ".NET Solution"),
    # Elixir
    ("mix.exs",               "Elixir / Mix"),
    # Haskell
    ("stack.yaml",            "Haskell / Stack"),
    ("*.cabal",               "Haskell / Cabal"),
    # Docker / infra
    ("Dockerfile",            "Docker"),
    ("docker-compose.yml",    "Docker Compose"),
    ("docker-compose.yaml",   "Docker Compose"),
]

# Files/dirs whose presence is worth flagging
_NOTABLE_FLAGS: list[tuple[str, str]] = [
    (".env.example",          "Environment template (.env.example) present"),
    (".env",                  "Live .env file present (check it's gitignored!)"),
    ("tests",                 "Tests directory present"),
    ("test",                  "Test directory present"),
    ("__tests__",             "Jest-style __tests__ directory present"),
    ("spec",                  "Spec directory present"),
    (".github",               "GitHub Actions / workflows present"),
    (".gitlab-ci.yml",        "GitLab CI config present"),
    ("Jenkinsfile",           "Jenkins CI config present"),
    (".circleci",             "CircleCI config present"),
    ("azure-pipelines.yml",   "Azure Pipelines config present"),
    ("LICENSE",               "LICENSE file present"),
    ("LICENSE.md",            "LICENSE file present"),
    ("CHANGELOG.md",          "CHANGELOG present"),
    ("CONTRIBUTING.md",       "CONTRIBUTING guide present"),
    ("Makefile",              "Makefile present (build/task automation)"),
    ("docker-compose.yml",    "Docker Compose present"),
    ("docker-compose.yaml",   "Docker Compose present"),
    (".pre-commit-config.yaml", "Pre-commit hooks configured"),
    ("renovate.json",         "Renovate dependency-update bot configured"),
    (".editorconfig",         "EditorConfig present"),
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


def analyze(node: TreeNode) -> LlmSummary:
    """
    Inspect a TreeNode tree and return an LlmSummary with detected stack,
    counts, flags, and top-level structure. Pure rule-based, zero deps,
    no filesystem access beyond the already-built tree.
    """
    summary = LlmSummary()

    all_files, all_dirs = _collect_all_names(node)
    all_names = all_files | all_dirs

    # Stack detection — first match wins per signal, deduplicate labels
    seen_labels: set[str] = set()
    for pattern, label in _STACK_SIGNALS:
        for name in all_names:
            if _matches_pattern(name, pattern) and label not in seen_labels:
                summary.detected_stack.append(label)
                seen_labels.add(label)
                break

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