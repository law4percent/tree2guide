"""
tree2guide.cli — argument parsing and the `tree2guide` command entry point.
"""

import argparse
import sys
from pathlib import Path

from tree2guide.ignore import EXCLUDE_FILENAME, ExcludeMatcher, load_exclude_patterns
from tree2guide.renderers.html import render_html
from tree2guide.renderers.json_renderer import render_json
from tree2guide.renderers.llm import render_llm
from tree2guide.renderers.markdown import render_markdown
from tree2guide.renderers.text import render_text
from tree2guide.renderers.yaml_renderer import render_yaml
from tree2guide.scanner import TreeOptions, build_node_tree

_FORMAT_EXTENSIONS = {
    "markdown": ".md",
    "text":     ".txt",
    "json":     ".json",
    "yaml":     ".yaml",
    "html":     ".html",
    "llm":      ".txt",
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="tree2guide",
        description="Generate a structured tree view of a folder in multiple formats.",
    )
    parser.add_argument("target", help="Path to the target folder")
    parser.add_argument(
        "-o", "--output", default=None,
        help="Output file path (default: <folder>_tree.<ext> based on --format)",
    )
    parser.add_argument(
        "--exclude-file", default=None,
        help=f"Path to exclude file (default: <target>/{EXCLUDE_FILENAME})",
    )
    parser.add_argument("--title", default=None, help="Optional title above the tree")
    parser.add_argument(
        "--no-footer", action="store_true",
        help="Omit the author/license footer (markdown and html only)",
    )
    parser.add_argument(
        "--stdout", action="store_true",
        help="Print to stdout instead of writing a file",
    )
    parser.add_argument(
        "--format",
        choices=["markdown", "text", "json", "yaml", "html", "llm"],
        default="markdown",
        help="Output format (default: markdown). Use 'llm' for an AI-friendly summary.",
    )
    parser.add_argument(
        "--llm", action="store_true",
        help="Shorthand for --format llm (AI-friendly project summary)",
    )
    parser.add_argument(
        "--max-depth", type=int, default=None, metavar="N",
        help="Limit recursion depth",
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--dirs-only", action="store_true", help="Only show directories")
    group.add_argument("--files-only", action="store_true", help="Only show files")
    parser.add_argument("--no-hidden", action="store_true", help="Skip dotfiles/dotfolders")
    parser.add_argument(
        "--sort",
        choices=["dirs-first", "files-first", "alpha"],
        default="dirs-first",
        help="Sort order within each folder (default: dirs-first)",
    )
    return parser


def _render(fmt: str, tree, title: str | None, include_footer: bool) -> str:
    if fmt == "markdown":
        return render_markdown(tree, title=title, include_footer=include_footer)
    if fmt == "text":
        return render_text(tree, title=title)
    if fmt == "json":
        return render_json(tree)
    if fmt == "yaml":
        return render_yaml(tree)
    if fmt == "html":
        return render_html(tree, title=title, include_footer=include_footer)
    if fmt == "llm":
        return render_llm(tree, title=title)
    raise ValueError(f"Unknown format: {fmt}")


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    # --llm is a shorthand for --format llm
    fmt = "llm" if args.llm else args.format

    root = Path(args.target).resolve()
    if not root.is_dir():
        print(f"Error: '{root}' is not a valid directory.", file=sys.stderr)
        return 1

    exclude_file = (
        Path(args.exclude_file).resolve() if args.exclude_file else root / EXCLUDE_FILENAME
    )
    patterns = load_exclude_patterns(exclude_file)
    matcher = ExcludeMatcher(patterns)

    options = TreeOptions(
        max_depth=args.max_depth,
        dirs_only=args.dirs_only,
        files_only=args.files_only,
        no_hidden=args.no_hidden,
        sort=args.sort,
    )

    tree = build_node_tree(root, matcher, options)
    output = _render(fmt, tree, title=args.title, include_footer=not args.no_footer)

    if args.stdout:
        sys.stdout.buffer.write(output.encode("utf-8"))
        return 0

    ext = _FORMAT_EXTENSIONS[fmt]
    # llm output gets a distinct suffix so it doesn't clobber a plain text file
    suffix = "_llm" if fmt == "llm" else "_tree"
    output_path = (
        Path(args.output).resolve()
        if args.output
        else Path.cwd() / f"{root.name}{suffix}{ext}"
    )
    output_path.write_text(output, encoding="utf-8")

    print(f"✅ Tree written to: {output_path}")
    if exclude_file.is_file():
        print(f"   Used exclude file: {exclude_file}")
    else:
        print(f"   No exclude file found at {exclude_file} (only defaults applied)")

    return 0


if __name__ == "__main__":
    sys.exit(main())