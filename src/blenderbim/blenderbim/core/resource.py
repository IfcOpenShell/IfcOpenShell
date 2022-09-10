# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2022 Dion Moult, Yassine Oualid <dion@thinkmoult.com>
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

# ############################################################################ #


def load_resources(resource):
    resource.load_resources()
    resource.load_resource_properties()


def add_resource(tool_ifc, resource_tool, ifc_class, parent_resource=None):
    tool_ifc.run("resource.add_resource", ifc_class=ifc_class, parent_resource=parent_resource)
    resource_tool.load_resources()
    resource_tool.load_resource_properties()


def load_resource_properties(resource_tool, resource=None):
    resource_tool.load_resource_properties()


def disable_editing_resource(resource_tool):
    resource_tool.disable_editing_resource()


def disable_resource_editing_ui(resource_tool):
    resource_tool.disable_resource_editing_ui()


def enable_editing_resource(resource_tool, resource):
    resource_tool.enable_editing_resource(resource)
    resource_tool.load_resource_attributes(resource)


def edit_resource(ifc, resource_tool, resource):
    attributes = resource_tool.get_resource_attributes()
    ifc.run("resource.edit_resource", resource=resource, attributes=attributes)
    resource_tool.load_resource_properties()
    resource_tool.disable_editing_resource()


def remove_resource(ifc, resource_tool, resource=None):
    ifc.run("resource.remove_resource", resource=resource)
    resource_tool.load_resources()
    resource_tool.load_resource_properties()


def enable_editing_resource_time(ifc_tool, resource_tool, resource):
    resource_time = resource_tool.get_resource_time(resource)
    if resource_time is None:
        resource_time = ifc_tool.run("resource.add_resource_time", resource=resource)
    resource_tool.enable_editing_resource_time(resource)
    resource_tool.load_resource_time_attributes(resource_time)


def edit_resource_time(ifc, resource_tool, resource_time):
    attributes = resource_tool.get_resource_time_attributes()
    ifc.run("resource.edit_resource_time", resource_time=resource_time, attributes=attributes)
    resource_tool.disable_editing_resource()


def disable_editing_resource_time(resource_tool):
    resource_tool.disable_editing_resource()


def calculate_resource_work(ifc, resource_tool, resource):
    ifc.run("calculate_resource_work", resource=resource)
    resource_tool.load_resources()
    resource_tool.load_resource_properties()


def enable_editing_resource_costs(resource_tool, resource):
    resource_tool.enable_editing_resource_costs(resource)
    resource_tool.disable_editing_resource_cost_value()


def disable_editing_resource_cost_value(resource_tool):
    resource_tool.disable_editing_resource_cost_value()


def enable_editing_resource_cost_value(resource_tool, cost_value):
    resource_tool.enable_editing_cost_value_attributes(cost_value)
    resource_tool.load_cost_value_attributes(cost_value)


def enable_editing_resource_cost_value_formula(resource_tool, cost_value):
    resource_tool.enable_editing_resource_cost_value_formula(cost_value)


def edit_resource_cost_value_formula(ifc, resource_tool, cost_value):
    formula = resource_tool.get_resource_cost_value_formula()
    ifc.run("cost.edit_cost_value_formula", cost_value=cost_value, formula=formula)
    resource_tool.disable_editing_resource_cost_value()


def edit_resource_cost_value(ifc, resource_tool, cost_value):
    attributes = resource_tool.get_resource_cost_value_attributes()
    ifc.run("cost.edit_cost_value", cost_value=cost_value, attributes=attributes)
    resource_tool.disable_editing_resource_cost_value()


def enable_editing_resource_base_quantity(resource_tool, resource):
    resource_tool.enable_editing_resource_base_quantity(resource)


def add_resource_quantity(ifc, ifc_class, resource):
    ifc.run("resource.add_resource_quantity", resource=resource, ifc_class=ifc_class)


def remove_resource_quantity(ifc, resource):
    ifc.run("resource.remove_resource_quantity", resource=resource)


def enable_editing_resource_quantity(resource_tool, resource_quantity=None):
    resource_tool.enable_editing_resource_quantity(resource_quantity)


def disable_editing_resource_quantity(resource_tool):
    resource_tool.disable_editing_resource_quantity()


def edit_resource_quantity(resource_tool, ifc, physical_quantity=None):
    attributes = resource_tool.get_resource_quantity_attributes()
    ifc.run("resource.edit_resource_quantity", physical_quantity=physical_quantity, attributes=attributes)
    resource_tool.disable_editing_resource_quantity()


def import_resources(resource_tool, file_path):
    resource_tool.import_resources(file_path)
    resource_tool.load_resources()
    resource_tool.load_resource_properties()


def expand_resource(resource_tool, resource):
    resource_tool.expand_resource(resource)
    resource_tool.load_resources()
    resource_tool.load_resource_properties()


def contract_resource(resource_tool, resource):
    resource_tool.contract_resource(resource)
    resource_tool.load_resources()
    resource_tool.load_resource_properties()


def assign_resource(ifc, resource_tool, resource=None, products=None):
    if not products:
        products = resource_tool.get_selected_products()
    for product in products:
        rel = ifc.run("resource.assign_resource", relating_resource=resource, related_object=product)


def unassign_resource(ifc, resource_tool, resource=None, products=None):
    if not products:
        products = resource_tool.get_selected_products()
    for product in products:
        ifc.run("resource.unassign_resource", relating_resource=resource, related_object=product)
