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
from typing import Any, Optional, Literal


SURFACE_STYLE_TYPES = Literal[
    "IfcSurfaceStyleShading",
    "IfcSurfaceStyleRendering",
    "IfcSurfaceStyleWithTextures",
    "IfcSurfaceStyleLighting",
    "IfcSurfaceStyleRefraction",
    "IfcExternallyDefinedSurfaceStyle",
]


def add_surface_style(
    file: ifcopenshell.file,
    style: ifcopenshell.entity_instance,
    ifc_class: SURFACE_STYLE_TYPES = "IfcSurfaceStyleShading",
    attributes: Optional[dict[str, Any]] = None,
) -> ifcopenshell.entity_instance:
    """Adds a new presentation item to a surface style

    A surface style can have multiple different types of presentation items
    assigned to it:

    - Shading, this is the simplest item, which defines a single basic
      colour and transparency that can be used to display the object on a
      screen. It is an indicative colour of what the object would be in real
      life. It is commonly incorrectly abused to colour code systems for MEP
      equipment or object types for structural steel. If you just want to
      give something a colour, this is what you need.
    - Rendering, this is an advanced extension of shading, which includes
      the definition of a shader for a rendering engine. You may select the
      reflectance / lighting model such as PHYSICAL, for PBR style
      rendering, or FLAT, for flat shading, or PHONG for older biased
      rendering workflows. Based on the chosen lighting model, you may then
      specify the appropriate colour maps, such as diffuse colours,
      specularity, emissive component, etc. These lighting models are fully
      compatible with glTF and X3D. This should be used if your model is
      prepared to be rendered by a rendering engine which is compatible with
      glTF / X3D shader descriptions. If you are doing archviz or 3D
      rendering, this is what you need.
    - Textures, this is a special type of Rendering presentation item that
      uses image textures instead of single colours. Textures may be either
      mapped using a bounding box stretch mapping, or with UV coordinates
      for mesh-like geometry.
    - Lighting, this is used to define photometrically accurate colour
      parameters used in lighting simulation. If you are a simulationist,
      this is what you need.
    - Reflectance, this is a special type of Lighting presentation item
      which includes some lesser used photometric properties, typically
      required for advanced materials like glazing.
    - External, this is for any other surface style defined using an
      external URI. This is relevant if you are using a third-party non-glTF
      compatible shader definition such as for Cycles, Renderman, V-Ray,
      etc, or a complex lighting simulation definition, such as for
      Radiance.

    Shading is sufficient for the majority of basic models.

    The attributes you specify will depend on the type of presentation item
    you are adding. An example is shown below, but for full details please
    refer to the IFC documentation.

    :param style: The IfcSurfaceStyle you want to add to presentation item
        to. See ifcopenshell.api.style.add_style.
    :param ifc_class: Choose from IfcSurfaceStyleShading,
        IfcSurfaceStyleRendering, IfcSurfaceStyleWithTextures,
        IfcSurfaceStyleLighting, IfcSurfaceStyleReflectance, or
        IfcExternallyDefinedSurfaceStyle.
    :param attributes: a dictionary of attribute names and values.
    :return: The newly created presentation item based on the provided
        ifc_class.

    Example:

    .. code:: python

        # Create a new surface style
        style = ifcopenshell.api.style.add_style(model)

        # Create a simple shading colour and transparency.
        ifcopenshell.api.style.add_surface_style(model,
            style=style, ifc_class="IfcSurfaceStyleShading", attributes={
                "SurfaceColour": { "Name": None, "Red": 1.0, "Green": 0.8, "Blue": 0.8 },
                "Transparency": 0., # 0 is opaque, 1 is transparent
            })

        # Alternatively, create a rendering style.
        ifcopenshell.api.style.add_surface_style(model,
            style=style, ifc_class="IfcSurfaceStyleRendering", attributes={
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
    attributes = attributes or {}
    style_item = file.create_entity(ifc_class)
    ifcopenshell.api.style.edit_surface_style(file, style=style_item, attributes=attributes)
    styles: list[ifcopenshell.entity_instance]
    styles = list(style.Styles or [])

    select_class = ifc_class
    if select_class == "IfcSurfaceStyleRendering":
        select_class = "IfcSurfaceStyleShading"
    duplicate_items = [s for s in styles if s.is_a(select_class)]
    for duplicate_item in duplicate_items:
        ifcopenshell.api.style.remove_surface_style(file, style=duplicate_item)

    styles = list(style.Styles or [])
    styles.append(style_item)
    style.Styles = styles
    return style_item
