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

"""Voids on IFC4 Reference View files.

A Reference View exporter writes the host body already cut and gives the
matching IfcOpeningElement a Reference representation only, so the importer
skips the booleans. An opening Bonsai authors is different: it carries a Body
representation and nothing has cut the host yet. Treating both the same made
a door's hole show in the session and vanish on reload, measured on
Perspective générique.ifc (6.527 m3 uncut, 6.200 m3 cut) and on
DigitalHub_FM-ARC_v2.ifc."""

import bpy
import ifcopenshell
import pytest

import bonsai.tool as tool
from bonsai.bim.module.model.wall import DumbWallGenerator
from test.bim.bootstrap import NewFile

pytestmark = pytest.mark.geometry

_files = []


def _host_with_opening(representation_identifier):
    ifc = ifcopenshell.file(schema="IFC4")
    _files.append(ifc)
    context = ifc.create_entity(
        "IfcGeometricRepresentationContext",
        ContextType="Model",
        CoordinateSpaceDimension=3,
    )
    wall = ifc.create_entity("IfcWall", GlobalId=ifcopenshell.guid.new())
    opening = ifc.create_entity("IfcOpeningElement", GlobalId=ifcopenshell.guid.new())
    if representation_identifier is not None:
        representation = ifc.create_entity(
            "IfcShapeRepresentation",
            ContextOfItems=context,
            RepresentationIdentifier=representation_identifier,
            RepresentationType="Tessellation",
            Items=[],
        )
        opening.Representation = ifc.create_entity("IfcProductDefinitionShape", Representations=[representation])
    ifc.create_entity(
        "IfcRelVoidsElement",
        GlobalId=ifcopenshell.guid.new(),
        RelatingBuildingElement=wall,
        RelatedOpeningElement=opening,
    )
    return wall


def test_body_opening_still_has_to_be_subtracted():
    from bonsai.bim.import_ifc import IfcImporter

    assert IfcImporter.has_subtractive_void(_host_with_opening("Body")) is True


def test_reference_only_opening_was_already_baked_in():
    from bonsai.bim.import_ifc import IfcImporter

    assert IfcImporter.has_subtractive_void(_host_with_opening("Reference")) is False


def test_opening_without_geometry_was_already_baked_in():
    from bonsai.bim.import_ifc import IfcImporter

    assert IfcImporter.has_subtractive_void(_host_with_opening(None)) is False


def test_host_without_openings_is_not_affected():
    from bonsai.bim.import_ifc import IfcImporter

    ifc = ifcopenshell.file(schema="IFC4")
    wall = ifc.create_entity("IfcWall", GlobalId=ifcopenshell.guid.new())
    assert IfcImporter.has_subtractive_void(wall) is False


def _classify(elements, *, reference_view, void_limit=30):
    """Run ``process_element_filter``'s void classification without Blender."""
    from bonsai.bim.import_ifc import IfcImporter

    importer = IfcImporter.__new__(IfcImporter)
    importer.elements = set(elements)
    importer.ifc_import_settings = type(
        "Settings", (), {"void_limit": void_limit, "is_reference_view": reference_view}
    )()
    IfcImporter.classify_voided_elements(importer)
    return importer


def test_baked_voids_are_not_offered_for_recut():
    wall = _host_with_opening("Reference")
    importer = _classify([wall], reference_view=True)
    assert importer.baked_void_elements == {wall}
    assert importer.gross_elements == set()
    assert wall not in importer.elements


def test_excessive_voids_are_still_offered_for_recut():
    wall = _host_with_opening("Body")
    importer = _classify([wall], reference_view=True, void_limit=0)
    assert importer.gross_elements == {wall}
    assert importer.baked_void_elements == set()
    assert wall not in importer.elements


def test_authored_void_on_a_reference_view_host_is_cut_normally():
    wall = _host_with_opening("Body")
    importer = _classify([wall], reference_view=True)
    assert importer.elements == {wall}
    assert importer.gross_elements == set()
    assert importer.baked_void_elements == set()


class TestReferenceViewLoad(NewFile):
    def test_an_authored_door_stays_cut_and_nothing_is_offered_for_recut(self, tmp_path):
        tool.Project.get_project_props().export_schema = "IFC4"
        bpy.ops.bim.create_project()
        ifc = tool.Ifc.get()
        bpy.ops.bim.add_default_type(ifc_element_type="IfcWallType")
        polyline_props = tool.Model.get_polyline_props()
        polyline_data = polyline_props.insertion_polyline.add()
        for co in ((0.0, 0.0, 0.0), (5.0, 0.0, 0.0)):
            point = polyline_data.polyline_points.add()
            point.x, point.y, point.z = co
        walls, _ = DumbWallGenerator(ifc.by_type("IfcWallType")[-1]).generate(insertion_type="POLYLINE")
        polyline_props.insertion_polyline.clear()
        wall_obj = walls[0]["obj"] if isinstance(walls[0], dict) else walls[0]
        rprops = tool.Root.get_root_props()
        rprops.ifc_product = "IfcElementType"
        rprops.ifc_class = "IfcDoorType"
        rprops.ifc_predefined_type = "DOOR"
        rprops.representation_template = "DOOR"
        bpy.ops.bim.add_element()
        tool.Blender.select_and_activate_single_object(bpy.context, wall_obj)
        bpy.context.scene.cursor.location = (2.0, 0.0, 0.0)
        bpy.ops.bim.add_occurrence(relating_type_id=ifc.by_type("IfcDoorType")[-1].id())
        wall = tool.Ifc.get_entity(wall_obj)
        assert wall.HasOpenings
        ifc.header.file_description.description = ("ViewDefinition [ReferenceView_V1.2]",)
        path = tmp_path / "reference_view.ifc"
        ifc.write(str(path))

        bpy.ops.bim.load_project(filepath=str(path))
        wall_obj = tool.Ifc.get_object(tool.Ifc.get().by_type("IfcWall")[0])
        assert not tool.Project.get_project_props().pending_opening_recut
        assert len(wall_obj.data.vertices) > 8
