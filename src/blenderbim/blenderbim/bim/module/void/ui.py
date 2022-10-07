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

import bpy
from bpy.types import Panel
from ifcopenshell.api.void.data import Data
from blenderbim.bim.ifc import IfcStore
from blenderbim.bim.module.void.data import BooleansData


class BIM_PT_voids(Panel):
    bl_label = "IFC Voids"
    bl_idname = "BIM_PT_voids"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"
    bl_parent_id = "BIM_PT_geometry_object"

    @classmethod
    def poll(cls, context):
        if not context.active_object:
            return False
        if not IfcStore.get_element(context.active_object.BIMObjectProperties.ifc_definition_id):
            return False
        return IfcStore.get_file()

    def draw(self, context):
        props = context.active_object.BIMObjectProperties
        file = IfcStore.get_file()
        if props.ifc_definition_id not in Data.products:
            Data.load(file, props.ifc_definition_id)
        active_object_is_an_opening = file.by_id(props.ifc_definition_id).is_a("IfcOpeningElement")
        row = self.layout.row(align=True)
        if len(context.selected_objects) == 2:
            op = row.operator("bim.add_opening", icon="ADD", text="Add Opening")
            for obj in context.selected_objects:
                if (
                    "IfcOpeningElement" in obj.name
                    or "IfcOpeningStandardCase" in obj.name
                    or not obj.BIMObjectProperties.ifc_definition_id
                ):
                    op.opening = obj.name
                elif len(obj.children) == 1 and not obj.children[0].BIMObjectProperties.ifc_definition_id:
                    op.opening = obj.children[0].name
                else:
                    op.obj = obj.name

            opening_id = None
            obj_name = None
            for obj in context.selected_objects:
                if obj.BIMObjectProperties.ifc_definition_id in Data.openings:
                    opening_id = obj.BIMObjectProperties.ifc_definition_id
                elif obj.BIMObjectProperties.ifc_definition_id in Data.fillings:
                    opening_id = Data.fillings[obj.BIMObjectProperties.ifc_definition_id]["FillsVoid"]
                else:
                    obj_name = obj.name
            if opening_id and obj_name:
                op = row.operator("bim.remove_opening", icon="X", text="Remove Opening").opening_id = opening_id
        else:
            row.label(text="Select an opening and an element to modify", icon="HELP")

        opening_ids = Data.products[props.ifc_definition_id]
        if not opening_ids and not active_object_is_an_opening:
            row = self.layout.row(align=True)
            row.label(text="No Openings", icon="SELECT_SUBTRACT")
        for opening_id in opening_ids:
            opening = Data.openings[opening_id]
            if opening["HasFillings"]:
                for filling_id in opening["HasFillings"]:
                    filling = Data.fillings.get(filling_id)
                    if filling is None:
                        continue
                    row = self.layout.row(align=True)
                    row.label(text=opening["Name"], icon="SELECT_SUBTRACT")
                    row.label(text=filling["Name"], icon="SELECT_INTERSECT")
            else:
                row = self.layout.row(align=True)
                row.label(text=opening["Name"], icon="SELECT_SUBTRACT")
            op = row.operator("bim.remove_opening", icon="X", text="").opening_id = opening_id
        if props.ifc_definition_id in Data.openings:
            for filling_id in Data.openings[props.ifc_definition_id]["HasFillings"]:
                filling = Data.fillings.get(filling_id)
                if filling is None:
                    continue
                row = self.layout.row(align=True)
                row.label(text=filling["Name"], icon="SELECT_INTERSECT")
                op = row.operator("bim.remove_filling", icon="X", text="")
                op.obj = IfcStore.get_element(filling_id).name
        if active_object_is_an_opening:
            pass
        elif props.ifc_definition_id not in Data.fillings:
            row = self.layout.row(align=True)
            row.prop(context.scene.VoidProperties, "desired_opening", text="", icon="SELECT_INTERSECT")
            row.operator("bim.add_filling", icon="ADD", text="")
        else:
            opening = Data.openings[Data.fillings[props.ifc_definition_id]["FillsVoid"]]
            row = self.layout.row(align=True)
            row.label(text=opening["Name"], icon="SELECT_INTERSECT")
            row.operator("bim.remove_filling", icon="X", text="")


class BIM_PT_booleans(Panel):
    bl_label = "IFC Booleans"
    bl_idname = "BIM_PT_booleans"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "data"

    @classmethod
    def poll(cls, context):
        return (
            context.active_object is not None
            and context.active_object.type == "MESH"
            and hasattr(context.active_object.data, "BIMMeshProperties")
            and (
                context.active_object.data.BIMMeshProperties.ifc_definition_id
                or context.active_object.data.BIMMeshProperties.ifc_boolean_id
            )
        )

    def draw(self, context):
        if not BooleansData.is_loaded:
            BooleansData.load()

        if not context.active_object.data:
            return
        layout = self.layout
        props = context.active_object.data.BIMMeshProperties

        if context.active_object.data.BIMMeshProperties.ifc_definition_id:
            row = layout.row(align=True)
            row.label(text=f"{BooleansData.data['total_booleans']} Booleans Found")
            row.operator("bim.add_boolean", text="", icon="ADD")
            row.operator("bim.show_booleans", text="", icon="HIDE_OFF")
            row.operator("bim.hide_booleans", text="", icon="HIDE_ON")
        elif context.active_object.data.BIMMeshProperties.ifc_boolean_id:
            row = layout.row()
            row.operator("bim.remove_booleans", text="Remove Boolean", icon="X")
