# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2022 Dion Moult <dion@thinkmoult.com>
#
# This file is part of BlenderBIM Add-on.
#
# BlenderBIM Add-on is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# BlenderBIM Add-on is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with BlenderBIM Add-on.  If not, see <http://www.gnu.org/licenses/>.

import bpy
import ifcopenshell
import ifcopenshell.util.schema
from ifcopenshell.util.doc import get_entity_doc
import blenderbim.tool as tool


def refresh():
    SystemData.is_loaded = False
    ObjectSystemData.is_loaded = False
    PortData.is_loaded = False
    SystemDecorationData.is_loaded = False


class SystemData:
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        cls.data = {
            "system_class": cls.system_class(),
            "total_systems": cls.total_systems(),
        }
        cls.is_loaded = True

    @classmethod
    def system_class(cls):
        declaration = tool.Ifc.schema().declaration_by_name("IfcSystem")
        declarations = ifcopenshell.util.schema.get_subtypes(declaration)
        version = tool.Ifc.get_schema()
        # We're only interested in systems for services. Not sure why IFC groups these together.
        return [
            (c, c, get_entity_doc(version, c).get("description", ""))
            for c in sorted([d.name() for d in declarations])
            if c not in ("IfcStructuralAnalysisModel")
        ]

    @classmethod
    def total_systems(cls):
        return len(tool.Ifc.get().by_type("IfcSystem"))


class ObjectSystemData:
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        cls.data = {
            "systems": cls.systems(),
            "total_systems": cls.total_systems(),
        }
        cls.is_loaded = True

    @classmethod
    def systems(cls):
        results = []
        element = tool.Ifc.get_entity(bpy.context.active_object)
        if not element:
            return results
        for system in ifcopenshell.util.system.get_element_systems(element):
            results.append({"id": system.id(), "name": system.Name or "Unnamed", "ifc_class": system.is_a()})
        return results

    @classmethod
    def total_systems(cls):
        return len(tool.Ifc.get().by_type("IfcSystem"))


class PortData:
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        element = tool.Ifc.get_entity(bpy.context.active_object)
        cls.element = element
        is_port = cls.is_port()
        cls.data = {
            "total_ports": cls.total_ports(),
            "located_ports_data": cls.located_ports_data(),
            "is_port": is_port,
            "port_connected_object": cls.port_connected_object() if is_port else None,
            "port_relating_object": cls.port_relating_object() if is_port else None,
        }
        # AFTER located_ports_data
        cls.data["selected_objects_flow_direction"] = cls.selected_objects_flow_direction() if not is_port else None
        cls.is_loaded = True

    @classmethod
    def total_ports(cls):
        return len(ifcopenshell.util.system.get_ports(cls.element))

    @classmethod
    def is_port(cls):
        return cls.element and cls.element.is_a("IfcDistributionPort")

    @classmethod
    def port_relating_object(cls):
        return tool.Ifc.get_object(tool.System.get_port_relating_element(cls.element))

    @classmethod
    def port_connected_object(cls):
        connected_port = tool.System.get_connected_port(cls.element)
        if not connected_port:
            return
        connected_element = tool.System.get_port_relating_element(connected_port)
        return tool.Ifc.get_object(connected_element)

    @classmethod
    def located_ports_data(cls):
        ports = ifcopenshell.util.system.get_ports(cls.element)

        data = []
        for port in ports:
            port_obj = tool.Ifc.get_object(port)
            connected_port = tool.System.get_connected_port(port)
            if connected_port:
                connected_obj = tool.Ifc.get_object(tool.System.get_port_relating_element(connected_port))
            else:
                connected_obj = None

            data.append((port, port_obj, connected_obj))
        return data

    @classmethod
    def selected_objects_flow_direction(cls):
        for port, port_obj, connected_obj in cls.data["located_ports_data"]:
            if connected_obj in bpy.context.selected_objects:
                return port.FlowDirection


class SystemDecorationData:
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        cls.data = {
            "decoration_data": cls.decoration_data(),
        }
        cls.is_loaded = True

    @classmethod
    def decoration_data(cls):
        return tool.System.get_decoration_data()
