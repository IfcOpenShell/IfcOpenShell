# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2022 Dion Moult <dion@thinkmoult.com>
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
import ifcopenshell.util.system
import blenderbim.core.tool
import blenderbim.tool as tool


class System(blenderbim.core.tool.System):
    @classmethod
    def disable_editing_system(cls):
        bpy.context.scene.BIMSystemProperties.active_system_id = 0

    @classmethod
    def disable_system_editing_ui(cls):
        bpy.context.scene.BIMSystemProperties.is_editing = False

    @classmethod
    def enable_system_editing_ui(cls):
        bpy.context.scene.BIMSystemProperties.is_editing = True

    @classmethod
    def export_system_attributes(cls):
        return blenderbim.bim.helper.export_attributes(bpy.context.scene.BIMSystemProperties.system_attributes)

    @classmethod
    def import_system_attributes(cls, system):
        blenderbim.bim.helper.import_attributes2(system, bpy.context.scene.BIMSystemProperties.system_attributes)

    @classmethod
    def import_systems(cls):
        props = bpy.context.scene.BIMSystemProperties
        props.systems.clear()
        for system in tool.Ifc.get().by_type("IfcSystem"):
            if system.is_a() in ["IfcZone", "IfcStructuralAnalysisModel"]:
                continue
            new = props.systems.add()
            new.ifc_definition_id = system.id()
            new.name = system.Name or "Unnamed"
            new.ifc_class = system.is_a()

    @classmethod
    def select_system_products(cls, system):
        for element in ifcopenshell.util.system.get_system_elements(system):
            obj = tool.Ifc.get_object(element)
            if obj:
                obj.select_set(True)

    @classmethod
    def set_active_system(cls, system):
        bpy.context.scene.BIMSystemProperties.active_system_id = system.id()
