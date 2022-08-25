# IfcSverchok - IFC Sverchok extension
# Copyright (C) 2020, 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of IfcSverchok.
#
# IfcSverchok is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# IfcSverchok is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with IfcSverchok.  If not, see <http://www.gnu.org/licenses/>.

import bpy
import ifcopenshell
import ifcsverchok.helper
import ifcopenshell.api
import blenderbim.tool as tool
import blenderbim.core.geometry as core
from bpy.props import StringProperty
from sverchok.node_tree import SverchCustomTreeNode
from sverchok.data_structure import updateNode
from blenderbim.bim.module.root.prop import get_contexts


class SvIfcBMeshToIfcGeo(bpy.types.Node, SverchCustomTreeNode, ifcsverchok.helper.SvIfcCore):
    """
    Triggers: BMesh to Ifc Geo
    Tooltip: Blender mesh to Ifc Geometric Representation
    """
    bl_idname = "SvIfcBMeshToIfcGeo"
    bl_label = "IFC Blender Mesh to IFC Geo"
    tooltip: StringProperty(name="Tooltip")
    context_id: bpy.props.IntProperty()

    def sv_init(self, context):
        input_socket = self.inputs.new("SvStringsSocket", "file")
        input_socket.tooltip = "ifc file to add the geometry to"
        input_socket = self.inputs.new("SvObjectSocket", "blender_object")
        input_socket.tooltip = "Pick or pass Blender Mesh object"
        input_socket = self.inputs.new("SvStringsSocket", "ifc_representation_class")
        input_socket.tooltip = "Whether to cast a mesh into a particular class"
        self.outputs.new("SvVerticesSocket", "file")
        self.outputs.new("SvVerticesSocket", "representation")
    
    def draw_buttons(self, context, layout):
        op = layout.operator("node.sv_ifc_tooltip", text="", icon="QUESTION", emboss=False).tooltip = "Description?"
        #op.tooltip = self.tooltip

    def process(self):
        print("Running process...")

        # file
        file = self.inputs["file"].sv_get()[0][0]

        # blender mesh
        blender_object = self.inputs["blender_object"].sv_get()[0]
        print("blender object: ", blender_object)

        #geometry
        geometry = blender_object.data
        print("geometry: ", geometry)

        #run process_ifc
        self.process_ifc(file, blender_object, geometry)

    def process_ifc(self, file, blender_object, geometry):
        #get context
        try:
            for context in file.by_type("IFCGEOMETRICREPRESENTATIONCONTEXT", include_subtypes=True):
                if context.get_info()["ContextType"] == "Model" and context.get_info()["ContextIdentifier"] == "Body":
                    repr_context= context
                    print("pop", context)
                elif context.get_info()["ContextType"] == "Model":
                    repr_context= context
        except:
            raise Exception(
                "Ifc Geometric Representation Context is missing."
            )
        
        representation = [ifcopenshell.api.run("geometry.add_representation", file, should_run_listeners=False,blender_object = blender_object, geometry=geometry, context = repr_context)]
        print("representation: ", representation)
        try:
            self.outputs["file"].sv_set([[file]])
            self.outputs["representation"].sv_set([representation])
        except:
            raise Exception(
                "Couldn't write to file. Representation: {}".format(
                    representation
                )
            )


def register():
    bpy.utils.register_class(SvIfcBMeshToIfcGeo)


def unregister():
    bpy.utils.unregister_class(SvIfcBMeshToIfcGeo)
