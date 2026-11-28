# This file was generated with the assistance of an AI coding tool.

import numpy as np
import pytest

import ifcopenshell
import ifcopenshell.geom
import ifcopenshell.guid
import ifcopenshell.util.shape

RED = (1.0, 0.0, 0.0)
BLUE = (0.0, 0.0, 1.0)
DEFAULT = (0.7, 0.7, 0.7)


def make_file():
    f = ifcopenshell.file(schema="IFC4")
    axes = f.createIfcAxis2Placement3D(f.createIfcCartesianPoint((0.0, 0.0, 0.0)), None, None)
    context = f.createIfcGeometricRepresentationContext(None, "Model", 3, 1e-5, axes, None)
    units = f.createIfcUnitAssignment([f.createIfcSIUnit(None, "LENGTHUNIT", None, "METRE")])
    f.createIfcProject(ifcopenshell.guid.new(), None, "Project", None, None, None, None, [context], units)
    return f, axes, context


def make_box(f, axes, size=1.0):
    position = f.createIfcAxis2Placement2D(f.createIfcCartesianPoint((0.0, 0.0)), None)
    profile = f.createIfcRectangleProfileDef("AREA", None, position, size, size)
    return f.createIfcExtrudedAreaSolid(profile, axes, f.createIfcDirection((0.0, 0.0, 1.0)), 1.0)


def make_style(f, colour):
    shading = f.createIfcSurfaceStyleShading(f.createIfcColourRgb(None, *colour), 0.0)
    return f.createIfcSurfaceStyle(None, "POSITIVE", [shading])


def make_placement(f, i):
    location = f.createIfcCartesianPoint((i * 2.0, 0.0, 0.0))
    return f.createIfcLocalPlacement(None, f.createIfcAxis2Placement3D(location, None, None))


def make_styled_occurrences(target_offset):
    f, axes, context = make_file()
    mapped = f.createIfcShapeRepresentation(context, "Body", "SweptSolid", [make_box(f, axes)])
    representation_map = f.createIfcRepresentationMap(axes, mapped)
    styles = {colour: make_style(f, colour) for colour in (RED, BLUE)}
    for i, colour in enumerate((RED, RED, BLUE, None)):
        target = f.createIfcCartesianTransformationOperator3D(
            None, None, f.createIfcCartesianPoint(target_offset), 1.0, None
        )
        mapped_item = f.createIfcMappedItem(representation_map, target)
        if colour:
            f.createIfcStyledItem(mapped_item, [styles[colour]], None)
        representation = f.createIfcShapeRepresentation(context, "Body", "MappedRepresentation", [mapped_item])
        shape = f.createIfcProductDefinitionShape(None, None, [representation])
        f.createIfcBuildingElementProxy(
            ifcopenshell.guid.new(), None, f"Element{i}", None, None, make_placement(f, i), shape
        )
    return f


def make_shared_representation(colours, opening_in=None):
    f, axes, context = make_file()
    representation = f.createIfcShapeRepresentation(context, "Body", "SweptSolid", [make_box(f, axes)])
    shape = f.createIfcProductDefinitionShape(None, None, [representation])
    materials = {}
    for colour in set(colours):
        materials[colour] = f.createIfcMaterial(str(colour))
        styled_item = f.createIfcStyledItem(None, [make_style(f, colour)], None)
        styled = f.createIfcStyledRepresentation(context, None, None, [styled_item])
        f.createIfcMaterialDefinitionRepresentation(None, None, [styled], materials[colour])
    for i, colour in enumerate(colours):
        wall = f.createIfcWall(ifcopenshell.guid.new(), None, f"Element{i}", None, None, make_placement(f, i), shape)
        f.createIfcRelAssociatesMaterial(ifcopenshell.guid.new(), None, None, None, [wall], materials[colour])
        if i == opening_in:
            hole = f.createIfcShapeRepresentation(context, "Body", "SweptSolid", [make_box(f, axes, 0.5)])
            opening = f.createIfcOpeningElement(
                ifcopenshell.guid.new(),
                None,
                "Opening",
                None,
                None,
                f.createIfcLocalPlacement(wall.ObjectPlacement, axes),
                f.createIfcProductDefinitionShape(None, None, [hole]),
            )
            f.createIfcRelVoidsElement(ifcopenshell.guid.new(), None, None, None, wall, opening)
    return f


def iterate(f, reuse, world_coords=False):
    settings = ifcopenshell.geom.settings()
    settings.set("apply-default-materials", True)
    settings.set("use-world-coords", world_coords)
    settings.set("no-parallel-mapping", reuse)
    settings.set("permissive-shape-reuse", reuse)
    iterator = ifcopenshell.geom.iterator(settings, f, 1)
    assert iterator.initialize()
    elements = {}
    while True:
        element = iterator.get()
        elements[element.name] = element
        if not iterator.next():
            break
    return elements


def colours_of(element):
    colours = ifcopenshell.util.shape.get_material_colors(element.geometry)
    return {tuple(round(c, 3) for c in rgba[:3]) for rgba in colours}


def bounds_of(element):
    vertices = ifcopenshell.util.shape.get_vertices(element.geometry)
    matrix = ifcopenshell.util.shape.get_shape_matrix(element)
    world = np.hstack([vertices, np.ones((len(vertices), 1))]) @ matrix.T
    return np.concatenate([world[:, :3].min(axis=0), world[:, :3].max(axis=0)])


def volume_of(element):
    return ifcopenshell.util.shape.get_volume(element.geometry)


@pytest.mark.parametrize("target_offset", [(0.0, 0.0, 0.0), (0.0, 0.0, 5.0)], ids=["identity_target", "offset_target"])
@pytest.mark.parametrize("world_coords", [False, True], ids=["local", "world"])
def test_styled_occurrences_keep_style_and_position(target_offset, world_coords):
    f = make_styled_occurrences(target_offset)
    reused = iterate(f, True, world_coords)
    plain = iterate(f, False, world_coords)
    assert sorted(reused) == sorted(plain) == [f"Element{i}" for i in range(4)]
    for name, colour in zip(sorted(reused), (RED, RED, BLUE, DEFAULT)):
        assert colours_of(reused[name]) == colours_of(plain[name]) == {colour}
        assert bounds_of(reused[name]) == pytest.approx(bounds_of(plain[name]), abs=1e-9)


def test_occurrences_with_equal_style_share_geometry():
    reused = iterate(make_styled_occurrences((0.0, 0.0, 5.0)), True)
    assert reused["Element0"].geometry.id == reused["Element1"].geometry.id
    assert reused["Element0"].geometry.id != reused["Element2"].geometry.id
    assert reused["Element0"].geometry.id != reused["Element3"].geometry.id


def test_products_keep_their_own_material():
    f = make_shared_representation((RED, BLUE, BLUE))
    reused = iterate(f, True)
    plain = iterate(f, False)
    assert sorted(reused) == sorted(plain) == [f"Element{i}" for i in range(3)]
    for name, colour in zip(sorted(reused), (RED, BLUE, BLUE)):
        assert colours_of(reused[name]) == colours_of(plain[name]) == {colour}
        assert bounds_of(reused[name]) == pytest.approx(bounds_of(plain[name]), abs=1e-9)


def test_product_with_opening_keeps_it_to_itself():
    f = make_shared_representation((RED, RED, RED), opening_in=2)
    reused = iterate(f, True)
    assert volume_of(reused["Element0"]) == pytest.approx(1.0)
    assert volume_of(reused["Element1"]) == pytest.approx(1.0)
    assert volume_of(reused["Element2"]) == pytest.approx(0.75)
