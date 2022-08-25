
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
import blenderbim.bim.import_ifc
from bpy.props import StringProperty
from sverchok.node_tree import SverchCustomTreeNode
from sverchok.data_structure import updateNode

from sverchok.data_structure import zip_long_repeat


class SvIfcCreateShapeRefresh(bpy.types.Operator):
    bl_idname = "node.sv_ifc_create_shape_refresh"
    bl_label = "IFC Create Shape Refresh"
    bl_options = {"UNDO"}

    tree_name: StringProperty(default="")
    node_name: StringProperty(default="")

    def execute(self, context):
        node = bpy.data.node_groups[self.tree_name].nodes[self.node_name]
        node.process()
        return {"FINISHED"}


class SvIfcCreateShape(bpy.types.Node, SverchCustomTreeNode, ifcsverchok.helper.SvIfcCore):
    bl_idname = "SvIfcCreateShape"
    bl_label = "IFC Create Shape"
    file: StringProperty(name="file", update=updateNode)
    entity: StringProperty(name="entity", update=updateNode)

    def sv_init(self, context):
        self.inputs.new("SvStringsSocket", "file").prop_name = "file"
        self.inputs.new("SvStringsSocket", "entity").prop_name = "entity"

    def draw_buttons(self, context, layout):
        self.wrapper_tracked_ui_draw_op(layout, "node.sv_ifc_create_shape_refresh", icon="FILE_REFRESH", text="Refresh")

    def process(self):
        self.sv_input_names = ["file", "entity"]
        super().process()
    
    def process_helper(self):
        print("Hello from helper")
        sv_inputs_nested = []
        for name in self.sv_input_names:
            sv_inputs_nested.append(self.inputs[name].sv_get())
            print(24*"#","\n", "sv_input: ", self.inputs[name].sv_get(), "input type: ", type(self.inputs[name].sv_get()), "\n", "#"*24)
        for sv_input_nested in zip_long_repeat(*sv_inputs_nested):
            for sv_input in zip_long_repeat(*sv_input_nested):
                sv_input = list(sv_input)
                print(24*"#","\n", "sv_input post zip_long_repeat: ", sv_input, "input type: ", type(sv_input), "\n", "#"*24)
                self.process_ifc(*sv_input)

    def process_ifc(self, file, entity):
        print("process ifc...")
        print("entity: ", entity)
        try:
            if not entity.is_a("IfcProduct"):
                return
            logger = logging.getLogger("ImportIFC")
            self.ifc_import_settings = blenderbim.bim.import_ifc.IfcImportSettings.factory(bpy.context, "", logger)
            settings = ifcopenshell.geom.settings()
            shape = ifcopenshell.geom.create_shape(settings, entity)
            ifc_importer = blenderbim.bim.import_ifc.IfcImporter(self.ifc_import_settings)
            ifc_importer.file = file
            mesh = ifc_importer.create_mesh(entity, shape)
            obj = bpy.data.objects.new("IFC Element", mesh)
            bpy.context.scene.collection.objects.link(obj)
        except:
            print("Entity could not be converted into a shape", entity)


def register():
    bpy.utils.register_class(SvIfcCreateShapeRefresh)
    bpy.utils.register_class(SvIfcCreateShape)


def unregister():
    bpy.utils.unregister_class(SvIfcCreateShape)
    bpy.utils.unregister_class(SvIfcCreateShapeRefresh)
