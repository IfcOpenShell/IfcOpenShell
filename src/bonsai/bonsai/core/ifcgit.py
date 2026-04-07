# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
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

from __future__ import annotations

import platform
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import bpy
    import git

    import bonsai.tool as tool


def create_repo(ifcgit: type[tool.IfcGit], ifc: type[tool.Ifc]) -> None:
    path_ifc = ifc.get_path()
    path_dir = ifcgit.get_path_dir(path_ifc)
    ifcgit.init_repo(path_dir)


def add_file(ifcgit: type[tool.IfcGit], ifc: type[tool.Ifc]) -> None:
    path_ifc = ifc.get_path()
    repo = ifcgit.repo_from_path(path_ifc)
    ifcgit.add_file_to_repo(repo, path_ifc)


def clone_repo(ifcgit: type[tool.IfcGit], remote_url: str, local_folder: str, operator: bpy.types.Operator) -> None:
    repo = ifcgit.clone_repo(remote_url, local_folder)
    if not repo:
        operator.report({"ERROR"}, "Clone failed")
        return
    operator.report({"INFO"}, "Repository cloned")
    ifcgit.load_anyifc(repo)


def discard_uncommitted(ifcgit: type[tool.IfcGit], ifc: type[tool.Ifc]) -> None:
    path_ifc = ifc.get_path()
    # NOTE this is calling the git binary in a subprocess
    ifcgit.git_checkout(path_ifc)
    ifcgit.load_project(path_ifc)


def commit_changes(
    ifcgit: type[tool.IfcGit], ifc: type[tool.Ifc], commit_message: str, new_branch_name: str = ""
) -> None:
    """Commit and create new branches as required"""
    path_ifc = ifc.get_path()

    if ifcgit.is_head_detached():
        ifcgit.git_commit(path_ifc, commit_message)
        ifcgit.create_new_branch(new_branch_name)
    else:
        if new_branch_name:
            ifcgit.checkout_new_branch(path_ifc, new_branch_name)
        ifcgit.git_commit(path_ifc, commit_message)


def add_tag(ifcgit: type[tool.IfcGit], repo: git.Repo, hexsha: str, tag_name: str, tag_message: str = "") -> None:
    ifcgit.add_tag(repo, hexsha, tag_name, tag_message)


def delete_tag(ifcgit: type[tool.IfcGit], repo: git.Repo, tag_name: git.TagReference) -> None:
    ifcgit.delete_tag(repo, tag_name)


def add_remote(ifcgit: type[tool.IfcGit], repo: git.Repo, remote_name: str, remote_url: str) -> None:
    ifcgit.add_remote(repo, remote_name, remote_url)


def delete_remote(ifcgit: type[tool.IfcGit], repo: git.Repo, remote_name: str) -> None:
    ifcgit.delete_remote(repo, remote_name)


def rename_branch(ifcgit: type[tool.IfcGit], repo: git.Repo, new_name: str) -> None:
    ifcgit.rename_branch(repo, new_name)


def push(ifcgit: type[tool.IfcGit], repo: git.Repo, remote_name: str, operator: bpy.types.Operator) -> None:
    error_message = ifcgit.push(repo, remote_name, ifcgit.get_active_branch_name())
    if error_message:
        operator.report({"ERROR"}, error_message)


def refresh_revision_list(ifcgit: type[tool.IfcGit], ifc: type[tool.Ifc]) -> None:
    ifcgit.clear_merge_conflicts()
    if ifcgit.repo_has_commits():
        ifcgit.refresh_revision_list(ifc.get_path())


def colourise_revision(ifcgit: type[tool.IfcGit]) -> None:

    step_ids = ifcgit.get_revisions_step_ids()
    if not step_ids:
        return
    modified_step_ids = ifcgit.get_modified_step_ids(step_ids)
    final_step_ids = ifcgit.update_step_ids(step_ids, modified_step_ids)
    ifcgit.colourise(final_step_ids)


def colourise_uncommitted(ifcgit: type[tool.IfcGit], ifc: type[tool.Ifc], repo: git.Repo) -> None:
    path_ifc = ifc.get_path()
    step_ids = ifcgit.ifc_diff_ids(repo, None, "HEAD", path_ifc)
    if not step_ids:
        return
    modified_step_ids = ifcgit.get_modified_step_ids(step_ids)
    final_step_ids = ifcgit.update_step_ids(step_ids, modified_step_ids)
    ifcgit.colourise(final_step_ids)


def switch_revision(ifcgit: type[tool.IfcGit], ifc: type[tool.Ifc]) -> None:
    # FIXME bad things happen when switching to a revision that predates current project

    path_ifc = ifc.get_path()
    ifcgit.switch_to_revision_item()
    ifcgit.load_project(path_ifc)
    ifcgit.refresh_revision_list(path_ifc)
    ifcgit.decolourise()


def merge_branch(ifcgit: type[tool.IfcGit], ifc: type[tool.Ifc], operator: bpy.types.Operator) -> bool | None:
    path_ifc = ifc.get_path()
    ifcgit.config_ifcmerge()

    branch_name = ifcgit.get_selected_branch()
    if branch_name is None:
        return

    mergetool = ifcgit.get_merge_tool(branch_name)
    merge_result = ifcgit.git_merge(branch_name)

    if merge_result == "error":
        operator.report({"ERROR"}, "Unknown IFC Merge failure")
        return False
    elif merge_result == "conflict":
        conflicts = ifcgit.git_mergetool(mergetool, path_ifc)
        if conflicts is not None:
            ifcgit.git_merge_abort()
            if conflicts:
                ifcgit.store_merge_conflicts(conflicts)
                operator.report({"WARNING"}, "Merge failed — see the conflict report in the panel below")
            else:
                operator.report({"ERROR"}, "Merge tool failed — check that ifcmerge is installed correctly")
            return False
        ifcgit.commit_merge(path_ifc)

    ifcgit.clear_merge_conflicts()
    ifcgit.set_display_branch()
    ifcgit.git_checkout(path_ifc)
    ifcgit.load_project(path_ifc)
    ifcgit.refresh_revision_list(path_ifc)
    ifcgit.decolourise()


def dry_run_merge(ifcgit: type[tool.IfcGit], ifc: type[tool.Ifc], operator: bpy.types.Operator) -> None:
    path_ifc = ifc.get_path()
    ifcgit.config_ifcmerge()

    branch_name = ifcgit.get_selected_branch()
    if branch_name is None:
        return

    mergetool = ifcgit.get_merge_tool(branch_name)
    merge_result = ifcgit.git_merge_no_commit(branch_name)

    if merge_result == "error":
        try:
            ifcgit.git_merge_abort()
        except Exception:
            pass
        operator.report({"ERROR"}, "Unknown IFC Merge failure")
        return

    if merge_result == "conflict":
        conflicts = ifcgit.git_mergetool(mergetool, path_ifc)
        ifcgit.git_merge_abort()
        if conflicts is not None:
            ifcgit.store_merge_conflicts(conflicts)
            operator.report({"WARNING"}, "Merge preview: conflicts found — see the panel below")
        else:
            ifcgit.clear_merge_conflicts()
            operator.report({"INFO"}, "Merge preview: no conflicts")
    else:
        # Clean merge or already up to date — abort the pending merge state if any
        try:
            ifcgit.git_merge_abort()
        except Exception:
            pass
        ifcgit.clear_merge_conflicts()
        operator.report({"INFO"}, "Merge preview: no conflicts")


def entity_log(ifcgit: type[tool.IfcGit], ifc: type[tool.Ifc], step_id: int, operator: bpy.types.Operator) -> None:
    path_ifc = ifc.get_path()
    log_text = ifcgit.entity_log(path_ifc, step_id)
    # ERROR is only way to display a multi-line message
    operator.report({"ERROR"}, log_text)


def install_git(ifcgit: type[tool.IfcGit], operator: bpy.types.Operator) -> None:
    if platform.system() == "Windows":
        ifcgit.install_git_windows(operator=operator)
    else:
        print("install_git() not implemented")


def fetch(ifcgit: type[tool.IfcGit], remote_name: str) -> None:
    ifcgit.fetch(remote_name)


def run_git_diff(ifcgit: type[tool.IfcGit], operator: bpy.types.Operator, save_to_temp: bool) -> None:
    ifcgit.run_git_diff(operator, save_to_temp)
