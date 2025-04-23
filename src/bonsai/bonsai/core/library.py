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
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    import bpy
    import ifcopenshell
    import bonsai.tool as tool


def add_library(ifc: tool.Ifc) -> ifcopenshell.entity_instance:
    return ifc.run("library.add_library", name="Unnamed")


def remove_library(ifc: tool.Ifc, library: ifcopenshell.entity_instance) -> None:
    ifc.run("library.remove_library", library=library)


def enable_editing_library_references(library_tool: tool.Library, library: ifcopenshell.entity_instance) -> None:
    library_tool.set_editing_mode("REFERENCES")
    library_tool.set_active_library(library)
    library_tool.import_references(library)


def disable_editing_library_references(library: tool.Library) -> None:
    library.clear_editing_mode()
    library.set_active_library(None)


def enable_editing_library(library: tool.Library) -> None:
    library.set_editing_mode("LIBRARY")
    library.import_library_attributes(library.get_active_library())


def disable_editing_library(library: tool.Library) -> None:
    library.set_editing_mode("REFERENCES")


def edit_library(ifc: tool.Ifc, library: tool.Library) -> None:
    library.set_editing_mode("REFERENCES")
    active_library = library.get_active_library()
    attributes = library.export_library_attributes()
    ifc.run("library.edit_library", library=active_library, attributes=attributes)
    library.import_references(active_library)


def add_library_reference(ifc: tool.Ifc, library: tool.Library) -> ifcopenshell.entity_instance:
    active_library = library.get_active_library()
    reference = ifc.run("library.add_reference", library=active_library)
    library.import_references(active_library)
    return reference


def remove_library_reference(ifc: tool.Ifc, library: tool.Library, reference: ifcopenshell.entity_instance) -> None:
    ifc.run("library.remove_reference", reference=reference)
    library.import_references(library.get_active_library())


def enable_editing_library_reference(library: tool.Library, reference: ifcopenshell.entity_instance) -> None:
    library.set_editing_mode("REFERENCE")
    library.set_active_reference(reference)
    library.import_reference_attributes(reference)


def disable_editing_library_reference(library: tool.Library) -> None:
    library.set_editing_mode("REFERENCES")


def edit_library_reference(ifc: tool.Ifc, library: tool.Library) -> None:
    library.set_editing_mode("REFERENCES")
    active_reference = library.get_active_reference()
    attributes = library.export_reference_attributes()
    ifc.run("library.edit_reference", reference=active_reference, attributes=attributes)
    library.import_references(library.get_active_library())


def assign_library_reference(ifc: tool.Ifc, obj: bpy.types.Object, reference: ifcopenshell.entity_instance) -> None:
    ifc.run("library.assign_reference", products=[ifc.get_entity(obj)], reference=reference)


def unassign_library_reference(ifc: tool.Ifc, obj: bpy.types.Object, reference: ifcopenshell.entity_instance) -> None:
    ifc.run("library.unassign_reference", products=[ifc.get_entity(obj)], reference=reference)
