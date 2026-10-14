# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
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

from __future__ import annotations

import fractions
import json
import math
from typing import TYPE_CHECKING, Any, Union

import bpy
import ifcopenshell
import ifcopenshell.api.context
import ifcopenshell.api.pset
import ifcopenshell.api.structural
import ifcopenshell.util.attribute
import ifcopenshell.util.element
import ifcopenshell.util.placement
import ifcopenshell.util.representation
import ifcopenshell.util.unit
import numpy as np

import bonsai.bim.helper
import bonsai.core.tool
import bonsai.tool as tool

if TYPE_CHECKING:
    from ifcopenshell.api.structural.edit_structural_boundary_condition import (
        AttributeDict,
    )

    from bonsai.bim.module.structural.prop import (
        BIMObjectStructuralProperties,
        BIMStructuralProperties,
    )


class Structural(bonsai.core.tool.Structural):
    @classmethod
    def get_structural_props(cls) -> BIMStructuralProperties:
        return bpy.context.scene.BIMStructuralProperties

    @classmethod
    def get_object_structural_props(cls, obj: bpy.types.Object) -> BIMObjectStructuralProperties:
        return obj.BIMStructuralProperties

    @classmethod
    def disable_editing_structural_analysis_model(cls) -> None:
        props = cls.get_structural_props()
        props.active_structural_analysis_model_id = 0

    @classmethod
    def disable_structural_analysis_model_editing_ui(cls) -> None:
        props = cls.get_structural_props()
        props.is_editing = False

    @classmethod
    def enable_editing_structural_analysis_model(cls, model: Union[int, None]) -> None:
        if model:
            props = cls.get_structural_props()
            props.active_structural_analysis_model_id = model

    @classmethod
    def enable_structural_analysis_model_editing_ui(cls) -> None:
        props = cls.get_structural_props()
        props.is_editing = True

    @classmethod
    def enabled_structural_analysis_model_editing_ui(cls) -> bool:
        props = cls.get_structural_props()
        return props.is_editing

    @classmethod
    def ensure_representation_contexts(cls) -> None:
        ifc_file = tool.Ifc.get()
        model = ifcopenshell.util.representation.get_context(ifc_file, "Model")
        if not model:
            model = ifcopenshell.api.context.add_context(
                ifc_file,
                context_type="Model",
                context_identifier="",
                target_view="",
                parent=0,
            )
        graph = ifcopenshell.util.representation.get_context(ifc_file, "Model", "Reference", "GRAPH_VIEW")
        if not graph:
            model = ifcopenshell.api.context.add_context(
                ifc_file,
                context_type="Model",
                context_identifier="Reference",
                target_view="GRAPH_VIEW",
                parent=model,
            )

    @classmethod
    def get_active_structural_analysis_model(cls) -> ifcopenshell.entity_instance:
        props = cls.get_structural_props()
        model = tool.Ifc.get().by_id(props.active_structural_analysis_model_id)
        return model

    @classmethod
    def get_in_plane_components(
        cls,
        mode: str,
        magnitude: float = 0.0,
        angle: float = 0.0,
        rise: float = 0.0,
        run: float = 0.0,
        direction: str = "Q1",
    ) -> tuple[float, float]:
        """Get the horizontal and vertical components of a force in a vertical plane.

        :param mode: ANGLE for an angle in degrees, or SLOPE for a rise over a run.
        :param direction: Q1 to Q8, the eighths of a circle counter-clockwise from +X.
            An angle is measured from the axis the eighth touches, turning into it:
            Q1 from +X towards +Z, Q2 from +Z towards +X, Q3 from +Z towards -X, and
            so on, so that 40 degrees Q4 points 140 degrees from +X. A slope's rise is
            always vertical and its run horizontal, as for a roof pitch, so the eighth
            only gives the quadrant: Q1 and Q2 are up and right, Q3 and Q4 up and left,
            and so on. Negative angles, rises or runs turn the other way.
        :return: The horizontal (X) and vertical (Z) components.
        """
        eighth = int(direction[1])
        if mode == "SLOPE":
            if not (length := math.hypot(rise, run)):
                return 0.0, 0.0
            sign_x = 1 if eighth in (1, 2, 7, 8) else -1
            sign_z = 1 if eighth <= 4 else -1
            return magnitude * sign_x * run / length, magnitude * sign_z * rise / length
        turned = math.radians(angle)
        theta = math.radians(90 * (eighth // 2)) + (turned if eighth % 2 else -turned)
        x, z = magnitude * math.cos(theta), magnitude * math.sin(theta)
        # Keep components along an axis exactly zero rather than rounding noise.
        return (0.0 if abs(x) < 1e-12 * magnitude else x), (0.0 if abs(z) < 1e-12 * magnitude else z)

    @classmethod
    def get_draw_order_key(cls, activity: ifcopenshell.entity_instance) -> tuple[int, int, int]:
        """A sort key for drawing applied loads tip to tail: by their set draw order, else in the order applied"""
        order = ifcopenshell.util.element.get_pset(activity, "BBIM_Structural", "DrawOrder")
        return (0, order, activity.id()) if order is not None else (1, 0, activity.id())

    @classmethod
    def get_chain_activities(
        cls, item: ifcopenshell.entity_instance, load_case: Union[ifcopenshell.entity_instance, None]
    ) -> list[ifcopenshell.entity_instance]:
        """The applied loads on an item in a load case, or in none, in the order they are drawn tip to tail"""

        def is_in_case(activity: ifcopenshell.entity_instance) -> bool:
            groups = [
                r.RelatingGroup
                for r in activity.HasAssignments
                if r.is_a("IfcRelAssignsToGroup") and r.RelatingGroup and r.RelatingGroup.is_a("IfcStructuralLoadGroup")
            ]
            if not load_case:
                return not groups
            # Directly, or through a load group within the case.
            return any(
                g == load_case
                or any(r.is_a("IfcRelAssignsToGroup") and r.RelatingGroup == load_case for r in g.HasAssignments)
                for g in groups
            )

        activities = [
            r.RelatedStructuralActivity for r in item.AssignedStructuralActivity if r.RelatedStructuralActivity
        ]
        return sorted(filter(is_in_case, activities), key=cls.get_draw_order_key)

    @classmethod
    def set_draw_order(cls, activities: list[ifcopenshell.entity_instance]) -> None:
        """Record the order applied loads are drawn tip to tail, which IFC does not order"""
        for order, activity in enumerate(activities, 1):
            cls.edit_bbim_structural(activity, {"DrawOrder": order})

    @classmethod
    def edit_bbim_structural(cls, activity: ifcopenshell.entity_instance, properties: dict[str, Any]) -> None:
        """Set properties of an applied load that Bonsai keeps for itself, in its BBIM_Structural property set"""
        ifc_file = tool.Ifc.get()
        if pset := ifcopenshell.util.element.get_pset(activity, "BBIM_Structural"):
            pset = ifc_file.by_id(pset["id"])
        else:
            pset = ifcopenshell.api.pset.add_pset(ifc_file, product=activity, name="BBIM_Structural")
        ifcopenshell.api.pset.edit_pset(ifc_file, pset=pset, properties=properties)

    @classmethod
    def get_resultant_found(
        cls, locks: list[tuple[bool, bool]], links: Union[list[Union[str, None]], None] = None
    ) -> list[str]:
        """What of a resultant was found, from how many force values were: Edit Resultant finds two unknowns in all.

        :param links: A key per force, the same for forces of equal magnitude, whose magnitudes count as one.
        """
        unknown = sum(not locked for lock in locks for locked in lock)
        # Linked magnitudes unknown together count once; linked to a known one, not at all.
        links = links or [None] * len(locks)
        for key in {k for k in links if k}:
            members = [lock for lock, k in zip(locks, links) if k == key]
            unknown -= sum(not lock[0] for lock in members) - (0 if any(lock[0] for lock in members) else 1)
        return [["magnitude", "direction"], ["magnitude"]][unknown] if unknown < 2 else []

    @classmethod
    def get_locks(cls, activity: ifcopenshell.entity_instance) -> tuple[bool, bool]:
        """Whether an applied load's magnitude and direction are known, so kept when solving for a resultant"""
        pset = ifcopenshell.util.element.get_pset(activity, "BBIM_Structural") or {}
        return pset.get("MagnitudeLocked", True), pset.get("DirectionLocked", True)

    @classmethod
    def set_locks(cls, activity: ifcopenshell.entity_instance, magnitude: bool, direction: bool) -> None:
        if (magnitude, direction) != cls.get_locks(activity):
            cls.edit_bbim_structural(activity, {"MagnitudeLocked": magnitude, "DirectionLocked": direction})

    @classmethod
    def get_known_component(cls, activity: ifcopenshell.entity_instance) -> Union[str, None]:
        """Which component of an applied load is known, X or Z, its magnitude following from it and its direction"""
        component = ifcopenshell.util.element.get_pset(activity, "BBIM_Structural", "KnownComponent")
        return component if component in ("X", "Z") else None

    @classmethod
    def set_known_component(cls, activity: ifcopenshell.entity_instance, component: Union[str, None]) -> None:
        if component != cls.get_known_component(activity):
            cls.edit_bbim_structural(activity, {"KnownComponent": component})

    @classmethod
    def get_push(cls, activity: ifcopenshell.entity_instance) -> bool:
        """Whether an applied load pushes on its item rather than pulls, which IFC's force vector cannot say"""
        return bool(ifcopenshell.util.element.get_pset(activity, "BBIM_Structural", "Push"))

    @classmethod
    def set_push(cls, activity: ifcopenshell.entity_instance, push: bool) -> None:
        if push != cls.get_push(activity):
            cls.edit_bbim_structural(activity, {"Push": push})

    @classmethod
    def get_magnitude_link(cls, activity: ifcopenshell.entity_instance) -> Union[str, None]:
        """The GlobalId of the applied load an applied load's magnitude is linked to, if any"""
        return ifcopenshell.util.element.get_pset(activity, "BBIM_Structural", "SameMagnitudeAs") or None

    @classmethod
    def get_magnitude_ratio(cls, activity: ifcopenshell.entity_instance) -> float:
        """How many times the magnitude of the applied load it is linked to an applied load's magnitude is, 1 if
        equal or unset"""
        return ifcopenshell.util.element.get_pset(activity, "BBIM_Structural", "MagnitudeRatio") or 1.0

    @classmethod
    def set_magnitude_link(
        cls,
        activity: ifcopenshell.entity_instance,
        other: Union[ifcopenshell.entity_instance, None],
        ratio: float = 1.0,
    ) -> None:
        """Link an applied load's magnitude to another's, as equal or a number of times it, as two equal tensions
        are or a quarter of a load, or unlink it"""
        guid = other.GlobalId if other else None
        ratio = None if not guid or math.isclose(ratio, 1.0) else ratio
        if guid != cls.get_magnitude_link(activity) or (ratio or 1.0) != cls.get_magnitude_ratio(activity):
            cls.edit_bbim_structural(activity, {"SameMagnitudeAs": guid, "MagnitudeRatio": ratio})

    @classmethod
    def get_magnitude_groups(
        cls, activities: list[ifcopenshell.entity_instance], overrides: Union[dict[str, Any], None] = None
    ) -> list[Union[str, None]]:
        """A key per applied load, the same for those whose magnitudes are linked, directly or through others
        among them, or None for one linked to none of them.

        :param overrides: Links to take instead of applied loads' own, by GlobalId, as while editing one: the
            other's GlobalId or None, or that and a ratio.
        """
        return cls.get_magnitude_links(activities, overrides)[0]

    @classmethod
    def get_magnitude_links(
        cls, activities: list[ifcopenshell.entity_instance], overrides: Union[dict[str, Any], None] = None
    ) -> tuple[list[Union[str, None]], list[float]]:
        """get_magnitude_groups, with each applied load's magnitude as a factor of a magnitude its group shares,
        from the ratios of their links, 1 for one linked to none"""
        overrides = overrides or {}
        guids = {a.GlobalId for a in activities}
        edges: dict[str, list[tuple[str, float]]] = {guid: [] for guid in guids}
        for activity in activities:
            if activity.GlobalId in overrides:
                link = overrides[activity.GlobalId]
                other, ratio = link if isinstance(link, tuple) else (link, 1.0)
            else:
                other, ratio = cls.get_magnitude_link(activity), cls.get_magnitude_ratio(activity)
            if other in guids and other != activity.GlobalId and ratio:
                # This one's magnitude is ratio times the other's, and the other's this one's over ratio.
                edges[activity.GlobalId].append((other, 1 / ratio))
                edges[other].append((activity.GlobalId, ratio))
        keys: dict[str, str] = {}
        factors: dict[str, float] = {}
        for activity in activities:
            if activity.GlobalId in keys:
                continue
            root, queue = activity.GlobalId, [activity.GlobalId]
            keys[root], factors[root] = root, 1.0
            while queue:
                guid = queue.pop()
                for other, ratio in edges[guid]:
                    if other not in keys:
                        keys[other], factors[other] = root, factors[guid] * ratio
                        queue.append(other)
        counts = {key: list(keys.values()).count(key) for key in set(keys.values())}
        groups = [keys[a.GlobalId] if counts[keys[a.GlobalId]] > 1 else None for a in activities]
        return groups, [factors[a.GlobalId] if group else 1.0 for a, group in zip(activities, groups)]

    @classmethod
    def get_axes_rotation(cls, item: ifcopenshell.entity_instance) -> np.ndarray:
        """A structural item's own axes, as the columns x', y' and z' of a rotation, global ones if it has none"""
        if ccs := getattr(item, "ConditionCoordinateSystem", None):
            return ifcopenshell.util.placement.get_placement(ccs)[:3, :3]
        return np.eye(3)

    @classmethod
    def get_axes_tilt(cls, item: ifcopenshell.entity_instance) -> Union[float, None]:
        """The degrees a structural item's own axes are tilted by in the X-Z plane, x' turning from +X towards +Z.

        :return: 0 if they are not set, or None if they are turned otherwise than in that plane.
        """
        if not getattr(item, "ConditionCoordinateSystem", None):
            return 0.0
        rotation = cls.get_axes_rotation(item)
        x, y = rotation[:, 0], rotation[:, 1]
        if abs(x[1]) > 1e-6 or abs(y[1] - 1) > 1e-6:
            return None
        return math.degrees(math.atan2(x[2], x[0]))

    @classmethod
    def get_axes_slope(cls, item: ifcopenshell.entity_instance) -> Union[tuple[float, float], None]:
        """The rise and run a point's axes were tilted by, if set as a slope and still matching their tilt"""
        pset = ifcopenshell.util.element.get_pset(item, "BBIM_Structural") or {}
        rise, run, tilt = pset.get("AxesRise"), pset.get("AxesRun"), cls.get_axes_tilt(item)
        if rise is None or run is None or tilt is None or not (rise or run):
            return None
        # Against the line's angle from the horizontal, as a slope falling to the right has the same one.
        line = abs(tilt) % 180
        if not math.isclose(math.degrees(math.atan2(abs(rise), abs(run))), min(line, 180 - line), abs_tol=1e-6):
            return None
        return rise, run

    @classmethod
    def set_axes_slope(cls, item: ifcopenshell.entity_instance, slope: Union[tuple[float, float], None]) -> None:
        """Remember the slope a point's axes were tilted by, as an incline is given, or forget it"""
        pset = ifcopenshell.util.element.get_pset(item, "BBIM_Structural") or {}
        rise, run = slope or (None, None)
        # Against what is stored, so that a slope gone stale is cleared too.
        if (rise, run) != (pset.get("AxesRise"), pset.get("AxesRun")):
            cls.edit_bbim_structural(item, {"AxesRise": rise, "AxesRun": run})

    @classmethod
    def get_axes_terms(
        cls, item: ifcopenshell.entity_instance
    ) -> tuple[str, Union[str, None], float, Union[tuple[float, float], None]]:
        """The terms a point's axes were set in, as Edit Axes takes them.

        :return: "THREE_D", or "ANGLE" or "SLOPE" in the X-Z plane, then the eighth x' points into, its angle
            from that eighth's axis, and the slope's rise and run if set as one.
        """
        if cls.get_axes_tilt(item) is None:
            return "THREE_D", None, 0.0, None
        rotation = cls.get_axes_rotation(item)
        eighth, angle, _, _ = cls.get_eighth(rotation[0, 0], rotation[2, 0])
        slope = cls.get_axes_slope(item)
        return ("SLOPE" if slope else "ANGLE"), eighth, angle, slope

    @classmethod
    def to_axes(cls, x: float, z: float, tilt: float) -> tuple[float, float]:
        """Global X and Z components as components along axes tilted by degrees in the X-Z plane, x' and z'"""
        c, s = math.cos(math.radians(tilt)), math.sin(math.radians(tilt))
        return x * c + z * s, -x * s + z * c

    @classmethod
    def from_axes(cls, x: float, z: float, tilt: float) -> tuple[float, float]:
        """Components along axes tilted by degrees in the X-Z plane, x' and z', as global X and Z components"""
        c, s = math.cos(math.radians(tilt)), math.sin(math.radians(tilt))
        return x * c - z * s, x * s + z * c

    @classmethod
    def get_activity_load_case(
        cls, activity: ifcopenshell.entity_instance
    ) -> Union[ifcopenshell.entity_instance, None]:
        """The load case an applied load is in, directly or through a load group within it"""
        for rel in activity.HasAssignments:
            if not (rel.is_a("IfcRelAssignsToGroup") and (group := rel.RelatingGroup)):
                continue
            if group.is_a("IfcStructuralLoadCase"):
                return group
            for parent in group.HasAssignments if group.is_a("IfcStructuralLoadGroup") else []:
                if parent.is_a("IfcRelAssignsToGroup") and parent.RelatingGroup.is_a("IfcStructuralLoadCase"):
                    return parent.RelatingGroup
        return None

    @classmethod
    def get_resultant(
        cls, item: ifcopenshell.entity_instance, load_case: ifcopenshell.entity_instance
    ) -> Union[dict[str, Any], None]:
        """The resultant locked at an item for a load case: MagnitudeLocked, DirectionLocked and Force, if any"""
        return cls.get_resultants(item).get(load_case.GlobalId)

    @classmethod
    def get_resultants(cls, item: ifcopenshell.entity_instance) -> dict[str, dict[str, Any]]:
        value = ifcopenshell.util.element.get_pset(item, "BBIM_Structural", "Resultants")
        try:
            return json.loads(value) if value else {}
        except ValueError:
            return {}

    @classmethod
    def set_resultant(
        cls,
        item: ifcopenshell.entity_instance,
        load_case: ifcopenshell.entity_instance,
        magnitude_locked: bool,
        direction_locked: bool,
        force: tuple[float, float, float],
    ) -> None:
        """Keep a resultant locked at an item for a load case, so that solving keeps it so, or forget it if unlocked.

        A resultant is no IFC entity, so it is kept on the item, by load case GlobalId.
        """
        resultants = cls.get_resultants(item)
        if magnitude_locked or direction_locked:
            resultants[load_case.GlobalId] = {
                "MagnitudeLocked": magnitude_locked,
                "DirectionLocked": direction_locked,
                "Force": [float(c) for c in force],
            }
        elif load_case.GlobalId not in resultants:
            return
        else:
            del resultants[load_case.GlobalId]
        cls.edit_bbim_structural(item, {"Resultants": json.dumps(resultants) if resultants else None})

    @classmethod
    def get_resultant_eighth(
        cls, item: ifcopenshell.entity_instance, load_case: ifcopenshell.entity_instance
    ) -> Union[str, None]:
        """The eighth a resultant's angle is chosen to be measured in at an item for a load case, if any"""
        value = ifcopenshell.util.element.get_pset(item, "BBIM_Structural", "ResultantEighths")
        try:
            eighth = (json.loads(value) if value else {}).get(load_case.GlobalId)
        except ValueError:
            return None
        return eighth if eighth in [f"Q{i}" for i in range(1, 9)] else None

    @classmethod
    def set_resultant_eighth(
        cls, item: ifcopenshell.entity_instance, load_case: ifcopenshell.entity_instance, eighth: Union[str, None]
    ) -> None:
        """Choose the eighth a resultant's angle is measured in, as from -X rather than +Z, or forget it.

        Kept on the item by load case GlobalId, apart from Resultants, which holds only locked ones.
        """
        if eighth == cls.get_resultant_eighth(item, load_case):
            return
        value = ifcopenshell.util.element.get_pset(item, "BBIM_Structural", "ResultantEighths")
        try:
            eighths = json.loads(value) if value else {}
        except ValueError:
            eighths = {}
        if eighth:
            eighths[load_case.GlobalId] = eighth
        else:
            eighths.pop(load_case.GlobalId, None)
        cls.edit_bbim_structural(item, {"ResultantEighths": json.dumps(eighths) if eighths else None})

    @classmethod
    def get_point_items(cls, case: ifcopenshell.entity_instance) -> list[ifcopenshell.entity_instance]:
        """The structural point connections with loads in a load case, directly or in its load groups, by name"""
        items, groups, seen = set(), [case], set()
        while groups:
            group = groups.pop()
            if group.id() in seen:
                continue
            seen.add(group.id())
            for rel in group.IsGroupedBy or []:
                for obj in rel.RelatedObjects:
                    if obj.is_a("IfcStructuralLoadGroup") and not obj.is_a("IfcStructuralLoadCase"):
                        groups.append(obj)
                    elif obj.is_a("IfcStructuralActivity") and (connects := obj.AssignedToStructuralItem):
                        if (item := connects[0].RelatingElement) and item.is_a("IfcStructuralPointConnection"):
                            items.add(item)
        return sorted(items, key=lambda item: (item.Name or "", item.id()))

    @classmethod
    def get_moment_about(
        cls, case: ifcopenshell.entity_instance, centre: ifcopenshell.entity_instance
    ) -> Union[float, None]:
        """The sum of the moments of a load case's point forces about a point connection, counter-clockwise
        positive as the X-Z plane is seen from -Y, in its force unit times the project's length unit, or None if
        it has no point forces. Moments applied as loads are left out, as the drawing leaves them out."""
        location = lambda obj: np.array(obj.matrix_world @ obj.data.vertices[0].co, dtype=float)
        has_point = lambda obj: obj and obj.type == "MESH" and obj.data.vertices
        if not has_point(centre_obj := tool.Ifc.get_object(centre)):
            return None
        at = location(centre_obj)
        length_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
        total, found = 0.0, False
        for item in cls.get_point_items(case):
            if not has_point(obj := tool.Ifc.get_object(item)):
                continue
            for activity in cls.get_chain_activities(item, case):
                load = activity.AppliedLoad
                if not load or not load.is_a("IfcStructuralLoadSingleForce"):
                    continue
                force = np.array([getattr(load, a) or 0.0 for a in ("ForceX", "ForceY", "ForceZ")])
                total += cls.get_moment(at, location(obj), force)[0] / length_scale
                found = True
        return total if found else None

    @classmethod
    def get_moment_centre(cls, load_group: ifcopenshell.entity_instance) -> Union[ifcopenshell.entity_instance, None]:
        """The point connection moments are taken about for a load case or load group, if one is chosen"""
        guid = ifcopenshell.util.element.get_pset(load_group, "BBIM_Structural", "MomentCentre")
        try:
            centre = tool.Ifc.get().by_guid(guid) if guid else None
        except RuntimeError:
            return None  # Removed since.
        return centre if centre and centre.is_a("IfcStructuralPointConnection") else None

    @classmethod
    def set_moment_centre(
        cls, load_group: ifcopenshell.entity_instance, centre: Union[ifcopenshell.entity_instance, None]
    ) -> None:
        """Choose the point connection to take moments about for a load case or load group, or none"""
        cls.edit_bbim_structural(load_group, {"MomentCentre": centre.GlobalId if centre else None})

    @classmethod
    def get_resultant_moment(cls, load_group: ifcopenshell.entity_instance) -> Union[float, None]:
        """The sum of moments about its moment centre a load case keeps, counter-clockwise positive, in its force
        unit times the project's length unit, if it is locked: forces changing re-solve the unknown to keep it"""
        value = ifcopenshell.util.element.get_pset(load_group, "BBIM_Structural", "ResultantMoment")
        return None if value is None else float(value)

    @classmethod
    def set_resultant_moment(cls, load_group: ifcopenshell.entity_instance, moment: Union[float, None]) -> None:
        """Keep a sum of moments about a load case's moment centre, or forget it"""
        cls.edit_bbim_structural(load_group, {"ResultantMoment": moment})

    @classmethod
    def get_moment_centre_unknown(
        cls, load_group: ifcopenshell.entity_instance
    ) -> tuple[Union[str, None], Union[ifcopenshell.entity_instance, None]]:
        """Which place a kept moment finds for a load case, if any. Of the moment centre's: ARM, a force's moment
        arm d, A sliding along it; REACH, its distance r from the force's point, A sliding along r; or SWING, the
        angle of r, phi and alpha with it, A swinging round the point. Or the force's own, its point moving and A
        staying: POINT_X or POINT_Z, along X or Z; POINT_REACH, along the line from A; or POINT_SWING, round A.
        With the applied load it is of."""
        value = ifcopenshell.util.element.get_pset(load_group, "BBIM_Structural", "MomentCentreUnknown")
        try:
            unknown = json.loads(value) if value else {}
            activity = tool.Ifc.get().by_guid(unknown["activity"]) if unknown else None
        except (ValueError, KeyError, RuntimeError):
            return None, None
        kind = unknown.get("kind")
        return (
            (kind, activity)
            if kind in ("ARM", "REACH", "SWING", "POINT_X", "POINT_Z", "POINT_REACH", "POINT_SWING") and activity
            else (None, None)
        )

    @classmethod
    def set_moment_centre_unknown(
        cls,
        load_group: ifcopenshell.entity_instance,
        kind: Union[str, None],
        activity: Union[ifcopenshell.entity_instance, None] = None,
    ) -> None:
        """Choose which of the moment centre's place a kept moment finds, from a force's point, or none"""
        value = json.dumps({"kind": kind, "activity": activity.GlobalId}) if kind and activity else None
        cls.edit_bbim_structural(load_group, {"MomentCentreUnknown": value})

    @classmethod
    def solve_force_point(
        cls,
        points: list[np.ndarray],
        forces: list[np.ndarray],
        centre: np.ndarray,
        moment: float,
        j: int,
        axis: str = "X",
    ) -> tuple[np.ndarray, str]:
        """Find where force j must act, the centre and the other forces staying, for the moments of point forces
        about the centre to sum to a moment, counter-clockwise positive as the X-Z plane is seen from -Y.

        Its moment is its Z component times its distance along X from the centre, less its X component times its
        distance along Z, so it is linear in where it acts along any line, and a sine of its angle round the centre.
        Along Y it would change no moment in the X-Z plane, so Y is not offered.

        :param axis: How its point moves: X or Z; REACH, along the line from the centre; or SWING, round the
            centre, its distance kept, to the nearer of the two places that serve.
        :return: Where it acts, and why not if it cannot be found.
        """
        cross = lambda a, b: a[0] * b[2] - a[2] * b[0]
        total = sum(cross(p - centre, f) for p, f in zip(points, forces))
        point = np.array(points[j], dtype=float)
        r = np.array((point[0] - centre[0], 0.0, point[2] - centre[2]))
        if axis in ("REACH", "SWING") and not np.linalg.norm(r):
            return points[j], f"F{j + 1} acts at the centre: no line from it to move along, or round"
        if axis == "SWING":
            reach, size = float(np.linalg.norm(r)), math.hypot(forces[j][0], forces[j][2])
            need = moment - (total - cross(r, forces[j]))  # Its own moment must make up the rest.
            if not size or abs(need) > reach * size * (1 + 1e-12):
                return points[j], f"No angle round the centre makes that moment with F{j + 1} where it is"
            # reach (cos t F_z - sin t F_x) = need: a cosine of t less the angle of (F_z, -F_x).
            towards = math.atan2(-forces[j][0], forces[j][2])
            turn = math.acos(max(-1.0, min(1.0, need / (reach * size))))
            now = math.atan2(r[2], r[0])
            apart = lambda angle: abs((angle - now + math.pi) % (2 * math.pi) - math.pi)
            angle = min((towards + turn, towards - turn), key=apart)
            point[0], point[2] = centre[0] + reach * math.cos(angle), centre[2] + reach * math.sin(angle)
            return point, ""
        if axis == "REACH":
            along = r / np.linalg.norm(r)
            per = cross(along, forces[j])
            if abs(per) < 1e-12:
                return points[j], f"F{j + 1} runs along the line from the centre: moving it along it changes no moment"
            point += (moment - total) / per * along
            return point, ""
        k, per = (0, forces[j][2]) if axis == "X" else (2, -forces[j][0])
        if abs(per) < 1e-12:
            return points[j], f"F{j + 1} runs along {axis}: moving it along {axis} changes no moment"
        point[k] += (moment - total) / per
        return point, ""

    @classmethod
    def solve_centre_position(
        cls,
        points: list[np.ndarray],
        forces: list[np.ndarray],
        centre: np.ndarray,
        moment: float,
        kind: str,
        j: int,
    ) -> tuple[np.ndarray, str]:
        """Find where the moment centre must be for the moments of point forces about it to sum to a moment,
        counter-clockwise positive as the X-Z plane is seen from -Y, moving it one way from where it is.

        Moving the centre changes every force's moment, as all are taken about it: about a centre A, they sum to
        the sum about the origin less A crossed with their resultant, so the sum is linear in where A is.

        :param points: Where each force acts.
        :param kind: How it moves, from force j: ARM, along j's moment arm, its foot kept on j's line of action;
            REACH, along r, from j's point to A; SWING, round j's point, r's length kept, to the nearer of the two
            places that serve.
        :return: The centre, and why not if it could not be found.
        """
        cross = lambda a, b: a[0] * b[2] - a[2] * b[0]
        resultant = sum(forces)
        about_origin = sum(cross(p, f) for p, f in zip(points, forces))
        # The sum about A is about_origin - cross(A, resultant); find A on its path for it to be the moment.
        point, force = points[j], forces[j]
        if kind == "SWING":
            r = np.array((centre[0] - point[0], 0.0, centre[2] - point[2]))
            reach = float(np.linalg.norm(r))
            size = math.hypot(resultant[0], resultant[2])
            if not reach or not size:
                return centre, "A is at the force's point, or the forces add to nothing: swinging A changes nothing"
            # r (cos t resultant_z - sin t resultant_x) must be this, a cosine of t less the resultant's angle.
            need = about_origin - cross(point, resultant) - moment
            if abs(need) > reach * size * (1 + 1e-12):
                return centre, "No angle of r makes that moment: move A further from the force's point, or closer"
            towards = math.atan2(-resultant[0], resultant[2])
            turn = math.acos(max(-1.0, min(1.0, need / (reach * size))))
            now = math.atan2(r[2], r[0])
            apart = lambda angle: abs((angle - now + math.pi) % (2 * math.pi) - math.pi)
            angle = min((towards + turn, towards - turn), key=apart)
            return np.array((point[0] + reach * math.cos(angle), centre[1], point[2] + reach * math.sin(angle))), ""
        if kind == "ARM":
            _, _, start = cls.get_moment(centre, point, force)
            along = np.array((centre[0] - start[0], 0.0, centre[2] - start[2]))
            if not np.linalg.norm(along):
                along = np.array((-force[2], 0.0, force[0]))  # On the line of action: either side of it.
        else:
            start = np.array(point, dtype=float)
            along = np.array((centre[0] - point[0], 0.0, centre[2] - point[2]))
        if not np.linalg.norm(along):
            return centre, "A is at the force's point: no direction to move it along"
        along /= np.linalg.norm(along)
        per = cross(along, resultant)
        if abs(per) < 1e-12 * max(1.0, np.linalg.norm(resultant)):
            return centre, "Moving A that way changes no moment: the forces' resultant runs along it"
        distance = (about_origin - cross(start, resultant) - moment) / per
        return np.array((start[0] + distance * along[0], centre[1], start[2] + distance * along[2])), ""

    @classmethod
    def solve_moment_unknown(
        cls,
        arms: list[np.ndarray],
        forces: list[np.ndarray],
        locks: list[tuple[bool, bool]],
        moment: float,
        links: Union[list[Union[str, None]], None] = None,
        factors: Union[list[float], None] = None,
    ) -> tuple[list[np.ndarray], str]:
        """Find the one unknown value of point forces for their moments about a centre to sum to a moment,
        counter-clockwise positive as the X-Z plane is seen from -Y. A moment is one equation, so finds one value:
        an unlocked magnitude, forces linked to it following by their ratios, or an unlocked direction, the one
        nearer its present direction of the two that make the moment.

        :param arms: Where each force acts, from the centre, in the units the moment's lengths are in.
        :param locks: Whether each force's magnitude and direction are known.
        :param links: A key per force, the same for forces whose magnitudes are linked, which count as one.
        :param factors: Each force's magnitude as a factor of the magnitude its link shares.
        :return: The forces, the unknown found, and why not if it could not be.
        """
        links = links or [None] * len(forces)
        factors = factors or [1.0] * len(forces)
        forces = [np.array(force, dtype=float) for force in forces]
        moment_of = lambda i, force: arms[i][0] * force[2] - arms[i][2] * force[0]
        unknowns, groups = [], set()
        for i, (magnitude, direction) in enumerate(locks):
            members = [j for j in range(len(forces)) if links[i] and links[j] == links[i]] or [i]
            if not magnitude and not any(locks[j][0] for j in members) and links[i] not in groups:
                unknowns.append(("MAGNITUDE", i, members))
                if links[i]:
                    groups.add(links[i])  # Linked magnitudes, all unknown, are one unknown.
            if not direction:
                unknowns.append(("DIRECTION", i, [i]))
        if len(unknowns) != 1:
            if not unknowns:
                return forces, "Unlock one force's magnitude or direction for the moment to find"
            names = ", ".join(f"F{i + 1} {kind.lower()}" for kind, i, _ in unknowns)
            return forces, f"Unlocked: {names}. A moment finds one value; lock the others"
        kind, j, members = unknowns[0]
        if kind == "MAGNITUDE":
            along = {}
            for i in members:
                if not (planar := math.hypot(forces[i][0], forces[i][2])):
                    return forces, f"F{i + 1} has no direction in the X-Z plane to find its magnitude along"
                along[i] = np.array((forces[i][0], 0.0, forces[i][2])) / planar
            per = sum(factors[i] / factors[j] * moment_of(i, along[i]) for i in members)
            if abs(per) < 1e-12:
                return forces, f"F{j + 1}'s line of action passes through the centre: its magnitude makes no moment"
            rest = sum(moment_of(i, force) for i, force in enumerate(forces) if i not in members)
            magnitude = (moment - rest) / per  # Negative reverses it, a pull becoming a push.
            for i in members:
                forces[i] = magnitude * factors[i] / factors[j] * along[i]
            return forces, ""
        magnitude = math.hypot(forces[j][0], forces[j][2])
        reach = math.hypot(arms[j][0], arms[j][2])
        if not magnitude or not reach:
            return forces, f"F{j + 1} acts at the centre or has no magnitude: no direction of it makes a moment"
        # Its moment is magnitude times reach times the sine of the angle from where it acts to its direction.
        need = moment - sum(moment_of(i, force) for i, force in enumerate(forces) if i != j)
        if abs(need) > magnitude * reach * (1 + 1e-12):
            return forces, f"F{j + 1} makes at most {magnitude * reach:.4g} where it acts, too little for that moment"
        towards = math.atan2(arms[j][2], arms[j][0])
        turn = math.asin(max(-1.0, min(1.0, need / (magnitude * reach))))
        now = math.atan2(forces[j][2], forces[j][0])
        apart = lambda angle: abs((angle - now + math.pi) % (2 * math.pi) - math.pi)
        angle = min((towards + turn, towards + math.pi - turn), key=apart)
        forces[j] = np.array((magnitude * math.cos(angle), 0.0, magnitude * math.sin(angle)))
        return forces, ""

    @classmethod
    def get_moment(cls, centre: np.ndarray, point: np.ndarray, force: np.ndarray) -> tuple[float, float, np.ndarray]:
        """The moment about a centre of a force acting at a point, counter-clockwise positive as the X-Z plane is
        seen from -Y, with its moment arm, the perpendicular distance from the centre to the force's line of
        action, and the foot of the arm on that line.

        It is the force's X and Z components times their distances from the centre, by Varignon's theorem.
        IFC's MomentY, by the right-hand rule about +Y, is its negative.
        """
        dx, dz = point[0] - centre[0], point[2] - centre[2]
        moment = dx * force[2] - dz * force[0]
        planar = math.hypot(force[0], force[2])
        if not planar:
            return 0.0, 0.0, np.array(point, dtype=float)
        along = np.array((force[0], 0.0, force[2])) / planar
        foot = point + float(np.dot(centre - point, along)) * along
        foot[1] = point[1]  # On the force's line of action, in its own X-Z plane.
        return moment, abs(moment) / planar, foot

    @classmethod
    def solve_unknowns(
        cls,
        forces: list[tuple[float, float, float]],
        locks: list[tuple[bool, bool]],
        resultant: tuple[float, float, float],
        resultant_locks: tuple[bool, bool],
        links: Union[list[Union[str, None]], None] = None,
        factors: Union[list[float], None] = None,
    ) -> tuple[Union[list[tuple[float, float, float]], None], Union[tuple[float, float, float], None], str]:
        """Find the two unknowns of concurrent forces and their resultant: magnitudes or directions not locked.

        :param forces: The forces, as they are. An unknown magnitude is solved along the force's direction.
        :param locks: Whether each force's magnitude and direction are known.
        :param resultant: The resultant. Only its direction counts if its magnitude is unknown.
        :param resultant_locks: Whether the resultant's magnitude and direction are known.
        :param links: A key per force, the same for forces of equal magnitude, as two equal cable tensions: their
            magnitudes count as one unknown, or follow one that is known.
        :param factors: Each force's magnitude as a factor of the one its links share, as a quarter of another's;
            all 1, equal, if not given.
        :return: The forces and resultant with the unknowns found, or why they cannot be.
        """
        if links and len({key for key in links if key is not None}) < sum(key is not None for key in links):
            return cls.solve_linked_unknowns(
                forces, locks, resultant, resultant_locks, links, factors or [1.0] * len(forces)
            )
        unknowns = [
            (i, kind)
            for i, lock in enumerate(locks)
            for kind, locked in zip(("MAGNITUDE", "DIRECTION"), lock)
            if not locked
        ]
        unknowns += [(None, kind) for kind, locked in zip(("MAGNITUDE", "DIRECTION"), resultant_locks) if not locked]
        if len(unknowns) != 2:
            # Name them as forces are numbered in reports, F1, F2 and so on, and say what to do.
            subscripts = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")
            named = [
                f"{'R' if i is None else 'F' + str(i + 1).translate(subscripts)} {kind.lower()}" for i, kind in unknowns
            ]
            if not unknowns:
                return None, None, "Nothing is unlocked: unlock two values to find"
            advice = "unlock one more" if len(unknowns) == 1 else f"lock {len(unknowns) - 2} of them"
            return None, None, f"Unlocked: {', '.join(named)}. Two can be found: {advice}"
        forces = list(forces)
        total = lambda vectors: tuple(sum(v[k] for v in vectors) for k in range(3))
        others = lambda i: total([f for k, f in enumerate(forces) if k != i])
        unit = lambda v: tuple(c / math.hypot(*v) for c in v) if math.hypot(*v) else None
        (i, first), (j, second) = unknowns
        if i is None and j is None:
            return forces, total(forces), ""  # Just their sum.
        if i == j:
            forces[i] = tuple(r - o for r, o in zip(resultant, others(i)))  # The force that makes up the rest.
            return forces, resultant, ""
        if "DIRECTION" in (first, second):
            return None, None, "Finding a direction with another unknown is not supported yet"
        if not (direction := unit(forces[i])) or (j is not None and not unit(forces[j])):
            return None, None, "A force with an unknown magnitude needs a direction: give it a magnitude first"
        if j is None:
            # A force's magnitude and the resultant's: others + a * direction = r * along.
            if not (along := unit(resultant)):
                return None, None, "The resultant needs a direction"
            magnitudes = cls.solve_two_force_magnitudes(tuple(-c for c in others(i)), direction, along)
            if magnitudes is None:
                return None, None, "The force and the resultant are parallel, so their magnitudes cannot be found"
            forces[i] = tuple(magnitudes[0] * c for c in direction)
            return forces, tuple(-magnitudes[1] * c for c in along), ""
        kept = total([f for k, f in enumerate(forces) if k not in (i, j)])
        target = tuple(r - k for r, k in zip(resultant, kept))
        magnitudes = cls.solve_two_force_magnitudes(target, direction, unit(forces[j]))
        if magnitudes is None:
            return None, None, "The two forces are parallel, so they cannot make this resultant"
        forces[i] = tuple(magnitudes[0] * c for c in direction)
        forces[j] = tuple(magnitudes[1] * c for c in unit(forces[j]))
        return forces, resultant, ""

    @classmethod
    def get_eighth(cls, x: float, z: float, preferred: Union[str, None] = None) -> tuple[str, float, float, float]:
        """Get which eighth of a circle (Q1 to Q8) in-plane components point into, and their angle from its axis.

        :param preferred: An eighth to use if the components lie in it, such as the one a
            load was entered with, as a force on a boundary lies in two.
        :return: The eighth, the angle in degrees from the axis it touches (0 to 45),
            and the components along and across that axis, as a run and a rise.
        """
        theta = math.degrees(math.atan2(z, x)) % 360

        def get_angle(eighth: int) -> float:
            turned = (theta - 90 * (eighth // 2) + 180) % 360 - 180
            return turned if eighth % 2 else -turned

        eighths = [int(preferred[1])] if preferred else []
        # On a diagonal, measure from the horizontal as statics texts do.
        eighths += [{1: 1, 2: 1, 3: 4, 4: 4, 5: 5, 6: 5, 7: 8, 8: 8}[min(int(theta // 45), 7) + 1]]
        eighths += [min(int(theta // 45), 7) + 1]
        eighth = next(e for e in eighths if -1e-6 <= get_angle(e) <= 45 + 1e-6)
        angle = min(max(get_angle(eighth), 0.0), 45.0) + 0.0  # Not -0.0
        length = math.hypot(x, z)
        return f"Q{eighth}", angle, length * math.cos(math.radians(angle)), length * math.sin(math.radians(angle))

    @classmethod
    def get_angle_from_eighth(cls, x: float, z: float, eighth: str) -> Union[float, None]:
        """The angle in degrees of in-plane components from the axis of an eighth, turning the way it turns, as Q4
        measures from -X turning up and Q6 from -Z turning left: 0 to under 360, or None for no direction"""
        if not (x or z):
            return None
        e = int(eighth[1])
        turned = math.degrees(math.atan2(z, x)) - 90 * (e // 2)
        angle = (turned if e % 2 else -turned) % 360
        return 0.0 if angle > 360 - 1e-6 else angle + 0.0

    @classmethod
    def solve_linked_unknowns(
        cls,
        forces: list[tuple[float, float, float]],
        locks: list[tuple[bool, bool]],
        resultant: tuple[float, float, float],
        resultant_locks: tuple[bool, bool],
        links: list[Union[str, None]],
        factors: list[float],
    ) -> tuple[Union[list[tuple[float, float, float]], None], Union[tuple[float, float, float], None], str]:
        """solve_unknowns for forces whose magnitudes are linked, as equal or in a ratio.

        A linked force follows a known magnitude among its links. Otherwise the linked forces stand in as one
        force along the sum of their directions, each weighted by its factor, whose one magnitude is found and
        given to each by its factor.
        """
        forces, locks = list(forces), list(locks)
        unit = lambda v: tuple(c / math.hypot(*v) for c in v) if math.hypot(*v) else None
        groups: dict[str, list[int]] = {}
        for i, key in enumerate(links):
            if key is not None:
                groups.setdefault(key, []).append(i)
        stand_ins: list[tuple[list[int], tuple[float, float, float]]] = []
        for members in (m for m in groups.values() if len(m) > 1):
            if any(not unit(forces[i]) or not locks[i][1] for i in members):
                return None, None, "Forces of equal magnitude need known directions"
            if known := [i for i in members if locks[i][0]]:
                shared = math.hypot(*forces[known[0]]) / factors[known[0]]
                for i in members:
                    forces[i], locks[i] = tuple(shared * factors[i] * c for c in unit(forces[i])), (True, True)
            else:
                along = tuple(sum(factors[i] * unit(forces[i])[k] for i in members) for k in range(3))
                if not math.hypot(*along):
                    return None, None, "Forces of equal magnitude cancel out, so their magnitude cannot be found"
                stand_ins.append((members, along))
        merged = {i for members, _ in stand_ins for i in members}
        kept = [i for i in range(len(forces)) if i not in merged]
        reduced_forces = [forces[i] for i in kept] + [along for _, along in stand_ins]
        reduced_locks = [locks[i] for i in kept] + [(False, True)] * len(stand_ins)
        solved, solved_resultant, error = cls.solve_unknowns(reduced_forces, reduced_locks, resultant, resultant_locks)
        if error:
            return None, None, error
        for n, i in enumerate(kept):
            forces[i] = solved[n]
        for n, (members, along) in enumerate(stand_ins):
            # The stand-in is the shared magnitude times the sum of the directions.
            shared = sum(s * a for s, a in zip(solved[len(kept) + n], along)) / sum(a * a for a in along)
            for i in members:
                forces[i] = tuple(shared * factors[i] * c for c in unit(forces[i]))
        return forces, solved_resultant, ""

    @classmethod
    def solve_two_force_magnitudes(
        cls, target: tuple[float, float, float], first: tuple[float, float, float], second: tuple[float, float, float]
    ) -> Union[tuple[float, float], None]:
        """Get the magnitudes along two unit directions whose forces add up to a target force.

        A negative magnitude reverses that direction. Returns None if the directions are
        parallel, or if together they cannot make the target, as when it is out of their plane.
        """
        dot = lambda a, b: sum(i * j for i, j in zip(a, b))
        cosine = dot(first, second)
        determinant = 1 - cosine * cosine
        if determinant < 1e-12:
            return None
        along_first, along_second = dot(first, target), dot(second, target)
        a = (along_first - cosine * along_second) / determinant
        b = (along_second - cosine * along_first) / determinant
        error = math.dist([a * i + b * j for i, j in zip(first, second)], target)
        if error > 1e-6 * max(1.0, math.hypot(*target)):
            return None
        return a, b

    @classmethod
    def get_simple_slope(cls, x: float, z: float, max_denominator: int = 24) -> tuple[float, float]:
        """Get a rise and run along the in-plane components x and z, as small whole numbers if they make one.

        For example, components of -160 and -120 give a rise of -3 and a run of -4.
        """
        if not x or not z:
            return (math.copysign(1.0, z) if z else 0.0), (math.copysign(1.0, x) if x else 0.0)
        exact = abs(z) / abs(x)
        ratio = fractions.Fraction(exact).limit_denominator(max_denominator)
        if ratio and math.isclose(float(ratio), exact, rel_tol=1e-6):
            return math.copysign(ratio.numerator, z), math.copysign(ratio.denominator, x)
        length = math.hypot(x, z)
        return z / length, x / length

    @classmethod
    def get_current_structural_analysis_model(cls) -> Union[ifcopenshell.entity_instance, None]:
        """Get the model that new structural items and load cases are assigned to.

        Falls back to the only model in the project when none has been chosen.
        """
        ifc_file = tool.Ifc.get()
        if model_id := cls.get_structural_props().current_structural_analysis_model_id:
            try:
                model = ifc_file.by_id(model_id)
                if model.is_a("IfcStructuralAnalysisModel"):
                    return model
            except RuntimeError:
                pass
        models = ifc_file.by_type("IfcStructuralAnalysisModel")
        return models[0] if len(models) == 1 else None

    @classmethod
    def set_current_structural_analysis_model(cls, model: ifcopenshell.entity_instance) -> None:
        cls.get_structural_props().current_structural_analysis_model_id = model.id()

    @classmethod
    def assign_to_current_structural_analysis_model(cls, element: ifcopenshell.entity_instance) -> None:
        if not (model := cls.get_current_structural_analysis_model()):
            return
        if element.is_a("IfcStructuralLoadGroup"):
            ifcopenshell.api.structural.assign_structural_load_group(
                tool.Ifc.get(), load_groups=[element], structural_analysis_model=model
            )
        elif element.is_a("IfcStructuralItem"):
            ifcopenshell.api.structural.assign_structural_analysis_model(
                tool.Ifc.get(), products=[element], structural_analysis_model=model
            )

    @classmethod
    def get_ifc_structural_analysis_model_attributes(cls, model: Union[int, None]) -> Union[dict[str, Any], None]:
        if model:
            ifc_model = tool.Ifc.get().by_id(model)
            data = ifc_model.get_info()

            del data["OwnerHistory"]

            loaded_by = []
            for load_group in ifc_model.LoadedBy or []:
                loaded_by.append(load_group.id())
            data["LoadedBy"] = loaded_by

            has_results = []
            for result_group in ifc_model.HasResults or []:
                has_results.append(result_group.id())
            data["HasResults"] = has_results

            data["OrientationOf2DPlane"] = (
                ifc_model.OrientationOf2DPlane.id() if ifc_model.OrientationOf2DPlane else None
            )
            data["SharedPlacement"] = ifc_model.SharedPlacement.id() if ifc_model.SharedPlacement else None
            return data

    @classmethod
    def get_ifc_structural_analysis_models(cls) -> dict[int, dict[str, Union[str, None]]]:
        models = {}
        for model in tool.Ifc.get().by_type("IfcStructuralAnalysisModel"):
            models[model.id()] = {"Name": model.Name}
        return models

    @classmethod
    def get_product_or_active_object(cls, product: str) -> Union[bpy.types.Object, None]:
        product = bpy.data.objects.get(product) if product else bpy.context.active_object
        try:
            props = tool.Blender.get_object_bim_props(product)
            if props.ifc_definition_id:
                return product
            else:
                return None
        except:
            return None

    @classmethod
    def get_structural_analysis_model_attributes(cls) -> dict[str, Any]:
        props = cls.get_structural_props()
        attributes = bonsai.bim.helper.export_attributes(props.structural_analysis_model_attributes)
        return attributes

    @classmethod
    def load_structural_analysis_model_attributes(cls, data: dict[str, Any]) -> None:
        props = cls.get_structural_props()
        props.structural_analysis_model_attributes.clear()
        schema = tool.Ifc.schema()
        assert (entity := schema.declaration_by_name("IfcStructuralAnalysisModel").as_entity())
        for attribute in entity.all_attributes():
            data_type = str(attribute.type_of_attribute)
            if "<entity" in data_type:
                continue
            new = props.structural_analysis_model_attributes.add()
            new.name = attribute.name()
            new.is_null = data[attribute.name()] is None
            new.is_optional = attribute.optional()
            if attribute.name() == "PredefinedType":
                new.enum_items = json.dumps(ifcopenshell.util.attribute.get_enum_items(attribute))
                new.data_type = "enum"
                if data[attribute.name()]:
                    new.enum_value = data[attribute.name()]
            else:
                new.string_value = "" if new.is_null else data[attribute.name()]
                new.data_type = "string"

    @classmethod
    def load_structural_analysis_models(cls) -> None:
        models = tool.Structural.get_ifc_structural_analysis_models()
        props = cls.get_structural_props()
        props.structural_analysis_models.clear()
        for ifc_definition_id, model in models.items():
            new = props.structural_analysis_models.add()
            new.ifc_definition_id = ifc_definition_id
            new.name = model["Name"] or "Unnamed"

    @classmethod
    def get_vertex_representation(
        cls, product: ifcopenshell.entity_instance
    ) -> Union[ifcopenshell.entity_instance, None]:
        """
        :param product: IfcStructuralPointConnection
        :return: IfcTopologyRepresentation if it's valid.
        """
        vertex_representation, undefined_representation = None, None
        # At least 1 representation is mandatory in IFC for IfcStructuralPointConnection.
        for rep in product.Representation.Representations:
            rep: ifcopenshell.entity_instance
            rep_type: str = rep.RepresentationType
            if rep_type == "Vertex":
                vertex_representation = rep
                break
            # It's possible to have 'Undefined' or some other non-predefined type.
            elif rep_type not in ("Edge", "Path", "Face", "Shell"):
                undefined_representation = rep

        if not vertex_representation and not undefined_representation:
            return

        # All other checks in this case are covered by IFC validation.
        if vertex_representation:
            items = vertex_representation.Items
            if len(items) != 1:
                return None
            return vertex_representation

        if undefined_representation is None:
            return

        items = undefined_representation.Items
        if len(items) != 1 or not all(item.is_a("IfcVertex") for item in items):
            return None

        return undefined_representation

    @classmethod
    def import_boundary_condition_attributes(
        cls,
        boundary_condition: ifcopenshell.entity_instance,
        props: Union[BIMStructuralProperties, BIMObjectStructuralProperties],
    ) -> None:
        props_attrs = props.boundary_condition_attributes
        props_attrs.clear()
        schema = tool.Ifc.schema()
        # Don't use `import_attributes`,
        # because we need to support 2 types of values for the same props.
        ifc_class = boundary_condition.is_a()
        entity = schema.declaration_by_name(ifc_class).as_entity()
        assert entity
        for attribute in entity.all_attributes():
            attribute_name = attribute.name()
            value = getattr(boundary_condition, attribute_name)
            new = props_attrs.add()
            new.name = attribute_name
            new.ifc_class = ifc_class
            new.is_null = value is None
            new.is_optional = attribute.optional()

            # Select attribute values are typically wrapped.
            if isinstance(value, ifcopenshell.entity_instance):
                value = value.wrappedValue

            if attribute_name == "Name":
                new.string_value = "" if new.is_null else value
                new.data_type = "string"
            else:
                enum_items = [s.name() for s in ifcopenshell.util.attribute.get_select_items(attribute)]
                new.enum_items = json.dumps(enum_items)
                if isinstance(value, bool):
                    new.bool_value = False if new.is_null else value
                    new.data_type = "boolean"
                    new.enum_value = "IfcBoolean"
                else:
                    print(value)
                    new.float_value = 0 if new.is_null else value
                    new.data_type = "float"
                    new.enum_value = next(i for i in enum_items if i != "IfcBoolean")

    @classmethod
    def export_and_apply_boundary_condition_attributes(
        cls,
        boundary_condition: ifcopenshell.entity_instance,
        props: Union[BIMStructuralProperties, BIMObjectStructuralProperties],
    ) -> None:
        attributes: dict[str, AttributeDict] = {}
        for attribute in props.boundary_condition_attributes:
            if attribute.is_null:
                attributes[attribute.name] = {"value": None, "type": "null"}
            elif attribute.data_type == "string":
                attributes[attribute.name] = {"value": attribute.string_value, "type": "string"}
            elif attribute.enum_value == "IfcBoolean":
                attributes[attribute.name] = {"value": attribute.bool_value, "type": attribute.enum_value}
            else:
                attributes[attribute.name] = {"value": attribute.float_value, "type": attribute.enum_value}

        ifc_file = tool.Ifc.get()
        ifcopenshell.api.structural.edit_structural_boundary_condition(
            ifc_file, condition=boundary_condition, attributes=attributes
        )
