"""Tests for tree2guide.renderers.markdown."""

from tree2guide.renderers.markdown import render_markdown


def test_basic_rendering_wraps_in_code_fence():
    output = render_markdown(["proj/", "├── a.txt"], include_footer=False)
    assert output.startswith("```\n")
    assert "proj/" in output
    assert output.rstrip().endswith("```")


def test_title_adds_heading():
    output = render_markdown(["proj/"], title="My Project", include_footer=False)
    assert output.startswith("# My Project\n")


def test_footer_included_by_default():
    output = render_markdown(["proj/"])
    assert "tree2guide" in output
    assert "MIT licensed" in output


def test_no_footer_omits_attribution():
    output = render_markdown(["proj/"], include_footer=False)
    assert "MIT licensed" not in output