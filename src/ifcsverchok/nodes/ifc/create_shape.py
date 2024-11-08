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
import logging
import ifcopenshell
import ifcsverchok.helper
from ifcsverchok.ifcstore import SvIfcStore
import bonsai.bim.import_ifc
from bpy.props import StringProperty, PointerProperty, BoolProperty
from sverchok.node_tree import SverchCustomTreeNode
from sverchok.data_structure import updateNode, flatten_data


class SvIfcCreateShape(bpy.types.Node, SverchCustomTreeNode, ifcsverchok.helper.SvIfcCore):
    """
    Triggers: Ifc create shape by entity
    Tooltip: Create Blender shape by Ifc Entity
    """

    is_scene_dependent = True
    is_interactive = False
    node_dict = {}

    def refresh_node(self, context):
        if self.refresh_local:
            self.process()
            self.refresh_local = False

    refresh_local: BoolProperty(name="Create shape(s)", description="Update Node", update=refresh_node)

    bl_idname = "SvIfcCreateShape"
    bl_label = "IFC Create Blender Shape"
    entity: StringProperty(name="Entity Id(s)", update=updateNode)

    def sv_init(self, context):
        self.inputs.new("SvStringsSocket", "Entities").prop_name = "entity"
        self.outputs.new("SvStringsSocket", "Object(s)")

    def draw_buttons(self, context, layout):
        row = layout.row(align=True)
        row.operator("node.sv_ifc_tooltip", text="", icon="QUESTION", emboss=False).tooltip = (
            "Create Blender shape from IfcEntity Id. Takes one or multiple IfcEntity IDs."
        )
        row.prop(self, "refresh_local", icon="FILE_REFRESH")

    def process(self):
        self.entities = flatten_data(self.inputs["Entities"].sv_get(), target_level=1)
        if not self.entities[0]:
            return

        if self.refresh_local or hash(self) not in self.node_dict:
            self.file = SvIfcStore.get_file()
            try:
                self.entities = [self.file.by_id(step_id) for step_id in self.entities]
            except Exception as e:
                raise
            blender_objects = self.create()
            self.node_dict[hash(self)] = blender_objects
        else:
            blender_objects = self.node_dict[hash(self)]

        self.outputs["Object(s)"].sv_set(blender_objects)

    def create(self):
        blender_objects = []
        for entity in self.entities:
            try:
                if not entity.is_a("IfcProduct"):
                    return
                logger = logging.getLogger("ImportIFC")
                self.ifc_import_settings = bonsai.bim.import_ifc.IfcImportSettings.factory(bpy.context, "", logger)
                settings = ifcopenshell.geom.settings()
                shape = ifcopenshell.geom.create_shape(settings, entity)
                ifc_importer = bonsai.bim.import_ifc.IfcImporter(self.ifc_import_settings)
                ifc_importer.file = self.file
                mesh = ifc_importer.create_mesh(entity, shape)
                obj = bpy.data.objects.new("IFC Element", mesh)
                blender_objects.append(obj)
                bpy.context.scene.collection.objects.link(obj)
            except:
                raise Exception("Entity could not be converted into a shape. Entity: {}".format(entity))
        return blender_objects


def register():
    # bpy.utils.register_class(SvIfcCreateShapeRefresh)
    bpy.utils.register_class(SvIfcCreateShape)


def unregister():
    bpy.utils.unregister_class(SvIfcCreateShape)
    # bpy.utils.unregister_class(SvIfcCreateShapeRefresh)
