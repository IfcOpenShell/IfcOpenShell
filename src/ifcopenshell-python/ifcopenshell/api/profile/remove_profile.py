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


class Usecase:
    def __init__(self, file, profile=None):
        """Removes a profile

        :param profile: The IfcProfileDef to remove.
        :type profile: ifcopenshell.entity_instance.entity_instance
        :return: None
        :rtype: None

        Example:

        .. code:: python

            circle = ifcopenshell.api.run("profile.add_parameterized_profile", model,
                ifc_class="IfcCircleProfileDef")
            circle = 1.
            ifcopenshell.api.run("profile.remove_profile", model, profile=circle)
        """
        self.file = file
        self.settings = {"profile": profile}

    def execute(self):
        self.file.remove(self.settings["profile"])
        # TODO: deep purge
