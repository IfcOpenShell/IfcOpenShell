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


def reorder_nesting(
    file: ifcopenshell.file, item: ifcopenshell.entity_instance, old_index: int = 0, new_index: int = 0
) -> None:
    """Reorders an item in a nesting set"""
    if not item.Nests:
        return
    nesting_set = item.Nests[0]
    if not old_index:
        old_index = nesting_set.RelatedObjects.index(item)
    items = list(getattr(nesting_set, "RelatedObjects") or [])
    items.insert(new_index, items.pop(old_index))
    setattr(nesting_set, "RelatedObjects", items)
