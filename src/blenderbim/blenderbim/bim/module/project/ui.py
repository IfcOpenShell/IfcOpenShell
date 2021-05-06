import os
from bpy.types import Panel, UIList
from blenderbim.bim.ifc import IfcStore


class BIM_PT_project(Panel):
    bl_label = "IFC Project"
    bl_idname = "BIM_PT_project"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"

    def draw(self, context):
        self.layout.use_property_decorate = False
        self.layout.use_property_split = True
        props = context.scene.BIMProperties
        self.file = IfcStore.get_file()
        if self.file or props.ifc_file:
            self.draw_project_ui(context)
        else:
            self.draw_create_project_ui(context)

    def draw_project_ui(self, context):
        props = context.scene.BIMProperties
        pprops = context.scene.BIMProjectProperties
        row = self.layout.row(align=True)
        row.label(text="IFC Filename", icon="FILE")
        row.label(text=os.path.basename(props.ifc_file) or "No File Found")

        if IfcStore.get_file():
            row.prop(pprops, "is_authoring", icon="GREASEPENCIL", text="")
            row = self.layout.row(align=True)
            row.label(text="IFC Schema", icon="FILE_CACHE")
            row.label(text=IfcStore.get_file().schema)
        else:
            row = self.layout.row(align=True)
            row.label(text="File Not Loaded", icon="ERROR")

        row = self.layout.row(align=True)
        row.prop(props, "ifc_file", text="")
        row.operator("bim.reload_ifc_file", icon="FILE_REFRESH", text="")
        row.operator("bim.select_ifc_file", icon="FILE_FOLDER", text="")

        row = self.layout.row(align=True)
        row.prop(props, "schema_dir")
        row.operator("bim.select_schema_dir", icon="FILE_FOLDER", text="")

        row = self.layout.row(align=True)
        row.prop(props, "data_dir")
        row.operator("bim.select_data_dir", icon="FILE_FOLDER", text="")

    def draw_create_project_ui(self, context):
        props = context.scene.BIMProperties
        row = self.layout.row()
        row.prop(props, "export_schema")
        row = self.layout.row()
        row.prop(context.scene.unit_settings, "system")
        row = self.layout.row()
        row.prop(context.scene.unit_settings, "length_unit")
        row = self.layout.row()
        row.prop(props, "area_unit", text="Area Unit")
        row = self.layout.row()
        row.prop(props, "volume_unit", text="Volume Unit")
        row = self.layout.row()
        row.operator("bim.create_project")
        if props.export_schema != "IFC2X3":
            row = self.layout.row()
            row.operator("bim.create_project_library")


class BIM_PT_project_library(Panel):
    bl_label = "IFC Project Library"
    bl_idname = "BIM_PT_project_library"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"

    def draw(self, context):
        self.layout.use_property_decorate = False
        self.layout.use_property_split = True
        self.props = context.scene.BIMProjectProperties
        row = self.layout.row(align=True)
        row.label(text=IfcStore.library_path or "No Library Loaded", icon="ASSET_MANAGER")
        if IfcStore.library_file:
            row.label(text=IfcStore.library_file.schema)
            row.operator("bim.save_library_file", text="", icon="EXPORT")
        row.operator("bim.select_library_file", icon="FILE_FOLDER", text="")
        if IfcStore.library_file:
            self.draw_library_ul()

    def draw_library_ul(self):
        if not self.props.library_elements:
            row = self.layout.row()
            row.label(text="No Assets Found", icon="ERROR")
            return
        row = self.layout.row(align=True)
        row.label(text=self.props.active_library_element or "Top Level Assets")
        if self.props.active_library_element:
            row.operator("bim.rewind_library", icon="FRAME_PREV", text="")
        row.operator("bim.refresh_library", icon="FILE_REFRESH", text="")
        self.layout.template_list(
            "BIM_UL_library",
            "",
            self.props,
            "library_elements",
            self.props,
            "active_library_element_index",
        )


class BIM_UL_library(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if item:
            row = layout.row(align=True)
            if not item.ifc_definition_id:
                op = row.operator("bim.change_library_element", text="", icon="DISCLOSURE_TRI_RIGHT", emboss=False)
                op.element_name = item.name
            row.label(text=item.name)
            if (
                item.ifc_definition_id
                and IfcStore.library_file.schema != "IFC2X3"
                and IfcStore.library_file.by_type("IfcProjectLibrary")
            ):
                if item.is_declared:
                    op = row.operator("bim.unassign_library_declaration", text="", icon="KEYFRAME_HLT", emboss=False)
                    op.definition = item.ifc_definition_id
                else:
                    op = row.operator("bim.assign_library_declaration", text="", icon="KEYFRAME", emboss=False)
                    op.definition = item.ifc_definition_id
            if item.ifc_definition_id:
                op = row.operator("bim.append_library_element", text="", icon="APPEND_BLEND")
                op.definition = item.ifc_definition_id
