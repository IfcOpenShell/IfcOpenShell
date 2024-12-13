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
import bonsai.tool as tool
import ifcopenshell.util.doc


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

class LoadGroupDecorationData:
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        cls.data = {"load groups to show": cls.load_groups_to_show()}
        cls.is_loaded = True
    
    @classmethod
    def load_groups_to_show(cls):
        ret = []
        abrv = {"LOAD_CASE": "L.Case: ",
                "LOAD_COMBINATION": "L.Comb: ",
                "LOAD_GROUP": "L.Gr: ",
                "USERDEFINED": "U.Def: ",
                "NOTDEFINED": "N.Def: "
        }
        models = tool.Ifc.get().by_type("IfcStructuralAnalysisModel")
        m = models[0]
        props = bpy.context.scene.BIMStructuralProperties
        if props.activity_type == "Action":
            groups = m.LoadedBy or []
            for g in groups:
                ret.append((str(g.id()),".   "+abrv[g.PredefinedType]+"   "+g.Name,""))
                related_objects = [rel.RelatedObjects for rel in g.IsGroupedBy]
                for item in related_objects:
                    for subgoup in [sg for sg in item if sg.is_a("IfcStructuralLoadGroup")]:
                        ret.append((str(subgoup.id()),".       "+abrv[subgoup.PredefinedType]+subgoup.Name,""))

        if props.activity_type == "External Reaction":
            groups = m.HasResults or []
            for g in groups:
                result_name = g.ResultForLoadGroup.Name or ""
                group_name = g.Name or ""
                ret.append((str(g.id()), group_name + " " + result_name,""))

        if len(ret) == 0:
            ret.append(("","",""))
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
        props = bpy.context.active_object.BIMStructuralProperties
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
        cls.data = {"total_models": cls.total_models(), "active_model_ids": cls.active_model_ids()}
        cls.is_loaded = True

    @classmethod
    def total_models(cls):
        return len(tool.Ifc.get().by_type("IfcStructuralAnalysisModel"))

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
            "applicable_structural_load_types": cls.applicable_structural_load_types(),
            "applicable_structural_loads": cls.applicable_structural_loads(),
        }

    @classmethod
    def load_cases(cls):
        results = []
        for load_case in tool.Ifc.get().by_type("IfcStructuralLoadCase"):
            load_groups = []
            for rel in load_case.IsGroupedBy or []:
                for related_object in rel.RelatedObjects:
                    load_groups.append({"id": related_object.id(), "name": related_object.Name or "Unnamed"})
            results.append({"id": load_case.id(), "name": load_case.Name or "Unnamed", "load_groups": load_groups})
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
        props = bpy.context.scene.BIMStructuralProperties
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
        declaration = tool.Ifc.schema().declaration_by_name("IfcStructuralLoadStatic")
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
        declaration = tool.Ifc.schema().declaration_by_name("IfcBoundaryCondition")
        version = tool.Ifc.get_schema()
        return [
            (d.name(), d.name(), ifcopenshell.util.doc.get_entity_doc(version, d.name()).get("description", ""))
            for d in declaration.subtypes()
        ]
