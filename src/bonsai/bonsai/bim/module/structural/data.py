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

import math
from typing import Union

import bpy
import ifcopenshell
import ifcopenshell.util.doc
import ifcopenshell.util.structural
import ifcopenshell.util.unit

import bonsai.tool as tool


def refresh():
    StructuralBoundaryConditionsData.is_loaded = False
    ConnectedStructuralMembersData.is_loaded = False
    StructuralMemberData.is_loaded = False
    StructuralConnectionData.is_loaded = False
    StructuralAnalysisModelsData.is_loaded = False
    StructuralLoadCasesData.is_loaded = False
    StructuralLoadCombinationsData.is_loaded = False
    StructuralLoadsData.is_loaded = False
    BoundaryConditionsData.is_loaded = False
    LoadGroupDecorationData.is_loaded = False
    StructuralItemLoadsData.is_loaded = False

    # Keep the loads shown in the viewport in step with every change, undo included.
    from bonsai.bim.module.structural.decorator import LoadsDecorator

    if LoadsDecorator.is_installed:
        LoadsDecorator.update()
        tool.Blender.update_all_viewports()


def get_load_combinations() -> list[ifcopenshell.entity_instance]:
    return [g for g in tool.Ifc.get().by_type("IfcStructuralLoadGroup") if g.PredefinedType == "LOAD_COMBINATION"]


def get_load_cases_and_combinations() -> list[ifcopenshell.entity_instance]:
    return tool.Structural.get_load_cases() + get_load_combinations()


class LoadGroupDecorationData:
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        cls.data = {
            "load_groups_to_show": cls.load_groups_to_show(),
        }
        cls.is_loaded = True

    @classmethod
    def load_groups_to_show(cls) -> list[tuple[str, str, str]]:
        ret: list[tuple[str, str, str]] = []
        # Load cases are the usual choice, so only other kinds of load group are marked.
        kinds = {"LOAD_COMBINATION": " (combination)", "LOAD_GROUP": " (group)"}
        m = tool.Structural.get_current_structural_analysis_model()
        props = tool.Structural.get_structural_props()
        if props.activity_type == "Action":
            # Without an analysis model, loads can still be shown by load case.
            groups = tool.Structural.get_load_cases(m) if m else get_load_cases_and_combinations()
            for g in groups:
                ret.append((str(g.id()), (g.Name or "Unnamed") + kinds.get(g.PredefinedType, ""), ""))
                if g.PredefinedType == "LOAD_COMBINATION":
                    # Its load cases, not the load groups some programs give their factors by.
                    subgroups = list(ifcopenshell.util.structural.get_combination_factors(g))
                else:
                    subgroups = [o for rel in g.IsGroupedBy for o in rel.RelatedObjects]
                for subgroup in [sg for sg in subgroups if sg.is_a("IfcStructuralLoadGroup")]:
                    name = (subgroup.Name or "Unnamed") + kinds.get(subgroup.PredefinedType, "")
                    ret.append((str(subgroup.id()), "    " + name, ""))

        elif props.activity_type == "External Reaction" and m:
            groups = m.HasResults or []
            for g in groups:
                result_name = (g.ResultForLoadGroup.Name or "") if g.ResultForLoadGroup else ""
                group_name = g.Name or ""
                ret.append((str(g.id()), group_name + " " + result_name, ""))

        if len(ret) == 0:
            ret.append(("", "", ""))
        return ret


class StructuralBoundaryConditionsData:
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        cls.data = {"boundary_condition": cls.boundary_condition(), "connection_id": cls.connection_id()}
        cls.is_loaded = True

    @classmethod
    def boundary_condition(cls):
        obj = bpy.context.active_object
        element = tool.Ifc.get_entity(obj)
        if not element or not element.AppliedCondition:
            return
        condition = element.AppliedCondition
        attributes = []
        for name, value in condition.get_info().items():
            if name in ["id", "type", "Name"]:
                continue
            if hasattr(value, "wrappedValue"):
                value = value.wrappedValue
            attributes.append({"name": name, "value": value, "is_bool": isinstance(value, bool)})
        return {"id": condition.id(), "type": condition.is_a(), "attributes": attributes}

    @classmethod
    def connection_id(cls):
        obj = bpy.context.active_object
        element = tool.Ifc.get_entity(obj)
        if element:
            return element.id()


class ConnectedStructuralMembersData:
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        cls.data = {"connections": cls.connections()}
        cls.is_loaded = True

    @classmethod
    def connections(cls):
        obj = bpy.context.active_object
        element = tool.Ifc.get_entity(obj)
        if not element:
            return []
        results = []
        assert obj
        props = tool.Structural.get_object_structural_props(obj)
        for rel in element.ConnectsStructuralMembers or []:
            condition = rel.AppliedCondition
            if condition:
                attributes = []
                for name, value in condition.get_info().items():
                    if name in ["id", "type"] or value is None:
                        continue
                    attributes.append({"name": name, "value": value, "is_bool": isinstance(value, bool)})
                condition = {"id": condition.id(), "type": condition.is_a(), "attributes": attributes}

            results.append(
                {
                    "id": rel.id(),
                    "member_name": rel.RelatingStructuralMember.Name or "Unnamed",
                    "is_active_condition": bool(condition and props.active_boundary_condition == condition["id"]),
                    "condition": condition,
                }
            )
        return results


class StructuralMemberData:
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        obj = bpy.context.active_object
        element = tool.Ifc.get_entity(obj) if obj else None
        unit = ifcopenshell.util.unit.get_project_unit(tool.Ifc.get(), "LENGTHUNIT") if element else None
        cls.data = {
            "active_object_class": element.is_a() if element else None,
            "thickness": getattr(element, "Thickness", None) if element else None,
            "length_unit": ifcopenshell.util.unit.get_unit_symbol(unit) if unit else "",
            "predefined_type": getattr(element, "PredefinedType", None) if element else None,
        }
        cls.is_loaded = True

    @classmethod
    def active_object_class(cls):
        obj = bpy.context.active_object
        element = tool.Ifc.get_entity(obj)
        if element:
            return element.is_a()


class StructuralConnectionData:
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        cls.data = {"active_object_class": cls.active_object_class()}
        cls.is_loaded = True

    @classmethod
    def active_object_class(cls):
        obj = bpy.context.active_object
        element = tool.Ifc.get_entity(obj)
        if element:
            return element.is_a()


class StructuralItemLoadsData:
    """The loads applied to the active structural item, by load case"""

    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        cls.data = {"load_cases": cls.load_cases(), "unloaded_cases": cls.unloaded_cases()}
        cls.is_loaded = True

    @classmethod
    def get_item(cls) -> Union[ifcopenshell.entity_instance, None]:
        element = tool.Ifc.get_entity(bpy.context.active_object) if bpy.context.active_object else None
        return element if element and element.is_a("IfcStructuralItem") else None

    @classmethod
    def get_load_case(
        cls, group: ifcopenshell.entity_instance
    ) -> tuple[ifcopenshell.entity_instance, Union[ifcopenshell.entity_instance, None]]:
        """The load case a load group belongs to, and the group itself if it is a group within the case"""
        if not tool.Structural.is_load_case(group):
            for rel in group.HasAssignments:
                if (
                    rel.is_a("IfcRelAssignsToGroup")
                    and rel.RelatingGroup
                    and tool.Structural.is_load_case(rel.RelatingGroup)
                ):
                    return rel.RelatingGroup, group
        return group, None

    @classmethod
    def load_cases(cls) -> list[dict]:
        if not (item := cls.get_item()):
            return []
        cases: dict[int, dict] = {}
        for rel in item.AssignedStructuralActivity:
            activity = rel.RelatedStructuralActivity
            if not activity:
                continue
            groups = [
                r.RelatingGroup
                for r in activity.HasAssignments
                if r.is_a("IfcRelAssignsToGroup") and r.RelatingGroup and r.RelatingGroup.is_a("IfcStructuralLoadGroup")
            ]
            for group in groups or [None]:
                case, subgroup = cls.get_load_case(group) if group else (None, None)
                entry = cases.setdefault(
                    case.id() if case else 0,
                    {
                        "id": case.id() if case else 0,
                        "name": (case.Name or "Unnamed") if case else "No load case",
                        "loads": [],
                        "forces": [],
                    },
                )
                load = activity.AppliedLoad
                entry["loads"].append(
                    {
                        "activity": activity.id(),
                        "order": activity.id(),
                        "name": (load.Name if load else None) or "Unnamed",
                        "group": (subgroup.Name or "Unnamed") if subgroup else None,
                    }
                )
                if load and load.is_a("IfcStructuralLoadSingleForce") and activity.GlobalOrLocal != "LOCAL_COORDS":
                    entry["forces"].append(tool.Structural.get_force(load))
        for entry in cases.values():
            entry["resultant"] = cls.get_resultant_label(entry.pop("forces"))
            # In the order applied, as they are drawn tip to tail.
            entry["loads"].sort(key=lambda load: load.pop("order"))
        return sorted(cases.values(), key=lambda entry: entry["name"])

    @classmethod
    def get_resultant_label(cls, forces: list[tuple[float, float, float]]) -> Union[str, None]:
        if not forces:
            return None
        x, y, z = (sum(force[k] for force in forces) for k in range(3))
        props = tool.Structural.get_structural_props()
        force_unit = ifcopenshell.util.unit.get_project_unit(tool.Ifc.get(), "FORCEUNIT")
        unit = ifcopenshell.util.unit.get_unit_symbol(force_unit) if force_unit else "N"
        label = f"R = {math.sqrt(x * x + y * y + z * z):.{props.force_decimals}f} {unit}"
        if not y and (x or z):
            label += f" at {math.degrees(math.atan2(z, x)):.{props.angle_decimals}f}°"
        return label

    @classmethod
    def unloaded_cases(cls) -> list[str]:
        if not cls.get_item() or not (model := tool.Structural.get_current_structural_analysis_model()):
            return []
        loaded = {entry["id"] for entry in cls.load_cases()}
        return [
            g.Name or "Unnamed"
            for g in tool.Structural.get_load_cases(model)
            if tool.Structural.is_load_case(g) and g.id() not in loaded
        ]


class StructuralAnalysisModelsData:
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        cls.data = {
            "total_models": cls.total_models(),
            "active_model_ids": cls.active_model_ids(),
            "current_model": cls.current_model(),
            "models": cls.models(),
            "buildings": cls.buildings(),
            "served_buildings": cls.served_buildings(),
            "unserved_buildings": cls.unserved_buildings(),
        }
        cls.is_loaded = True

    @classmethod
    def buildings(cls) -> list[tuple[str, str, str]]:
        return [(str(b.id()), b.Name or "Unnamed", "") for b in tool.Ifc.get().by_type("IfcBuilding")]

    @classmethod
    def served_buildings(cls) -> dict[int, list[tuple[int, str]]]:
        results = {}
        for model in tool.Ifc.get().by_type("IfcStructuralAnalysisModel"):
            buildings = [b for rel in model.ServicesBuildings or () for b in rel.RelatedBuildings]
            results[model.id()] = [(b.id(), b.Name or "Unnamed") for b in buildings]
        return results

    @classmethod
    def unserved_buildings(cls) -> dict[int, list[tuple[str, str, str]]]:
        """The buildings each model does not serve yet, as the choices to assign it to"""
        buildings = tool.Ifc.get().by_type("IfcBuilding")
        results = {}
        for model in tool.Ifc.get().by_type("IfcStructuralAnalysisModel"):
            served = {b for rel in model.ServicesBuildings or () for b in rel.RelatedBuildings}
            results[model.id()] = [(str(b.id()), b.Name or "Unnamed", "") for b in buildings if b not in served]
        return results

    @classmethod
    def total_models(cls):
        return len(tool.Ifc.get().by_type("IfcStructuralAnalysisModel"))

    @classmethod
    def models(cls):
        models = tool.Ifc.get().by_type("IfcStructuralAnalysisModel")
        return [{"id": m.id(), "name": m.Name or "Unnamed"} for m in models]

    @classmethod
    def current_model(cls):
        if model := tool.Structural.get_current_structural_analysis_model():
            return {"id": model.id(), "name": model.Name or "Unnamed"}

    @classmethod
    def active_model_ids(cls):
        obj = bpy.context.active_object
        element = tool.Ifc.get_entity(obj)
        if not element:
            return []
        results = []
        for rel in getattr(element, "HasAssignments", []) or []:
            if rel.is_a("IfcRelAssignsToGroup") and rel.RelatingGroup:
                results.append(rel.RelatingGroup.id())
        return results


class StructuralLoadCasesData:
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        cls.is_loaded = True
        cls.data = {
            "load_cases": cls.load_cases(),
            "models": cls.models(),
            "applicable_structural_load_types": cls.applicable_structural_load_types(),
            "applicable_structural_loads": cls.applicable_structural_loads(),
        }

    @classmethod
    def models(cls):
        return [
            {"id": m.id(), "name": m.Name or "Unnamed"} for m in tool.Ifc.get().by_type("IfcStructuralAnalysisModel")
        ]

    @classmethod
    def activity_name(cls, activity: ifcopenshell.entity_instance) -> str:
        load = activity.AppliedLoad
        rels = activity.AssignedToStructuralItem
        item = rels[0].RelatingElement if rels else None
        return f"{(load.Name if load else None) or 'Unnamed'} on {(item.Name if item else None) or 'Unnamed'}"

    @classmethod
    def load_cases(cls):
        results = []
        for load_case in tool.Structural.get_load_cases():
            load_groups = []
            activities = []
            for rel in load_case.IsGroupedBy or []:
                for related_object in rel.RelatedObjects:
                    if related_object.is_a("IfcStructuralLoadGroup"):
                        load_groups.append({"id": related_object.id(), "name": related_object.Name or "Unnamed"})
                    elif related_object.is_a("IfcStructuralActivity"):
                        rels = related_object.AssignedToStructuralItem
                        activities.append(
                            {
                                "id": related_object.id(),
                                "name": cls.activity_name(related_object),
                                "item": rels[0].RelatingElement.id() if rels else 0,
                                "item_name": (rels[0].RelatingElement.Name if rels else None) or "Unnamed",
                                "order": related_object.id(),
                            }
                        )
            # By item, and each item's in the order applied, as they are drawn tip to tail.
            activities.sort(key=lambda activity: (activity["item"], activity.pop("order")))
            results.append(
                {
                    "id": load_case.id(),
                    "name": load_case.Name or "Unnamed",
                    # Only an IfcStructuralLoadCase has self-weight, not a load group typed LOAD_CASE.
                    "has_self_weight_attribute": load_case.is_a("IfcStructuralLoadCase"),
                    "self_weight": tuple(coefficients)
                    if (coefficients := getattr(load_case, "SelfWeightCoefficients", None))
                    else None,
                    "load_groups": load_groups,
                    "activities": activities,
                    "model_ids": [m.id() for m in load_case.LoadGroupFor],
                }
            )
        return results

    @classmethod
    def applicable_structural_load_types(cls):
        element_classes = set()
        for obj in bpy.context.selected_objects:
            element = tool.Ifc.get_entity(obj)
            if element:
                element_classes.add(element.is_a())
        types = [("IfcStructuralLoadTemperature", "IfcStructuralLoadTemperature", "")]
        if "IfcStructuralPointConnection" in element_classes:
            types.extend(
                [
                    ("IfcStructuralLoadSingleForce", "IfcStructuralLoadSingleForce", ""),
                    ("IfcStructuralLoadSingleDisplacement", "IfcStructuralLoadSingleDisplacement", ""),
                ]
            )
        if "IfcStructuralCurveMember" in element_classes:
            types.append(("IfcStructuralLoadLinearForce", "IfcStructuralLoadLinearForce", ""))
        if "IfcStructuralSurfaceMember" in element_classes:
            types.append(("IfcStructuralLoadPlanarForce", "IfcStructuralLoadPlanarForce", ""))
        return types

    @classmethod
    def applicable_structural_loads(cls):
        props = tool.Structural.get_structural_props()
        results = []
        for load in tool.Ifc.get().by_type("IfcStructuralLoad"):
            if not load.Name or not load.is_a(props.applicable_structural_load_types):
                continue
            results.append((str(load.id()), load.Name or "Unnamed", ""))
        return results


class StructuralLoadCombinationsData:
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        cls.data = {"load_combinations": cls.load_combinations()}
        cls.is_loaded = True

    @classmethod
    def load_combinations(cls) -> list[dict]:
        results = []
        for combination in get_load_combinations():
            load_cases = [
                c
                for c in ifcopenshell.util.structural.get_combination_factors(combination)
                if tool.Structural.is_load_case(c)
            ]
            results.append(
                {
                    "id": combination.id(),
                    "name": combination.Name or "Unnamed",
                    "purpose": combination.Purpose or "",
                    "total_load_cases": len(load_cases),
                    "model_ids": [m.id() for m in combination.LoadGroupFor],
                }
            )
        return results


class StructuralLoadsData:
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        cls.data = {
            "total_loads": cls.total_loads(),
            "load_classes": cls.load_classes(),
            "structural_load_types": cls.structural_load_types(),
        }
        cls.is_loaded = True

    @classmethod
    def total_loads(cls):
        return len(tool.Ifc.get().by_type("IfcStructuralLoad"))

    @classmethod
    def load_classes(cls):
        return {l.id(): l.is_a() for l in tool.Ifc.get().by_type("IfcStructuralLoad")}

    @classmethod
    def structural_load_types(cls):
        declaration = tool.Ifc.schema().declaration_by_name("IfcStructuralLoadStatic").as_entity()
        assert declaration
        version = tool.Ifc.get_schema()
        return [
            (d.name(), d.name(), ifcopenshell.util.doc.get_entity_doc(version, d.name()).get("description", ""))
            for d in declaration.subtypes()
        ]


class BoundaryConditionsData:
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        cls.data = {
            "total_conditions": cls.total_conditions(),
            "condition_classes": cls.condition_classes(),
            "boundary_condition_types": cls.boundary_condition_types(),
        }
        cls.is_loaded = True

    @classmethod
    def total_conditions(cls):
        return len(tool.Ifc.get().by_type("IfcBoundaryCondition"))

    @classmethod
    def condition_classes(cls):
        return {c.id(): c.is_a() for c in tool.Ifc.get().by_type("IfcBoundaryCondition")}

    @classmethod
    def boundary_condition_types(cls):
        declaration = tool.Ifc.schema().declaration_by_name("IfcBoundaryCondition").as_entity()
        assert declaration
        version = tool.Ifc.get_schema()
        return [
            (d.name(), d.name(), ifcopenshell.util.doc.get_entity_doc(version, d.name()).get("description", ""))
            for d in declaration.subtypes()
        ]
