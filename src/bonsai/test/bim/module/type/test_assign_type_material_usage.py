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
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Bonsai.  If not, see <http://www.gnu.org/licenses/>.
#
# This file was generated with the assistance of an AI coding tool.

"""Regression test: retyping a per-instance profile occurrence must move its
material usage to the new type.

``core.assign_type`` passes ``should_map_representations=False`` for an
occurrence that owns its body, so the new type's shared representation is not
mapped over it. That flag also gates ``map_material_usages`` inside
``api type.assign_type``, which is the step that re-points the occurrence's
``IfcMaterialProfileSetUsage`` at the new type's material set.

Left unhandled, the occurrence kept a usage whose ``ForProfileSet`` still
referenced the OLD type's set. ``get_material(should_skip_usage=True)`` follows
that pointer, so the material panel showed — and edited — the old type's
profile: duplicating a profile-based type and changing the copy's profile
silently rewrote the original's, and every other occurrence of the original
moved with it.

The fix must re-point the usage without undoing what the flag exists for, so
the occurrence's own extrusion (and its length) has to survive intact.

These live here rather than in ``test/core``, even though the subject is
``bonsai.core.type``. The Prophecy harness ``test/core`` uses cannot reach this
branch: ``_is_per_instance_profile`` calls ``ifcopenshell.util`` directly on the
element, so a real entity is needed, and Prophecy serialises call arguments to
JSON. Driving a real IFC file in turn imports ``ifcopenshell.api.material`` and
so ``mathutils``, which ``make test-core`` (``pytest -p no:pytest-blender
test/core``) deliberately runs without. Nothing here touches ``bpy`` itself.
"""

from unittest import mock

import pytest

pytestmark = pytest.mark.type

DEPTH = 3.0


class _IfcStub:
    """Stand-in for ``tool.Ifc``. ``core.assign_type`` only reaches for ``run``
    and ``get_object``; ``run`` dispatches to the real API so the assertions are
    made against genuine IFC state rather than recorded calls."""

    def __init__(self, ifc_file):
        self._file = ifc_file

    def run(self, usecase, **kwargs):
        import ifcopenshell.api

        return ifcopenshell.api.run(usecase, self._file, **kwargs)

    def get_object(self, element):
        return None


def _add_profile_type(ifc_file, body_context, name, profile_name):
    """An element type carrying its own IfcMaterialProfileSet."""
    import ifcopenshell.api.material
    import ifcopenshell.api.root

    element_type = ifcopenshell.api.root.create_entity(ifc_file, ifc_class="IfcColumnType", name=name)
    material = ifcopenshell.api.material.add_material(ifc_file, name="STEEL")
    profile_set = ifcopenshell.api.material.add_material_set(
        ifc_file, name=f"{name} set", set_type="IfcMaterialProfileSet"
    )
    profile = ifc_file.create_entity(
        "IfcRectangleProfileDef", ProfileType="AREA", ProfileName=profile_name, XDim=0.1, YDim=0.2
    )
    ifcopenshell.api.material.add_profile(ifc_file, profile_set=profile_set, material=material, profile=profile)
    ifcopenshell.api.material.assign_material(ifc_file, products=[element_type], material=profile_set)
    return element_type, profile_set, profile


@pytest.fixture
def model():
    """Two profile types, and one occurrence of the first that owns its body:
    its own non-mapped extrusion plus its own usage pointing at type A's set.
    That is what makes ``_is_per_instance_profile`` true."""
    import ifcopenshell
    import ifcopenshell.api.material
    import ifcopenshell.api.root
    import ifcopenshell.api.type

    ifc_file = ifcopenshell.file(schema="IFC4")
    ifcopenshell.api.root.create_entity(ifc_file, ifc_class="IfcProject")
    context = ifc_file.create_entity(
        "IfcGeometricRepresentationContext",
        ContextType="Model",
        CoordinateSpaceDimension=3,
        WorldCoordinateSystem=ifc_file.create_entity(
            "IfcAxis2Placement3D", Location=ifc_file.create_entity("IfcCartesianPoint", Coordinates=(0.0, 0.0, 0.0))
        ),
    )
    body_context = ifc_file.create_entity(
        "IfcGeometricRepresentationSubContext",
        ContextIdentifier="Body",
        ContextType="Model",
        ParentContext=context,
        TargetView="MODEL_VIEW",
    )

    type_a, profile_set_a, profile_a = _add_profile_type(ifc_file, body_context, "Type A", "RECT_A")
    type_b, profile_set_b, profile_b = _add_profile_type(ifc_file, body_context, "Type B", "RECT_B")

    occurrence = ifcopenshell.api.root.create_entity(ifc_file, ifc_class="IfcColumn", name="Column")
    ifcopenshell.api.type.assign_type(
        ifc_file, related_objects=[occurrence], relating_type=type_a, should_map_representations=False
    )
    ifcopenshell.api.material.assign_material(
        ifc_file, products=[occurrence], type="IfcMaterialProfileSetUsage", material=profile_set_a
    )

    solid = ifc_file.create_entity(
        "IfcExtrudedAreaSolid",
        SweptArea=profile_a,
        Position=ifc_file.create_entity(
            "IfcAxis2Placement3D", Location=ifc_file.create_entity("IfcCartesianPoint", Coordinates=(0.0, 0.0, 0.0))
        ),
        ExtrudedDirection=ifc_file.create_entity("IfcDirection", DirectionRatios=(0.0, 0.0, 1.0)),
        Depth=DEPTH,
    )
    representation = ifc_file.create_entity(
        "IfcShapeRepresentation",
        ContextOfItems=body_context,
        RepresentationIdentifier="Body",
        RepresentationType="SweptSolid",
        Items=[solid],
    )
    occurrence.Representation = ifc_file.create_entity(
        "IfcProductDefinitionShape", Representations=[representation]
    )

    return {
        "file": ifc_file,
        "occurrence": occurrence,
        "type_a": type_a,
        "type_b": type_b,
        "profile_set_a": profile_set_a,
        "profile_set_b": profile_set_b,
        "profile_b": profile_b,
        "solid": solid,
    }


def _retype(model, new_type):
    """Drive ``core.assign_type`` with the real IFC file behind ``ifc.run``.
    ``model``/``type_tool`` are mocked: they only drive Blender-side refresh,
    which has no bearing on the IFC state under test."""
    import bonsai.core.type as subject

    model_tool = mock.Mock()
    model_tool.get_usage_type.return_value = None
    type_tool = mock.Mock()
    type_tool.record_material_usage_attributes.return_value = None
    type_tool.get_object_data.return_value = None

    subject.assign_type(
        _IfcStub(model["file"]),
        model_tool,
        type_tool,
        element=model["occurrence"],
        type=new_type,
    )


def test_usage_follows_the_new_type(model):
    """The occurrence's own usage must point at the new type's profile set.

    Before the fix it still referenced type A's set, so the material panel
    edited type A's profile while the user believed they were editing type B's."""
    import ifcopenshell.util.element

    _retype(model, model["type_b"])

    usage = ifcopenshell.util.element.get_material(model["occurrence"], should_inherit=False)
    assert usage is not None, "occurrence must keep a material usage of its own"
    assert usage.is_a("IfcMaterialProfileSetUsage")
    assert usage.ForProfileSet == model["profile_set_b"], (
        "usage must follow the new type; still pointing at the old type's set means editing "
        "the occurrence's profile would mutate the old type"
    )

    resolved = ifcopenshell.util.element.get_material(model["occurrence"], should_skip_usage=True)
    assert resolved == model["profile_set_b"], "the set the material panel resolves to must be the new type's"


def test_per_instance_geometry_survives_the_retype(model):
    """Re-pointing the usage must not undo what should_map_representations=False
    exists for: the occurrence keeps its own non-mapped body at its own length,
    picking up only the new type's profile."""
    import ifcopenshell.util.element
    import ifcopenshell.util.representation

    _retype(model, model["type_b"])

    body = ifcopenshell.util.representation.get_representation(
        model["occurrence"], "Model", "Body", "MODEL_VIEW"
    )
    assert body is not None
    assert not any(
        item.is_a("IfcMappedItem") for item in body.Items
    ), "occurrence must keep its own body, not be mapped onto the type's shared representation"
    assert model["solid"].Depth == DEPTH, "per-instance extrusion length must be preserved"
    assert model["solid"].SweptArea == model["profile_b"], "body must pick up the new type's profile"


def test_old_type_is_left_alone(model):
    """The type the occurrence came from must not be touched by the retype."""
    import ifcopenshell.util.element

    profile_set_a = model["profile_set_a"]
    profile_a = profile_set_a.MaterialProfiles[0].Profile

    _retype(model, model["type_b"])

    assert ifcopenshell.util.element.get_material(model["type_a"], should_skip_usage=True) == profile_set_a
    assert profile_set_a.MaterialProfiles[0].Profile == profile_a, "old type's profile must be untouched"
