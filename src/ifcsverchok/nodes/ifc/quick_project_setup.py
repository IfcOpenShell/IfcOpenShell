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


from email.mime import application
import bpy
import ifcopenshell
import ifcsverchok.helper
from bpy.props import StringProperty
from sverchok.node_tree import SverchCustomTreeNode
from sverchok.data_structure import updateNode
from ifcopenshell import template


class SvIfcQuickProjectSetup(bpy.types.Node, SverchCustomTreeNode, ifcsverchok.helper.SvIfcCore):
    bl_idname = "SvIfcQuickProjectSetup"
    bl_label = "IFC Quick Project Setup"
    schema_identifier: StringProperty(name="schema_identifier", update=updateNode, default="IFC4")
    timestring: StringProperty(name="timestring", update=updateNode)
    application: StringProperty(name="application", update=updateNode)
    application_version: StringProperty(name="application_version", update=updateNode)
    timestamp: StringProperty(name="timestamp", update=updateNode)

    def sv_init(self, context):
        input_socket = self.inputs.new("SvStringsSocket", "filename")
        input_socket.tooltip = "Ifc file name"
        input_socket = self.inputs.new("SvStringsSocket", "timestring")
        input_socket.tooltip = "Timestring, default = current time"
        input_socket = self.inputs.new("SvStringsSocket", "organization")
        input_socket.tooltip = "Organization"
        input_socket = self.inputs.new("SvStringsSocket", "creator")
        input_socket.tooltip = "creator"
        input_socket = self.inputs.new("SvStringsSocket", "schema_identifier")
        input_socket.tooltip = "Schema, default = 'IFC4'"
        input_socket = self.inputs.new("SvStringsSocket", "application_version")
        input_socket.tooltip = "Application version"
        input_socket = self.inputs.new("SvStringsSocket", "timestamp")
        input_socket.tooltip = "Timestamp, default = current time"
        input_socket = self.inputs.new("SvStringsSocket", "application")
        input_socket.tooltip = "Application, default = 'IfcOpenShell'"
        input_socket = self.inputs.new("SvStringsSocket", "project_globalid")
        input_socket.tooltip = "Project GlobalId"
        input_socket = self.inputs.new("SvStringsSocket", "project_name")
        input_socket.tooltip = "Project name"
        self.outputs.new("SvVerticesSocket", "file")

    def draw_buttons(self, context, layout):
        op = layout.operator(
            "node.sv_ifc_tooltip", text="", icon="QUESTION", emboss=False
        ).tooltip = "Quick Project Setup: creates Ifc file and sets up a basic project"
        # op.tooltip = self.tooltip

    def process(self):
        self.sv_input_names = [i.name for i in self.inputs]
        super().process()

    def process_ifc(self, *setting_values):
        settings = dict(zip(self.sv_input_names, setting_values))
        settings = {k: v for k, v in settings.items() if v != ""}
        file = template.create(
            filename=settings["filename"],
            timestring=settings["timestring"],
            organization=settings["organization"],
            creator=settings["creator"],
            schema_identifier=settings["schema_identifier"],
            application_version=settings["application_version"],
            timestamp=settings["timestamp"],
            application=settings["application"],
            project_globalid=settings["project_globalid"],
            project_name=settings["project_name"],
        )

        self.outputs["file"].sv_set([[file]])


def register():
    bpy.utils.register_class(SvIfcQuickProjectSetup)


def unregister():
    bpy.utils.unregister_class(SvIfcQuickProjectSetup)
