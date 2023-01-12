# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2021, 2022 Dion Moult <dion@thinkmoult.com>
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
    def __init__(self, file, profile=None, attributes=None, profile_def=None, material=None):
        """Edits the attributes of an IfcMaterialProfile

        For more information about the attributes and data types of an
        IfcMaterialProfile, consult the IFC documentation.

        :param profile: The IfcMaterialProfile entity you want to edit
        :type profile: ifcopenshell.entity_instance.entity_instance
        :param attributes: a dictionary of attribute names and values.
        :type attributes: dict, optional
        :param profile_def: The IfcProfileDef entity the profile curve should be
            extruded from.
        :type profile_def: ifcopenshell.entity_instance.entity_instance, optional
        :param material: The IfcMaterial entity you want to change the profile
            to be made from.
        :type material: ifcopenshell.entity_instance.entity_instance, optional
        :return: None
        :rtype: None

        Example:

        .. code:: python

            # Let's create a material set to store our profiles.
            material_set = ifcopenshell.api.run("material.add_profile_set", model,
                name="B1", set_type="IfcMaterialProfileSet")

            # Create a couple steel materials.
            steel1 = ifcopenshell.api.run("material.add_material", model, name="ST01", category="steel")
            steel2 = ifcopenshell.api.run("material.add_material", model, name="ST01", category="steel")

            # Create some I-shaped profiles. Notice how we name our profiles based
            # on standardised steel profile names.
            hea100 = self.file.create_entity(
                "IfcIShapeProfileDef", ProfileName="HEA100", ProfileType="AREA",
                OverallWidth=100, OverallDepth=96, WebThickness=5, FlangeThickness=8, FilletRadius=12,
            )
            hea200 = self.file.create_entity(
                "IfcIShapeProfileDef", ProfileName="HEA200", ProfileType="AREA",
                OverallWidth=200, OverallDepth=190, WebThickness=6.5, FlangeThickness=10, FilletRadius=18,
            )

            # Define that steel material and cross section as a single profile
            # item. If this were a composite beam, we might add multiple profile
            # items instead, but this is rarely the case in most construction.
            profile_item = ifcopenshell.api.run("material.add_profile", model,
                profile_set=material_set, material=steel1, profile=hea100)

            # Edit our profile item to use a HEA200 profile instead made out of
            # another type of steel.
            ifcopenshell.api.run("material.edit_profile", model,
                profile=profile_item, profile_def=hea200, material=steel2)
        """
        self.file = file
        self.settings = {
            "profile": profile,
            "attributes": attributes or {},
            "profile_def": profile_def,
            "material": material,
        }

    def execute(self):
        for name, value in self.settings["attributes"].items():
            setattr(self.settings["profile"], name, value)
        if self.settings["material"]:
            self.settings["profile"].Material = self.settings["material"]
        if self.settings["profile_def"]:
            self.settings["profile"].Profile = self.settings["profile_def"]
