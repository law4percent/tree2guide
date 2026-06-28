"""
Tests for tree2guide.renderers — text, json, yaml, html.

These tests use build_node_tree() on real (temp) filesystems so we're
testing the full scanner→renderer pipeline, not just the renderer in
isolation.
"""

import json
import tempfile
from pathlib import Path

from tree2guide.ignore import ExcludeMatcher
from tree2guide.renderers.html import render_html
from tree2guide.renderers.json_renderer import render_json
from tree2guide.renderers.text import render_text
from tree2guide.renderers.yaml_renderer import render_yaml
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


def _simple_tree():
    """Returns (tmp TemporaryDirectory ctx, root Path, TreeNode)."""
    tmp = tempfile.TemporaryDirectory()
    root = Path(tmp.name) / "proj"
    _make_tree({"src": {"main.py": None, "utils.py": None}, "README.md": None}, root)
    matcher = ExcludeMatcher([])
    node = build_node_tree(root, matcher, TreeOptions())
    return tmp, node


# ---------------------------------------------------------------------------
# Text renderer
# ---------------------------------------------------------------------------

class TestTextRenderer:
    def test_contains_tree_lines(self):
        tmp, node = _simple_tree()
        with tmp:
            output = render_text(node)
            assert "proj/" in output
            assert "src/" in output
            assert "main.py" in output
            assert "README.md" in output

    def test_no_code_fences(self):
        tmp, node = _simple_tree()
        with tmp:
            output = render_text(node)
            assert "```" not in output

    def test_title_is_plain_text(self):
        tmp, node = _simple_tree()
        with tmp:
            output = render_text(node, title="My Project")
            assert output.startswith("My Project\n")
            assert "#" not in output.splitlines()[0]

    def test_trailing_newline(self):
        tmp, node = _simple_tree()
        with tmp:
            output = render_text(node)
            assert output.endswith("\n")


# ---------------------------------------------------------------------------
# JSON renderer
# ---------------------------------------------------------------------------

class TestJsonRenderer:
    def test_valid_json(self):
        tmp, node = _simple_tree()
        with tmp:
            output = render_json(node)
            parsed = json.loads(output)
            assert isinstance(parsed, dict)

    def test_root_name_and_type(self):
        tmp, node = _simple_tree()
        with tmp:
            parsed = json.loads(render_json(node))
            assert parsed["name"] == "proj"
            assert parsed["type"] == "directory"

    def test_children_present(self):
        tmp, node = _simple_tree()
        with tmp:
            parsed = json.loads(render_json(node))
            child_names = [c["name"] for c in parsed["children"]]
            assert "src" in child_names
            assert "README.md" in child_names

    def test_file_node_type(self):
        tmp, node = _simple_tree()
        with tmp:
            parsed = json.loads(render_json(node))
            readme = next(c for c in parsed["children"] if c["name"] == "README.md")
            assert readme["type"] == "file"

    def test_nested_directory(self):
        tmp, node = _simple_tree()
        with tmp:
            parsed = json.loads(render_json(node))
            src = next(c for c in parsed["children"] if c["name"] == "src")
            assert src["type"] == "directory"
            nested_names = [c["name"] for c in src["children"]]
            assert "main.py" in nested_names

    def test_trailing_newline(self):
        tmp, node = _simple_tree()
        with tmp:
            assert render_json(node).endswith("\n")


# ---------------------------------------------------------------------------
# YAML renderer
# ---------------------------------------------------------------------------

class TestYamlRenderer:
    def test_contains_name_and_type_keys(self):
        tmp, node = _simple_tree()
        with tmp:
            output = render_yaml(node)
            assert "name: proj" in output
            assert "type: directory" in output

    def test_contains_file_entries(self):
        tmp, node = _simple_tree()
        with tmp:
            output = render_yaml(node)
            assert "main.py" in output
            assert "README.md" in output

    def test_no_json_braces(self):
        tmp, node = _simple_tree()
        with tmp:
            output = render_yaml(node)
            # should look like YAML, not JSON
            assert "{" not in output
            assert "}" not in output

    def test_trailing_newline(self):
        tmp, node = _simple_tree()
        with tmp:
            assert render_yaml(node).endswith("\n")


# ---------------------------------------------------------------------------
# HTML renderer
# ---------------------------------------------------------------------------

class TestHtmlRenderer:
    def test_is_valid_html_skeleton(self):
        tmp, node = _simple_tree()
        with tmp:
            output = render_html(node)
            assert "<!DOCTYPE html>" in output
            assert "<html" in output
            assert "</html>" in output

    def test_contains_folder_and_file_names(self):
        tmp, node = _simple_tree()
        with tmp:
            output = render_html(node)
            assert "proj" in output
            assert "src" in output
            assert "main.py" in output
            assert "README.md" in output

    def test_title_in_page_title_and_h1(self):
        tmp, node = _simple_tree()
        with tmp:
            output = render_html(node, title="My Project")
            assert "<title>My Project" in output
            assert "<h1>My Project</h1>" in output

    def test_expand_collapse_buttons_present(self):
        tmp, node = _simple_tree()
        with tmp:
            output = render_html(node)
            assert "expandAll" in output
            assert "collapseAll" in output

    def test_footer_included_by_default(self):
        tmp, node = _simple_tree()
        with tmp:
            output = render_html(node)
            assert "tree2guide" in output
            assert "MIT licensed" in output

    def test_no_footer_when_disabled(self):
        tmp, node = _simple_tree()
        with tmp:
            output = render_html(node, include_footer=False)
            assert "MIT licensed" not in output

    def test_trailing_newline(self):
        tmp, node = _simple_tree()
        with tmp:
            assert render_html(node).endswith("\n")