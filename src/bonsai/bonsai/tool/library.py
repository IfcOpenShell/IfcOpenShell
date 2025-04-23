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
import ifcopenshell
import bpy
import bonsai.bim.helper
import bonsai.core.tool
import bonsai.tool as tool
from typing import Literal, Any, Union, TYPE_CHECKING

if TYPE_CHECKING:
    from bonsai.bim.module.library.prop import BIMLibraryProperties


class Library(bonsai.core.tool.Library):
    @classmethod
    def get_library_props(cls) -> BIMLibraryProperties:
        return bpy.context.scene.BIMLibraryProperties

    @classmethod
    def clear_editing_mode(cls) -> None:
        cls.get_library_props().editing_mode = "NONE"

    @classmethod
    def export_library_attributes(cls) -> dict[str, Any]:
        props = cls.get_library_props()
        return bonsai.bim.helper.export_attributes(props.library_attributes)

    @classmethod
    def export_reference_attributes(cls) -> dict[str, Any]:
        props = cls.get_library_props()
        return bonsai.bim.helper.export_attributes(props.reference_attributes)

    @classmethod
    def get_active_library(cls) -> ifcopenshell.entity_instance:
        props = cls.get_library_props()
        return tool.Ifc.get().by_id(props.active_library_id)

    @classmethod
    def get_active_reference(cls) -> ifcopenshell.entity_instance:
        props = cls.get_library_props()
        return tool.Ifc.get().by_id(props.active_reference_id)

    @classmethod
    def import_library_attributes(cls, library: ifcopenshell.entity_instance) -> None:
        props = cls.get_library_props()
        props.library_attributes.clear()
        bonsai.bim.helper.import_attributes2(library, props.library_attributes)

    @classmethod
    def import_reference_attributes(cls, reference: ifcopenshell.entity_instance) -> None:
        props = cls.get_library_props()
        props.reference_attributes.clear()
        bonsai.bim.helper.import_attributes2(reference, props.reference_attributes)

    @classmethod
    def import_references(cls, library: ifcopenshell.entity_instance) -> None:
        props = cls.get_library_props()
        props.references.clear()
        if tool.Ifc.get_schema() == "IFC2X3":
            references = library.LibraryReference
        else:
            references = library.HasLibraryReferences
        for reference in references:
            new = props.references.add()
            new.ifc_definition_id = reference.id()
            new.name = reference.Name or "Unnamed"

    @classmethod
    def set_active_library(cls, library: Union[ifcopenshell.entity_instance, None]) -> None:
        props = cls.get_library_props()
        if library is None:
            props.active_library_id = 0
        else:
            props.active_library_id = library.id()

    @classmethod
    def set_active_reference(cls, reference: ifcopenshell.entity_instance) -> None:
        props = cls.get_library_props()
        props.active_reference_id = reference.id()

    @classmethod
    def set_editing_mode(cls, mode: Literal["LIBRARY", "REFERENCES", "REFERENCE"]) -> None:
        props = cls.get_library_props()
        props.editing_mode = mode
