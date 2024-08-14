# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2023 Dion Moult <dion@thinkmoult.com>
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

import bpy
import bonsai.tool as tool


def refresh():
    ConstraintsData.is_loaded = False
    ObjectConstraintsData.is_loaded = False


class ConstraintsData:
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        cls.data = {"total_objectives": cls.total_objectives()}
        cls.is_loaded = True

    @classmethod
    def total_objectives(cls):
        return len(tool.Ifc.get().by_type("IfcObjective"))


class ObjectConstraintsData:
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        cls.data = {"constraints": cls.constraints()}
        cls.is_loaded = True

    @classmethod
    def constraints(cls):
        results = []
        element = tool.Ifc.get_entity(bpy.context.active_object)
        for rel in element.HasAssociations or []:
            if rel.is_a("IfcRelAssociatesConstraint"):
                constraint = rel.RelatingConstraint
                results.append({"id": constraint.id(), "type": constraint.is_a(), "name": constraint.Name or "Unnamed"})
        return results
