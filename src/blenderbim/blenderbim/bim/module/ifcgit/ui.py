import bpy
import time
from data import IfcGitData


class IFCGIT_PT_panel(bpy.types.Panel):
    """Scene Properties panel to interact with IFC repository data"""

    bl_label = "IFC Git"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_options = {"DEFAULT_CLOSED"}
    bl_parent_id = "BIM_PT_project_info"

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
            if IfcGitData.data["repo"]:
                name_ifc = IfcGitData.data["name_ifc"]
                row.label(text=IfcGitData.data["repo"].working_dir, icon="SYSTEM")
                if name_ifc in IfcGitData.data["repo"].untracked_files:
                    row.operator(
                        "ifcgit.addfile",
                        text="Add '" + name_ifc + "' to repository",
                        icon="FILE",
                    )
                else:
                    row.label(text=name_ifc, icon="FILE")
            else:
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

            if IfcGitData.data["repo"].head.is_detached:
                row = layout.row()
                row.label(
                    text="HEAD is detached, commit will create a branch", icon="ERROR"
                )
                row.prop(props, "new_branch_name")

            row = layout.row()
            row.operator("ifcgit.commit_changes", icon="GREASEPENCIL")

        row = layout.row()
        if IfcGitData.data["repo"].head.is_detached:
            row.label(text="Working branch: Detached HEAD")
        else:
            row.label(
                text="Working branch: " + IfcGitData.data["repo"].active_branch.name
            )

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

            # TODO operator to tag selected

            row = column.row()
            row.operator("ifcgit.merge", icon="EXPERIMENTAL", text="")

        if not props.ifcgit_commits:
            return

        item = props.ifcgit_commits[props.commit_index]
        commit = IfcGitData.data["commit"]
        if not item.relevant:
            row = layout.row()
            row.label(text="Revision unrelated to current IFC project", icon="ERROR")

        box = layout.box()
        column = box.column(align=True)
        row = column.row()
        row.label(text=commit.hexsha)
        row = column.row()
        row.label(text=commit.author.name + " <" + commit.author.email + ">")
        row = column.row()
        row.label(text=commit.message)


class COMMIT_UL_List(bpy.types.UIList):
    """List of Git commits"""

    def draw_item(
        self, context, layout, data, item, icon, active_data, active_propname, index
    ):

        props = context.scene.IfcGitProperties

        current_revision = IfcGitData.data["current_revision"]

        # TODO Figure how this "item" can be acesse in "data.py"
        # so it's possible to move the ".commit"
        commit = IfcGitData.data["repo"].commit(rev=item.hexsha)

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
            layout.label(
                text="[HEAD] " + refs + commit.message, icon="DECORATE_KEYFRAME"
            )
        else:
            layout.label(text=refs + commit.message, icon="DECORATE_ANIMATE")
        layout.label(text=time.strftime("%c", time.localtime(commit.committed_date)))
