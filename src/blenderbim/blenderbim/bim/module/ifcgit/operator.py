import os
import re
import bpy
import blenderbim.core.ifcgit as core
import blenderbim.tool as tool
from blenderbim.bim.module.ifcgit.data import IfcGitData, refresh


class CreateRepo(bpy.types.Operator):
    """Initialise a Git repository"""

    bl_label = "Create Git repository"
    bl_idname = "ifcgit.createrepo"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        path_ifc = IfcGitData.data["path_ifc"]
        if not os.path.isfile(path_ifc):
            return False
        if IfcGitData.data["repo"]:
            # repo already exists
            return False
        if re.match("^/home/[^/]+/?$", os.path.dirname(path_ifc)):
            # don't make ${HOME} a repo
            return False
        return True

    def execute(self, context):

        core.create_repo(tool.IfcGit, tool.Ifc)
        refresh()
        return {"FINISHED"}


class AddFileToRepo(bpy.types.Operator):
    """Add a file to a repository"""

    bl_label = "Add file to repository"
    bl_idname = "ifcgit.addfile"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        path_ifc = IfcGitData.data["path_ifc"]
        if not os.path.isfile(path_ifc):
            return False
        if not IfcGitData.data["repo"]:
            # repo doesn't exist
            return False
        return True

    def execute(self, context):

        core.add_file(tool.IfcGit, tool.Ifc)
        refresh()
        return {"FINISHED"}


class CloneRepo(bpy.types.Operator):
    """Clone a remote Git repository"""

    bl_label = "Clone repository"
    bl_idname = "ifcgit.clone_repo"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        props = context.scene.IfcGitProperties
        if (
            props.remote_url
            and props.local_folder
            and os.path.isdir(props.local_folder)
            and not os.listdir(props.local_folder)
        ):
            return True
        return False

    def execute(self, context):

        props = context.scene.IfcGitProperties
        core.clone_repo(tool.IfcGit, props.remote_url, props.local_folder, self)
        refresh()
        return {"FINISHED"}


class DiscardUncommitted(bpy.types.Operator):
    """Discard saved changes and update to HEAD"""

    bl_label = "Discard uncommitted changes"
    bl_idname = "ifcgit.discard"
    bl_options = {"REGISTER"}

    def execute(self, context):

        core.discard_uncomitted(tool.IfcGit, tool.Ifc)
        refresh()
        return {"FINISHED"}


class CommitChanges(bpy.types.Operator):
    """Commit current saved changes"""

    bl_label = "Commit changes"
    bl_idname = "ifcgit.commit_changes"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        props = context.scene.IfcGitProperties
        repo = IfcGitData.data["repo"]
        if props.commit_message == "":
            return False
        if (
            repo
            and repo.head.is_detached
            and (
                not tool.IfcGit.is_valid_ref_format(props.new_branch_name)
                or props.new_branch_name in [branch.name for branch in repo.branches]
            )
        ):
            cls.poll_message_set(
                "The new branch name is invalid, please insert a valid branch name (eg. with no spaces, ...)"
            )
            return False
        return True

    def execute(self, context):

        repo = IfcGitData.data["repo"]
        core.commit_changes(tool.IfcGit, tool.Ifc, repo, context)
        bpy.ops.ifcgit.refresh()
        refresh()
        return {"FINISHED"}


class AddTag(bpy.types.Operator):
    """Tag selected revision"""

    bl_label = "Add tag"
    bl_idname = "ifcgit.add_tag"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        props = context.scene.IfcGitProperties
        repo = IfcGitData.data["repo"]
        if repo and (
            not tool.IfcGit.is_valid_ref_format(props.new_tag_name)
            or props.new_tag_name in [tag.name for tag in repo.tags]
        ):
            return False
        return True

    def execute(self, context):

        repo = IfcGitData.data["repo"]
        core.add_tag(tool.IfcGit, repo)
        bpy.ops.ifcgit.refresh()
        refresh()
        return {"FINISHED"}


class RefreshGit(bpy.types.Operator):
    """Refresh revision list"""

    bl_label = ""
    bl_idname = "ifcgit.refresh"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        repo = IfcGitData.data["repo"]
        if repo != None and repo.heads:
            return True
        return False

    def execute(self, context):

        repo = IfcGitData.data["repo"]
        core.refresh_revision_list(tool.IfcGit, repo, tool.Ifc)
        refresh()
        return {"FINISHED"}


class DisplayRevision(bpy.types.Operator):
    """Colourise objects by selected revision"""

    bl_label = ""
    bl_idname = "ifcgit.display_revision"
    bl_options = {"REGISTER"}

    def execute(self, context):

        core.colourise_revision(tool.IfcGit, context)
        refresh()
        return {"FINISHED"}


class DisplayUncommitted(bpy.types.Operator):
    """Colourise uncommitted objects"""

    bl_label = "Show uncommitted changes"
    bl_idname = "ifcgit.display_uncommitted"
    bl_options = {"REGISTER"}

    def execute(self, context):

        repo = IfcGitData.data["repo"]
        core.colourise_uncommitted(tool.IfcGit, tool.Ifc, repo)
        refresh()
        return {"FINISHED"}


class SwitchRevision(bpy.types.Operator):
    """Switches the repository to the selected revision and reloads the IFC file"""

    bl_label = ""
    bl_idname = "ifcgit.switch_revision"
    bl_options = {"REGISTER"}

    def execute(self, context):

        core.switch_revision(tool.IfcGit, tool.Ifc)
        refresh()
        return {"FINISHED"}


class Merge(bpy.types.Operator):
    """Merges the selected branch into working branch"""

    bl_label = "Merge this branch"
    bl_idname = "ifcgit.merge"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        if IfcGitData.data["ifcmerge_exe"]:
            return True
        return False

    def execute(self, context):

        if core.merge_branch(tool.IfcGit, tool.Ifc, self):
            refresh()
            return {"FINISHED"}
        else:
            return {"CANCELLED"}
