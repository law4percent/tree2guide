"""
tree2guide.renderers.json_renderer — renders the tree as a JSON document.

The JSON shape is designed to be stable and easy to consume by other tools
(the --llm mode in Phase 4, web-based interactive visualizations, etc.):

    {
        "name": "src",
        "type": "directory",
        "children": [
            { "name": "main.py", "type": "file" },
            { "name": "api", "type": "directory", "children": [...] }
        ]
    }

Symlinks carry an extra "target" key and have type "symlink".
"""

from __future__ import annotations
import json
from tree2guide.scanner import TreeNode


def _node_to_dict(node: TreeNode) -> dict:
    if node.is_symlink:
        return {
            "name": node.name,
            "type": "symlink",
            "target": node.symlink_target,
        }
    if node.is_dir:
        result: dict = {
            "name": node.name,
            "type": "directory",
        }
        if node.children:
            result["children"] = [_node_to_dict(c) for c in node.children]
        else:
            result["children"] = []
        return result
    return {"name": node.name, "type": "file"}


def render_json(tree: TreeNode, indent: int = 2) -> str:
    """
    Render a TreeNode as a pretty-printed JSON string with a trailing newline.
    """
    return json.dumps(_node_to_dict(tree), indent=indent) + "\n"