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

    def generate(self, link_to_scene=True):
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

                return self.derive_from_cursor(link_to_scene=link_to_scene)
        elif self.relating_type.is_a("IfcPipeSegmentType"):
            pass

    def derive_from_cursor(self, link_to_scene):
        self.location = bpy.context.scene.cursor.location
        return self.create_rectangle_segment(link_to_scene)

    def create_rectangle_segment(self, link_to_scene):
        verts = [
            Vector((-self.width / 2, self.height / 2, 0)),
            Vector((-self.width / 2, -self.height / 2, 0)),
            Vector((-self.width / 2, self.height / 2, self.length)),
            Vector((-self.width / 2, -self.height / 2, self.length)),
            Vector((self.width / 2, self.height / 2, 0)),
            Vector((self.width / 2, -self.height / 2, 0)),
            Vector((self.width / 2, self.height / 2, self.length)),
            Vector((self.width / 2, -self.height / 2, self.length)),
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
        if link_to_scene:
            obj.location = self.location
            obj.rotation_euler[0] = math.pi / 2
            obj.rotation_euler[2] = math.pi / 2
            self.collection.objects.link(obj)

        bpy.ops.bim.assign_class(
            obj=obj.name,
            ifc_class=ifc_class,
            ifc_representation_class="IfcExtrudedAreaSolid/IfcRectangleProfileDef",
        )

        element = tool.Ifc.get_entity(obj)

        blenderbim.core.type.assign_type(tool.Ifc, tool.Type, element=element, type=self.relating_type)
        pset = ifcopenshell.api.run("pset.add_pset", self.file, product=element, name="EPset_Parametric")
        ifcopenshell.api.run("pset.edit_pset", self.file, pset=pset, properties={"Engine": "BlenderBIM.Mep"})

        start_port_matrix = Matrix()
        end_port_matrix = Matrix.Translation((0, 0, self.length))

        for mat in [start_port_matrix, end_port_matrix]:
            port = tool.Ifc.run("root.create_entity", ifc_class="IfcDistributionPort")
            tool.Ifc.run("system.assign_port", element=element, port=port)
            tool.Ifc.run("geometry.edit_object_placement", product=port, matrix=obj.matrix_world @ mat, is_si=True)

        try:
            obj.select_set(True)
        except RuntimeError:
            def msg(self, context):
                txt = "The created object could not be assigned to a collection. "
                txt += "Has any IfcSpatialElement been deleted?"
                self.layout.label(text=txt)

            bpy.context.window_manager.popup_menu(msg, title="Error", icon="ERROR")
        return obj
