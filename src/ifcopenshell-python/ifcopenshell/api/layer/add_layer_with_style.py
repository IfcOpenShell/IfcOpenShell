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
from typing import Union, Literal, Sequence

IfcLogical = Union[bool, Literal["UNKNOWN"]]


def add_layer_with_style(
    file: ifcopenshell.file,
    name: str = "Unnamed",
    on: IfcLogical = "UNKNOWN",
    frozen: IfcLogical = "UNKNOWN",
    blocked: IfcLogical = "UNKNOWN",
    styles: Sequence[ifcopenshell.entity_instance] = (),
) -> ifcopenshell.entity_instance:
    """Adds a new layer with style

    :param name: The name of the layer.
    :param on: Whether layer is visible.
    :param frozen:
    :param blocked: Whether layer elements are blocked from manipulation.
    :param styles: Styles to be used as default for representation item.
    :return: The newly created IfcPresentationLayerWithStyle element

    Example:

        ifcopenshell.api.layer.add_layer_with_style(
            model,
            name="AI-WALL-FULL-DIMS-N",
            on=True,
            frozen=False,
            blocked=False,
            stlyes=[curve_style]
        )
    """
    return file.create_entity(
        "IfcPresentationLayerWithStyle",
        Name=name,
        LayerOn=on,
        LayerFrozen=frozen,
        LayerBlocked=blocked,
        LayerStyles=styles,
    )
