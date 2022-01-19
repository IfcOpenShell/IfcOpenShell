# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of IfcOpenShell.
#
# IfcOpenShell is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# IfcOpenShell is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with IfcOpenShell.  If not, see <http://www.gnu.org/licenses/>.

import ifcopenshell


class Data:
    is_loaded = False
    materials = {}
    constituent_sets = {}
    constituents = {}
    layer_sets_usages = {}
    layer_sets = {}
    layers = {}
    profile_set_usages = {}
    profile_sets = {}
    profiles = {}
    lists = {}
    products = {}
    _file = None

    @classmethod
    def purge(cls):
        cls.is_loaded = False
        cls.materials = {}
        cls.constituent_sets = {}
        cls.constituents = {}
        cls.layer_set_usages = {}
        cls.layer_sets = {}
        cls.layers = {}
        cls.profile_set_usages = {}
        cls.profile_sets = {}
        cls.profiles = {}
        cls.lists = {}
        cls.products = {}
        cls._file = None

    @classmethod
    def load(cls, file, product_id=None):
        cls._file = file
        if not cls._file:
            return
        if product_id:
            return cls.load_product_material(product_id)
        cls.load_materials()
        cls.load_constituents()
        cls.load_layers()
        cls.load_layer_usages()
        cls.load_profiles()
        cls.load_profile_usages()
        cls.load_lists()
        cls.is_loaded = True

    @classmethod
    def load_materials(cls):
        cls.materials = {}
        cls.load_element("IfcMaterial", cls.materials)

    @classmethod
    def load_constituents(cls):
        cls.constituent_sets = {}
        cls.constituents = {}
        cls.load_element("IfcMaterialConstituent", cls.constituents)
        cls.load_element("IfcMaterialConstituentSet", cls.constituent_sets)

    @classmethod
    def load_layers(cls):
        cls.layer_sets = {}
        cls.layers = {}
        cls.load_element("IfcMaterialLayer", cls.layers)
        cls.load_element("IfcMaterialLayerSet", cls.layer_sets)

    @classmethod
    def load_layer_usages(cls):
        cls.layer_set_usages = {}
        cls.load_element("IfcMaterialLayerSetUsage", cls.layer_set_usages)

    @classmethod
    def load_profile_usages(cls):
        cls.profile_set_usages = {}
        cls.load_element("IfcMaterialProfileSetUsage", cls.profile_set_usages)

    @classmethod
    def load_profiles(cls):
        cls.profile_sets = {}
        cls.profiles = {}
        cls.load_element("IfcMaterialProfile", cls.profiles)
        cls.load_element("IfcMaterialProfileSet", cls.profile_sets)

    @classmethod
    def load_lists(cls):
        cls.lists = {}
        cls.load_element("IfcMaterialList", cls.lists)

    @classmethod
    def load_product_material(cls, product_id):
        cls.products[product_id] = {}
        for association in cls._file.by_id(product_id).HasAssociations:
            if association.is_a("IfcRelAssociatesMaterial"):
                cls.load_association(association, product_id)

    @classmethod
    def load_element(cls, ifc_class, to_dict):
        try:
            elements = cls._file.by_type(ifc_class)
        except:
            return
        for element in elements:
            to_dict[element.id()] = cls.get_simple_info(element)

    @classmethod
    def get_simple_info(cls, element):
        info = element.get_info()
        for key, value in info.items():
            if isinstance(value, ifcopenshell.entity_instance):
                info[key] = value.id()
            elif isinstance(value, tuple) and value and isinstance(value[0], ifcopenshell.entity_instance):
                info[key] = [v.id() for v in value]
        return info

    @classmethod
    def load_association(cls, association, product_id):
        material_select = association.RelatingMaterial
        cls.products[product_id] = {"type": material_select.is_a(), "id": material_select.id()}
