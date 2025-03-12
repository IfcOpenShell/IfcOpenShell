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
import ifcopenshell.geom
import ifcopenshell.util.representation
import ifcopenshell.util.shape
from ifcopenshell.geom import ShapeType
from typing import Any


def edit_profile_usage(
    file: ifcopenshell.file, usage: ifcopenshell.entity_instance, attributes: dict[str, Any]
) -> None:
    """Edits the attributes of an IfcMaterialProfileSetUsage

    This is typically used to change the cardinal point of the profile.
    The cardinal point represents whether the profile is extruded along the
    center of the axis line, at a corner, at a shear center, at the bottom,
    top, etc.

    For more information about the attributes and data types of an
    IfcMaterialProfileSetUsage, consult the IFC documentation.

    :param usage: The IfcMaterialProfileSetUsage entity you want to edit
    :param attributes: a dictionary of attribute names and values.
    :return: None

    Example:

    .. code:: python

        # Let's imagine we have a steel I-beam. Notice we are assigning to
        # the type only, as all occurrences of that type will automatically
        # inherit the material.
        beam_type = ifcopenshell.api.root.create_entity(model, ifc_class="IfcBeamType", name="B1")

        # First, let's create a material set. This will later be assigned
        # to our beam type element.
        material_set = ifcopenshell.api.material.add_material_set(model,
            name="B1", set_type="IfcMaterialProfileSet")

        # Create a steel material.
        steel = ifcopenshell.api.material.add_material(model, name="ST01", category="steel")

        # Create an I-beam profile curve. Notice how we name our profiles
        # based on standardised steel profile names.
        hea100 = model.create_entity(
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
        rel = ifcopenshell.api.material.assign_material(model, material=material_set,
            products=[beam], type="IfcMaterialProfileSetUsage")

        # Let's give a 1000mm long beam body representation.
        body = ifcopenshell.api.geometry.add_profile_representation(
            context=body_context, profile=hea100, depth=1000)
        ifcopenshell.api.geometry.assign_representation(model, product=beam, representation=body)
        ifcopenshell.api.geometry.edit_object_placement(model, product=beam)

        # Let's change the cardinal point to be the top center of the axis
        # line. This is represented by the number "8". Consult the IFC
        # documentation for all the numbers you can use.
        ifcopenshell.api.material.edit_profile_usage(model,
            usage=rel.RelatingMaterial, attributes={"CardinalPoint": 8})
    """
    usecase = Usecase()

    usecase.file = file
    return usecase.execute(usage, attributes)


class Usecase:
    file: ifcopenshell.file

    def execute(self, usage: ifcopenshell.entity_instance, attributes: dict[str, Any]) -> None:
        self.usage = usage
        self.attributes = attributes
        self.cardinal_point = attributes.get("CardinalPoint")
        if self.cardinal_point and self.cardinal_point != usage.CardinalPoint:
            self.update_cardinal_point()

        for name, value in attributes.items():
            setattr(usage, name, value)

    def update_cardinal_point(self):
        material_set = self.usage.ForProfileSet
        self.profile = material_set.CompositeProfile
        if not self.profile and material_set.MaterialProfiles:
            self.profile = material_set.MaterialProfiles[0].Profile
        if not self.profile:
            return

        self.position = self.calculate_position()

        if self.file.schema == "IFC2X3":
            for rel in self.file.get_inverse(self.usage):
                if not rel.is_a("IfcRelAssociatesMaterial"):
                    continue
                for element in rel.RelatedObjects:
                    self.update_representation(element)
        else:
            for rel in self.usage.AssociatedTo:
                for element in rel.RelatedObjects:
                    self.update_representation(element)

    def calculate_position(self):
        self.dummy = ifcopenshell.file(schema=self.file.schema)
        dummy_profile = self.dummy.add(self.profile)
        # We clear all radiuses so that we can calculate geometric centroid easily
        for i, attribute in enumerate(dummy_profile):
            name = dummy_profile.attribute_name(i)
            if "Radius" in name and name != "RoundingRadius":
                dummy_profile[i] = None
        dummy_solid = self.dummy.create_entity(
            "IfcExtrudedAreaSolid",
            **{
                "SweptArea": dummy_profile,
                "ExtrudedDirection": self.dummy.createIfcDirection((0.0, 0.0, 1.0)),
                "Depth": 1,
            }
        )
        self.settings_2d = ifcopenshell.geom.settings()
        self.settings_2d.set("dimensionality", ifcopenshell.ifcopenshell_wrapper.CURVES_SURFACES_AND_SOLIDS)
        shape = ifcopenshell.geom.create_shape(self.settings_2d, dummy_solid)

        # NOTE: points do not need unit conversion
        # as dummy file is inherently using project units.
        if self.cardinal_point == 1:
            return self.get_bottom_left(shape)
        elif self.cardinal_point == 2:
            return self.get_bottom_centre(shape)
        elif self.cardinal_point == 3:
            return self.get_bottom_right(shape)
        elif self.cardinal_point == 4:
            return self.get_mid_depth_left(shape)
        elif self.cardinal_point == 5:
            return self.get_mid_depth_centre(shape)
        elif self.cardinal_point == 6:
            return self.get_mid_depth_right(shape)
        elif self.cardinal_point == 7:
            return self.get_top_left(shape)
        elif self.cardinal_point == 8:
            return self.get_top_centre(shape)
        elif self.cardinal_point == 9:
            return self.get_top_right(shape)

    def get_bottom_left(self, shape: ShapeType) -> ifcopenshell.entity_instance:
        width = ifcopenshell.util.shape.get_x(shape)
        height = ifcopenshell.util.shape.get_y(shape)
        return self.file.createIfcAxis2Placement3D(self.file.createIfcCartesianPoint((-width / 2, height / 2, 0.0)))

    def get_bottom_centre(self, shape: ShapeType) -> ifcopenshell.entity_instance:
        height = ifcopenshell.util.shape.get_y(shape)
        return self.file.createIfcAxis2Placement3D(self.file.createIfcCartesianPoint((0.0, height / 2, 0.0)))

    def get_bottom_right(self, shape: ShapeType) -> ifcopenshell.entity_instance:
        width = ifcopenshell.util.shape.get_x(shape)
        height = ifcopenshell.util.shape.get_y(shape)
        return self.file.createIfcAxis2Placement3D(self.file.createIfcCartesianPoint((width / 2, height / 2, 0.0)))

    def get_mid_depth_left(self, shape: ShapeType) -> ifcopenshell.entity_instance:
        width = ifcopenshell.util.shape.get_x(shape)
        return self.file.createIfcAxis2Placement3D(self.file.createIfcCartesianPoint((-width / 2, 0.0, 0.0)))

    def get_mid_depth_centre(self, shape: ShapeType) -> ifcopenshell.entity_instance:
        return self.file.createIfcAxis2Placement3D(self.file.createIfcCartesianPoint((0.0, 0.0, 0.0)))

    def get_mid_depth_right(self, shape: ShapeType) -> ifcopenshell.entity_instance:
        width = ifcopenshell.util.shape.get_x(shape)
        return self.file.createIfcAxis2Placement3D(self.file.createIfcCartesianPoint((width / 2, 0.0, 0.0)))

    def get_top_left(self, shape: ShapeType) -> ifcopenshell.entity_instance:
        width = ifcopenshell.util.shape.get_x(shape)
        height = ifcopenshell.util.shape.get_y(shape)
        return self.file.createIfcAxis2Placement3D(self.file.createIfcCartesianPoint((-width / 2, -height / 2, 0.0)))

    def get_top_centre(self, shape: ShapeType) -> ifcopenshell.entity_instance:
        height = ifcopenshell.util.shape.get_y(shape)
        return self.file.createIfcAxis2Placement3D(self.file.createIfcCartesianPoint((0.0, -height / 2, 0.0)))

    def get_top_right(self, shape: ShapeType) -> ifcopenshell.entity_instance:
        width = ifcopenshell.util.shape.get_x(shape)
        height = ifcopenshell.util.shape.get_y(shape)
        return self.file.createIfcAxis2Placement3D(self.file.createIfcCartesianPoint((width / 2, -height / 2, 0.0)))

    def update_representation(self, element: ifcopenshell.entity_instance) -> None:
        representation = ifcopenshell.util.representation.get_representation(element, "Model", "Body", "MODEL_VIEW")
        if not representation:
            return

        for subelement in self.file.traverse(representation):
            if subelement.is_a("IfcSweptAreaSolid") and subelement.SweptArea == self.profile:
                self.update_swept_area_solid(subelement)

    def update_swept_area_solid(self, element: ifcopenshell.entity_instance) -> None:
        element.Position = self.position
