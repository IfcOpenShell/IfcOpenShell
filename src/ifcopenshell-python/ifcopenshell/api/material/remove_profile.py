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
        """Removes a profile item from a profile set

        Note that it is invalid to have zero items in a set, so you should leave
        at least one profile to ensure a valid IFC dataset.

        :param profile: The IfcMaterialProfile entity you want to remove
        :type profile: ifcopenshell.entity_instance.entity_instance
        :return: None
        :rtype: None

        Example:

        .. code:: python

            # First, let's create a material set.
            material_set = ifcopenshell.api.run("material.add_profile_set", model,
                name="B1", set_type="IfcMaterialProfileSet")

            # Create a steel material.
            steel = ifcopenshell.api.run("material.add_material", model, name="ST01", category="steel")

            # Create an I-beam profile curve. Notice how we name our profiles
            # based on standardised steel profile names.
            hea100 = self.file.create_entity(
                "IfcIShapeProfileDef", ProfileName="HEA100", ProfileType="AREA",
                OverallWidth=100, OverallDepth=96, WebThickness=5, FlangeThickness=8, FilletRadius=12,
            )

            # Define that steel material and cross section as a single profile item.
            ifcopenshell.api.run("material.add_profile", model,
                profile_set=material_set, material=steel, profile=hea100)

            # Imagine a welded square along the length of the profile.
            welded_square = ifcopenshell.api.run("profile.add_arbitrary_profile", model,
                profile=[(.0025, .0025), (.0325, .0025), (.0325, -.0025), (.0025, -.0025), (.0025, .0025)])
            weld_profile = ifcopenshell.api.run("material.add_profile", model,
                profile_set=material_set, material=steel, profile=welded_square)

            # Let's remove our welded square.
            ifcopenshell.api.run("material.remove_profile", model, profile=weld_profile)
        """

        self.file = file
        self.settings = {"profile": profile}

    def execute(self):
        self.file.remove(self.settings["profile"])
        # TODO: deep purge
