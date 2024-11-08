import os
import re
import bpy
import bonsai.core.ifcgit as core
import bonsai.tool as tool
from bonsai.bim.module.ifcgit.data import IfcGitData, refresh


class CreateRepo(bpy.types.Operator):
    """Initialise a Git repository"""

    bl_label = "Create Git repository"
    bl_idname = "ifcgit.createrepo"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        IfcGitData.make_sure_is_loaded()
        path_ifc = IfcGitData.data["path_ifc"]
        if not path_ifc or not os.path.isfile(path_ifc):
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
        IfcGitData.make_sure_is_loaded()
        path_ifc = IfcGitData.data["path_ifc"]
        if not path_ifc or not os.path.isfile(path_ifc):
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
        props.remote_url = ""
        refresh()
        return {"FINISHED"}


class DiscardUncommitted(bpy.types.Operator):
    """Discard saved changes and update to HEAD"""

    bl_label = "Discard uncommitted changes"
    bl_idname = "ifcgit.discard"
    bl_options = {"REGISTER"}

    def execute(self, context):

        core.discard_uncommitted(tool.IfcGit, tool.Ifc)
        refresh()
        tool.IfcGit.decolourise()
        return {"FINISHED"}


class CommitChanges(bpy.types.Operator):
    """Commit current saved changes"""

    bl_label = "Commit changes"
    bl_idname = "ifcgit.commit_changes"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        IfcGitData.make_sure_is_loaded()
        props = context.scene.IfcGitProperties
        repo = IfcGitData.data["repo"]
        if props.commit_message == "":
            return False
        if repo:
            if props.new_branch_name in [branch.name for branch in repo.branches]:
                cls.poll_message_set("Branch already exists!")
                return False
            elif not tool.IfcGit.is_valid_ref_format(props.new_branch_name):
                if repo.head.is_detached:
                    cls.poll_message_set("Branch name is invalid or empty!")
                    return False
                elif props.new_branch_name != "":
                    cls.poll_message_set("Branch name is invalid!")
                    return False
        return True

    def execute(self, context):

        repo = IfcGitData.data["repo"]
        core.commit_changes(tool.IfcGit, tool.Ifc, repo)
        core.refresh_revision_list(tool.IfcGit, repo, tool.Ifc)
        refresh()
        return {"FINISHED"}


class AddTag(bpy.types.Operator):
    """Tag selected revision"""

    bl_label = "Tag selected revision"
    bl_idname = "ifcgit.add_tag"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        IfcGitData.make_sure_is_loaded()
        props = context.scene.IfcGitProperties
        if props.new_tag_name == "":
            return False
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
        core.refresh_revision_list(tool.IfcGit, repo, tool.Ifc)
        refresh()
        return {"FINISHED"}


class DeleteTag(bpy.types.Operator):
    """Delete a tag"""

    bl_label = "Delete tag"
    bl_idname = "ifcgit.delete_tag"
    bl_options = {"REGISTER"}
    tag_name: bpy.props.StringProperty()

    def execute(self, context):

        repo = IfcGitData.data["repo"]
        core.delete_tag(tool.IfcGit, repo, self.tag_name)
        core.refresh_revision_list(tool.IfcGit, repo, tool.Ifc)
        refresh()
        return {"FINISHED"}


class RefreshGit(bpy.types.Operator):
    """Refresh revision list"""

    bl_label = ""
    bl_idname = "ifcgit.refresh"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        IfcGitData.make_sure_is_loaded()
        repo = IfcGitData.data["repo"]
        if repo:
            return True
        return False

    def execute(self, context):

        repo = IfcGitData.data["repo"]
        core.refresh_revision_list(tool.IfcGit, repo, tool.Ifc)
        refresh()
        tool.IfcGit.decolourise()
        return {"FINISHED"}


class DisplayRevision(bpy.types.Operator):
    """Colourise objects by selected revision"""

    bl_label = ""
    bl_idname = "ifcgit.display_revision"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        props = context.scene.IfcGitProperties
        if props.ifcgit_commits:
            return True

    def execute(self, context):

        core.colourise_revision(tool.IfcGit)
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

    @classmethod
    def poll(cls, context):
        props = context.scene.IfcGitProperties
        if props.ifcgit_commits:
            return True

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
        IfcGitData.make_sure_is_loaded()
        props = context.scene.IfcGitProperties
        if IfcGitData.data["ifcmerge_exe"] and props.ifcgit_commits and not IfcGitData.data["is_detached"]:
            return True
        return False

    def execute(self, context):

        if core.merge_branch(tool.IfcGit, tool.Ifc, self):
            refresh()
            return {"FINISHED"}
        else:
            return {"CANCELLED"}


class Push(bpy.types.Operator):
    """Pushes the working branch to selected remote"""

    bl_label = "Push working branch"
    bl_idname = "ifcgit.push"
    bl_options = {"REGISTER"}

    def execute(self, context):

        props = context.scene.IfcGitProperties
        repo = IfcGitData.data["repo"]
        core.push(tool.IfcGit, repo, props.select_remote, self)
        return {"FINISHED"}


class Fetch(bpy.types.Operator):
    """Fetches from the selected remote"""

    bl_label = "Fetch from remote"
    bl_idname = "ifcgit.fetch"
    bl_options = {"REGISTER"}

    def execute(self, context):

        props = context.scene.IfcGitProperties
        repo = IfcGitData.data["repo"]
        remote = repo.remotes[props.select_remote]
        remote.fetch()
        return {"FINISHED"}


class AddRemote(bpy.types.Operator):
    """Add a remote repository"""

    bl_label = "Add Remote"
    bl_idname = "ifcgit.add_remote"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        IfcGitData.make_sure_is_loaded()
        props = context.scene.IfcGitProperties
        repo = IfcGitData.data["repo"]
        if (
            not repo
            or not tool.IfcGit.is_valid_ref_format(props.remote_name)
            or not props.remote_url
            or props.remote_name in [remote.name for remote in repo.remotes]
        ):
            return False
        return True

    def execute(self, context):

        repo = IfcGitData.data["repo"]
        core.add_remote(tool.IfcGit, repo)
        core.refresh_revision_list(tool.IfcGit, repo, tool.Ifc)
        refresh()
        return {"FINISHED"}


class DeleteRemote(bpy.types.Operator):
    """Delete the selected remote"""

    bl_label = "Delete Remote"
    bl_idname = "ifcgit.delete_remote"
    bl_options = {"REGISTER"}

    def execute(self, context):

        repo = IfcGitData.data["repo"]
        core.delete_remote(tool.IfcGit, repo)
        core.refresh_revision_list(tool.IfcGit, repo, tool.Ifc)
        refresh()
        return {"FINISHED"}


class ObjectLog(bpy.types.Operator):
    """Displays Git log of selected object"""

    bl_label = "Selected Object History"
    bl_idname = "ifcgit.object_log"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        if not context.active_object:
            cls.poll_message_set("No Active Object")
        elif not context.active_object.BIMObjectProperties.ifc_definition_id:
            cls.poll_message_set("Active Object doesn't have an IFC definition")
        else:
            return True

    def execute(self, context):

        step_id = context.active_object.BIMObjectProperties.ifc_definition_id
        core.entity_log(tool.IfcGit, tool.Ifc, step_id, self)
        return {"FINISHED"}
