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
from decimal import Context
from email.policy import default
import bpy
import ifcopenshell
import ifcsverchok.helper
import ifcopenshell.api
from ifcsverchok.ifcstore import SvIfcStore
import bonsai.tool as tool
import bonsai.core.geometry as core
from bpy.props import (
    StringProperty,
    EnumProperty,
    IntProperty,
    BoolProperty,
    PointerProperty,
)
from sverchok.node_tree import SverchCustomTreeNode
from sverchok.data_structure import updateNode, flatten_data, fixed_iter, flat_iter
from bonsai.bim.module.root.prop import get_contexts
from sverchok.data_structure import zip_long_repeat, node_id
from sverchok.core.socket_data import sv_get_socket

from itertools import chain, cycle


class SvIfcBMeshToIfcRepr(bpy.types.Node, SverchCustomTreeNode, ifcsverchok.helper.SvIfcCore):
    """
    Triggers: BMesh to Ifc Repr
    Tooltip: Blender mesh to Ifc Shape Representation
    """

    bl_idname = "SvIfcBMeshToIfcRepr"
    bl_label = "IFC Blender Mesh to IFC Repr"
    node_dict = {}

    is_scene_dependent = True  # if True and is_interactive then the node will be updated upon scene changes

    def refresh_node(self, context):
        if self.refresh_local:
            self.process()
            self.refresh_local = False

    refresh_local: BoolProperty(name="Update Node", description="Update Node", update=refresh_node)

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
    blender_objects: PointerProperty(
        name="Blender Mesh(es)",
        description="Blender Mesh Object(s)",
        update=updateNode,
        type=bpy.types.Object,
    )
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
    tooltip: StringProperty(name="Tooltip")

    def sv_init(self, context):
        self.inputs.new("SvStringsSocket", "context_type").prop_name = "context_type"
        self.inputs.new("SvStringsSocket", "context_identifier").prop_name = "context_identifier"
        self.inputs.new("SvStringsSocket", "target_view").prop_name = "target_view"
        self.inputs.new("SvObjectSocket", "blender_objects").prop_name = "blender_objects"  # no prop for now
        self.outputs.new("SvVerticesSocket", "Representations")
        self.outputs.new("SvMatrixSocket", "Locations")

    def draw_buttons(self, context, layout):
        layout.operator("node.sv_ifc_tooltip", text="", icon="QUESTION", emboss=False).tooltip = (
            "Blender mesh to Ifc Shape Representation. \nTakes one or multiple geometries.\nDeconstructs joined geometries and creates a separate representation for each."
        )

        row = layout.row(align=True)
        row.prop(self, "is_interactive", icon="SCENE_DATA", icon_only=True)
        row.prop(self, "refresh_local", icon="FILE_REFRESH")

    def process(self):
        self.sv_input_names = [i.name for i in self.inputs]

        if hash(self) not in self.node_dict:
            self.node_dict[hash(self)] = {}  # happens if node is already on canvas when blender loads
        if not self.node_dict[hash(self)]:
            self.node_dict[hash(self)].update(dict.fromkeys(self.sv_input_names, 0))

        if not self.inputs["blender_objects"].sv_get(deepcopy=True)[0]:
            return
        edit = False
        for i in range(len(self.inputs)):
            input = self.inputs[i].sv_get(deepcopy=True)
            if (
                isinstance(self.node_dict[hash(self)][self.inputs[i].name], list)
                and input != self.node_dict[hash(self)][self.inputs[i].name]
            ):
                edit = True
            self.node_dict[hash(self)][self.inputs[i].name] = input.copy()

        blender_objects = self.inputs["blender_objects"].sv_get(deepcopy=True)
        self.file = SvIfcStore.get_file()

        if self.refresh_local:
            edit = True
        if self.node_id not in SvIfcStore.id_map:
            representations, locations = self.create(blender_objects)
        else:
            if edit is True:
                self.edit()
                representations, locations = self.create(blender_objects)
            else:
                representations = SvIfcStore.id_map[self.node_id]["Representations"]
                locations = SvIfcStore.id_map[self.node_id]["Locations"]

        self.outputs["Representations"].sv_set(representations)
        self.outputs["Locations"].sv_set(locations)

    def create(self, blender_objects):
        representations_ids = []
        locations = []
        context = self.get_context()
        for blender_object in blender_objects:
            bpy.context.view_layer.objects.active = blender_object
            try:
                bpy.ops.object.mode_set(mode="OBJECT")
            except Exception as e:
                print(e)
                pass
            bpy.ops.object.select_all(action="DESELECT")
            blender_object.select_set(True)
            try:
                bpy.ops.object.mode_set(mode="EDIT")
            except Exception as e:
                print(e)
                pass
            bpy.ops.mesh.separate(
                type="LOOSE"
            )  # This isn't a great solution bc it creates new objects in the scene, thus changing the users model
            representations_ids_obj = []
            locations_obj = []
            try:
                bpy.ops.object.mode_set(mode="OBJECT")
            except Exception as e:
                print(e)
                pass
            for obj in bpy.context.selected_objects:
                if blender_object.type == "MESH":
                    representation = ifcopenshell.api.run(
                        "geometry.add_representation",
                        self.file,
                        should_run_listeners=False,
                        blender_object=obj,
                        geometry=obj.data,
                        context=context,
                    )
                    if not representation:
                        raise Exception("Couldn't create representation. Possibly wrong context.")

                    representations_ids_obj.append([representation.id()])
                    locations_obj.append([obj.matrix_world])
            representations_ids.append(representations_ids_obj)
            locations.append(locations_obj)

            SvIfcStore.id_map.setdefault(self.node_id, {}).setdefault("Representations", []).append(
                representations_ids_obj
            )
            SvIfcStore.id_map.setdefault(self.node_id, {}).setdefault("Locations", []).append(locations_obj)
        bpy.ops.object.select_all(action="DESELECT")
        return representations_ids, locations

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
        del SvIfcStore.id_map[self.node_id]["Locations"]
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
                for obj in SvIfcStore.id_map[self.node_id]["Representations"]:
                    for step_id in obj:
                        ifcopenshell.api.run(
                            "geometry.remove_representation",
                            self.file,
                            representation=self.file.by_id(step_id),
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
                        SvIfcStore.id_map[self.node_id]["Contexts"].remove(context_id)
            del SvIfcStore.id_map[self.node_id]
            del self.node_dict[hash(self)]
            # print('Node was deleted')
        except KeyError or AttributeError:
            pass


def register():
    bpy.utils.register_class(SvIfcBMeshToIfcRepr)


def unregister():
    bpy.utils.unregister_class(SvIfcBMeshToIfcRepr)
