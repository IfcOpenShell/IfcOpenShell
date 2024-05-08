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


def reorder_nesting(file, item=None, old_index=0, new_index=0) -> None:
    """Reorders an item in a nesting set"""
    settings = {"item": item, "old_index": old_index, "new_index": new_index}

    if not settings["item"].Nests:
        return
    nesting_set = settings["item"].Nests[0]
    if not settings["old_index"]:
        old_index = nesting_set.RelatedObjects.index(settings["item"])
    else:
        old_index = settings["old_index"]
    items = list(getattr(nesting_set, "RelatedObjects") or [])
    items.insert(settings["new_index"], items.pop(old_index))
    setattr(nesting_set, "RelatedObjects", items)
