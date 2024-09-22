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
import os
import re
import bpy
import logging
from bonsai.bim import import_ifc
from bonsai.bim.ifc import IfcStore
import bonsai.tool as tool
from typing import TYPE_CHECKING, Union

# allows git import even if git executable isn't found
os.environ["GIT_PYTHON_REFRESH"] = "quiet"
try:
    import git
except ImportError:
    print("Warning: GitPython not available.")

if TYPE_CHECKING:
    import git


class IfcGit:
    STEP_IDS = dict[str, set[int]]

    @classmethod
    def init_repo(cls, path_dir: str) -> None:
        IfcGitRepo.repo = git.Repo.init(path_dir)
        cls.config_info_attributes(IfcGitRepo.repo)

    @classmethod
    def clone_repo(cls, remote_url: str, local_folder: str) -> git.Repo:
        IfcGitRepo.repo = git.Repo.clone_from(
            url=remote_url,
            to_path=local_folder,
        )
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
        bpy.ops.ifcgit.refresh()

    @classmethod
    def git_checkout(cls, path_file: str) -> None:
        IfcGitRepo.repo.git.checkout(path_file)

    @classmethod
    def checkout_new_branch(cls, path_file: str) -> None:
        """Create a branch and move uncommitted changes to this branch"""
        props = bpy.context.scene.IfcGitProperties
        if props.new_branch_name:
            IfcGitRepo.repo.git.checkout(b=props.new_branch_name)
            props.display_branch = props.new_branch_name
            props.new_branch_name = ""
            bpy.ops.ifcgit.refresh()

    @classmethod
    def git_commit(cls, path_file: str) -> None:
        props = bpy.context.scene.IfcGitProperties
        repo = IfcGitRepo.repo
        if os.name == "nt":
            cls.dos2unix(path_file)
        repo.index.add(os.path.normpath(path_file))
        repo.index.commit(message=props.commit_message)
        props.commit_message = ""

    @classmethod
    def add_tag(cls, repo: git.Repo) -> None:
        props = bpy.context.scene.IfcGitProperties
        item = props.ifcgit_commits[props.commit_index]
        repo.create_tag(props.new_tag_name, ref=item.hexsha, message=props.new_tag_message)
        props.new_tag_name = ""
        props.new_tag_message = ""

    @classmethod
    def delete_tag(cls, repo: git.Repo, tag_name: git.TagReference) -> None:
        if tag_name in repo.tags:
            repo.delete_tag(tag_name)

    @classmethod
    def add_remote(cls, repo: git.Repo) -> None:
        props = bpy.context.scene.IfcGitProperties
        repo.create_remote(name=props.remote_name, url=props.remote_url)
        props.remote_name = ""
        props.remote_url = ""

    @classmethod
    def delete_remote(cls, repo: git.Repo) -> None:
        props = bpy.context.scene.IfcGitProperties
        remote_name = props.select_remote
        if remote_name in repo.remotes:
            repo.delete_remote(remote_name)
        if repo.remotes:
            props.select_remote = repo.remotes[0].name

    @classmethod
    def push(cls, repo: git.Repo, remote_name: str, branch_name: str) -> Union[str, None]:
        cls.config_push(repo)
        remote = repo.remotes[remote_name]
        try:
            remote.push(tags=True, refspec=branch_name).raise_if_error()
        except git.exc.GitCommandError as exc:
            return exc.stderr

    @classmethod
    def create_new_branch(cls) -> None:
        """Convert a detached HEAD into a branch"""
        props = bpy.context.scene.IfcGitProperties
        repo = IfcGitRepo.repo
        new_branch = repo.create_head(props.new_branch_name)
        new_branch.checkout()
        props.display_branch = props.new_branch_name
        props.new_branch_name = ""

        bpy.ops.ifcgit.refresh()

    @classmethod
    def clear_commits_list(cls) -> None:
        props = bpy.context.scene.IfcGitProperties

        # ifcgit_commits is registered list widget
        props.ifcgit_commits.clear()

    @classmethod
    def get_commits_list(cls, path_ifc: str, lookup: dict[str, Any]) -> None:

        props = bpy.context.scene.IfcGitProperties
        repo = cls.repo_from_path(path_ifc)
        commits = list(
            git.objects.commit.Commit.iter_items(
                repo=repo,
                rev=[props.display_branch],
            )
        )
        commits_relevant = list(
            git.objects.commit.Commit.iter_items(
                repo=repo,
                rev=[props.display_branch],
                paths=[path_ifc],
            )
        )

        for commit in commits:

            if props.ifcgit_filter == "tagged" and commit.hexsha not in lookup:
                continue
            elif props.ifcgit_filter == "relevant" and commit not in commits_relevant:
                continue

            props.ifcgit_commits.add()
            list_item = props.ifcgit_commits[-1]
            list_item.hexsha = commit.hexsha
            list_item.message = commit.message
            list_item.author_name = commit.author.name
            list_item.author_email = commit.author.email
            if commit in commits_relevant:
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

        settings = import_ifc.IfcImportSettings.factory(bpy.context, path_ifc, logging.getLogger("ImportIFC"))
        settings.should_setup_viewport_camera = False
        ifc_importer = import_ifc.IfcImporter(settings)
        ifc_importer.execute()
        tool.Project.load_pset_templates()
        tool.Project.load_default_thumbnails()
        tool.Project.set_default_context()
        tool.Project.set_default_modeling_dimensions()
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

        path_ifc = bpy.data.scenes["Scene"].BIMProperties.ifc_file
        props = bpy.context.scene.IfcGitProperties
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
    def get_modified_shape_object_step_ids(cls, step_ids: STEP_IDS) -> STEP_IDS:
        model = tool.Ifc.get()
        modified_shape_object_step_ids = {"modified": []}

        for step_id in step_ids["modified"]:
            if model.by_id(step_id).is_a() == "IfcProductDefinitionShape":
                product = model.by_id(step_id).ShapeOfProduct[0]
                modified_shape_object_step_ids["modified"].append(product.id())

        return modified_shape_object_step_ids

    @classmethod
    def update_step_ids(cls, step_ids: STEP_IDS, modified_shape_object_step_ids: STEP_IDS) -> STEP_IDS:

        final_step_ids = {}
        final_step_ids["added"] = step_ids["added"]
        final_step_ids["removed"] = step_ids["removed"]
        final_step_ids["modified"] = step_ids["modified"].union(modified_shape_object_step_ids["modified"])
        return final_step_ids

    @classmethod
    def colourise(cls, step_ids: STEP_IDS) -> None:
        area = next(area for area in bpy.context.screen.areas if area.type == "VIEW_3D")
        area.spaces[0].shading.color_type = "OBJECT"
        bpy.ops.object.select_all(action="DESELECT")

        for obj in bpy.context.visible_objects:
            if not obj.BIMObjectProperties.ifc_definition_id:
                continue
            step_id = obj.BIMObjectProperties.ifc_definition_id
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
        area = next(area for area in bpy.context.screen.areas if area.type == "VIEW_3D")
        area.spaces[0].shading.color_type = "MATERIAL"

    @classmethod
    def switch_to_revision_item(cls) -> None:
        props = bpy.context.scene.IfcGitProperties
        repo = IfcGitRepo.repo
        item = props.ifcgit_commits[props.commit_index]

        lookup = cls.branches_by_hexsha(repo)
        if item.hexsha in lookup:
            for branch in lookup[item.hexsha]:
                if branch.name == props.display_branch:
                    branch.checkout()
                    return
        # NOTE this is calling the git binary in a subprocess
        repo.git.checkout(item.hexsha)

    @classmethod
    def delete_collection(cls, blender_collection: bpy.types.Collection) -> None:
        for obj in blender_collection.objects:
            bpy.data.objects.remove(obj, do_unlink=True)
        bpy.data.collections.remove(blender_collection)

    @classmethod
    def is_valid_branch_name(cls, new_branch_name: str):
        """Check if a branch name is valid and doesn't conflict with existing branches"""
        if not cls.is_valid_ref_format(new_branch_name):
            return False
        if new_branch_name in [branch.name for branch in IfcGitRepo.repo.branches]:
            return False
        return True

    @classmethod
    def config_ifcmerge(cls) -> None:
        config_reader = IfcGitRepo.repo.config_reader()
        section = 'mergetool "ifcmerge"'
        if not config_reader.has_section(section):
            with IfcGitRepo.repo.config_writer() as config_writer:
                config_writer.set_value(section, "cmd", "ifcmerge $BASE $LOCAL $REMOTE $MERGED")
                config_writer.set_value(section, "trustExitCode", True)
        section = 'mergetool "ifcmerge-forward"'
        if not config_reader.has_section(section):
            with IfcGitRepo.repo.config_writer() as config_writer:
                config_writer.set_value(section, "cmd", "ifcmerge $BASE $REMOTE $LOCAL $MERGED")
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
    def execute_merge(cls, path_ifc: str, operator: bpy.types.Operator) -> Union[None, False]:
        props = bpy.context.scene.IfcGitProperties
        repo = IfcGitRepo.repo
        item = props.ifcgit_commits[props.commit_index]
        lookup = cls.branches_by_hexsha(repo)
        if item.hexsha in lookup:
            for branch in lookup[item.hexsha]:
                if branch.name == props.display_branch:
                    # this is a branch!
                    if re.match("^(origin/)?(HEAD|main|master)$", branch.name):
                        # preserve remote IDs in origin/main or main
                        mergetool = "ifcmerge"
                    else:
                        # rewrite remote IDs
                        mergetool = "ifcmerge-forward"
                    try:
                        # NOTE this is calling the git binary in a subprocess
                        repo.git.merge(branch)
                    except git.exc.GitCommandError:
                        # merge is expected to fail, run ifcmerge
                        try:
                            repo.git.mergetool(tool=mergetool)
                        except git.exc.GitCommandError as exc:
                            message = re.sub("(  stderr: '|')", "", exc.stderr)
                            # ifcmerge failed, rollback
                            repo.git.merge(abort=True)

                            operator.report({"ERROR"}, "IFC Merge failed:" + message)
                            return False
                        else:
                            if os.name == "nt":
                                cls.dos2unix(path_ifc)
                            repo.index.add(os.path.normpath(path_ifc))
                            repo.git.commit("--no-edit")
                    except git.exc.GitError:
                        operator.report({"ERROR"}, "Unknown IFC Merge failure")
                        return False

            props.display_branch = repo.active_branch.name

            cls.load_project(path_ifc)
            cls.refresh_revision_list(path_ifc)
            cls.decolourise()

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


class IfcGitRepo:
    repo: git.Repo = None
