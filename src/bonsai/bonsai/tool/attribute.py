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
import bpy
import bonsai.core.tool
import bonsai.bim.helper as helper
import bonsai.tool as tool
import ifcopenshell
from typing import (
    Any,
    Optional,
    Union,
    Literal,
    TypeVar,
    TYPE_CHECKING,
    assert_never,
)

if TYPE_CHECKING:
    from bonsai.bim.module.attribute.prop import BIMAttributeProperties, BIMExplorerProperties

    T = TypeVar("T")


class Attribute(bonsai.core.tool.Attribute):
    @classmethod
    def get_explorer_props(cls) -> BIMExplorerProperties:
        assert (scene := bpy.context.scene)
        return scene.BIMExplorerProperties  # pyright: ignore[reportAttributeAccessIssue]

    @classmethod
    def refresh_uilist_entities(cls) -> None:
        props = cls.get_explorer_props()
        props.entities.clear()
        ifc_file = tool.Ifc.get()
        for element in ifc_file.by_type(props.ifc_class):
            entity = props.entities.add()
            entity.name = str(element)
            entity.ifc_definition_id = element.id()

    @classmethod
    def enable_editing_entity(cls, entity: ifcopenshell.entity_instance) -> None:
        props = cls.get_explorer_props()
        props.editing_entity_id = entity.id()

    @classmethod
    def disable_editing_entity(cls) -> None:
        props = cls.get_explorer_props()
        props.entity_attributes.clear()
        props.property_unset("editing_entity_id")

    @classmethod
    def import_entity_attributes(cls, entity: ifcopenshell.entity_instance) -> None:
        props = cls.get_explorer_props()
        helper.import_attributes(entity.is_a(), props.entity_attributes, entity.get_info())

    @classmethod
    def export_entity_attributes(cls) -> dict[str, Any]:
        props = cls.get_explorer_props()
        attributes = helper.export_attributes(props.entity_attributes)
        return attributes
