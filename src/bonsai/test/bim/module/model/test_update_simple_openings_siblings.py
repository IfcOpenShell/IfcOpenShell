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

import json
from pathlib import Path

import bpy
import ifcopenshell
import ifcopenshell.api.aggregate
import ifcopenshell.api.context
import ifcopenshell.api.feature
import ifcopenshell.api.geometry
import ifcopenshell.api.material
import ifcopenshell.api.pset
import ifcopenshell.api.root
import ifcopenshell.api.spatial
import ifcopenshell.api.type
import ifcopenshell.api.unit
import ifcopenshell.geom
import ifcopenshell.guid
import ifcopenshell.util.element
import ifcopenshell.util.placement
import ifcopenshell.util.representation
import ifcopenshell.util.shape
import ifcopenshell.util.shape_builder
import numpy as np
import pytest

import bonsai.tool as tool
from test.bim.bootstrap import NewFile

pytestmark = pytest.mark.model

LINING = {
    "LiningDepth": 0.06,
    "LiningThickness": 0.06,
    "LiningOffset": 0.0,
    "LiningToPanelOffsetX": 0.025,
    "LiningToPanelOffsetY": 0.025,
}
PANEL = [{"FrameDepth": 0.035, "FrameThickness": 0.035}]


def _add_window(f, body, storey, wall, name, x, width, height, opening_dz=0.0):
    window = ifcopenshell.api.root.create_entity(f, ifc_class="IfcWindow", name=name)
    ifcopenshell.api.spatial.assign_container(f, relating_structure=storey, products=[window])
    matrix = np.eye(4)
    matrix[:3, 3] = [x, 0.0, 0.9]
    ifcopenshell.api.geometry.edit_object_placement(f, product=window, matrix=matrix)
    representation = ifcopenshell.api.geometry.add_window_representation(
        f,
        context=body,
        overall_height=height,
        overall_width=width,
        partition_type="SINGLE_PANEL",
        lining_properties=LINING,
        panel_properties=PANEL,
    )
    window.Representation = f.createIfcProductDefinitionShape(Representations=[representation])
    window.OverallWidth, window.OverallHeight = width, height
    data = {
        "window_type": "SINGLE_PANEL",
        "overall_height": height,
        "overall_width": width,
        "lining_properties": {
            "lining_depth": 0.06,
            "lining_thickness": 0.06,
            "lining_offset": 0.0,
            "lining_to_panel_offset_x": 0.025,
            "lining_to_panel_offset_y": 0.025,
        },
        "panel_properties": {
            "frame_depth": [0.035] * 3,
            "frame_thickness": [0.035] * 3,
        },
    }
    pset = ifcopenshell.api.pset.add_pset(f, product=window, name="BBIM_Window")
    ifcopenshell.api.pset.edit_pset(f, pset=pset, properties={"Data": json.dumps(data)})
    opening = ifcopenshell.api.root.create_entity(f, ifc_class="IfcOpeningElement", name=name + "-OPENING")
    opening_matrix = matrix.copy()
    opening_matrix[2, 3] += opening_dz
    ifcopenshell.api.geometry.edit_object_placement(f, product=opening, matrix=opening_matrix)
    builder = ifcopenshell.util.shape_builder.ShapeBuilder(f)
    profile = builder.rectangle(size=np.array([width, 1.2]), position=np.array([0.0, -0.45]))
    solid = builder.extrude(profile, magnitude=height, position=np.array([0.0, 0.0, 0.0]))
    ifcopenshell.api.geometry.assign_representation(
        f, product=opening, representation=builder.get_representation(body, [solid])
    )
    ifcopenshell.api.feature.add_feature(f, feature=opening, element=wall)
    ifcopenshell.api.feature.add_filling(f, opening=opening, element=window)
    return window


def _build_model(filepath: Path) -> None:
    f = ifcopenshell.file(schema="IFC4X3")
    project = ifcopenshell.api.root.create_entity(f, ifc_class="IfcProject", name="Project")
    ifcopenshell.api.unit.assign_unit(f, length={"is_metric": True, "raw": "METERS"})
    model = ifcopenshell.api.context.add_context(f, context_type="Model")
    body = ifcopenshell.api.context.add_context(
        f,
        context_type="Model",
        context_identifier="Body",
        target_view="MODEL_VIEW",
        parent=model,
    )
    site = ifcopenshell.api.root.create_entity(f, ifc_class="IfcSite", name="Site")
    building = ifcopenshell.api.root.create_entity(f, ifc_class="IfcBuilding", name="Building")
    storey = ifcopenshell.api.root.create_entity(f, ifc_class="IfcBuildingStorey", name="Storey")
    ifcopenshell.api.aggregate.assign_object(f, relating_object=project, products=[site])
    ifcopenshell.api.aggregate.assign_object(f, relating_object=site, products=[building])
    ifcopenshell.api.aggregate.assign_object(f, relating_object=building, products=[storey])
    for element in (site, building, storey):
        ifcopenshell.api.geometry.edit_object_placement(f, product=element)

    material = ifcopenshell.api.material.add_material(f, name="Masonry")
    layer_set = ifcopenshell.api.material.add_material_set(f, name="W300", set_type="IfcMaterialLayerSet")
    ifcopenshell.api.material.add_layer(f, layer_set=layer_set, material=material).LayerThickness = 0.3
    wall_type = ifcopenshell.api.root.create_entity(f, ifc_class="IfcWallType", name="W300")
    ifcopenshell.api.material.assign_material(f, products=[wall_type], material=layer_set)
    wall = ifcopenshell.api.root.create_entity(f, ifc_class="IfcWall", name="WALL")
    ifcopenshell.api.type.assign_type(f, related_objects=[wall], relating_type=wall_type)
    ifcopenshell.api.geometry.edit_object_placement(f, product=wall)
    ifcopenshell.api.spatial.assign_container(f, relating_structure=storey, products=[wall])
    wall_representation = ifcopenshell.api.geometry.add_wall_representation(
        f, context=body, length=6.0, height=3.0, thickness=0.3
    )
    ifcopenshell.api.geometry.assign_representation(f, product=wall, representation=wall_representation)

    window_type = ifcopenshell.api.root.create_entity(f, ifc_class="IfcWindowType", name="Universal")
    type_representation = ifcopenshell.api.geometry.add_window_representation(
        f,
        context=body,
        overall_height=1.2,
        overall_width=1.0,
        partition_type="SINGLE_PANEL",
        lining_properties=LINING,
        panel_properties=PANEL,
    )
    ifcopenshell.api.geometry.assign_representation(f, product=window_type, representation=type_representation)
    window_a = _add_window(f, body, storey, wall, "FENS-A", 1.0, 1.4, 1.2, opening_dz=-0.07)
    window_b = _add_window(f, body, storey, wall, "FENS-B", 3.5, 0.6, 0.8)
    f.createIfcRelDefinesByType(ifcopenshell.guid.new(), None, None, None, [window_a, window_b], window_type)
    f.write(str(filepath))


def _opening_width(window: ifcopenshell.entity_instance) -> float | None:
    opening = window.FillsVoids[0].RelatingOpeningElement
    if not (
        representation := ifcopenshell.util.representation.get_representation(opening, "Model", "Body", "MODEL_VIEW")
    ):
        return None
    shape = ifcopenshell.geom.create_shape(ifcopenshell.geom.settings(), representation)
    return ifcopenshell.util.shape.get_x(shape)


def _opening_z(window: ifcopenshell.entity_instance) -> float:
    opening = window.FillsVoids[0].RelatingOpeningElement
    return ifcopenshell.util.placement.get_local_placement(opening.ObjectPlacement)[2][3]


class TestUpdateSimpleOpeningsSiblings(NewFile):
    def _edit_window_b_width(
        self, tmp_path: Path, width: float, share_type_geometry: bool = False
    ) -> tuple[ifcopenshell.entity_instance, ...]:
        filepath = tmp_path / "siblings.ifc"
        _build_model(filepath)
        bpy.ops.bim.load_project(filepath=str(filepath))
        f = tool.Ifc.get()
        window_a, window_b = (next(w for w in f.by_type("IfcWindow") if w.Name == n) for n in ("FENS-A", "FENS-B"))
        if share_type_geometry:
            window_type = ifcopenshell.util.element.get_type(window_a)
            for window in (window_a, window_b):
                ifcopenshell.api.type.map_type_representations(f, related_object=window, relating_type=window_type)
        obj = tool.Ifc.get_object(window_b)
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        bpy.ops.bim.enable_editing_window()
        tool.Model.get_window_props(obj).overall_width = width
        bpy.ops.bim.finish_editing_window()
        return window_a, window_b

    def test_sibling_opening_keeps_its_geometry(self, tmp_path):
        window_a, window_b = self._edit_window_b_width(tmp_path, 0.7)
        assert _opening_width(window_a) == pytest.approx(1.4)

    def test_edited_window_opening_follows_the_edit(self, tmp_path):
        window_a, window_b = self._edit_window_b_width(tmp_path, 0.7)
        assert _opening_width(window_b) == pytest.approx(0.7)

    def test_sibling_opening_placement_is_untouched(self, tmp_path):
        window_a, window_b = self._edit_window_b_width(tmp_path, 0.7)
        assert _opening_z(window_a) == pytest.approx(0.83)

    def test_sibling_sharing_the_type_geometry_follows_the_edit(self, tmp_path):
        window_a, window_b = self._edit_window_b_width(tmp_path, 0.7, share_type_geometry=True)
        assert _opening_width(window_a) == pytest.approx(0.7)
