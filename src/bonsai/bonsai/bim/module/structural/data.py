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

import bpy
import ifcopenshell.util.doc

import bonsai.tool as tool


def refresh():
    StructuralBoundaryConditionsData.is_loaded = False
    ConnectedStructuralMembersData.is_loaded = False
    StructuralMemberData.is_loaded = False
    StructuralConnectionData.is_loaded = False
    StructuralAnalysisModelsData.is_loaded = False
    StructuralLoadCasesData.is_loaded = False
    StructuralLoadsData.is_loaded = False
    BoundaryConditionsData.is_loaded = False
    LoadGroupDecorationData.is_loaded = False

    # Keep the loads shown in the viewport in step with every change, undo included.
    from bonsai.bim.module.structural.decorator import LoadsDecorator

    if LoadsDecorator.is_installed:
        LoadsDecorator.update()
        tool.Blender.update_all_viewports()


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
            groups = (m.LoadedBy or []) if m else tool.Ifc.get().by_type("IfcStructuralLoadCase")
            for g in groups:
                ret.append((str(g.id()), (g.Name or "Unnamed") + kinds.get(g.PredefinedType, ""), ""))
                related_objects = [rel.RelatedObjects for rel in g.IsGroupedBy]
                for item in related_objects:
                    for subgoup in [sg for sg in item if sg.is_a("IfcStructuralLoadGroup")]:
                        name = (subgoup.Name or "Unnamed") + kinds.get(subgoup.PredefinedType, "")
                        ret.append((str(subgoup.id()), "    " + name, ""))

        elif props.activity_type == "External Reaction" and m:
            groups = m.HasResults or []
            for g in groups:
                result_name = g.ResultForLoadGroup.Name or ""
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
            if name in ["id", "type"] or value is None:
                continue
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
        cls.data = {"active_object_class": cls.active_object_class()}
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


class StructuralAnalysisModelsData:
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        cls.data = {
            "total_models": cls.total_models(),
            "active_model_ids": cls.active_model_ids(),
            "current_model": cls.current_model(),
        }
        cls.is_loaded = True

    @classmethod
    def total_models(cls):
        return len(tool.Ifc.get().by_type("IfcStructuralAnalysisModel"))

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
            if rel.is_a("IfcRelAssignsToGroup"):
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
        for load_case in tool.Ifc.get().by_type("IfcStructuralLoadCase"):
            load_groups = []
            activities = []
            for rel in load_case.IsGroupedBy or []:
                for related_object in rel.RelatedObjects:
                    if related_object.is_a("IfcStructuralLoadGroup"):
                        load_groups.append({"id": related_object.id(), "name": related_object.Name or "Unnamed"})
                    elif related_object.is_a("IfcStructuralActivity"):
                        activities.append({"id": related_object.id(), "name": cls.activity_name(related_object)})
            results.append(
                {
                    "id": load_case.id(),
                    "name": load_case.Name or "Unnamed",
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
