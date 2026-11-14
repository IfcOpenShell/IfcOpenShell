# This file was generated with the assistance of an AI coding tool.

import pytest

import ifcopenshell
import ifcopenshell.api.context
import ifcopenshell.api.geometry
import ifcopenshell.api.project
import ifcopenshell.api.root
import ifcopenshell.api.unit
import ifcopenshell.geom


def _create_model(representation_also_used_directly):
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
    representation = ifcopenshell.api.geometry.add_wall_representation(
        model, context=body, length=4, height=3, thickness=1
    )
    if representation_also_used_directly:
        direct = ifcopenshell.api.root.create_entity(model, ifc_class="IfcWall", name="Direct")
        ifcopenshell.api.geometry.assign_representation(model, product=direct, representation=representation)
    mapped = ifcopenshell.api.root.create_entity(model, ifc_class="IfcWall", name="Mapped")
    ifcopenshell.api.geometry.assign_representation(
        model,
        product=mapped,
        representation=ifcopenshell.api.geometry.map_representation(model, representation=representation),
    )
    return model


@pytest.mark.parametrize("representation_also_used_directly", [False, True], ids=["map_only", "direct_and_map"])
def test_representation_used_directly_and_as_mapped_item_warns(representation_also_used_directly):
    model = _create_model(representation_also_used_directly)
    ifcopenshell.get_log()

    list(ifcopenshell.geom.consume_iterator(ifcopenshell.geom.iterator(ifcopenshell.geom.settings(), model, 1)))

    assert ("WR11" in ifcopenshell.get_log()) == representation_also_used_directly
