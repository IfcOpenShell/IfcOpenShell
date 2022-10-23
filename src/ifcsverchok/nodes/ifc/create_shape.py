
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
import logging
import ifcopenshell
import ifcsverchok.helper
from ifcsverchok.ifcstore import SvIfcStore
import blenderbim.bim.import_ifc
from bpy.props import StringProperty, PointerProperty, BoolProperty
from sverchok.node_tree import SverchCustomTreeNode
from sverchok.data_structure import updateNode, flatten_data


# class SvIfcCreateShapeRefresh(bpy.types.Operator):
#     bl_idname = "node.sv_ifc_create_shape_refresh"
#     bl_label = "IFC Create Shape Refresh"
#     bl_options = {"UNDO"}


#     tree_name: StringProperty(default="")
#     node_name: StringProperty(default="")

#     def execute(self, context):
#         node = bpy.data.node_groups[self.tree_name].nodes[self.node_name]
#         node.process()
#         return {"FINISHED"}


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

    refresh_local: BoolProperty(name="Update Node", description="Update Node", update=refresh_node)

    bl_idname = "SvIfcCreateShape"
    bl_label = "IFC Create Blender Shape"
    entity: StringProperty(name="Entities", update=updateNode)
    

    def sv_init(self, context):
        self.inputs.new("SvStringsSocket", "Entities").prop_name = "entity"
        self.outputs.new('SvStringsSocket', "Object(s)")

    def draw_buttons(self, context, layout):
        # self.wrapper_tracked_ui_draw_op(layout, "node.sv_ifc_create_shape_refresh", icon="FILE_REFRESH", text="Refresh")
        row = layout.row(align=True)
        row.operator("node.sv_ifc_tooltip", text="", icon="QUESTION", emboss=False).tooltip = "Create Blender shape from Ifc Entity. Takes one or multiple Ifc Entities."
        # row.prop(self, 'is_interactive', icon='SCENE_DATA', icon_only=True)
        row.prop(self, 'refresh_local', icon='FILE_REFRESH')

    def process(self):
        print("#"*20, "\n running create_entity3 PROCESS()... \n", "#"*20,)
        print("#"*20, "\n hash(self):", hash(self), "\n", "#"*20,)
        print("node_dict: ", self.node_dict)
        self.entities = flatten_data(self.inputs["Entities"].sv_get(), target_level = 1)
        if not self.entities[0]:
            return
        
        if self.refresh_local or hash(self) not in self.node_dict:
            print("grr")
            self.file = SvIfcStore.get_file()
            blender_objects = self.create()
            self.node_dict[hash(self)] = blender_objects
            print("blender_objects: ", blender_objects)
        else:
            blender_objects = self.node_dict[hash(self)]
        
        self.outputs["Object(s)"].sv_set(blender_objects)

    def create(self):
        blender_objects = []
        for entity in self.entities:
            print("entity: ", entity)
            try:
                if not entity.is_a("IfcProduct"):
                    return
                logger = logging.getLogger("ImportIFC")
                self.ifc_import_settings = blenderbim.bim.import_ifc.IfcImportSettings.factory(bpy.context, "", logger)
                settings = ifcopenshell.geom.settings()
                shape = ifcopenshell.geom.create_shape(settings, entity)
                ifc_importer = blenderbim.bim.import_ifc.IfcImporter(self.ifc_import_settings)
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
