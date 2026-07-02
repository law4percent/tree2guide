"""Tests for tree2guide.scanner (build_tree, build_node_tree, TreeOptions)."""

import tempfile
import time
from pathlib import Path
from unittest.mock import patch

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


class TestBuildNodeTreeProgress:
    """on_progress is pure instrumentation: default None must leave every
    existing caller (including build_tree()) completely unaffected."""

    def test_default_none_has_no_effect(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "proj"
            _make_tree({"a.txt": None, "b.txt": None}, root)
            matcher = ExcludeMatcher([])
            node = build_node_tree(root, matcher)  # no on_progress arg at all
            assert {c.name for c in node.children} == {"a.txt", "b.txt"}

    def test_on_progress_not_called_on_a_fast_scan(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "proj"
            _make_tree({"a.txt": None}, root)
            matcher = ExcludeMatcher([])
            calls = []
            build_node_tree(root, matcher, TreeOptions(), on_progress=lambda f, d: calls.append((f, d)))
            assert calls == []

    def test_on_progress_fires_and_reports_correct_running_totals(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "proj"
            _make_tree({"a.txt": None, "b.txt": None, "sub": {"c.txt": None}}, root)
            matcher = ExcludeMatcher([])
            calls = []

            fake_clock = [0.0]

            def fake_monotonic():
                fake_clock[0] += 1.5  # always exceeds the 1s gate
                return fake_clock[0]

            with patch("tree2guide.scanner.time.monotonic", side_effect=fake_monotonic):
                build_node_tree(
                    root, matcher, TreeOptions(),
                    on_progress=lambda f, d: calls.append((f, d)),
                )

            assert len(calls) > 0
            assert calls[-1] == (3, 1)  # 3 files (a, b, c), 1 dir (sub) — final totals

    def test_on_progress_excludes_symlinks_matching_final_count_convention(self):
        """Found via real-world testing against a repo with thousands of
        symlinks (venv/node_modules .bin links): progress must count
        entries the same way _count_tree()/_count_entries() do elsewhere
        in the codebase, or the live number and the final summary
        disagree. A symlinked file and a symlinked dir must both be
        excluded from the running totals, exactly like they're excluded
        from is_symlink-checked counts everywhere else."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "proj"
            _make_tree({"a.txt": None, "real_dir": {"b.txt": None}}, root)
            (root / "link_to_file").symlink_to(root / "a.txt")
            (root / "link_to_dir").symlink_to(root / "real_dir")
            matcher = ExcludeMatcher([])
            calls = []

            fake_clock = [0.0]

            def fake_monotonic():
                fake_clock[0] += 1.5
                return fake_clock[0]

            with patch("tree2guide.scanner.time.monotonic", side_effect=fake_monotonic):
                build_node_tree(
                    root, matcher, TreeOptions(),
                    on_progress=lambda f, d: calls.append((f, d)),
                )

            assert len(calls) > 0
            # 2 real files (a.txt, real_dir/b.txt), 1 real dir (real_dir) —
            # the 2 symlinks must not inflate either count.
            assert calls[-1] == (2, 1)

    def test_no_progress_equivalent_is_on_progress_none(self):
        """Mirrors the CLI's --no-progress: passing None wires no callback
        at all, regardless of how slow the walk is."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "proj"
            _make_tree({"a.txt": None}, root)
            matcher = ExcludeMatcher([])

            fake_clock = [0.0]

            def fake_monotonic():
                fake_clock[0] += 1.5
                return fake_clock[0]

            with patch("tree2guide.scanner.time.monotonic", side_effect=fake_monotonic):
                node = build_node_tree(root, matcher, TreeOptions(), on_progress=None)
            assert node is not None