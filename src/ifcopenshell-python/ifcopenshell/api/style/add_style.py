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
from typing import Optional


def add_style(
    file: ifcopenshell.file, name: Optional[str] = None, ifc_class="IfcSurfaceStyle"
) -> ifcopenshell.entity_instance:
    """Add a new presentation style

    A presentation style is a container of visual settings (called
    presentation items) that affect the appearance of objects. There are
    four types of style:

    - Surface styles, which give 3D objects (which have surfaces / faces)
      their colours and textures. This is the most common type of style.
    - Curve styles, which give 2D and 3D curves, lines, polylines, their
      stroke thickness and colour.
    - Fill area styles, which gives 2D polygons and flat 3D planes their
      colours, hatch patterns, tiled patterns, and pattern scales.
    - Text styles, which gives text their font family, weight, variant,
      size, indentation, alignment, decoration, spacing, and transformation.

    Once you have created a presentation style object, you can further
    define the properties of your style using other API functions by adding
    presentation items, such as ifcopenshell.api.style.add_surface_style.

    :param name: The name of the style. Used to easily identify it using a
        style library.
    :type name: str,optional
    :param ifc_class: Choose from IfcSurfaceStyle, IfcCurveStyle,
        IfcFillAreaStyle, or IfcTextStyle.
    :type ifc_class: str
    :return: The newly created style element, based on the provided
        ifc_class.
    :rtype: ifcopenshell.entity_instance

    Example:

    .. code:: python

        # Create a new surface style
        style = ifcopenshell.api.style.add_style(model)
    """

    kwargs = {"Name": name}
    if ifc_class == "IfcSurfaceStyle":
        # Name is filled out because Revit treats this incorrectly as the material name
        kwargs["Side"] = "BOTH"

    return file.create_entity(ifc_class, **kwargs)
