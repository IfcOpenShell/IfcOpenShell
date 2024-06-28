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
from typing import Any


def edit_surface_style(
    file: ifcopenshell.file, style: ifcopenshell.entity_instance, attributes: dict[str, Any]
) -> None:
    """Edits the attributes of an IfcPresentationItem

    For more information about the attributes and data types of an
    IfcPresentationItem, consult the IFC documentation.

    The IfcPresentationItem is expected to be one of IfcSurfaceStyleShading,
    IfcSurfaceStyleRendering, IfcSurfaceStyleWithTextures,
    IfcSurfaceStyleLighting, IfcSurfaceStyleReflectance, or
    IfcExternallyDefinedSurfaceStyle.

    To represent a colour, a nested dictionary should be used. See the
    example below.

    :param style: The IfcPresentationStyle entity you want to edit
    :type style: ifcopenshell.entity_instance
    :param attributes: a dictionary of attribute names and values.
    :type attributes: dict
    :return: None
    :rtype: None

    Example:

    .. code:: python

        # Create a new surface style
        style = ifcopenshell.api.style.add_style(model)

        # Create a blank rendering style.
        rendering = ifcopenshell.api.style.add_surface_style(model,
            style=style, ifc_class="IfcSurfaceStyleRendering")

        # Edit the attributes of the rendering style.
        ifcopenshell.api.style.edit_surface_style(model,
            style=rendering, attributes={
                # A surface colour and transparency is still supplied for
                # viewport display only. This will supersede the shading
                # presentation item.
                "SurfaceColour": { "Name": None, "Red": 1.0, "Green": 0.8, "Blue": 0.8 },
                "Transparency": 0., # 0 is opaque, 1 is transparent

                # NOTDEFINED is assumed to be a PHYSICAL (PBR) lighting
                # model. In IFC4X3, you may choose PHYSICAL directly.
                "ReflectanceMethod": "NOTDEFINED",

                # For PBR shading, you may specify these parameters:
                "DiffuseColour": { "Name": None, "Red": 0.9, "Green": 0.8, "Blue": 0.8 },
                "SpecularColour": 0.1, # Metallic factor
                "SpecularHighlight": {"SpecularRoughness": 0.5}, # Roughness factor
            })
    """
    usecase = Usecase()
    usecase.file = file
    usecase.settings = {"style": style, "attributes": attributes or {}}
    return usecase.execute()


class Usecase:
    def execute(self):
        attributes = {}
        for attribute in self.settings["style"].wrapped_data.declaration().as_entity().all_attributes():
            attribute_type = attribute.type_of_attribute()
            if attribute_type.as_aggregation_type() is None:
                attribute_type = attribute_type.declared_type().name()
            else:
                # doesn't have .declared_type()
                attribute_type = attribute_type.type_of_element()
            attributes[attribute.name()] = attribute_type

        for key, value in self.settings["attributes"].items():
            attribute_class = attributes.get(key)
            if attribute_class == "IfcColourRgb":
                self.edit_colour_rgb(key, value)
            elif key == "SpecularHighlight":
                self.edit_specular_highlight(value)
            elif attribute_class == "IfcColourOrFactor":
                self.edit_colour_or_factor(key, value)
            else:
                setattr(self.settings["style"], key, value)

    def edit_colour_rgb(self, name, value: dict):
        if (attribute := getattr(self.settings["style"], name)) is None:
            attribute = self.file.createIfcColourRgb()
            setattr(self.settings["style"], name, attribute)
        attribute.Name = value.get("Name", None)
        attribute.Red = value["Red"]
        attribute.Green = value["Green"]
        attribute.Blue = value["Blue"]

    def edit_colour_or_factor(self, name, value):
        if isinstance(value, dict):
            attribute = getattr(self.settings["style"], name)
            if not attribute or not attribute.is_a("IfcColourRgb"):
                colour = self.file.createIfcColourRgb(None, 0, 0, 0)
                setattr(self.settings["style"], name, colour)
                attribute = getattr(self.settings["style"], name)
            attribute[1] = value["Red"]
            attribute[2] = value["Green"]
            attribute[3] = value["Blue"]
        else:  # assume it's float value for IfcNormalisedRatioMeasure or None
            existing_value = getattr(self.settings["style"], name)
            if existing_value and existing_value.id():
                self.file.remove(existing_value)
            if value is not None:
                value = self.file.createIfcNormalisedRatioMeasure(value)
            setattr(self.settings["style"], name, value)

    def edit_specular_highlight(self, value):
        if value is None:
            self.settings["style"].SpecularHighlight = None
        elif value.get("IfcSpecularExponent", None):
            self.settings["style"].SpecularHighlight = self.file.createIfcSpecularExponent(value["IfcSpecularExponent"])
        elif value.get("IfcSpecularRoughness", None):
            self.settings["style"].SpecularHighlight = self.file.createIfcSpecularRoughness(
                value["IfcSpecularRoughness"]
            )
