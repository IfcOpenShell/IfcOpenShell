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
    def __init__(self, file, shape_representation=None, styles=None, should_use_presentation_style_assignment=False):
        """Assigns a style directly to an object representation

        A style may either be assigned directly to an object's representation,
        or to a material which is then associated with the object. If both
        exist, then the style assigned directly to the object's representation
        takes precedence. It is recommended to use materials and assign styles
        to materials. However, sometimes you may want to assign colours directly
        to the object representation as an override. This API function provides
        that capability.

        If you want to assign styles to a material instead (recommended), then
        please see ifcopenshell.api.style.assign_material_style.

        :param shape_representation: The IfcShapeRepresentation of the object
            that you want to assign styles to. This implicitly defines the
            context at which the styles should be used.
        :type shape_representation: ifcopenshell.entity_instance.entity_instance
        :param styles: A list of presentation styles, typically IfcSurfaceStyle.
            The number of items in the list should correlate with the number of
            items in the shape_representation's Items attribute. If you have
            more items than styles, the last style is used.
        :type styles: list[ifcopenshell.entity_instance.entity_instance]
        :param should_use_presentation_style_assignment: This is a technical
            detail to accomodate a bug in Revit. This should always be left as
            the default of False, unless you are finding that colours aren't
            showing up in Revit. In that case, set it to True, but keep in mind
            that this is no longer a valid IFC. Blame Autodesk.
        :type should_use_presentation_style_assignment: bool
        :return: None
        :rtype: None

        Example:

        .. code:: python

            # A model context is needed to store 3D geometry
            model3d = ifcopenshell.api.run("context.add_context", model, context_type="Model")

            # Specifically, we want to store body geometry
            body = ifcopenshell.api.run("context.add_context", model,
                context_type="Model", context_identifier="Body", target_view="MODEL_VIEW", parent=model3d)

            # Let's create a new wall. The wall does not have any geometry yet.
            wall = ifcopenshell.api.run("root.create_entity", model, ifc_class="IfcWall")

            # Let's use the "3D Body" representation we created earlier to add a
            # new wall-like body geometry, 5 meters long, 3 meters high, and
            # 200mm thick
            representation = ifcopenshell.api.run("geometry.add_wall_representation", model,
                context=body, length=5, height=3, thickness=0.2)

            # Assign our new body geometry back to our wall
            ifcopenshell.api.run("geometry.assign_representation", model,
                product=wall, representation=representation)

            # Place our wall at the origin
            ifcopenshell.api.run("geometry.edit_object_placement", model, product=wall)

            # Create a new surface style
            style = ifcopenshell.api.run("style.add_style", model)

            # Create a simple grey shading colour and transparency.
            ifcopenshell.api.run("style.add_surface_style", model,
                style=style, ifc_class="IfcSurfaceStyleShading", attributes={
                    "SurfaceColour": { "Name": None, "Red": 0.5, "Green": 0.5, "Blue": 0.5 },
                    "Transparency": 0., # 0 is opaque, 1 is transparent
                })

            # Now specifically our wall only will be coloured grey.
            ifcopenshell.api.run("style.assign_representation_styles", model,
                shape_representation=representation, styles=[style])
        """
        self.file = file
        self.settings = {
            "shape_representation": shape_representation,
            "styles": styles or [],
            "should_use_presentation_style_assignment": should_use_presentation_style_assignment,
        }

    def execute(self):
        if not self.settings["styles"]:
            return []
        self.results = []
        for element in self.file.traverse(self.settings["shape_representation"]):
            if not element.is_a("IfcShapeRepresentation"):
                continue
            for item in element.Items:
                if not item.is_a("IfcGeometricRepresentationItem"):
                    continue
                if self.settings["styles"]:
                    # If there are more items than styles, fallback to using the last style
                    style = self.settings["styles"].pop(0)
                name = style.Name
                if self.file.schema == "IFC2X3" or self.settings["should_use_presentation_style_assignment"]:
                    style_assignment = self.file.createIfcPresentationStyleAssignment([style])
                    self.results.append(self.file.createIfcStyledItem(item, [style_assignment], name))
                else:
                    self.results.append(self.file.createIfcStyledItem(item, [style], name))
        return self.results
