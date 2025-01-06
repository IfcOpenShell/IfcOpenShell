# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
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

from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Any

if TYPE_CHECKING:
    import bpy
    import ifcopenshell
    import bsdd
    import bonsai.tool as tool


def get_class_properties(client: bsdd.Client, bsdd: tool.Bsdd) -> dict[str, dict[str, Any]]:
    bsdd.clear_class_psets()
    data = bsdd.get_active_class_data(client)
    pset_dict = bsdd.get_property_dict(data)
    if pset_dict is None:
        return {}
    bsdd.create_class_psets(pset_dict)
    return pset_dict


def load_bsdd(client: bsdd.Client, bsdd: tool.Bsdd) -> None:
    bsdd.clear_domains()
    if bsdd.should_load_preview_domains():
        dictionaries = bsdd.get_dictionaries(client)
    else:
        dictionaries = bsdd.get_dictionaries(client, "Active")
    bsdd.create_dictionaries(dictionaries)


def search_class(keyword: str, client: bsdd.Client, bsdd: tool.Bsdd) -> int:
    bsdd.clear_classes()
    related_entities = bsdd.get_related_ifc_entities()
    active_dictionary_uri = bsdd.get_active_dictionary_uri()
    classes = bsdd.search_class(client, keyword, [active_dictionary_uri], related_entities)
    bsdd.create_classes(classes)
    return len(classes)


def set_active_bsdd_dictionary(name: str, uri: str, bsdd: tool.Bsdd) -> None:
    bsdd.set_active_bsdd(name, uri)
