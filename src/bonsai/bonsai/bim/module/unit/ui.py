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

import bonsai.bim.helper
from bpy.types import Panel, UIList
from bonsai.bim.ifc import IfcStore
from bonsai.bim.helper import prop_with_search
from bonsai.bim.module.unit.data import UnitsData


class BIM_PT_units(Panel):
    bl_label = "Units"
    bl_idname = "BIM_PT_units"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_parent_id = "BIM_PT_tab_geometry"

    @classmethod
    def poll(cls, context):
        file = IfcStore.get_file()
        return file

    def draw(self, context):
        if not UnitsData.is_loaded:
            UnitsData.load()

        self.props = context.scene.BIMUnitProperties

        row = self.layout.row(align=True)
        row.label(text="{} Units Found".format(UnitsData.data["total_units"]), icon="SNAP_GRID")
        if self.props.is_editing:
            row.operator("bim.disable_unit_editing_ui", text="", icon="CANCEL")
        else:
            row.operator("bim.load_units", text="", icon="GREASEPENCIL")

        if not self.props.is_editing:
            row = self.layout.row(align=True)
            row.label(text="Length Unit", icon="ARROW_LEFTRIGHT")
            row.label(text=str(UnitsData.data["length_unit"]))

            row = self.layout.row(align=True)
            row.label(text="Area Unit", icon="ORIENTATION_VIEW")
            row.label(text=str(UnitsData.data["area_unit"]))

            row = self.layout.row(align=True)
            row.label(text="Volume Unit", icon="EMPTY_ARROWS")
            row.label(text=str(UnitsData.data["volume_unit"]))
            return

        row = self.layout.row(align=True)
        prop_with_search(row, self.props, "unit_classes", text="")

        if self.props.unit_classes == "IfcMonetaryUnit":
            row.operator("bim.add_monetary_unit", text="", icon="ADD")
        elif self.props.unit_classes in ("IfcConversionBasedUnit", "IfcConversionBasedUnitWithOffset"):
            prop_with_search(row, self.props, "conversion_unit_types", text="")
            op = row.operator("bim.add_conversion_based_unit", text="", icon="ADD")
            op.name = self.props.conversion_unit_types
        elif self.props.unit_classes == "IfcDerivedUnit":
            pass  # TODO
        elif self.props.unit_classes == "IfcSIUnit":
            prop_with_search(row, self.props, "named_unit_types", text="")
            op = row.operator("bim.add_si_unit", text="", icon="ADD")
            op.unit_type = self.props.named_unit_types
        elif self.props.unit_classes == "IfcContextDependentUnit":
            prop_with_search(row, self.props, "named_unit_types", text="")
            op = row.operator("bim.add_context_dependent_unit", text="", icon="ADD")
            op.name = "THINGAMAJIG"
            op.unit_type = self.props.named_unit_types

        self.layout.template_list(
            "BIM_UL_units",
            "",
            self.props,
            "units",
            self.props,
            "active_unit_index",
        )

        if self.props.active_unit_id:
            self.draw_editable_ui(context)

    def draw_editable_ui(self, context):
        bonsai.bim.helper.draw_attributes(self.props.unit_attributes, self.layout)


class BIM_UL_units(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        props = context.scene.BIMUnitProperties
        if item:
            icon = "MOD_MESHDEFORM"
            if item.ifc_class == "IfcSIUnit":
                icon = "SNAP_GRID"
            elif item.ifc_class == "IfcMonetaryUnit":
                icon = "COPY_ID"

            row = layout.row(align=True)
            row.label(text=item.unit_type or "No Type", icon=icon)
            row.label(text=item.name or "Unnamed")

            if item.is_assigned:
                op = row.operator("bim.unassign_unit", text="", icon="KEYFRAME_HLT", emboss=False)
                op.unit = item.ifc_definition_id
            else:
                op = row.operator("bim.assign_unit", text="", icon="KEYFRAME", emboss=False)
                op.unit = item.ifc_definition_id

            if props.active_unit_id == item.ifc_definition_id:
                row.operator("bim.edit_unit", text="", icon="CHECKMARK").unit = item.ifc_definition_id
                row.operator("bim.disable_editing_unit", text="", icon="CANCEL")
            elif props.active_unit_id:
                row.operator("bim.remove_unit", text="", icon="X").unit = item.ifc_definition_id
            else:
                op = row.operator("bim.enable_editing_unit", text="", icon="GREASEPENCIL")
                op.unit = item.ifc_definition_id
                row.operator("bim.remove_unit", text="", icon="X").unit = item.ifc_definition_id
