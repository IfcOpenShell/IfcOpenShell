import os
import re
from typing import TYPE_CHECKING

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
        props = tool.IfcGit.get_ifcgit_props()
        if (
            props.remote_url
            and props.local_folder
            and os.path.isdir(props.local_folder)
            and not os.listdir(props.local_folder)
        ):
            return True
        return False

    def execute(self, context):

        props = tool.IfcGit.get_ifcgit_props()
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
        props = tool.IfcGit.get_ifcgit_props()
        repo = IfcGitData.data["repo"]
        if props.commit_message == "":
            return False
        if repo:
            if props.new_branch_name in IfcGitData.data["branch_names"]:
                cls.poll_message_set("Branch already exists!")
                return False
            elif not tool.IfcGit.is_valid_ref_format(props.new_branch_name):
                if IfcGitData.data["is_detached"]:
                    cls.poll_message_set("Branch name is invalid or empty!")
                    return False
                elif props.new_branch_name != "":
                    cls.poll_message_set("Branch name is invalid!")
                    return False
        return True

    def execute(self, context):

        props = tool.IfcGit.get_ifcgit_props()
        commit_message = props.commit_message
        new_branch_name = props.new_branch_name
        core.commit_changes(tool.IfcGit, tool.Ifc, commit_message, new_branch_name)
        props.new_branch_name = ""
        props.commit_message = ""
        core.refresh_revision_list(tool.IfcGit, tool.Ifc)
        refresh()
        IfcGitData.load()
        if new_branch_name:
            props.display_branch = new_branch_name
        return {"FINISHED"}


class AddTag(bpy.types.Operator):
    """Tag selected revision"""

    bl_label = "Tag selected revision"
    bl_idname = "ifcgit.add_tag"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        IfcGitData.make_sure_is_loaded()
        props = tool.IfcGit.get_ifcgit_props()
        if props.new_tag_name == "":
            return False
        repo = IfcGitData.data["repo"]
        if repo and (
            not tool.IfcGit.is_valid_ref_format(props.new_tag_name)
            or props.new_tag_name in IfcGitData.data["tag_names"]
        ):
            return False
        return True

    def execute(self, context):

        repo = IfcGitData.data["repo"]
        props = tool.IfcGit.get_ifcgit_props()
        item = props.ifcgit_commits[props.commit_index]
        core.add_tag(tool.IfcGit, repo, item.hexsha, props.new_tag_name, props.new_tag_message)
        props.new_tag_name = ""
        props.new_tag_message = ""
        core.refresh_revision_list(tool.IfcGit, tool.Ifc)
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
        core.refresh_revision_list(tool.IfcGit, tool.Ifc)
        refresh()
        return {"FINISHED"}


class RefreshGit(bpy.types.Operator):
    """Refresh revision list"""

    bl_label = "Refresh"
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

        core.refresh_revision_list(tool.IfcGit, tool.Ifc)
        refresh()
        tool.IfcGit.decolourise()
        return {"FINISHED"}


class DisplayRevision(bpy.types.Operator):
    """Colourise objects by selected revision"""

    bl_label = "Colourise Revision"
    bl_idname = "ifcgit.display_revision"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        props = tool.IfcGit.get_ifcgit_props()
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

    bl_label = "Switch Revision"
    bl_idname = "ifcgit.switch_revision"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        props = tool.IfcGit.get_ifcgit_props()
        if props.ifcgit_commits:
            return True

    def execute(self, context):

        core.switch_revision(tool.IfcGit, tool.Ifc)
        refresh()
        return {"FINISHED"}


class Merge(bpy.types.Operator):
    """Merges the selected branch into working branch.\nCtrl+click to preview without merging"""

    bl_label = "Merge this branch"
    bl_idname = "ifcgit.merge"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        IfcGitData.make_sure_is_loaded()
        props = tool.IfcGit.get_ifcgit_props()
        if IfcGitData.data["ifcmerge_exe"] and props.ifcgit_commits and not IfcGitData.data["is_detached"]:
            return True
        return False

    def invoke(self, context, event):
        if event.ctrl:
            core.dry_run_merge(tool.IfcGit, tool.Ifc, self)
            refresh()
            return {"FINISHED"}
        return self.execute(context)

    def execute(self, context):
        if core.merge_branch(tool.IfcGit, tool.Ifc, self) is not False:
            refresh()
            return {"FINISHED"}
        else:
            return {"CANCELLED"}


class SelectConflictEntity(bpy.types.Operator):
    """Select the conflicting entity in the viewport"""

    bl_label = "Select Conflict Entity"
    bl_idname = "ifcgit.select_conflict_entity"
    bl_options = {"REGISTER"}

    step_id: bpy.props.IntProperty()

    if TYPE_CHECKING:
        step_id: int

    def execute(self, context):
        model = tool.Ifc.get()
        if not model:
            return {"CANCELLED"}

        try:
            entity = model.by_id(self.step_id)
        except Exception:
            self.report({"WARNING"}, f"Entity #{self.step_id} not found (may have been deleted locally)")
            return {"CANCELLED"}

        obj = tool.Ifc.get_object(entity)
        if obj is None:
            # Walk inverse references up to 5 hops to find nearest entity with a Blender object
            visited = {entity.id()}
            queue = [entity]
            for _ in range(5):
                next_queue = []
                for ent in queue:
                    for inv in model.get_inverse(ent):
                        if inv.id() in visited:
                            continue
                        visited.add(inv.id())
                        obj = tool.Ifc.get_object(inv)
                        if obj is not None:
                            break
                        next_queue.append(inv)
                    if obj is not None:
                        break
                if obj is not None:
                    break
                queue = next_queue

        if obj is None:
            self.report({"INFO"}, f"No viewport representation found for #{self.step_id} ({entity.is_a()})")
            return {"CANCELLED"}

        bpy.ops.object.select_all(action="DESELECT")
        obj.select_set(True)
        context.view_layer.objects.active = obj
        for area in context.screen.areas:
            if area.type == "VIEW_3D":
                region = next((r for r in area.regions if r.type == "WINDOW"), None)
                if region:
                    with context.temp_override(area=area, region=region):
                        bpy.ops.view3d.view_selected()
                break

        return {"FINISHED"}


class Push(bpy.types.Operator):
    """Pushes the working branch to selected remote"""

    bl_label = "Push working branch"
    bl_idname = "ifcgit.push"
    bl_options = {"REGISTER"}

    def execute(self, context):
        props = tool.IfcGit.get_ifcgit_props()
        repo = IfcGitData.data["repo"]
        core.push(tool.IfcGit, repo, props.select_remote, self)
        return {"FINISHED"}


class Fetch(bpy.types.Operator):
    """Fetches from the selected remote"""

    bl_label = "Fetch from remote"
    bl_idname = "ifcgit.fetch"
    bl_options = {"REGISTER"}

    def execute(self, context):
        props = tool.IfcGit.get_ifcgit_props()
        core.fetch(tool.IfcGit, props.select_remote)
        core.refresh_revision_list(tool.IfcGit, tool.Ifc)
        refresh()
        return {"FINISHED"}


class AddRemote(bpy.types.Operator):
    """Add a remote repository"""

    bl_label = "Add Remote"
    bl_idname = "ifcgit.add_remote"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        IfcGitData.make_sure_is_loaded()
        props = tool.IfcGit.get_ifcgit_props()
        repo = IfcGitData.data["repo"]
        if (
            not repo
            or not tool.IfcGit.is_valid_ref_format(props.remote_name)
            or not props.remote_url
            or props.remote_name in IfcGitData.data["remote_names"]
        ):
            return False
        return True

    def execute(self, context):

        repo = IfcGitData.data["repo"]
        props = tool.IfcGit.get_ifcgit_props()
        core.add_remote(tool.IfcGit, repo, props.remote_name, props.remote_url)
        props.remote_name = ""
        props.remote_url = ""
        core.refresh_revision_list(tool.IfcGit, tool.Ifc)
        refresh()
        return {"FINISHED"}


class DeleteRemote(bpy.types.Operator):
    """Delete the selected remote"""

    bl_label = "Delete Remote"
    bl_idname = "ifcgit.delete_remote"
    bl_options = {"REGISTER"}

    def execute(self, context):

        repo = IfcGitData.data["repo"]
        props = tool.IfcGit.get_ifcgit_props()
        remote_name = props.select_remote
        if props.display_branch.startswith(remote_name + "/"):
            active = IfcGitData.data["active_branch_name"]
            if active:
                props.display_branch = active
            else:
                local_branches = [b for b in IfcGitData.data["branch_names"] if "/" not in b]
                if local_branches:
                    props.display_branch = local_branches[0]
        core.delete_remote(tool.IfcGit, repo, remote_name)
        tool.IfcGit.select_first_remote()
        core.refresh_revision_list(tool.IfcGit, tool.Ifc)
        refresh()
        return {"FINISHED"}


class ObjectLog(bpy.types.Operator):
    """Displays Git log of selected object"""

    bl_label = "Selected Object History"
    bl_idname = "ifcgit.object_log"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        if not (obj := context.active_object) or not obj.select_get():
            cls.poll_message_set("No selected object")
        elif not tool.Blender.get_ifc_definition_id(obj):
            cls.poll_message_set("Active Object doesn't have an IFC definition")
        else:
            return True

    def execute(self, context):
        obj = context.active_object
        assert obj
        step_id = tool.Blender.get_ifc_definition_id(obj)
        core.entity_log(tool.IfcGit, tool.Ifc, step_id, self)
        return {"FINISHED"}


class InstallGit(bpy.types.Operator):
    """Install Git Version Control System from the
    Windows Package Manager Community Repository,
    requires restarting Blender after installation"""

    bl_label = "Install Git"
    bl_idname = "ifcgit.install_git"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        IfcGitData.make_sure_is_loaded()
        if IfcGitData.data["git_exe"]:
            return False
        return True

    def execute(self, context):
        core.install_git(tool.IfcGit, self)
        refresh()
        return {"FINISHED"}


class RunGitDiff(bpy.types.Operator):

    bl_label = "Git Diff"
    bl_idname = "ifcgit.git_diff"
    bl_description = (
        "Run `git diff` for the current version of IFC file and the last saved one.\n\n"
        "ALT+click to save output to temp directory."
    )
    bl_options = set()

    save_to_temp: bpy.props.BoolProperty(options={"SKIP_SAVE"})

    if TYPE_CHECKING:
        save_to_temp: bool

    @classmethod
    def poll(cls, context):
        if not tool.Ifc.get():
            cls.poll_message_set("No IFC file loaded.")
            return False
        if not tool.Ifc.get_path():
            cls.poll_message_set("Current IFC file was never saved.")
            return False
        return True

    def invoke(self, context, event):
        if event.alt:
            self.save_to_temp = True
        return self.execute(context)

    def execute(self, context):
        core.run_git_diff(tool.IfcGit, self, self.save_to_temp)
        return {"FINISHED"}


class RenameBranch(bpy.types.Operator):
    """Rename the current branch"""

    bl_label = "Rename Branch"
    bl_idname = "ifcgit.rename_branch"
    bl_options = {"REGISTER"}

    new_name: bpy.props.StringProperty(name="New name")

    if TYPE_CHECKING:
        new_name: str

    @classmethod
    def poll(cls, context):
        IfcGitData.make_sure_is_loaded()
        if not IfcGitData.data["repo"]:
            return False
        if IfcGitData.data["is_detached"]:
            return False
        if IfcGitData.data["is_dirty"]:
            return False
        return True

    def invoke(self, context, event):
        self.new_name = IfcGitData.data["active_branch_name"]
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        repo = IfcGitData.data["repo"]
        core.rename_branch(tool.IfcGit, repo, self.new_name)
        refresh()
        return {"FINISHED"}
