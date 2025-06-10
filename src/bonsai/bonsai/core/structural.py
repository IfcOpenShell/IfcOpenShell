# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of Bonsai.
#
# Bonsai is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Bonsai is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Bonsai.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Union

if TYPE_CHECKING:
    import bpy
    import ifcopenshell
    import bonsai.tool as tool


def add_structural_analysis_model(ifc: tool.Ifc, structural: tool.Structural) -> ifcopenshell.entity_instance:
    result = ifc.run("structural.add_structural_analysis_model")
    structural.load_structural_analysis_models()
    structural.ensure_representation_contexts()
    return result


def assign_structural_analysis_model(
    ifc: tool.Ifc,
    products: list[ifcopenshell.entity_instance],
    structural_analysis_model: ifcopenshell.entity_instance,
) -> None:
    ifc.run(
        "structural.assign_structural_analysis_model",
        products=products,
        structural_analysis_model=structural_analysis_model,
    )


def disable_editing_structural_analysis_model(structural: tool.Structural) -> None:
    structural.disable_editing_structural_analysis_model()


def disable_structural_analysis_model_editing_ui(structural: tool.Structural) -> None:
    structural.disable_structural_analysis_model_editing_ui()


def edit_structural_analysis_model(ifc: tool.Ifc, structural: tool.Structural) -> None:
    attributes = structural.get_structural_analysis_model_attributes()
    ifc.run(
        "structural.edit_structural_analysis_model",
        structural_analysis_model=structural.get_active_structural_analysis_model(),
        attributes=attributes,
    )
    structural.load_structural_analysis_models()
    structural.disable_editing_structural_analysis_model()


def enable_editing_structural_analysis_model(structural: tool.Structural, model: Union[int, None]) -> None:
    structural.enable_editing_structural_analysis_model(model)


def enable_structural_analysis_model_editing_ui(structural: tool.Structural) -> None:
    structural.enable_structural_analysis_model_editing_ui()


def load_structural_analysis_model_attributes(structural: tool.Structural, model: Union[int, None]) -> None:
    data = structural.get_ifc_structural_analysis_model_attributes(model)
    if data is None:
        return
    structural.load_structural_analysis_model_attributes(data)


def load_structural_analysis_models(structural: tool.Structural) -> None:
    structural.load_structural_analysis_models()
    structural.enable_structural_analysis_model_editing_ui()
    # structural.disable_editing_structural_analysis_model()


def remove_structural_analysis_model(ifc: tool.Ifc, structural: tool.Structural, model: int) -> None:
    ifc.run(
        "structural.remove_structural_analysis_model",
        structural_analysis_model=ifc.get().by_id(model),
    )
    structural.load_structural_analysis_models()


def unassign_structural_analysis_model(
    ifc: tool.Ifc,
    products: list[ifcopenshell.entity_instance],
    structural_analysis_model: ifcopenshell.entity_instance,
) -> None:
    ifc.run(
        "structural.unassign_structural_analysis_model",
        products=products,
        structural_analysis_model=structural_analysis_model,
    )
