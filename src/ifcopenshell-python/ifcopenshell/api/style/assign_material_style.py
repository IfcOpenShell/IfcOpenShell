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

import ifcopenshell
import ifcopenshell.api.style
import ifcopenshell.util.element
from typing import Any


def assign_material_style(
    file: ifcopenshell.file,
    material: ifcopenshell.entity_instance,
    style: ifcopenshell.entity_instance,
    context: ifcopenshell.entity_instance,
    should_use_presentation_style_assignment: bool = False,
) -> None:
    """Assigns a style to a material

    A style may either be assigned directly to an object's representation,
    or to a material which is then associated with the object. If both
    exist, then the style assigned directly to the object's representation
    takes precedence. It is recommended to use materials and assign styles
    to materials. This API function provides that capability.

    :param material: The IfcMaterial which you want to assign the style to.
    :type material: ifcopenshell.entity_instance
    :param style: The IfcPresentationStyle (typically IfcSurfaceStyle) that
        you want to assign to the material. This will then be applied to all
        objects that have that material.
    :type style: ifcopenshell.entity_instance
    :param context: The IfcGeometricRepresentationSubContext at which this
        style should be used. Typically this is the Model BODY context.
    :type context: ifcopenshell.entity_instance
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
        model3d = ifcopenshell.api.context.add_context(model, context_type="Model")

        # Specifically, we want to store body geometry
        body = ifcopenshell.api.context.add_context(model,
            context_type="Model", context_identifier="Body", target_view="MODEL_VIEW", parent=model3d)

        # Let's create a new wall. The wall does not have any geometry yet.
        wall = ifcopenshell.api.root.create_entity(model, ifc_class="IfcWall")

        # Let's use the "3D Body" representation we created earlier to add a
        # new wall-like body geometry, 5 meters long, 3 meters high, and
        # 200mm thick
        representation = ifcopenshell.api.geometry.add_wall_representation(model,
            context=body, length=5, height=3, thickness=0.2)

        # Assign our new body geometry back to our wall
        ifcopenshell.api.geometry.assign_representation(model,
            product=wall, representation=representation)

        # Place our wall at the origin
        ifcopenshell.api.geometry.edit_object_placement(model, product=wall)

        # Let's prepare a concrete material. Note that our concrete material
        # does not have any colours (styles) at this point.
        concrete = ifcopenshell.api.material.add_material(model, name="CON01", category="concrete")

        # Assign our concrete material to our wall
        ifcopenshell.api.material.assign_material(model,
            products=[wall], type="IfcMaterial", material=concrete)

        # Create a new surface style
        style = ifcopenshell.api.style.add_style(model)

        # Create a simple grey shading colour and transparency.
        ifcopenshell.api.style.add_surface_style(model,
            style=style, ifc_class="IfcSurfaceStyleShading", attributes={
                "SurfaceColour": { "Name": None, "Red": 0.5, "Green": 0.5, "Blue": 0.5 },
                "Transparency": 0., # 0 is opaque, 1 is transparent
            })

        # Now any element (like our wall) with a concrete material will have
        # a grey colour applied.
        ifcopenshell.api.style.assign_material_style(model, material=concrete, style=style, context=body)
    """
    usecase = Usecase()
    usecase.file = file
    usecase.settings = {
        "material": material,
        "style": style,
        "context": context,
        "should_use_presentation_style_assignment": should_use_presentation_style_assignment,
    }
    return usecase.execute()


class Usecase:
    file: ifcopenshell.file
    settings: dict[str, Any]

    def execute(self):
        self.style = self.settings["style"]
        if self.file.schema == "IFC2X3" or self.settings["should_use_presentation_style_assignment"]:
            self.style = self.file.createIfcPresentationStyleAssignment([self.settings["style"]])

        if self.settings["material"].HasRepresentation:
            self.modify_existing_definition_representation()
        else:
            self.create_new_definition_representation()

        # handle material constituents and shape aspects
        material_constituents_names = []
        for inverse in self.file.get_inverse(self.settings["material"]):
            if inverse.is_a("IfcMaterialConstituent") and inverse.Name:
                material_constituents_names.append(inverse.Name)
        if not material_constituents_names:
            return

        elements = ifcopenshell.util.element.get_elements_by_material(self.file, self.settings["material"])
        shape_aspects = []
        for element in elements:
            shape_aspects += ifcopenshell.util.element.get_shape_aspects(element)

        for shape_aspect in shape_aspects:
            if shape_aspect.Name not in material_constituents_names:
                continue

            for rep in shape_aspect.ShapeRepresentations:
                ifcopenshell.api.style.assign_representation_styles(
                    self.file, shape_representation=rep, styles=[self.style]
                )

    def modify_existing_definition_representation(self):
        # NOTE: while it's theoritically possible to have multiple styles per 1 material
        # (either with multiple styled items or multiple styles in 1 item)
        # we use an implicit convention that there is only 1 style per material.
        definition_representation = self.settings["material"].HasRepresentation[0]
        representation = self.get_styled_representation(definition_representation)
        if representation:
            items = list(representation.Items)
            new_items = []
            same_style_items = []
            for item in items:
                if not item.is_a("IfcStyledItem"):
                    continue
                if self.has_proposed_style(item):
                    return
                if self.has_same_style_type(item):
                    same_style_items.append(item)
                else:
                    new_items.append(item)
            item_to_reuse = same_style_items.pop(0) if same_style_items else None
            new_items.append(self.create_styled_item(item_to_reuse))
            representation.Items = new_items
            for item in same_style_items:
                if self.file.get_total_inverses(item) == 0:
                    self.file.remove(item)
        else:
            representations = list(definition_representation.Representations)
            representations.append(self.create_styled_representation())
            definition_representation.Representations = representations

    def has_proposed_style(self, styled_item: ifcopenshell.entity_instance) -> bool:
        style = self.settings["style"]
        styles = styled_item.Styles
        if style in styles:
            return True
        if self.file.schema != "IFC4X3":
            # IfcPresentationStyleAssignment is removed in IFC4X3
            for s in styles:
                if s.is_a("IfcPresentationStyleAssignment"):
                    if style in s.Styles:
                        return True
        return False

    def has_same_style_type(self, styled_item: ifcopenshell.entity_instance) -> bool:
        style = self.settings["style"]
        style_class = style.is_a()
        for s in styled_item.Styles:
            s_class = s.is_a()
            if s_class == style_class:
                return True
            elif s_class == "IfcPresentationStyleAssignment":
                for ss in s.Styles:
                    if ss.is_a() == style_class:
                        return True
        return False

    def create_new_definition_representation(self):
        representation = self.create_styled_representation()
        definition_representation = self.file.create_entity(
            "IfcMaterialDefinitionRepresentation",
            **{"Representations": [representation], "RepresentedMaterial": self.settings["material"]},
        )

    def get_styled_representation(self, definition_representation):
        representations = [
            r
            for r in definition_representation.Representations
            if r.is_a("IfcStyledRepresentation") and r.ContextOfItems == self.settings["context"]
        ]
        if representations:
            return representations[0]

    def create_styled_representation(self):
        return self.file.create_entity(
            "IfcStyledRepresentation",
            **{
                "ContextOfItems": self.settings["context"],
                "RepresentationIdentifier": self.settings["context"].ContextIdentifier,
                "Items": [self.create_styled_item()],
            },
        )

    def create_styled_item(self, reuse_item=None):
        if reuse_item is None:
            return self.file.create_entity(
                "IfcStyledItem", **{"Styles": [self.style], "Name": self.settings["style"].Name}
            )

        # IfcPresentationStyleAssignment we created end up not being used
        # TODO: do not create IfcPresentationStyleAssignment in the first place
        # as it might get removed
        if reuse_item.is_a("IfcPresentationStyleAssignment") and self.style.is_a("IfcPresentationStyleAssignment"):
            self.file.remove(self.style)
            self.style = reuse_item

        reuse_item.Styles = (self.settings["style"],)
        reuse_item.Name = self.settings["style"].Name
        return reuse_item
