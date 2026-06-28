"""
tree2guide — see your project structure clearly.

Public API:
    build_node_tree(root, matcher, options=None) -> TreeNode
    build_tree(root, matcher, options=None) -> list[str]   # backward compat
    TreeNode, TreeOptions
    ExcludeMatcher, GitignoreRule, load_exclude_patterns
    analyze(node) -> LlmSummary
    render_markdown / render_text / render_json / render_yaml / render_html / render_llm
"""

from tree2guide.ignore import (
    DEFAULT_EXCLUDES,
    EXCLUDE_FILENAME,
    ExcludeMatcher,
    GitignoreRule,
    load_exclude_patterns,
)
from tree2guide.llm import LlmSummary, analyze
from tree2guide.renderers.html import render_html
from tree2guide.renderers.json_renderer import render_json
from tree2guide.renderers.llm import render_llm
from tree2guide.renderers.markdown import render_markdown
from tree2guide.renderers.text import render_text
from tree2guide.renderers.yaml_renderer import render_yaml
from tree2guide.scanner import TreeNode, TreeOptions, build_node_tree, build_tree

__version__ = "1.0.0"

__all__ = [
    "__version__",
    "DEFAULT_EXCLUDES",
    "EXCLUDE_FILENAME",
    "ExcludeMatcher",
    "GitignoreRule",
    "load_exclude_patterns",
    "TreeNode",
    "TreeOptions",
    "build_node_tree",
    "build_tree",
    "LlmSummary",
    "analyze",
    "render_markdown",
    "render_text",
    "render_json",
    "render_yaml",
    "render_html",
    "render_llm",
]