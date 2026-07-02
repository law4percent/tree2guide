"""
Tests for tree2guide.cli (build_parser, main).

Historically no test imported tree2guide.cli at all, which is why a missing
`from __future__ import annotations` (needed for the `str | None` / `list[str]
| None` type hints in this module) went undetected on the Python 3.9 CI job —
the module was never actually loaded during the test run. These tests close
that gap.
"""

from unittest.mock import patch

import pytest

from tree2guide.cli import build_parser, main


class TestVersionFlag:
    def test_version_flag_exits_zero_and_prints_version(self, capsys):
        with pytest.raises(SystemExit) as exc:
            main(["--version"])
        assert exc.value.code == 0
        captured = capsys.readouterr()
        assert "tree2guide" in captured.out


class TestMainErrorHandling:
    def test_invalid_target_returns_1(self, tmp_path, capsys):
        missing = tmp_path / "does_not_exist"
        code = main([str(missing)])
        assert code == 1
        captured = capsys.readouterr()
        assert "not a valid directory" in captured.err


class TestMainStdout:
    def test_stdout_flag_writes_only_tree_bytes(self, tmp_path, capsysbinary):
        (tmp_path / "a.txt").touch()
        code = main([str(tmp_path), "--stdout", "--format", "text"])
        assert code == 0
        captured = capsysbinary.readouterr()
        assert b"a.txt" in captured.out
        assert captured.err == b""

    def test_output_file_written_when_stdout_not_passed(self, tmp_path, capsys, monkeypatch):
        (tmp_path / "a.txt").touch()
        out_dir = tmp_path / "out"
        out_dir.mkdir()
        monkeypatch.chdir(out_dir)
        code = main([str(tmp_path), "--format", "text"])
        assert code == 0
        written = list(out_dir.glob("*_tree.txt"))
        assert len(written) == 1


class TestNoProgressFlag:
    def test_parser_has_no_progress_flag_defaulting_false(self):
        parser = build_parser()
        args = parser.parse_args(["some_target"])
        assert args.no_progress is False

    def test_no_progress_suppresses_stderr_on_a_slow_scan(self, tmp_path, capsys):
        (tmp_path / "a.txt").touch()
        (tmp_path / "b.txt").touch()

        fake_clock = [0.0]

        def fake_monotonic():
            fake_clock[0] += 1.5
            return fake_clock[0]

        with patch("tree2guide.scanner.time.monotonic", side_effect=fake_monotonic):
            code = main([str(tmp_path), "--stdout", "--no-progress"])
        assert code == 0
        captured = capsys.readouterr()
        assert captured.err == ""

    def test_progress_and_final_summary_appear_on_a_slow_scan(self, tmp_path, capsys):
        (tmp_path / "a.txt").touch()
        (tmp_path / "b.txt").touch()

        fake_clock = [0.0]

        def fake_monotonic():
            fake_clock[0] += 1.5
            return fake_clock[0]

        with patch("tree2guide.scanner.time.monotonic", side_effect=fake_monotonic):
            code = main([str(tmp_path), "--stdout"])
        assert code == 0
        captured = capsys.readouterr()
        assert "Scanning..." in captured.err
        assert "Scan complete." in captured.err
        assert "Files: 2" in captured.err

    def test_no_progress_or_telemetry_on_a_fast_scan(self, tmp_path, capsys):
        (tmp_path / "a.txt").touch()
        code = main([str(tmp_path), "--stdout"])
        assert code == 0
        captured = capsys.readouterr()
        assert captured.err == ""
