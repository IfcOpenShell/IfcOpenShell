import os
import re

# allows git import even if git executable isn't found
os.environ["GIT_PYTHON_REFRESH"] = "quiet"
import git
import bpy
from blenderbim.bim.ifc import IfcStore
import blenderbim.tool as tool


class IfcGit:
    @classmethod
    def init_repo(cls, path_dir):
        IfcGitRepo.repo = git.Repo.init(path_dir)

    @classmethod
    def get_path_dir(cls, path_ifc):
        return os.path.abspath(os.path.dirname(path_ifc))

    @classmethod
    def repo_from_path(cls, path):
        """Returns a Git repository object or None"""

        if os.path.isdir(path):
            path_dir = os.path.abspath(path)
        elif os.path.isfile(path):
            path_dir = os.path.abspath(os.path.dirname(path))
        else:
            return None

        if IfcGitRepo.repo != None and IfcGitRepo.repo.working_dir == path_dir:
            return IfcGitRepo.repo

        try:
            repo = git.Repo(path_dir)
        except:
            parentdir_path = os.path.abspath(os.path.join(path_dir, os.pardir))
            if parentdir_path == path_dir:
                # root folder
                return None
            return IfcGit.repo_from_path(parentdir_path)
        if repo:
            IfcGitRepo.repo = repo
        return repo

    @classmethod
    def add_file_to_repo(cls, repo, path_file):
        repo.index.add(path_file)
        repo.index.commit(
            message="Added " + os.path.relpath(path_file, repo.working_dir)
        )
        bpy.ops.ifcgit.refresh()

    @classmethod
    def git_checkout(cls, path_file):
        IfcGitRepo.repo.git.checkout(path_file)

    @classmethod
    def git_commit(cls, path_file):
        props = bpy.context.scene.IfcGitProperties
        repo = IfcGitRepo.repo
        repo.index.add(path_file)
        repo.index.commit(message=props.commit_message)
        props.commit_message = ""
        return repo

    @classmethod
    def create_new_branch(cls):
        props = bpy.context.scene.IfcGitProperties
        repo = IfcGitRepo.repo
        new_branch = repo.create_head(props.new_branch_name)
        new_branch.checkout()
        props.display_branch = props.new_branch_name
        props.new_branch_name = ""

        bpy.ops.ifcgit.refresh()

    @classmethod
    def clear_commits_list(cls):
        area = next(area for area in bpy.context.screen.areas if area.type == "VIEW_3D")
        area.spaces[0].shading.color_type = "MATERIAL"
        props = bpy.context.scene.IfcGitProperties

        # ifcgit_commits is registered list widget
        props.ifcgit_commits.clear()

    @classmethod
    def get_commits_list(cls, path_ifc, lookup):

        props = bpy.context.scene.IfcGitProperties
        commits = list(
            git.objects.commit.Commit.iter_items(
                repo=IfcGitRepo.repo,
                rev=[props.display_branch],
            )
        )
        commits_relevant = list(
            git.objects.commit.Commit.iter_items(
                repo=IfcGitRepo.repo,
                rev=[props.display_branch],
                paths=[path_ifc],
            )
        )

        for commit in commits:

            if props.ifcgit_filter == "tagged" and not commit.hexsha in lookup:
                continue
            elif props.ifcgit_filter == "relevant" and not commit in commits_relevant:
                continue

            props.ifcgit_commits.add()
            props.ifcgit_commits[-1].hexsha = commit.hexsha
            if commit in commits_relevant:
                props.ifcgit_commits[-1].relevant = True

    @classmethod
    def is_valid_ref_format(cls, string):
        """Check a bare branch or tag name is valid"""

        return re.match(
            "^(?!\.| |-|/)((?!\.\.)(?!.*/\.)(/\*|/\*/)*(?!@\{)[^\~\:\^\\\ \?*\[])+(?<!\.|/)(?<!\.lock)$",
            string,
        )

    @classmethod
    def load_project(cls, path_ifc):
        """Clear and load an ifc project"""

        IfcStore.purge()
        # delete any IfcProject/* collections
        for collection in bpy.data.collections:
            if re.match("^IfcProject/", collection.name):
                IfcGit.delete_collection(collection)
        # delete any Ifc* objects not in IfcProject/ heirarchy
        for obj in bpy.data.objects:
            if re.match("^Ifc", obj.name):
                bpy.data.objects.remove(obj, do_unlink=True)

        bpy.data.orphans_purge(do_recursive=True)

        bpy.ops.bim.load_project(filepath=path_ifc)
        bpy.ops.ifcgit.refresh()

    @classmethod
    def branches_by_hexsha(cls, repo):
        """reverse lookup for branches"""

        result = {}
        for branch in repo.branches:
            if branch.commit.hexsha in result:
                result[branch.commit.hexsha].append(branch)
            else:
                result[branch.commit.hexsha] = [branch]
        return result

    @classmethod
    def tags_by_hexsha(cls, repo):
        """reverse lookup for tags"""

        result = {}
        for tag in repo.tags:
            if tag.commit.hexsha in result:
                result[tag.commit.hexsha].append(tag)
            else:
                result[tag.commit.hexsha] = [tag]
        return result

    @classmethod
    def ifc_diff_ids(cls, repo, hash_a, hash_b, path_ifc):
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
    def get_revisions_step_ids(cls):

        path_ifc = bpy.data.scenes["Scene"].BIMProperties.ifc_file
        props = bpy.context.scene.IfcGitProperties
        repo = IfcGitRepo.repo
        item = props.ifcgit_commits[props.commit_index]

        selected_revision = repo.commit(rev=item.hexsha)
        current_revision = repo.commit()

        if selected_revision == current_revision:
            area = next(
                area for area in bpy.context.screen.areas if area.type == "VIEW_3D"
            )
            area.spaces[0].shading.color_type = "MATERIAL"
            return

        if current_revision.committed_date > selected_revision.committed_date:
            step_ids = IfcGit.ifc_diff_ids(
                repo,
                selected_revision.hexsha,
                current_revision.hexsha,
                path_ifc,
            )
        else:
            step_ids = IfcGit.ifc_diff_ids(
                repo,
                current_revision.hexsha,
                selected_revision.hexsha,
                path_ifc,
            )
        return step_ids

    @classmethod
    def get_modified_shape_object_step_ids(cls, step_ids):
        model = tool.Ifc.get()
        modified_shape_object_step_ids = {"modified": []}

        for step_id in step_ids["modified"]:
            if model.by_id(step_id).is_a() == "IfcProductDefinitionShape":
                product = model.by_id(step_id).ShapeOfProduct[0]
                modified_shape_object_step_ids["modified"].append(product.id())

        return modified_shape_object_step_ids

    @classmethod
    def update_step_ids(cls, step_ids, modified_shape_object_step_ids):

        final_step_ids = {}
        final_step_ids["added"] = step_ids["added"]
        final_step_ids["removed"] = step_ids["removed"]
        final_step_ids["modified"] = step_ids["modified"].union(
            modified_shape_object_step_ids["modified"]
        )
        return final_step_ids

    @classmethod
    def colourise(cls, step_ids):
        area = next(area for area in bpy.context.screen.areas if area.type == "VIEW_3D")
        area.spaces[0].shading.color_type = "OBJECT"

        for obj in bpy.context.visible_objects:
            if not obj.BIMObjectProperties.ifc_definition_id:
                continue
            step_id = obj.BIMObjectProperties.ifc_definition_id
            if step_id in step_ids["modified"]:
                obj.color = (0.3, 0.3, 1.0, 1)
            elif step_id in step_ids["added"]:
                obj.color = (0.2, 0.8, 0.2, 1)
            elif step_id in step_ids["removed"]:
                obj.color = (1.0, 0.2, 0.2, 1)
            else:
                obj.color = (1.0, 1.0, 1.0, 0.5)

    @classmethod
    def switch_to_revision_item(cls):
        props = bpy.context.scene.IfcGitProperties
        repo = IfcGitRepo.repo
        item = props.ifcgit_commits[props.commit_index]

        lookup = IfcGit.branches_by_hexsha(repo)
        if item.hexsha in lookup:
            for branch in lookup[item.hexsha]:
                if branch.name == props.display_branch:
                    branch.checkout()
        else:
            # NOTE this is calling the git binary in a subprocess
            repo.git.checkout(item.hexsha)

    @classmethod
    def delete_collection(cls, blender_collection):
        for obj in blender_collection.objects:
            bpy.data.objects.remove(obj, do_unlink=True)
        bpy.data.collections.remove(blender_collection)
        for collection in bpy.data.collections:
            if not collection.users:
                bpy.data.collections.remove(collection)

    @classmethod
    def is_valid_branch_name(cls, new_branch_name):
        """Check if a branch name is valid and doesn't conflict with existing branches"""
        if not IfcGit.is_valid_ref_format(new_branch_name):
            return False
        if new_branch_name in [branch.name for branch in IfcGitRepo.repo.branches]:
            return False
        return True

    @classmethod
    def config_ifcmerge(cls):
        config_reader = IfcGitRepo.repo.config_reader()
        section = 'mergetool "ifcmerge"'
        if not config_reader.has_section(section):
            config_writer = IfcGitRepo.repo.config_writer()
            config_writer.set_value(
                section, "cmd", "ifcmerge $BASE $LOCAL $REMOTE $MERGED"
            )
            config_writer.set_value(section, "trustExitCode", True)

    @classmethod
    def execute_merge(cls, path_ifc, operator):
        props = bpy.context.scene.IfcGitProperties
        repo = IfcGitRepo.repo
        item = props.ifcgit_commits[props.commit_index]
        lookup = IfcGit.branches_by_hexsha(repo)
        if item.hexsha in lookup:
            for branch in lookup[item.hexsha]:
                if branch.name == props.display_branch:
                    # this is a branch!
                    try:
                        # NOTE this is calling the git binary in a subprocess
                        repo.git.merge(branch)
                    except git.exc.GitCommandError:
                        # merge is expected to fail, run ifcmerge
                        try:
                            repo.git.mergetool(tool="ifcmerge")
                        except:
                            # ifcmerge failed, rollback
                            repo.git.merge(abort=True)
                            # FIXME need to report errors somehow

                            operator.report({"ERROR"}, "IFC Merge failed")
                            return False
                    except:

                        operator.report({"ERROR"}, "Unknown IFC Merge failure")
                        return False

            repo.index.add(path_ifc)
            props.commit_message = "Merged branch: " + props.display_branch
            props.display_branch = repo.active_branch.name

            IfcGit.load_project(path_ifc)


class IfcGitRepo:
    repo = None
