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
import ifcopenshell.util.element


def remove_library(file: ifcopenshell.file, library: ifcopenshell.entity_instance) -> None:
    """Removes a library

    All references along with their relationships will also be removed. Any
    products which have relationships to this library will not be removed.

    :param library: The IfcLibraryInformation entity you want to remove
    :return: None

    Example:

    .. code:: python

        library = ifcopenshell.api.library.add_library(model, name="Brickschema")
        ifcopenshell.api.library.remove_library(model, library=library)
    """

    if file.schema != "IFC2X3":
        rels = []
        for reference in set(library.HasLibraryReferences):
            rels.extend(reference.LibraryRefForObjects)
            file.remove(reference)
        rels.extend(library.LibraryInfoForObjects)
        file.remove(library)
    else:
        for reference in set(library.LibraryReference or []):
            file.remove(reference)
        file.remove(library)
        # RelatingLibrary could either be library itself or library reference we removed
        rels = [rel for rel in file.by_type("IfcRelAssociatesLibrary") if rel.RelatingLibrary is None]

    for rel in rels:
        history = rel.OwnerHistory
        file.remove(rel)
        if history:
            ifcopenshell.util.element.remove_deep2(file, history)
