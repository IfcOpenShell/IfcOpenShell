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
from typing import Any, Literal, Union
from bonsai.bim.ifc import IfcStore


def refresh():
    ClassificationsData.is_loaded = False
    ObjectClassificationsData.is_loaded = False
    MaterialClassificationsData.is_loaded = False
    CostClassificationsData.is_loaded = False
    ZoneClassificationsData.is_loaded = False


class ClassificationsData:
    data: dict[str, Any] = {}
    is_loaded = False

    @classmethod
    def load(cls):
        cls.is_loaded = True
        cls.data["has_classification_file"] = cls.has_classification_file()
        cls.data["classifications"] = cls.classifications()
        cls.data["available_classifications"] = cls.available_classifications()
        cls.data["classification_source"] = cls.classification_source()

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
            data["Name"] = data["Name"] or "Unnamed"
            results.append(data)
        return results

    @classmethod
    def available_classifications(cls):
        if not IfcStore.classification_file:
            return []
        return [(str(e.id()), e.Name, "") for e in IfcStore.classification_file.by_type("IfcClassification")]

    @classmethod
    def classification_source(cls) -> tool.Blender.BLENDER_ENUM_ITEMS:
        items = [
            ("FILE", "IFC File", ""),
            ("MANUAL", "Manual Entry", ""),
        ]
        dictionaries = tool.Bsdd.get_active_bsdd_enum_items()
        if dictionaries:
            items.append(("BSDD", "All Active bSDDs", ""))
        items.extend(dictionaries)
        return items


class ReferencesData:
    data: dict[str, Any]
    is_loaded = False
    obj_type: Literal["Object", "Material", "Cost", "Zone"]

    @classmethod
    def load(cls):
        cls.is_loaded = True
        cls.data = {}
        cls.data["references"] = cls.references()
        cls.data["active_classification_library"] = cls.active_classification_library()
        cls.data["classifications"] = cls.classifications()

    @classmethod
    def get_element(cls) -> Union[ifcopenshell.entity_instance, None]:
        """Get element to get classification references from."""
        raise NotImplementedError

    @classmethod
    def references(cls) -> list[dict[str, Any]]:
        results = []
        element = cls.get_element()
        if element:
            for reference in ifcopenshell.util.classification.get_references(element):
                data = reference.get_info()
                del data["ReferencedSource"]
                results.append(data)
        return results

    @classmethod
    def active_classification_library(cls):
        if not IfcStore.classification_file or not IfcStore.classification_file.by_type("IfcClassification"):
            return False
        props = tool.Classification.get_classification_props()
        name = IfcStore.classification_file.by_id(int(props.available_classifications)).Name
        if name in [e.Name for e in tool.Ifc.get().by_type("IfcClassification")]:
            return name

    @classmethod
    def classifications(cls):
        return [(str(e.id()), e.Name, "") for e in tool.Ifc.get().by_type("IfcClassification")]


class ObjectClassificationsData(ReferencesData):
    obj_type = "Object"

    @classmethod
    def get_element(cls) -> Union[ifcopenshell.entity_instance, None]:
        if obj := bpy.context.active_object:
            return tool.Ifc.get_entity(obj)
        return None


class MaterialClassificationsData(ReferencesData):
    obj_type = "Material"

    @classmethod
    def get_element(cls) -> Union[ifcopenshell.entity_instance, None]:
        props = tool.Material.get_material_props()
        if material := props.active_material:
            return tool.Ifc.get().by_id(material.ifc_definition_id)
        return None


class CostClassificationsData(ReferencesData):
    obj_type = "Cost"

    @classmethod
    def get_element(cls) -> Union[ifcopenshell.entity_instance, None]:
        props = tool.Cost.get_cost_props()
        if cost_item := props.active_cost_item:
            return tool.Ifc.get().by_id(cost_item.ifc_definition_id)
        return None


class ZoneClassificationsData(ReferencesData):
    obj_type = "Zone"

    @classmethod
    def get_element(cls) -> Union[ifcopenshell.entity_instance, None]:
        props = tool.System.get_zone_props()
        if active_zone := props.active_zone:
            return tool.Ifc.get().by_id(active_zone.ifc_definition_id)
        return None
