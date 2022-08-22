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
import blenderbim.core.root
import blenderbim.core.spatial
import blenderbim.tool as tool


class Spatial(blenderbim.core.tool.Spatial):
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
            if not structure.is_a("IfcSpatialStructureElement") and not structure.is_a(
                "IfcExternalSpatialStructureElement"
            ):
                return False
        if not hasattr(element, "ContainedInStructure"):
            return False
        return True

    @classmethod
    def can_reference(cls, structure, element):
        if not structure or not element:
            return False
        if tool.Ifc.get_schema() == "IFC2X3":
            if not structure.is_a("IfcSpatialStructureElement"):
                return False
        else:
            if not structure.is_a("IfcSpatialElement"):
                return False
        if not hasattr(element, "ReferencedInStructures"):
            return False
        return True

    @classmethod
    def disable_editing(cls, obj):
        obj.BIMObjectSpatialProperties.is_editing = False

    @classmethod
    def duplicate_object_and_data(cls, obj):
        new_obj = obj.copy()
        if obj.data:
            new_obj.data = obj.data.copy()
        return new_obj

    @classmethod
    def enable_editing(cls, obj):
        obj.BIMObjectSpatialProperties.is_editing = True

    @classmethod
    def get_container(cls, element):
        return ifcopenshell.util.element.get_container(element)

    @classmethod
    def get_decomposed_elements(cls, container):
        return ifcopenshell.util.element.get_decomposition(container)

    @classmethod
    def get_object_matrix(cls, obj):
        return obj.matrix_world

    @classmethod
    def get_relative_object_matrix(cls, target_obj, relative_to_obj):
        return relative_to_obj.matrix_world.inverted() @ target_obj.matrix_world

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
                related_objects.append((element, ifcopenshell.util.placement.get_storey_elevation(element)))
            related_objects = sorted(related_objects, key=lambda e: e[1])
            for element in related_objects:
                element = element[0]
                new = props.containers.add()
                new.name = element.Name or "Unnamed"
                new.long_name = element.LongName or ""
                new.has_decomposition = bool(element.IsDecomposedBy)
                new.ifc_definition_id = element.id()

    @classmethod
    def run_root_copy_class(cls, obj=None):
        return blenderbim.core.root.copy_class(tool.Ifc, tool.Collector, tool.Geometry, tool.Root, obj=obj)

    @classmethod
    def run_spatial_assign_container(cls, structure_obj=None, element_obj=None):
        return blenderbim.core.spatial.assign_container(
            tool.Ifc, tool.Collector, tool.Spatial, structure_obj=structure_obj, element_obj=element_obj
        )

    @classmethod
    def select_object(cls, obj):
        obj.select_set(True)

    @classmethod
    def set_active_object(cls, obj):
        bpy.context.view_layer.objects.active = obj
        cls.select_object(obj)

    @classmethod
    def set_relative_object_matrix(cls, target_obj, relative_to_obj, matrix):
        target_obj.matrix_world = relative_to_obj.matrix_world @ matrix
