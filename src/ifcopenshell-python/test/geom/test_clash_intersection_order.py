# This file was generated with the assistance of an AI coding tool.

import pytest

import ifcopenshell.api.context
import ifcopenshell.api.geometry
import ifcopenshell.api.project
import ifcopenshell.api.root
import ifcopenshell.api.unit
import ifcopenshell.geom


def _create_box_and_open_sheet():
    model = ifcopenshell.api.project.create_file()
    ifcopenshell.api.root.create_entity(model, ifc_class="IfcProject")
    ifcopenshell.api.unit.assign_unit(model)
    body = ifcopenshell.api.context.add_context(
        model,
        context_type="Model",
        context_identifier="Body",
        target_view="MODEL_VIEW",
        parent=ifcopenshell.api.context.add_context(model, context_type="Model"),
    )
    box = ifcopenshell.api.root.create_entity(model, ifc_class="IfcBuildingElementProxy", name="Box")
    box_representation = ifcopenshell.api.geometry.add_wall_representation(
        model, context=body, length=4, height=3, thickness=1
    )
    ifcopenshell.api.geometry.assign_representation(model, product=box, representation=box_representation)
    sheet = ifcopenshell.api.root.create_entity(model, ifc_class="IfcBuildingElementProxy", name="Sheet")
    sheet_representation = ifcopenshell.api.geometry.add_mesh_representation(
        model,
        context=body,
        vertices=[[(2.0, -2.0, 1.0), (2.0, 2.0, 1.0), (2.0, 2.0, 2.0), (2.0, -2.0, 2.0)]],
        faces=[[(0, 1, 2, 3)]],
    )
    ifcopenshell.api.geometry.assign_representation(model, product=sheet, representation=sheet_representation)
    return model, box, sheet


@pytest.mark.parametrize("sheet_in_set_a", [False, True], ids=["box_in_a", "sheet_in_a"])
def test_clash_intersection_many_keeps_set_order(sheet_in_set_a):
    model, box, sheet = _create_box_and_open_sheet()
    tree = ifcopenshell.geom.tree(backend="opencascade.trianglebvh")
    tree.add_file(model, ifcopenshell.geom.settings())

    set_a, set_b = ([sheet], [box]) if sheet_in_set_a else ([box], [sheet])
    clashes = tree.clash_intersection_many(set_a, set_b, 0.002, True)

    assert len(clashes) == 1
    assert (clashes[0].a.id(), clashes[0].b.id()) == (set_a[0].id(), set_b[0].id())
