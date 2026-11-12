from __future__ import annotations

import os
import platform
import time
from typing import TYPE_CHECKING

import bpy

import bonsai.tool as tool
from bonsai.bim.module.ifcgit.data import IfcGitData

if TYPE_CHECKING:
    from bonsai.bim.module.ifcgit.prop import IfcGitListItem, IfcGitProperties


class IFCGIT_PT_panel(bpy.types.Panel):
    """Scene Properties panel to interact with IFC repository data"""

    bl_label = "Git"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_options = {"DEFAULT_CLOSED"}
    bl_parent_id = "BIM_PT_tab_project_info"

    def draw(self, context):

        if not IfcGitData.is_loaded:
            IfcGitData.load()

        layout = self.layout
        path_ifc = IfcGitData.data["path_ifc"]

        if not IfcGitData.data["git_exe"]:
            row = layout.row()
            row.label(text="Git is not installed", icon="ERROR")
            if platform.system() == "Windows":
                row.operator(
                    "ifcgit.install_git",
                    text="Install Git",
                    icon="PACKAGE",
                )
            return

        props = tool.IfcGit.get_ifcgit_props()

        # TODO if file isn't saved, offer to save to disk

        row = layout.row()
        if path_ifc:
            if IfcGitData.data["repo"] and os.path.exists(IfcGitData.data["repo"].git_dir):
                name_ifc = IfcGitData.data["name_ifc"]
                row.label(text=IfcGitData.data["working_dir"], icon="SYSTEM")
                if IfcGitData.data["ifc_is_untracked"]:
                    row.operator(
                        "ifcgit.addfile",
                        text="Add '" + name_ifc + "' to repository",
                        icon="FILE",
                    )
                else:
                    row.label(text=name_ifc, icon="FILE")
            else:
                IfcGitData.load()
                row.operator(
                    "ifcgit.createrepo",
                    text="Create '" + IfcGitData.data["dir_name"] + "' repository",
                    icon="SYSTEM",
                )
                row.label(text=IfcGitData.data["base_name"], icon="FILE")
                return
        else:
            row.label(text="No Git repository found", icon="SYSTEM")
            row.label(text="No IFC project saved", icon="FILE")

            box = layout.box()
            row = box.row()
            row.label(text="Clone a remote Git repository")
            row = box.row()
            row.prop(props, "remote_url")
            row = box.row()
            row.prop(props, "local_folder")
            row = box.row()
            row.operator("ifcgit.clone_repo", icon="IMPORT")
            return

        is_dirty = IfcGitData.data["is_dirty"]

        if is_dirty:
            row = layout.row()
            row.label(text="Saved changes have not been committed", icon="ERROR")

            row = layout.row()
            row.operator("ifcgit.display_uncommitted", icon="SELECT_DIFFERENCE")
            row.operator("ifcgit.discard", icon="TRASH")

            row = layout.row()
            row.prop(props, "commit_message")

            row = layout.row()
            if IfcGitData.data["is_detached"]:
                row.label(text="HEAD is detached, commit will create a branch", icon="ERROR")
            else:
                row.label(text="Optionally create a branch:")
            row.prop(props, "new_branch_name")

            row = layout.row()
            row.operator("ifcgit.commit_changes", icon="GREASEPENCIL")

        row = layout.row()
        if IfcGitData.data["is_detached"]:
            row.label(text="Working branch: Detached HEAD")
        else:
            row.label(text="Working branch: " + IfcGitData.data["active_branch_name"])
            row.operator("ifcgit.rename_branch", icon="GREASEPENCIL", text="")

        row = layout.row()
        row.prop(props, "display_branch", text="Browse branch")
        row.prop(props, "ifcgit_filter", text="Filter revisions")

        layout.template_list(
            "COMMIT_UL_List",
            "The_List",
            props,
            "ifcgit_commits",
            props,
            "commit_index",
        )

        row = layout.row(align=True)
        row.operator("ifcgit.refresh", icon="FILE_REFRESH")
        if not is_dirty:
            row.operator("ifcgit.display_revision", icon="SELECT_DIFFERENCE")
            row.operator("ifcgit.switch_revision", icon="CURRENT_FILE")
            row.operator("ifcgit.merge", icon="SYSTEM")

        conflicts = tool.IfcGit.get_merge_conflicts()
        if conflicts is not None:
            box = layout.box()
            box.alert = True
            row = box.row()
            row.label(
                text=f"Merge failed \u2014 {len(conflicts)} conflict(s)",
                icon="ERROR",
            )
            for conflict in conflicts:
                col = box.column(align=True)
                conflict_type = conflict.get("type", "")
                entity_id = conflict.get("entity_id", "?")
                local_id = conflict.get("original_local_id")

                if conflict_type == "attribute_conflict":
                    entity_class = conflict.get("entity_class", "Entity")
                    attr_idx = conflict.get("attribute_index", "?")
                    desc = f"#{entity_id} {entity_class}: attribute {attr_idx} conflict"
                elif conflict_type == "entity_deleted_and_modified":
                    entity_class = conflict.get("entity_class", "Entity")
                    desc = f"#{entity_id} {entity_class}: " + conflict.get("message", "deleted/modified conflict")
                elif conflict_type == "class_changed":
                    desc = (
                        f"#{entity_id}: class changed "
                        + conflict.get("base_class", "?")
                        + " \u2192 "
                        + conflict.get("modified_class", "?")
                    )
                elif conflict_type == "required_entity_deleted":
                    desc = f"#{entity_id}: " + conflict.get("message", "required entity deleted")
                else:
                    desc = f"#{entity_id}: {conflict_type}"

                row = col.row(align=True)
                row.label(text=desc)
                if local_id:
                    op = row.operator(
                        "ifcgit.select_conflict_entity",
                        text="",
                        icon="RESTRICT_SELECT_OFF",
                    )
                    op.step_id = local_id

                if conflict_type == "attribute_conflict":
                    sub = col.column(align=True)
                    sub.scale_y = 0.75
                    sub.label(text=f"  Base:   {conflict.get('base_value', '')}")
                    sub.label(text=f"  Local:  {conflict.get('local_value', '')}")
                    sub.label(text=f"  Remote: {conflict.get('remote_value', '')}")

        if not props.ifcgit_commits:
            return

        item = props.ifcgit_commits[props.commit_index]
        if not item.relevant:
            row = layout.row()
            row.label(text="Revision unrelated to current IFC project", icon="ERROR")

        box = layout.box()
        column = box.column(align=True)
        row = column.row()
        row.label(text=item.hexsha)
        row = column.row()
        row.label(text=item.author_name + " <" + item.author_email + ">")
        for message_line in item.message.split("\n"):
            row = column.row()
            row.label(text=message_line)

        for tag in item.tags:
            box = layout.box()
            item = box.row()
            column = item.column(align=True)
            row = column.row()
            row.label(text=tag.name)
            row.operator("ifcgit.delete_tag", icon="PANEL_CLOSE").tag_name = tag.name
            if tag.message:
                for message_line in tag.message.split("\n"):
                    row = column.row()
                    row.label(text=message_line)

        box = layout.box()
        row = box.row()
        row.prop(props, "new_tag_name")
        row = box.row()
        row.prop(props, "new_tag_message")
        row = box.row()
        row.operator("ifcgit.add_tag", icon="GREASEPENCIL")

        if IfcGitData.data["remotes"]:
            row = layout.row()
            row.prop(props, "select_remote", text="Select remote")
            urls = IfcGitData.data["remote_urls"]
            row.label(text=urls[props.select_remote])
            row.operator("ifcgit.delete_remote", text="", icon="PANEL_CLOSE")
            row = layout.row()
            row.operator("ifcgit.push", icon="EXPORT")
            row.operator("ifcgit.fetch", icon="IMPORT")

        box = layout.box()
        row = box.row()
        row.prop(props, "remote_name")
        row = box.row()
        row.prop(props, "remote_url")
        row = box.row()
        row.operator("ifcgit.add_remote", icon="ADD")


class COMMIT_UL_List(bpy.types.UIList):
    """List of Git commits"""

    def draw_item(
        self,
        context: bpy.types.UILayout,
        layout: bpy.types.UILayout,
        data: IfcGitProperties,
        item: IfcGitListItem,
        icon,
        active_data,
        active_propname,
        index: int,
    ):

        current_revision = IfcGitData.data["current_revision"]
        current_hexsha = current_revision.hexsha if current_revision else None

        lookup = IfcGitData.data["branches_by_hexsha"]
        refs = ""
        if item.hexsha in lookup:
            for branch in lookup[item.hexsha]:
                if branch.name == data.display_branch:
                    refs = "[" + branch.name + "] "

        lookup = IfcGitData.data["tags_by_hexsha"]
        if item.hexsha in lookup:
            for tag in lookup[item.hexsha]:
                refs += "{" + tag.name + "} "

        if item.hexsha == current_hexsha:
            layout.label(text="[HEAD] " + refs + item.message.split("\n")[0], icon="DECORATE_KEYFRAME")
        else:
            layout.label(text=refs + item.message.split("\n")[0], icon="DECORATE_ANIMATE")
        layout.label(text=time.strftime("%c", time.localtime(item.committed_date)))

    def draw_filter(self, context, layout):

        # We only need filtering and reverse sort, not reordering by name
        row = layout.row(align=True)
        row.prop(self, "filter_name", text="")
        row.prop(self, "use_filter_invert", text="", icon="ARROW_LEFTRIGHT")
        row.prop(self, "use_filter_sort_reverse", text="", icon="SORT_DESC")

    def filter_items(self, context, data, propname):

        commits = getattr(data, propname)
        helper_funcs = bpy.types.UI_UL_list

        # Default return values.
        flt_flags = []
        flt_neworder = list(range(len(commits)))

        # Filtering by commit message
        if self.filter_name:
            flt_flags = helper_funcs.filter_items_by_name(
                self.filter_name, self.bitflag_filter_item, commits, "message", reverse=False
            )
        if not flt_flags:
            flt_flags = [self.bitflag_filter_item] * len(commits)

        return flt_flags, flt_neworder


class IFCGIT_PT_revision_inspector(bpy.types.Panel):
    """Tool panel to interact with revision history"""

    bl_idname = "IFCGIT_PT_revision_inspector"
    bl_label = "Git History"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_options = {"DEFAULT_CLOSED"}
    bl_parent_id = "IFCGIT_PT_panel"

    def draw(self, context):

        if not IfcGitData.is_loaded:
            IfcGitData.load()

        layout = self.layout
        assert layout

        if not IfcGitData.data["git_exe"]:
            row = layout.row()
            row.label(text="Git is not installed", icon="ERROR")
            return

        row = layout.row()
        row.operator(
            "ifcgit.object_log",
            icon="TEXT",
        )
        row = layout.row()
        row.operator("ifcgit.git_diff")
