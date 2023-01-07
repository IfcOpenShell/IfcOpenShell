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
from blenderbim.bim.module.pset.calc_quantity_function_mapper import mapper


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
    def assign_base_qto_to_object(cls, obj):
        file = tool.Ifc.get()
        entity = tool.Ifc.get_entity(obj)
        pset_qto_name = cls.get_qto_applicable_name(obj)
        ifcopenshell.api.run(
            "pset.add_qto",
            file,
            **{
                "product": entity,
                "name": pset_qto_name,
            },
        )

    @classmethod
    def get_pset_qto_object_ifc_info(cls, obj):
        element = tool.Ifc.get_entity(obj)
        pset_qto_ifc_info = ifcopenshell.util.element.get_psets(element, qtos_only = True)
        return pset_qto_ifc_info

    @classmethod
    def get_applicable_quantity_names(cls, obj):
        file = tool.Ifc.get()
        schema = file.schema
        pset_qto = util.pset.PsetQto(schema)
        qto_name = cls.get_qto_applicable_name(obj)
        properties_templates = pset_qto.get_by_name(qto_name).get_info()['HasPropertyTemplates']
        applicable_quantity_names = [a.get_info()['Name'] for a in properties_templates]
        return applicable_quantity_names

    @classmethod
    def get_qto_applicable_name(cls, obj):
        entity = tool.Ifc.get_entity(obj)
        ifc_class = entity.get_info()['type']
        qto_applicable_names = blenderbim.bim.schema.ifc.psetqto.get_applicable_names(ifc_class, qto_only=True)
        qto_applicable_name = [q for q in qto_applicable_names if "Qto_" in q and "Base" in q][0]
        return qto_applicable_name

    @classmethod
    def edit_qto(cls, obj, calculated_quantities):
        file = tool.Ifc.get()
        pset_qto_applicable_name = cls.get_qto_applicable_name(obj)
        qto_entity = cls.get_qto_entity(obj, pset_qto_applicable_name)

        ifcopenshell.api.run("pset.edit_qto",
                file,
                qto = qto_entity, properties = calculated_quantities,
            )

    @classmethod
    def get_qto_entity(cls, obj, pset_qto_applicable_name):
        file = tool.Ifc.get()
        pset_qto_object_ifc_info = cls.get_pset_qto_object_ifc_info(obj)
        qto_entity = file.by_id(pset_qto_object_ifc_info[pset_qto_applicable_name]['id'])
        return qto_entity

    @classmethod
    def get_new_calculated_quantity(cls, qto_name, quantity_name, obj):
        calculator = QtoCalculator()
        new_quantity = calculator.calculate_quantity(qto_name, quantity_name, obj)
        return new_quantity

    @classmethod
    def get_new_guessed_quantity(cls, obj, quantity_name, alternative_prop_names):
        calculator = QtoCalculator()
        new_quantity = calculator.guess_quantity(quantity_name, alternative_prop_names, obj)

    @classmethod
    def get_rounded_value(cls, new_quantity):
        return round(new_quantity, 3)

    @classmethod
    def get_calculated_quantities(cls, obj, applicable_quantity_names):
        calculated_quantities = {}
        qto_name = cls.get_qto_applicable_name(obj)
        calculator = QtoCalculator()

        for quantity_name in applicable_quantity_names:
            if not cls.has_calculator(qto_name, quantity_name):
                continue
            else:
                new_quantity = calculator.calculate_quantity(qto_name, quantity_name, obj)
                new_quantity = cls.get_rounded_value(new_quantity)

            calculated_quantities[quantity_name] = new_quantity

        return calculated_quantities

    @classmethod
    def has_calculator(cls, qto_name, quantity_name):
        return bool(mapper.get(qto_name, {}).get(quantity_name, None))

    @classmethod
    def get_guessed_quantities(cls, obj, pset_qto_properties):
        calculated_quantities = {}
        for pset_qto_property in pset_qto_properties:
            quantity_name = pset_qto_property.get_info()['Name']
            alternative_prop_names = [p.get_info()['Name'] for p in pset_qto_properties]

            new_quantity = cls.get_new_guessed_quantity(obj, quantity_name, alternative_prop_names)

            if not new_quantity:
                new_quantity = 0
            else:
                new_quantity = cls.get_rounded_value(new_quantity)

            calculated_quantities[quantity_name] = new_quantity

        return calculated_quantities

