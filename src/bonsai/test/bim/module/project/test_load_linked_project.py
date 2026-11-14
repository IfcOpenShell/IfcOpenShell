# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2026
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
#
# This file was generated with the assistance of an AI coding tool.

import bpy
import ifcopenshell.api.context
import ifcopenshell.api.geometry
import ifcopenshell.api.project
import ifcopenshell.api.root
import ifcopenshell.api.unit
import numpy as np
import pytest

from test.bim.bootstrap import NewFile

pytestmark = pytest.mark.project


def write_model(filepath: str, schema: str, ifc_classes: tuple[str, ...]) -> dict[str, str]:
    ifc = ifcopenshell.api.project.create_file(version=schema)
    ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcProject")
    ifcopenshell.api.unit.assign_unit(ifc)
    model = ifcopenshell.api.context.add_context(ifc, context_type="Model")
    body = ifcopenshell.api.context.add_context(
        ifc, context_type="Model", context_identifier="Body", target_view="MODEL_VIEW", parent=model
    )
    guids = {}
    for i, ifc_class in enumerate(ifc_classes):
        element = ifcopenshell.api.root.create_entity(ifc, ifc_class=ifc_class)
        representation = ifcopenshell.api.geometry.add_wall_representation(
            ifc, context=body, length=1.0, height=1.0, thickness=1.0
        )
        ifcopenshell.api.geometry.assign_representation(ifc, product=element, representation=representation)
        matrix = np.eye(4)
        matrix[0][3] = i * 2.0
        ifcopenshell.api.geometry.edit_object_placement(ifc, product=element, matrix=matrix, is_si=True)
        guids[ifc_class] = element.GlobalId
    ifc.write(filepath)
    return guids


def get_linked_guids() -> set[str]:
    return {guid for obj in bpy.data.objects if "guids" in obj for guid in obj["guids"]}


class TestLoadLinkedProject(NewFile):
    @pytest.mark.parametrize("schema", ("IFC4", "IFC4X3"))
    def test_the_default_query_keeps_surface_features_and_drops_other_features(self, tmp_path, schema):
        filepath = str(tmp_path / "model.ifc")
        guids = write_model(filepath, schema, ("IfcSlab", "IfcSurfaceFeature", "IfcOpeningElement"))
        bpy.ops.bim.load_linked_project(filepath=filepath)
        assert get_linked_guids() == {guids["IfcSlab"], guids["IfcSurfaceFeature"]}
