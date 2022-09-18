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

def calculate_all_qtos(qto, selected_objects):
    for object in selected_objects:

        qto.set_active_object(object)

        if not qto.get_pset_qto_object_ifc_instance(object):
            print("There is no pset qto instance associated to object " + object.name)
            continue

        pset_qto_properties = qto.get_pset_qto_properties(object)

        for pset_qto_property in pset_qto_properties:
            quantity_name = pset_qto_property.get_info()['Name']
            alternative_prop_names = [p.get_info()['Name'] for p in pset_qto_properties]

            new_quantity = qto.get_new_quantity(object, quantity_name, alternative_prop_names)

            if not new_quantity:
                new_quantity = qto.get_non_calculated_value()
            else:
                new_quantity = qto.get_rounded_value(new_quantity)

            qto.edit_qto(object, quantity_name, new_quantity)
