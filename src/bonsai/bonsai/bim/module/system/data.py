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

from typing import Any, Union, Optional, List, Literal

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
            "unassigned_distribution_elements": cls.unassigned_distribution_elements(),
        }
        cls.is_loaded = True

    @classmethod
    def system_class(cls):
        declaration = tool.Ifc.schema().declaration_by_name("IfcSystem").as_entity()
        assert declaration
        declarations = ifcopenshell.util.schema.get_subtypes(declaration)
        version = tool.Ifc.get_schema()

        # We're only interested in systems for services. Not sure why IFC groups these together.
        return [
            (c, c, get_entity_doc(version, c).get("description", ""), tool.System.SYSTEM_ICONS[c], i)
            for i, c in enumerate(sorted([d.name() for d in declarations]))
            if c != "IfcStructuralAnalysisModel"
        ]

    @classmethod
    def total_systems(cls):
        return len(tool.System.get_systems())

    @classmethod
    def active_system(cls) -> Union[dict[str, Any], None]:
        active_system = tool.System.get_active_system()
        if not active_system:
            return None
        return {"id": active_system.id(), "Name": active_system.Name, "ifc_class": active_system.is_a()}

    @classmethod
    def unassigned_distribution_elements(cls):
        results = []
        ifc_file = tool.Ifc.get()
        for element in ifc_file.by_type("IfcDistributionElement"):
            if not ifcopenshell.util.system.get_element_systems(element):
                obj = tool.Ifc.get_object(element)
                name = obj.name if obj else element.Name or "Unnamed"
                results.append({
                    "id": element.id(),
                    "name": name,
                    "ifc_class": element.is_a(),
                })
        
        return results


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
        cls.element = None
        if obj := bpy.context.active_object:
            cls.element = tool.Ifc.get_entity(obj)
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
    def total_ports(cls) -> int:
        return len(ifcopenshell.util.system.get_ports(cls.element))

    @classmethod
    def is_port(cls) -> bool:
        return bool(cls.element and cls.element.is_a("IfcDistributionPort"))

    @classmethod
    def port_relating_object_name(cls) -> str:
        return tool.Ifc.get_object(tool.System.get_port_relating_element(cls.element)).name

    @classmethod
    def port_connected_object_name(cls) -> Union[str, None]:
        connected_port = tool.System.get_connected_port(cls.element)
        if not connected_port:
            return
        connected_element = tool.System.get_port_relating_element(connected_port)
        return tool.Ifc.get_object(connected_element).name

    @classmethod
    def located_ports_data(cls) -> list[dict[str, Any]]:
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

            data.append(
                {
                    "id": port.id(),
                    "FlowDirection": port.FlowDirection,
                    "port_obj_name": port_obj_name,
                    "connected_obj_name": connected_obj_name,
                }
            )
        return data

    @classmethod
    def selected_objects_flow_direction(cls) -> Union[str, None]:
        for port_data in cls.data["located_ports_data"]:
            if port_data["connected_obj_name"] is None:
                continue
            connected_obj = bpy.data.objects[port_data["connected_obj_name"]]
            if connected_obj in bpy.context.selected_objects:
                return port_data["FlowDirection"]


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
    def zones(cls) -> list[dict[str, Any]]:
        obj = bpy.context.active_object
        assert obj
        element = tool.Ifc.get_entity(obj)
        assert element
        return [
            {
                "id": z.id(),
                "Name": (z.Name or "Unnamed"),
            }
            for z in ifcopenshell.util.system.get_element_zones(element)
        ]


# Tree structure for system/group hierarchy representation

NodeType = Literal["system", "connection_group", "branch_group", "element"]


class SystemTreeNode:
    """Represents a node in the system hierarchy tree.
    
    This separates the tree structure from the UI representation,
    making it easier to navigate and manipulate the hierarchy.
    """
    
    def __init__(
        self,
        node_type: NodeType,
        ifc_entity: Optional[ifcopenshell.entity_instance] = None,
        synthetic_id: Optional[int] = None,
        name: str = "",
        is_expanded: bool = False,
    ):
        """Initialize a tree node.
        
        Args:
            node_type: Type of node (system, connection_group, branch_group, element)
            ifc_entity: The IFC entity this node represents (None for synthetic groups)
            synthetic_id: Negative ID for connection/branch groups
            name: Display name for the node
            is_expanded: Whether this node's children are visible
        """
        self.node_type: NodeType = node_type
        self.ifc_entity: Optional[ifcopenshell.entity_instance] = ifc_entity
        self.synthetic_id: Optional[int] = synthetic_id
        self.name: str = name
        self.is_expanded: bool = is_expanded
        
        self.parent: Optional[SystemTreeNode] = None
        self.children: List[SystemTreeNode] = []
        self.depth: int = 0
        
        # Additional metadata
        self.connection_group_index: Optional[int] = None
        self.is_connection_group: bool = node_type == "connection_group"
        self.is_branch_group: bool = node_type == "branch_group"
        self.is_element: bool = node_type == "element"
    
    @property
    def ifc_definition_id(self) -> int:
        """Get the IFC ID or synthetic ID for this node."""
        if self.synthetic_id is not None:
            return self.synthetic_id
        if self.ifc_entity:
            return self.ifc_entity.id()
        return 0
    
    def add_child(self, child: "SystemTreeNode") -> "SystemTreeNode":
        """Add a child node and set parent/depth relationships."""
        child.parent = self
        child.depth = self.depth + 1
        self.children.append(child)
        return child
    
    def find_ancestor_system(self) -> Optional["SystemTreeNode"]:
        """Find the nearest ancestor that is a system node."""
        current = self.parent
        while current:
            if current.node_type == "system":
                return current
            current = current.parent
        return None
    
    def find_by_ifc_id(self, ifc_id: int) -> Optional["SystemTreeNode"]:
        """Recursively find a node by IFC entity ID."""
        if self.ifc_definition_id == ifc_id:
            return self
        for child in self.children:
            result = child.find_by_ifc_id(ifc_id)
            if result:
                return result
        return None
    
    def flatten_to_list(self, result: Optional[List["SystemTreeNode"]] = None) -> List["SystemTreeNode"]:
        """Flatten the tree to a list in display order (depth-first, respecting expanded state).
        
        This generates the order that should appear in the UIList.
        """
        if result is None:
            result = []
        
        result.append(self)
        
        # Only include children if this node is expanded
        if self.is_expanded:
            for child in self.children:
                child.flatten_to_list(result)
        
        return result
    
    def __repr__(self) -> str:
        entity_info = f"#{self.ifc_entity.id()}" if self.ifc_entity else f"synthetic:{self.synthetic_id}"
        return f"<SystemTreeNode {self.node_type} {entity_info} '{self.name}' depth={self.depth} children={len(self.children)}>"


class SystemTree:
    """Container for the entire system tree structure."""
    
    def __init__(self):
        self.roots: List[SystemTreeNode] = []
        self._id_map: dict[int, SystemTreeNode] = {}
    
    def add_root(self, node: SystemTreeNode) -> SystemTreeNode:
        """Add a root-level node."""
        self.roots.append(node)
        self._index_node(node)
        return node
    
    def _index_node(self, node: SystemTreeNode):
        """Recursively index a node and its children by IFC ID."""
        self._id_map[node.ifc_definition_id] = node
        for child in node.children:
            self._index_node(child)
    
    def find_by_id(self, ifc_id: int) -> Optional[SystemTreeNode]:
        """Find a node by IFC entity ID using the index."""
        return self._id_map.get(ifc_id)
    
    def flatten(self) -> List[SystemTreeNode]:
        """Flatten entire tree to a list."""
        result = []
        for root in self.roots:
            root.flatten_to_list(result)
        return result
    
    def rebuild_index(self):
        """Rebuild the ID index after tree modifications."""
        self._id_map.clear()
        for root in self.roots:
            self._index_node(root)

