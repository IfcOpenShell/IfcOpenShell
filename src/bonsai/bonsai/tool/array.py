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

"""Bonsai parametric array service.

Top-level array-domain helpers. The ``BBIM_Array`` pset on a parent ``IfcElement``
holds the list of layers; each layer holds the GUIDs of its child replicas. These
helpers navigate that graph and manage the Blender-side CHILD_OF constraint that
pins children to the parent's matrix_world."""

from __future__ import annotations

import json
from collections.abc import Generator
from typing import TYPE_CHECKING, Any

import bpy
import ifcopenshell
import ifcopenshell.util.element
from mathutils import Matrix, Vector

import bonsai.core.tool
import bonsai.tool as tool

if TYPE_CHECKING:
    from ifcopenshell import entity_instance


class Array(bonsai.core.tool.Array):
    # ``BBIM_Array.Data`` layers written before radial arrays existed carry no
    # ``type`` key; ``LINEAR`` reproduces their behaviour byte-for-byte.
    DEFAULT_ARRAY_TYPE = "LINEAR"
    # Below this the rotation axis is treated as degenerate and the radial
    # layer collapses to "every copy sits on the source".
    MIN_AXIS_LENGTH = 1e-9

    @classmethod
    def child_matrix(cls, source_matrix: Matrix, layer: dict[str, Any], i: int, unit_scale: float) -> Matrix:
        """World matrix for instance ``i`` of ``layer``, given the world matrix
        of the instance it is copied from. ``i == 0`` is the source itself.

        Single source of truth for array placement: both the regenerator
        (``tool.Model._regenerate_array_body``) and the drag-time ghost preview
        (``ArrayPreviewDecorator``) call this, so the preview cannot drift from
        what Finish actually builds.

        ``source_matrix`` is the *previous layer's* instance, not necessarily
        the root parent — that is what makes stacked layers compose (a radial
        layer over a linear one arrays a whole row about the pivot).

        ``unit_scale`` converts the layer's stored distances (project units)
        to Blender SI. Callers whose values are already SI pass ``1.0``."""
        if layer.get("type", cls.DEFAULT_ARRAY_TYPE) == "RADIAL":
            return cls._radial_child_matrix(source_matrix, layer, i, unit_scale)
        return cls._linear_child_matrix(source_matrix, layer, i, unit_scale)

    @classmethod
    def step_divisor(cls, layer: dict[str, Any]) -> int:
        """Number the per-instance step is divided by under ``DISTRIBUTE``.

        ``DISTRIBUTE`` spreads ``count`` instances across a fixed total span, so
        the step is the span over the number of *gaps*. A closed radial loop
        (``full_circle``) has ``count`` gaps because the last instance's gap
        wraps back onto the first; every other case has ``count - 1``."""
        count = max(int(layer.get("count", 1)), 1)
        if layer.get("type", cls.DEFAULT_ARRAY_TYPE) == "RADIAL" and cls.is_closed_loop(layer):
            return count
        return max(count - 1, 1)

    @classmethod
    def layer_from_props(cls, props, count: int | None = None, si_conversion: float = 1.0) -> dict:
        """Build a ``BBIM_Array.Data`` layer dict from the draft edit props.

        Distances are divided by ``si_conversion`` so the result is in project
        units, matching what the pset stores. Callers that want SI out (the ghost
        preview, which already holds SI props) pass ``si_conversion=1.0``.

        ``angle`` is unit-scale-free: it is stored in radians, following the same
        convention as ``BBIM_Roof``, and is deliberately *not* wrapped to one turn
        so multi-turn sweeps (spiral stairs, helical ramps) survive the round-trip.

        ``count`` overrides ``props.count`` for callers that have already clamped
        it (the preview caps instances for GPU budget reasons)."""
        return {
            "count": props.count if count is None else count,
            "type": props.array_type,
            "method": props.method,
            "x": props.x / si_conversion,
            "y": props.y / si_conversion,
            "z": props.z / si_conversion,
            "angle": props.angle,
            "rise": props.rise / si_conversion,
            "rise_method": props.rise_method,
            "axis": list(props.get_axis_vector()),
            "center": [c / si_conversion for c in props.center],
            "full_circle": props.full_circle,
            "rotate_children": props.rotate_children,
            "use_local_space": props.use_local_space,
            "per_child_opening": props.per_child_opening,
        }

    @classmethod
    def angle_gap_count(cls, layer: dict[str, Any]) -> int:
        """Number of steps actually between instances — 0 for a lone instance.

        Distinct from ``step_divisor``, which floors at 1 to keep the DISTRIBUTE
        division safe. For display the honest count matters: a one-instance
        layer spans nothing and should report nothing, not a phantom step."""
        count = max(int(layer.get("count", 1)), 1)
        if layer.get("type", cls.DEFAULT_ARRAY_TYPE) == "RADIAL" and cls.is_closed_loop(layer):
            return count
        return count - 1

    @classmethod
    def rise_gap_count(cls, layer: dict[str, Any]) -> int:
        """Steps between instances for the climb. Never the closed-loop count —
        a closed loop requires zero rise (see ``is_closed_loop``)."""
        return max(int(layer.get("count", 1)), 1) - 1

    @classmethod
    def resolved_rise(cls, layer: dict[str, Any]) -> tuple[float, float]:
        """``(per_copy, total)`` climb, however the layer happens to specify it.

        Whichever of the two the user typed, the other is the one they need to
        see: a spiral stair given as a floor-to-floor total still has to clear
        a code-limited riser height, and that riser only exists as a derived
        number. Returning both lets the panel show the half that was computed.

        Units follow the layer's — project units in, project units out."""
        rise = layer.get("rise", 0.0)
        gaps = cls.rise_gap_count(layer)
        if cls.rise_method(layer) == "DISTRIBUTE":
            return (rise / gaps if gaps else 0.0), rise
        return rise, rise * gaps

    @classmethod
    def resolved_angle(cls, layer: dict[str, Any]) -> tuple[float, float]:
        """``(per_copy, total)`` sweep in radians, however it was specified.

        The total is deliberately NOT wrapped: reporting 630 degrees rather
        than 270 is the whole point of showing it, since the turn count is
        exactly what a bare heading hides."""
        angle = layer.get("angle", 0.0)
        gaps = cls.angle_gap_count(layer)
        if layer.get("method") == "DISTRIBUTE":
            return (angle / gaps if gaps else 0.0), angle
        return angle, angle * gaps

    @classmethod
    def rise_method(cls, layer: dict[str, Any]) -> str:
        """Spacing method governing the helix climb, independent of the angle's.

        Falls back to the layer's main ``method`` when unset, so a layer that
        specifies only one method stays coherent.

        The two are decoupled because a spiral stair is normally specified with
        one quantity per-copy and the other as a total — "30 degrees a tread,
        3 metres floor to floor", or "540 degrees total, 180mm risers". The
        floor-to-floor height is fixed by the building while the tread angle is
        a design choice (or vice versa), and forcing both quantities into the
        same mode makes the common specification unstatable."""
        return layer.get("rise_method") or layer.get("method", "OFFSET")

    @classmethod
    def rise_divisor(cls, layer: dict[str, Any]) -> int:
        """Divisor for the climb under a DISTRIBUTE ``rise_method``.

        Always the gap count, never the closed-loop ``count`` branch that
        ``step_divisor`` can take: a closed loop requires ``rise == 0`` (see
        ``is_closed_loop``), so no helix ever divides its climb by ``count``."""
        return max(int(layer.get("count", 1)) - 1, 1)

    @classmethod
    def is_closed_loop(cls, layer: dict[str, Any]) -> bool:
        """True when the radial sweep closes back onto its start, so the
        endpoint instance would duplicate the first one and must be dropped.

        A non-zero ``rise`` breaks the closure — the endpoint lands a full
        climb above the start, not on top of it — so ``full_circle`` is ignored
        for helices rather than silently dropping a real instance."""
        if not layer.get("full_circle"):
            return False
        return not layer.get("rise", 0.0)

    @classmethod
    def _linear_child_matrix(cls, source_matrix: Matrix, layer: dict[str, Any], i: int, unit_scale: float) -> Matrix:
        offset = Vector((layer.get("x", 0.0), layer.get("y", 0.0), layer.get("z", 0.0))) * unit_scale
        if layer.get("method") == "DISTRIBUTE":
            offset = offset / cls.step_divisor(layer)
        offset = offset * i
        matrix = source_matrix.copy()
        if layer.get("use_local_space", True):
            matrix.translation = source_matrix @ offset
        else:
            matrix.translation = source_matrix.translation + offset
        return matrix

    @classmethod
    def _radial_child_matrix(cls, source_matrix: Matrix, layer: dict[str, Any], i: int, unit_scale: float) -> Matrix:
        """Rotate instance ``i`` about ``center``/``axis``, optionally climbing
        ``rise`` along the axis per step (helix: spiral stairs, ramps).

        The cumulative angle ``step * i`` is fed straight into
        ``Matrix.Rotation`` and is never wrapped, normalised, or round-tripped
        through a quaternion/Euler. That is what lets a sweep exceed one full
        turn: decomposing a rotation matrix would fold 630 degrees back to -90
        and silently stack later instances onto earlier ones."""
        angle = layer.get("angle", 0.0)
        rise = layer.get("rise", 0.0) * unit_scale
        # Angle and climb take their DISTRIBUTE decisions separately — see
        # ``rise_method`` for why a stair usually needs one of each.
        if layer.get("method") == "DISTRIBUTE":
            angle = angle / cls.step_divisor(layer)
        if cls.rise_method(layer) == "DISTRIBUTE":
            rise = rise / cls.rise_divisor(layer)

        axis = Vector(layer.get("axis", (0.0, 0.0, 1.0)))
        center = Vector(layer.get("center", (0.0, 0.0, 0.0))) * unit_scale
        # ``center``/``axis`` are stored relative to the source instance, exactly
        # like the linear offsets — an absolute world pivot would stay behind
        # when the parent moves, tearing the ring away from its own contents
        # (children track the parent via the BBIM_Array CHILD_OF constraint).
        if layer.get("use_local_space", True):
            axis = source_matrix.to_3x3() @ axis
            pivot = source_matrix @ center
        else:
            pivot = source_matrix.translation + center

        if axis.length < cls.MIN_AXIS_LENGTH:
            return source_matrix.copy()
        axis = axis.normalized()

        rotation = Matrix.Rotation(angle * i, 4, axis)
        matrix = Matrix.Translation(pivot) @ rotation @ Matrix.Translation(-pivot) @ source_matrix
        if not layer.get("rotate_children", True):
            # Orbit the position but keep the source's orientation — upright
            # copies around a pivot rather than a tangentially-turned ring.
            oriented = source_matrix.copy()
            oriented.translation = matrix.translation
            matrix = oriented
        if rise:
            matrix.translation = matrix.translation + axis * (rise * i)
        return matrix

    @classmethod
    def bake_children_transform(cls, parent_element: entity_instance, item: int) -> None:
        modifier_data = list(cls.get_modifiers_data(parent_element))[item]
        children = cls.get_children_objects(modifier_data)
        for child in children:
            constraint = next((c for c in child.constraints if c.type == "CHILD_OF"), None)
            if constraint:
                with bpy.context.temp_override(object=child):
                    bpy.ops.constraint.apply(constraint=constraint.name, owner="OBJECT")

    @classmethod
    def constrain_children_to_parent(cls, parent_element: ifcopenshell.entity_instance) -> None:
        if not (parent_obj := tool.Ifc.get_object(parent_element)):
            return  # Filtered out, arrayed void, etc
        assert isinstance(parent_obj, bpy.types.Object)
        children = cls.get_all_children_objects(parent_element)
        for child in children:
            constraint = next((c for c in child.constraints if c.type == "CHILD_OF"), None)
            if constraint:
                child.constraints.remove(constraint)
            constraint = child.constraints.new("CHILD_OF")
            constraint.name = "BBIM_Array_CHILD_OF"
            assert isinstance(constraint, bpy.types.ChildOfConstraint)
            constraint.target = parent_obj

    @classmethod
    def set_children_lock_state(
        cls, parent_element: ifcopenshell.entity_instance, item: int, lock_state: bool = True
    ) -> None:
        modifier_data = list(cls.get_modifiers_data(parent_element))[item]
        children = cls.get_children_objects(modifier_data)
        for child_obj in children:
            tool.Blender.lock_transform(child_obj, lock_state)

    @classmethod
    def remove_constraints(cls, parent_element: ifcopenshell.entity_instance) -> None:
        children = cls.get_all_children_objects(parent_element)
        for child in children:
            constraint = next((c for c in child.constraints if c.type == "CHILD_OF"), None)
            if constraint:
                child.constraints.remove(constraint)

    @classmethod
    def get_all_objects(cls, parent_element: ifcopenshell.entity_instance) -> list[bpy.types.Object]:
        parent_obj = tool.Ifc.get_object(parent_element)
        assert isinstance(parent_obj, bpy.types.Object)
        children_objects = list(cls.get_all_children_objects(parent_element))
        array_objects = [parent_obj] + children_objects  # We ensure the parent is at index 0
        return array_objects

    @classmethod
    def get_all_children_objects(cls, parent_element: ifcopenshell.entity_instance) -> Generator[bpy.types.Object]:
        for array_modifier in cls.get_modifiers_data(parent_element):
            yield from cls.get_children_objects(array_modifier)

    @classmethod
    def get_parent_element(cls, element: entity_instance) -> entity_instance | None:
        """Inverse of ``get_all_children_objects``: resolve an array element
        back to its parent entity. Returns ``None`` when the element isn't
        part of a Bonsai parametric array, or the stored Parent GUID does
        not resolve in the current file (this is a data-integrity warning
        and is logged to the console)."""
        pset = ifcopenshell.util.element.get_pset(element, "BBIM_Array")
        if not pset:
            return None
        parent_guid = pset["Parent"]
        try:
            return tool.Ifc.get().by_guid(parent_guid)
        except RuntimeError:
            print(
                f"BBIM_Array.Parent GUID {parent_guid!r} on {element} does not resolve "
                f"in the current file — array integrity may be broken."
            )
            return None

    @classmethod
    def get_parent_object(cls, element: entity_instance) -> bpy.types.Object | None:
        parent_element = cls.get_parent_element(element)
        if parent_element is None:
            return None
        return tool.Ifc.get_object(parent_element)

    @classmethod
    def get_modifiers_data(cls, parent_element: ifcopenshell.entity_instance) -> Generator[dict[str, Any]]:
        array_pset = ifcopenshell.util.element.get_pset(parent_element, "BBIM_Array")
        yield from json.loads(array_pset["Data"])

    @classmethod
    def get_children_objects(cls, modifier_data: dict[str, Any]) -> Generator[bpy.types.Object]:
        child_guid: str
        for child_guid in modifier_data["children"]:
            child_obj = tool.Blender.get_object_from_guid(child_guid)
            if child_obj:
                yield child_obj

    @classmethod
    def get_array_root_guid(cls, element: entity_instance) -> str:
        """Walk ``BBIM_Array.Parent`` upwards and return the topmost ancestor's
        GlobalId. For an element with no ``BBIM_Array`` pset (independent
        window, never arrayed, or former-child after the apply path), returns
        the element's own GlobalId — its "family" is just itself."""
        current = element
        seen: set[str] = set()
        while True:
            pset = ifcopenshell.util.element.get_pset(current, "BBIM_Array")
            parent_guid = pset.get("Parent") if pset else None
            if not parent_guid or parent_guid == current.GlobalId or parent_guid in seen:
                return current.GlobalId
            seen.add(parent_guid)
            try:
                current = tool.Ifc.get().by_guid(parent_guid)
            except RuntimeError:
                return current.GlobalId

    @classmethod
    def get_parametric_propagation_targets(cls, element: entity_instance) -> list[entity_instance]:
        """Type-occurrences that should receive parametric updates when
        ``element`` is edited.

        Returns occurrences in ``element``'s Bonsai array family. When
        ``element`` is not part of any array, returns the type-occurrence
        peers that are likewise free of ``BBIM_Array`` (preserving the
        bulk-edit-by-type UX for standalone parametric elements). An
        occurrence whose ``BBIM_Array`` root differs from ``element``'s root
        is excluded — that is the "independent former child" case the array
        apply path produces."""
        occurrences = tool.Ifc.get_all_element_occurrences(element)
        element_pset = ifcopenshell.util.element.get_pset(element, "BBIM_Array")
        if not element_pset:
            return [o for o in occurrences if not ifcopenshell.util.element.get_pset(o, "BBIM_Array")]
        element_root = cls.get_array_root_guid(element)
        return [o for o in occurrences if cls.get_array_root_guid(o) == element_root]

    @classmethod
    def select_only_parent(cls, parent_obj: bpy.types.Object, context: bpy.types.Context) -> None:
        """Post-condition for the user-facing regenerate and finish-edit paths:
        only ``parent_obj`` is selected + active. Grow and shrink otherwise
        diverge on which objects stay selected, surfacing an inconsistency."""
        tool.Blender.select_and_activate_single_object(context, parent_obj)

    @classmethod
    def is_array_child(cls, element: entity_instance) -> bool:
        """True when ``element`` is a child of a parametric array — has a
        BBIM_Array pset whose Parent GUID points to a different element.
        Lighter than ``get_child_layer_index`` (no ``by_guid`` lookup, no
        Data parse); suitable for per-element checks in draw handlers."""
        pset = ifcopenshell.util.element.get_pset(element, "BBIM_Array")
        if not pset:
            return False
        parent_guid = pset.get("Parent")
        return bool(parent_guid) and parent_guid != element.GlobalId

    @classmethod
    def get_child_layer_index(cls, child_element: entity_instance) -> int | None:
        """Index of the layer that produced ``child_element``, or ``None``
        if the child is unparented, missing from the parent's data, or the
        parent's pset is unreadable. Total: never raises."""
        pset = ifcopenshell.util.element.get_pset(child_element, "BBIM_Array")
        if not pset:
            return None
        parent_guid = pset.get("Parent")
        if not parent_guid or parent_guid == child_element.GlobalId:
            return None
        try:
            parent_element = tool.Ifc.get().by_guid(parent_guid)
        except RuntimeError:
            return None
        data_text = ifcopenshell.util.element.get_pset(parent_element, "BBIM_Array", "Data")
        if not data_text:
            return None
        try:
            layers = json.loads(data_text)
        except (ValueError, TypeError):
            return None
        child_guid = child_element.GlobalId
        for i, layer in enumerate(layers):
            if child_guid in layer.get("children", []):
                return i
        return None
