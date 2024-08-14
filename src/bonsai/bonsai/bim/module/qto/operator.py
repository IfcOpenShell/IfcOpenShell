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
import ifcopenshell
import ifcopenshell.api
import bonsai.tool as tool
import bonsai.core.qto as core
from bonsai.bim.ifc import IfcStore
from bonsai.bim.module.qto import helper


class CalculateCircleRadius(bpy.types.Operator):
    bl_idname = "bim.calculate_circle_radius"
    bl_label = "Calculate Circle Radius"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.active_object

    def execute(self, context):
        core.calculate_circle_radius(tool.Qto, obj=context.active_object)
        return {"FINISHED"}


class CalculateEdgeLengths(bpy.types.Operator):
    bl_idname = "bim.calculate_edge_lengths"
    bl_label = "Calculate Edge Lengths"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.selected_objects and context.active_object

    def execute(self, context):
        result = helper.calculate_edges_lengths([o for o in context.selected_objects if o.type == "MESH"], context)
        context.scene.BIMQtoProperties.qto_result = str(round(result, 3))
        return {"FINISHED"}


class CalculateFaceAreas(bpy.types.Operator):
    bl_idname = "bim.calculate_face_areas"
    bl_label = "Calculate Face Areas"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.selected_objects and context.active_object

    def execute(self, context):
        result = helper.calculate_faces_areas([o for o in context.selected_objects if o.type == "MESH"], context)
        context.scene.BIMQtoProperties.qto_result = str(round(result, 3))
        return {"FINISHED"}


class CalculateObjectVolumes(bpy.types.Operator):
    bl_idname = "bim.calculate_object_volumes"
    bl_label = "Calculate Object Volumes"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.selected_objects and context.active_object

    def execute(self, context):
        result = helper.calculate_volumes([o for o in context.selected_objects if o.type == "MESH"], context)
        context.scene.BIMQtoProperties.qto_result = str(round(result, 3))
        return {"FINISHED"}


class CalculateFormworkArea(bpy.types.Operator):
    bl_idname = "bim.calculate_formwork_area"
    bl_label = "Calculate Formwork Area"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.selected_objects and context.active_object

    def execute(self, context):
        result = helper.calculate_formwork_area([o for o in context.selected_objects if o.type == "MESH"], context)
        context.scene.BIMQtoProperties.qto_result = str(round(result, 3))
        return {"FINISHED"}


class CalculateSideFormworkArea(bpy.types.Operator):
    bl_idname = "bim.calculate_side_formwork_area"
    bl_label = "Calculate Side Formwork Area"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.selected_objects and context.active_object

    def execute(self, context):
        result = helper.calculate_side_formwork_area([o for o in context.selected_objects if o.type == "MESH"], context)
        context.scene.BIMQtoProperties.qto_result = str(round(result, 3))
        return {"FINISHED"}


class CalculateSingleQuantity(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.calculate_single_quantity"
    bl_label = "Calculate Single Quantity"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Calculate a single quantity using a function on the selected objects"

    @classmethod
    def poll(cls, context):
        return tool.Ifc.get() and context.selected_objects

    def _execute(self, context):
        import ifc5d.qto

        props = context.scene.BIMQtoProperties
        elements = set()
        for obj in context.selected_objects:
            element = tool.Ifc.get_entity(obj)
            if element:
                elements.add(element)

        rules = {
            "calculators": {
                props.calculator: {
                    "IfcProduct": {props.qto_name: {props.prop_name: props.calculator_function}},
                }
            }
        }

        ifc_file = tool.Ifc.get()
        results = ifc5d.qto.quantify(ifc_file, elements, rules)
        ifc5d.qto.edit_qtos(ifc_file, results)
        return {"FINISHED"}


class PerformQuantityTakeOff(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.perform_quantity_take_off"
    bl_label = "Perform Quantity Take-off"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = (
        "Perform a quantity take off on selected objects based of a QTO rule configuration."
        "If no objects are selected, quantities calculated for all available IfcElements."
    )

    @classmethod
    def poll(cls, context):
        return tool.Ifc.get()

    def _execute(self, context):
        import ifc5d.qto

        props = context.scene.BIMQtoProperties

        if context.selected_objects:
            elements = set()
            for obj in context.selected_objects:
                element = tool.Ifc.get_entity(obj)
                if element:
                    elements.add(element)
        else:
            elements = set(tool.Ifc.get().by_type("IfcElement"))

        rules = ifc5d.qto.rules[props.qto_rule]

        ifc_file = tool.Ifc.get()
        results = ifc5d.qto.quantify(ifc_file, elements, rules)
        ifc5d.qto.edit_qtos(ifc_file, results)

        self.report({"INFO"}, f"Quantities are calculated for {len(elements)} elements.")
        return {"FINISHED"}
