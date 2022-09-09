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
from ifcsverchok.ifcstore import SvIfcStore
import blenderbim.tool as tool
import blenderbim.core.geometry as core
from bpy.props import StringProperty, EnumProperty
from sverchok.node_tree import SverchCustomTreeNode
from sverchok.data_structure import updateNode
from blenderbim.bim.module.root.prop import get_contexts


class SvIfcBMeshToIfcRepr(bpy.types.Node, SverchCustomTreeNode, ifcsverchok.helper.SvIfcCore):
    """
    Triggers: BMesh to Ifc Repr
    Tooltip: Blender mesh to Ifc Shape Representation
    """
    bl_idname = "SvIfcBMeshToIfcRepr"
    bl_label = "IFC Blender Mesh to IFC Repr"
    blender_objects: StringProperty(name="Blender Mesh(es)", description="Blender Mesh Object(s)", update=updateNode)
    ifc_representation_class: StringProperty(name="Ifc Representation Class", description="Whether to cast a mesh into a particular class", update=updateNode)
    
    context_types = [
        ('Model', 'Model', 'Context type: Model', 0),
        ('Plan', 'Plan', 'Context type: Plan', 1),
    ]

    context_identifiers = [
        ('Body', 'Body', 'Context identifier: Body', 0),
        ('Annotation', 'Annotation', 'Context identifier: Annotation', 1),
        ('Box', 'Box', 'Context identifier: Box', 2),
        ('Axis', 'Axis', 'Context identifier: Axis', 3),
    ]
    target_views = [
        ('MODEL_VIEW', 'MODEL_VIEW', 'Target View: MODEL_VIEW', 0),
        ('PLAN_VIEW', 'PLAN_VIEW', 'Target View: PLAN_VIEW', 1),
        ('GRAPH_VIEW', 'GRAPH_VIEW', 'Target View: GRAPH_VIEW', 2),
        ('SKETCH_VIEW', 'SKETCH_VIEW', 'Target View: SKETCH_VIEW', 3),
    ]
    paradigms = [
        ('Tessellation', 'Tessellation', 'Geometry paradigm: Tessellation', 0),
        ('Extrusion', 'Extrusion', 'Geometry paradigm: Extrusion', 1),
    ]
    
    context_type: EnumProperty(name="Context Type", description="Default: Model", default="Model",items=context_types,update=updateNode)
    context_identifier: EnumProperty(name="Context Identifier", description="Default: Body", default="Body", items=context_identifiers, update=updateNode)
    target_view: EnumProperty(name="Target View", description="Default: MODEL VIEW", default="MODEL_VIEW",items=target_views, update=updateNode)
    paradigm: EnumProperty(name="Paradigm", description="Which geometry type to convert to. Choose between tessellation or extrusion. Default: Tessellation.",default="Tessellation",items=paradigms, update=updateNode)
    tooltip: StringProperty(name="Tooltip")
    context_id: bpy.props.IntProperty()

    def sv_init(self, context):
        self.inputs.new("SvObjectSocket", "blender_objects") #no prop for now
        self.inputs.new("SvStringsSocket", "ifc_representation_class").prop_name = "ifc_representation_class"
        self.inputs.new("SvStringsSocket", "context_type").prop_name = "context_type"
        self.inputs.new("SvStringsSocket", "context_identifier").prop_name = "context_identifier"
        self.inputs.new("SvStringsSocket", "target_view").prop_name = "target_view"
        self.inputs.new("SvStringsSocket", "paradigm").prop_name = "paradigm"
        self.outputs.new("SvVerticesSocket", "file")
        self.outputs.new("SvVerticesSocket", "Representation")
    
    def draw_buttons(self, context, layout):
        op = layout.operator("node.sv_ifc_tooltip", text="", icon="QUESTION", emboss=False).tooltip = "Blender mesh to Ifc Shape Representation"
        # layout.prop(self, 'context_type', text='')
        # layout.prop(self, 'context_identifier', text='')
        # layout.prop(self, 'target_view', text='')
        # layout.prop(self, 'paradigm', text='')
        #op.tooltip = self.tooltip

    def process(self):
        # if not self.inputs['blender_objects'].is_linked:
        #     return

        self.file = SvIfcStore.get_file()
        

        self.sv_input_names = [i.name for i in self.inputs]
        for i in range(0, len(self.inputs)):
            print("self.sv_input_names[i]: ", self.sv_input_names[i])
            print("self.inputs[i].sv_get(): ", self.inputs[i].sv_get())
            if self.sv_input_names[i] != "blender_objects":
                setattr(self, self.sv_input_names[i], self.inputs[i].sv_get()) #doesn't work for lists?

        self.blender_objects = self.inputs["blender_object"].sv_get()
        self.create_context()

        if self.node_id not in SvIfcStore.id_map.values():
            for blender_object in self.blender_objects:
                geometry = blender_object.data
                self.process_ifc(self.file, blender_object, geometry)
        else:
            #TODO: edit existing representation
            raise Exception("Editing not yet implemented")


        SvIfcStore.file = self.file
        try:
            self.outputs["file"].sv_set([[self.file]]) #only for testing
            self.outputs["Representation"].sv_set([self.representation])
        except:
            raise Exception(
                "Couldn't write to file. Representation: {}".format(
                    self.representation
                )
            )

    def process_ifc(self, blender_object, geometry):
        try:
            self.representation = [ifcopenshell.api.run("geometry.add_representation", self.file, should_run_listeners=False,blender_object = blender_object, geometry=geometry, context = self.context)]
        except:
            raise Exception("Couldn't create representation. Representation: {}".format(
                    self.representation
                ))
        SvIfcStore.id_map[self.representation.id()] = self.node_id

    def create_context(self):
        if self.file.by_type("IFCGEOMETRICREPRESENTATIONCONTEXT", include_subtypes=True):
            for context in self.file.by_type("IFCGEOMETRICREPRESENTATIONCONTEXT", include_subtypes=True):
                if context.get_info()["ContextType"] == "Model" and context.get_info()["ContextIdentifier"] == "Body":
                    self.context = context
                elif context.get_info()["ContextType"] == "Model":
                    self.context= context
        else:
            model = ifcopenshell.api.run("context.add_context", self.file, context_type=self.context_type)
            self.context = ifcopenshell.api.run(
                    "context.add_context",
                    self.file,
                    context_type=self.context_type,
                    context_identifier=self.context_identifier,
                    target_view=self.target_view,
                    parent=model,
                )
        SvIfcStore.id_map[self.context.id()] = self.node_id
    
    def sv_free(self):
        try:
            SvIfcStore.id_map.pop(self.representation.id())
            SvIfcStore.id_map.pop(self.context.id())
        except KeyError or AttributeError:
            pass

def register():
    bpy.utils.register_class(SvIfcBMeshToIfcRepr)


def unregister():
    bpy.utils.unregister_class(SvIfcBMeshToIfcRepr)
