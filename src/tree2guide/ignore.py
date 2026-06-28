"""
tree2guide.ignore — gitignore-compatible pattern matching, zero dependencies.
"""

import re
from pathlib import Path

DEFAULT_EXCLUDES: list[str] = [
    ".git",
    ".tree2ignore",
    "__pycache__",
    "*.pyc",
    ".DS_Store",
]

EXCLUDE_FILENAME = ".tree2ignore"


def load_exclude_patterns(exclude_file: Path) -> list[str]:
    patterns = list(DEFAULT_EXCLUDES)
    if exclude_file.is_file():
        for line in exclude_file.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            patterns.append(line.rstrip("\n"))
    return patterns


class GitignoreRule:
    def __init__(self, raw: str):
        pattern = raw
        self.negate = pattern.startswith("!")
        if self.negate:
            pattern = pattern[1:]
        self.dir_only = pattern.endswith("/")
        if self.dir_only:
            pattern = pattern[:-1]
        self.anchored = pattern.startswith("/")
        if self.anchored:
            pattern = pattern[1:]
        has_slash = "/" in pattern
        if not has_slash and not self.anchored:
            pattern = "**/" + pattern
        self.regex = re.compile(self._translate(pattern))

    @staticmethod
    def _translate(pattern: str) -> str:
        segments = pattern.split("/")
        parts = []
        for i, segment in enumerate(segments):
            if segment == "**":
                if i == 0 and i == len(segments) - 1:
                    parts.append(".*")
                elif i == 0:
                    parts.append("(?:.*/)?")
                elif i == len(segments) - 1:
                    parts.append("(?:/.*)?" if parts else ".*")
                else:
                    parts.append("(?:[^/]+/)*")
                continue
            seg_regex = "".join(
                "[^/]*" if c == "*" else "[^/]" if c == "?" else re.escape(c)
                for c in segment
            )
            if parts and segments[i - 1] != "**":
                parts.append("/")
            parts.append(seg_regex)
        body = "".join(parts)
        return f"^{body}$"

    def matches(self, rel_path: str, is_dir: bool) -> bool:
        parts = rel_path.split("/")
        if not (self.dir_only and not is_dir):
            if self.regex.match(rel_path):
                return True
        for k in range(1, len(parts)):
            if self.regex.match("/".join(parts[:k])):
                return True
        return False


class ExcludeMatcher:
    def __init__(self, patterns: list[str]):
        self.rules: list[GitignoreRule] = [GitignoreRule(p) for p in patterns]

    def is_excluded(self, rel_path: str, is_dir: bool) -> bool:
        excluded = False
        for rule in self.rules:
            if rule.matches(rel_path, is_dir):
                excluded = not rule.negate
        return excluded