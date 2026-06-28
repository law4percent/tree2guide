"""
tree2guide.renderers — output formatters for a tree built by tree2guide.scanner.

Renderers: markdown (default), text, json, yaml, html, llm.
Each takes a TreeNode and returns a string. Only the llm renderer also
calls tree2guide.llm.analyze() to attach heuristic metadata.
"""