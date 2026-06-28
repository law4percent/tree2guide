"""Tests for tree2guide.scanner (build_tree, build_node_tree, TreeOptions)."""

import tempfile
from pathlib import Path

from tree2guide.ignore import ExcludeMatcher
from tree2guide.scanner import TreeOptions, build_node_tree, build_tree


def _make_tree(structure: dict, base: Path):
    base.mkdir(parents=True, exist_ok=True)
    for name, contents in structure.items():
        path = base / name
        if isinstance(contents, dict):
            path.mkdir(parents=True, exist_ok=True)
            _make_tree(contents, path)
        else:
            path.touch()


class TestBuildTreeOptions:
    def test_max_depth_limits_recursion(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "proj"
            _make_tree({"a": {"b": {"c": {"deep.txt": None}}}, "top.txt": None}, root)
            matcher = ExcludeMatcher([])
            lines = build_tree(root, matcher, TreeOptions(max_depth=1))
            joined = "\n".join(lines)
            assert "a/" in joined
            assert "top.txt" in joined
            assert "deep.txt" not in joined

    def test_dirs_only_hides_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "proj"
            _make_tree({"src": {"main.py": None}, "readme.md": None}, root)
            matcher = ExcludeMatcher([])
            lines = build_tree(root, matcher, TreeOptions(dirs_only=True))
            joined = "\n".join(lines)
            assert "src/" in joined
            assert "main.py" not in joined
            assert "readme.md" not in joined

    def test_files_only_still_shows_files_nested_in_dirs(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "proj"
            _make_tree({"src": {"deep": {"main.py": None}}}, root)
            matcher = ExcludeMatcher([])
            lines = build_tree(root, matcher, TreeOptions(files_only=True))
            joined = "\n".join(lines)
            assert "main.py" in joined

    def test_files_only_hides_empty_directory_branches(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "proj"
            _make_tree({"empty_dir": {}, "has_file": {"x.txt": None}}, root)
            matcher = ExcludeMatcher([])
            lines = build_tree(root, matcher, TreeOptions(files_only=True))
            joined = "\n".join(lines)
            assert "empty_dir" not in joined
            assert "x.txt" in joined

    def test_no_hidden_skips_dotfiles(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "proj"
            _make_tree({".env": None, "main.py": None}, root)
            matcher = ExcludeMatcher([])
            lines = build_tree(root, matcher, TreeOptions(no_hidden=True))
            joined = "\n".join(lines)
            assert ".env" not in joined
            assert "main.py" in joined

    def test_sort_alpha_ignores_dir_file_grouping(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "proj"
            _make_tree({"zfile.txt": None, "afolder": {}}, root)
            matcher = ExcludeMatcher([])
            lines = build_tree(root, matcher, TreeOptions(sort="alpha"))
            joined = "\n".join(lines)
            assert joined.index("afolder") < joined.index("zfile.txt")

    def test_default_sort_is_dirs_first(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "proj"
            _make_tree({"zfolder": {}, "afile.txt": None}, root)
            matcher = ExcludeMatcher([])
            lines = build_tree(root, matcher, TreeOptions())
            joined = "\n".join(lines)
            assert joined.index("zfolder") < joined.index("afile.txt")

    def test_symlink_rendered_as_arrow_not_followed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "proj"
            _make_tree({"real": {"file.txt": None}}, root)
            link = root / "link_to_real"
            link.symlink_to(root / "real")
            matcher = ExcludeMatcher([])
            lines = build_tree(root, matcher, TreeOptions())
            joined = "\n".join(lines)
            assert "link_to_real ->" in joined
            assert joined.count("file.txt") == 1


class TestBuildNodeTree:
    def test_returns_root_node_with_correct_name(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "myproject"
            _make_tree({"src": {"main.py": None}}, root)
            matcher = ExcludeMatcher([])
            node = build_node_tree(root, matcher)
            assert node.name == "myproject"
            assert node.is_dir is True

    def test_children_populated(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "proj"
            _make_tree({"a.txt": None, "b.txt": None}, root)
            matcher = ExcludeMatcher([])
            node = build_node_tree(root, matcher)
            names = [c.name for c in node.children]
            assert "a.txt" in names
            assert "b.txt" in names

    def test_file_nodes_have_is_dir_false(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "proj"
            _make_tree({"readme.md": None}, root)
            matcher = ExcludeMatcher([])
            node = build_node_tree(root, matcher)
            file_node = node.children[0]
            assert file_node.is_dir is False