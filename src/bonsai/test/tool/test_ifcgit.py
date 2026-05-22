# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2025 Dion Moult <dion@thinkmoult.com>
#
# This file is part of Bonsai.
#
# Bonsai is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Bonsai is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Bonsai.  If not, see <http://www.gnu.org/licenses/>.
# This file was generated with the assistance of an AI coding tool.

import os
import tempfile

import bonsai.core.tool
from bonsai.tool.ifcgit import IfcGit, IfcGitRepo
from test.bim.bootstrap import NewFile

try:
    import git
    import git.exc

    HAS_GIT = True
except ImportError:
    HAS_GIT = False

import pytest

requires_git = pytest.mark.skipif(not HAS_GIT, reason="GitPython not available")


def _make_repo(tmpdir: str) -> "git.Repo":
    """Initialise a git repo with user config (needed for commits)."""
    repo = git.Repo.init(tmpdir)
    with repo.config_writer() as cfg:
        cfg.set_value("user", "name", "Test User")
        cfg.set_value("user", "email", "test@example.com")
    return repo


def _commit_ifc(repo: "git.Repo", tmpdir: str, content: str, message: str) -> str:
    """Write content to model.ifc, stage and commit it. Returns commit hexsha."""
    ifc_path = os.path.join(tmpdir, "model.ifc")
    with open(ifc_path, "w") as f:
        f.write(content)
    repo.index.add([os.path.normpath(ifc_path)])
    commit = repo.index.commit(message)
    return commit.hexsha


# ---------------------------------------------------------------------------
# Interface conformance
# ---------------------------------------------------------------------------


class TestImplementsTool(NewFile):
    def test_run(self):
        assert isinstance(IfcGit(), bonsai.core.tool.IfcGit)


# ---------------------------------------------------------------------------
# Pure-logic (no git required)
# ---------------------------------------------------------------------------


class TestIsValidRefFormat(NewFile):
    def test_simple_name(self):
        assert IfcGit.is_valid_ref_format("main")

    def test_name_with_slash(self):
        assert IfcGit.is_valid_ref_format("feature/my-feature")

    def test_name_with_numbers(self):
        assert IfcGit.is_valid_ref_format("release-2024")

    def test_rejects_leading_dot(self):
        assert not IfcGit.is_valid_ref_format(".hidden")

    def test_rejects_leading_dash(self):
        assert not IfcGit.is_valid_ref_format("-branch")

    def test_rejects_space(self):
        assert not IfcGit.is_valid_ref_format("my branch")

    def test_rejects_double_dot(self):
        assert not IfcGit.is_valid_ref_format("my..branch")

    def test_rejects_tilde(self):
        assert not IfcGit.is_valid_ref_format("my~branch")

    def test_rejects_caret(self):
        assert not IfcGit.is_valid_ref_format("my^branch")

    def test_rejects_trailing_dot(self):
        assert not IfcGit.is_valid_ref_format("branch.")

    def test_rejects_trailing_slash(self):
        assert not IfcGit.is_valid_ref_format("branch/")

    def test_rejects_dot_lock_suffix(self):
        assert not IfcGit.is_valid_ref_format("branch.lock")

    def test_rejects_empty_string(self):
        assert not IfcGit.is_valid_ref_format("")

    def test_rejects_at_brace(self):
        assert not IfcGit.is_valid_ref_format("branch@{upstream}")


class TestGetPathDir(NewFile):
    def test_returns_parent_directory(self):
        assert IfcGit.get_path_dir("/some/path/model.ifc") == "/some/path"

    def test_handles_nested_path(self):
        assert IfcGit.get_path_dir("/a/b/c/d.ifc") == "/a/b/c"

    def test_returns_absolute_path(self):
        result = IfcGit.get_path_dir("/a/b/model.ifc")
        assert os.path.isabs(result)


# ---------------------------------------------------------------------------
# File I/O
# ---------------------------------------------------------------------------


class TestDos2Unix(NewFile):
    def test_converts_crlf_to_lf(self):
        with tempfile.NamedTemporaryFile(suffix=".ifc", delete=False, mode="wb") as f:
            f.write(b"line1\r\nline2\r\nline3\r\n")
            path = f.name
        try:
            IfcGit.dos2unix(path)
            with open(path, "rb") as f:
                assert f.read() == b"line1\nline2\nline3\n"
        finally:
            os.unlink(path)

    def test_lf_only_file_is_unchanged(self):
        with tempfile.NamedTemporaryFile(suffix=".ifc", delete=False, mode="wb") as f:
            f.write(b"line1\nline2\nline3\n")
            path = f.name
        try:
            IfcGit.dos2unix(path)
            with open(path, "rb") as f:
                assert f.read() == b"line1\nline2\nline3\n"
        finally:
            os.unlink(path)

    def test_empty_file_unchanged(self):
        with tempfile.NamedTemporaryFile(suffix=".ifc", delete=False, mode="wb") as f:
            f.write(b"")
            path = f.name
        try:
            IfcGit.dos2unix(path)
            with open(path, "rb") as f:
                assert f.read() == b""
        finally:
            os.unlink(path)


# ---------------------------------------------------------------------------
# Git repo initialisation
# ---------------------------------------------------------------------------


class TestInitRepo(NewFile):
    @requires_git
    def test_creates_git_repo(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            IfcGitRepo.repo = None
            IfcGit.init_repo(tmpdir)
            assert IfcGitRepo.repo is not None
            assert os.path.isdir(IfcGitRepo.repo.git_dir)
            IfcGitRepo.repo = None

    @requires_git
    def test_creates_info_attributes_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            IfcGitRepo.repo = None
            IfcGit.init_repo(tmpdir)
            attrs_path = os.path.join(IfcGitRepo.repo.git_dir, "info", "attributes")
            assert os.path.isfile(attrs_path)
            with open(attrs_path) as f:
                assert "*.ifc text" in f.read()
            IfcGitRepo.repo = None


class TestRepoFromPath(NewFile):
    @requires_git
    def test_finds_repo_from_file_in_root(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            IfcGitRepo.repo = None
            repo = _make_repo(tmpdir)
            ifc_path = os.path.join(tmpdir, "model.ifc")
            open(ifc_path, "w").close()
            result = IfcGit.repo_from_path(ifc_path)
            assert result is not None
            assert os.path.abspath(result.working_dir) == os.path.abspath(tmpdir)
            IfcGitRepo.repo = None

    @requires_git
    def test_finds_repo_from_subdirectory(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            IfcGitRepo.repo = None
            _make_repo(tmpdir)
            subdir = os.path.join(tmpdir, "sub", "dir")
            os.makedirs(subdir)
            result = IfcGit.repo_from_path(subdir)
            assert result is not None
            IfcGitRepo.repo = None

    @requires_git
    def test_returns_none_for_path_outside_any_repo(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            IfcGitRepo.repo = None
            # a plain directory with no .git anywhere above it (using /tmp directly
            # is safe since /tmp is not a git repo on this system)
            result = IfcGit.repo_from_path("/nonexistent/path/that/does/not/exist")
            assert result is None
            IfcGitRepo.repo = None


# ---------------------------------------------------------------------------
# Git repo configuration
# ---------------------------------------------------------------------------


class TestConfigInfoAttributes(NewFile):
    @requires_git
    def test_creates_attributes_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = _make_repo(tmpdir)
            IfcGit.config_info_attributes(repo)
            attrs_path = os.path.join(repo.git_dir, "info", "attributes")
            assert os.path.isfile(attrs_path)
            with open(attrs_path) as f:
                assert "*.ifc text" in f.read()

    @requires_git
    def test_does_not_overwrite_existing_attributes(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = _make_repo(tmpdir)
            attrs_path = os.path.join(repo.git_dir, "info", "attributes")
            os.makedirs(os.path.dirname(attrs_path), exist_ok=True)
            with open(attrs_path, "w") as f:
                f.write("*.png binary\n")
            IfcGit.config_info_attributes(repo)
            with open(attrs_path) as f:
                content = f.read()
            assert "*.png binary" in content  # original content preserved


class TestConfigPush(NewFile):
    @requires_git
    def test_sets_push_defaults(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = _make_repo(tmpdir)
            IfcGit.config_push(repo)
            reader = repo.config_reader()
            assert reader.get_value("push", "default") == "current"
            assert reader.get_value("push", "autoSetupRemote") is True

    @requires_git
    def test_does_not_overwrite_existing_push_section(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = _make_repo(tmpdir)
            with repo.config_writer() as w:
                w.set_value("push", "default", "simple")
            IfcGit.config_push(repo)
            reader = repo.config_reader()
            assert reader.get_value("push", "default") == "simple"


# ---------------------------------------------------------------------------
# Branch / tag lookups
# ---------------------------------------------------------------------------


class TestBranchesByHexsha(NewFile):
    @requires_git
    def test_maps_head_commit_to_active_branch(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = _make_repo(tmpdir)
            _commit_ifc(repo, tmpdir, "#1=IFCPROJECT('abc',$,$,$,$,$,$,$,$);\n", "init")
            result = IfcGit.branches_by_hexsha(repo)
            head_sha = repo.head.commit.hexsha
            assert head_sha in result
            names = [b.name for b in result[head_sha]]
            assert repo.active_branch.name in names

    @requires_git
    def test_returns_empty_dict_when_no_commits(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = _make_repo(tmpdir)
            result = IfcGit.branches_by_hexsha(repo)
            assert result == {}

    @requires_git
    def test_includes_both_branches_when_pointing_to_same_commit(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = _make_repo(tmpdir)
            _commit_ifc(repo, tmpdir, "#1=IFCPROJECT('abc',$,$,$,$,$,$,$,$);\n", "init")
            repo.create_head("feature")
            result = IfcGit.branches_by_hexsha(repo)
            head_sha = repo.head.commit.hexsha
            names = [b.name for b in result[head_sha]]
            assert len(names) == 2


class TestTagsByHexsha(NewFile):
    @requires_git
    def test_returns_empty_dict_when_no_tags(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = _make_repo(tmpdir)
            _commit_ifc(repo, tmpdir, "#1=IFCPROJECT('abc',$,$,$,$,$,$,$,$);\n", "init")
            assert IfcGit.tags_by_hexsha(repo) == {}

    @requires_git
    def test_maps_commit_to_annotated_tag(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = _make_repo(tmpdir)
            _commit_ifc(repo, tmpdir, "#1=IFCPROJECT('abc',$,$,$,$,$,$,$,$);\n", "init")
            repo.create_tag("v1.0", message="Release 1.0")
            result = IfcGit.tags_by_hexsha(repo)
            head_sha = repo.head.commit.hexsha
            assert head_sha in result
            assert result[head_sha][0].name == "v1.0"

    @requires_git
    def test_maps_commit_to_lightweight_tag(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = _make_repo(tmpdir)
            _commit_ifc(repo, tmpdir, "#1=IFCPROJECT('abc',$,$,$,$,$,$,$,$);\n", "init")
            repo.create_tag("v0.1")
            result = IfcGit.tags_by_hexsha(repo)
            head_sha = repo.head.commit.hexsha
            assert head_sha in result


class TestDeleteTag(NewFile):
    @requires_git
    def test_removes_existing_tag(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = _make_repo(tmpdir)
            _commit_ifc(repo, tmpdir, "#1=IFCPROJECT('abc',$,$,$,$,$,$,$,$);\n", "init")
            repo.create_tag("v1.0")
            IfcGit.delete_tag(repo, "v1.0")
            assert "v1.0" not in [t.name for t in repo.tags]

    @requires_git
    def test_does_not_raise_for_nonexistent_tag(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = _make_repo(tmpdir)
            _commit_ifc(repo, tmpdir, "#1=IFCPROJECT('abc',$,$,$,$,$,$,$,$);\n", "init")
            IfcGit.delete_tag(repo, "does-not-exist")  # must not raise


# ---------------------------------------------------------------------------
# IFC diff parsing
# ---------------------------------------------------------------------------


class TestIfcDiffIds(NewFile):
    @requires_git
    def test_detects_modified_entity(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = _make_repo(tmpdir)
            sha_a = _commit_ifc(repo, tmpdir, "#1=IFCPROJECT('abc',$,$,$,$,$,$,$,$);\n", "init")
            ifc_path = os.path.join(tmpdir, "model.ifc")
            sha_b = _commit_ifc(repo, tmpdir, "#1=IFCPROJECT('xyz',$,$,$,$,$,$,$,$);\n", "update")
            result = IfcGit.ifc_diff_ids(repo, sha_a, sha_b, ifc_path)
            assert 1 in result["modified"]
            assert result["added"] == set()
            assert result["removed"] == set()

    @requires_git
    def test_detects_added_entity(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = _make_repo(tmpdir)
            sha_a = _commit_ifc(repo, tmpdir, "#1=IFCPROJECT('abc',$,$,$,$,$,$,$,$);\n", "init")
            ifc_path = os.path.join(tmpdir, "model.ifc")
            sha_b = _commit_ifc(
                repo,
                tmpdir,
                "#1=IFCPROJECT('abc',$,$,$,$,$,$,$,$);\n#2=IFCSITE('new',$,$,$,$,$,$,$,$,$,$,$,$);\n",
                "add site",
            )
            result = IfcGit.ifc_diff_ids(repo, sha_a, sha_b, ifc_path)
            assert 2 in result["added"]
            assert 1 not in result["modified"]
            assert result["removed"] == set()

    @requires_git
    def test_detects_removed_entity(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = _make_repo(tmpdir)
            sha_a = _commit_ifc(repo, tmpdir, "#1=IFCPROJECT('abc',$,$,$,$,$,$,$,$);\n", "init")
            ifc_path = os.path.join(tmpdir, "model.ifc")
            sha_b = _commit_ifc(repo, tmpdir, "", "clear")
            result = IfcGit.ifc_diff_ids(repo, sha_a, sha_b, ifc_path)
            assert 1 in result["removed"]
            assert result["added"] == set()
            assert result["modified"] == set()

    @requires_git
    def test_no_changes_between_identical_commits(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = _make_repo(tmpdir)
            sha = _commit_ifc(repo, tmpdir, "#1=IFCPROJECT('abc',$,$,$,$,$,$,$,$);\n", "init")
            ifc_path = os.path.join(tmpdir, "model.ifc")
            result = IfcGit.ifc_diff_ids(repo, sha, sha, ifc_path)
            assert result["modified"] == set()
            assert result["added"] == set()
            assert result["removed"] == set()

    @requires_git
    def test_diff_against_working_tree_with_none_hash_a(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = _make_repo(tmpdir)
            _commit_ifc(repo, tmpdir, "#1=IFCPROJECT('abc',$,$,$,$,$,$,$,$);\n", "init")
            ifc_path = os.path.join(tmpdir, "model.ifc")
            # Make an uncommitted change in working tree
            with open(ifc_path, "w") as f:
                f.write("#1=IFCPROJECT('xyz',$,$,$,$,$,$,$,$);\n")
            result = IfcGit.ifc_diff_ids(repo, None, "HEAD", ifc_path)
            assert 1 in result["modified"]

    @requires_git
    def test_handles_multiple_changed_entities(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = _make_repo(tmpdir)
            sha_a = _commit_ifc(
                repo,
                tmpdir,
                "#1=IFCPROJECT('abc',$,$,$,$,$,$,$,$);\n#2=IFCSITE('s',$,$,$,$,$,$,$,$,$,$,$,$);\n",
                "init",
            )
            ifc_path = os.path.join(tmpdir, "model.ifc")
            sha_b = _commit_ifc(
                repo,
                tmpdir,
                "#1=IFCPROJECT('xyz',$,$,$,$,$,$,$,$);\n#2=IFCSITE('t',$,$,$,$,$,$,$,$,$,$,$,$);\n",
                "update both",
            )
            result = IfcGit.ifc_diff_ids(repo, sha_a, sha_b, ifc_path)
            assert 1 in result["modified"]
            assert 2 in result["modified"]


# ---------------------------------------------------------------------------
# Merge conflict report — store / clear / get
# ---------------------------------------------------------------------------


class TestStoreClearGetMergeConflicts(NewFile):
    def test_round_trip(self):
        conflicts = [{"type": "attribute_conflict", "entity_id": 42}]
        IfcGit.store_merge_conflicts(conflicts)
        result = IfcGit.get_merge_conflicts()
        assert result == conflicts

    def test_get_returns_none_when_empty(self):
        IfcGit.clear_merge_conflicts()
        assert IfcGit.get_merge_conflicts() is None

    def test_clear_removes_stored_conflicts(self):
        IfcGit.store_merge_conflicts([{"type": "class_changed"}])
        IfcGit.clear_merge_conflicts()
        assert IfcGit.get_merge_conflicts() is None

    def test_get_returns_none_on_corrupt_json(self):
        import bpy

        bpy.context.scene.IfcGitProperties.merge_conflicts = "not valid json {"
        assert IfcGit.get_merge_conflicts() is None


# ---------------------------------------------------------------------------
# git_mergetool — report file reading
# ---------------------------------------------------------------------------


class TestGitMergetool:
    @requires_git
    def test_returns_none_when_report_file_absent(self):
        import unittest.mock as mock

        with tempfile.TemporaryDirectory() as tmpdir:
            ifc_path = os.path.join(tmpdir, "model.ifc")
            mock_repo = mock.MagicMock()
            IfcGitRepo.repo = mock_repo
            result = IfcGit.git_mergetool("ifcmerge", ifc_path)
            assert result is None
            IfcGitRepo.repo = None

    @requires_git
    def test_returns_none_when_report_file_empty(self):
        import unittest.mock as mock

        with tempfile.TemporaryDirectory() as tmpdir:
            ifc_path = os.path.join(tmpdir, "model.ifc")
            report_path = ifc_path + ".ifcmerge"
            open(report_path, "w").close()
            mock_repo = mock.MagicMock()
            IfcGitRepo.repo = mock_repo
            result = IfcGit.git_mergetool("ifcmerge", ifc_path)
            assert result is None
            assert not os.path.exists(report_path)
            IfcGitRepo.repo = None

    @requires_git
    def test_parses_conflict_report_and_deletes_file(self):
        import json
        import unittest.mock as mock

        with tempfile.TemporaryDirectory() as tmpdir:
            ifc_path = os.path.join(tmpdir, "model.ifc")
            report_path = ifc_path + ".ifcmerge"
            conflicts = [{"type": "attribute_conflict", "entity_id": 5}]
            with open(report_path, "w") as f:
                json.dump({"status": "failed", "conflicts": conflicts}, f)
            mock_repo = mock.MagicMock()
            mock_repo.git.mergetool.side_effect = git.exc.GitCommandError("mergetool", 1)
            IfcGitRepo.repo = mock_repo
            result = IfcGit.git_mergetool("ifcmerge", ifc_path)
            assert result == conflicts
            assert not os.path.exists(report_path)
            IfcGitRepo.repo = None


# ---------------------------------------------------------------------------
# config_ifcmerge — cmd format and update
# ---------------------------------------------------------------------------


class TestConfigIfcmerge:
    @requires_git
    def test_writes_redirect_cmd_on_first_call(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = _make_repo(tmpdir)
            IfcGitRepo.repo = repo
            IfcGit.config_ifcmerge()
            reader = repo.config_reader()
            cmd = reader.get_value('mergetool "ifcmerge"', "cmd")
            assert "> $MERGED.ifcmerge" in cmd
            IfcGitRepo.repo = None

    @requires_git
    def test_updates_cmd_missing_redirect(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = _make_repo(tmpdir)
            IfcGitRepo.repo = repo
            with repo.config_writer() as w:
                w.set_value('mergetool "ifcmerge"', "cmd", "ifcmerge $BASE $LOCAL $REMOTE $MERGED")
                w.set_value('mergetool "ifcmerge"', "trustExitCode", True)
            IfcGit.config_ifcmerge()
            reader = repo.config_reader()
            cmd = reader.get_value('mergetool "ifcmerge"', "cmd")
            assert "> $MERGED.ifcmerge" in cmd
            IfcGitRepo.repo = None

    @requires_git
    def test_forward_tool_writes_redirect_cmd(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = _make_repo(tmpdir)
            IfcGitRepo.repo = repo
            IfcGit.config_ifcmerge()
            reader = repo.config_reader()
            cmd = reader.get_value('mergetool "ifcmerge-forward"', "cmd")
            assert "--prioritise-local" in cmd
            assert "> $MERGED.ifcmerge" in cmd
            IfcGitRepo.repo = None
