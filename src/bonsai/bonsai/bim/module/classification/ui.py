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

from __future__ import annotations
import bpy
import bonsai.bim.helper
import bonsai.tool as tool
import bonsai.bim.module.classification.prop as classification_prop
from bpy.types import Panel, UIList
from bonsai.bim.module.classification.data import (
    ClassificationsData,
    ObjectClassificationsData,
    MaterialClassificationsData,
    CostClassificationsData,
    ZoneClassificationsData,
)
from typing import TYPE_CHECKING, Any, Union

if TYPE_CHECKING:
    from bonsai.bim.module.classification.prop import BIMClassificationProperties, ClassificationReference


class BIM_PT_classifications(Panel):
    bl_label = "Classifications"
    bl_idname = "BIM_PT_classifications"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_parent_id = "BIM_PT_tab_project_setup"

    @classmethod
    def poll(cls, context):
        return tool.Ifc.get()

    def draw(self, context):
        if not ClassificationsData.is_loaded:
            ClassificationsData.load()

        self.props = tool.Classification.get_classification_props()
        assert self.layout

        row = self.layout.row(align=True)
        row.label(text="Source", icon="OUTLINER")
        row.prop(self.props, "classification_source", text="")

        if self.props.classification_source == "FILE":
            self.draw_add_file_ui(context)
        elif self.props.classification_source == "MANUAL":
            self.draw_add_manual_ui(context)
        else:
            self.draw_add_bsdd_ui(context)

        for classification in ClassificationsData.data["classifications"]:
            if self.props.active_classification_id == classification["id"]:
                self.draw_editable_ui()
            else:
                self.draw_ui(classification)

    def draw_add_manual_ui(self, context):
        assert self.layout
        if self.props.is_adding:
            bonsai.bim.helper.draw_attributes(self.props.classification_attributes, self.layout)
            row = self.layout.row(align=True)
            row.operator("bim.add_manual_classification", text="Save", icon="CHECKMARK")
            row.operator("bim.disable_adding_manual_classification", text="", icon="CANCEL")
        else:
            row = self.layout.row()
            row.operator("bim.enable_adding_manual_classification", text="Add Classification", icon="ADD")

    def draw_add_bsdd_ui(self, context):
        assert self.layout
        row = self.layout.row()
        row.operator("bim.add_classification_from_bsdd", icon="ADD")

    def draw_add_file_ui(self, context):
        assert self.layout
        if ClassificationsData.data["has_classification_file"]:
            row = self.layout.row(align=True)
            row.prop(self.props, "available_classifications", text="")
            row.operator("bim.load_classification_library", text="", icon="IMPORT")
            row.operator("bim.add_classification", text="", icon="ADD")
        else:
            row = self.layout.row(align=True)
            row.label(text="No Active Classification Library")
            row.operator("bim.load_classification_library", text="", icon="IMPORT")

    def draw_editable_ui(self) -> None:
        assert self.layout
        row = self.layout.row(align=True)
        row.operator("bim.edit_classification", text="Save changes", icon="CHECKMARK")
        row.operator("bim.disable_editing_classification", text="", icon="CANCEL")
        bonsai.bim.helper.draw_attributes(self.props.classification_attributes, self.layout)

    def draw_ui(self, classification: dict[str, Any]) -> None:
        assert self.layout
        row = self.layout.row(align=True)
        row.label(text=classification["Name"], icon="ASSET_MANAGER")
        if not self.props.active_classification_id:
            op = row.operator("bim.enable_editing_classification", text="", icon="GREASEPENCIL")
            op.classification = classification["id"]
        row.operator("bim.remove_classification", text="", icon="X").classification = classification["id"]


class ReferenceUI:
    layout: Union[bpy.types.UILayout, None]
    data: type[
        Union[
            ObjectClassificationsData,
            MaterialClassificationsData,
            CostClassificationsData,
            ZoneClassificationsData,
        ]
    ]

    obj: str
    """Object name."""

    def get_object_name(self, context: bpy.types.Context) -> str:
        return ""

    def draw(self, context: bpy.types.Context) -> None:
        if not self.data.is_loaded:
            self.data.load()
        self.obj = self.get_object_name(context)
        self.draw_ui(context)

    def draw_ui(self, context: bpy.types.Context) -> None:
        self.sprops = tool.Classification.get_classification_props()
        self.bprops = tool.Bsdd.get_bsdd_props()
        self.props = tool.Classification.get_classification_reference_props()
        self.file = tool.Ifc.get()

        self.draw_add_ui(context)

        if not self.data.data["references"]:
            row = self.layout.row(align=True)
            row.label(text="No References")

        for reference in self.data.data["references"]:
            if self.props.active_reference_id == reference["id"]:
                self.draw_editable_ui()
            else:
                self.draw_reference_ui(reference)

    def draw_add_ui(self, context: bpy.types.Context) -> None:
        row = self.layout.row(align=True)
        row.label(text="Source", icon="OUTLINER")
        row.prop(self.sprops, "classification_source", text="")

        if self.sprops.classification_source == "FILE":
            self.draw_add_file_ui(context)
        elif self.sprops.classification_source == "MANUAL":
            self.draw_add_manual_ui(context)
        else:
            self.draw_add_bsdd_ui(context)

    def draw_add_manual_ui(self, context: object) -> None:
        row = self.layout.row()
        row.prop(self.props, "classifications", text="")
        if self.props.is_adding:
            bonsai.bim.helper.draw_attributes(self.props.reference_attributes, self.layout)
            row = self.layout.row(align=True)
            op = row.operator("bim.add_manual_classification_reference", text="Save", icon="CHECKMARK")
            op.obj_type = self.data.obj_type
            row.operator("bim.disable_adding_manual_classification_reference", text="", icon="CANCEL")
        else:
            row = self.layout.row()
            row.operator("bim.enable_adding_manual_classification_reference", text="Add Reference", icon="ADD")

    def draw_add_bsdd_ui(self, context: object) -> None:
        row = self.layout.row(align=True)
        row.prop(self.bprops, "keyword", text="")
        row.prop(self.bprops, "should_filter_ifc_class", text="", icon="FILTER")
        row.operator("bim.search_bsdd_classifications", text="", icon="VIEWZOOM")

        if len(self.bprops.classifications):
            self.layout.template_list(
                "BIM_UL_bsdd_classifications",
                "",
                self.bprops,
                "classifications",
                self.bprops,
                "active_classification_index",
            )
        else:
            row = self.layout.row()
            row.label(text="No Search Results")

        if self.bprops.active_classification_index < len(self.bprops.classifications):
            row = self.layout.row(align=True)
            op = row.operator(
                "bim.add_classification_reference_from_bsdd", text="Add Classification Reference", icon="ADD"
            )
            op.obj = self.obj
            op.obj_type = self.data.obj_type

    def draw_add_file_ui(self, context: object) -> None:
        if not self.data.data["active_classification_library"]:
            row = self.layout.row(align=True)
            row.label(text="No Active Classification Library", icon="ERROR")
            row.operator("bim.load_classification_library", text="", icon="IMPORT")
            return

        row = self.layout.row(align=True)
        row.label(text=f"Active Classification Library: {self.data.data['active_classification_library']}")
        # row.prop(self.sprops, "available_classifications", text="")
        if not self.sprops.available_library_references:
            op = row.operator("bim.change_classification_level", text="", icon="GREASEPENCIL")
            op.parent_id = int(self.sprops.available_classifications)
            return
        if self.sprops.active_library_referenced_source:
            op = row.operator("bim.change_classification_level", text="", icon="FRAME_PREV")
            op.parent_id = self.sprops.active_library_referenced_source
        if self.sprops.active_library_reference_index < len(self.sprops.available_library_references):
            op = row.operator("bim.add_classification_reference", text="", icon="ADD")
            op.obj = self.obj
            op.obj_type = self.data.obj_type
            op.reference = self.sprops.available_library_references[
                self.sprops.active_library_reference_index
            ].ifc_definition_id
        row.operator("bim.disable_editing_classification_references", text="", icon="CANCEL")
        self.layout.template_list(
            "BIM_UL_classifications",
            "",
            self.sprops,
            "available_library_references",
            self.sprops,
            "active_library_reference_index",
        )

    def draw_editable_ui(self) -> None:
        row = self.layout.row(align=True)
        row.operator("bim.edit_classification_reference", text="Save changes", icon="CHECKMARK")
        row.operator("bim.disable_editing_classification_reference", text="", icon="CANCEL")
        bonsai.bim.helper.draw_attributes(self.props.reference_attributes, self.layout)

    def draw_reference_ui(self, reference: dict[str, Any]) -> None:
        row = self.layout.row(align=True)
        if self.file.schema == "IFC2X3":
            name = reference["ItemReference"] or "No Identification"
        else:
            name = reference["Identification"] or "No Identification"
        row.label(text=name, icon="ASSET_MANAGER")
        row.label(text=reference["Name"] or "")
        if reference["Location"]:
            row.operator("bim.open_uri", icon="URL", text="").uri = reference["Location"]
        if not self.props.active_reference_id:
            op = row.operator("bim.enable_editing_classification_reference", text="", icon="GREASEPENCIL")
            op.reference = reference["id"]
        op = row.operator("bim.remove_classification_reference", text="", icon="X")
        op.reference = reference["id"]
        op.obj = self.obj
        op.obj_type = self.data.obj_type


class BIM_PT_classification_references(Panel, ReferenceUI):
    bl_label = "Classification References"
    bl_idname = "BIM_PT_classification_references"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"
    bl_parent_id = "BIM_PT_tab_object_metadata"

    data = ObjectClassificationsData

    @classmethod
    def poll(cls, context):
        return bool((obj := context.active_object) and tool.Ifc.get_entity(obj))

    def get_object_name(self, context: bpy.types.Context) -> str:
        assert (obj := context.active_object)
        return obj.name


class BIM_PT_material_classifications(Panel, ReferenceUI):
    bl_label = "Material Classifications"
    bl_idname = "BIM_PT_material_classifications"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_parent_id = "BIM_PT_materials"

    data = MaterialClassificationsData

    @classmethod
    def poll(cls, context):
        if not tool.Ifc.get():
            return False
        props = tool.Material.get_material_props()
        if props.is_editing and (material := props.active_material) and material.ifc_definition_id:
            return True
        return False


class BIM_PT_cost_classifications(Panel, ReferenceUI):
    bl_label = "Cost Item Classifications"
    bl_idname = "BIM_PT_cost_classifications"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_parent_id = "BIM_PT_cost_schedules"

    data = CostClassificationsData

    @classmethod
    def poll(cls, context):
        if not tool.Ifc.get():
            return False
        props = tool.Cost.get_cost_props()
        return bool(props.cost_items)


class BIM_PT_zone_classifications(Panel, ReferenceUI):
    bl_label = "Zone Classifications"
    bl_idname = "BIM_PT_zone_classifications"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_parent_id = "BIM_PT_zones"

    data = ZoneClassificationsData

    @classmethod
    def poll(cls, context):
        props = tool.System.get_zone_props()
        return bool(props.active_zone)


class BIM_UL_classifications(UIList):
    def draw_item(
        self,
        context,
        layout: bpy.types.UILayout,
        data: BIMClassificationProperties,
        item: ClassificationReference,
        icon,
        active_data,
        active_propname,
    ):
        if item:
            if item.has_references:
                op = layout.operator("bim.change_classification_level", text="", icon="DISCLOSURE_TRI_RIGHT")
                op.parent_id = item.ifc_definition_id
            layout.label(text=item.identification)
            layout.label(text=item.name)
