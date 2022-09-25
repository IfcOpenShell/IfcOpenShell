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

from types import ClassMethodDescriptorType
import bpy
import blenderbim.core.tool
import blenderbim.tool as tool
import ifcopenshell
from mathutils import Vector
from ifcopenshell import util
from blenderbim.bim.module.pset.qto_calculator import QtoCalculator



class Qto(blenderbim.core.tool.Qto):
    @classmethod
    def get_radius_of_selected_vertices(cls, obj):
        selected_verts = [v.co for v in obj.data.vertices if v.select]
        total = Vector()
        for v in selected_verts:
            total += v
        circle_center = total / len(selected_verts)
        return max([(v - circle_center).length for v in selected_verts])

    @classmethod
    def set_qto_result(cls, result):
        bpy.context.scene.BIMQtoProperties.qto_result = str(round(result, 3))

    @classmethod
    def set_active_object(cls, object):
        bpy.context.view_layer.objects.active = object

    @classmethod
    def get_pset_qto_object_ifc_info(cls, object):
        element = tool.Ifc.get_entity(object)
        pset_qto_ifc_instance = ifcopenshell.util.element.get_psets(element, qtos_only = True)
        return pset_qto_ifc_instance

    @classmethod
    def get_pset_qto_properties(cls, object):
        file = tool.Ifc.get()
        schema = file.schema
        pset_qto = util.pset.PsetQto(schema)
        pset_qto_name = cls.get_pset_qto_name(object)
        pset_qto_properties = pset_qto.get_by_name(pset_qto_name).get_info()['HasPropertyTemplates']
        return pset_qto_properties

    @classmethod
    def get_pset_qto_name(cls, object):
        applicable_pset_names = cls.get_applicable_pset_names(object)
        for applicable_pset_name in applicable_pset_names:
            if 'Qto_' in applicable_pset_name:
                pset_qto_name = applicable_pset_name
                return pset_qto_name

    @classmethod
    def get_applicable_pset_names(cls, object):
        file = tool.Ifc.get()
        schema = file.schema
        pset_qto = util.pset.PsetQto(schema)
        entity = tool.Ifc.get_entity(object)
        ifc_object_type = entity.get_info()['type']
        applicable_pset_names = pset_qto.get_applicable_names(ifc_object_type)
        return applicable_pset_names

    @classmethod
    def edit_qto(cls, object, calculated_quantities):
        file = tool.Ifc.get()
        pset_qto_id = cls.get_pset_qto_id(object)
        pset_qto_name = cls.get_pset_qto_name(object)

        ifcopenshell.api.run("pset.edit_qto",
                file,
                **{"qto" : pset_qto_id, "name" : pset_qto_name, "properties": calculated_quantities}
            )

    @classmethod
    def get_pset_qto_id(cls, object):
        file = tool.Ifc.get()
        pset_qto_name = cls.get_pset_qto_name(object)
        pset_qto_object_ifc_instance = cls.get_pset_qto_object_ifc_info(object)
        pset_qto_id = file.by_id(pset_qto_object_ifc_instance[pset_qto_name]['id'])
        return pset_qto_id

    @classmethod
    def get_pset_qto_name(cls, object):
        applicable_pset_names = cls.get_applicable_pset_names(object)
        for applicable_pset_name in applicable_pset_names:
            if 'Qto_' in applicable_pset_name:
                pset_qto_name = applicable_pset_name
                return pset_qto_name

    @classmethod
    def get_new_quantity(cls, object, quantity_name, alternative_prop_names):
        calculator = QtoCalculator()
        new_quantity = calculator.guess_quantity(quantity_name, alternative_prop_names, object)
        return new_quantity

    @classmethod
    def get_non_calculated_value(cls):
        return 0

    @classmethod
    def get_rounded_value(cls, new_quantity):
        return round(new_quantity, 3)

    @classmethod
    def get_calculated_quantities(cls, object, pset_qto_properties):
        calculated_quantities = {}
        for pset_qto_property in pset_qto_properties:
            quantity_name = pset_qto_property.get_info()['Name']
            alternative_prop_names = [p.get_info()['Name'] for p in pset_qto_properties]

            new_quantity = cls.get_new_quantity(object, quantity_name, alternative_prop_names)

            if not new_quantity:
                new_quantity = cls.get_non_calculated_value()
            else:
                new_quantity = cls.get_rounded_value(new_quantity)

            calculated_quantities[quantity_name] = new_quantity

        return calculated_quantities

    @classmethod
    def assign_pset_qto_to_selected_object(cls, object):
        file = tool.Ifc.get()
        entity = tool.Ifc.get_entity(object)
        pset_qto_name = cls.get_pset_qto_name(object)
        ifcopenshell.api.run(
            "pset.add_qto",
            file,
            **{
                "product": entity,
                "name": pset_qto_name,
            },
        )
