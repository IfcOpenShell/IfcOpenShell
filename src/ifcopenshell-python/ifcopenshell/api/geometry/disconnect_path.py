# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2022 Dion Moult <dion@thinkmoult.com>
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
import ifcopenshell.api
import ifcopenshell.util.element


def disconnect_path(file, **usecase_settings) -> None:
    settings = {
        "relating_element": None,
        "related_element": None,
        "element": None,
        "connection_type": None,
    }
    for key, value in usecase_settings.items():
        settings[key] = value

    if settings["connection_type"] and settings["element"]:
        connections = [
            r
            for r in settings["element"].ConnectedTo
            if r.is_a("IfcRelConnectsPathElements") and r.RelatingConnectionType == settings["connection_type"]
        ] + [
            r
            for r in settings["element"].ConnectedFrom
            if r.is_a("IfcRelConnectsPathElements") and r.RelatedConnectionType == settings["connection_type"]
        ]
    else:
        connections = [
            r
            for r in settings["relating_element"].ConnectedTo
            if r.is_a("IfcRelConnectsPathElements") and r.RelatedElement == settings["related_element"]
        ]

    for connection in set(connections):
        history = connection.OwnerHistory
        file.remove(connection)
        if history:
            ifcopenshell.util.element.remove_deep2(file, history)
