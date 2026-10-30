# This file was generated with the assistance of an AI coding tool.

import math

import pytest

import ifcopenshell
import ifcopenshell.geom
import ifcopenshell.guid

FOOT = 0.3048


def _model():
    """An IFC4 model in feet, the unit whose scaling to metres brings out the rounding below."""
    model = ifcopenshell.file(schema="IFC4")
    origin = model.createIfcAxis2Placement3D(model.createIfcCartesianPoint((0.0, 0.0, 0.0)))
    context = model.createIfcGeometricRepresentationContext(None, "Model", 3, 1e-5, origin, None)
    metre = model.createIfcSIUnit(None, "LENGTHUNIT", None, "METRE")
    foot = model.createIfcConversionBasedUnit(
        model.createIfcDimensionalExponents(1, 0, 0, 0, 0, 0, 0),
        "LENGTHUNIT",
        "foot",
        model.createIfcMeasureWithUnit(model.createIfcLengthMeasure(FOOT), metre),
    )
    units = model.createIfcUnitAssignment([foot])
    model.createIfcProject(ifcopenshell.guid.new(), None, "Test", None, None, None, None, [context], units)
    return model, context


def _box(model, context, x, y, z, turn):
    """A product's representation and placement: a box spanning x, y and z (each a (low, high) pair, in
    feet) in a frame turned by `turn` degrees about the vertical."""
    (x0, x1), (y0, y1), (z0, z1) = x, y, z
    points = [(x0, y0), (x1, y0), (x1, y1), (x0, y1), (x0, y0)]
    profile = model.createIfcArbitraryClosedProfileDef(
        "AREA", None, model.createIfcPolyline([model.createIfcCartesianPoint(p) for p in points])
    )
    position = model.createIfcAxis2Placement3D(model.createIfcCartesianPoint((0.0, 0.0, z0)))
    solid = model.createIfcExtrudedAreaSolid(profile, position, model.createIfcDirection((0.0, 0.0, 1.0)), z1 - z0)
    representation = model.createIfcShapeRepresentation(context, "Body", "SweptSolid", [solid])
    a = math.radians(turn)
    placement = model.createIfcLocalPlacement(
        None,
        model.createIfcAxis2Placement3D(
            model.createIfcCartesianPoint((0.0, 0.0, 0.0)),
            model.createIfcDirection((0.0, 0.0, 1.0)),
            model.createIfcDirection((math.cos(a), math.sin(a), 0.0)),
        ),
    )
    return placement, model.createIfcProductDefinitionShape(None, None, [representation])


def _wall_with_an_element(turn, element_x, element_y, element_z):
    """A wall 6 in thick, 30 ft long and 20 ft high, with an opening 20 ft long from 2 ft along it, between 10 and
    18 ft high; and an element (a railing) spanning element_x, element_y and element_z, all in one turned frame."""
    model, context = _model()
    placement, shape = _box(model, context, (0.0, 0.5), (0.0, 30.0), (0.0, 20.0), turn)
    wall = model.createIfcWall(ifcopenshell.guid.new(), None, "Wall", None, None, placement, shape)
    placement, shape = _box(model, context, (-0.01, 0.51), (2.0, 22.0), (10.0, 18.0), turn)
    opening = model.createIfcOpeningElement(ifcopenshell.guid.new(), None, "Opening", None, None, placement, shape)
    model.createIfcRelVoidsElement(ifcopenshell.guid.new(), None, None, None, wall, opening)
    placement, shape = _box(model, context, element_x, element_y, element_z, turn)
    element = model.createIfcRailing(ifcopenshell.guid.new(), None, "Railing", None, None, placement, shape)
    return model, wall, element


def _clashes(model, element, others):
    settings = ifcopenshell.geom.settings()
    settings.set("use-world-coords", True)
    tree = ifcopenshell.geom.tree(backend="opencascade.trianglebvh")
    iterator = ifcopenshell.geom.iterator(settings, model, include=[element, *others])
    assert iterator.initialize()
    while True:
        tree.add_element(iterator.get())
        if not iterator.next():
            break
    return tree.clash_intersection_many([element], others, tolerance=0.002, check_all=True)


TURNS = list(range(0, 180, 5))


@pytest.mark.parametrize("turn", TURNS)
def test_an_element_flush_between_the_jambs_of_an_opening_does_not_pierce_the_wall(turn):
    # A guard rail 1.5 in thick standing on the opening's sill, exactly as long as the opening: its long edges end on
    # the two jambs. They touch the wall there and run through the opening between, so this is no clash. It was
    # reported as a pierce as deep as the wall is thick (the cap), with the two points at the ends of an edge,
    # for many of these turns: each crossing at an edge's own end lands just inside the edge by rounding.
    model, wall, guard = _wall_with_an_element(turn, (0.1875, 0.3125), (2.0, 22.0), (10.0, 13.5))
    assert [(c.clash_type, round(c.distance, 4)) for c in _clashes(model, guard, [wall])] == []


@pytest.mark.parametrize("turn", [0, 25, 65])
def test_an_element_through_the_solid_head_of_the_wall_still_pierces_it(turn):
    # The same guard reaching above the opening's head runs inside the wall's solid part there.
    model, wall, guard = _wall_with_an_element(turn, (0.1875, 0.3125), (2.0, 22.0), (10.0, 19.0))
    clashes = _clashes(model, guard, [wall])
    assert len(clashes) == 1
    assert ifcopenshell.geom.tree.get_clash_type(clashes[0].clash_type) in ("protrusion", "pierce")


@pytest.mark.parametrize("turn", [0, 25, 65])
def test_a_bar_passing_through_the_wall_pierces_it_by_the_walls_thickness(turn):
    # A bar 4 in square passing right through the wall's solid part below the opening, out on both faces.
    model, wall, bar = _wall_with_an_element(turn, (-1.0, 1.5), (25.0, 25.333), (4.0, 4.333))
    clashes = _clashes(model, bar, [wall])
    assert len(clashes) == 1
    assert ifcopenshell.geom.tree.get_clash_type(clashes[0].clash_type) == "pierce"
    assert clashes[0].distance == pytest.approx(0.5 * FOOT, abs=1e-6)
