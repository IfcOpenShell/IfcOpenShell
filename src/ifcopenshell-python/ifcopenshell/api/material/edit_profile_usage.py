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


class Usecase:
    def __init__(self, file, usage=None, attributes=None):
        """Edits the attributes of an IfcMaterialProfileSetUsage

        This is typically used to change the cardinal point of the profile.
        The cardinal point represents whether the profile is extruded along the
        center of the axis line, at a corner, at a shear center, at the bottom,
        top, etc.

        For more information about the attributes and data types of an
        IfcMaterialProfileSetUsage, consult the IFC documentation.

        :param usage: The IfcMaterialProfileSetUsage entity you want to edit
        :type usage: ifcopenshell.entity_instance.entity_instance
        :param attributes: a dictionary of attribute names and values.
        :type attributes: dict, optional
        :return: None
        :rtype: None

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
            profile_item = ifcopenshell.api.run("material.add_profile", model,
                profile_set=material_set, material=steel, profile=hea100)

            # Great! Let's assign our material set to our beam type.
            ifcopenshell.api.run("material.assign_material", model, product=beam_type, material=material_set)

            # Let's create an occurrence of this beam.
            beam = ifcopenshell.api.run("root.create_entity", model, ifc_class="IfcBeam", name="B1.01")
            rel = ifcopenshell.api.run("material.assign_material", model,
                product=beam, type="IfcMaterialProfileSetUsage")

            # Let's give a 1000mm long beam body representation.
            body = ifcopenshell.api.run("geoemtry.add_profile_representation",
                context=body_context, profile=hea100, depth=1000)
            ifcopenshell.api.run("geometry.assign_representation", model, product=beam, representation=body)
            ifcopenshell.api.run("geometry.edit_object_placement", model, product=beam)

            # Let's change the cardinal point to be the top center of the axis
            # line. This is represented by the number "8". Consult the IFC
            # documentation for all the numbers you can use.
            ifcopenshell.api.run("material.edit_profile_usage", model,
                usage=rel.RelatingMaterial, attributes={"CardinalPoint": 8})
        """

        self.file = file
        self.settings = {"usage": usage, "attributes": attributes or {}}

    def execute(self):
        self.cardinal_point = self.settings["attributes"].get("CardinalPoint")
        if self.cardinal_point and self.cardinal_point != self.settings["usage"].CardinalPoint:
            self.update_cardinal_point()

        for name, value in self.settings["attributes"].items():
            setattr(self.settings["usage"], name, value)

    def update_cardinal_point(self):
        material_set = self.settings["usage"].ForProfileSet
        self.profile = material_set.CompositeProfile
        if not self.profile and material_set.MaterialProfiles:
            self.profile = material_set.MaterialProfiles[0].Profile
        if not self.profile:
            return

        self.position = self.calculate_position()

        if self.file.schema == "IFC2X3":
            for rel in self.file.get_inverse(self.settings["usage"]):
                if not rel.is_a("IfcRelAssociatesMaterial"):
                    continue
                for element in rel.RelatedObjects:
                    self.update_representation(element)
        else:
            for rel in self.settings["usage"].AssociatedTo:
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
        self.settings_2d.set(self.settings_2d.INCLUDE_CURVES, True)
        shape = ifcopenshell.geom.create_shape(self.settings_2d, dummy_solid)

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

    def get_bottom_left(self, shape):
        v = shape.verts
        x = [v[i] for i in range(0, len(v), 3)]
        y = [v[i + 1] for i in range(0, len(v), 3)]
        width = max(x) - min(x)
        height = max(y) - min(y)
        return self.file.createIfcAxis2Placement3D(self.file.createIfcCartesianPoint((-width / 2, height / 2, 0.0)))

    def get_bottom_centre(self, shape):
        v = shape.verts
        y = [v[i + 1] for i in range(0, len(v), 3)]
        height = max(y) - min(y)
        return self.file.createIfcAxis2Placement3D(self.file.createIfcCartesianPoint((0.0, height / 2, 0.0)))

    def get_bottom_right(self, shape):
        v = shape.verts
        x = [v[i] for i in range(0, len(v), 3)]
        y = [v[i + 1] for i in range(0, len(v), 3)]
        width = max(x) - min(x)
        height = max(y) - min(y)
        return self.file.createIfcAxis2Placement3D(self.file.createIfcCartesianPoint((width / 2, height / 2, 0.0)))

    def get_mid_depth_left(self, shape):
        v = shape.verts
        x = [v[i] for i in range(0, len(v), 3)]
        width = max(x) - min(x)
        return self.file.createIfcAxis2Placement3D(self.file.createIfcCartesianPoint((-width / 2, 0.0, 0.0)))

    def get_mid_depth_centre(self, shape):
        return self.file.createIfcAxis2Placement3D(self.file.createIfcCartesianPoint((0.0, 0.0, 0.0)))

    def get_mid_depth_right(self, shape):
        v = shape.verts
        x = [v[i] for i in range(0, len(v), 3)]
        width = max(x) - min(x)
        return self.file.createIfcAxis2Placement3D(self.file.createIfcCartesianPoint((width / 2, 0.0, 0.0)))

    def get_top_left(self, shape):
        v = shape.verts
        x = [v[i] for i in range(0, len(v), 3)]
        y = [v[i + 1] for i in range(0, len(v), 3)]
        width = max(x) - min(x)
        height = max(y) - min(y)
        return self.file.createIfcAxis2Placement3D(self.file.createIfcCartesianPoint((-width / 2, -height / 2, 0.0)))

    def get_top_centre(self, shape):
        v = shape.verts
        y = [v[i + 1] for i in range(0, len(v), 3)]
        height = max(y) - min(y)
        return self.file.createIfcAxis2Placement3D(self.file.createIfcCartesianPoint((0.0, -height / 2, 0.0)))

    def get_top_right(self, shape):
        v = shape.verts
        x = [v[i] for i in range(0, len(v), 3)]
        y = [v[i + 1] for i in range(0, len(v), 3)]
        width = max(x) - min(x)
        height = max(y) - min(y)
        return self.file.createIfcAxis2Placement3D(self.file.createIfcCartesianPoint((width / 2, -height / 2, 0.0)))

    def update_representation(self, element):
        representation = ifcopenshell.util.representation.get_representation(element, "Model", "Body", "MODEL_VIEW")
        if not representation:
            return

        for subelement in self.file.traverse(representation):
            if subelement.is_a("IfcSweptAreaSolid") and subelement.SweptArea == self.profile:
                self.update_swept_area_solid(subelement)

    def update_swept_area_solid(self, element):
        element.Position = self.position
