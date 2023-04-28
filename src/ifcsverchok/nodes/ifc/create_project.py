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
import ifcsverchok.helper
from sverchok.node_tree import SverchCustomTreeNode


class SvIfcCreateProject(bpy.types.Node, SverchCustomTreeNode, ifcsverchok.helper.SvIfcCore):
    bl_idname = "SvIfcCreateProject"
    bl_label = "IFC Create Project"

    def sv_init(self, context):
        input_socket = self.inputs.new("SvStringsSocket", "file")
        input_socket.tooltip = "ifc file to add the project to"
        input_socket = self.inputs.new("SvStringsSocket", "project_name")
        input_socket.tooltip = "Project name"
        self.outputs.new("SvVerticesSocket", "file")

    def draw_buttons(self, context, layout):
        op = layout.operator(
            "node.sv_ifc_tooltip", text="", icon="QUESTION", emboss=False
        ).tooltip = "Adds project, unit and context to IFC file"
        # op.tooltip = self.tooltip

    def process(self):
        # file
        file = self.inputs["file"].sv_get()[0][0]
        if file:
            schema_name = file.wrapped_data.schema
        else:
            schema_name = "IFC4"

        # project name
        project_name = self.inputs["project_name"].sv_get()[0][0]
        self.process_ifc(file, project_name)

    def process_ifc(self, file, project_name):
        # create project
        project = ifcopenshell.api.run("root.create_entity", file, ifc_class="IfcProject", name=str(project_name))
        lengthunit = ifcopenshell.api.run("unit.add_si_unit", file, unit_type="LENGTHUNIT")
        ifcopenshell.api.run("unit.assign_unit", file, units=[lengthunit])
        model = ifcopenshell.api.run("context.add_context", file, context_type="Model")
        context = ifcopenshell.api.run(
            "context.add_context",
            file,
            context_type="Model",
            context_identifier="Body",
            target_view="MODEL_VIEW",
            parent=model,
        )

        self.outputs["file"].sv_set([[file]])


def register():
    bpy.utils.register_class(SvIfcCreateProject)


def unregister():
    bpy.utils.unregister_class(SvIfcCreateProject)
