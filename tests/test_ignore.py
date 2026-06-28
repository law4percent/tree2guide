"""Tests for tree2guide.ignore (GitignoreRule, ExcludeMatcher)."""

from tree2guide.ignore import ExcludeMatcher, GitignoreRule


class TestGitignoreRuleBasics:
    def test_simple_name_matches_at_any_depth(self):
        rule = GitignoreRule("logs")
        assert rule.matches("logs", True)
        assert rule.matches("lib/logs", True)
        assert rule.matches("a/b/c/logs", True)

    def test_simple_name_does_not_match_partial(self):
        rule = GitignoreRule("logs")
        assert not rule.matches("logsfile.txt", False)
        assert not rule.matches("mylogs", True)

    def test_wildcard_extension(self):
        rule = GitignoreRule("*.log")
        assert rule.matches("debug.log", False)
        assert rule.matches("nested/debug.log", False)
        assert not rule.matches("debug.txt", False)

    def test_wildcard_in_middle(self):
        rule = GitignoreRule("app.*.symbols")
        assert rule.matches("app.foo.symbols", False)
        assert rule.matches("lib/app.bar.symbols", False)
        assert not rule.matches("app.symbols", False)


class TestDirOnly:
    def test_trailing_slash_only_matches_directories(self):
        rule = GitignoreRule("build/")
        assert rule.matches("build", True)
        assert not rule.matches("build", False)

    def test_dir_only_excludes_files_inside_matched_dir(self):
        rule = GitignoreRule("/build/")
        assert rule.matches("build", True)
        assert rule.matches("build/output.txt", False)
        assert rule.matches("build/sub/deep.txt", False)


class TestAnchoring:
    def test_leading_slash_anchors_to_root(self):
        rule = GitignoreRule("/build")
        assert rule.matches("build", True)
        assert not rule.matches("lib/build", True)

    def test_no_leading_slash_matches_any_depth(self):
        rule = GitignoreRule("build")
        assert rule.matches("build", True)
        assert rule.matches("lib/build", True)
        assert rule.matches("a/b/build", True)


class TestDoubleStar:
    def test_double_star_prefix_matches_any_depth(self):
        rule = GitignoreRule("**/android/key.properties")
        assert rule.matches("android/key.properties", False)
        assert rule.matches("app/android/key.properties", False)
        assert rule.matches("a/b/c/android/key.properties", False)
        assert not rule.matches("android/other.properties", False)

    def test_double_star_directory_pattern(self):
        rule = GitignoreRule("**/doc/api/")
        assert rule.matches("doc/api", True)
        assert rule.matches("lib/doc/api", True)
        assert not rule.matches("doc/api", False)


class TestNegation:
    def test_negation_flag_set(self):
        rule = GitignoreRule("!admin")
        assert rule.negate is True

    def test_non_negated_flag(self):
        rule = GitignoreRule("admin")
        assert rule.negate is False


class TestExcludeMatcherEvaluationOrder:
    def test_later_rule_overrides_earlier_rule(self):
        matcher = ExcludeMatcher(["*", "!admin"])
        assert matcher.is_excluded("api", True)
        assert not matcher.is_excluded("admin", True)

    def test_whitelist_only_pattern(self):
        matcher = ExcludeMatcher(["*", "!admin", "!admin/**"])
        assert matcher.is_excluded("api", True)
        assert matcher.is_excluded("BUGS", True)
        assert not matcher.is_excluded("admin", True)
        assert not matcher.is_excluded("admin/file.md", False)
        assert not matcher.is_excluded("admin/sub/file.md", False)

    def test_plain_blocklist(self):
        matcher = ExcludeMatcher(["api", "BUGS", "business-and-legal-notes"])
        assert matcher.is_excluded("api", True)
        assert matcher.is_excluded("BUGS", True)
        assert not matcher.is_excluded("admin", True)

    def test_flutter_style_gitignore_content(self):
        patterns = [
            "logs",
            "**/android/app/keystore/*.jks",
            "**/android/key.properties",
            "*.class",
            "*.log",
            ".DS_Store",
            ".idea/",
            ".dart_tool/",
            "/build/",
            "/coverage/",
            "/android/app/debug",
        ]
        matcher = ExcludeMatcher(patterns)
        assert matcher.is_excluded("build", True)
        assert matcher.is_excluded("build/output.txt", False)
        assert matcher.is_excluded("coverage", True)
        assert matcher.is_excluded("coverage/report.html", False)
        assert matcher.is_excluded(".idea", True)
        assert matcher.is_excluded("android/app/keystore/release.jks", False)
        assert matcher.is_excluded("android/key.properties", False)
        assert matcher.is_excluded("android/app/debug", True)
        assert matcher.is_excluded("debug.log", False)
        assert matcher.is_excluded("Test.class", False)
        assert not matcher.is_excluded("lib", True)
        assert not matcher.is_excluded("lib/main.dart", False)
        assert not matcher.is_excluded("android/app/keystore", True)