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

import pytest

import bonsai.core.ifcgit as subject
from test.core.bootstrap import ifc, ifcgit


class MockOperator:
    def __init__(self):
        self.reports = []

    def report(self, level, message):
        self.reports.append((level, message))


class TestCreateRepo:
    def test_run(self, ifcgit, ifc):
        ifc.get_path().should_be_called().will_return("path/to/model.ifc")
        ifcgit.get_path_dir("path/to/model.ifc").should_be_called().will_return("path/to")
        ifcgit.init_repo("path/to").should_be_called()
        subject.create_repo(ifcgit, ifc)


class TestAddFile:
    def test_run(self, ifcgit, ifc):
        ifc.get_path().should_be_called().will_return("path/to/model.ifc")
        ifcgit.repo_from_path("path/to/model.ifc").should_be_called().will_return("repo")
        ifcgit.add_file_to_repo("repo", "path/to/model.ifc").should_be_called()
        subject.add_file(ifcgit, ifc)


class TestCloneRepo:
    def test_successful_clone(self, ifcgit):
        ifcgit.clone_repo("http://example.com/repo.git", "/local/folder").should_be_called().will_return("repo")
        ifcgit.load_anyifc("repo").should_be_called()
        op = MockOperator()
        subject.clone_repo(ifcgit, "http://example.com/repo.git", "/local/folder", operator=op)
        assert op.reports == [({"INFO"}, "Repository cloned")]

    def test_failed_clone_reports_error(self, ifcgit):
        ifcgit.clone_repo("http://example.com/repo.git", "/local/folder").should_be_called().will_return(None)
        op = MockOperator()
        subject.clone_repo(ifcgit, "http://example.com/repo.git", "/local/folder", operator=op)
        assert op.reports == [({"ERROR"}, "Clone failed")]


class TestDiscardUncommitted:
    def test_run(self, ifcgit, ifc):
        ifc.get_path().should_be_called().will_return("path/to/model.ifc")
        ifcgit.git_checkout("path/to/model.ifc").should_be_called()
        ifcgit.load_project("path/to/model.ifc").should_be_called()
        subject.discard_uncommitted(ifcgit, ifc)


class TestCommitChanges:
    def test_commit_on_branch_without_new_branch(self, ifcgit, ifc):
        ifc.get_path().should_be_called().will_return("path/to/model.ifc")
        ifcgit.is_head_detached().should_be_called().will_return(False)
        ifcgit.git_commit("path/to/model.ifc", "my message").should_be_called()
        subject.commit_changes(ifcgit, ifc, "my message", "")

    def test_commit_on_branch_with_new_branch(self, ifcgit, ifc):
        ifc.get_path().should_be_called().will_return("path/to/model.ifc")
        ifcgit.is_head_detached().should_be_called().will_return(False)
        ifcgit.checkout_new_branch("path/to/model.ifc", "feature").should_be_called()
        ifcgit.git_commit("path/to/model.ifc", "my message").should_be_called()
        subject.commit_changes(ifcgit, ifc, "my message", "feature")

    def test_commit_on_detached_head(self, ifcgit, ifc):
        ifc.get_path().should_be_called().will_return("path/to/model.ifc")
        ifcgit.is_head_detached().should_be_called().will_return(True)
        ifcgit.git_commit("path/to/model.ifc", "my message").should_be_called()
        ifcgit.create_new_branch("feature").should_be_called()
        subject.commit_changes(ifcgit, ifc, "my message", "feature")


class TestAddTag:
    def test_run(self, ifcgit):
        ifcgit.add_tag("repo", "abc123", "v1.0", "Release notes").should_be_called()
        subject.add_tag(ifcgit, "repo", "abc123", "v1.0", "Release notes")


class TestDeleteTag:
    def test_run(self, ifcgit):
        ifcgit.delete_tag("repo", "v1.0").should_be_called()
        subject.delete_tag(ifcgit, "repo", "v1.0")


class TestAddRemote:
    def test_run(self, ifcgit):
        ifcgit.add_remote("repo", "origin", "http://example.com").should_be_called()
        subject.add_remote(ifcgit, "repo", "origin", "http://example.com")


class TestDeleteRemote:
    def test_run(self, ifcgit):
        ifcgit.delete_remote("repo", "origin").should_be_called()
        subject.delete_remote(ifcgit, "repo", "origin")


class TestPush:
    def test_push_succeeds_silently(self, ifcgit):
        ifcgit.get_active_branch_name().should_be_called().will_return("main")
        ifcgit.push("repo", "origin", "main").should_be_called().will_return(None)
        subject.push(ifcgit, "repo", "origin", operator=None)

    def test_push_failure_reports_error(self, ifcgit):
        ifcgit.get_active_branch_name().should_be_called().will_return("main")
        ifcgit.push("repo", "origin", "main").should_be_called().will_return("stderr: rejected")
        op = MockOperator()
        subject.push(ifcgit, "repo", "origin", operator=op)
        assert op.reports == [({"ERROR"}, "stderr: rejected")]


class TestRefreshRevisionList:
    def test_refreshes_when_repo_has_heads(self, ifcgit, ifc):
        ifcgit.clear_merge_conflicts().should_be_called()
        ifcgit.repo_has_commits().should_be_called().will_return(True)
        ifc.get_path().should_be_called().will_return("path/to/model.ifc")
        ifcgit.refresh_revision_list("path/to/model.ifc").should_be_called()
        subject.refresh_revision_list(ifcgit, ifc)

    def test_skips_when_repo_has_no_heads(self, ifcgit, ifc):
        ifcgit.clear_merge_conflicts().should_be_called()
        ifcgit.repo_has_commits().should_be_called().will_return(False)
        subject.refresh_revision_list(ifcgit, ifc)
        # nothing else should be called — Prophecy will verify


class TestColouriseRevision:
    def test_skips_when_no_step_ids(self, ifcgit):
        ifcgit.get_revisions_step_ids().should_be_called().will_return(None)
        subject.colourise_revision(ifcgit)

    def test_colourises_with_step_ids(self, ifcgit):
        ifcgit.get_revisions_step_ids().should_be_called().will_return("step_ids")
        ifcgit.get_modified_step_ids("step_ids").should_be_called().will_return("modified_step_ids")
        ifcgit.update_step_ids("step_ids", "modified_step_ids").should_be_called().will_return("final_step_ids")
        ifcgit.colourise("final_step_ids").should_be_called()
        subject.colourise_revision(ifcgit)


class TestColouriseUncommitted:
    def test_skips_when_no_step_ids(self, ifcgit, ifc):
        ifc.get_path().should_be_called().will_return("path/to/model.ifc")
        ifcgit.ifc_diff_ids("repo", None, "HEAD", "path/to/model.ifc").should_be_called().will_return(None)
        subject.colourise_uncommitted(ifcgit, ifc, "repo")

    def test_colourises_with_step_ids(self, ifcgit, ifc):
        ifc.get_path().should_be_called().will_return("path/to/model.ifc")
        ifcgit.ifc_diff_ids("repo", None, "HEAD", "path/to/model.ifc").should_be_called().will_return("step_ids")
        ifcgit.get_modified_step_ids("step_ids").should_be_called().will_return("modified_step_ids")
        ifcgit.update_step_ids("step_ids", "modified_step_ids").should_be_called().will_return("final_step_ids")
        ifcgit.colourise("final_step_ids").should_be_called()
        subject.colourise_uncommitted(ifcgit, ifc, "repo")


class TestSwitchRevision:
    def test_run(self, ifcgit, ifc):
        ifc.get_path().should_be_called().will_return("path/to/model.ifc")
        ifcgit.switch_to_revision_item().should_be_called()
        ifcgit.load_project("path/to/model.ifc").should_be_called()
        ifcgit.refresh_revision_list("path/to/model.ifc").should_be_called()
        ifcgit.decolourise().should_be_called()
        subject.switch_revision(ifcgit, ifc)


class TestMergeBranch:
    def test_no_branch_at_selected_commit(self, ifcgit, ifc):
        ifc.get_path().should_be_called().will_return("path/to/model.ifc")
        ifcgit.config_ifcmerge().should_be_called()
        ifcgit.get_selected_branch().should_be_called().will_return(None)
        subject.merge_branch(ifcgit, ifc, operator=None)

    def test_clean_merge(self, ifcgit, ifc):
        ifc.get_path().should_be_called().will_return("path/to/model.ifc")
        ifcgit.config_ifcmerge().should_be_called()
        ifcgit.get_selected_branch().should_be_called().will_return("feature")
        ifcgit.get_merge_tool("feature").should_be_called().will_return("ifcmerge-forward")
        ifcgit.git_merge("feature").should_be_called().will_return(None)
        ifcgit.clear_merge_conflicts().should_be_called()
        ifcgit.set_display_branch().should_be_called()
        ifcgit.git_checkout("path/to/model.ifc").should_be_called()
        ifcgit.load_project("path/to/model.ifc").should_be_called()
        ifcgit.refresh_revision_list("path/to/model.ifc").should_be_called()
        ifcgit.decolourise().should_be_called()
        subject.merge_branch(ifcgit, ifc, operator=None)

    def test_conflict_mergetool_success(self, ifcgit, ifc):
        ifc.get_path().should_be_called().will_return("path/to/model.ifc")
        ifcgit.config_ifcmerge().should_be_called()
        ifcgit.get_selected_branch().should_be_called().will_return("feature")
        ifcgit.get_merge_tool("feature").should_be_called().will_return("ifcmerge-forward")
        ifcgit.git_merge("feature").should_be_called().will_return("conflict")
        ifcgit.git_mergetool("ifcmerge-forward", "path/to/model.ifc").should_be_called().will_return(None)
        ifcgit.commit_merge("path/to/model.ifc").should_be_called()
        ifcgit.clear_merge_conflicts().should_be_called()
        ifcgit.set_display_branch().should_be_called()
        ifcgit.git_checkout("path/to/model.ifc").should_be_called()
        ifcgit.load_project("path/to/model.ifc").should_be_called()
        ifcgit.refresh_revision_list("path/to/model.ifc").should_be_called()
        ifcgit.decolourise().should_be_called()
        subject.merge_branch(ifcgit, ifc, operator=None)

    def test_conflict_mergetool_failure(self, ifcgit, ifc):
        conflicts = [{"type": "attribute_conflict", "entity_id": 42}]
        ifc.get_path().should_be_called().will_return("path/to/model.ifc")
        ifcgit.config_ifcmerge().should_be_called()
        ifcgit.get_selected_branch().should_be_called().will_return("feature")
        ifcgit.get_merge_tool("feature").should_be_called().will_return("ifcmerge-forward")
        ifcgit.git_merge("feature").should_be_called().will_return("conflict")
        ifcgit.git_mergetool("ifcmerge-forward", "path/to/model.ifc").should_be_called().will_return(conflicts)
        ifcgit.git_merge_abort().should_be_called()
        ifcgit.store_merge_conflicts(conflicts).should_be_called()
        op = MockOperator()
        subject.merge_branch(ifcgit, ifc, op)
        assert op.reports == [({"WARNING"}, "Merge failed — see the conflict report in the panel below")]

    def test_unknown_merge_error(self, ifcgit, ifc):
        ifc.get_path().should_be_called().will_return("path/to/model.ifc")
        ifcgit.config_ifcmerge().should_be_called()
        ifcgit.get_selected_branch().should_be_called().will_return("feature")
        ifcgit.get_merge_tool("feature").should_be_called().will_return("ifcmerge-forward")
        ifcgit.git_merge("feature").should_be_called().will_return("error")
        op = MockOperator()
        subject.merge_branch(ifcgit, ifc, op)
        assert op.reports == [({"ERROR"}, "Unknown IFC Merge failure")]


class TestDryRunMerge:
    def test_no_branch_at_selected_commit(self, ifcgit, ifc):
        ifc.get_path().should_be_called().will_return("path/to/model.ifc")
        ifcgit.config_ifcmerge().should_be_called()
        ifcgit.get_selected_branch().should_be_called().will_return(None)
        subject.dry_run_merge(ifcgit, ifc, operator=None)

    def test_clean_merge_preview(self, ifcgit, ifc):
        ifc.get_path().should_be_called().will_return("path/to/model.ifc")
        ifcgit.config_ifcmerge().should_be_called()
        ifcgit.get_selected_branch().should_be_called().will_return("feature")
        ifcgit.get_merge_tool("feature").should_be_called().will_return("ifcmerge-forward")
        ifcgit.git_merge_no_commit("feature").should_be_called().will_return(None)
        ifcgit.git_merge_abort().should_be_called()
        ifcgit.clear_merge_conflicts().should_be_called()
        op = MockOperator()
        subject.dry_run_merge(ifcgit, ifc, op)
        assert op.reports == [({"INFO"}, "Merge preview: no conflicts")]

    def test_conflict_preview_shows_report(self, ifcgit, ifc):
        conflicts = [{"type": "attribute_conflict", "entity_id": 42}]
        ifc.get_path().should_be_called().will_return("path/to/model.ifc")
        ifcgit.config_ifcmerge().should_be_called()
        ifcgit.get_selected_branch().should_be_called().will_return("feature")
        ifcgit.get_merge_tool("feature").should_be_called().will_return("ifcmerge-forward")
        ifcgit.git_merge_no_commit("feature").should_be_called().will_return("conflict")
        ifcgit.git_mergetool("ifcmerge-forward", "path/to/model.ifc").should_be_called().will_return(conflicts)
        ifcgit.git_merge_abort().should_be_called()
        ifcgit.store_merge_conflicts(conflicts).should_be_called()
        op = MockOperator()
        subject.dry_run_merge(ifcgit, ifc, op)
        assert op.reports == [({"WARNING"}, "Merge preview: conflicts found — see the panel below")]

    def test_conflict_preview_mergetool_succeeds(self, ifcgit, ifc):
        ifc.get_path().should_be_called().will_return("path/to/model.ifc")
        ifcgit.config_ifcmerge().should_be_called()
        ifcgit.get_selected_branch().should_be_called().will_return("feature")
        ifcgit.get_merge_tool("feature").should_be_called().will_return("ifcmerge-forward")
        ifcgit.git_merge_no_commit("feature").should_be_called().will_return("conflict")
        ifcgit.git_mergetool("ifcmerge-forward", "path/to/model.ifc").should_be_called().will_return(None)
        ifcgit.git_merge_abort().should_be_called()
        ifcgit.clear_merge_conflicts().should_be_called()
        op = MockOperator()
        subject.dry_run_merge(ifcgit, ifc, op)
        assert op.reports == [({"INFO"}, "Merge preview: no conflicts")]


class TestEntityLog:
    def test_run(self, ifcgit, ifc):
        ifc.get_path().should_be_called().will_return("path/to/model.ifc")
        ifcgit.entity_log("path/to/model.ifc", 42).should_be_called().will_return("log text")
        op = MockOperator()
        subject.entity_log(ifcgit, ifc, 42, op)
        assert op.reports == [({"ERROR"}, "log text")]


class TestInstallGit:
    def test_windows(self, ifcgit):
        import unittest.mock as mock

        with mock.patch("platform.system", return_value="Windows"):
            ifcgit.install_git_windows(operator="op").should_be_called()
            subject.install_git(ifcgit, "op")

    def test_non_windows_does_nothing(self, ifcgit):
        import unittest.mock as mock

        with mock.patch("platform.system", return_value="Linux"):
            subject.install_git(ifcgit, "op")
            # no tool method should be called — Prophecy will verify


class TestFetch:
    def test_run(self, ifcgit):
        ifcgit.fetch("origin").should_be_called()
        subject.fetch(ifcgit, "origin")


class TestRunGitDiff:
    def test_run(self, ifcgit):
        ifcgit.run_git_diff("operator", False).should_be_called()
        subject.run_git_diff(ifcgit, "operator", False)
