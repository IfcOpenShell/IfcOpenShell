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
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    import bpy
    import ifcopenshell
    import bonsai.tool as tool
    import git


def create_repo(ifcgit: tool.IfcGit, ifc: tool.Ifc) -> None:
    path_ifc = ifc.get_path()
    path_dir = ifcgit.get_path_dir(path_ifc)
    ifcgit.init_repo(path_dir)


def add_file(ifcgit: tool.IfcGit, ifc: tool.Ifc) -> None:
    path_ifc = ifc.get_path()
    repo = ifcgit.repo_from_path(path_ifc)
    ifcgit.add_file_to_repo(repo, path_ifc)


def clone_repo(ifcgit: tool.IfcGit, remote_url: str, local_folder: str, operator: bpy.types.Operator) -> None:
    repo = ifcgit.clone_repo(remote_url, local_folder)
    if not repo:
        operator.report({"ERROR"}, "Clone failed")
        return
    operator.report({"INFO"}, "Repository cloned")
    ifcgit.load_anyifc(repo)


def discard_uncommitted(ifcgit: tool.IfcGit, ifc: tool.Ifc) -> None:
    path_ifc = ifc.get_path()
    # NOTE this is calling the git binary in a subprocess
    ifcgit.git_checkout(path_ifc)
    ifcgit.load_project(path_ifc)


def commit_changes(ifcgit: tool.IfcGit, ifc: tool.Ifc, repo: git.Repo) -> None:
    """Commit and create new branches as required"""
    path_ifc = ifc.get_path()

    if repo.head.is_detached:
        ifcgit.git_commit(path_ifc)
        ifcgit.create_new_branch()
    else:
        ifcgit.checkout_new_branch(path_ifc)
        ifcgit.git_commit(path_ifc)


def add_tag(ifcgit: tool.IfcGit, repo: git.Repo) -> None:
    ifcgit.add_tag(repo)


def delete_tag(ifcgit: tool.IfcGit, repo: git.Repo, tag_name: git.TagReference) -> None:
    ifcgit.delete_tag(repo, tag_name)


def add_remote(ifcgit: tool.IfcGit, repo: git.Repo) -> None:
    ifcgit.add_remote(repo)


def delete_remote(ifcgit: tool.IfcGit, repo: git.Repo) -> None:
    ifcgit.delete_remote(repo)


def push(ifcgit: tool.IfcGit, repo: git.Repo, remote_name: str, operator: bpy.types.Operator) -> None:
    error_message = ifcgit.push(repo, remote_name, repo.active_branch.name)
    if error_message:
        operator.report({"ERROR"}, error_message)


def refresh_revision_list(ifcgit: tool.IfcGit, repo: git.Repo, ifc: tool.Ifc) -> None:
    if repo.heads:
        ifcgit.refresh_revision_list(ifc.get_path())


def colourise_revision(ifcgit: tool.IfcGit) -> None:

    step_ids = ifcgit.get_revisions_step_ids()
    if not step_ids:
        return
    modified_shape_object_step_ids = ifcgit.get_modified_shape_object_step_ids(step_ids)
    final_step_ids = ifcgit.update_step_ids(step_ids, modified_shape_object_step_ids)
    ifcgit.colourise(final_step_ids)


def colourise_uncommitted(ifcgit: tool.IfcGit, ifc: tool.Ifc, repo: git.Repo) -> None:
    path_ifc = ifc.get_path()
    step_ids = ifcgit.ifc_diff_ids(repo, None, "HEAD", path_ifc)
    ifcgit.colourise(step_ids)


def switch_revision(ifcgit: tool.IfcGit, ifc: tool.Ifc) -> None:
    # FIXME bad things happen when switching to a revision that predates current project

    path_ifc = ifc.get_path()
    ifcgit.switch_to_revision_item()
    ifcgit.load_project(path_ifc)
    ifcgit.refresh_revision_list(path_ifc)
    ifcgit.decolourise()


def merge_branch(ifcgit: tool.IfcGit, ifc: tool.Ifc, operator: bpy.types.Operator) -> None:
    path_ifc = ifc.get_path()
    ifcgit.config_ifcmerge()
    ifcgit.execute_merge(path_ifc, operator)


def entity_log(ifcgit: tool.IfcGit, ifc: tool.Ifc, step_id: int, operator: bpy.types.Operator) -> None:
    path_ifc = ifc.get_path()
    log_text = ifcgit.entity_log(path_ifc, step_id)
    # ERROR is only way to display a multi-line message
    operator.report({"ERROR"}, log_text)
