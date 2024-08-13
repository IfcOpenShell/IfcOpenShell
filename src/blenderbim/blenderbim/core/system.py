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


def load_systems(system):
    system.import_systems()
    system.enable_system_editing_ui()
    system.disable_editing_system()


def disable_system_editing_ui(system):
    system.disable_editing_system()
    system.disable_system_editing_ui()


def add_system(ifc, system, ifc_class=None):
    ifc.run("system.add_system", ifc_class=ifc_class)
    system.import_systems()


def edit_system(ifc, system_tool, system=None):
    attributes = system_tool.export_system_attributes()
    ifc.run("system.edit_system", system=system, attributes=attributes)
    system_tool.disable_editing_system()
    system_tool.import_systems()


def remove_system(ifc, system_tool, system=None):
    ifc.run("system.remove_system", system=system)
    system_tool.import_systems()


def enable_editing_system(system_tool, system=None):
    system_tool.import_system_attributes(system)
    system_tool.set_active_edited_system(system)


def disable_editing_system(system):
    system.disable_editing_system()


def assign_system(ifc, system=None, product=None):
    ifc.run("system.assign_system", products=[product], system=system)


def unassign_system(ifc, system=None, product=None):
    ifc.run("system.unassign_system", products=[product], system=system)


def select_system_products(system_tool, system=None):
    system_tool.select_system_products(system)
    system_tool.set_active_system(system)


def show_ports(ifc, system, spatial, element=None):
    obj = ifc.get_object(element)
    if obj and ifc.is_moved(obj):
        system.run_geometry_edit_object_placement(obj=obj)

    ports = system.get_ports(element)
    system.load_ports(element, ports)
    spatial.select_products(ports)


def hide_ports(ifc, system, element=None):
    obj = ifc.get_object(element)
    if obj and ifc.is_moved(obj):
        system.run_geometry_edit_object_placement(obj=obj)

    ports = system.get_ports(element)
    for port in ports:
        obj = ifc.get_object(port)
        if obj and ifc.is_moved(obj):
            system.run_geometry_edit_object_placement(obj=obj)

    system.delete_element_objects(ports)


def add_port(ifc, system, element=None):
    system.load_ports(element, system.get_ports(element))
    obj = system.create_empty_at_cursor_with_element_orientation(element)
    port = system.run_root_assign_class(obj=obj, ifc_class="IfcDistributionPort", should_add_representation=False)
    ifc.run("system.assign_port", element=element, port=port)


def remove_port(ifc, system, port=None):
    system.delete_element_objects([port])
    ifc.run("root.remove_product", product=port)


def connect_port(ifc, port1=None, port2=None):
    ifc.run("system.connect_port", port1=port1, port2=port2)


def disconnect_port(ifc, port=None):
    ifc.run("system.disconnect_port", port=port)


def set_flow_direction(ifc, system, port=None, direction=None):
    port2 = system.get_connected_port(port)
    if not port2:
        return
    ifc.run("system.connect_port", port1=port, port2=port2, direction=direction)
