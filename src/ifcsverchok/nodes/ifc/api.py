
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
import ifcopenshell.api
import ifcsverchok.helper
from bpy.props import StringProperty, EnumProperty
from sverchok.node_tree import SverchCustomTreeNode
from sverchok.data_structure import updateNode


def update_usecase(self, context):
    module_usecase = self.get_module_usecase()
    if module_usecase:
        self.generate_node(*module_usecase)


class SvIfcTooltip(bpy.types.Operator):
    bl_idname = "node.sv_ifc_tooltip"
    bl_label = "IFC Info"
    tooltip: bpy.props.StringProperty()

    @classmethod
    def description(cls, context, properties):
        return properties.tooltip

    def execute(self, context):
        return {"FINISHED"}


class SvIfcApi(bpy.types.Node, SverchCustomTreeNode, ifcsverchok.helper.SvIfcCore):
    bl_idname = "SvIfcApi"
    bl_label = "IFC API"
    tooltip: StringProperty(name="Tooltip")
    usecase: StringProperty(name="Usecase", update=update_usecase)

    def sv_init(self, context):
        self.inputs.new("SvStringsSocket", "usecase").prop_name = "usecase"
        self.outputs.new("SvStringsSocket", "file")

    def draw_buttons(self, context, layout):
        op = layout.operator("node.sv_ifc_tooltip", text="", icon="QUESTION", emboss=False)
        op.tooltip = self.tooltip

    def process(self):
        print("process api node")
        module_usecase = self.get_module_usecase()
        if module_usecase:
            self.sv_input_names = [i.name for i in self.inputs]
            super().process()

    def get_module_usecase(self):
        usecase = self.inputs["usecase"].sv_get()[0][0]
        if usecase:
            return usecase.split(".")

    def generate_node(self, module, usecase):
        try:
            node_data = ifcopenshell.api.extract_docs(module, usecase)
        except:
            print("node not generated:", module, usecase)
            return
        while len(self.inputs) > 1:
            self.inputs.remove(self.inputs[-1])

        self.tooltip = ""
        for name, data in node_data["inputs"].items():
            setattr(SvIfcApi, name, StringProperty(name=name, update=updateNode))
            self.inputs.new("SvStringsSocket", name).prop_name = name
            if "default" in data:
                self.tooltip = f"{name} ({data['default']}): {data['description']}\n"
            else:
                self.tooltip = f"{name}: {data['description']}\n"

        if "output" in node_data:
            name = node_data["output"]["name"]
            if name != "file":
                setattr(SvIfcApi, name, StringProperty(name=name, update=updateNode))
                self.outputs.new("SvStringsSocket", name).prop_name = name
                self.tooltip = f"{name}: {node_data['output']['description']}\n"



        self.tooltip = self.tooltip.strip()

    def process_ifc(self, usecase, *setting_values):
        if usecase:
            settings = dict(zip(self.sv_input_names[1:], setting_values))
            settings = {k: v for k, v in settings.items() if v != ""}
            if "file" in settings: 
                file = settings.pop("file")   
                if file:     
                    print("triggered if statement: " + usecase)
                    try:    
                        output = ifcopenshell.api.run(usecase, file[0], **settings)
                    except:
                        print("failed to run", usecase)
                        return
                    self.outputs["file"].sv_set([file]) 
                    output_key = [k for k in self.outputs.keys() if k != "file"] 
                    if output_key:
                        self.outputs[output_key[0]].sv_set([output])
            else:
                print("triggered else statement: " + usecase)
                try: 
                    file = ifcopenshell.api.run(usecase, **settings)
                except:
                    print("Failed to run", usecase)
                    return
                self.outputs["file"].sv_set([file])



def register():
    bpy.utils.register_class(SvIfcTooltip)
    bpy.utils.register_class(SvIfcApi)

def unregister():
    bpy.utils.unregister_class(SvIfcApi)
    bpy.utils.unregister_class(SvIfcTooltip)
