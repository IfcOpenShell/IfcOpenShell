# IfcPatch - IFC patching utility
# Copyright (C) 2024-2026 Bruno Postle <bruno@postle.net>
#
# This file is part of IfcPatch.
#
# IfcPatch is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# IfcPatch is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with IfcPatch.  If not, see <http://www.gnu.org/licenses/>.

from collections.abc import Sequence
from typing import Optional

import ifcopenshell
import ifcopenshell.api.aggregate
import ifcopenshell.api.context
import ifcopenshell.api.document
import ifcopenshell.api.geometry
import ifcopenshell.api.project
import ifcopenshell.api.pset
import ifcopenshell.api.root
import ifcopenshell.api.spatial
import ifcopenshell.api.unit
import ifcopenshell.geom
import ifcopenshell.util.element
import ifcopenshell.util.placement
import ifcopenshell.util.representation
import ifcopenshell.util.selector
import numpy as np
import pytest

import ifcpatch
import ifcpatch.recipes.GenerateGeneralArrangementDrawings as recipe
import test.bootstrap

RECIPE = "GenerateGeneralArrangementDrawings"

DEFAULT_ASSETS = {
    "Stylesheet": "drawings/assets/default.css",
    "Markers": "drawings/assets/markers.svg",
    "Symbols": "drawings/assets/symbols.svg",
    "Patterns": "drawings/assets/patterns.svg",
    "ShadingStyles": "drawings/assets/shading_styles.json",
}

# Normals of the building bbox faces that elevations are drawn of, in order
FACE_NORMALS = [[0.0, 1.0, 0.0], [0.0, -1.0, 0.0], [-1.0, 0.0, 0.0], [1.0, 0.0, 0.0]]


def run(file: ifcopenshell.file, *arguments) -> None:
    ifcpatch.execute({"file": file, "recipe": RECIPE, "arguments": list(arguments)})


# Model builders


def placement(
    file: ifcopenshell.file,
    relative_to: Optional[ifcopenshell.entity_instance] = None,
    rotation: float = 0.0,
    xyz: Sequence[float] = (0.0, 0.0, 0.0),
) -> ifcopenshell.entity_instance:
    """Create a local placement at xyz (project units), rotated about z by rotation degrees"""
    angle = np.radians(rotation)
    return file.createIfcLocalPlacement(
        relative_to,
        file.createIfcAxis2Placement3D(
            file.createIfcCartesianPoint([float(c) for c in xyz]),
            file.createIfcDirection((0.0, 0.0, 1.0)),
            file.createIfcDirection((float(np.cos(angle)), float(np.sin(angle)), 0.0)),
        ),
    )


def create_project(
    file: ifcopenshell.file, prefix: Optional[str] = None, imperial: bool = False, contexts: bool = True
) -> tuple[ifcopenshell.entity_instance, Optional[ifcopenshell.entity_instance]]:
    """Add a project with a length unit and, optionally, Model and Body contexts

    :param prefix: SI length unit prefix, such as "MILLI", or None for metres
    :param imperial: Use feet instead of an SI unit
    :return: (project, body context) tuple
    """
    project = ifcopenshell.api.root.create_entity(file, ifc_class="IfcProject")
    if imperial:
        unit = ifcopenshell.api.unit.add_conversion_based_unit(file, name="foot")
    else:
        unit = ifcopenshell.api.unit.add_si_unit(file, unit_type="LENGTHUNIT", prefix=prefix)
    ifcopenshell.api.unit.assign_unit(file, units=[unit])
    body = None
    if contexts:
        model = ifcopenshell.api.context.add_context(file, context_type="Model")
        body = ifcopenshell.api.context.add_context(
            file, context_type="Model", context_identifier="Body", target_view="MODEL_VIEW", parent=model
        )
    return project, body


def add_site(
    file: ifcopenshell.file, project: ifcopenshell.entity_instance, rotation: float = 0.0
) -> ifcopenshell.entity_instance:
    site = ifcopenshell.api.root.create_entity(file, ifc_class="IfcSite")
    ifcopenshell.api.aggregate.assign_object(file, relating_object=project, products=[site])
    site.ObjectPlacement = placement(file, None, rotation)
    return site


def add_building(
    file: ifcopenshell.file,
    parent: ifcopenshell.entity_instance,
    name: str = "Test Building",
    rotation: float = 0.0,
    xyz: Sequence[float] = (0.0, 0.0, 0.0),
) -> ifcopenshell.entity_instance:
    building = ifcopenshell.api.root.create_entity(file, ifc_class="IfcBuilding", name=name)
    ifcopenshell.api.aggregate.assign_object(file, relating_object=parent, products=[building])
    building.ObjectPlacement = placement(file, getattr(parent, "ObjectPlacement", None), rotation, xyz)
    return building


def add_storey(
    file: ifcopenshell.file, building: ifcopenshell.entity_instance, name: str = "Ground Floor"
) -> ifcopenshell.entity_instance:
    storey = ifcopenshell.api.root.create_entity(file, ifc_class="IfcBuildingStorey", name=name)
    ifcopenshell.api.aggregate.assign_object(file, relating_object=building, products=[storey])
    storey.ObjectPlacement = placement(file, building.ObjectPlacement)
    return storey


def add_wall(
    file: ifcopenshell.file,
    storey: ifcopenshell.entity_instance,
    xyz: Sequence[float] = (0.0, 0.0, 0.0),
    body: Optional[ifcopenshell.entity_instance] = None,
    rotation: float = 0.0,
    length: float = 5.0,
    thickness: float = 0.2,
) -> ifcopenshell.entity_instance:
    """Add a wall at xyz (project units), with a 3m high body if a context is given

    Body dimensions are in metres, converted to project units by the API.
    """
    wall = ifcopenshell.api.root.create_entity(file, ifc_class="IfcWall")
    ifcopenshell.api.spatial.assign_container(file, relating_structure=storey, products=[wall])
    wall.ObjectPlacement = placement(file, storey.ObjectPlacement, rotation, xyz)
    if body:
        representation = ifcopenshell.api.geometry.add_wall_representation(
            file, context=body, length=length, height=3.0, thickness=thickness
        )
        ifcopenshell.api.geometry.assign_representation(file, product=wall, representation=representation)
    return wall


def add_space(
    file: ifcopenshell.file,
    storey: ifcopenshell.entity_instance,
    body: ifcopenshell.entity_instance,
    name: str = "Kitchen",
    rotation: float = 0.0,
    xyz: Sequence[float] = (0.0, 0.0, 0.0),
    profile_points: Optional[list[tuple[float, float]]] = None,
) -> ifcopenshell.entity_instance:
    """Add a 4m x 2m x 3m space, or an extrusion of a closed profile 3m high"""
    space = ifcopenshell.api.root.create_entity(file, ifc_class="IfcSpace", name=name)
    ifcopenshell.api.aggregate.assign_object(file, relating_object=storey, products=[space])
    space.ObjectPlacement = placement(file, storey.ObjectPlacement, rotation, xyz)
    if profile_points:
        points = [file.createIfcCartesianPoint(p) for p in profile_points + profile_points[:1]]
        profile = file.createIfcArbitraryClosedProfileDef("AREA", None, file.createIfcPolyline(points))
        representation = ifcopenshell.api.geometry.add_profile_representation(
            file, context=body, profile=profile, depth=3.0
        )
    else:
        representation = ifcopenshell.api.geometry.add_wall_representation(
            file, context=body, length=4.0, height=3.0, thickness=2.0
        )
    ifcopenshell.api.geometry.assign_representation(file, product=space, representation=representation)
    return space


def create_model(file: ifcopenshell.file, building_name: str = "Test Building") -> ifcopenshell.entity_instance:
    """Add a metre project with one building, a "Ground Floor" storey and a 5m wall

    :return: The IfcProject
    """
    project, body = create_project(file)
    building = add_building(file, add_site(file, project), building_name)
    add_wall(file, add_storey(file, building), body=body)
    return project


def create_placed_walls(
    file: ifcopenshell.file, prefix: Optional[str] = None, imperial: bool = False
) -> ifcopenshell.entity_instance:
    """Add a project with a "Test Building" whose two walls have placements but no geometry

    The walls are at (1, 1, 0) and (10, 10, 3) in project units.

    :return: The IfcSite
    """
    project, _ = create_project(file, prefix=prefix, imperial=imperial)
    site = add_site(file, project)
    storey = add_storey(file, add_building(file, site))
    add_wall(file, storey, (1.0, 1.0, 0.0))
    add_wall(file, storey, (10.0, 10.0, 3.0))
    return site


def create_block(
    file: ifcopenshell.file,
    building_rotation: float = 0.0,
    site_rotation: float = 0.0,
    block_rotation: float = 0.0,
    true_north: Optional[tuple[float, float]] = None,
) -> ifcopenshell.entity_instance:
    """Add a metre model with a 10m x 6m x 3m block in a building "Block" at (100, 50, 0)

    The block, and a 4m x 2m "Hall" space, run along the storey's x axis.

    :param building_rotation: Building placement rotation relative to the site, in degrees
    :param site_rotation: Site placement rotation, in degrees
    :param block_rotation: Rotation of the block's own placement in the storey, in degrees
    :param true_north: Optional 2D TrueNorth direction ratios for the Model context
    :return: The IfcBuilding
    """
    project, body = create_project(file)
    if true_north:
        model = ifcopenshell.util.representation.get_context(file, "Model")
        model.TrueNorth = file.createIfcDirection([float(c) for c in true_north])
    site = add_site(file, project, site_rotation)
    building = add_building(file, site, "Block", building_rotation, (100.0, 50.0, 0.0))
    storey = add_storey(file, building)
    add_wall(file, storey, body=body, rotation=block_rotation, length=10.0, thickness=6.0)
    add_space(file, storey, body, name="Hall")
    return building


def create_twin_buildings(file: ifcopenshell.file) -> list[tuple]:
    """Add two buildings both named "Plot", with storeys "Ground A" and "Ground B" holding one wall each

    :return: List of (building, storey, wall) tuples
    """
    project, _ = create_project(file)
    site = add_site(file, project)
    plots = []
    for suffix, x in (("A", 0.0), ("B", 50.0)):
        building = add_building(file, site, "Plot")
        storey = add_storey(file, building, f"Ground {suffix}")
        plots.append((building, storey, add_wall(file, storey, (x, 1.0, 0.0))))
    return plots


def add_user_sheet(
    file: ifcopenshell.file, drawing_locations: list[str], purpose: str = "General Arrangement"
) -> ifcopenshell.entity_instance:
    """Add a sheet made by the user, holding drawings at the given locations"""
    sheet = ifcopenshell.api.document.add_information(file)
    ifcopenshell.api.document.edit_information(
        file,
        information=sheet,
        attributes={"Identification": "GA-101", "Name": "User GA", "Purpose": purpose, "Scope": "SHEET"},
    )
    for i, location in enumerate(drawing_locations):
        reference = ifcopenshell.api.document.add_reference(file, information=sheet)
        ifcopenshell.api.document.edit_reference(
            file,
            reference=reference,
            attributes={"Location": location, "Identification": str(i + 1), "Description": "DRAWING"},
        )
    return sheet


def set_documentation(file: ifcopenshell.file, project: ifcopenshell.entity_instance, properties: dict) -> None:
    pset = ifcopenshell.api.pset.add_pset(file, product=project, name="BBIM_Documentation")
    ifcopenshell.api.pset.edit_pset(file, pset=pset, properties=properties)


# Queries


def get_generated_drawings(file: ifcopenshell.file) -> list[ifcopenshell.entity_instance]:
    return [
        a
        for a in file.by_type("IfcAnnotation")
        if ifcopenshell.util.element.get_pset(a, "EPset_Drawing", "GeneratedBy") == "endrawing"
    ]


def get_labels(file: ifcopenshell.file) -> list[ifcopenshell.entity_instance]:
    return [
        a
        for a in file.by_type("IfcAnnotation")
        if ifcopenshell.util.element.get_pset(a, "EPset_Annotation", "GeneratedBy") == "endrawing"
    ]


def get_drawings(file: ifcopenshell.file) -> dict[str, ifcopenshell.entity_instance]:
    return {a.Name: a for a in file.by_type("IfcAnnotation") if a.ObjectType == "DRAWING"}


def get_drawing(file: ifcopenshell.file, name: str) -> ifcopenshell.entity_instance:
    return get_drawings(file)[name]


def get_drawing_reference(drawing: ifcopenshell.entity_instance) -> ifcopenshell.entity_instance:
    return next(r.RelatingDocument for r in drawing.HasAssociations if r.is_a("IfcRelAssociatesDocument"))


def get_drawing_location(drawing: ifcopenshell.entity_instance) -> str:
    """The location of the SVG that the drawing's document reference points at"""
    return get_drawing_reference(drawing).Location


def get_sheets(file: ifcopenshell.file) -> list[ifcopenshell.entity_instance]:
    return sorted((d for d in file.by_type("IfcDocumentInformation") if d.Scope == "SHEET"), key=lambda d: d[0] or "")


def get_sheets_by_id(file: ifcopenshell.file, identification: str) -> list[ifcopenshell.entity_instance]:
    return [d for d in file.by_type("IfcDocumentInformation") if d.Identification == identification]


def get_sheet_locations(file: ifcopenshell.file) -> dict[str, str]:
    """The LAYOUT and TITLEBLOCK locations of the only sheet"""
    [sheet] = get_sheets(file)
    return {r.Description: r.Location for r in sheet.HasDocumentReferences if r.Description != "DRAWING"}


def get_assets(drawing: ifcopenshell.entity_instance) -> dict[str, str]:
    pset = ifcopenshell.util.element.get_pset(drawing, "EPset_Drawing")
    return {name: pset[name] for name in DEFAULT_ASSETS}


def get_scales(file: ifcopenshell.file) -> dict[str, tuple[str, str]]:
    """{drawing name: (Scale, HumanScale)} for generated drawings"""
    scales = {}
    for drawing in get_generated_drawings(file):
        pset = ifcopenshell.util.element.get_pset(drawing, "EPset_Drawing")
        scales[drawing.Name] = (pset["Scale"], pset["HumanScale"])
    return scales


def is_elevation(drawing: ifcopenshell.entity_instance) -> bool:
    return ifcopenshell.util.element.get_pset(drawing, "EPset_Drawing", "TargetView") == "ELEVATION_VIEW"


def get_camera(drawing: ifcopenshell.entity_instance) -> tuple:
    """(location, axis, ref direction, block dimensions) of a drawing camera"""
    relative_placement = drawing.ObjectPlacement.RelativePlacement
    block = drawing.Representation.Representations[0].Items[0].TreeRootExpression
    return (
        np.array(relative_placement.Location.Coordinates),
        np.array(relative_placement.Axis.DirectionRatios),
        np.array(relative_placement.RefDirection.DirectionRatios),
        (block.XLength, block.YLength, block.ZLength),
    )


def get_axes(rotation: float) -> tuple[np.ndarray, np.ndarray]:
    angle = np.radians(rotation)
    return np.array([np.cos(angle), np.sin(angle), 0.0]), np.array([-np.sin(angle), np.cos(angle), 0.0])


class TestBasics(test.bootstrap.IFC4):
    def test_no_buildings_raises_error(self):
        create_project(self.file)
        with pytest.raises(ValueError, match="No IfcBuilding"):
            run(self.file)

    def test_no_model_context_raises_error(self):
        project, _ = create_project(self.file, contexts=False)
        add_building(self.file, project)
        with pytest.raises(ValueError, match="No Model context"):
            run(self.file)

    def test_generates_marked_drawings(self):
        create_model(self.file)
        run(self.file)
        assert get_generated_drawings(self.file)

    def test_rerun_keeps_counts(self):
        create_model(self.file)
        run(self.file)
        counts = (
            len(self.file.by_type("IfcAnnotation")),
            len(self.file.by_type("IfcGroup")),
            len(get_sheets(self.file)),
        )
        assert all(counts)

        run(self.file)

        assert counts == (
            len(self.file.by_type("IfcAnnotation")),
            len(self.file.by_type("IfcGroup")),
            len(get_sheets(self.file)),
        )

    def test_custom_scale(self):
        create_model(self.file)
        run(self.file, 50)
        assert ("1/50", "1:50") in get_scales(self.file).values()

    def test_scale_and_titleblock_as_strings_from_the_command_line(self):
        create_model(self.file)
        run(self.file, "48", "A1")
        assert set(get_scales(self.file).values()) == {("1/48", "1:48")}
        assert get_sheet_locations(self.file)["TITLEBLOCK"] == "layouts/titleblocks/A1.svg"

    def test_sheet_drawings_numbered_from_one(self):
        """Drawings on a sheet are numbered from 1, the industry convention"""
        create_model(self.file)
        run(self.file)
        [sheet] = get_sheets(self.file)
        numbers = [r.Identification for r in sheet.HasDocumentReferences if r.Description == "DRAWING"]
        assert sorted(numbers, key=int) == [str(i) for i in range(1, len(numbers) + 1)]

    def test_sheets_in_natural_order_of_building_names(self):
        project, _ = create_project(self.file)
        site = add_site(self.file, project)
        for name in ("Plot 10", "Plot 2", "Plot 1"):
            add_building(self.file, site, name)
        run(self.file)
        assert [(s.Identification, s.Name) for s in get_sheets(self.file)] == [
            ("A001", "Plot 1"),
            ("A002", "Plot 2"),
            ("A003", "Plot 10"),
        ]


class TestCleanup(test.bootstrap.IFC4):
    def test_manual_drawings_preserved(self):
        create_model(self.file)
        manual = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcAnnotation", name="Manual Drawing")
        manual.ObjectType = "DRAWING"
        for _ in range(2):
            run(self.file)
        assert manual in self.file.by_type("IfcAnnotation")

    def test_annotations_without_psets(self):
        create_model(self.file)
        orphan = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcAnnotation", name="Orphan")
        orphan.ObjectType = "DRAWING"
        run(self.file)
        assert get_generated_drawings(self.file)

    def test_repeated_runs_are_stable(self):
        create_model(self.file)
        for _ in range(3):
            run(self.file)
        counts = (len(self.file.by_type("IfcAnnotation")), len(self.file.by_type("IfcGroup")))
        run(self.file)
        assert (len(self.file.by_type("IfcAnnotation")), len(self.file.by_type("IfcGroup"))) == counts

    def test_repeated_runs_leave_no_orphans(self):
        """Drawing documents and references are removed with their drawings"""
        create_model(self.file)
        run(self.file)
        count = len(list(self.file))
        documents = len(self.file.by_type("IfcDocumentInformation"))
        run(self.file)
        assert len(self.file.by_type("IfcDocumentInformation")) == documents
        assert len(list(self.file)) == count

    def test_cleanup_removes_all_generated_entities(self):
        create_model(self.file)
        run(self.file)
        assert get_generated_drawings(self.file)
        assert [g for g in self.file.by_type("IfcGroup") if g.ObjectType == "DRAWING"]
        assert get_sheets(self.file)

        recipe.DrawingGenerator(self.file).cleanup_existing_drawings()

        assert not get_generated_drawings(self.file)
        assert not [g for g in self.file.by_type("IfcGroup") if g.ObjectType == "DRAWING"]
        assert not [d for d in self.file.by_type("IfcDocumentInformation") if d.Purpose == "General Arrangement"]

    def test_user_general_arrangement_sheet_preserved(self):
        """A user's sheet with the same Purpose, holding the user's drawing, survives"""
        create_model(self.file)
        add_user_sheet(self.file, ["drawings/USER PLAN.svg"])
        for _ in range(2):
            run(self.file)
        [sheet] = get_sheets_by_id(self.file, "GA-101")
        assert [r.Location for r in sheet.HasDocumentReferences] == ["drawings/USER PLAN.svg"]

    def test_empty_user_sheet_preserved(self):
        create_model(self.file)
        add_user_sheet(self.file, [])
        for _ in range(2):
            run(self.file)
        assert len(get_sheets_by_id(self.file, "GA-101")) == 1

    def test_sheet_mixing_user_and_generated_drawings_preserved(self):
        create_model(self.file)
        run(self.file)
        add_user_sheet(self.file, ["drawings/Test Building Ground Floor.svg", "drawings/USER PLAN.svg"])
        run(self.file)
        [sheet] = get_sheets_by_id(self.file, "GA-101")
        assert len(sheet.HasDocumentReferences) == 2
        assert len(get_sheets_by_id(self.file, "A001")) == 1

    def test_file_writes_after_cleanup(self, tmp_path):
        create_model(self.file)
        for _ in range(2):
            run(self.file)
        path = tmp_path / "cleanup.ifc"
        self.file.write(str(path))
        assert get_generated_drawings(ifcopenshell.open(str(path)))


class TestDocuments(test.bootstrap.IFC4):
    def parents(self) -> tuple[list, list]:
        documents = [
            d for d in self.file.by_type("IfcDocumentInformation") if d.Name == "DRAWINGS" and d.Scope == "DRAWINGS"
        ]
        groups = [g for g in self.file.by_type("IfcGroup") if g.Name == "DRAWINGS" and g.ObjectType == "DRAWINGS"]
        return documents, groups

    def test_drawings_nested_under_bonsai_parents(self):
        create_model(self.file)
        run(self.file)

        [parent_document], [parent_group] = self.parents()
        nested = {d for rel in parent_document.IsPointer for d in rel.RelatedDocuments}
        grouped = {g for rel in parent_group.IsGroupedBy for g in rel.RelatedObjects}
        drawings = get_generated_drawings(self.file)
        assert drawings
        for drawing in drawings:
            information = get_drawing_reference(drawing).ReferencedDocument
            assert information in nested
            assert information.Scope == "DRAWING"
            assert information.Name == drawing.Name
            # Nested documents aren't associated with the project directly
            assert not information.DocumentInfoForObjects
            group = next(r.RelatingGroup for r in drawing.HasAssignments if r.is_a("IfcRelAssignsToGroup"))
            assert group in grouped

    def test_bonsai_parents_reused_and_kept(self):
        """Existing parents are reused, and a Bonsai drawing's document under them survives cleanup"""
        create_model(self.file)
        parent = ifcopenshell.api.document.add_information(self.file)
        ifcopenshell.api.document.edit_information(
            self.file,
            information=parent,
            attributes={"Identification": "DRAWINGS", "Name": "DRAWINGS", "Scope": "DRAWINGS"},
        )
        user_drawing = ifcopenshell.api.document.add_information(self.file, parent=parent)
        ifcopenshell.api.document.edit_information(
            self.file,
            information=user_drawing,
            attributes={"Identification": "X", "Name": "USER SECTION", "Scope": "DRAWING"},
        )

        for _ in range(2):
            run(self.file)

        documents, groups = self.parents()
        assert documents == [parent]
        assert len(groups) == 1
        nested = {d for rel in parent.IsPointer for d in rel.RelatedDocuments}
        assert user_drawing in nested
        assert len(nested) == len(get_generated_drawings(self.file)) + 1

    def test_plan_context_registered_with_project(self):
        project = create_model(self.file)
        recipe.DrawingGenerator(self.file)
        plan = ifcopenshell.util.representation.get_context(self.file, "Plan")
        assert plan in project.RepresentationContexts


class TestDocumentsIFC2X3(test.bootstrap.IFC2X3):
    def test_ifc2x3_attribute_names(self, tmp_path):
        """IFC2X3 models get drawings and sheets, using IFC2X3 attribute names"""
        create_placed_walls(self.file)

        for _ in range(2):
            run(self.file)

        [sheet] = get_sheets(self.file)
        assert sheet.DocumentId == "A001"
        assert sheet.Purpose == "General Arrangement"
        drawings = get_generated_drawings(self.file)
        assert sorted(r.Name for r in sheet.DocumentReferences) == sorted(
            ["LAYOUT", "TITLEBLOCK"] + ["DRAWING"] * len(drawings)
        )
        for drawing in drawings:
            [information] = get_drawing_reference(drawing).ReferenceToDocument
            assert information.Name == drawing.Name
            assert information.Scope == "DRAWING"

        path = tmp_path / "ifc2x3.ifc"
        self.file.write(str(path))
        assert len(get_generated_drawings(ifcopenshell.open(str(path)))) == len(drawings)


class TestUnits(test.bootstrap.IFC4):
    @pytest.mark.parametrize(
        "prefix, imperial, scale",
        [(None, False, 1.0), ("MILLI", False, 0.001), (None, True, 0.3048)],
    )
    def test_unit_scale(self, prefix, imperial, scale):
        create_placed_walls(self.file, prefix=prefix, imperial=imperial)
        assert recipe.DrawingGenerator(self.file).unit_scale == pytest.approx(scale, rel=1e-4)

    @pytest.mark.parametrize("prefix, imperial, height", [("MILLI", False, 1800.0), (None, True, 1.8 / 0.3048)])
    def test_plan_camera_height_in_project_units(self, prefix, imperial, height):
        """The plan camera is 1.8m above the floor, in project units"""
        create_placed_walls(self.file, prefix=prefix, imperial=imperial)
        run(self.file)
        location = get_drawing(self.file, "Test Building Ground Floor").ObjectPlacement.RelativePlacement.Location
        assert location.Coordinates[2] == pytest.approx(height, rel=1e-3)

    def test_bbox_padding_in_millimetres(self):
        """The 2m padding is 2000mm, not 2mm"""
        create_placed_walls(self.file, prefix="MILLI")
        generator = recipe.DrawingGenerator(self.file)
        assert generator.dim_all_x > 1000
        assert generator.dim_all_y > 1000

    def test_same_building_in_metres_and_millimetres(self):
        create_placed_walls(self.file)
        millimetres = ifcopenshell.api.project.create_file()
        create_placed_walls(millimetres, prefix="MILLI")

        heights = []
        for file in (self.file, millimetres):
            run(file)
            drawing = get_drawing(file, "Test Building Ground Floor")
            heights.append(drawing.ObjectPlacement.RelativePlacement.Location.Coordinates[2])

        assert heights[1] / heights[0] == pytest.approx(1000.0, rel=0.01)

    @pytest.mark.parametrize("prefix, imperial", [(None, False), ("MILLI", False), (None, True)])
    def test_generates_drawings_in_any_unit(self, prefix, imperial):
        create_placed_walls(self.file, prefix=prefix, imperial=imperial)
        run(self.file)
        assert get_generated_drawings(self.file)


class TestBoundingBox(test.bootstrap.IFC4):
    def create_storey_with_walls(self, coords: list[tuple[float, float, float]]) -> ifcopenshell.entity_instance:
        """Add walls at the given placements, without geometry, and return their building"""
        project, _ = create_project(self.file, contexts=False)
        building = add_building(self.file, project)
        storey = add_storey(self.file, building)
        for xyz in coords:
            add_wall(self.file, storey, xyz)
        return building

    def create_building(self, prefix: Optional[str] = None) -> tuple:
        """Add a building with a storey, and return (building, storey, body context)"""
        project, body = create_project(self.file, prefix=prefix)
        building = add_building(self.file, project)
        return building, add_storey(self.file, building), body

    def test_single_element(self):
        building = self.create_storey_with_walls([(5.0, 6.0, 7.0)])
        assert recipe.GeometryUtils.get_bbox(self.file, [building]) == ([5.0, 6.0, 7.0],) * 3

    def test_no_elements_gives_degenerate_bbox(self):
        building = self.create_storey_with_walls([])
        assert recipe.GeometryUtils.get_bbox(self.file, [building]) == ([0.0, 0.0, 0.0],) * 3

    def test_elements_on_a_world_axis_kept(self):
        building = self.create_storey_with_walls([(0.0, 4.0, 0.0), (8.0, 0.0, 0.0)])
        bbox_min, _, bbox_max = recipe.GeometryUtils.get_bbox(self.file, [building])
        assert (bbox_min, bbox_max) == ([0.0, 0.0, 0.0], [8.0, 4.0, 0.0])

    def test_only_elements_at_the_world_origin_skipped(self):
        building = self.create_storey_with_walls([(0.0, 0.0, 0.0), (2.0, 3.0, 4.0), (9.0, 1.0, 1.0)])
        bbox_min, _, bbox_max = recipe.GeometryUtils.get_bbox(self.file, [building])
        assert (bbox_min, bbox_max) == ([2.0, 1.0, 1.0], [9.0, 3.0, 4.0])

    def test_spans_all_elements(self):
        building = self.create_storey_with_walls([(1.0, 1.0, 1.0), (5.0, 5.0, 5.0), (3.0, 9.0, 2.0)])
        bbox_min, _, bbox_max = recipe.GeometryUtils.get_bbox(self.file, [building])
        assert (bbox_min, bbox_max) == ([1.0, 1.0, 1.0], [5.0, 9.0, 5.0])

    def test_encloses_geometry_not_origin(self):
        building, storey, body = self.create_building()
        add_wall(self.file, storey, (1.0, 2.0, 0.0), body)
        bbox_min, bbox_mid, bbox_max = recipe.GeometryUtils.get_bbox(self.file, [building])
        assert bbox_min == pytest.approx([1.0, 2.0, 0.0])
        assert bbox_max == pytest.approx([6.0, 2.2, 3.0])
        assert bbox_mid == pytest.approx([3.5, 2.1, 1.5])

    def test_geometry_in_millimetres(self):
        building, storey, body = self.create_building(prefix="MILLI")
        add_wall(self.file, storey, (1000.0, 2000.0, 0.0), body)
        bbox_min, _, bbox_max = recipe.GeometryUtils.get_bbox(self.file, [building])
        assert bbox_min == pytest.approx([1000.0, 2000.0, 0.0])
        assert bbox_max == pytest.approx([6000.0, 2200.0, 3000.0])

    def test_mixes_geometry_and_origin_fallback(self):
        building, storey, body = self.create_building()
        add_wall(self.file, storey, (1.0, 2.0, 0.0), body)
        add_wall(self.file, storey, (20.0, 30.0, 1.0))
        bbox_min, _, bbox_max = recipe.GeometryUtils.get_bbox(self.file, [building])
        assert bbox_min == pytest.approx([1.0, 2.0, 0.0])
        assert bbox_max == pytest.approx([20.0, 30.0, 3.0])

    def test_uses_precomputed_bounds(self):
        building, storey, body = self.create_building()
        wall = add_wall(self.file, storey, (1.0, 2.0, 0.0), body)
        fake_bounds = {wall.id(): ([-1.0, -2.0, -3.0], [4.0, 5.0, 6.0])}
        bbox_min, _, bbox_max = recipe.GeometryUtils.get_bbox(self.file, [building], fake_bounds)
        assert (bbox_min, bbox_max) == ([-1.0, -2.0, -3.0], [4.0, 5.0, 6.0])

    def test_generator_site_bbox_encloses_geometry(self):
        building, storey, body = self.create_building()
        add_wall(self.file, storey, (1.0, 2.0, 0.0), body)
        assert recipe.DrawingGenerator(self.file).bbox_all_max == pytest.approx([6.0, 2.2, 3.0])
        run(self.file)

    def test_falls_back_without_cgal(self, monkeypatch):
        """Builds without the hybrid CGAL kernel fall back to OpenCASCADE"""
        building, storey, body = self.create_building()
        add_wall(self.file, storey, (1.0, 2.0, 0.0), body)
        real_iterator = ifcopenshell.geom.iterator
        libraries = []

        def iterator(*args, geometry_library="opencascade", **kwargs):
            libraries.append(geometry_library)
            if geometry_library != "opencascade":
                raise RuntimeError(f"No geometry kernel registered for {geometry_library}")
            return real_iterator(*args, geometry_library=geometry_library, **kwargs)

        monkeypatch.setattr(ifcopenshell.geom, "iterator", iterator)
        _, _, bbox_max = recipe.GeometryUtils.get_bbox(self.file, [building])

        assert libraries == ["hybrid-cgal-simple-opencascade", "opencascade"]
        assert bbox_max == pytest.approx([6.0, 2.2, 3.0])


class TestCentroids(test.bootstrap.IFC4):
    def create_space(self, prefix=None, rotation=0.0, xyz=(10.0, 20.0, 0.0), profile_points=None):
        project, body = create_project(self.file, prefix=prefix)
        storey = add_storey(self.file, add_building(self.file, add_site(self.file, project)))
        return add_space(self.file, storey, body, rotation=rotation, xyz=xyz, profile_points=profile_points)

    @pytest.mark.parametrize(
        "prefix, rotation, xyz, expected",
        [
            (None, 0.0, (10.0, 20.0, 0.0), [12.0, 21.0, 1.5]),
            ("MILLI", 0.0, (10000.0, 20000.0, 0.0), [12000.0, 21000.0, 1500.0]),
            (None, 90.0, (10.0, 20.0, 0.0), [9.0, 22.0, 1.5]),
            ("MILLI", 90.0, (10000.0, 20000.0, 0.0), [9000.0, 22000.0, 1500.0]),
        ],
    )
    def test_world_coordinates_in_project_units(self, prefix, rotation, xyz, expected):
        """Centroids include the placement rotation and are in project units"""
        space = self.create_space(prefix, rotation, xyz)
        assert recipe.GeometryUtils.get_centroids(self.file, [space])[space.id()] == pytest.approx(expected)

    def test_volume_centroid_not_vertex_mean(self):
        """An L-shaped space's centroid is weighted by volume, not by vertex count"""
        # 4m x 1m leg plus a 1m x 2m leg: area centroid (1.5, 1.0), vertex mean (1.67, 1.33)
        space = self.create_space(
            profile_points=[(0.0, 0.0), (4.0, 0.0), (4.0, 1.0), (1.0, 1.0), (1.0, 3.0), (0.0, 3.0)]
        )
        assert recipe.GeometryUtils.get_centroids(self.file, [space])[space.id()] == pytest.approx([11.5, 21.0, 1.5])

    def test_spaces_without_geometry_skipped(self):
        space = self.create_space()
        ifcopenshell.api.geometry.unassign_representation(
            self.file, product=space, representation=space.Representation.Representations[0]
        )
        assert recipe.GeometryUtils.get_centroids(self.file, [space]) == {}

    def test_space_label_placed_at_centroid(self):
        """The space label sits over the rotated space in a millimetre model"""
        self.create_space("MILLI", 90.0, (10000.0, 20000.0, 0.0))
        run(self.file)
        [label] = get_labels(self.file)
        x, y, z = label.ObjectPlacement.RelativePlacement.Location.Coordinates
        assert (x, y) == pytest.approx((9000.0, 22000.0))
        assert z == pytest.approx(100.0)


class TestDuplicateNames(test.bootstrap.IFC4):
    def test_buildings_sharing_a_name_keep_their_own_storeys(self):
        create_twin_buildings(self.file)
        run(self.file)
        plan_locations = {"drawings/Plot Ground A.svg", "drawings/Plot Ground B.svg"}
        plans = [
            sorted(r.Location for r in sheet.HasDocumentReferences if r.Location in plan_locations)
            for sheet in get_sheets(self.file)
        ]
        assert sorted(plans) == [["drawings/Plot Ground A.svg"], ["drawings/Plot Ground B.svg"]]

    def test_include_filters_select_their_own_building(self):
        """Elevation and location plan Include filters select one building, not every "Plot" """
        plots = create_twin_buildings(self.file)
        run(self.file)
        includes = [
            pset["Include"]
            for drawing in get_generated_drawings(self.file)
            if "Include" in (pset := ifcopenshell.util.element.get_pset(drawing, "EPset_Drawing"))
        ]
        # Four elevations and a location plan per building
        assert len(includes) == 10
        walls = {wall for _, _, wall in plots}
        for include in includes:
            assert len(ifcopenshell.util.selector.filter_elements(self.file, include) & walls) == 1, include

    def test_storeys_sharing_a_name_get_their_own_svg(self):
        """Plans are named "{building} {storey}", so each building's "Ground Floor" gets its own SVG"""
        for (building, storey, _), name in zip(create_twin_buildings(self.file), ("North Block", "South Block")):
            building.Name = name
            storey.Name = "Ground Floor"
        run(self.file)
        locations = {
            name: get_drawing_location(drawing)
            for name, drawing in get_drawings(self.file).items()
            if name.endswith("Ground Floor")
        }
        assert locations == {
            "North Block Ground Floor": "drawings/North Block Ground Floor.svg",
            "South Block Ground Floor": "drawings/South Block Ground Floor.svg",
        }


class TestScale(test.bootstrap.IFC4):
    @pytest.mark.parametrize("prefix", [None, "MILLI"])
    def test_metric_default(self, prefix):
        create_placed_walls(self.file, prefix=prefix)
        run(self.file)
        assert set(get_scales(self.file).values()) == {("1/100", "1:100")}

    def test_imperial_default(self):
        """Imperial projects default to 1/8"=1'-0", like Bonsai"""
        create_placed_walls(self.file, imperial=True)
        run(self.file)
        assert set(get_scales(self.file).values()) == {("1/96", '1/8"=1\'-0"')}

    @pytest.mark.parametrize("scale, human_scale", [(48, '1/4"=1\'-0"'), (240, "1\"=20'"), (100, "1:100")])
    def test_imperial_custom(self, scale, human_scale):
        """Imperial scales use architectural or engineering notation where Bonsai has one"""
        create_placed_walls(self.file, imperial=True)
        run(self.file, scale)
        assert set(get_scales(self.file).values()) == {(f"1/{scale}", human_scale)}

    def test_imperial_location_plan(self):
        """The location plan is ten times the drawing scale: 1/960 is 1"=80'"""
        site = create_placed_walls(self.file, imperial=True)
        add_building(self.file, site, "Other Building")
        run(self.file)
        locations = {scale for name, scale in get_scales(self.file).items() if name.endswith(" LOCATION")}
        assert locations == {("1/960", "1\"=80'")}


class TestOrientation(test.bootstrap.IFC4):
    ROTATED = [
        pytest.param({"building_rotation": 30.0}, 30.0, id="30"),
        pytest.param({"building_rotation": 45.0}, 45.0, id="45"),
        pytest.param({"site_rotation": 30.0}, 30.0, id="site-30"),
    ]

    @pytest.mark.parametrize("kwargs, rotation", ROTATED + [pytest.param({}, 0.0, id="0")])
    def test_building_rotation_from_placement(self, kwargs, rotation):
        """A building's rotation includes its site's, and unrotated buildings have none"""
        building = create_block(self.file, **kwargs)
        matrix = recipe.GeometryUtils.get_rotation(building)
        if rotation == 0.0:
            assert matrix is None
        else:
            x_axis, y_axis = get_axes(rotation)
            assert matrix[:, 0] == pytest.approx(x_axis)
            assert matrix[:, 1] == pytest.approx(y_axis)

    @pytest.mark.parametrize("kwargs, rotation", ROTATED)
    def test_oriented_bbox_fits_rotated_building(self, kwargs, rotation):
        """The bbox of a rotated building is aligned to it, not inflated by the world axes"""
        building = create_block(self.file, **kwargs)
        bbox_min, _, bbox_max = recipe.GeometryUtils.get_bbox(
            self.file, [building], rotation=recipe.GeometryUtils.get_rotation(building)
        )
        assert np.subtract(bbox_max, bbox_min) == pytest.approx([10.0, 6.0, 3.0])

    @pytest.mark.parametrize("kwargs, rotation", ROTATED + [pytest.param({}, 0.0, id="0")])
    def test_plan_square_to_building(self, kwargs, rotation):
        """Plan cameras run along the building's x axis and fit its bbox"""
        building = create_block(self.file, **kwargs)
        run(self.file)
        location, axis, ref_direction, dims = get_camera(get_drawing(self.file, "Block Ground Floor"))
        assert axis == pytest.approx([0.0, 0.0, 1.0])
        assert ref_direction == pytest.approx(get_axes(rotation)[0])
        assert dims == pytest.approx((12.0, 8.0, 10.0))
        matrix = ifcopenshell.util.placement.get_local_placement(building.ObjectPlacement)
        assert location == pytest.approx(matrix[:3, :3] @ [5.0, 3.0, 1.8] + matrix[:3, 3])

    @pytest.mark.parametrize(
        "kwargs, names",
        [
            pytest.param({}, ["NORTH", "SOUTH", "WEST", "EAST"], id="0"),
            pytest.param({"building_rotation": 22.5}, ["NORTH", "SOUTH", "WEST", "EAST"], id="22.5-tie"),
            pytest.param(
                {"building_rotation": 30.0}, ["NORTH-WEST", "SOUTH-EAST", "SOUTH-WEST", "NORTH-EAST"], id="30"
            ),
            pytest.param(
                {"building_rotation": 45.0}, ["NORTH-WEST", "SOUTH-EAST", "SOUTH-WEST", "NORTH-EAST"], id="45"
            ),
            pytest.param(
                {"site_rotation": 30.0}, ["NORTH-WEST", "SOUTH-EAST", "SOUTH-WEST", "NORTH-EAST"], id="site-30"
            ),
            # True north 90 degrees anticlockwise of project north, towards world -x
            pytest.param({"true_north": (-1.0, 0.0)}, ["EAST", "WEST", "NORTH", "SOUTH"], id="true-north-90"),
            pytest.param(
                {"building_rotation": 30.0, "true_north": (-1.0, 0.0)},
                ["NORTH-EAST", "SOUTH-WEST", "NORTH-WEST", "SOUTH-EAST"],
                id="30-true-north-90",
            ),
        ],
    )
    def test_elevations_named_by_compass_point(self, kwargs, names):
        """Each elevation looks square on to one face of the building and is named by its compass bearing"""
        building = create_block(self.file, **kwargs)
        rotation = recipe.GeometryUtils.get_rotation(building)
        rotation = np.eye(3) if rotation is None else rotation
        run(self.file)

        drawings = get_drawings(self.file)
        assert {n for n, d in drawings.items() if is_elevation(d)} == {f"Block {n}" for n in names}
        for name, normal in zip(names, FACE_NORMALS):
            _, axis, ref_direction, dims = get_camera(drawings[f"Block {name}"])
            assert axis == pytest.approx(rotation @ normal)
            assert ref_direction == pytest.approx(rotation @ np.cross([0.0, 0.0, 1.0], normal))
            # Face width and height padded by 2m, depth padded by 2m less 1m
            width, depth = (12.0, 7.0) if normal[1] else (8.0, 11.0)
            assert dims == pytest.approx((width, 5.0, depth))

    def test_rotated_elements_in_unrotated_building_stay_world_aligned(self):
        """Orientation comes from the building placement only, never from its geometry"""
        create_block(self.file, block_rotation=30.0)
        run(self.file)
        drawings = get_drawings(self.file)
        assert {n for n, d in drawings.items() if is_elevation(d)} == {
            "Block NORTH",
            "Block SOUTH",
            "Block EAST",
            "Block WEST",
        }
        _, _, ref_direction, dims = get_camera(drawings["Block Ground Floor"])
        assert ref_direction == pytest.approx([1.0, 0.0, 0.0])
        # World-aligned bbox of the rotated block, padded by 2m
        angle = np.radians(30.0)
        assert dims[0] == pytest.approx(10.0 * np.cos(angle) + 6.0 * np.sin(angle) + 2.0)

    def test_location_plan_stays_north_up(self):
        """The site-wide location plan isn't rotated with the buildings"""
        create_block(self.file, building_rotation=30.0)
        add_building(self.file, self.file.by_type("IfcSite")[0], "Other")
        run(self.file)
        assert get_drawing(self.file, "Block LOCATION").ObjectPlacement.RelativePlacement.RefDirection is None

    def test_space_labels_follow_rotated_plan(self):
        """Space label text runs along the building's x axis, like its plan"""
        create_block(self.file, building_rotation=30.0)
        run(self.file)
        [label] = get_labels(self.file)
        ref_direction = label.ObjectPlacement.RelativePlacement.RefDirection.DirectionRatios
        assert np.array(ref_direction) == pytest.approx(get_axes(30.0)[0])


class TestDocumentationPaths(test.bootstrap.IFC4):
    def test_bonsai_defaults_without_pset(self):
        create_model(self.file)
        run(self.file)
        drawing = get_drawing(self.file, "Test Building Ground Floor")
        assert get_drawing_location(drawing) == "drawings/Test Building Ground Floor.svg"
        assert get_sheet_locations(self.file) == {
            "LAYOUT": "layouts/A001 - Test Building.svg",
            "TITLEBLOCK": "layouts/titleblocks/A2.svg",
        }
        assert get_assets(drawing) == DEFAULT_ASSETS

    def test_partial_pset_falls_back_per_property(self):
        project = create_model(self.file)
        set_documentation(
            self.file,
            project,
            {"DrawingsDir": "docs/plans/", "StylesheetPath": "docs/house.css", "MarkersPath": ""},
        )
        run(self.file)
        drawing = get_drawing(self.file, "Test Building Ground Floor")
        assert get_drawing_location(drawing) == "docs/plans/Test Building Ground Floor.svg"
        assert get_sheet_locations(self.file) == {
            "LAYOUT": "layouts/A001 - Test Building.svg",
            "TITLEBLOCK": "layouts/titleblocks/A2.svg",
        }
        assert get_assets(drawing) == DEFAULT_ASSETS | {"Stylesheet": "docs/house.css"}

    def test_full_pset(self):
        project = create_model(self.file)
        set_documentation(
            self.file,
            project,
            {
                "DrawingsDir": "docs/drawings",
                "LayoutsDir": "docs/layouts/",
                # Windows separators and no trailing separator
                "TitleblocksDir": "docs\\titleblocks",
                "StylesheetPath": "docs/assets/house.css",
                "MarkersPath": "docs/assets/markers.svg",
                "SymbolsPath": "docs/assets/symbols.svg",
                "PatternsPath": "docs/assets/patterns.svg",
                "ShadingStylesPath": "docs/assets/shading.json",
            },
        )
        run(self.file, 0, "A1")
        drawing = get_drawing(self.file, "Test Building Ground Floor")
        assert get_drawing_location(drawing) == "docs/drawings/Test Building Ground Floor.svg"
        assert get_sheet_locations(self.file) == {
            "LAYOUT": "docs/layouts/A001 - Test Building.svg",
            "TITLEBLOCK": "docs/titleblocks/A1.svg",
        }
        assert get_assets(drawing) == {
            "Stylesheet": "docs/assets/house.css",
            "Markers": "docs/assets/markers.svg",
            "Symbols": "docs/assets/symbols.svg",
            "Patterns": "docs/assets/patterns.svg",
            "ShadingStyles": "docs/assets/shading.json",
        }

    def test_file_names_sanitised_like_bonsai(self):
        create_model(self.file, building_name="Block A/B: East")
        run(self.file)
        # The drawing keeps its name, but its file name loses "/" and ":"
        drawing = get_drawing(self.file, "Block A/B: East Ground Floor")
        assert get_drawing_location(drawing) == "drawings/Block AB East Ground Floor.svg"
        assert get_sheet_locations(self.file)["LAYOUT"] == "layouts/A001 - Block AB East.svg"
