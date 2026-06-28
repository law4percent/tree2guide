"""
tree2guide.renderers.html — renders the tree as a self-contained HTML page.

Produces a single .html file with:
  - Collapsible folder nodes (pure CSS + minimal JS, no external deps)
  - Expand/collapse all buttons
  - A monospace tree with the same connector characters as the text/markdown renderers
  - Clean, minimal styling that works in any modern browser
  - An optional title shown as a <h1>
  - An optional attribution footer

No external CSS frameworks, fonts, or scripts are loaded — the file works
fully offline.
"""

from __future__ import annotations
from tree2guide.scanner import TreeNode

_CSS = """\
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
body {
    font-family: system-ui, -apple-system, sans-serif;
    background: #0f1117;
    color: #e2e8f0;
    min-height: 100vh;
    padding: 2rem;
}
h1 { font-size: 1.5rem; font-weight: 600; margin-bottom: 1.25rem; color: #f8fafc; }
.controls { margin-bottom: 1rem; display: flex; gap: 0.5rem; }
button {
    background: #1e2433;
    color: #94a3b8;
    border: 1px solid #2d3748;
    border-radius: 6px;
    padding: 0.3rem 0.75rem;
    font-size: 0.8rem;
    cursor: pointer;
    transition: background 0.15s, color 0.15s;
}
button:hover { background: #2d3748; color: #e2e8f0; }
.tree {
    font-family: 'Cascadia Code', 'Fira Code', 'Consolas', monospace;
    font-size: 0.88rem;
    line-height: 1.7;
    background: #1a1f2e;
    border: 1px solid #2d3748;
    border-radius: 10px;
    padding: 1.25rem 1.5rem;
    overflow-x: auto;
}
ul { list-style: none; padding: 0; }
li { white-space: nowrap; }
.entry { display: inline-flex; align-items: center; gap: 0.3rem; }
.connector { color: #4a5568; user-select: none; }
.toggle {
    cursor: pointer;
    background: none;
    border: none;
    padding: 0;
    font: inherit;
    color: inherit;
    display: inline-flex;
    align-items: center;
    gap: 0.3rem;
}
.toggle:hover .dirname { color: #7dd3fc; }
.icon { font-size: 0.8em; color: #64748b; user-select: none; transition: transform 0.15s; }
.collapsed > .children { display: none; }
.collapsed .icon { transform: rotate(-90deg); }
.dirname { color: #93c5fd; font-weight: 500; }
.filename { color: #e2e8f0; }
.symlink { color: #a78bfa; }
.symlink-arrow { color: #64748b; }
.root { color: #34d399; font-weight: 600; }
footer {
    margin-top: 1.5rem;
    font-size: 0.78rem;
    color: #4a5568;
}
footer a { color: #64748b; }
"""

_JS = """\
function expandAll() {
    document.querySelectorAll('.dir-item').forEach(el => el.classList.remove('collapsed'));
}
function collapseAll() {
    document.querySelectorAll('.dir-item').forEach(el => el.classList.add('collapsed'));
}
function toggle(el) {
    el.closest('.dir-item').classList.toggle('collapsed');
}
"""

FOOTER_HTML = (
    '<footer>Generated with '
    '<a href="https://github.com/law4percent/tree2guide">tree2guide</a> '
    'by <a href="https://github.com/law4percent">Lawrence Roble</a> '
    '— open source, MIT licensed.</footer>'
)


def _node_to_html(node: TreeNode, prefix: str = "", is_last: bool = True, is_root: bool = False) -> list[str]:
    lines: list[str] = []

    if is_root:
        # Root node — no connector, special styling, always expanded
        lines.append('<li class="dir-item">')
        lines.append(
            f'  <span class="entry">'
            f'<button class="toggle" onclick="toggle(this)">'
            f'<span class="icon">▾</span>'
            f'<span class="root">{_esc(node.name)}/</span>'
            f'</button></span>'
        )
        if node.children:
            lines.append('  <ul class="children">')
            for i, child in enumerate(node.children):
                lines.extend(_node_to_html(child, prefix="", is_last=(i == len(node.children) - 1)))
            lines.append("  </ul>")
        lines.append("</li>")
        return lines

    connector = "└── " if is_last else "├── "
    child_prefix = prefix + ("    " if is_last else "│   ")

    if node.is_symlink:
        lines.append("<li>")
        lines.append(
            f'  <span class="entry">'
            f'<span class="connector">{_esc(prefix + connector)}</span>'
            f'<span class="symlink">{_esc(node.name)}</span>'
            f'<span class="symlink-arrow"> -> </span>'
            f'<span class="symlink">{_esc(node.symlink_target or "")}</span>'
            f'</span>'
        )
        lines.append("</li>")
        return lines

    if not node.is_dir:
        lines.append("<li>")
        lines.append(
            f'  <span class="entry">'
            f'<span class="connector">{_esc(prefix + connector)}</span>'
            f'<span class="filename">{_esc(node.name)}</span>'
            f'</span>'
        )
        lines.append("</li>")
        return lines

    # Directory — collapsible
    lines.append('<li class="dir-item">')
    lines.append(
        f'  <span class="entry">'
        f'<span class="connector">{_esc(prefix + connector)}</span>'
        f'<button class="toggle" onclick="toggle(this)">'
        f'<span class="icon">▾</span>'
        f'<span class="dirname">{_esc(node.name)}/</span>'
        f'</button></span>'
    )
    if node.children:
        lines.append('  <ul class="children">')
        for i, child in enumerate(node.children):
            lines.extend(_node_to_html(child, prefix=child_prefix, is_last=(i == len(node.children) - 1)))
        lines.append("  </ul>")
    lines.append("</li>")
    return lines


def _esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def render_html(
    tree: TreeNode,
    title: str | None = None,
    include_footer: bool = True,
) -> str:
    """
    Render a TreeNode as a self-contained HTML page string with a trailing newline.
    """
    title_tag = title or f"{tree.name} — tree2guide"

    body_parts: list[str] = []
    if title:
        body_parts.append(f"<h1>{_esc(title)}</h1>")
    body_parts.append(
        '<div class="controls">'
        '<button onclick="expandAll()">Expand all</button>'
        '<button onclick="collapseAll()">Collapse all</button>'
        '</div>'
    )
    body_parts.append('<div class="tree"><ul>')
    body_parts.extend(_node_to_html(tree, is_root=True))
    body_parts.append("</ul></div>")
    if include_footer:
        body_parts.append(FOOTER_HTML)

    body = "\n".join(body_parts)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{_esc(title_tag)}</title>
<style>
{_CSS}
</style>
</head>
<body>
{body}
<script>
{_JS}
</script>
</body>
</html>
"""