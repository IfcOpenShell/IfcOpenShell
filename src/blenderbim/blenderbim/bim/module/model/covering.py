# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2023 Dion Moult <dion@thinkmoult.com>
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
import ifcopenshell
import blenderbim.tool as tool
import blenderbim.core.covering as core

class AddInstanceFlooringCoveringFromCursor(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_instance_flooring_covering_from_cursor"
    bl_label = "Add Flooring From Cursor"
    bl_options = {"REGISTER"}
    bl_description = "Add a typed instance flooring covering from cursor position. Move the cursor position into the desired position, select the right space collection and run the operator"

    @classmethod
    def poll(cls, context):
        collection = context.view_layer.active_layer_collection.collection
        collection_obj = collection.BIMCollectionProperties.obj
        relating_type_id = int(bpy.data.scenes["Scene"].BIMModelProperties.relating_type_id)
        relating_type = ifcopenshell.util.element.get_predefined_type(tool.Ifc.get().by_id(relating_type_id))
        return tool.Ifc.get_entity(collection_obj) and relating_type == "FLOORING"

    def _execute(self, context):

        def msg(self, context):
            self.layout.label(text="NO ACTIVE STOREY")

        collection = context.view_layer.active_layer_collection.collection
        collection_obj = collection.BIMCollectionProperties.obj
        if not collection_obj:
            bpy.context.window_manager.popup_menu(msg, title="Error", icon="ERROR")
            return
        spatial_element = tool.Ifc.get_entity(collection_obj)
        if not spatial_element:
            bpy.context.window_manager.popup_menu(msg, title="Error", icon="ERROR")
            return

        core.add_instance_flooring_covering_from_cursor(tool.Ifc, tool.Spatial, tool.Model, tool.Type, tool.Geometry)

class AddInstanceCeilingCoveringFromCursor(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_instance_ceiling_covering_from_cursor"
    bl_label = "Add Ceiling From Cursor"
    bl_options = {"REGISTER"}
    bl_description = "Add a typed instance ceiling covering from cursor position. Move the cursor position into the desired position, select the right space collection and run the operator"

    @classmethod
    def poll(cls, context):
        collection = context.view_layer.active_layer_collection.collection
        collection_obj = collection.BIMCollectionProperties.obj
        relating_type_id = int(bpy.data.scenes["Scene"].BIMModelProperties.relating_type_id)
        relating_type = ifcopenshell.util.element.get_predefined_type(tool.Ifc.get().by_id(relating_type_id))
        return tool.Ifc.get_entity(collection_obj) and relating_type == "CEILING"

    def _execute(self, context):

        def msg(self, context):
            self.layout.label(text="NO ACTIVE STOREY")

        collection = context.view_layer.active_layer_collection.collection
        collection_obj = collection.BIMCollectionProperties.obj
        if not collection_obj:
            bpy.context.window_manager.popup_menu(msg, title="Error", icon="ERROR")
            return
        spatial_element = tool.Ifc.get_entity(collection_obj)
        if not spatial_element:
            bpy.context.window_manager.popup_menu(msg, title="Error", icon="ERROR")
            return

        core.add_instance_ceiling_covering_from_cursor(tool.Ifc, tool.Spatial, tool.Model, tool.Type, tool.Geometry, tool.Covering)

class RegenSelectedCoveringObject(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.regen_selected_covering_object"
    bl_label = "Regen"
    bl_options = {"REGISTER"}
    bl_description = "Regen selected covering object"

    @classmethod
    def poll(cls, context):
        active_obj = bpy.context.active_object
        element = tool.Ifc.get_entity(active_obj)
        return element and element.is_a("IfcCovering")

    def _execute(self, context):

        def msg(self, context):
            self.layout.label(text="NO ACTIVE STOREY")

        active_obj = bpy.context.active_object
        element = tool.Ifc.get_entity(active_obj)
        if not  element.is_a("IfcCovering"):
            bpy.context.window_manager.popup_menu(msg, title="Error", icon="ERROR")
            return

        core.regen_selected_covering_object(tool.Ifc, tool.Spatial, tool.Model, tool.Type, tool.Geometry)


class AddInstanceFlooringCoveringsFromWalls(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_instance_flooring_coverings_from_walls"
    bl_label = "Add Flooring From Walls"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Add instance flooring coverings from selected walls. The active object must be a wall and layered vertically"

    @classmethod
    def poll(cls, context):
        active_obj = bpy.context.active_object
        element = tool.Ifc.get_entity(active_obj)
        relating_type_id = int(bpy.data.scenes["Scene"].BIMModelProperties.relating_type_id)
        relating_type = ifcopenshell.util.element.get_predefined_type(tool.Ifc.get().by_id(relating_type_id))
        if element:
            if element.is_a("IfcWall") and tool.Model.get_usage_type(element) == "LAYER2":
                return context.selected_objects and relating_type == "FLOORING"

    def _execute(self, context):
        # This only works based on a 2D plan only considering the standard
        # walls (i.e. prismatic) in the active object storey.
        # In order to run, the active object must be a wall and
        # there must be selected walls

        active_obj = bpy.context.active_object
        if not active_obj:
            self.report({"ERROR"}, "No active object. Please select a wall")
            return

        element = tool.Ifc.get_entity(active_obj)
        if element and not element.is_a("IfcWall"):
            return self.report({"ERROR"}, "The active object is not a wall. Please select a wall.")

        container = ifcopenshell.util.element.get_container(element)
        if not container:
            self.report({"ERROR"}, "The wall is not contained.")

        if not bpy.context.selected_objects:
            self.report({"ERROR"}, "No selected objects found. Please select walls.")
            return

        core.add_instance_flooring_coverings_from_walls(tool.Ifc, tool.Spatial, tool.Collector, tool.Geometry)

class AddInstanceCeilingCoveringsFromWalls(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_instance_ceiling_coverings_from_walls"
    bl_label = "Add Ceiling From Walls"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Add instance ceiling coverings from selected walls. The active object must be a wall and layered vertically"

    @classmethod
    def poll(cls, context):
        active_obj = bpy.context.active_object
        element = tool.Ifc.get_entity(active_obj)
        relating_type_id = int(bpy.data.scenes["Scene"].BIMModelProperties.relating_type_id)
        relating_type = ifcopenshell.util.element.get_predefined_type(tool.Ifc.get().by_id(relating_type_id))
        if element:
            if element.is_a("IfcWall") and tool.Model.get_usage_type(element) == "LAYER2":
                return context.selected_objects and relating_type == "CEILING"

    def _execute(self, context):
        # This only works based on a 2D plan only considering the standard
        # walls (i.e. prismatic) in the active object storey.
        # In order to run, the active object must be a wall and
        # there must be selected walls

        active_obj = bpy.context.active_object
        if not active_obj:
            self.report({"ERROR"}, "No active object. Please select a wall")
            return

        element = tool.Ifc.get_entity(active_obj)
        if element and not element.is_a("IfcWall"):
            return self.report({"ERROR"}, "The active object is not a wall. Please select a wall.")

        container = ifcopenshell.util.element.get_container(element)
        if not container:
            self.report({"ERROR"}, "The wall is not contained.")

        if not bpy.context.selected_objects:
            self.report({"ERROR"}, "No selected objects found. Please select walls.")
            return

        core.add_instance_ceiling_coverings_from_walls(tool.Ifc, tool.Spatial, tool.Collector, tool.Geometry, tool.Covering)

