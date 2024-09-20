import bpy
import time
import os

from bonsai.bim.module.ifcgit.data import IfcGitData


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
            return

        props = context.scene.IfcGitProperties

        # TODO if file isn't saved, offer to save to disk

        row = layout.row()
        if path_ifc:
            if IfcGitData.data["repo"] and os.path.exists(IfcGitData.data["repo"].git_dir):
                name_ifc = IfcGitData.data["name_ifc"]
                row.label(text=IfcGitData.data["working_dir"], icon="SYSTEM")
                if name_ifc in IfcGitData.data["untracked_files"]:
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

        grouped = layout.row()
        column = grouped.column()
        row = column.row()
        row.prop(props, "display_branch", text="Browse branch")
        row.prop(props, "ifcgit_filter", text="Filter revisions")

        row = column.row()
        row.template_list(
            "COMMIT_UL_List",
            "The_List",
            props,
            "ifcgit_commits",
            props,
            "commit_index",
        )
        column = grouped.column()
        row = column.row()
        row.operator("ifcgit.refresh", icon="FILE_REFRESH")

        if not is_dirty:

            row = column.row()
            row.operator("ifcgit.display_revision", icon="SELECT_DIFFERENCE")

            row = column.row()
            row.operator("ifcgit.switch_revision", icon="CURRENT_FILE")

            row = column.row()
            row.operator("ifcgit.merge", icon="EXPERIMENTAL", text="")

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

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):

        props = context.scene.IfcGitProperties

        current_revision = IfcGitData.data["current_revision"]

        # TODO Figure how this "item" can be acesse in "data.py"
        # so it's possible to move the ".commit"
        try:
            commit = IfcGitData.data["repo"].commit(rev=item.hexsha)
        except ValueError:
            return

        lookup = IfcGitData.data["branches_by_hexsha"]
        refs = ""
        if item.hexsha in lookup:
            for branch in lookup[item.hexsha]:
                if branch.name == props.display_branch:
                    refs = "[" + branch.name + "] "

        lookup = IfcGitData.data["tags_by_hexsha"]
        if item.hexsha in lookup:
            for tag in lookup[item.hexsha]:
                refs += "{" + tag.name + "} "

        if commit == current_revision:
            layout.label(text="[HEAD] " + refs + commit.message.split("\n")[0], icon="DECORATE_KEYFRAME")
        else:
            layout.label(text=refs + commit.message.split("\n")[0], icon="DECORATE_ANIMATE")
        layout.label(text=time.strftime("%c", time.localtime(commit.committed_date)))

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

        if not IfcGitData.data["git_exe"]:
            row = layout.row()
            row.label(text="Git is not installed", icon="ERROR")
            return

        row = layout.row()
        row.operator(
            "ifcgit.object_log",
            icon="TEXT",
        )
