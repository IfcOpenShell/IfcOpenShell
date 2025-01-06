# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2020, 2021 Dion Moult <dion@thinkmoult.com>
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

import bpy
import bonsai.bim.helper
import bonsai.tool as tool
from bpy.types import Panel
from bonsai.bim.module.drawing.data import (
    ProductAssignmentsData,
    SheetsData,
    DocumentsData,
    DrawingsData,
    ElementFiltersData,
    DecoratorData,
)


class BIM_PT_camera(Panel):
    bl_label = "Active Drawing"
    bl_idname = "BIM_PT_camera"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_parent_id = "BIM_PT_tab_drawings"

    def draw(self, context):
        if not (context.scene.camera and hasattr(context.scene.camera.data, "BIMCameraProperties")):
            row = self.layout.row()
            row.label(text="No Active Drawing", icon="ERROR")
            return

        if "/" not in context.scene.camera.name:
            self.layout.label(text="This is not a BIM camera.")
            return

        self.layout.use_property_split = True
        dprops = context.scene.DocProperties
        props = context.scene.camera.data.BIMCameraProperties

        col = self.layout.column(align=True)
        row = col.row(align=True)
        row.prop(props, "has_underlay", icon="OUTLINER_OB_IMAGE")
        row.prop(dprops, "should_use_underlay_cache", text="", icon="FILE_REFRESH")
        row = col.row(align=True)
        row.prop(props, "has_linework", icon="IMAGE_DATA")
        row.prop(dprops, "should_use_linework_cache", text="", icon="FILE_REFRESH")
        row = col.row(align=True)
        row.prop(props, "has_annotation", icon="MOD_EDGESPLIT")
        row.prop(dprops, "should_use_annotation_cache", text="", icon="FILE_REFRESH")

        row = self.layout.row()
        row.prop(props, "linework_mode")
        if props.linework_mode == "OPENCASCADE":
            row = self.layout.row()
            row.prop(props, "fill_mode")
            row = self.layout.row()
            row.prop(props, "cut_mode")

        row = self.layout.row()
        row.prop(props, "width")
        row = self.layout.row()
        row.prop(props, "height")

        row = self.layout.row()
        row.prop(context.scene.camera.data, "clip_end", text="Depth")

        row = self.layout.row(align=True)
        row.prop(props, "diagram_scale", text="Scale")
        row.prop(props, "is_nts", text="", icon="MOD_EDGESPLIT")

        if props.diagram_scale == "CUSTOM":
            row = self.layout.row(align=True)
            row.prop(props, "custom_scale_numerator", text="Custom Scale")
            row.prop(props, "custom_scale_denominator", text="")

        if props.has_underlay:
            row = self.layout.row()
            row.prop(props, "dpi")


class BIM_PT_element_filters(Panel):
    bl_label = "Element Filters"
    bl_idname = "BIM_PT_element_filters"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_parent_id = "BIM_PT_camera"

    @classmethod
    def poll(cls, context):
        return bool((camera := context.scene.camera) and tool.Ifc.get_entity(camera))

    def draw(self, context):
        if not ElementFiltersData.is_loaded:
            ElementFiltersData.load()

        props = context.scene.camera.data.BIMCameraProperties

        if props.filter_mode == "INCLUDE":
            bonsai.bim.helper.draw_filter(
                self.layout, props.include_filter_groups, ElementFiltersData, "drawing_include"
            )
            row = self.layout.row(align=True)
            row.operator("bim.edit_element_filter", icon="CHECKMARK", text="Save Include Filter").filter_mode = (
                "INCLUDE"
            )
            row.operator("bim.enable_editing_element_filter", icon="CANCEL", text="").filter_mode = "NONE"
        elif props.filter_mode == "EXCLUDE":
            bonsai.bim.helper.draw_filter(
                self.layout, props.exclude_filter_groups, ElementFiltersData, "drawing_exclude"
            )
            row = self.layout.row(align=True)
            row.operator("bim.edit_element_filter", icon="CHECKMARK", text="Save Exclude Filter").filter_mode = (
                "EXCLUDE"
            )
            row.operator("bim.enable_editing_element_filter", icon="CANCEL", text="").filter_mode = "NONE"
        else:
            row = self.layout.row(align=True)
            text = "Include Filter" if ElementFiltersData.data["has_include_filter"] else "No Include Filter Found"
            icon = "GREASEPENCIL" if ElementFiltersData.data["has_include_filter"] else "ADD"
            row.label(text=text, icon="FILTER")
            row.operator("bim.enable_editing_element_filter", icon=icon, text="").filter_mode = "INCLUDE"
            row = self.layout.row(align=True)
            text = "Exclude Filter" if ElementFiltersData.data["has_exclude_filter"] else "No Exclude Filter Found"
            icon = "GREASEPENCIL" if ElementFiltersData.data["has_exclude_filter"] else "ADD"
            row.label(text=text, icon="FILTER")
            row.operator("bim.enable_editing_element_filter", icon=icon, text="").filter_mode = "EXCLUDE"


class BIM_PT_drawing_underlay(Panel):
    bl_label = "Drawing Underlay"
    bl_idname = "BIM_PT_drawing_underlay"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_parent_id = "BIM_PT_camera"

    @classmethod
    def poll(cls, context):
        return bool((camera := context.scene.camera) and tool.Ifc.get_entity(camera))

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        camera = context.scene.camera
        assert camera
        dprops = context.scene.DocProperties
        props = camera.data.BIMCameraProperties
        drawing_index_is_valid = props.active_drawing_style_index < len(dprops.drawing_styles)

        if not DrawingsData.is_loaded:
            DrawingsData.load()
        drawing_pset_data = DrawingsData.data["active_drawing_pset_data"]

        row = layout.row(align=True)
        current_shading_style = drawing_pset_data.get("CurrentShadingStyle", None)
        if current_shading_style is None:
            row.label(text="Current style is not set.")
        else:
            row.label(text="Current Shading Style:")
            row.label(text=current_shading_style)
        row.operator("bim.add_drawing_style", icon="ADD", text="")
        if drawing_index_is_valid:
            row.operator("bim.remove_drawing_style", icon="X", text="").index = props.active_drawing_style_index
        row.operator("bim.reload_drawing_styles", icon="FILE_REFRESH", text="")

        if not dprops.drawing_styles:
            return
        layout.template_list("BIM_UL_generic", "", dprops, "drawing_styles", props, "active_drawing_style_index")

        if not drawing_index_is_valid:
            return
        drawing_style = dprops.drawing_styles[props.active_drawing_style_index]

        row = layout.row(align=True)
        row.prop(drawing_style, "name")

        row = layout.row()
        row.prop(drawing_style, "render_type")
        row = layout.row(align=True)
        row.prop(drawing_style, "include_query")
        row = layout.row(align=True)
        row.prop(drawing_style, "exclude_query")

        row = layout.row()
        row.operator("bim.add_drawing_style_attribute")

        for index, attribute in enumerate(drawing_style.attributes):
            row = layout.row(align=True)
            row.prop(attribute, "name", text="")
            row.operator("bim.remove_drawing_style_attribute", icon="X", text="").index = index

        row = layout.row(align=True)
        row.operator("bim.save_drawing_style")
        row.operator("bim.activate_drawing_style")


class BIM_PT_drawings(Panel):
    bl_label = "Drawings"
    bl_idname = "BIM_PT_drawings"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_parent_id = "BIM_PT_tab_drawings"
    bl_options = {"HIDE_HEADER"}

    def draw(self, context):
        if not DrawingsData.is_loaded:
            DrawingsData.load()

        if not DrawingsData.data["has_saved_ifc"]:
            draw_project_not_saved_ui(self)
            return

        self.props = context.scene.DocProperties

        if not self.props.is_editing_drawings:
            row = self.layout.row(align=True)
            row.label(text=f"{DrawingsData.data['total_drawings']} Drawings Found", icon="IMAGE_DATA")
            row.operator("bim.load_drawings", text="", icon="IMPORT")
            return

        row = self.layout.row(align=True)
        row.prop(self.props, "target_view", text="")
        row.prop(self.props, "location_hint", text="")
        row.operator("bim.add_drawing", text="", icon="ADD")
        row.operator("bim.disable_editing_drawings", text="", icon="CANCEL")

        if self.props.drawings:
            if self.props.active_drawing_index < len(self.props.drawings):
                active_drawing = self.props.drawings[self.props.active_drawing_index]
                row = self.layout.row(align=True)
                row2 = row.row(align=True)
                row2.operator("bim.remove_drawing", icon="X", text="").drawing = active_drawing.ifc_definition_id

                row2.separator(factor=0.5, type="SPACE")

                row2.operator("bim.duplicate_drawing", icon="DUPLICATE", text="").drawing = (
                    active_drawing.ifc_definition_id
                )

                row3 = row.row(align=True)
                row3.alignment = "RIGHT"

                row3.operator("bim.activate_drawing", icon="OUTLINER_OB_CAMERA", text="").drawing = (
                    active_drawing.ifc_definition_id
                )
                row3.operator("bim.activate_model", icon="VIEW3D", text="")

                row3.separator(factor=0.5, type="SPACE")

                row3.operator("bim.select_all_drawings", icon="CHECKBOX_HLT", text="")
                row3.operator("bim.create_drawing", text="", icon="OUTPUT")
                row3.operator("bim.convert_svg_to_dxf", text="", icon="SEQ_PREVIEW").view = active_drawing.name
                row3.operator("bim.open_drawing", icon="HIDE_OFF", text="").view = active_drawing.name
            self.layout.template_list(
                "BIM_UL_drawinglist", "", self.props, "drawings", self.props, "active_drawing_index"
            )

        # Commented out until federated drawing generation is rebuilt
        # row = self.layout.row()
        # row.operator("bim.add_ifc_file")

        # for index, ifc_file in enumerate(self.props.ifc_files):
        #     row = self.layout.row(align=True)
        #     row.prop(ifc_file, "name", text="IFC #{}".format(index + 1))
        #     row.operator("bim.select_doc_ifc_file", icon="FILE_FOLDER", text="").index = index
        #     row.operator("bim.remove_ifc_file", icon="X", text="").index = index


class BIM_PT_schedules(Panel):
    bl_label = "Schedules"
    bl_idname = "BIM_PT_schedules"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_parent_id = "BIM_PT_tab_schedules"
    bl_options = {"HIDE_HEADER"}

    def draw(self, context):
        if not DocumentsData.is_loaded:
            DocumentsData.load()

        if not DocumentsData.data["has_saved_ifc"]:
            draw_project_not_saved_ui(self)
            return

        self.props = context.scene.DocProperties

        if not self.props.is_editing_schedules:
            row = self.layout.row(align=True)
            row.label(text=f"{DocumentsData.data['total_schedules']} Schedules Found", icon="PRESET")
            row.operator("bim.load_schedules", text="", icon="IMPORT")
            return

        row = self.layout.row(align=True)
        row.operator("bim.add_schedule", icon="ADD")
        row.operator("bim.disable_editing_schedules", text="", icon="CANCEL")

        if self.props.schedules:
            if self.props.active_schedule_index < len(self.props.schedules):
                active_schedule = self.props.schedules[self.props.active_schedule_index]
                row = self.layout.row(align=True)
                row.alignment = "RIGHT"
                row.operator("bim.open_schedule", icon="URL", text="").schedule = active_schedule.ifc_definition_id
                row.operator("bim.build_schedule", icon="LINENUMBERS_ON", text="").schedule = (
                    active_schedule.ifc_definition_id
                )
                row.operator("bim.remove_schedule", icon="X", text="").schedule = active_schedule.ifc_definition_id

            self.layout.template_list(
                "BIM_UL_generic", "", self.props, "schedules", self.props, "active_schedule_index"
            )


def draw_project_not_saved_ui(self):
    row = self.layout.row()
    row.label(text="Project Not Yet Saved", icon="ERROR")


class BIM_PT_references(Panel):
    bl_label = "References"
    bl_idname = "BIM_PT_references"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_parent_id = "BIM_PT_tab_references"
    bl_options = {"HIDE_HEADER"}

    def draw(self, context):
        if not DocumentsData.is_loaded:
            DocumentsData.load()

        if not DocumentsData.data["has_saved_ifc"]:
            draw_project_not_saved_ui(self)
            return

        self.props = context.scene.DocProperties

        if not self.props.is_editing_references:
            row = self.layout.row(align=True)
            row.label(text=f"{DocumentsData.data['total_references']} References Found", icon="IMAGE_REFERENCE")
            row.operator("bim.load_references", text="", icon="IMPORT")
            return

        row = self.layout.row(align=True)
        row.operator("bim.add_reference", icon="ADD")
        row.operator("bim.disable_editing_references", text="", icon="CANCEL")

        if self.props.references:
            if self.props.active_reference_index < len(self.props.references):
                active_reference = self.props.references[self.props.active_reference_index]
                row = self.layout.row(align=True)
                row.alignment = "RIGHT"
                row.operator("bim.open_reference", icon="URL", text="").reference = active_reference.ifc_definition_id
                row.operator("bim.remove_reference", icon="X", text="").reference = active_reference.ifc_definition_id

            self.layout.template_list(
                "BIM_UL_generic", "", self.props, "references", self.props, "active_reference_index"
            )


class BIM_PT_sheets(Panel):
    bl_label = "Sheets"
    bl_idname = "BIM_PT_sheets"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_parent_id = "BIM_PT_tab_sheets"
    bl_options = {"HIDE_HEADER"}

    def draw(self, context):
        if not SheetsData.is_loaded:
            SheetsData.load()

        if not SheetsData.data["has_saved_ifc"]:
            draw_project_not_saved_ui(self)
            return

        self.props = context.scene.DocProperties

        if not self.props.is_editing_sheets:
            row = self.layout.row(align=True)
            row.label(text=f"{SheetsData.data['total_sheets']} Sheets Found", icon="FILE")
            row.operator("bim.load_sheets", text="", icon="IMPORT")
            return

        row = self.layout.row(align=True)
        row.prop(self.props, "titleblock", text="")
        row.operator("bim.add_sheet", text="", icon="ADD")
        row.operator("bim.disable_editing_sheets", text="", icon="CANCEL")

        if self.props.sheets and self.props.active_sheet_index < len(self.props.sheets):
            active_sheet = self.props.sheets[self.props.active_sheet_index]
            row = self.layout.row(align=True)
            row2 = row.row(align=True)
            if active_sheet.is_sheet:
                row2.operator("bim.remove_sheet", icon="X", text="").sheet = active_sheet.ifc_definition_id
            else:
                row2.operator("bim.remove_drawing_from_sheet", icon="X", text="").reference = (
                    active_sheet.ifc_definition_id
                )

            row2.separator(factor=0.5, type="SPACE")

            row2.operator("bim.duplicate_sheet", icon="DUPLICATE", text="").drawing = active_sheet.ifc_definition_id
            row2.operator("bim.open_documentation_web_ui", icon="URL", text="")

            row3 = row.row(align=True)
            row3.alignment = "RIGHT"

            op = row3.operator("bim.activate_drawing_from_sheet", icon="OUTLINER_OB_CAMERA", text="")

            if active_sheet.reference_type == "DRAWING":
                drawingnamesvg = active_sheet.name
                drawingname = drawingnamesvg.split(".svg")[0]
                ifc_file = tool.Ifc.get()
                ifc_annotations = ifc_file.by_type("IfcAnnotation")
                drawingid = None

                for annotation in ifc_annotations:
                    Annotation_Name = annotation.Name.replace(",", "")  # Remove commas
                    if Annotation_Name == drawingname:
                        drawingid = annotation.id()
                        break

                if drawingid is not None:
                    op.drawing = drawingid

            row3.separator(factor=0.5, type="SPACE")

            row3.operator("bim.edit_sheet", icon="GREASEPENCIL", text="")
            row3.operator("bim.add_drawing_to_sheet", icon="IMAGE_PLANE", text="")
            row3.operator("bim.add_schedule_to_sheet", icon="PRESET_NEW", text="")
            row3.operator("bim.add_reference_to_sheet", icon="IMAGE_REFERENCE", text="")
            row3.operator("bim.open_layout", icon="CURRENT_FILE", text="")

            row3.separator(factor=0.5, type="SPACE")

            row3.operator("bim.select_all_sheets", icon="CHECKBOX_HLT", text="")
            row3.operator("bim.create_sheets", icon="OUTPUT", text="")
            row3.operator("bim.open_sheet", icon="HIDE_OFF", text="")

        self.layout.template_list("BIM_UL_sheets", "", self.props, "sheets", self.props, "active_sheet_index")


class BIM_PT_product_assignments(Panel):
    bl_label = "Product Assignments"
    bl_idname = "BIM_PT_product_assignments"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"
    bl_order = 1
    bl_parent_id = "BIM_PT_tab_object_metadata"

    @classmethod
    def poll(cls, context):
        if not tool.Ifc.get() or not context.active_object:
            return
        element = tool.Ifc.get_entity(context.active_object)
        if not element:
            return
        return element.is_a("IfcAnnotation")

    def draw(self, context):
        if not ProductAssignmentsData.is_loaded:
            ProductAssignmentsData.load()

        props = context.active_object.BIMAssignedProductProperties

        if props.is_editing_product:
            row = self.layout.row(align=True)
            row.prop(props, "relating_product", text="")
            row.operator("bim.assign_selected_as_product", icon="OBJECT_DATA", text="")
            row.operator("bim.edit_assigned_product", icon="CHECKMARK", text="")
            row.operator("bim.disable_editing_assigned_product", icon="CANCEL", text="")
        else:
            row = self.layout.row(align=True)
            row.label(text=ProductAssignmentsData.data["relating_product"] or "No Relating Product", icon="OBJECT_DATA")
            row.operator("bim.enable_editing_assigned_product", icon="GREASEPENCIL", text="")
            col = row.column()
            col.operator("bim.select_assigned_product", icon="RESTRICT_SELECT_OFF", text="")
            col.enabled = bool(ProductAssignmentsData.data["relating_product"])


class BIM_PT_text(Panel):
    bl_label = "Text"
    bl_idname = "BIM_PT_text"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"
    bl_order = 0
    bl_parent_id = "BIM_PT_tab_object_metadata"

    @classmethod
    def poll(cls, context):
        if not tool.Ifc.get() or not context.active_object:
            return
        element = tool.Ifc.get_entity(context.active_object)
        if not element:
            return
        return tool.Drawing.is_annotation_object_type(element, ["TEXT", "TEXT_LEADER"])

    def draw(self, context):
        obj = context.active_object
        props = obj.BIMTextProperties

        if props.is_editing:
            # shares most of the code with EditTextPopup.draw()
            # need to keep them in sync or move to some common function

            row = self.layout.row(align=True)
            row.operator("bim.edit_text", icon="CHECKMARK")
            row.operator("bim.add_text_literal", icon="ADD", text="")
            row.operator("bim.disable_editing_text", icon="CANCEL", text="")

            row = self.layout.row(align=True)
            row.prop(props, "font_size")
            row = self.layout.row(align=True)
            row.prop(props, "newline_at")

            for i, literal_props in enumerate(props.literals):
                box = self.layout.box()
                row = self.layout.row(align=True)

                row = box.row(align=True)
                row.label(text=f"Literal[{i}]:")
                if i > 0:
                    row.operator("bim.order_text_literal_up", icon="TRIA_UP", text="").literal_prop_id = i
                if i < len(props.literals) - 1:
                    row.operator("bim.order_text_literal_down", icon="TRIA_DOWN", text="").literal_prop_id = i
                row.operator("bim.remove_text_literal", icon="X", text="").literal_prop_id = i

                # skip BoxAlignment since we're going to format it ourselves
                attributes = [a for a in literal_props.attributes if a.name != "BoxAlignment"]
                bonsai.bim.helper.draw_attributes(attributes, box)

                row = box.row(align=True)
                cols = [row.column(align=True) for i in range(3)]
                for i in range(9):
                    cols[i % 3].prop(
                        literal_props,
                        "box_alignment",
                        text="",
                        index=i,
                        icon="RADIOBUT_ON" if literal_props.box_alignment[i] else "RADIOBUT_OFF",
                    )

                col = row.column(align=True)
                col.label(text="    Text box alignment:")
                col.label(text=f'    {literal_props.attributes["BoxAlignment"].string_value}')

        else:
            text_data = DecoratorData.get_ifc_text_data(obj)

            row = self.layout.row()
            row.operator("bim.enable_editing_text", icon="GREASEPENCIL")

            row = self.layout.row(align=True)
            row.label(text="FontSize")
            row.label(text=str(text_data["FontSize"]))
            row = self.layout.row(align=True)
            row.label(text="Newline_At")
            row.label(text=str(text_data["Newline_At"]))

            for literal_data in text_data["Literals"]:
                box = self.layout.box()
                for attribute in literal_data:
                    row = box.row(align=True)
                    row.label(text=attribute)
                    row.label(text=literal_data[attribute])


class BIM_UL_drawinglist(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if not item:
            layout.label(text="", translate=False)
            return

        row = layout.row(align=True)
        if item.is_drawing:
            row.label(text="", icon="BLANK1")
            selected_icon = "CHECKBOX_HLT" if item.is_selected else "CHECKBOX_DEHLT"
            row.prop(item, "is_selected", text="", icon=selected_icon, emboss=False)
            row.prop(item, "name", text="", emboss=False)
            self.props = context.scene.DocProperties
            if (
                self.props.drawings
                and self.props.active_drawing_id
                and item.ifc_definition_id == self.props.active_drawing_id
            ):
                row.label(text="", icon="OUTLINER_OB_CAMERA")
        else:
            if item.target_view == "PLAN_VIEW":
                icon = "UV_FACESEL"
            elif item.target_view == "ELEVATION_VIEW":
                icon = "UV_VERTEXSEL"
            elif item.target_view == "SECTION_VIEW":
                icon = "UV_EDGESEL"
            elif item.target_view == "REFLECTED_PLAN_VIEW":
                icon = "XRAY"
            elif item.target_view == "MODEL_VIEW":
                icon = "SNAP_VOLUME"
            else:
                icon = "CLIPUV_HLT"
            if item.is_expanded:
                row.operator(
                    "bim.contract_target_view", text="", emboss=False, icon="DISCLOSURE_TRI_DOWN"
                ).target_view = item.target_view
            else:
                row.operator(
                    "bim.expand_target_view", text="", emboss=False, icon="DISCLOSURE_TRI_RIGHT"
                ).target_view = item.target_view
            row.prop(item, "name", text="", icon=icon, emboss=False)


class BIM_UL_sheets(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if not item:
            layout.label(text="", translate=False)
            return

        row = layout.row(align=True)
        if item.is_sheet:
            if item.is_expanded:
                row.operator("bim.contract_sheet", text="", emboss=False, icon="DISCLOSURE_TRI_DOWN").sheet = (
                    item.ifc_definition_id
                )
            else:
                row.operator("bim.expand_sheet", text="", emboss=False, icon="DISCLOSURE_TRI_RIGHT").sheet = (
                    item.ifc_definition_id
                )

            selected_icon = "CHECKBOX_HLT" if item.is_selected else "CHECKBOX_DEHLT"
            row.prop(item, "is_selected", text="", icon=selected_icon, emboss=False)

            row.label(text=f"{item.identification} - {item.name}")
        else:
            row.label(text="", icon="BLANK1")
            if item.reference_type == "DRAWING":
                row.label(text="", icon="IMAGE_DATA")
            elif item.reference_type == "SCHEDULE":
                row.label(text="", icon="PRESET")
            elif item.reference_type == "TITLEBLOCK":
                row.label(text="", icon="MENU_PANEL")
            elif item.reference_type == "REVISION":
                row.label(text="", icon="RECOVER_LAST")
            elif item.reference_type == "REFERENCE":
                row.label(text="", icon="IMAGE_REFERENCE")

            if item.identification:
                name = f"{item.identification} - {item.name or 'Unnamed'}"
            else:
                name = item.name or "Unnamed"
            row.label(text=name)

    def draw_filter(self, context, layout):
        # We only need filtering, not reordering for sheets.
        row = layout.row(align=True)
        row.prop(self, "filter_name", text="")
        row.prop(self, "use_filter_invert", text="", icon="ARROW_LEFTRIGHT")

    def filter_items(self, context, data, propname):
        flt_flags = []
        flt_neworder = []

        if self.filter_name:
            filter_name = self.filter_name.lower()
            active_sheet = None
            for sheet in data.sheets:
                if sheet.is_sheet:
                    active_sheet = sheet
                    active_sheet_index = len(flt_flags)
                if filter_name in sheet.name.lower() or filter_name in sheet.identification.lower():
                    flt_flags.append(self.bitflag_filter_item)
                    if not sheet.is_sheet:
                        flt_flags[active_sheet_index] = self.bitflag_filter_item
                else:
                    flt_flags.append(0)

        if not flt_flags:
            return flt_flags, flt_neworder
        return flt_flags, flt_neworder


def add_object_button(self, context):
    self.layout.operator("bim.add_reference_image", icon="TEXTURE", text="IFC Reference Image")
