# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2021-2022 Dion Moult <dion@thinkmoult.com>, Yassine Oualid <yassine@sigmadimensions.com>
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
import ifcopenshell.api.nest
import ifcopenshell.api.owner
import ifcopenshell.util.element


def change_nest(
    file: ifcopenshell.file, item: ifcopenshell.entity_instance, new_parent: ifcopenshell.entity_instance
) -> None:
    """Assigns a cost item to a new parent cost item"""
    if not item.Nests:
        return
    nests = item.Nests[0]
    related_objects = list(nests.RelatedObjects)
    related_objects.remove(item)
    if related_objects:
        nests.RelatedObjects = related_objects
        ifcopenshell.api.owner.update_owner_history(file, element=nests)
    else:
        history = nests.OwnerHistory
        file.remove(nests)
        if history:
            ifcopenshell.util.element.remove_deep2(file, history)
    ifcopenshell.api.nest.assign_object(file, related_objects=[item], relating_object=new_parent)
