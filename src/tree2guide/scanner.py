"""
tree2guide.scanner — walks the filesystem and builds a tree model.
"""

from __future__ import annotations
import os
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

from tree2guide.ignore import ExcludeMatcher


@dataclass
class TreeNode:
    """Internal tree model — one node per filesystem entry."""
    name: str
    is_dir: bool
    is_symlink: bool = False
    symlink_target: str | None = None
    children: list["TreeNode"] = field(default_factory=list)


@dataclass
class TreeOptions:
    max_depth: int | None = None
    dirs_only: bool = False
    files_only: bool = False
    no_hidden: bool = False
    sort: str = "dirs-first"  # "dirs-first" | "files-first" | "alpha"


def _sort_key(sort_mode: str):
    if sort_mode == "alpha":
        return lambda p: p.name.lower()
    if sort_mode == "files-first":
        return lambda p: (p.is_dir(), p.name.lower())
    return lambda p: (p.is_file(), p.name.lower())


def build_node_tree(
    root: Path,
    matcher: ExcludeMatcher,
    options: TreeOptions | None = None,
    on_progress: Callable[[int, int], None] | None = None,
) -> TreeNode:
    """
    Build and return a TreeNode tree rooted at `root`.

    This is the canonical Scanner output — a single O(n) pass that
    every renderer consumes. build_tree() is kept for backward compat
    and simply calls render_lines() on the result.

    `on_progress`, if given, is called with (files_visited, dirs_visited)
    no more than once per second of wall-clock time during the walk.
    It is pure instrumentation: the scanner does not know or care who's
    listening, and passing None (the default) has zero effect on the
    returned tree or on any existing caller.
    """
    options = options or TreeOptions()
    sort_key = _sort_key(options.sort)
    counts = {"files": 0, "dirs": 0}
    last_tick = time.monotonic()

    def maybe_report() -> None:
        nonlocal last_tick
        if on_progress is None:
            return
        now = time.monotonic()
        if now - last_tick >= 1.0:
            on_progress(counts["files"], counts["dirs"])
            last_tick = now

    def rel_str(path: Path) -> str:
        return path.relative_to(root).as_posix()

    def is_excluded(path: Path, is_dir: bool) -> bool:
        return matcher.is_excluded(rel_str(path), is_dir)

    def recurse(dir_path: Path, depth: int) -> list[TreeNode]:
        if options.max_depth is not None and depth > options.max_depth:
            return []
        try:
            entries = sorted(dir_path.iterdir(), key=sort_key)
        except PermissionError:
            return []

        children: list[TreeNode] = []
        for entry in entries:
            if options.no_hidden and entry.name.startswith("."):
                continue

            is_symlink = entry.is_symlink()
            entry_is_dir = entry.is_dir() and not is_symlink
            excluded = is_excluded(entry, entry.is_dir())

            child_nodes = recurse(entry, depth + 1) if entry_is_dir else []

            hide_for_type = (
                (options.dirs_only and not entry.is_dir())
                or (options.files_only and entry.is_dir() and not child_nodes)
            )
            if hide_for_type:
                continue

            if excluded and not (entry_is_dir and child_nodes):
                continue

            symlink_target: str | None = None
            if is_symlink:
                try:
                    symlink_target = str(Path(os.readlink(entry)))
                except OSError:
                    symlink_target = str(entry.resolve())

            node = TreeNode(
                name=entry.name,
                is_dir=entry.is_dir(),
                is_symlink=is_symlink,
                symlink_target=symlink_target,
                children=child_nodes,
            )
            children.append(node)

            if not node.is_symlink:
                if node.is_dir:
                    counts["dirs"] += 1
                else:
                    counts["files"] += 1
            maybe_report()

        return children

    root_node = TreeNode(name=root.name, is_dir=True, children=recurse(root, depth=1))
    return root_node


def render_lines(node: TreeNode, prefix: str = "") -> list[str]:
    """Flatten a TreeNode tree into connector-prefixed display lines (for text/markdown)."""
    lines: list[str] = [f"{node.name}/"]
    _render_children(node.children, prefix="", lines=lines)
    return lines


def _render_children(children: list[TreeNode], prefix: str, lines: list[str]) -> None:
    for i, child in enumerate(children):
        is_last = i == len(children) - 1
        connector = "└── " if is_last else "├── "

        if child.is_symlink:
            display = f"{child.name} -> {child.symlink_target}"
        elif child.is_dir:
            display = f"{child.name}/"
        else:
            display = child.name

        lines.append(f"{prefix}{connector}{display}")

        if child.is_dir and not child.is_symlink and child.children:
            extension = "    " if is_last else "│   "
            _render_children(child.children, prefix + extension, lines)


# ---------------------------------------------------------------------------
# Backward-compatible API — kept so existing callers don't break
# ---------------------------------------------------------------------------

def build_tree(
    root: Path,
    matcher: ExcludeMatcher,
    options: TreeOptions | None = None,
) -> list[str]:
    """Return tree display lines (backward-compatible wrapper around build_node_tree)."""
    node = build_node_tree(root, matcher, options)
    return render_lines(node)