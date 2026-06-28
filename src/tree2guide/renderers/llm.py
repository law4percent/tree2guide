"""
tree2guide.renderers.llm — AI-consumption-friendly project summary renderer.

Produces a structured plain-text document optimised for pasting into an LLM
context window. The format is deliberately verbose and unambiguous: explicit
labels, no markdown fences that an LLM might misread as code to execute,
and a tree that uses the same connector characters humans are used to so
spatial relationships are clear.

No network calls, no API keys, no third-party dependencies.
"""

from __future__ import annotations
from tree2guide.llm import LlmSummary, analyze
from tree2guide.scanner import TreeNode, render_lines


_SEPARATOR = "=" * 60


def render_llm(tree: TreeNode, title: str | None = None) -> str:
    """
    Render a TreeNode as an LLM-friendly project summary.
    Returns a string with a trailing newline.
    """
    summary: LlmSummary = analyze(tree)
    project_name = title or tree.name
    lines: list[str] = []

    # ------------------------------------------------------------------ header
    lines.append(_SEPARATOR)
    lines.append(f"PROJECT STRUCTURE SUMMARY: {project_name}")
    lines.append(_SEPARATOR)
    lines.append("")

    # ----------------------------------------------------------- detected stack
    lines.append("DETECTED STACK / LANGUAGE:")
    if summary.detected_stack:
        for item in summary.detected_stack:
            lines.append(f"  - {item}")
    else:
        lines.append("  (No known stack signals detected)")
    lines.append("")

    # ------------------------------------------------------------------ counts
    lines.append("SIZE:")
    lines.append(f"  Files      : {summary.file_count}")
    lines.append(f"  Directories: {summary.dir_count}")
    lines.append("")

    # --------------------------------------------------------- top-level layout
    lines.append("TOP-LEVEL LAYOUT:")
    if summary.top_level_dirs:
        lines.append("  Directories:")
        for d in summary.top_level_dirs:
            lines.append(f"    {d}")
    if summary.top_level_files:
        lines.append("  Files:")
        for f in summary.top_level_files:
            lines.append(f"    {f}")
    lines.append("")

    # --------------------------------------------------------------- flags
    if summary.notable_flags:
        lines.append("NOTABLE FLAGS:")
        for flag in summary.notable_flags:
            lines.append(f"  - {flag}")
        lines.append("")

    # --------------------------------------------------------------- full tree
    lines.append(_SEPARATOR)
    lines.append("FULL DIRECTORY TREE:")
    lines.append(_SEPARATOR)
    lines.append("")
    lines.extend(render_lines(tree))
    lines.append("")
    lines.append(_SEPARATOR)
    lines.append("END OF PROJECT STRUCTURE SUMMARY")
    lines.append(_SEPARATOR)

    return "\n".join(lines) + "\n"