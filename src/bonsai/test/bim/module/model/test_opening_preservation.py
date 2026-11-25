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

"""A manually adjusted opening must survive host/fill regeneration.

``bim.recalculate_fill`` (and the Shift+G regen hotkey that routes into it for
doors and windows) refreshes a filling's opening by regenerating it from the
filling's bounding box. For an opening the user has adjusted by hand that is
destructive: the edit is silently replaced with the bounding box. Openings that
carry user intent stay frozen and are only changed by the user adjusting them
again.

These tests pin the guard in ``tool.Model.regenerate_filling_opening_body`` --
the single choke point every regen path funnels through -- and the two hazards
the guard exposes by putting ``should_preserve_opening`` on that hot path:
comparing against a default built at the wrong host thickness, and consuming
the type's shared 'Reference' template as if it were a throwaway default."""

import ast
from pathlib import Path
from unittest.mock import MagicMock, patch

import ifcopenshell
import ifcopenshell.api.context
import ifcopenshell.api.geometry
import ifcopenshell.api.root
import ifcopenshell.api.unit
import ifcopenshell.geom
import ifcopenshell.util.element
import ifcopenshell.util.representation
import ifcopenshell.util.shape
import numpy as np
import pytest
from ifcopenshell.util.shape_builder import ShapeBuilder

import bonsai.tool as tool
from bonsai.bim.module.model.opening import FilledOpeningGenerator

pytestmark = pytest.mark.model


def _voided_obj() -> MagicMock:
    obj = MagicMock()
    obj.data = MagicMock()
    obj.dimensions = (1.0, 0.2, 3.0)
    return obj


def _patch_regen_collaborators(preserve: bool) -> list:
    """Patch ``regenerate_filling_opening_body``'s collaborators down to the
    branch under test, so the guard can be exercised without a live host mesh."""
    return [
        patch.object(tool.Ifc, "get", MagicMock()),
        patch.object(tool.Ifc, "get_object", MagicMock(return_value=_voided_obj())),
        patch.object(tool.Geometry, "get_body_representation", MagicMock(return_value=MagicMock())),
        patch.object(tool.Geometry, "resolve_mapped_representation", MagicMock(side_effect=lambda r: r)),
        patch.object(FilledOpeningGenerator, "should_preserve_opening", MagicMock(return_value=preserve)),
    ]


def test_regenerate_filling_opening_body_preserves_adjusted_void():
    filling = MagicMock()
    with (
        patch.object(ifcopenshell.api.geometry, "unassign_representation") as unassign,
        patch.object(ifcopenshell.api.geometry, "remove_representation") as remove,
        patch.object(FilledOpeningGenerator, "generate_opening_from_filling") as generate,
    ):
        for patcher in _patch_regen_collaborators(preserve=True):
            patcher.start()
        try:
            tool.Model.regenerate_filling_opening_body(filling)
        finally:
            patch.stopall()

    generate.assert_not_called()
    unassign.assert_not_called()
    remove.assert_not_called()


def test_regenerate_filling_opening_body_regenerates_plain_void():
    filling = MagicMock()
    with (
        patch.object(ifcopenshell.api.geometry, "unassign_representation") as unassign,
        patch.object(ifcopenshell.api.geometry, "remove_representation"),
        patch.object(FilledOpeningGenerator, "generate_opening_from_filling") as generate,
    ):
        for patcher in _patch_regen_collaborators(preserve=False):
            patcher.start()
        try:
            tool.Model.regenerate_filling_opening_body(filling)
        finally:
            patch.stopall()

    generate.assert_called_once()
    unassign.assert_called_once()


def test_preserve_guard_runs_before_the_void_is_unassigned():
    """Forward-compat: the guard is only protective if it short-circuits before
    the old body is unassigned and removed. A guard moved below that point would
    still delete the user's geometry."""
    import bonsai.tool.model as model_module

    source = Path(model_module.__file__).read_text(encoding="utf-8")
    body = None
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.FunctionDef) and node.name == "regenerate_filling_opening_body":
            body = ast.unparse(node)
            break
    assert body is not None, "regenerate_filling_opening_body was not found in tool/model.py"
    assert "should_preserve_opening" in body, (
        "regenerate_filling_opening_body must consult should_preserve_opening, or a "
        "manually adjusted opening is reset to its filling's bounding box on every "
        "bim.recalculate_fill."
    )
    assert body.index("should_preserve_opening") < body.index("unassign_representation"), (
        "The should_preserve_opening guard must short-circuit before "
        "unassign_representation, otherwise the adjusted body is already gone."
    )


def test_is_adjusted_extrusion_does_not_consume_the_type_template():
    """When a type carries a 'Reference' opening template,
    ``generate_opening_from_filling`` hands back that template rather than a
    throwaway default -- so generating and then removing it would destroy the
    shared geometry. The template case must short-circuit instead."""
    generator = FilledOpeningGenerator()
    opening = MagicMock()
    with (
        patch.object(tool.Ifc, "get_object", MagicMock(return_value=MagicMock())),
        patch.object(ifcopenshell.util.representation, "get_representation", MagicMock(return_value=MagicMock())),
        patch.object(ifcopenshell.util.representation, "resolve_representation", MagicMock(side_effect=lambda r: r)),
        patch.object(ifcopenshell.util.element, "get_type", MagicMock(return_value=MagicMock())),
        patch.object(FilledOpeningGenerator, "get_type_opening_representation", MagicMock(return_value=MagicMock())),
        patch.object(FilledOpeningGenerator, "generate_opening_from_filling") as generate,
        patch.object(ifcopenshell.api.geometry, "remove_representation") as remove,
    ):
        assert generator._is_adjusted_extrusion(opening) is True

    generate.assert_not_called()
    remove.assert_not_called()


def _rectangular_opening_body(ifc_file, context, size, position, depth):
    shape_builder = ShapeBuilder(ifc_file)
    curve = shape_builder.rectangle(size=size, position=position)
    extrusion = shape_builder.extrude(curve, magnitude=depth, **shape_builder.extrude_kwargs("Y"))
    return shape_builder.get_representation(context, [extrusion])


def test_representation_bbox_separates_an_adjusted_void_from_the_default():
    """The bounding-box comparison behind ``_is_adjusted_extrusion`` must clear
    the 1mm tolerance for a hand-inset profile while reporting no difference for
    an unmodified one, so plain openings keep tracking their filling's size."""
    ifc_file = ifcopenshell.file(schema="IFC4")
    ifcopenshell.api.root.create_entity(ifc_file, ifc_class="IfcProject")
    ifcopenshell.api.unit.assign_unit(ifc_file, length={"is_metric": True, "raw": "METERS"})
    model = ifcopenshell.api.context.add_context(ifc_file, context_type="Model")
    body = ifcopenshell.api.context.add_context(
        ifc_file, context_type="Model", context_identifier="Body", target_view="MODEL_VIEW", parent=model
    )

    default = _rectangular_opening_body(ifc_file, body, (0.9, 2.1), (0.0, 0.0), 1.2)
    adjusted = _rectangular_opening_body(ifc_file, body, (0.8, 2.0), (0.05, 0.05), 1.2)

    settings = ifcopenshell.geom.settings()
    default_bbox = FilledOpeningGenerator._representation_bbox(settings, default)
    adjusted_bbox = FilledOpeningGenerator._representation_bbox(settings, adjusted)
    assert default_bbox is not None and adjusted_bbox is not None

    tolerance = 1e-3

    def differs(a, b):
        (a_min, a_max), (b_min, b_max) = a, b
        return bool(np.any(np.abs(a_min - b_min) > tolerance) or np.any(np.abs(a_max - b_max) > tolerance))

    assert differs(adjusted_bbox, default_bbox), "A 50mm inset profile must read as manually adjusted"
    assert not differs(default_bbox, default_bbox), "An unmodified profile must not read as manually adjusted"


def test_default_is_generated_against_the_host_thickness():
    """The transient default must be built with the host's thickness. Built with
    the 1.2m fallback instead, the extrusion depth alone reads as an adjustment
    on any host thicker than that, freezing openings that should still track
    their filling."""
    import bonsai.bim.module.model.opening as opening_module

    source = Path(opening_module.__file__).read_text(encoding="utf-8")
    body = None
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.FunctionDef) and node.name == "_is_adjusted_extrusion":
            body = ast.unparse(node)
            break
    assert body is not None, "_is_adjusted_extrusion was not found in opening.py"
    assert "dimensions[1]" in body, (
        "_is_adjusted_extrusion must pass the voided host's thickness into "
        "generate_opening_from_filling so the extrusion depth is compared like for like."
    )
