# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
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
import blenderbim.core.tool
import blenderbim.tool as tool


class Container(blenderbim.core.tool.Container):
    @classmethod
    def can_contain(cls, structure_obj, element_obj):
        structure = tool.Ifc.get_entity(structure_obj)
        element = tool.Ifc.get_entity(element_obj)
        if not structure or not element:
            return False
        if tool.Ifc.get_schema() == "IFC2X3":
            if not structure.is_a("IfcSpatialStructureElement"):
                return False
        else:
            if not structure.is_a("IfcSpatialElement"):
                return False
        if not element.is_a("IfcElement"):
            return False
        return True

    @classmethod
    def enable_editing(cls, obj):
        obj.BIMObjectSpatialProperties.is_editing = True

    @classmethod
    def disable_editing(cls, obj):
        obj.BIMObjectSpatialProperties.is_editing = False

    @classmethod
    def import_containers(cls, parent=None):
        props = bpy.context.scene.BIMSpatialProperties
        props.containers.clear()

        if not parent:
            parent = tool.Ifc.get().by_type("IfcProject")[0]

        props.active_container_id = parent.id()

        for rel in parent.IsDecomposedBy or []:
            related_objects = []
            for element in rel.RelatedObjects:
                if element.ObjectPlacement:
                    related_objects.append(
                        (element, ifcopenshell.util.placement.get_local_placement(element.ObjectPlacement)[2][3])
                    )
                else:
                    related_objects.append((element, float("-inf")))
            related_objects = sorted(related_objects, key=lambda e: e[1])
            for element in related_objects:
                element = element[0]
                new = props.containers.add()
                new.name = element.Name or "Unnamed"
                new.long_name = element.LongName or ""
                new.has_decomposition = bool(element.IsDecomposedBy)
                new.ifc_definition_id = element.id()
