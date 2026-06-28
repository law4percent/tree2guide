"""
tree2guide.renderers.yaml — renders the tree as YAML, zero third-party deps.

Output shape mirrors the JSON renderer exactly, hand-serialized so the
package stays dependency-free. Each node is a YAML mapping; children are
a YAML sequence of nested mappings.

    name: src
    type: directory
    children:
      - name: main.py
        type: file
      - name: api
        type: directory
        children: []
"""

from __future__ import annotations
from tree2guide.scanner import TreeNode


def _node_to_yaml(node: TreeNode, indent: int) -> list[str]:
    pad = " " * indent
    lines: list[str] = []

    if node.is_symlink:
        lines.append(f"{pad}name: {_scalar(node.name)}")
        lines.append(f"{pad}type: symlink")
        lines.append(f"{pad}target: {_scalar(node.symlink_target or '')}")
        return lines

    lines.append(f"{pad}name: {_scalar(node.name)}")
    if node.is_dir:
        lines.append(f"{pad}type: directory")
        lines.append(f"{pad}children:")
        if node.children:
            for child in node.children:
                lines.append(f"{pad}  -")
                lines.extend(_node_to_yaml(child, indent + 4))
        else:
            lines.append(f"{pad}  []")
    else:
        lines.append(f"{pad}type: file")

    return lines


def _scalar(value: str) -> str:
    """Quote a scalar value if it contains YAML-unsafe characters."""
    unsafe = {":", "#", "{", "}", "[", "]", ",", "&", "*", "?", "|", "-", "<", ">",
               "=", "!", "%", "@", "`", "'", '"', "\n", "\r"}
    if any(c in value for c in unsafe) or not value:
        escaped = value.replace("\\", "\\\\").replace('"', '\\"')
        return f'"{escaped}"'
    return value


def render_yaml(tree: TreeNode) -> str:
    """
    Render a TreeNode as a YAML string with a trailing newline.
    No third-party dependencies — hand-serialized to keep the package zero-dep.
    """
    lines = _node_to_yaml(tree, indent=0)
    return "\n".join(lines) + "\n"