# IfcSverchok - IFC Sverchok extension
# Copyright (C) 2022 Martina Jakubowska <martina@jakubowska.dk>
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

from copy import deepcopy
import bpy
import ifcopenshell
import ifcsverchok.helper
import ifcopenshell.api
import ifcopenshell.util.representation
from ifcsverchok.ifcstore import SvIfcStore
import bonsai.tool as tool
import bonsai.core.geometry as core
from bpy.props import StringProperty, EnumProperty, IntProperty, FloatVectorProperty
from sverchok.node_tree import SverchCustomTreeNode
from sverchok.data_structure import updateNode, ensure_min_nesting


class SvIfcSverchokToIfcRepr(bpy.types.Node, SverchCustomTreeNode, ifcsverchok.helper.SvIfcCore):
    """
    Triggers: Sv to Ifc Repr
    Tooltip: Sverchok geometry to Ifc Shape Representation
    """

    bl_idname = "SvIfcSverchokToIfcRepr"
    bl_label = "IFC Sverchok to IFC Repr"
    node_dict = {}

    n_id: StringProperty()
    context_types = [
        ("Model", "Model", "Context type: Model", 0),
        ("Plan", "Plan", "Context type: Plan", 1),
    ]

    context_identifiers = [
        ("Body", "Body", "Context identifier: Body", 0),
        ("Annotation", "Annotation", "Context identifier: Annotation", 1),
        ("Box", "Box", "Context identifier: Box", 2),
        ("Axis", "Axis", "Context identifier: Axis", 3),
    ]
    target_views = [
        ("MODEL_VIEW", "MODEL_VIEW", "Target View: MODEL_VIEW", 0),
        ("PLAN_VIEW", "PLAN_VIEW", "Target View: PLAN_VIEW", 1),
        ("GRAPH_VIEW", "GRAPH_VIEW", "Target View: GRAPH_VIEW", 2),
        ("SKETCH_VIEW", "SKETCH_VIEW", "Target View: SKETCH_VIEW", 3),
    ]

    context_type: EnumProperty(
        name="Context Type",
        description="Default: Model",
        default="Model",
        items=context_types,
        update=updateNode,
    )
    context_identifier: EnumProperty(
        name="Context Identifier",
        description="Default: Body",
        default="Body",
        items=context_identifiers,
        update=updateNode,
    )
    target_view: EnumProperty(
        name="Target View",
        description="Default: MODEL VIEW",
        default="MODEL_VIEW",
        items=target_views,
        update=updateNode,
    )

    def sv_init(self, context):
        self.inputs.new("SvStringsSocket", "context_type").prop_name = "context_type"
        self.inputs.new("SvStringsSocket", "context_identifier").prop_name = "context_identifier"
        self.inputs.new("SvStringsSocket", "target_view").prop_name = "target_view"
        self.inputs.new("SvVerticesSocket", "Vertices")
        self.inputs.new("SvStringsSocket", "Edges")
        self.inputs.new("SvStringsSocket", "Faces")
        self.outputs.new("SvVerticesSocket", "Representation(s)")
        self.width = 210
        self.node_dict[hash(self)] = {}

    def draw_buttons(self, context, layout):
        op = layout.operator("node.sv_ifc_tooltip", text="", icon="QUESTION", emboss=False).tooltip = (
            "Sverchok geometry to Ifc Shape Representation. \nTakes one or multiple geometries."
        )

    def process(self):
        if not any(socket.is_linked for socket in self.inputs):
            return
        self.file = SvIfcStore.get_file()
        self.sv_input_names = [i.name for i in self.inputs]

        if hash(self) not in self.node_dict:
            self.node_dict[hash(self)] = {}  # happens if node is already on canvas when blender loads
        if not self.node_dict[hash(self)]:
            self.node_dict[hash(self)].update(dict.fromkeys(self.sv_input_names, 0))

        edit = False
        for i in range(len(self.inputs)):
            input = self.inputs[i].sv_get(deepcopy=False)
            if (
                isinstance(self.node_dict[hash(self)][self.inputs[i].name], list)
                and input != self.node_dict[hash(self)][self.inputs[i].name]
            ):
                edit = True
            self.node_dict[hash(self)][self.inputs[i].name] = input

        self.vertices = ensure_min_nesting(self.inputs["Vertices"].sv_get(deepcopy=False), 4)
        self.edges = ensure_min_nesting(self.inputs["Edges"].sv_get(deepcopy=False), 4)
        self.faces = ensure_min_nesting(self.inputs["Faces"].sv_get(deepcopy=False), 4)
        data = list(zip(self.vertices, self.edges, self.faces))
        objects = []
        for object in data:
            objects.append(list(zip(object[0], object[1], object[2])))

        if self.node_id not in SvIfcStore.id_map:
            representations = self.create(objects)
        else:
            if edit is True:
                self.edit()
                representations = self.create(objects)
            else:
                representations = SvIfcStore.id_map[self.node_id]["Representations"]
        self.outputs["Representation(s)"].sv_set(representations)

    def create(self, geo_data):
        representations_ids = []
        self.context = self.get_context()
        for obj in geo_data:
            representations_ids_obj = []
            for item in obj:
                representation = ifcopenshell.api.run(
                    "geometry.add_mesh_representation",
                    self.file,
                    should_run_listeners=False,
                    context=self.context,
                    vertices=[list(map(tuple, item[0]))],
                    edges=[list(map(tuple, item[1]))],
                    faces=[list(map(tuple, item[2]))],
                )
                if not representation:
                    raise Exception("Couldn't create representation. Possibly wrong context.")
                representations_ids_obj.append([representation.id()])
            representations_ids.append(representations_ids_obj)
            SvIfcStore.id_map.setdefault(self.node_id, {}).setdefault("Representations", []).append(
                representations_ids_obj
            )
        return representations_ids

    def edit(self):
        if "Representations" not in SvIfcStore.id_map[self.node_id]:
            return
        for obj in SvIfcStore.id_map[self.node_id]["Representations"]:
            for step_id in obj:
                ifcopenshell.api.run(
                    "geometry.remove_representation",
                    self.file,
                    representation=self.file.by_id(step_id[0]),
                )
        del SvIfcStore.id_map[self.node_id]["Representations"]
        return

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
                parent=parent,
            )
            SvIfcStore.id_map.setdefault(self.node_id, {}).setdefault("Contexts", []).append(context.id())
        return context

    def sv_free(self):
        try:
            self.file = SvIfcStore.get_file()
            if "Representations" in SvIfcStore.id_map[self.node_id]:
                for step_id in SvIfcStore.id_map[self.node_id]["Representations"]:
                    ifcopenshell.api.run(
                        "geometry.remove_representation",
                        self.file,
                        representation=self.file.by_id(step_id[0]),
                    )

            if "Contexts" in SvIfcStore.id_map[self.node_id]:
                for context_id in SvIfcStore.id_map[self.node_id]["Contexts"]:
                    context = self.file.by_id(context_id)
                    if not self.file.get_inverse(context):
                        if self.file.by_id(context_id).ParentContext:
                            parent = self.file.by_id(context_id).ParentContext
                        ifcopenshell.api.run("context.remove_context", self.file, context=context)
                        if parent:
                            if not self.file.get_inverse(parent):
                                ifcopenshell.api.run("context.remove_context", self.file, context=parent)
                        # print("Removed context with step ID: ", context_id)
                        SvIfcStore.id_map[self.node_id]["Contexts"].remove(context_id)
            del SvIfcStore.id_map[self.node_id]
            del self.node_dict[hash(self)]
            # print('Node was deleted')
        except KeyError or AttributeError:
            pass


def register():
    bpy.utils.register_class(SvIfcSverchokToIfcRepr)


def unregister():
    bpy.utils.unregister_class(SvIfcSverchokToIfcRepr)
