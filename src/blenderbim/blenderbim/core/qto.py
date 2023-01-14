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

def assign_pset_qto(qto, selected_objects):
    for obj in selected_objects:
        qto.assign_base_qto_to_object(obj)

def calculate_all_qtos(qto, selected_objects):
    for obj in selected_objects:
        if not qto.get_qto_entity(obj):
            print(f"There is no pset qto instance associated to object {obj.name}")
            continue

        applicable_quantity_names = qto.get_applicable_quantity_names(obj)

        calculated_quantities = qto.get_calculated_quantities(obj, applicable_quantity_names)

        qto.edit_qto(obj, calculated_quantities)

def guess_all_qtos(qto, selected_objects):
    for obj in selected_objects:
        if not qto.get_qto_entity(obj):
            print(f"There is no pset qto instance associated to object {obj.name}")
            continue

        applicable_quantity_names = qto.get_applicable_quantity_names(obj)

        calculated_quantities = qto.get_calculated_quantities(obj, applicable_quantity_names)

        qto.edit_qto(obj, calculated_quantities)
