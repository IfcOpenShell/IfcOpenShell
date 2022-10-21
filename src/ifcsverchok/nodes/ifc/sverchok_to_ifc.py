# IfcSverchok - IFC Sverchok extension
# Copyright (C) 2022 Dion Moult <dion@thinkmoult.com>
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
from bpy.props import StringProperty, EnumProperty, IntProperty
from sverchok.node_tree import SverchCustomTreeNode
from sverchok.data_structure import updateNode
 
 
class SvIfcSverchokToIfc(bpy.types.Node, SverchCustomTreeNode, ifcsverchok.helper.SvIfcCore):
    bl_idname = "SvIfcSverchokToIfc"
    bl_label = "IFC Sverchok to IFC"
 
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
 
    context_type: EnumProperty(name="Context Type", description="Default: Model", default="Model",items=context_types,update=updateNode)
    context_identifier: EnumProperty(name="Context Identifier", description="Default: Body", default="Body", items=context_identifiers, update=updateNode)
    target_view: EnumProperty(name="Target View", description="Default: MODEL VIEW", default="MODEL_VIEW",items=target_views, update=updateNode)
 
    def sv_init(self, context):
        self.inputs.new("SvVerticesSocket", "Vertices")
        self.inputs.new("SvStringsSocket", "Edges")
        self.inputs.new("SvStringsSocket", "Faces")
        self.inputs.new("SvStringsSocket", "context_type").prop_name = "context_type"
        self.inputs.new("SvStringsSocket", "context_identifier").prop_name = "context_identifier"
        self.inputs.new("SvStringsSocket", "target_view").prop_name = "target_view"
 
        self.outputs.new("SvVerticesSocket", "Representation")
        self.outputs.new("SvVerticesSocket", "File")
 
    def draw_buttons(self, context, layout):
        op = layout.operator(
            "node.sv_ifc_tooltip", text="", icon="QUESTION", emboss=False
        ).tooltip = "Blender mesh to Ifc Shape Representation"
 
    def process(self):
        self.file = SvIfcStore.get_file()
 
        self.sv_input_names = [i.name for i in self.inputs]
 
        if self.node_id in SvIfcStore.id_map:
            for step_id in SvIfcStore.id_map[self.node_id]:
                ifcopenshell.api.run(
                    "geometry.remove_representation", self.file, representation=self.file.by_id(step_id)
                )
            del SvIfcStore.id_map[self.node_id]
 
        results = []
 
        representation = ifcopenshell.api.run(
            "geometry.add_sverchok_representation",
            self.file,
            should_run_listeners=False,
            context=self.get_context(),
            vertices=self.inputs["Vertices"].sv_get(),
            faces=self.inputs["Faces"].sv_get(),
        )
        results.append(representation)
        SvIfcStore.id_map.setdefault(self.node_id, []).append(representation.id())
 
        SvIfcStore.file = self.file
 
        self.outputs["File"].sv_set([[self.file]])  # only for testing
        self.outputs["Representation"].sv_set([results])
 
    def get_context(self):
        context = ifcopenshell.util.representation.get_context(
            self.file, self.context_type, self.context_identifier, self.target_view
        )
        if not context:
            parent = ifcopenshell.util.representation.get_context(self.file, self.context_type)
            if not parent:
                parent = ifcopenshell.api.run("context.add_context", self.file, context_type=self.context_type)
            context = ifcopenshell.api.run(
                "context.add_context",
                self.file,
                context_type=self.context_type,
                context_identifier=self.context_identifier,
                target_view=self.target_view,
                parent=model,
            )
        return context
 
    def sv_free(self):
        print("it was deleted")
        try:
            pass
            # SvIfcStore.id_map.pop(self.representation.id())
            # SvIfcStore.id_map.pop(self.context.id())
        except KeyError or AttributeError:
            pass
 
 
def register():
    bpy.utils.register_class(SvIfcSverchokToIfc)
 
 
def unregister():
    bpy.utils.unregister_class(SvIfcSverchokToIfc)