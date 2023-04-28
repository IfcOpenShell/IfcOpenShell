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
    def __init__(self, file, ifc_class=None):
        """Adds a new parameterised profile

        IFC offers parameterised profiles for common standardised hot roll
        steel sections and common concrete forms. A full list is available on
        the IFC documentation as subclasses of IfcParameterizedProfileDef.

        Currently, this API has no benefit over directly calling
        ifcopenshell.file.file.create_entity.

        :param ifc_class: The subclass of IfcParameterizedProfileDef that you'd
            like to create.
        :type ifc_class: str
        :return: The newly created element depending on the specified ifc_class.
        :rtype: ifcopenshell.entity_instance.entity_instance

        Example:

        .. code:: python

            circle = ifcopenshell.api.run("profile.add_parameterized_profile", model,
                ifc_class="IfcCircleProfileDef")
            circle.Radius = 1.
        """
        self.file = file
        self.settings = {"ifc_class": ifc_class}

    def execute(self):
        return self.file.create_entity(self.settings["ifc_class"])
