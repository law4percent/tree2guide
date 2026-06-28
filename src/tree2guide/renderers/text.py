"""
tree2guide.renderers.text — renders the tree as plain text (no markdown fencing).

Identical visual output to the markdown renderer but with no ``` fences,
no title heading syntax, and no footer — just the raw tree lines.
Useful for terminal output, clipboard piping, and non-markdown tools.
"""

from __future__ import annotations
from tree2guide.scanner import TreeNode, render_lines


def render_text(
    tree: "TreeNode | list[str]",
    title: str | None = None,
) -> str:
    """
    Render a TreeNode as plain text. Returns a string with a trailing newline.
    Title (if given) is printed as a plain line above the tree, not a heading.
    """
    lines: list[str] = []
    if title:
        lines.append(title)
        lines.append("")
    if isinstance(tree, list):
        lines.extend(tree)
    else:
        lines.extend(render_lines(tree))
    return "\n".join(lines) + "\n"