# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
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


def calculate_circle_radius(qto, obj=None):
    result = qto.get_radius_of_selected_vertices(obj)
    qto.set_qto_result(result)
    return result


def assign_objects_base_qto(ifc, qto, selected_objects):
    for obj in selected_objects:
        assign_object_base_qto(ifc, qto, obj)


def assign_object_base_qto(ifc, qto, obj):
    product = ifc.get_entity(obj)
    if not product:
        return
    base_quantity_name = qto.get_applicable_base_quantity_name(product)
    if not base_quantity_name:
        return
    ifc.run(
        "pset.add_qto",
        product=product,
        name=base_quantity_name,
    )


def calculate_objects_base_quantities(ifc, cost, qto, calculator, selected_objects):
    if selected_objects:
        for obj in selected_objects:
            calculate_object_base_quantities(ifc, cost, qto, calculator, obj)


def calculate_object_base_quantities(ifc, cost, qto, calculator, obj):
    product = ifc.get_entity(obj)
    if not product:
        return
    base_quantity_name = qto.get_applicable_base_quantity_name(product)
    if not base_quantity_name:
        print(f"There is no base quantity")
        return
    base_qto = qto.get_base_qto(product)
    if not base_qto:
        base_qto = ifc.run(
            "pset.add_qto",
            product=product,
            name=base_quantity_name,
        )
    calculated_quantities = qto.get_calculated_object_quantities(calculator, base_quantity_name, obj)
    ifc.run("pset.edit_qto", qto=base_qto, properties=calculated_quantities)
    cost.update_cost_items(product=product)