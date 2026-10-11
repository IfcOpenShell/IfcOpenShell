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
    def get_axes_rotation(cls, item: ifcopenshell.entity_instance) -> np.ndarray:
        """A structural item's own axes, as the columns x', y' and z' of a rotation, global ones if it has none"""
        if ccs := getattr(item, "ConditionCoordinateSystem", None):
            return ifcopenshell.util.placement.get_axis2placement(ccs)[:3, :3]
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
    def solve_unknowns(
        cls,
        forces: list[tuple[float, float, float]],
        locks: list[tuple[bool, bool]],
        resultant: tuple[float, float, float],
        resultant_locks: tuple[bool, bool],
    ) -> tuple[Union[list[tuple[float, float, float]], None], Union[tuple[float, float, float], None], str]:
        """Find the two unknowns of concurrent forces and their resultant: magnitudes or directions not locked.

        :param forces: The forces, as they are. An unknown magnitude is solved along the force's direction.
        :param locks: Whether each force's magnitude and direction are known.
        :param resultant: The resultant. Only its direction counts if its magnitude is unknown.
        :param resultant_locks: Whether the resultant's magnitude and direction are known.
        :return: The forces and resultant with the unknowns found, or why they cannot be.
        """
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
