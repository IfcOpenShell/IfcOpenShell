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
    def __init__(self, file, profile_set=None, material=None, profile=None):
        """Add a new profile item to a profile set

        A profile item in a profile set represents an extruded 2D profile curve
        that is extruded along the axis of the element. Most commonly there will
        only be a single profile item in a profile set. For example, a beam will
        have a material profile set containing a single profile item, which may
        have a steel material and a I-beam shaped profile curve.

        Note that the "profile item" represents a single extrusion in the
        profile set, whereas the "profile curve" represents a 2D curve used by a
        "profile item".

        In some cases, a profiled element (i.e. beam, column) may be a composite
        beam or column and include multiple extrusions. This is rare. The order
        of the profiles does not matter.

        :param profile_set: The IfcMaterialProfileSet that the profile is part of. The
            profile set represents a group of profile items. See
            ifcopenshell.api.material.add_material_set for more information on
            how to add a profile set.
        :type profile_set: ifcopenshell.entity_instance.entity_instance
        :param material: The IfcMaterial that the profile item is made out of.
        :type material: ifcopenshell.entity_instance.entity_instance
        :param profile: The IfcProfileDef that represents the 2D cross section
            of the the profile item.
        :type profile: ifcopenshell.entity_instance.entity_instance
        :return: The newly created IfcMaterialProfile
        :rtype: ifcopenshell.entity_instance.entity_instance

        Example:

        .. code:: python

            # Let's imagine we have a steel I-beam. Notice we are assigning to
            # the type only, as all occurrences of that type will automatically
            # inherit the material.
            beam_type = ifcopenshell.api.run("root.create_entity", model, ifc_class="IfcBeamType", name="B1")

            # First, let's create a material set. This will later be assigned
            # to our beam type element.
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

            # Define that steel material and cross section as a single profile
            # item. If this were a composite beam, we might add multiple profile
            # items instead, but this is rarely the case in most construction.
            ifcopenshell.api.run("material.add_profile", model,
                profile_set=material_set, material=steel, profile=hea100)

            # Great! Let's assign our material set to our beam type.
            ifcopenshell.api.run("material.assign_material", model, product=beam_type, material=material_set)
        """
        self.file = file
        self.settings = {"profile_set": profile_set, "material": material, "profile": profile}

    def execute(self):
        profiles = list(self.settings["profile_set"].MaterialProfiles or [])
        profile = self.file.create_entity("IfcMaterialProfile")
        if self.settings["material"]:
            profile.Material = self.settings["material"]
        if self.settings["profile"]:
            profile.Profile = self.settings["profile"]
        profiles.append(profile)
        self.settings["profile_set"].MaterialProfiles = profiles
        return profile
