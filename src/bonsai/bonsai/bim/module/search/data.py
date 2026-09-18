# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2023 Dion Moult <dion@thinkmoult.com>
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

import json

import bpy
import ifcopenshell.util.element
from natsort import natsorted

import bonsai.tool as tool


def refresh():
    SearchData.is_loaded = False
    ColourByPropertyData.is_loaded = False
    SelectSimilarData.is_loaded = False


class SearchData:
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        cls.is_loaded = True
        cls.data = {}
        cls.data["saved_searches"] = cls.saved_searches()

    @classmethod
    def saved_searches(cls) -> list[tuple[str, str, str]]:
        if not tool.Ifc.get():
            return []
        groups = tool.Ifc.get().by_type("IfcGroup")
        results: list[ifcopenshell.entity_instance] = []
        for group in groups:
            try:
                data = json.loads(group.Description)
                if isinstance(data, dict) and data.get("type", None) == "BBIM_Search" and data.get("query", None):
                    results.append(group)
            except:
                pass
        enum_items = [(str(g.id()), g.Name or "Unnamed", "") for g in results]
        return natsorted(enum_items, key=lambda x: x[1])


class ColourByPropertyData:
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        cls.is_loaded = True
        cls.data = {}
        cls.data["saved_colourschemes"] = cls.saved_colourschemes()
        cls.data["colourscheme_key"] = cls.colourscheme_key()

    @classmethod
    def saved_colourschemes(cls):
        groups = tool.Ifc.get().by_type("IfcGroup")
        results = []
        for group in groups:
            try:
                data = json.loads(group.Description)
                if (
                    isinstance(data, dict)
                    and data.get("type", None) == "BBIM_Search"
                    and data.get("colourscheme", None)
                ):
                    results.append(group)
            except:
                pass
        return [(str(g.id()), g.Name or "Unnamed", "") for g in sorted(results, key=lambda x: x.Name or "Unnamed")]

    @classmethod
    def colourscheme_key(cls):
        default = [("QUERY", "Custom Query", "Specify a custom query to colour by"), None]
        ifc_file = tool.Ifc.get()
        if not ifc_file:
            return default

        keys = set()

        # Include the attributes of the currently selected element's class, if any.
        obj = bpy.context.active_object
        element = tool.Ifc.get_entity(obj) if obj else None
        if element:
            keys.update(a.name() for a in element.wrapped_data.declaration().as_entity().all_attributes())

        # Regardless of selection, offer every property and quantity set defined
        # anywhere in the loaded IFC file, not just the ones on the active object.
        for pset in ifc_file.by_type("IfcPropertySet"):
            keys.update(cls.property_set_keys(pset.Name, (p.Name for p in pset.HasProperties or [])))
        for qto in ifc_file.by_type("IfcElementQuantity"):
            keys.update(cls.property_set_keys(qto.Name, (q.Name for q in qto.Quantities or [])))

        results = [(k, k, "") for k in natsorted(keys)]
        return default + results

    @staticmethod
    def property_set_keys(pset_name, property_names):
        if not pset_name:
            return []
        if pset_name.endswith("Common"):
            template = '/.*Common/."{}"'
        elif pset_name.endswith("BaseQuantities"):
            template = '/.*BaseQuantities/."{}"'
        else:
            template = f'"{pset_name}"."{{}}"'
        return [template.format(name) for name in property_names if name and name != "id"]


class SelectSimilarData:
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        cls.is_loaded = True
        cls.data = {}
        cls.data["element_key"] = cls.element_key()

    @classmethod
    def element_key(cls):
        obj = bpy.context.active_object
        if not obj:
            return []
        element = tool.Ifc.get_entity(obj)
        if not element:
            return []
        keys = [a.name() for a in element.wrapped_data.declaration().as_entity().all_attributes()]
        psets = ifcopenshell.util.element.get_psets(element, psets_only=True)
        for pset, properties in psets.items():
            if pset.endswith("Common"):
                keys.extend([f'/.*Common/."{name}"' for name in properties.keys() if name != "id"])
            else:
                pset_part = f'"{pset}"' if " " in pset else pset
                keys.extend(
                    [
                        f'{pset_part}."{name}"' if " " in name else f"{pset_part}.{name}"
                        for name in properties.keys()
                        if name != "id"
                    ]
                )
        return [(k, k, "") for k in keys]
