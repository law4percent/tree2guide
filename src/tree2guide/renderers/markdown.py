"""
tree2guide.renderers.markdown — renders the tree as a markdown code block.
"""

from __future__ import annotations
from tree2guide.scanner import TreeNode, render_lines

FOOTER = (
    "*Generated with [tree2guide](https://github.com/law4percent/tree2guide) "
    "by Lawrence Roble ([@law4percent](https://github.com/law4percent)) "
    "— open source, MIT licensed. Contributions welcome!*"
)


def render_markdown(
    tree: "TreeNode | list[str]",
    title: str | None = None,
    include_footer: bool = True,
) -> str:
    """
    Render a TreeNode (or raw line list for backward compat) as a markdown document.
    Returns a string with a trailing newline.
    """
    if isinstance(tree, list):
        lines = tree
    else:
        lines = render_lines(tree)

    md: list[str] = []
    if title:
        md.append(f"# {title}\n")
    md.append("```")
    md.extend(lines)
    md.append("```")
    if include_footer:
        md.append("")
        md.append("---")
        md.append(FOOTER)
    return "\n".join(md) + "\n"