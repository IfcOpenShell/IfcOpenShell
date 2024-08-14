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

import bpy
import ifcopenshell
import ifcopenshell.util.date
import ifcopenshell.util.classification
import bonsai.tool as tool
from bonsai.bim.ifc import IfcStore


def refresh():
    ClassificationsData.is_loaded = False
    ClassificationReferencesData.is_loaded = False
    MaterialClassificationsData.is_loaded = False
    CostClassificationsData.is_loaded = False


class ClassificationsData:
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        cls.is_loaded = True
        cls.data["has_classification_file"] = cls.has_classification_file()
        cls.data["classifications"] = cls.classifications()
        cls.data["available_classifications"] = cls.available_classifications()

    @classmethod
    def has_classification_file(cls):
        return bool(IfcStore.classification_file)

    @classmethod
    def classifications(cls):
        results = []
        for element in tool.Ifc.get().by_type("IfcClassification"):
            data = element.get_info()
            if tool.Ifc.get().schema == "IFC2X3" and element.EditionDate:
                data["EditionDate"] = ifcopenshell.util.date.ifc2datetime(data["EditionDate"])
            results.append(data)
        return results

    @classmethod
    def available_classifications(cls):
        if not IfcStore.classification_file:
            return []
        return [(str(e.id()), e.Name, "") for e in IfcStore.classification_file.by_type("IfcClassification")]


class ReferencesData:
    @classmethod
    def active_classification_library(cls):
        if not IfcStore.classification_file or not IfcStore.classification_file.by_type("IfcClassification"):
            return False
        props = bpy.context.scene.BIMClassificationProperties
        name = IfcStore.classification_file.by_id(int(props.available_classifications)).Name
        if name in [e.Name for e in tool.Ifc.get().by_type("IfcClassification")]:
            return name

    @classmethod
    def classifications(cls):
        return [(str(e.id()), e.Name, "") for e in tool.Ifc.get().by_type("IfcClassification")]


class ClassificationReferencesData(ReferencesData):
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        cls.is_loaded = True
        cls.data["references"] = cls.references()
        cls.data["active_classification_library"] = cls.active_classification_library()
        cls.data["classifications"] = cls.classifications()
        cls.data["object_type"] = "Object"

    @classmethod
    def references(cls):
        results = []
        element = tool.Ifc.get_entity(bpy.context.active_object)
        if element:
            for reference in ifcopenshell.util.classification.get_references(element):
                data = reference.get_info()
                del data["ReferencedSource"]
                results.append(data)
        return results


class MaterialClassificationsData(ReferencesData):
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        cls.is_loaded = True
        cls.data["references"] = cls.references()
        cls.data["active_classification_library"] = cls.active_classification_library()
        cls.data["classifications"] = cls.classifications()
        cls.data["object_type"] = "Material"

    @classmethod
    def references(cls):
        results = []

        props = bpy.context.scene.BIMMaterialProperties
        if props.materials and props.active_material_index < len(props.materials):
            material = props.materials[props.active_material_index]
            if material.ifc_definition_id:
                element = tool.Ifc.get().by_id(material.ifc_definition_id)
                for reference in ifcopenshell.util.classification.get_references(element):
                    data = reference.get_info()
                    del data["ReferencedSource"]
                    results.append(data)
        return results


class CostClassificationsData(ReferencesData):
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        cls.is_loaded = True
        cls.data["references"] = cls.references()
        cls.data["active_classification_library"] = cls.active_classification_library()
        cls.data["classifications"] = cls.classifications()
        cls.data["object_type"] = "Cost"

    @classmethod
    def references(cls):
        results = []
        element = tool.Ifc.get().by_id(
            bpy.context.scene.BIMCostProperties.cost_items[
                bpy.context.scene.BIMCostProperties.active_cost_item_index
            ].ifc_definition_id
        )
        if element:
            for reference in ifcopenshell.util.classification.get_references(element):
                data = reference.get_info()
                del data["ReferencedSource"]
                results.append(data)
        return results
