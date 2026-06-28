"""
Tests for tree2guide.llm (analyze) and tree2guide.renderers.llm (render_llm).
"""

import tempfile
from pathlib import Path

from tree2guide.ignore import ExcludeMatcher
from tree2guide.llm import analyze
from tree2guide.renderers.llm import render_llm
from tree2guide.scanner import TreeOptions, build_node_tree


def _make_tree(structure: dict, base: Path):
    base.mkdir(parents=True, exist_ok=True)
    for name, contents in structure.items():
        path = base / name
        if isinstance(contents, dict):
            path.mkdir(parents=True, exist_ok=True)
            _make_tree(contents, path)
        else:
            path.touch()


def _build(structure: dict):
    """Helper: create a temp fs tree, return (TemporaryDirectory, TreeNode)."""
    tmp = tempfile.TemporaryDirectory()
    root = Path(tmp.name) / "proj"
    _make_tree(structure, root)
    matcher = ExcludeMatcher([])
    node = build_node_tree(root, matcher, TreeOptions())
    return tmp, node


# ---------------------------------------------------------------------------
# analyze() — LlmSummary
# ---------------------------------------------------------------------------

class TestAnalyzeStackDetection:
    def test_detects_python_pyproject(self):
        tmp, node = _build({"pyproject.toml": None, "src": {"main.py": None}})
        with tmp:
            s = analyze(node)
            assert any("Python" in label for label in s.detected_stack)

    def test_detects_nodejs_package_json(self):
        tmp, node = _build({"package.json": None, "index.js": None})
        with tmp:
            s = analyze(node)
            assert any("Node.js" in label for label in s.detected_stack)

    def test_detects_go_mod(self):
        tmp, node = _build({"go.mod": None, "main.go": None})
        with tmp:
            s = analyze(node)
            assert any("Go" in label for label in s.detected_stack)

    def test_detects_rust_cargo(self):
        tmp, node = _build({"Cargo.toml": None, "src": {"main.rs": None}})
        with tmp:
            s = analyze(node)
            assert any("Rust" in label for label in s.detected_stack)

    def test_detects_flutter_pubspec(self):
        tmp, node = _build({"pubspec.yaml": None, "lib": {"main.dart": None}})
        with tmp:
            s = analyze(node)
            assert any("Flutter" in label for label in s.detected_stack)

    def test_detects_docker(self):
        tmp, node = _build({"Dockerfile": None, "app.py": None})
        with tmp:
            s = analyze(node)
            assert any("Docker" in label for label in s.detected_stack)

    def test_no_signals_returns_empty_stack(self):
        tmp, node = _build({"README.md": None, "notes.txt": None})
        with tmp:
            s = analyze(node)
            assert s.detected_stack == []

    def test_multiple_stacks_detected(self):
        tmp, node = _build({
            "pyproject.toml": None,
            "Dockerfile": None,
            "docker-compose.yml": None,
        })
        with tmp:
            s = analyze(node)
            assert len(s.detected_stack) >= 2


class TestAnalyzeCounts:
    def test_file_count(self):
        tmp, node = _build({"a.py": None, "b.py": None, "c.py": None})
        with tmp:
            s = analyze(node)
            assert s.file_count == 3

    def test_dir_count(self):
        tmp, node = _build({"src": {}, "tests": {}, "docs": {}})
        with tmp:
            s = analyze(node)
            assert s.dir_count == 3

    def test_nested_counts(self):
        tmp, node = _build({"src": {"a.py": None, "b.py": None}, "main.py": None})
        with tmp:
            s = analyze(node)
            assert s.file_count == 3
            assert s.dir_count == 1


class TestAnalyzeNotableFlags:
    def test_flags_tests_directory(self):
        tmp, node = _build({"tests": {"test_main.py": None}})
        with tmp:
            s = analyze(node)
            assert any("Tests directory" in f for f in s.notable_flags)

    def test_flags_env_example(self):
        tmp, node = _build({".env.example": None})
        with tmp:
            s = analyze(node)
            assert any(".env.example" in f for f in s.notable_flags)

    def test_flags_github_actions(self):
        tmp, node = _build({".github": {"workflows": {"ci.yml": None}}})
        with tmp:
            s = analyze(node)
            assert any("GitHub" in f for f in s.notable_flags)

    def test_flags_license(self):
        tmp, node = _build({"LICENSE": None})
        with tmp:
            s = analyze(node)
            assert any("LICENSE" in f for f in s.notable_flags)

    def test_flags_changelog(self):
        tmp, node = _build({"CHANGELOG.md": None})
        with tmp:
            s = analyze(node)
            assert any("CHANGELOG" in f for f in s.notable_flags)

    def test_no_flags_on_empty_project(self):
        tmp, node = _build({"main.py": None})
        with tmp:
            s = analyze(node)
            assert s.notable_flags == []


class TestAnalyzeTopLevel:
    def test_top_level_dirs_have_trailing_slash(self):
        tmp, node = _build({"src": {}, "docs": {}})
        with tmp:
            s = analyze(node)
            assert "src/" in s.top_level_dirs
            assert "docs/" in s.top_level_dirs

    def test_top_level_files_listed(self):
        tmp, node = _build({"README.md": None, "pyproject.toml": None})
        with tmp:
            s = analyze(node)
            assert "README.md" in s.top_level_files
            assert "pyproject.toml" in s.top_level_files


# ---------------------------------------------------------------------------
# render_llm()
# ---------------------------------------------------------------------------

class TestRenderLlm:
    def test_contains_section_headers(self):
        tmp, node = _build({"pyproject.toml": None, "src": {"main.py": None}})
        with tmp:
            out = render_llm(node)
            assert "PROJECT STRUCTURE SUMMARY" in out
            assert "DETECTED STACK" in out
            assert "SIZE:" in out
            assert "TOP-LEVEL LAYOUT:" in out
            assert "FULL DIRECTORY TREE:" in out
            assert "END OF PROJECT STRUCTURE SUMMARY" in out

    def test_contains_project_name(self):
        tmp, node = _build({"main.py": None})
        with tmp:
            out = render_llm(node)
            assert "proj" in out

    def test_custom_title_used(self):
        tmp, node = _build({"main.py": None})
        with tmp:
            out = render_llm(node, title="My Awesome App")
            assert "My Awesome App" in out

    def test_contains_file_and_dir_counts(self):
        tmp, node = _build({"src": {"a.py": None, "b.py": None}})
        with tmp:
            out = render_llm(node)
            assert "Files" in out
            assert "Directories" in out

    def test_contains_tree_lines(self):
        tmp, node = _build({"src": {"main.py": None}})
        with tmp:
            out = render_llm(node)
            assert "src/" in out
            assert "main.py" in out

    def test_no_markdown_fences(self):
        tmp, node = _build({"main.py": None})
        with tmp:
            out = render_llm(node)
            assert "```" not in out

    def test_trailing_newline(self):
        tmp, node = _build({"main.py": None})
        with tmp:
            assert render_llm(node).endswith("\n")

    def test_notable_flags_section_present_when_flags_exist(self):
        tmp, node = _build({"tests": {"test_x.py": None}, "LICENSE": None})
        with tmp:
            out = render_llm(node)
            assert "NOTABLE FLAGS:" in out

    def test_notable_flags_section_absent_when_no_flags(self):
        tmp, node = _build({"main.py": None})
        with tmp:
            out = render_llm(node)
            assert "NOTABLE FLAGS:" not in out