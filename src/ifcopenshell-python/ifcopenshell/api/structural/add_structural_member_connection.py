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
import ifcopenshell.api


class Usecase:
    def __init__(self, file, relating_structural_member=None, related_structural_connection=None):
        """Relates a structural member and a structural connection

        :param relating_structural_member: The IfcStructuralMember to have a
            connection added to it.
        :type relating_structural_member: ifcopenshell.entity_instance.entity_instance
        :param related_structural_connection: The IfcStructuralConnection to add
            to the IfcStructuralMember.
        :type related_structural_connection: ifcopenshell.entity_instance.entity_instance
        :return: The IfcRelConnectsStructuralMember relationship
        :rtype: ifcopenshell.entity_instance.entity_instance
        """
        self.file = file
        self.settings = {
            "relating_structural_member": relating_structural_member,
            "related_structural_connection": related_structural_connection,
        }

    def execute(self):
        for connection in self.settings["related_structural_connection"].ConnectsStructuralMembers or []:
            if connection.RelatingStructuralMember == self.settings["relating_structural_member"]:
                return
        rel = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcRelConnectsStructuralMember")
        rel.RelatingStructuralMember = self.settings["relating_structural_member"]
        rel.RelatedStructuralConnection = self.settings["related_structural_connection"]
        return rel
