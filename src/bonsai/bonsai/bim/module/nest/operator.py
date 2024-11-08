# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2023 Dion Moult <dion@thinkmoult.com>
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
import ifcopenshell.util.element
import bonsai.tool as tool
import bonsai.core.nest as core
from bonsai.bim.ifc import IfcStore


class BIM_OT_nest_assign_object(bpy.types.Operator, tool.Ifc.Operator):
    """Create nest relationship between two ifc elements"""

    bl_idname = "bim.nest_assign_object"
    bl_label = "Assign Object To Nesting"
    bl_options = {"REGISTER", "UNDO"}
    relating_object: bpy.props.IntProperty()

    def _execute(self, context):
        relating_obj = None
        if self.relating_object:
            relating_obj = tool.Ifc.get_object(tool.Ifc.get().by_id(self.relating_object))
        elif context.active_object:
            relating_obj = context.active_object
        if not relating_obj:
            return

        for obj in bpy.context.selected_objects:
            if obj == relating_obj:
                continue
            element = tool.Ifc.get_entity(obj)
            if not element:
                continue
            result = core.assign_object(
                tool.Ifc,
                tool.Nest,
                tool.Collector,
                relating_obj=relating_obj,
                related_obj=obj,
            )
            if not result:
                self.report({"ERROR"}, f" Cannot nest {obj.name} to {relating_obj.name}")


class BIM_OT_nest_unassign_object(bpy.types.Operator, tool.Ifc.Operator):
    """Remove nest relationship between two ifc elements"""

    bl_idname = "bim.nest_unassign_object"
    bl_label = "Unassign Object From Nesting"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        for obj in bpy.context.selected_objects:
            element = tool.Ifc.get_entity(obj)
            if not element:
                continue
            nest = ifcopenshell.util.element.get_nest(element)
            if not nest:
                continue
            core.unassign_object(
                tool.Ifc,
                tool.Nest,
                tool.Collector,
                relating_obj=tool.Ifc.get_object(nest),
                related_obj=tool.Ifc.get_object(element),
            )


class BIM_OT_enable_editing_nest(bpy.types.Operator, tool.Ifc.Operator):
    """Enable editing nest relationship"""

    bl_idname = "bim.enable_editing_nest"
    bl_label = "Enable Editing Nest"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        core.enable_editing_nest(tool.Nest, obj=context.active_object)


class BIM_OT_disable_editing_nest(bpy.types.Operator, tool.Ifc.Operator):
    """Disable editing nest relationship"""

    bl_idname = "bim.disable_editing_nest"
    bl_label = "Disable Editing Nest"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        core.disable_editing_nest(tool.Nest, obj=context.active_object)


class BIM_OT_select_components(bpy.types.Operator):
    """Select Components"""

    bl_idname = "bim.select_components"
    bl_label = "Select Components"
    bl_options = {"REGISTER", "UNDO"}
    obj: bpy.props.StringProperty()

    def execute(self, context):
        self.file = IfcStore.get_file()
        obj = bpy.data.objects.get(self.obj) or context.active_object
        components = ifcopenshell.util.element.get_components(tool.Ifc.get_entity(obj))
        component_objs = set(tool.Ifc.get_object(c) for c in components)
        selectable_component_objs = set(context.selectable_objects).intersection(component_objs)
        for selectable_component_obj in selectable_component_objs:
            selectable_component_obj.select_set(True)
        return {"FINISHED"}


class BIM_OT_select_nest(bpy.types.Operator):
    """Select Nest"""

    bl_idname = "bim.select_nest"
    bl_label = "Select Nest"
    bl_options = {"REGISTER", "UNDO"}
    obj: bpy.props.StringProperty()

    def execute(self, context):
        self.file = IfcStore.get_file()
        obj = bpy.data.objects.get(self.obj) or context.active_object
        nest = ifcopenshell.util.element.get_nest(tool.Ifc.get_entity(obj))
        nest_obj = tool.Ifc.get_object(nest)
        if nest_obj in context.selectable_objects:
            nest_obj.select_set(True)
            bpy.context.view_layer.objects.active = nest_obj
        return {"FINISHED"}
