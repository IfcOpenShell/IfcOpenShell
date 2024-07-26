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

import ifcopenshell.util.representation


def assign_profile(
    file: ifcopenshell.file, material_profile: ifcopenshell.entity_instance, profile: ifcopenshell.entity_instance
) -> None:
    """Changes the profile curve of a material profile item in a profile set

    In addition to changing the profile curve, it will also change the
    profile curve used in any body representation extrusions.

    :param material_profile: The IfcMaterialProfile to change the profile
        curve of. See ifcopenshell.api.material.add_profile to see how to
        create profiles.
    :type material_profile: ifcopenshell.entity_instance
    :param profile: The IfcProfileDef to set the profile item's curve to.
    :type profile: ifcopenshell.entity_instance
    :return: None
    :rtype: None

    Example:

    .. code:: python

        # Let's imagine we have a steel I-beam. Notice we are assigning to
        # the type only, as all occurrences of that type will automatically
        # inherit the material.
        beam_type = ifcopenshell.api.root.create_entity(model, ifc_class="IfcBeamType", name="B1")

        # First, let's create a material set. This will later be assigned
        # to our beam type element.
        material_set = ifcopenshell.api.material.add_profile_set(model,
            name="B1", set_type="IfcMaterialProfileSet")

        # Create a steel material.
        steel = ifcopenshell.api.material.add_material(model, name="ST01", category="steel")

        # Create an I-beam profile curve. Notice how we name our profiles
        # based on standardised steel profile names.
        hea100 = usecase.file.create_entity(
            "IfcIShapeProfileDef", ProfileName="HEA100", ProfileType="AREA",
            OverallWidth=100, OverallDepth=96, WebThickness=5, FlangeThickness=8, FilletRadius=12,
        )

        # Define that steel material and cross section as a single profile
        # item. If this were a composite beam, we might add multiple profile
        # items instead, but this is rarely the case in most construction.
        profile_item = ifcopenshell.api.material.add_profile(model,
            profile_set=material_set, material=steel, profile=hea100)

        # Great! Let's assign our material set to our beam type.
        ifcopenshell.api.material.assign_material(model, products=[beam_type], material=material_set)

        # Let's create an occurrence of this beam.
        beam = ifcopenshell.api.root.create_entity(model, ifc_class="IfcBeam", name="B1.01")
        ifcopenshell.api.material.assign_material(model,
            products=[beam], type="IfcMaterialProfileSetUsage")

        # Let's give a 1000mm long beam body representation.
        body = ifcopenshell.api.geometry.add_profile_representation(
            context=body_context, profile=hea100, depth=1000)
        ifcopenshell.api.geometry.assign_representation(model, product=beam, representation=body)
        ifcopenshell.api.geometry.edit_object_placement(model, product=beam)

        # Now let's change the profile to a HEA200 standard profile instead.
        # This will automatically change the body representation that we
        # just added as well to a HEA200 profile.
        hea200 = usecase.file.create_entity(
            "IfcIShapeProfileDef", ProfileName="HEA200", ProfileType="AREA",
            OverallWidth=200, OverallDepth=190, WebThickness=6.5, FlangeThickness=10, FilletRadius=18,
        )
        ifcopenshell.api.material.assign_profile(model, material_profile=profile_item, profile=hea200)
    """
    usecase = Usecase()
    usecase.file = file
    usecase.settings = {"material_profile": material_profile, "profile": profile}
    return usecase.execute()


class Usecase:
    file: ifcopenshell.file

    def execute(self) -> None:
        # TODO: handle composite profiles
        old_profile = self.settings["material_profile"].Profile
        self.settings["material_profile"].Profile = self.settings["profile"]
        for profile_set in self.settings["material_profile"].ToMaterialProfileSet:
            for inverse in self.file.get_inverse(profile_set):
                if not inverse.is_a("IfcMaterialProfileSetUsage"):
                    continue
                if self.file.schema == "IFC2X3":
                    for rel in self.file.get_inverse(inverse):
                        if not rel.is_a("IfcRelAssociatesMaterial"):
                            continue
                        for element in rel.RelatedObjects:
                            self.change_profile(element)
                else:
                    for rel in inverse.AssociatedTo:
                        for element in rel.RelatedObjects:
                            self.change_profile(element)

        if old_profile and len(self.file.get_inverse(old_profile)) == 0:
            # TODO: check remove deep
            self.file.remove(old_profile)

    def change_profile(self, element: ifcopenshell.entity_instance) -> None:
        representation = ifcopenshell.util.representation.get_representation(element, "Model", "Body", "MODEL_VIEW")
        if not representation:
            return
        for subelement in self.file.traverse(representation):
            if subelement.is_a("IfcSweptAreaSolid"):
                subelement.SweptArea = self.settings["profile"]
