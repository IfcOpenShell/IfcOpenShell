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
import ifcopenshell
import ifcopenshell.api
import ifcsverchok.helper
from bpy.props import StringProperty
from sverchok.node_tree import SverchCustomTreeNode
from sverchok.data_structure import updateNode
import importlib


class SvIfcTooltipWIP(bpy.types.Operator):
    bl_idname = "node.sv_ifc_tooltipWIP"
    bl_label = "IFC Info"
    tooltip: bpy.props.StringProperty()

    @classmethod
    def description(cls, context, properties):
        return properties.tooltip

    def execute(self, context):
        return {"FINISHED"}


class SvIfcApiWIP(bpy.types.Node, SverchCustomTreeNode, ifcsverchok.helper.SvIfcCore):

    bl_idname = "SvIfcApiWIP"
    bl_label = "IFC API WIP"
    tooltip: StringProperty(name="Tooltip")
    usecase: StringProperty(name="usecase", update=updateNode)
    current_usecase: StringProperty(name="current_usecase")

    def sv_init(self, context):
        self.inputs.new("SvStringsSocket", "usecase").prop_name = "usecase"
        # input_socket.tooltip = "ifcopenshell.api usecase, written like 'module.usecase' \n E.g.: 'project.create_file'"
        self.outputs.new("SvVerticesSocket", "file")

    def draw_buttons(self, context, layout):
        op = layout.operator(
            "node.sv_ifc_tooltip", text="", icon="QUESTION", emboss=False
        ).tooltip = "ifcopenshell.api usecase, written like 'module.usecase' \n E.g.: 'project.create_file"
        # op.tooltip = self.tooltip

    def process(self):
        self.sv_input_names = ["usecase"]
        module_usecase = self.inputs["usecase"].sv_get()[0][0]
        if module_usecase:
            try:
                module_usecase = self.get_module_usecase()
            except:
                raise Exception(f"Couldn't run generate_node(). Module usecase: {module_usecase}")
            if ".".join(module_usecase) != self.current_usecase:
                self.generate_node(*module_usecase)
            try:
                for i in range(0, len(self.inputs)):
                    input = self.inputs[i].sv_get()
            except:
                # This occurs when a blender save file is reloaded
                self.generate_node(*module_usecase)

            self.sv_input_names = [i.name for i in self.inputs]

            super().process()  # super().process() uses zip_long_repeat() which doesn't take objects like bmesh

    def get_module_usecase(self):
        usecase = self.inputs["usecase"].sv_get()[0][0]
        if usecase:
            return usecase.split(".")

    def generate_node(self, module, usecase):
        importlib.import_module(f"ifcopenshell.api.{module}.{usecase}")
        local_module = getattr(getattr(ifcopenshell.api, module), usecase)

        node_inputs = {}
        if hasattr(local_module.Usecase(local_module), "file"):
            node_inputs["file"] = None
        node_inputs.update(getattr(local_module.Usecase(local_module), "settings", {}))
        # print("node inputs: ", node_inputs)

        while len(self.inputs) > 1:
            self.inputs.remove(self.inputs[-1])

        if node_inputs:
            self.tooltip = ""
            for name, data in node_inputs.items():
                setattr(SvIfcApiWIP, name, StringProperty(name=name))
                self.inputs.new("SvStringsSocket", name).prop_name = name
                if data is not None:
                    self.tooltip = f"{name} ({data}): {data}\n"
                else:
                    self.tooltip = f"{name}: None\n"
            self.tooltip = self.tooltip.strip()
        self.current_usecase = ".".join([module, usecase])

    def process_ifc(self, usecase, *setting_values):

        if usecase and setting_values:
            settings = dict(zip(self.sv_input_names[1:], setting_values))
            settings = {k: v for k, v in settings.items() if v != ""}
            try:
                if "file" in settings:
                    file = settings["file"]
                    settings.pop("file")
                    self.outputs["file"].sv_set([ifcopenshell.api.run(usecase, file, **settings)])
                else:
                    self.outputs["file"].sv_set([ifcopenshell.api.run(usecase, **settings)])
            except:
                raise Exception(f"Couldn't run usecase.")


def register():
    bpy.utils.register_class(SvIfcTooltip)
    bpy.utils.register_class(SvIfcApiWIP)


def unregister():
    bpy.utils.unregister_class(SvIfcApiWIP)
    bpy.utils.unregister_class(SvIfcTooltip)
