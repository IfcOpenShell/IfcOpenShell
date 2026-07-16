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

import json
import logging
import os
import re
import subprocess
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING, Any, Union

import bpy

import bonsai.core.tool
import bonsai.tool as tool
from bonsai.bim import import_ifc
from bonsai.bim.ifc import IfcStore

# allows git import even if git executable isn't found
os.environ["GIT_PYTHON_REFRESH"] = "quiet"
try:
    import git
    import git.exc
    import git.objects
except ImportError:
    print("Warning: GitPython not available.")

if TYPE_CHECKING:
    import git
    import git.exc
    import git.objects

    from bonsai.bim.module.ifcgit.prop import IfcGitProperties


class IfcGit(bonsai.core.tool.IfcGit):
    STEP_IDS = dict[str, set[int]]

    @classmethod
    def get_ifcgit_props(cls) -> IfcGitProperties:
        assert (scene := bpy.context.scene)
        return scene.IfcGitProperties

    @classmethod
    def init_repo(cls, path_dir: str) -> None:
        IfcGitRepo.repo = git.Repo.init(path_dir)
        cls.config_info_attributes(IfcGitRepo.repo)

    @classmethod
    def clone_repo(cls, remote_url: str, local_folder: str) -> git.Repo:
        repo = git.Repo.clone_from(
            url=remote_url,
            to_path=local_folder,
        )
        # Close the repo to release stale subprocess
        repo.close()
        IfcGitRepo.repo = git.Repo(local_folder)
        cls.config_info_attributes(IfcGitRepo.repo)
        return IfcGitRepo.repo

    @classmethod
    def load_anyifc(cls, repo: git.Repo) -> bool:
        working_dir = repo.working_dir
        for item in os.listdir(working_dir):
            path = os.path.join(working_dir, item)
            if os.path.isfile(path) and re.match(".*\\.ifc$", path, re.IGNORECASE):
                cls.load_project(path)
                return True
        return False

    @classmethod
    def get_path_dir(cls, path_ifc: str) -> str:
        return os.path.abspath(os.path.dirname(path_ifc))

    @classmethod
    def repo_from_path(cls, path: str) -> Union[git.Repo, None]:
        """Returns a Git repository object or None"""

        if os.path.isdir(path):
            path_dir = os.path.abspath(path)
        elif os.path.isfile(path):
            path_dir = os.path.abspath(os.path.dirname(path))
        else:
            return None

        if (
            IfcGitRepo.repo is not None
            and os.path.exists(IfcGitRepo.repo.git_dir)
            and IfcGitRepo.repo.working_dir == path_dir
        ):
            return IfcGitRepo.repo

        try:
            repo = git.Repo(path_dir)
        except git.exc.InvalidGitRepositoryError:
            parentdir_path = os.path.abspath(os.path.join(path_dir, os.pardir))
            if parentdir_path == path_dir:
                # root folder
                IfcGitRepo.repo = None
                return None
            return cls.repo_from_path(parentdir_path)
        except git.exc.NoSuchPathError:
            IfcGitRepo.repo = None
            return None
        if repo:
            IfcGitRepo.repo = repo
        return repo

    @classmethod
    def add_file_to_repo(cls, repo: git.Repo, path_file: str) -> None:
        if os.name == "nt":
            cls.dos2unix(path_file)
        repo.index.add(os.path.normpath(path_file))
        repo.index.commit(message="Added " + os.path.relpath(path_file, repo.working_dir))

    @classmethod
    def git_checkout(cls, path_file: str) -> None:
        IfcGitRepo.repo.git.checkout(path_file)

    @classmethod
    def checkout_new_branch(cls, path_file: str, branch_name: str) -> None:
        """Create a branch and move uncommitted changes to this branch"""
        IfcGitRepo.repo.git.checkout(b=branch_name)

    @classmethod
    def git_commit(cls, path_file: str, commit_message: str) -> None:
        repo = IfcGitRepo.repo
        if os.name == "nt":
            cls.dos2unix(path_file)
        repo.index.add(os.path.normpath(path_file))
        repo.index.commit(message=commit_message)

    @classmethod
    def add_tag(cls, repo: git.Repo, hexsha: str, tag_name: str, tag_message: str = "") -> None:
        repo.create_tag(tag_name, ref=hexsha, message=tag_message)

    @classmethod
    def delete_tag(cls, repo: git.Repo, tag_name: git.TagReference) -> None:
        if tag_name in repo.tags:
            repo.delete_tag(tag_name)

    @classmethod
    def rename_branch(cls, repo: git.Repo, new_name: str) -> None:
        repo.active_branch.rename(new_name)

    @classmethod
    def add_remote(cls, repo: git.Repo, remote_name: str, remote_url: str) -> None:
        repo.create_remote(name=remote_name, url=remote_url)

    @classmethod
    def delete_remote(cls, repo: git.Repo, remote_name: str) -> None:
        if remote_name in repo.remotes:
            repo.delete_remote(remote_name)

    @classmethod
    def push(cls, repo: git.Repo, remote_name: str, branch_name: str) -> Union[str, None]:
        cls.config_push(repo)
        remote = repo.remotes[remote_name]
        try:
            remote.push(tags=True, refspec=branch_name).raise_if_error()
        except git.exc.GitCommandError as exc:
            return exc.stderr

    @classmethod
    def is_head_detached(cls) -> bool:
        return bool(IfcGitRepo.repo.head.is_detached)

    @classmethod
    def repo_has_commits(cls) -> bool:
        if IfcGitRepo.repo:
            return bool(IfcGitRepo.repo.heads)
        return False

    @classmethod
    def get_active_branch_name(cls) -> str:
        return IfcGitRepo.repo.active_branch.name

    @classmethod
    def create_new_branch(cls, branch_name: str) -> None:
        """Convert a detached HEAD into a branch"""
        repo = IfcGitRepo.repo
        new_branch = repo.create_head(branch_name)
        new_branch.checkout()

    @classmethod
    def clear_commits_list(cls) -> None:
        props = cls.get_ifcgit_props()

        # ifcgit_commits is registered list widget
        props.ifcgit_commits.clear()

    @classmethod
    def get_commits_list(cls, path_ifc: str, lookup: dict[str, Any]) -> None:

        props = cls.get_ifcgit_props()
        repo = cls.repo_from_path(path_ifc)
        commits = list(
            git.objects.commit.Commit.iter_items(
                repo=repo,
                rev=[props.display_branch],
            )
        )
        commits_relevant = set(
            git.objects.commit.Commit.iter_items(
                repo=repo,
                rev=[props.display_branch],
                paths=[path_ifc],
            )
        )

        def is_relevant(commit):
            if commit in commits_relevant:
                return True
            # Merge commits are relevant too
            return len(commit.parents) > 1 and any(p in commits_relevant for p in commit.parents)

        for commit in commits:

            if props.ifcgit_filter == "tagged" and commit.hexsha not in lookup:
                continue
            elif props.ifcgit_filter == "relevant" and not is_relevant(commit):
                continue

            props.ifcgit_commits.add()
            list_item = props.ifcgit_commits[-1]
            list_item.hexsha = commit.hexsha
            list_item.message = commit.message
            list_item.author_name = commit.author.name
            list_item.author_email = commit.author.email
            list_item.committed_date = int(commit.committed_date)
            if is_relevant(commit):
                list_item.relevant = True
            if commit.hexsha in lookup:
                for tag in lookup[commit.hexsha]:
                    list_item.tags.add()
                    list_item.tags[-1].name = tag.name
                    if tag.tag:
                        # a lightweight tag has no message
                        list_item.tags[-1].message = tag.tag.message

    @classmethod
    def refresh_revision_list(cls, path_ifc: str) -> None:
        repo = cls.repo_from_path(path_ifc)
        cls.clear_commits_list()
        lookup = cls.tags_by_hexsha(repo)
        cls.get_commits_list(path_ifc, lookup)

    @classmethod
    def is_valid_ref_format(cls, string: str) -> Union[re.Match[str], None]:
        """Check a bare branch or tag name is valid"""

        return re.match(
            "^(?!\\.| |-|/)((?!\\.\\.)(?!.*/\\.)(/\\*|/\\*/)*(?!@\\{)[^\\~\\:\\^\\\\ \\?*\\[])+(?<!\\.|/)(?<!\\.lock)$",
            string,
        )

    @classmethod
    def load_project(cls, path_ifc: str = "") -> None:
        """Clear and load an ifc project"""

        if path_ifc:
            IfcStore.purge()
        # delete any IfcProject/* collections
        for collection in bpy.data.collections:
            if re.match("^IfcProject/", collection.name):
                cls.delete_collection(collection)
        # delete any Ifc* objects not in IfcProject/ heirarchy
        for obj in bpy.data.objects:
            if re.match("^Ifc", obj.name):
                bpy.data.objects.remove(obj, do_unlink=True)

        bpy.data.orphans_purge(do_recursive=True)

        import bonsai.bim.handler
        from bonsai.bim.module.model.data import AuthoringData
        from bonsai.bim.module.root.data import IfcClassData

        AuthoringData.type_thumbnails = {}

        IfcClassData.is_loaded = False

        settings = import_ifc.IfcImportSettings.factory(bpy.context, path_ifc, logging.getLogger("ImportIFC"))
        settings.should_setup_viewport_camera = False
        ifc_importer = import_ifc.IfcImporter(settings)
        ifc_importer.execute()
        tool.Project.load_default_thumbnails()
        tool.Project.set_default_context()
        tool.Project.set_default_modeling_dimensions()
        tool.Root.reload_grid_decorator()
        bonsai.bim.handler.refresh_ui_data()
        bpy.ops.object.select_all(action="DESELECT")

    @classmethod
    def branches_by_hexsha(cls, repo: git.Repo) -> dict[str, Any]:
        """reverse lookup for branches"""

        result = {}
        for branch in repo.branches:
            if branch.commit.hexsha in result:
                result[branch.commit.hexsha].append(branch)
            else:
                result[branch.commit.hexsha] = [branch]
        if repo.remotes:
            for remote in repo.remotes:
                for ref in remote.refs:
                    if ref.commit.hexsha in result:
                        result[ref.commit.hexsha].append(ref)
                    else:
                        result[ref.commit.hexsha] = [ref]
        return result

    @classmethod
    def tags_by_hexsha(cls, repo: git.Repo) -> dict[str, Any]:
        """reverse lookup for tags"""

        result = {}
        for tag in repo.tags:
            if tag.commit.hexsha in result:
                result[tag.commit.hexsha].append(tag)
            else:
                result[tag.commit.hexsha] = [tag]
        return result

    @classmethod
    def ifc_diff_ids(cls, repo: git.Repo, hash_a: str, hash_b: str, path_ifc: str) -> STEP_IDS:
        """Given two revision hashes and a filename, retrieve"""
        """step-ids of modified, added and removed entities"""

        # NOTE this is calling the git binary in a subprocess
        if not hash_a:
            diff_lines = repo.git.diff(hash_b, path_ifc).split("\n")
        else:
            diff_lines = repo.git.diff(hash_a, hash_b, path_ifc).split("\n")

        inserted = set()
        deleted = set()
        for line in diff_lines:
            re_search = re.search(r"^\+#([0-9]+)=", line)
            if re_search:
                inserted.add(int(re_search.group(1)))
                continue
            re_search = re.search(r"^-#([0-9]+)=", line)
            if re_search:
                deleted.add(int(re_search.group(1)))

        modified = inserted.intersection(deleted)

        return {
            "modified": modified,
            "added": inserted.difference(modified),
            "removed": deleted.difference(modified),
        }

    @classmethod
    def get_revisions_step_ids(cls) -> Union[STEP_IDS, None]:
        props = tool.Blender.get_bim_props()
        path_ifc = tool.Blender.get_bim_props().ifc_file
        props = cls.get_ifcgit_props()
        repo = IfcGitRepo.repo
        item = props.ifcgit_commits[props.commit_index]

        selected_revision = repo.commit(rev=item.hexsha)
        current_revision = repo.commit()

        if selected_revision == current_revision:
            cls.decolourise()
            return

        if current_revision.committed_date > selected_revision.committed_date:
            step_ids = cls.ifc_diff_ids(
                repo,
                selected_revision.hexsha,
                current_revision.hexsha,
                path_ifc,
            )
        else:
            step_ids = cls.ifc_diff_ids(
                repo,
                current_revision.hexsha,
                selected_revision.hexsha,
                path_ifc,
            )
        return step_ids

    @classmethod
    def get_modified_step_ids(cls, step_ids: STEP_IDS) -> STEP_IDS:
        model = tool.Ifc.get()
        modified_step_ids = {"modified": set()}

        def collect(entity, depth=0):
            if depth > 2:
                return
            if entity.is_a("IfcProduct"):
                modified_step_ids["modified"].add(entity.id())
            elif entity.is_a("IfcProductDefinitionShape"):
                for product in entity.ShapeOfProduct:
                    modified_step_ids["modified"].add(product.id())
            elif entity.is_a("IfcObjectPlacement"):
                for product in entity.PlacesObject:
                    modified_step_ids["modified"].add(product.id())
            elif entity.is_a("IfcTypeProduct"):
                for rel in entity.Types:
                    for obj in rel.RelatedObjects:
                        modified_step_ids["modified"].add(obj.id())
            elif entity.is_a("IfcShapeRepresentation"):
                for prod_rep in entity.OfProductRepresentation:
                    for product in prod_rep.ShapeOfProduct:
                        modified_step_ids["modified"].add(product.id())
            elif entity.is_a("IfcRepresentationItem"):
                for referencing in model.get_inverse(entity):
                    if referencing.is_a("IfcShapeRepresentation"):
                        collect(referencing, depth + 1)
            elif entity.is_a("IfcPropertySet"):
                for rel in entity.DefinesOccurrence:
                    for obj in rel.RelatedObjects:
                        modified_step_ids["modified"].add(obj.id())
            elif entity.is_a("IfcProperty"):
                for pset in entity.PartOfPset:
                    collect(pset, depth + 1)

        for step_id in step_ids["modified"] | step_ids["added"]:
            try:
                entity = model.by_id(step_id)
            except:
                continue
            collect(entity)

        return modified_step_ids

    @classmethod
    def update_step_ids(cls, step_ids: STEP_IDS, modified_step_ids: STEP_IDS) -> STEP_IDS:

        final_step_ids = {}
        final_step_ids["added"] = step_ids["added"]
        final_step_ids["removed"] = step_ids["removed"]
        final_step_ids["modified"] = (
            step_ids["modified"].union(modified_step_ids["modified"]).difference(step_ids["added"])
        )
        return final_step_ids

    @classmethod
    def colourise(cls, step_ids: STEP_IDS) -> None:
        area = tool.Blender.get_view3d_area()
        area.spaces[0].shading.color_type = "OBJECT"
        bpy.ops.object.select_all(action="DESELECT")

        for obj in bpy.context.visible_objects:
            props = tool.Blender.get_object_bim_props(obj)
            if not (step_id := props.ifc_definition_id):
                continue
            if step_id in step_ids["modified"]:
                obj.color = (0.3, 0.3, 1.0, 1)
                obj.select_set(True)
            elif step_id in step_ids["added"]:
                obj.color = (0.2, 0.8, 0.2, 1)
                obj.select_set(True)
            elif step_id in step_ids["removed"]:
                obj.color = (1.0, 0.2, 0.2, 1)
                obj.select_set(True)
            else:
                obj.color = (1.0, 1.0, 1.0, 0.5)

    @classmethod
    def decolourise(cls) -> None:
        area = tool.Blender.get_view3d_area()
        area.spaces[0].shading.color_type = "MATERIAL"

    @classmethod
    def switch_to_revision_item(cls) -> None:
        props = cls.get_ifcgit_props()
        repo = IfcGitRepo.repo
        item = props.ifcgit_commits[props.commit_index]

        lookup = cls.branches_by_hexsha(repo)
        if item.hexsha in lookup:
            for branch in lookup[item.hexsha]:
                if branch.name == props.display_branch:
                    if isinstance(branch, git.RemoteReference):
                        # Checking out a remote branch tip goes to detached HEAD.
                        # Pre-fill the new branch name field with the local equivalent
                        # so the user isn't blocked from committing without a hint.
                        local_name = branch.remote_head
                        props.new_branch_name = cls._unique_branch_name(repo, local_name)
                    branch.checkout()
                    return
        # NOTE this is calling the git binary in a subprocess
        repo.git.checkout(item.hexsha)

    @classmethod
    def _unique_branch_name(cls, repo: git.Repo, name: str) -> str:
        """Return name if unused, otherwise name-2, name-3, etc."""
        existing = {h.name for h in repo.heads}
        if name not in existing:
            return name
        i = 2
        while f"{name}-{i}" in existing:
            i += 1
        return f"{name}-{i}"

    @classmethod
    def delete_collection(cls, blender_collection: bpy.types.Collection) -> None:
        for obj in blender_collection.objects:
            bpy.data.objects.remove(obj, do_unlink=True)
        bpy.data.collections.remove(blender_collection)

    @classmethod
    def config_ifcmerge(cls) -> None:
        config_reader = IfcGitRepo.repo.config_reader()
        section = 'mergetool "ifcmerge"'
        new_cmd = "ifcmerge $BASE $LOCAL $REMOTE $MERGED > $MERGED.ifcmerge"
        if not config_reader.has_section(section):
            with IfcGitRepo.repo.config_writer() as config_writer:
                config_writer.set_value(section, "cmd", new_cmd)
                config_writer.set_value(section, "trustExitCode", True)
        elif config_reader.get_value(section, "cmd") != new_cmd:
            with IfcGitRepo.repo.config_writer() as config_writer:
                config_writer.set_value(section, "cmd", new_cmd)
                config_writer.set_value(section, "trustExitCode", True)
        section = 'mergetool "ifcmerge-forward"'
        new_cmd = "ifcmerge --prioritise-local $BASE $LOCAL $REMOTE $MERGED > $MERGED.ifcmerge"
        if not config_reader.has_section(section):
            with IfcGitRepo.repo.config_writer() as config_writer:
                config_writer.set_value(section, "cmd", new_cmd)
                config_writer.set_value(section, "trustExitCode", True)
        elif config_reader.get_value(section, "cmd") != new_cmd:
            with IfcGitRepo.repo.config_writer() as config_writer:
                config_writer.set_value(section, "cmd", new_cmd)
                config_writer.set_value(section, "trustExitCode", True)

    @classmethod
    def config_push(cls, repo: git.Repo) -> None:
        """Set push.autoSetupRemote"""
        config_reader = repo.config_reader()
        if not config_reader.has_section("push"):
            with repo.config_writer() as config_writer:
                config_writer.set_value("push", "default", "current")
                config_writer.set_value("push", "autoSetupRemote", True)

    @classmethod
    def config_info_attributes(cls, repo: git.Repo) -> None:
        """Set IFC files as text in .git/info/attributes"""
        path_attributes = os.path.join(repo.git_dir, "info", "attributes")
        if not os.path.exists(path_attributes):
            with open(path_attributes, "w") as f:
                # attributes patterns are case-insensitive
                f.write("*.ifc text")

    @classmethod
    def dos2unix(cls, path_file: str) -> None:
        with open(path_file, "rb") as infile:
            content = infile.read()
        with open(path_file, "wb") as output:
            for line in content.splitlines():
                output.write(line + b"\n")

    @classmethod
    def get_selected_branch(cls) -> Union[str, None]:
        """Return the name of the branch at the selected commit matching display_branch, or None."""
        props = cls.get_ifcgit_props()
        repo = IfcGitRepo.repo
        item = props.ifcgit_commits[props.commit_index]
        lookup = cls.branches_by_hexsha(repo)
        if item.hexsha not in lookup:
            return None
        for branch in lookup[item.hexsha]:
            if branch.name == props.display_branch:
                return branch.name
        return None

    @classmethod
    def get_merge_tool(cls, branch_name: str) -> str:
        if re.match("^(origin/)?(HEAD|main|master)$", branch_name):
            return "ifcmerge"
        return "ifcmerge-forward"

    @classmethod
    def git_merge(cls, branch_name: str) -> Union[str, None]:
        """Attempt a git merge. Returns None on clean merge, 'conflict' on expected
        GitCommandError, or 'error' on an unknown GitError."""
        repo = IfcGitRepo.repo
        branch = repo.refs[branch_name]
        try:
            repo.git.merge(branch)
            return None
        except git.exc.GitCommandError:
            return "conflict"
        except git.exc.GitError:
            return "error"

    @classmethod
    def git_merge_no_commit(cls, branch_name: str) -> Union[str, None]:
        """Attempt a git merge without committing (always leaves a merge state to abort).
        Returns None on clean merge, 'conflict' on conflict, or 'error' on unknown failure."""
        repo = IfcGitRepo.repo
        branch = repo.refs[branch_name]
        try:
            repo.git.merge(branch, no_commit=True, no_ff=True)
            return None
        except git.exc.GitCommandError:
            return "conflict"
        except git.exc.GitError:
            return "error"

    @classmethod
    def git_mergetool(cls, mergetool: str, path_ifc: str) -> Union[list, None]:
        """Run ifcmerge tool. Returns None on success, list of conflict dicts on failure."""
        repo = IfcGitRepo.repo
        report_path = path_ifc + ".ifcmerge"
        try:
            repo.git.mergetool(tool=mergetool)
        except git.exc.GitCommandError as e:
            print(f"ifcgit: mergetool failed: {e}")

        conflicts = None
        if os.path.exists(report_path):
            try:
                with open(report_path) as f:
                    content = f.read().strip()
                if content:
                    data = json.loads(content)
                    conflicts = data.get("conflicts", [])
            except (json.JSONDecodeError, OSError):
                pass
            try:
                os.remove(report_path)
            except OSError:
                pass

        if conflicts is None and repo.index.unmerged_blobs():
            conflicts = []

        return conflicts

    @classmethod
    def store_merge_conflicts(cls, conflicts: list) -> None:
        cls.get_ifcgit_props().merge_conflicts = json.dumps(conflicts)

    @classmethod
    def clear_merge_conflicts(cls) -> None:
        cls.get_ifcgit_props().merge_conflicts = ""

    @classmethod
    def get_merge_conflicts(cls) -> Union[list, None]:
        raw = cls.get_ifcgit_props().merge_conflicts
        if not raw:
            return None
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return None

    @classmethod
    def git_merge_abort(cls) -> None:
        IfcGitRepo.repo.git.merge(abort=True)

    @classmethod
    def commit_merge(cls, path_ifc: str) -> None:
        repo = IfcGitRepo.repo
        if os.name == "nt":
            cls.dos2unix(path_ifc)
        repo.index.add(os.path.normpath(path_ifc))
        repo.git.commit("--no-edit")

    @classmethod
    def set_display_branch(cls) -> None:
        props = cls.get_ifcgit_props()
        props.display_branch = IfcGitRepo.repo.active_branch.name

    @classmethod
    def entity_log(cls, path_ifc: str, step_id: int) -> str:
        """Raw git log for this entity"""
        repo = IfcGitRepo.repo
        if not repo:
            return "No repository found :("
        relpath_ifc = os.path.relpath(path_ifc, repo.working_dir)
        # regex only returns first match
        query = "/^#" + str(step_id) + "[ =]/,/;/:" + relpath_ifc
        try:
            logtext = repo.git.log("-L", query, "-s")
        except git.exc.CommandError:
            logtext = "No Git history found :("
        return logtext

    @classmethod
    def install_git_windows(cls, operator: bpy.types.Operator) -> None:
        """Command to install Git on Windows using winget"""
        command = ["winget", "install", "--id", "Git.Git", "-e", "--source", "winget"]
        try:
            subprocess.check_output(command)
        except subprocess.CalledProcessError as e:
            operator.report({"ERROR"}, f"Called Process Error occurred: {e}")
        except FileNotFoundError:
            operator.report({"ERROR"}, "Winget is not available. Make sure Windows Package Manager is installed.")

    @classmethod
    def select_first_remote(cls) -> None:
        props = cls.get_ifcgit_props()
        repo = IfcGitRepo.repo
        if repo and repo.remotes:
            props.select_remote = repo.remotes[0].name

    @classmethod
    def fetch(cls, remote_name: str) -> None:
        repo = IfcGitRepo.repo
        repo.remotes[remote_name].fetch()

    @classmethod
    def run_git_diff(cls, operator: bpy.types.Operator, save_to_temp: bool) -> None:
        path = tool.Ifc.get_path()
        ifc_file = tool.Ifc.get()
        ifc_str = ifc_file.to_string()

        color = "never" if save_to_temp else "always"
        # Avoid `text=True` as it's causing issues with colorful output.
        try:
            subprocess.check_output(
                ("git", "diff", "--no-index", f"--color={color}", "--", path, "-"),
                input=ifc_str.encode(),
            )
        except subprocess.CalledProcessError as e:
            if e.returncode == 1:
                if save_to_temp:
                    temp_path = Path(tempfile.gettempdir()) / "bonsai.diff"
                    temp_path.write_bytes(e.stdout)
                    operator.report({"INFO"}, f"Git diff output is saved to {temp_path}.")
                else:
                    print(e.stdout.decode())
                    operator.report({"INFO"}, "See system console for git diff output.")
                return
            print(e.output)
            raise Exception("Error running git diff, see system console.")

        operator.report({"INFO"}, "No changes since last save.")


class IfcGitRepo:
    repo: git.Repo = None
