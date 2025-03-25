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
import bonsai.tool as tool
from typing import Any, Generator, Union


def refresh():
    BooleansData.is_loaded = False
    VoidsData.is_loaded = False


class VoidsData:
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        cls.data = {
            "active_opening": cls.active_opening(),
            "openings": cls.openings(),
            "fillings": cls.fillings(),
            "voided_element": cls.voided_element(),
            "filled_voids": cls.filled_voids(),
        }
        cls.is_loaded = True

    @classmethod
    def get_element_data(cls, element: ifcopenshell.entity_instance) -> dict[str, Any]:
        return {"id": element.id(), "Name": element.Name or "Unnamed"}

    @classmethod
    def active_opening(cls):
        element = tool.Ifc.get_entity(bpy.context.active_object)
        cls.element = element
        if element and element.is_a("IfcOpeningElement"):
            cls.element = element
            return element.id()

    @classmethod
    def openings(cls):
        element = tool.Ifc.get_entity(bpy.context.active_object)
        if not element:
            return []
        results = []
        for rel in getattr(element, "HasOpenings", []) or []:
            has_fillings = []
            opening = rel.RelatedOpeningElement
            for rel2 in getattr(opening, "HasFillings", []) or []:
                filling = rel2.RelatedBuildingElement
                has_fillings.append(cls.get_element_data(filling))

            results.append(
                cls.get_element_data(opening)
                | {
                    "HasFillings": has_fillings,
                }
            )
        return results

    @classmethod
    def fillings(cls):
        element = tool.Ifc.get_entity(bpy.context.active_object)
        if not element:
            return []
        results = []
        for rel in getattr(element, "HasFillings", []) or []:
            filling = rel.RelatedBuildingElement
            results.append(cls.get_element_data(filling))
        return results

    @classmethod
    def get_voided_element_data(cls, opening: ifcopenshell.entity_instance) -> Union[dict[str, Any], None]:
        voids_elements = None
        if voids := opening.VoidsElements:
            voided_element = voids[0].RelatingBuildingElement
            voids_elements = cls.get_element_data(voided_element)
        return voids_elements

    @classmethod
    def voided_element(cls) -> Union[dict[str, Any], None]:
        if not (element := cls.element) or not element.is_a("IfcOpeningElement"):
            return None
        return cls.get_voided_element_data(element)

    @classmethod
    def filled_voids(cls) -> Union[dict[str, Any], None]:
        if not (element := cls.element) or not (fills_voids := getattr(element, "FillsVoids", [])):
            return None

        opening = fills_voids[0].RelatingOpeningElement
        result = cls.get_element_data(opening) | {
            "VoidsElements": cls.get_voided_element_data(opening),
        }
        return result


class BooleansData:
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        cls.data = {}
        cls.data["total_booleans"] = cls.booleans()
        cls.data["manual_booleans"] = cls.manual_booleans()
        cls.is_loaded = True

    @classmethod
    def booleans(cls):
        props = tool.Geometry.get_geometry_props()
        obj = props.representation_obj or bpy.context.active_object
        if not (representation := tool.Geometry.get_active_representation(obj)):
            return []
        return tool.Model.get_booleans(representation=representation)

    @classmethod
    def manual_booleans(cls):
        props = tool.Geometry.get_geometry_props()
        obj = props.representation_obj or bpy.context.active_object
        if not (representation := tool.Geometry.get_active_representation(obj)):
            return []
        return tool.Model.get_manual_booleans(tool.Ifc.get_entity(obj), representation=representation)
