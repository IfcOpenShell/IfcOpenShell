# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2022 Dion Moult <dion@thinkmoult.com>
#
# This file is part of Bonsai.
#
# Bonsai is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Bonsai is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Bonsai.  If not, see <http://www.gnu.org/licenses/>.

import bpy
import ifcopenshell
import ifcopenshell.util.schema
import ifcopenshell.util.system
import ifcopenshell.util.unit
from ifcopenshell.util.doc import get_entity_doc
import bonsai.tool as tool


def refresh():
    SystemData.is_loaded = False
    ZonesData.is_loaded = False
    ActiveObjectZonesData.is_loaded = False
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
        return len(tool.System.get_systems())


class ObjectSystemData:
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        cls.data = {
            "systems": cls.systems(),
            # AFTER SYSTEMS
            "connected_elements": cls.connected_elements(),
            "flow_controls_data": cls.flow_controls_data(),
        }
        cls.is_loaded = True

    @classmethod
    def systems(cls):
        results = []
        cls.element = tool.Ifc.get_entity(bpy.context.active_object)
        if not cls.element:
            return results
        for system in ifcopenshell.util.system.get_element_systems(cls.element):
            results.append({"id": system.id(), "name": system.Name or "Unnamed", "ifc_class": system.is_a()})
        return results

    @classmethod
    def connected_elements(cls):
        if not cls.element:
            return set()
        return tool.System.get_connected_elements(cls.element)

    @classmethod
    def flow_controls_data(cls):
        flow_controls_data = {}
        if not cls.element or not (
            cls.element.is_a("IfcDistributionControlElement") or cls.element.is_a("IfcDistributionFlowElement")
        ):
            return flow_controls_data

        if cls.element.is_a("IfcDistributionControlElement"):
            flow_controls_data["type"] = "IfcDistributionControlElement"
            flow_element = tool.System.get_flow_control_flow_element(cls.element)
            flow_element_obj = tool.Ifc.get_object(flow_element).name if flow_element else None
            flow_controls_data["flow_element"] = flow_element, flow_element_obj
        else:
            flow_controls_data["type"] = "IfcDistributionFlowElement"
            controls = [(c, tool.Ifc.get_object(c).name) for c in tool.System.get_flow_element_controls(cls.element)]
            flow_controls_data["controls"] = controls

        return flow_controls_data


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
            "port_connected_object_name": cls.port_connected_object_name() if is_port else None,
            "port_relating_object_name": cls.port_relating_object_name() if is_port else None,
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
    def port_relating_object_name(cls):
        return tool.Ifc.get_object(tool.System.get_port_relating_element(cls.element)).name

    @classmethod
    def port_connected_object_name(cls):
        connected_port = tool.System.get_connected_port(cls.element)
        if not connected_port:
            return
        connected_element = tool.System.get_port_relating_element(connected_port)
        return tool.Ifc.get_object(connected_element).name

    @classmethod
    def located_ports_data(cls):
        ports = ifcopenshell.util.system.get_ports(cls.element)

        data = []
        for port in ports:
            # port may be not present as a scene object
            port_obj_name = getattr(tool.Ifc.get_object(port), "name", None)
            connected_port = tool.System.get_connected_port(port)
            if connected_port:
                connected_obj_name = tool.Ifc.get_object(tool.System.get_port_relating_element(connected_port)).name
            else:
                connected_obj_name = None

            data.append((port, port_obj_name, connected_obj_name))
        return data

    @classmethod
    def selected_objects_flow_direction(cls):
        for port, _, connected_obj_name in cls.data["located_ports_data"]:
            if connected_obj_name is None:
                continue
            connected_obj = bpy.data.objects[connected_obj_name]
            if connected_obj in bpy.context.selected_objects:
                return port.FlowDirection


class SystemDecorationData:
    data = {}
    elements_ports_positions = {}
    is_loaded = False

    @classmethod
    def load(cls):
        cls.data = {
            "decorated_elements": cls.decorated_elements(),
        }
        cls.is_loaded = True
        cls.elements_ports_positions = {}

    @classmethod
    def get_element_ports_data(cls, element):
        """returns element's port data, caches the data until UI update

        Port data includes:
            - local port position in SI units
            - port flow direction

        """
        if element not in cls.elements_ports_positions:
            ports = tool.System.get_ports(element)
            si_conversion = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
            ports_data = []
            for port in ports:
                position = tool.Model.get_element_matrix(port, keep_local=True).translation * si_conversion
                port_data = {
                    "position": position,
                    "flow_direction": port.FlowDirection,
                }
                ports_data.append(port_data)
            cls.elements_ports_positions[element] = ports_data
        return cls.elements_ports_positions[element]

    @classmethod
    def decorated_elements(cls):
        if not ObjectSystemData.is_loaded:
            ObjectSystemData.load()

        # Priority:
        # 1. currently selected systems
        # 2. active system
        # 3. if previous steps didn't worked - decorate connected elements

        decorated_elements = set()
        if ObjectSystemData.data["systems"]:
            for system in ObjectSystemData.data["systems"]:
                system = tool.Ifc.get().by_id(system["id"])
                decorated_elements.update(ifcopenshell.util.system.get_system_elements(system))
        elif active_system := tool.System.get_active_system():
            decorated_elements = set(ifcopenshell.util.system.get_system_elements(active_system))

        if not decorated_elements:
            decorated_elements.update(ObjectSystemData.data["connected_elements"])

        return decorated_elements


class ZonesData:
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        cls.data = {"total_zones": cls.total_zones()}
        cls.is_loaded = True

    @classmethod
    def total_zones(cls):
        return len(tool.Ifc.get().by_type("IfcZone"))


class ActiveObjectZonesData:
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        cls.data = {"zones": cls.zones()}
        cls.is_loaded = True

    @classmethod
    def zones(cls):
        systems = ifcopenshell.util.system.get_element_systems(tool.Ifc.get_entity(bpy.context.active_object))
        return [s.Name or "Unnamed" for s in systems if s.is_a("IfcZone")]
