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

import ifcopenshell.api


class Usecase:
    def __init__(self, file, load_group=None):
        """Removes a structural load group

        :param load_group: The IfcStructuralLoadGroup to remove.
        :type load_group: ifcopenshell.entity_instance.entity_instance
        :return: None
        :rtype: None
        """
        self.file = file
        self.settings = {"load_group": load_group}

    def execute(self):
        # TODO: do a deep purge
        for inverse in self.file.get_inverse(self.settings["load_group"]):
            if inverse.is_a("IfcRelAssignsToGroup") and len(inverse.RelatedObjects) == 1:
                self.file.remove(inverse)
        self.file.remove(self.settings["load_group"])
