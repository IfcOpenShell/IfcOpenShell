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
import math
import bmesh
import ifcopenshell
import ifcopenshell.api
import ifcopenshell.util.unit
import ifcopenshell.util.element
import ifcopenshell.util.representation
import mathutils.geometry
import blenderbim.bim.handler
import blenderbim.core.type
import blenderbim.core.root
import blenderbim.core.geometry
import blenderbim.tool as tool
from math import pi, degrees
from mathutils import Vector, Matrix


class MepGenerator:
    def __init__(self, relating_type):
        self.relating_type = relating_type

    def generate(self):
        self.file = tool.Ifc.get()
        self.collection = bpy.context.view_layer.active_layer_collection.collection

        if self.relating_type.is_a("IfcCableCarrierSegmentType"):
            pass
        elif self.relating_type.is_a("IfcCableSegmentType"):
            pass
        elif self.relating_type.is_a("IfcDuctSegmentType"):
            dimensions = ifcopenshell.util.element.get_psets(self.relating_type).get("Pset_DuctSegmentTypeCommon") or {}
            shape = dimensions.get("Shape") or dimensions.get("CrossSectionShape")

            if shape == "RECTANGULAR":
                self.width = dimensions.get("NominalDiameterOrWidth")
                self.height = dimensions.get("NominalHeight")
                self.length = 1
                self.rotation = 0

                return self.derive_from_cursor()
        elif self.relating_type.is_a("IfcPipeSegmentType"):
            pass

    def derive_from_cursor(self):
        self.location = bpy.context.scene.cursor.location
        return self.create_rectangle_segment()

    def create_rectangle_segment(self):
        verts = [
            Vector((0, self.width, 0)),
            Vector((0, 0, 0)),
            Vector((0, self.width, self.height)),
            Vector((0, 0, self.height)),
            Vector((self.length, self.width, 0)),
            Vector((self.length, 0, 0)),
            Vector((self.length, self.width, self.height)),
            Vector((self.length, 0, self.height)),
        ]
        faces = [
            [1, 3, 2, 0],
            [4, 6, 7, 5],
            [1, 0, 4, 5],
            [3, 7, 6, 2],
            [0, 2, 6, 4],
            [1, 5, 7, 3],
        ]
        mesh = bpy.data.meshes.new(name="Segment")
        mesh.from_pydata(verts, [], faces)

        ifc_classes = ifcopenshell.util.type.get_applicable_entities(self.relating_type.is_a(), self.file.schema)
        ifc_class = ifc_classes[0]

        obj = bpy.data.objects.new(tool.Model.generate_occurrence_name(self.relating_type, ifc_class), mesh)
        obj.location = self.location
        obj.rotation_euler[2] = self.rotation
        self.collection.objects.link(obj)

        bpy.ops.bim.assign_class(
            obj=obj.name,
            ifc_class=ifc_class,
            ifc_representation_class="IfcExtrudedAreaSolid/IfcRectangleProfileDef",
        )

        blenderbim.core.type.assign_type(tool.Ifc, tool.Type, element=tool.Ifc.get_entity(obj), type=self.relating_type)
        element = self.file.by_id(obj.BIMObjectProperties.ifc_definition_id)
        pset = ifcopenshell.api.run("pset.add_pset", self.file, product=element, name="EPset_Parametric")
        ifcopenshell.api.run("pset.edit_pset", self.file, pset=pset, properties={"Engine": "BlenderBIM.Mep"})
        obj.select_set(True)
        return obj
