# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2020, 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of BlenderBIM Add-on.
#
# BlenderBIM Add-on is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# BlenderBIM Add-on is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with BlenderBIM Add-on.  If not, see <http://www.gnu.org/licenses/>.

import blenderbim.bim.helper
from bpy.types import Panel, UIList
from blenderbim.bim.ifc import IfcStore
from ifcopenshell.api.unit.data import Data


class BIM_PT_units(Panel):
    bl_label = "IFC Units"
    bl_idname = "BIM_PT_units"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"

    @classmethod
    def poll(cls, context):
        file = IfcStore.get_file()
        return file

    def draw(self, context):
        self.file = IfcStore.get_file()
        if not Data.is_loaded:
            Data.load(self.file)
        self.props = context.scene.BIMUnitProperties

        row = self.layout.row(align=True)
        row.label(text="{} Units Found".format(len(Data.units)), icon="SNAP_GRID")
        if self.props.is_editing:
            row.operator("bim.disable_unit_editing_ui", text="", icon="CANCEL")
        else:
            row.operator("bim.load_units", text="", icon="GREASEPENCIL")

        if not self.props.is_editing:
            return

        row = self.layout.row(align=True)
        row.prop(self.props, "unit_classes", text="")

        if self.props.unit_classes == "IfcMonetaryUnit":
            row.operator("bim.add_monetary_unit", text="", icon="ADD")
        elif self.props.unit_classes == "IfcDerivedUnit":
            pass  # TODO
        elif self.props.unit_classes == "IfcSIUnit":
            row.prop(self.props, "named_unit_types", text="")
            row.operator("bim.add_si_unit", text="", icon="ADD")
        elif self.props.unit_classes == "IfcContextDependentUnit":
            row.prop(self.props, "named_unit_types", text="")
            row.operator("bim.add_context_dependent_unit", text="", icon="ADD")

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
        blenderbim.bim.helper.draw_attributes(self.props.unit_attributes, self.layout)


class BIM_UL_units(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        props = context.scene.BIMUnitProperties
        if item:
            row = layout.row(align=True)
            row.label(text=item.unit_type or "No Type", icon=item.icon)
            row.label(text=item.name or "Unnamed")

            if item.is_assigned:
                op = row.operator("bim.unassign_unit", text="", icon="KEYFRAME_HLT", emboss=False)
                op.unit = item.ifc_definition_id
            else:
                op = row.operator("bim.assign_unit", text="", icon="KEYFRAME", emboss=False)
                op.unit = item.ifc_definition_id

            if props.active_unit_id == item.ifc_definition_id:
                row.operator("bim.edit_unit", text="", icon="CHECKMARK")
                row.operator("bim.disable_editing_unit", text="", icon="CANCEL")
            elif props.active_unit_id:
                row.operator("bim.remove_unit", text="", icon="X").unit = item.ifc_definition_id
            else:
                op = row.operator("bim.enable_editing_unit", text="", icon="GREASEPENCIL")
                op.unit = item.ifc_definition_id
                row.operator("bim.remove_unit", text="", icon="X").unit = item.ifc_definition_id
