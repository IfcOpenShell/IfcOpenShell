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
    system_tool.set_active_system(system)


def disable_editing_system(system):
    system.disable_editing_system()


def assign_system(ifc, system=None, product=None):
    ifc.run("system.assign_system", product=product, system=system)


def unassign_system(ifc, system=None, product=None):
    ifc.run("system.unassign_system", product=product, system=system)


def select_system_products(system_tool, system=None):
    system_tool.select_system_products(system)


def show_ports(system, element=None):
    ports = system.get_ports(element)
    system.load_ports(ports)
    system.select_elements(ports)


def hide_ports(system, element=None):
    system.delete_element_objects(system.get_ports(element))


def add_port(ifc, system, element=None):
    system.load_ports(system.get_ports(element))
    obj = system.create_empty_at_cursor_with_element_orientation(element)
    port = system.run_root_assign_class(obj=obj, ifc_class="IfcDistributionPort")
    ifc.run("system.assign_port", element=element, port=port)
