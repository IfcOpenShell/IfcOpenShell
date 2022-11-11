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

import bpy
from mathutils import Matrix
import ifcopenshell
import ifcsverchok.helper
from ifcsverchok.ifcstore import SvIfcStore

from bpy.props import StringProperty, BoolProperty
from sverchok.node_tree import SverchCustomTreeNode
from sverchok.data_structure import (
    updateNode,
    flatten_data,
    repeat_last_for_length,
    ensure_min_nesting,
)


class SvIfcCreateEntity(
    bpy.types.Node, SverchCustomTreeNode, ifcsverchok.helper.SvIfcCore
):
    bl_idname = "SvIfcCreateEntity"
    bl_label = "IFC Create Entity"
    node_dict = {}

    is_scene_dependent = True  # if True and is_interactive then the node will be updated upon scene changes

    def refresh_node(self, context):
        if self.refresh_local:
            self.process()
            self.refresh_local = False

    refresh_local: BoolProperty(
        name="Update Node", description="Update Node", update=refresh_node
    )

    Names: StringProperty(
        name="Names",
        default="",
        description="Entity name or list of names.",
        update=updateNode,
    )
    Descriptions: StringProperty(
        name="Descriptions",
        default="",
        description="Entity description or list of descriptions.",
        update=updateNode,
    )
    IfcClass: StringProperty(name="IfcClass", update=updateNode)
    Representations: StringProperty(
        name="Representations",
        description='IfcRepresentation(s). Use eg. "IFC BMesh to IFC" or "IFC Sverchok to IFC" nodes to create representations.',
        default="",
        update=updateNode,
    )
    # Locations: FloatVectorProperty(name="Locations", default="", update=updateNode)
    Properties: StringProperty(name="properties", update=updateNode)

    def sv_init(self, context):
        self.inputs.new("SvStringsSocket", "Names").prop_name = "Names"
        self.inputs.new("SvStringsSocket", "Descriptions").prop_name = "Descriptions"
        self.inputs.new("SvStringsSocket", "IfcClass").prop_name = "IfcClass"
        self.inputs.new(
            "SvStringsSocket", "Representations"
        ).prop_name = "Representations"
        self.inputs.new("SvMatrixSocket", "Locations").is_mandatory = False
        self.inputs.new("SvStringsSocket", "Properties").prop_name = "Properties"
        self.outputs.new("SvStringsSocket", "Entities")
        self.node_dict[hash(self)] = {}

    def draw_buttons(self, context, layout):
        layout.operator(
            "node.sv_ifc_tooltip", text="", icon="QUESTION", emboss=False
        ).tooltip = "Create IFC Entity. Takes one or multiple inputs. \nIf 'Representation(s)' is given, that determines number of output entities. Otherwise, 'Names' is used."

        row = layout.row(align=True)
        row.prop(self, "is_interactive", icon="SCENE_DATA", icon_only=True)
        row.prop(self, "refresh_local", icon="FILE_REFRESH")

    def process(self):
        self.names = flatten_data(self.inputs["Names"].sv_get(), target_level=1)
        self.descriptions = flatten_data(
            self.inputs["Descriptions"].sv_get(), target_level=1
        )
        self.ifc_class = flatten_data(self.inputs["IfcClass"].sv_get(), target_level=1)[
            0
        ]
        self.representations = ensure_min_nesting(
            self.inputs["Representations"].sv_get(), 2
        )
        self.representations = flatten_data(self.representations, target_level=2)
        self.locations = ensure_min_nesting(
            self.inputs["Locations"].sv_get(default=[]), 2
        )
        self.properties = self.inputs["Properties"].sv_get()

        self.sv_input_names = [i.name for i in self.inputs]

        if hash(self) not in self.node_dict:
            self.node_dict[
                hash(self)
            ] = {}  # happens if node is already on canvas when blender loads
        if not self.node_dict[hash(self)]:
            self.node_dict[hash(self)].update(dict.fromkeys(self.sv_input_names, 0))
        if not self.inputs["IfcClass"].sv_get()[0][0]:
            raise Exception('Mandatory input "IfcClass" is missing.')

        edit = False
        for i in range(len(self.inputs)):
            input = self.inputs[self.sv_input_names[i]].sv_get(
                deepcopy=True, default=[]
            )
            if (
                isinstance(self.node_dict[hash(self)][self.inputs[i].name], list)
                and input != self.node_dict[hash(self)][self.inputs[i].name]
            ):
                edit = True
            self.node_dict[hash(self)][self.inputs[i].name] = input.copy()

        if self.refresh_local:
            edit = True

        self.file = SvIfcStore.get_file()
        if self.representations[0][0]:
            try:
                # self.representations = [self.file.by_id(step_id) for step_id in self.representations]
                self.representations = [
                    [self.file.by_id(step_id) for step_id in representation]
                    for representation in self.representations
                ]
            except Exception as e:
                raise
            self.names = self.repeat_input_unique(self.names, len(self.representations))
            self.descriptions = self.repeat_input_unique(
                self.descriptions, len(self.representations)
            )
        elif not self.representations[0][0]:
            self.descriptions = self.repeat_input_unique(
                self.descriptions, len(self.names)
            )

        if self.node_id not in SvIfcStore.id_map:
            entities = self.create()
        else:
            if edit is True:
                entities = self.edit()
            else:
                entities = SvIfcStore.id_map[self.node_id]

        # print("Entities: ", entities)
        self.outputs["Entities"].sv_set(entities)

    def create(self, index=None):
        entities_ids = []
        iterator = range(len(self.names))
        if index is not None:
            iterator = [index]
        for i in iterator:
            try:
                entity = ifcopenshell.api.run(
                    "root.create_entity",
                    self.file,
                    ifc_class=self.ifc_class,
                    name=self.names[i],
                    description=self.descriptions[i],
                )
                print("Entity: ", entity)
                try:
                    print("Representations: ", self.representations[i])
                    for repr in self.representations[i]:
                        print("Representation: ", repr)
                        if repr:
                            ifcopenshell.api.run(
                                "geometry.assign_representation",
                                self.file,
                                product=entity,
                                representation=repr,
                            )
                except IndexError:
                    pass
                try:
                    for loc in self.locations[i]:
                        print("Location: ", loc)
                        if isinstance(loc, Matrix):
                            ifcopenshell.api.run(
                                "geometry.edit_object_placement",
                                self.file,
                                product=entity,
                                matrix=loc,
                            )
                except IndexError:
                    pass
                entities_ids.append(entity.id())
                SvIfcStore.id_map.setdefault(self.node_id, []).append(entity.id())
            except Exception as e:
                raise Exception("Something went wrong. Cannot create entity.", e)
        return entities_ids

    def edit(self):
        entities_ids = []
        id_map_copy = SvIfcStore.id_map[self.node_id].copy()
        for i, _ in enumerate(self.names):
            try:
                step_id = id_map_copy[i]
            except IndexError:
                id = self.create(index=i)
                entities_ids.append(id[0])
                continue
            entity = self.file.by_id(step_id)
            entity.Name = self.names[i]
            entity.Description = self.descriptions[i]

            try:
                for repr in self.representations[i]:
                    if repr and repr.is_a("IfcProductDefinitionShape"):
                        entity.Representation = repr
                    elif repr:
                        ifcopenshell.api.run(
                            "geometry.assign_representation",
                            self.file,
                            product=entity,
                            representation=repr,
                        )
            except IndexError:
                pass
            try:
                for loc in self.locations[i]:
                    if isinstance(loc, Matrix):
                        ifcopenshell.api.run(
                            "geometry.edit_object_placement",
                            self.file,
                            product=entity,
                            matrix=loc,
                        )
            except IndexError:
                pass
            if entity.is_a() != self.ifc_class:
                SvIfcStore.id_map[self.node_id].remove(step_id)
                entity = ifcopenshell.util.schema.reassign_class(
                    self.file, entity, self.ifc_class
                )
                SvIfcStore.id_map.setdefault(self.node_id, []).append(entity.id())
            entities_ids.append(entity.id())

        if id_map_copy > entities_ids:
            SvIfcStore.id_map[self.node_id] = entities_ids
        return entities_ids

    def repeat_input_unique(self, input, count):
        input = repeat_last_for_length(input, count, deepcopy=False)
        if input[0]:
            input = [
                a if not (s := sum(j == a for j in input[:i])) else f"{a}-{s+1}"
                for i, a in enumerate(input)
            ]  # add number to duplicates
        return input

    def sv_free(self):
        try:
            del SvIfcStore.id_map[self.node_id]
            del self.node_dict[hash(self)]
            # print('Node was deleted')
        except KeyError or AttributeError:
            pass


def register():
    bpy.utils.register_class(SvIfcCreateEntity)


def unregister():
    bpy.utils.unregister_class(SvIfcCreateEntity)
