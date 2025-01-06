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

import ifcopenshell.api.root
import ifcopenshell.util.element


def remove_opening(file: ifcopenshell.file, opening: ifcopenshell.entity_instance) -> None:
    """Remove an opening

    Fillings are retained as orphans. Voided elements remain. Openings
    cannot exist by themselves, so not only is the opening relationship
    removed, the opening is also removed.

    :param opening: The IfcOpeningElement to remove.
    :type opening: ifcopenshell.entity_instance
    :return: None
    :rtype: None

    Example:

    .. code:: python

        # Create an oprhaned opening. Note that an orphaned opening is
        # invalid, as an opening can only exist when voiding another
        # element.
        opening = ifcopenshell.api.root.create_entity(model, ifc_class="IfcOpeningElement")

        # Remove it. This brings us back to a valid model.
        ifcopenshell.api.void.remove_opening(model, opening=opening)
    """
    settings = {"opening": opening}

    for rel in settings["opening"].VoidsElements:
        history = rel.OwnerHistory
        file.remove(rel)
        if history:
            ifcopenshell.util.element.remove_deep2(file, history)
    if settings["opening"].is_a("IfcOpeningElement"):
        for rel in settings["opening"].HasFillings:
            history = rel.OwnerHistory
            file.remove(rel)
            if history:
                ifcopenshell.util.element.remove_deep2(file, history)
    ifcopenshell.api.root.remove_product(file, product=settings["opening"])
