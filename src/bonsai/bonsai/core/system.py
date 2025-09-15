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

from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Union

if TYPE_CHECKING:
    import bpy
    import ifcopenshell
    import bonsai.tool as tool


def load_systems(system: type[tool.System]) -> None:
    system.import_systems()
    system.enable_system_editing_ui()
    system.disable_editing_system()


def disable_system_editing_ui(system: type[tool.System]) -> None:
    system.disable_editing_system()
    system.disable_system_editing_ui()


def add_system(
    ifc: type[tool.Ifc],
    group: type[tool.Group],
    system: type[tool.System],
    ifc_class: str,
    parent_system: Union[ifcopenshell.entity_instance, None],
) -> None:
    new_system = ifc.run("system.add_system", ifc_class=ifc_class)
    if parent_system:
        ifc.run("group.assign_group", products=[new_system], group=parent_system)
        group.toggle_group(parent_system, "IfcSystem", "EXPAND")

    system.import_systems()


def edit_system(ifc: type[tool.Ifc], system_tool: type[tool.System], system: ifcopenshell.entity_instance) -> None:
    attributes = system_tool.export_system_attributes()
    ifc.run("system.edit_system", system=system, attributes=attributes)
    system_tool.disable_editing_system()
    system_tool.import_systems()


def remove_system(
    ifc: type[tool.Ifc],
    group: type[tool.Group],
    system_tool: type[tool.System],
    system: ifcopenshell.entity_instance,
) -> None:
    ifc.run("system.remove_system", system=system)
    system_tool.import_systems()
    group.update_uilist_index("IfcSystem")


def enable_editing_system(system_tool: type[tool.System], system: ifcopenshell.entity_instance) -> None:
    system_tool.import_system_attributes(system)
    system_tool.set_active_edited_system(system)


def disable_editing_system(system: type[tool.System]) -> None:
    system.disable_editing_system()


def assign_system(
    ifc: type[tool.Ifc], system: ifcopenshell.entity_instance, products: list[ifcopenshell.entity_instance]
) -> None:
    ifc.run("system.assign_system", products=products, system=system)


def unassign_system(
    ifc: type[tool.Ifc], system: ifcopenshell.entity_instance, products: list[ifcopenshell.entity_instance]
) -> None:
    ifc.run("system.unassign_system", products=products, system=system)


def select_system_products(system_tool: type[tool.System], system: ifcopenshell.entity_instance) -> None:
    system_tool.select_system_products(system)
    system_tool.set_active_system(system)


def show_ports(
    ifc: type[tool.Ifc], system: type[tool.System], spatial: type[tool.Spatial], element: ifcopenshell.entity_instance
) -> None:
    obj = ifc.get_object(element)
    if obj and ifc.is_moved(obj):
        system.run_geometry_edit_object_placement(obj=obj)

    ports = system.get_ports(element)
    system.load_ports(element, ports)
    spatial.select_products(ports)


def hide_ports(ifc: type[tool.Ifc], system: type[tool.System], element: ifcopenshell.entity_instance) -> None:
    obj = ifc.get_object(element)
    if obj and ifc.is_moved(obj):
        system.run_geometry_edit_object_placement(obj=obj)

    ports = system.get_ports(element)
    for port in ports:
        obj = ifc.get_object(port)
        if obj and ifc.is_moved(obj):
            system.run_geometry_edit_object_placement(obj=obj)

    system.delete_element_objects(ports)


def add_port(ifc: type[tool.Ifc], system: type[tool.System], element: ifcopenshell.entity_instance) -> None:
    system.load_ports(element, system.get_ports(element))
    obj = system.create_empty_at_cursor_with_element_orientation(element)
    port = system.run_root_assign_class(obj=obj, ifc_class="IfcDistributionPort", should_add_representation=False)
    ifc.run("system.assign_port", element=element, port=port)


def remove_port(ifc: type[tool.Ifc], system: type[tool.System], port: ifcopenshell.entity_instance) -> None:
    system.delete_element_objects([port])
    ifc.run("root.remove_product", product=port)


def connect_port(ifc: type[tool.Ifc], port1: ifcopenshell.entity_instance, port2: ifcopenshell.entity_instance) -> None:
    ifc.run("system.connect_port", port1=port1, port2=port2)


def disconnect_port(ifc: type[tool.Ifc], port: ifcopenshell.entity_instance) -> None:
    ifc.run("system.disconnect_port", port=port)


def set_flow_direction(
    ifc: type[tool.Ifc], system: type[tool.System], port: ifcopenshell.entity_instance, direction: str
) -> None:
    port2 = system.get_connected_port(port)
    if not port2:
        return
    ifc.run("system.connect_port", port1=port, port2=port2, direction=direction)
