"""Unit tests for check_copyright.py, mocking out `git log` calls."""

from __future__ import annotations

import subprocess
from pathlib import Path
from unittest.mock import patch

import check_copyright as cc


def _git_log_result(years: list[str]) -> subprocess.CompletedProcess:
    return subprocess.CompletedProcess(args=[], returncode=0, stdout="\n".join(years), stderr="")


def test_format_years_single():
    assert cc.format_years(2021, 2021) == "2021"


def test_format_years_range():
    assert cc.format_years(2020, 2025) == "2020-2025"


def test_parse_years_single():
    assert cc.parse_years("2021") == (2021, 2021)


def test_parse_years_dash_range():
    assert cc.parse_years("2020-2025") == (2020, 2025)


def test_parse_years_comma_range():
    assert cc.parse_years("2020, 2021") == (2020, 2021)


def test_git_year_range_none_when_no_history(tmp_path: Path):
    with patch.object(subprocess, "run", return_value=_git_log_result([])):
        assert cc.git_year_range(tmp_path / "f.py", tmp_path) is None


def test_git_year_range_first_and_last(tmp_path: Path):
    with patch.object(subprocess, "run", return_value=_git_log_result(["2025", "2016", "2020"])):
        assert cc.git_year_range(tmp_path / "f.py", tmp_path) == (2016, 2025)


def test_check_file_ok(tmp_path: Path):
    f = tmp_path / "ok.py"
    f.write_text("# Copyright (C) 2016-2025 Someone <someone@example.com>\n")
    with patch.object(subprocess, "run", return_value=_git_log_result(["2016", "2025"])):
        report = cc.check_file(f, tmp_path)
    assert report.status == "ok"


def test_check_file_mismatch(tmp_path: Path):
    f = tmp_path / "mismatch.py"
    f.write_text("# Copyright (C) 2021 Someone <someone@example.com>\n")
    with patch.object(subprocess, "run", return_value=_git_log_result(["2016", "2025"])):
        report = cc.check_file(f, tmp_path)
    assert report.status == "mismatch"
    assert "2021" in report.detail
    assert "2016-2025" in report.detail


def test_check_file_no_header(tmp_path: Path):
    f = tmp_path / "no_header.py"
    f.write_text("print('hello')\n")
    with patch.object(subprocess, "run", return_value=_git_log_result(["2020"])):
        report = cc.check_file(f, tmp_path)
    assert report.status == "no-header"


def test_check_file_no_history(tmp_path: Path):
    f = tmp_path / "untracked.py"
    f.write_text("# Copyright (C) 2021 Someone <someone@example.com>\n")
    with patch.object(subprocess, "run", return_value=_git_log_result([])):
        report = cc.check_file(f, tmp_path)
    assert report.status == "no-history"


def test_check_file_multi_author(tmp_path: Path):
    f = tmp_path / "multi.py"
    f.write_text(
        "# Copyright (C) 2020, 2021 Author One <one@example.com>\n"
        "# Copyright (C) 2022 Author Two <two@example.com>\n"
    )
    with patch.object(subprocess, "run", return_value=_git_log_result(["2020", "2021", "2022"])):
        report = cc.check_file(f, tmp_path)
    assert report.status == "multi-author"


def test_fix_file_rewrites_only_year(tmp_path: Path):
    f = tmp_path / "fixme.py"
    f.write_text("# Copyright (C) 2021 Someone <someone@example.com>\nprint(1)\n")
    with patch.object(subprocess, "run", return_value=_git_log_result(["2016", "2025"])):
        report = cc.check_file(f, tmp_path)
        assert report.status == "mismatch"
        cc.fix_file(f, report, tmp_path)
    assert f.read_text() == "# Copyright (C) 2016-2025 Someone <someone@example.com>\nprint(1)\n"
