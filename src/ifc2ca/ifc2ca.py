# Ifc2CA - IFC Code_Aster utility
# Copyright (C) 2020, 2021, 2023, 2024 Ioannis P. Christovasilis <ipc@aethereng.com>
#
# This file is part of Ifc2CA.
#
# Ifc2CA is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ifc2CA is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Ifc2CA.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import annotations
import json
import os
import subprocess
from copy import deepcopy
from pathlib import Path

import ifcopenshell as ios

# import ifcopenshell.geom
import ifcopenshell.util.element
import ifcopenshell.util.placement
import ifcopenshell.util.representation

# import ifcopenshell.util.shape
import numpy as np
from jinja2 import Environment, FileSystemLoader

from . import ca2ifc
from .scriptCodeAster import CommandFileConstructor


class Ifc2CA:
    file: ifcopenshell.file

    folder_path = None
    salome_path = None
    model_keys = ["id", "type", "GlobalId", "Name", "LoadedBy", "HasResults"]
    member_keys = ["id", "type", "GlobalId", "Name", "Thickness"]
    connection_keys = ["id", "type", "GlobalId", "Name"]
    material_keys = ["id", "type", "Name", "Category"]
    material_property_keys = ["MassDensity", "YoungModulus", "PoissonRatio", "ShearModulus"]
    profile_property_keys = ["CrossSectionArea", "MomentOfInertiaY", "MomentOfInertiaZ", "TorsionalConstantX"]
    fixed_conditions = {
        "Vertex": dict(zip(["dx", "dy", "dz", "drx", "dry", "drz"], [True, True, True, True, True, True])),
        "Edge": dict(zip(["dx", "dy", "dz", "drx", "dry", "drz"], [True, True, True, True, True, True])),
        "Face": dict(zip(["dx", "dy", "dz"], [True, True, True])),
    }

    def __init__(self, path: os.PathLike | str):
        self.path = Path(path)
        self.tol = 1e-06
        self.file = ios.open(self.path)
        self.folder_path = self.path.parent / f"{self.path.stem}_ifc2ca"
        self.env = Environment(loader=FileSystemLoader(Path(__file__).parent / "templates"))

    # expose GET api functions
    ## functions related to models
    def get_models(self):
        return self.file.by_type("IfcStructuralAnalysisModel")

    def get_context(self):
        return ifcopenshell.util.representation.get_context(self.file, "Model", "Reference", "GRAPH_VIEW")

    ## functions related to members and connections
    def get_items(self, model: ios.entity_instance | None = None):
        if model is not None:
            return ifcopenshell.util.element.get_grouped_by(model)
        return self.file.by_type("IfcStructuralItem")

    def get_elements(self, model: ios.entity_instance | None = None):
        if model is not None:
            return [
                item for item in ifcopenshell.util.element.get_grouped_by(model) if item.is_a("IfcStructuralMember")
            ]
        return self.file.by_type("IfcStructuralMember")

    def get_connections(self, model: ios.entity_instance | None = None):
        if model is not None:
            return [
                item for item in ifcopenshell.util.element.get_grouped_by(model) if item.is_a("IfcStructuralConnection")
            ]
        return self.file.by_type("IfcStructuralConnection")

    ## functions related to loads and load groups
    def get_actions(
        self,
        load_group: ios.entity_instance | None = None,
        element: ios.entity_instance | None = None,
        load_group_ids: list[int] | None = None,
    ):
        if load_group is not None:
            actions = [
                item
                for item in ifcopenshell.util.element.get_grouped_by(load_group)
                if item.is_a("IfcStructuralAction")
            ]
            return actions

        if element is not None:
            actions = [
                item.RelatedStructuralActivity
                for item in element.AssignedStructuralActivity
                if item.RelatedStructuralActivity.is_a("IfcStructuralAction")
            ]
            if load_group_ids is None:
                return actions

            actions = [action for action in actions if self.get_load_group(action).id() in load_group_ids]
            return actions

        return [item for item in self.file.by_type("IfcStructuralAction")]

    def get_load_group(self, action: ios.entity_instance):
        if action.HasAssignments is None:
            return None
        load_groups = [
            item.RelatingGroup
            for item in action.HasAssignments
            if (item.RelatingGroup.is_a("IfcStructuralLoadGroup") and item.RelatingGroup.PredefinedType == "LOAD_GROUP")
        ]
        if len(load_groups):
            return load_groups[0]
        return None

    def get_reactions(
        self, result_group: ios.entity_instance | None = None, element: ios.entity_instance | None = None
    ):
        if result_group is not None:
            reactions = [
                item
                for item in ifcopenshell.util.element.get_grouped_by(result_group)
                if item.is_a("IfcStructuralReaction")
            ]
            return reactions

        if element is not None:
            reactions = [
                item.RelatedStructuralActivity
                for item in element.AssignedStructuralActivity
                if item.RelatedStructuralActivity.is_a("IfcStructuralReaction")
            ]
            return reactions

        return [item for item in self.file.by_type("IfcStructuralReaction")]

    def get_load_groups(self, load_case: ios.entity_instance | None = None, model: ios.entity_instance | None = None):
        if load_case is not None:
            load_groups = [
                item
                for item in ifcopenshell.util.element.get_grouped_by(load_case)
                if (item.is_a("IfcStructuralLoadGroup") and item.PredefinedType == "LOAD_GROUP")
            ]
            return load_groups

        if model is not None:
            load_group_set = set()
            for load_case in self.get_load_cases(model):
                load_groups = set(
                    [
                        item
                        for item in ifcopenshell.util.element.get_grouped_by(load_case)
                        if (item.is_a("IfcStructuralLoadGroup") and item.PredefinedType == "LOAD_GROUP")
                    ]
                )
                load_group_set = load_group_set.union(load_groups)
            load_groups = list(load_group_set)
            load_groups.sort(key=lambda x: x.id())

            return load_groups

        return [item for item in self.file.by_type("IfcStructuralLoadGroup") if item.PredefinedType == "LOAD_GROUP"]

    ## functions related to load cases and load combinations
    def get_load_cases(self, model: ios.entity_instance | None = None, load_group: ios.entity_instance | None = None):
        if model is not None:
            load_case_set = set(self.get_analysis_load_cases(model))
            for comb in self.get_load_combinations(model):
                load_cases = set(
                    [
                        item
                        for item in ifcopenshell.util.element.get_grouped_by(comb)
                        if (item.is_a("IfcStructuralLoadCase") and item.PredefinedType == "LOAD_CASE")
                    ]
                )
                load_case_set = load_case_set.union(load_cases)
            load_cases = list(load_case_set)
            load_cases.sort(key=lambda x: x.id())

            return load_cases

        if load_group is not None:
            if load_group.HasAssignments is None:
                return []
            load_cases = [
                item.RelatingGroup
                for item in load_group.HasAssignments
                if (
                    item.RelatingGroup.is_a("IfcStructuralLoadCase")
                    and item.RelatingGroup.PredefinedType == "LOAD_CASE"
                )
            ]
            return load_cases

        return [item for item in self.file.by_type("IfcStructuralLoadCase") if item.PredefinedType == "LOAD_CASE"]

    def get_load_combinations(self, model: ios.entity_instance | None = None):
        if model is not None:
            if model.LoadedBy is None:
                return []
            load_groups = [
                item
                for item in model.LoadedBy
                if (item.is_a("IfcStructuralLoadGroup") and item.PredefinedType == "LOAD_COMBINATION")
            ]
            load_groups.sort(key=lambda x: x.id())
            return load_groups

        return [
            item for item in self.file.by_type("IfcStructuralLoadGroup") if item.PredefinedType == "LOAD_COMBINATION"
        ]

    def get_combination_assignments(self, load_combination: ios.entity_instance):
        return [
            rel for rel in self.file.by_type("IfcRelAssignsToGroup") if rel.RelatingGroup.id() == load_combination.id()
        ]

    def get_analysis_load_cases(self, model: ios.entity_instance):
        if model.LoadedBy is None:
            return []
        return [
            item
            for item in model.LoadedBy
            if (item.is_a("IfcStructuralLoadCase") and item.PredefinedType == "LOAD_CASE")
        ]

    def get_analysis_cases(self, model: ios.entity_instance):
        if model.LoadedBy is None:
            return []
        return list(model.LoadedBy)

    def get_result_cases(self, model: ios.entity_instance):
        if model.HasResults is None:
            return []
        return list(model.HasResults)

    # expose GET/PARSE api functions
    # functions to convert to json
    def get_ref_id(self, entity: ios.entity_instance):
        return f"{entity.is_a()}|{entity.id()}"

    def parse_transformation_matrix(self, matrix: np.ndarray):
        x_axis = np.round([v[0] for v in matrix][:3], 6)
        y_axis = np.round([v[1] for v in matrix][:3], 6)
        z_axis = np.round([v[2] for v in matrix][:3], 6)

        origin = np.round([v[3] for v in matrix][:3], 6)
        orientation = np.array([x_axis, y_axis, z_axis])

        return origin, orientation

    def parse_representation(self, representation: ios.entity_instance):
        repr_item = representation.Items[0]
        if representation.RepresentationType == "Vertex":
            geometry = repr_item.VertexGeometry.Coordinates

        elif representation.RepresentationType == "Edge":
            geometry = [
                repr_item.EdgeStart.VertexGeometry.Coordinates,
                repr_item.EdgeEnd.VertexGeometry.Coordinates,
            ]

        elif representation.RepresentationType == "Face":
            geometry = [x.EdgeStart.VertexGeometry.Coordinates for x in repr_item.Bounds[0].Bound.EdgeList]

        else:
            print(representation)
        return geometry

    def parse_material(self, material: ios.entity_instance):
        data = {k: v for k, v in material.get_info().items() if k in self.material_keys}
        data["ref_id"] = self.get_ref_id(material)

        psets = ifcopenshell.util.element.get_psets(material)
        properties = dict()
        for _, pset_properties in psets.items():
            properties |= pset_properties
        if len(properties):
            data["properties"] = {k: v for k, v in properties.items() if k in self.material_property_keys}
            if "PoissonRatio" not in data["properties"]:
                if "ShearModulus" in data["properties"]:
                    PoissonRatio = round(
                        data["properties"]["YoungModulus"] / 2.0 / data["properties"]["ShearModulus"] - 1, 3
                    )
                else:
                    PoissonRatio = 0.0
                data["properties"]["PoissonRatio"] = PoissonRatio
        else:
            data["properties"] = None

        return data

    def parse_profile(self, profile: ios.entity_instance):
        data = profile.get_info()
        data["ref_id"] = self.get_ref_id(profile)

        psets = ifcopenshell.util.element.get_psets(profile)
        properties = dict()
        for _, pset_properties in psets.items():
            properties |= pset_properties
        if len(properties):
            data["properties"] = {k: v for k, v in properties.items() if k in self.profile_property_keys}
        else:
            if profile.is_a("IfcIShapeProfileDef"):
                tf = profile.FlangeThickness
                tw = profile.WebThickness
                h = profile.OverallDepth
                b = profile.OverallWidth

                A = b * h - (b - tw) * (h - 2 * tf)
                Iy = b * (h**3) / 12 - (b - tw) * ((h - 2 * tf) ** 3) / 12
                Iz = (2 * tf) * (b**3) / 12 + (h - 2 * tf) * (tw**3) / 12
                Jx = 1 / 3 * ((h - tf) * (tw**3) + 2 * b * (tf**3))

                data["properties"] = {
                    "CrossSectionArea": A,
                    "MomentOfInertiaY": Iy,
                    "MomentOfInertiaZ": Iz,
                    "TorsionalConstantX": Jx,
                }

            else:
                data["properties"] = None

        return data

    def parse_applied_condition(
        self, condition: ios.entity_instance, geometry_type: str, should_fix_condition: bool = False
    ):
        if condition is None:
            if should_fix_condition:
                return self.fixed_conditions[geometry_type]
            else:
                return None

        if geometry_type == "Vertex":
            return {
                "dx": condition.TranslationalStiffnessX.wrappedValue,
                "dy": condition.TranslationalStiffnessY.wrappedValue,
                "dz": condition.TranslationalStiffnessZ.wrappedValue,
                "drx": condition.RotationalStiffnessX.wrappedValue,
                "dry": condition.RotationalStiffnessY.wrappedValue,
                "drz": condition.RotationalStiffnessZ.wrappedValue,
            }

        if geometry_type == "Edge":
            return {
                "dx": condition.TranslationalStiffnessByLengthX.wrappedValue,
                "dy": condition.TranslationalStiffnessByLengthY.wrappedValue,
                "dz": condition.TranslationalStiffnessByLengthZ.wrappedValue,
                "drx": condition.RotationalStiffnessByLengthX.wrappedValue,
                "dry": condition.RotationalStiffnessByLengthY.wrappedValue,
                "drz": condition.RotationalStiffnessByLengthZ.wrappedValue,
            }

        if geometry_type == "Face":
            return {
                "dx": condition.TranslationalStiffnessByAreaX.wrappedValue,
                "dy": condition.TranslationalStiffnessByAreaY.wrappedValue,
                "dz": condition.TranslationalStiffnessByAreaZ.wrappedValue,
            }

    def parse_element(self, element: ios.entity_instance):
        data = {k: v for k, v in element.get_info().items() if k in self.member_keys}

        data["ObjectType"] = ifcopenshell.util.element.get_predefined_type(element)
        data["ref_id"] = self.get_ref_id(element)
        representation = ifcopenshell.util.representation.get_representation(element, self.get_context())
        repr_item = representation.Items[0]
        data["geometry_type"] = representation.RepresentationType
        data["geometry"] = self.parse_representation(representation)

        if element.is_a("IfcStructuralCurveMember"):
            placement = ifcopenshell.util.placement.a2p(
                data["geometry"][0],
                element.Axis.DirectionRatios,
                [c2 - c1 for c1, c2 in zip(data["geometry"][0], data["geometry"][1])],
            )

        elif element.is_a("IfcStructuralSurfaceMember"):
            placement = ifcopenshell.util.placement.get_axis2placement(repr_item.FaceSurface.Position)

        origin, orientation = self.parse_transformation_matrix(placement)
        data["origin"] = origin
        data["orientation"] = orientation
        if element.is_a("IfcStructuralSurfaceMember") and not repr_item.SameSense:
            data["orientation"] *= -1

        materialset = ifcopenshell.util.element.get_material(element, should_skip_usage=True)
        if element.is_a() == "IfcStructuralCurveMember":
            data["material"] = materialset.MaterialProfiles[0].Material
            data["profile"] = materialset.MaterialProfiles[0].Profile
            # data["profile"] = ifcopenshell.util.shape.get_profiles(element)[0]
        elif element.is_a() == "IfcStructuralSurfaceMember":
            if materialset.is_a() == "IfcMaterial":
                data["material"] = materialset
            else:
                data["material"] = materialset.MaterialLayers[0].Material

        return data

    def parse_connection(self, connection: ios.entity_instance):
        data = {k: v for k, v in connection.get_info().items() if k in self.connection_keys}

        data["ObjectType"] = ifcopenshell.util.element.get_predefined_type(connection)
        data["ref_id"] = self.get_ref_id(connection)
        representation = ifcopenshell.util.representation.get_representation(connection, self.get_context())
        repr_item = representation.Items[0]
        data["geometry_type"] = representation.RepresentationType
        data["geometry"] = self.parse_representation(representation)

        if connection.is_a("IfcStructuralPointConnection"):
            if connection.ConditionCoordinateSystem is not None:
                placement = ifcopenshell.util.placement.get_axis2placement(connection.ConditionCoordinateSystem)
            else:
                placement = np.eye(4)
                for i, v in enumerate(placement[:3]):
                    v[3] = data["geometry"][i]

        if connection.is_a("IfcStructuralCurveConnection"):
            placement = ifcopenshell.util.placement.a2p(
                data["geometry"][0],
                connection.Axis.DirectionRatios,
                [c2 - c1 for c1, c2 in zip(data["geometry"][0], data["geometry"][1])],
            )

        elif connection.is_a("IfcStructuralSurfaceConnection"):
            placement = ifcopenshell.util.placement.get_axis2placement(repr_item.FaceSurface.Position)

        origin, orientation = self.parse_transformation_matrix(placement)
        data["origin"] = origin
        data["orientation"] = orientation
        if connection.is_a("IfcStructuralSurfaceConnection") and not repr_item.SameSense:
            data["orientation"] *= -1

        data["appliedCondition"] = self.parse_applied_condition(connection.AppliedCondition, data["geometry_type"])
        return data

    def parse_element_connections(self, element: dict, connections: list[dict]):
        ifc_element = self.file.by_id(element["id"])
        connection_ids = [c["id"] for c in connections]
        rels = [rel for rel in ifc_element.ConnectedBy if rel.RelatedStructuralConnection.id() in connection_ids]

        data = [dict() for _ in rels]
        for i, rel in enumerate(rels):
            data[i]["ref_id"] = self.get_ref_id(rel)
            data[i]["related_connection"] = self.get_ref_id(rel.RelatedStructuralConnection)
            data[i]["relating_element"] = self.get_ref_id(rel.RelatingStructuralMember)

            if rel.ConditionCoordinateSystem is None:
                data[i]["orientation"] = element["orientation"]
            else:
                placement = ifcopenshell.util.placement.get_axis2placement(rel.ConditionCoordinateSystem)
                _, orientation = self.parse_transformation_matrix(placement)
                data[i]["orientation"] = element["orientation"].dot(orientation)

            conn_repr = ifcopenshell.util.representation.get_representation(
                rel.RelatedStructuralConnection, self.get_context()
            )
            data[i]["geometry_type"] = conn_repr.RepresentationType
            data[i]["appliedCondition"] = self.parse_applied_condition(
                rel.AppliedCondition, data[i]["geometry_type"], should_fix_condition=True
            )

            if rel.is_a("IfcRelConnectsWithEccentricity") and rel.RelatedStructuralConnection.is_a(
                "IfcStructuralPointConnection"
            ):
                point_on_element = rel.ConnectionConstraint.PointOnRelatingElement.Coordinates
                element_length = round(
                    np.linalg.norm(np.array(element["geometry"][0]) - np.array(element["geometry"][1])), 6
                )
                x_local = min(max(0.0, point_on_element[0]), element_length)
                point_on_element = (
                    np.array(element["geometry"][0])
                    + (np.array(element["geometry"][1]) - np.array(element["geometry"][0])) * x_local / element_length
                )
                point_on_element = np.round(point_on_element, 6)
                data[i]["eccentricity"] = {"point_on_element": point_on_element}
            else:
                data[i]["eccentricity"] = (
                    rel.ConnectionConstraint.get_info(recursive=True)
                    if rel.is_a("IfcRelConnectsWithEccentricity")
                    else None
                )

        return data

    def parse_element_loads(
        self,
        element: dict,
        load_group_ids: list[int],
        load_cases: list[ios.entity_instance],
    ):
        ifc_element = self.file.by_id(element["id"])
        actions = self.get_actions(element=ifc_element, load_group_ids=load_group_ids)
        if not len(actions):
            return None

        if element["geometry_type"] in ["Vertex", "Edge"]:
            data = {
                "actions": [],
                "loadGroups": [],
                "loadsLC": {
                    "FX": np.array([0.0 for _ in load_cases]),
                    "FY": np.array([0.0 for _ in load_cases]),
                    "FZ": np.array([0.0 for _ in load_cases]),
                    "MX": np.array([0.0 for _ in load_cases]),
                    "MY": np.array([0.0 for _ in load_cases]),
                    "MZ": np.array([0.0 for _ in load_cases]),
                },
                "loadsCOMB": {
                    "FX": None,
                    "FY": None,
                    "FZ": None,
                    "MX": None,
                    "MY": None,
                    "MZ": None,
                },
            }
        elif element["geometry_type"] == "Face":
            data = {
                "actions": [],
                "loadGroups": [],
                "loadsLC": {
                    "FX": np.array([0.0 for _ in load_cases]),
                    "FY": np.array([0.0 for _ in load_cases]),
                    "FZ": np.array([0.0 for _ in load_cases]),
                },
                "loadsCOMB": {
                    "FX": None,
                    "FY": None,
                    "FZ": None,
                },
            }

        for action in actions:
            self.add_action_loads(element, action, data, load_cases)

        loadsLC = deepcopy(data["loadsLC"])
        loadsCOMB = deepcopy(data["loadsCOMB"])
        for key, load in data["loadsLC"].items():
            if np.max(np.abs(load)) == 0.0:
                del loadsLC[key]
                del loadsCOMB[key]
        if len(loadsLC) == 0:
            print(
                f"Actions {[self.get_ref_id(action) for action in actions]} for element {element['ref_id']} not accounted for in the load assignments"
            )
            return None
        else:
            data["loadsLC"] = loadsLC
            data["loadsCOMB"] = loadsCOMB

        return data

    def add_action_loads(
        self,
        element: dict,
        action: ios.entity_instance,
        data: dict,
        load_cases: list[ios.entity_instance],
    ):
        load_group = self.get_load_group(action)
        load_group_coeff = 1.0 if load_group.Coefficient is None else load_group.Coefficient
        active_load_case_ids = [lc.id() for lc in self.get_load_cases(load_group=load_group)]
        load = action.AppliedLoad

        data["actions"].append(action.get_info() | {"AppliedLoad": action.AppliedLoad.get_info()})
        if element["geometry_type"] in ["Vertex", "Edge"]:
            if action.is_a("IfcStructuralPointAction") and load.is_a("IfcStructuralLoadSingleForce"):
                FX = tempFX = load.ForceX if load.ForceX is not None else 0.0
                FY = tempFY = load.ForceY if load.ForceY is not None else 0.0
                FZ = tempFZ = load.ForceZ if load.ForceZ is not None else 0.0
                MX = tempMX = load.MomentX if load.MomentX is not None else 0.0
                MY = tempMY = load.MomentY if load.MomentY is not None else 0.0
                MZ = tempMZ = load.MomentZ if load.MomentZ is not None else 0.0
                if action.GlobalOrLocal == "LOCAL_COORDS":
                    # adjust for global/local
                    FX = np.array([tempFX, tempFY, tempFZ]).dot(element["orientation"][:, 0])
                    FY = np.array([tempFX, tempFY, tempFZ]).dot(element["orientation"][:, 1])
                    FZ = np.array([tempFX, tempFY, tempFZ]).dot(element["orientation"][:, 2])
                    MX = np.array([tempMX, tempMY, tempMZ]).dot(element["orientation"][:, 0])
                    MY = np.array([tempMX, tempMY, tempMZ]).dot(element["orientation"][:, 1])
                    MZ = np.array([tempMX, tempMY, tempMZ]).dot(element["orientation"][:, 2])

            elif action.is_a("IfcStructuralLinearAction") and load.is_a("IfcStructuralLoadLinearForce"):
                FX = tempFX = load.LinearForceX if load.LinearForceX is not None else 0.0
                FY = tempFY = load.LinearForceY if load.LinearForceY is not None else 0.0
                FZ = tempFZ = load.LinearForceZ if load.LinearForceZ is not None else 0.0
                MX = tempMX = load.LinearMomentX if load.LinearMomentX is not None else 0.0
                MY = tempMY = load.LinearMomentY if load.LinearMomentY is not None else 0.0
                MZ = tempMZ = load.LinearMomentZ if load.LinearMomentZ is not None else 0.0
                if action.GlobalOrLocal == "LOCAL_COORDS":
                    # adjust for global/local and projected/true
                    FX = np.array([tempFX, tempFY, tempFZ]).dot(element["orientation"][:, 0])
                    FY = np.array([tempFX, tempFY, tempFZ]).dot(element["orientation"][:, 1])
                    FZ = np.array([tempFX, tempFY, tempFZ]).dot(element["orientation"][:, 2])
                    MX = np.array([tempMX, tempMY, tempMZ]).dot(element["orientation"][:, 0])
                    MY = np.array([tempMX, tempMY, tempMZ]).dot(element["orientation"][:, 1])
                    MZ = np.array([tempMX, tempMY, tempMZ]).dot(element["orientation"][:, 2])
                    force_projection_coeff = 1.0
                    moment_projection_coeff = 1.0
                else:
                    if action.ProjectedOrTrue == "PROJECTED_LENGTH":
                        if force_length := np.linalg.norm(np.array([FX, FY, FZ])):
                            unit_force = np.array([FX, FY, FZ]) / force_length

                            force_projection_coeff = 1 - round(abs(unit_force.dot(element["orientation"][0])), 4)
                            assert force_projection_coeff >= 0, f"{force_projection_coeff}"
                        else:
                            force_projection_coeff = 1.0

                        if moment_length := np.linalg.norm(np.array([MX, MY, MZ])):
                            unit_moment = np.array([MX, MY, MZ]) / moment_length
                            moment_projection_coeff = 1 - round(abs(unit_moment.dot(element["orientation"][0])), 4)
                            assert moment_projection_coeff >= 0, f"{moment_projection_coeff}"
                        else:
                            moment_projection_coeff = 1.0
                    else:
                        force_projection_coeff = 1.0
                        moment_projection_coeff = 1.0

            for iLC, load_case in enumerate(load_cases):
                if load_case.id() in active_load_case_ids:
                    load_case_coeff = 1.0 if load_case.Coefficient is None else load_case.Coefficient
                    data["loadGroups"].append(load_group.Name)
                    data["loadsLC"]["FX"][iLC] += FX * load_group_coeff * load_case_coeff * force_projection_coeff
                    data["loadsLC"]["FY"][iLC] += FY * load_group_coeff * load_case_coeff * force_projection_coeff
                    data["loadsLC"]["FZ"][iLC] += FZ * load_group_coeff * load_case_coeff * force_projection_coeff
                    data["loadsLC"]["MX"][iLC] += MX * load_group_coeff * load_case_coeff * moment_projection_coeff
                    data["loadsLC"]["MY"][iLC] += MY * load_group_coeff * load_case_coeff * moment_projection_coeff
                    data["loadsLC"]["MZ"][iLC] += MZ * load_group_coeff * load_case_coeff * moment_projection_coeff

        elif element["geometry_type"] == "Face":
            if action.is_a("IfcStructuralSurfaceAction") and load.is_a("IfcStructuralLoadPlanarForce"):
                FX = tempFX = load.PlanarForceX if load.PlanarForceX is not None else 0.0
                FY = tempFY = load.PlanarForceY if load.PlanarForceY is not None else 0.0
                FZ = tempFZ = load.PlanarForceZ if load.PlanarForceZ is not None else 0.0
                if action.GlobalOrLocal == "LOCAL_COORDS":
                    # adjust for global/local and projected/true
                    FX = np.array([tempFX, tempFY, tempFZ]).dot(element["orientation"][:, 0])
                    FY = np.array([tempFX, tempFY, tempFZ]).dot(element["orientation"][:, 1])
                    FZ = np.array([tempFX, tempFY, tempFZ]).dot(element["orientation"][:, 2])
                    force_projection_coeff = 1.0
                else:
                    if action.ProjectedOrTrue == "PROJECTED_LENGTH":
                        if force_length := np.linalg.norm(np.array([FX, FY, FZ])):
                            unit_force = np.array([FX, FY, FZ]) / force_length
                            force_projection_coeff = round(abs(unit_force.dot(element["orientation"][2])), 4)
                            assert force_projection_coeff >= 0, f"{force_projection_coeff}"
                        else:
                            force_projection_coeff = 1.0
                    else:
                        force_projection_coeff = 1.0

            for iLC, load_case in enumerate(load_cases):
                if load_case.id() in active_load_case_ids:
                    load_case_coeff = 1.0 if load_case.Coefficient is None else load_case.Coefficient
                    data["loadGroups"].append(load_group.Name)
                    data["loadsLC"]["FX"][iLC] += FX * load_group_coeff * load_case_coeff * force_projection_coeff
                    data["loadsLC"]["FY"][iLC] += FY * load_group_coeff * load_case_coeff * force_projection_coeff
                    data["loadsLC"]["FZ"][iLC] += FZ * load_group_coeff * load_case_coeff * force_projection_coeff

    def parse_combination_loads(self, elements, load_combinations, load_case_ids):
        for element in elements:
            if element["loads"] is not None:
                for key, _ in element["loads"]["loadsCOMB"].items():
                    element["loads"]["loadsCOMB"][key] = np.array([0.0 for _ in load_combinations])

        for iComb, comb in enumerate(load_combinations):
            comb_factors = self.get_combination_factors(comb, load_case_ids)
            # print(comb_factors)
            for element in elements:
                if element["loads"] is None:
                    continue
                for key, load in element["loads"]["loadsLC"].items():
                    element["loads"]["loadsCOMB"][key][iComb] = round(comb_factors.dot(load), 4)

    def get_combination_factors(self, load_combination, load_case_ids: list[int]):
        comb_coeff = 1.0 if load_combination.Coefficient is None else load_combination.Coefficient
        comb_factors = np.array([0.0 for _ in load_case_ids])
        for assignment in self.get_combination_assignments(load_combination):
            for group in assignment.RelatedObjects:
                if group.id() in load_case_ids:
                    iLC = load_case_ids.index(group.id())
                    if assignment.is_a("IfcRelAssignsToGroupByFactor"):
                        comb_factors[iLC] += assignment.Factor * comb_coeff
                    else:
                        comb_factors[iLC] += 1.0 * comb_coeff

        return np.round(comb_factors, 4)

    def parse_model(self, model: ios.entity_instance):
        data = {"model": {k: v for k, v in model.get_info().items() if k in self.model_keys}}

        data["model"]["ObjectType"] = ifcopenshell.util.element.get_predefined_type(model)
        if model.LoadedBy:
            data["model"]["LoadedBy"] = [item.Name for item in model.LoadedBy]
        if model.HasResults:
            data["model"]["HasResults"] = [item.Name for item in model.HasResults]
        data["model"]["ref_id"] = self.get_ref_id(model)
        placement = ifcopenshell.util.placement.get_local_placement(model.SharedPlacement)
        origin, orientation = self.parse_transformation_matrix(placement)
        data["model"]["origin"] = origin
        data["model"]["orientation"] = orientation

        # elements and connections
        elements = [self.parse_element(element) for element in self.get_elements(model=model)]
        connections = [self.parse_connection(connection) for connection in self.get_connections(model=model)]
        for element in elements:
            element["connections"] = self.parse_element_connections(element, connections=connections)

        # loads, laod cases and laod combinations
        load_cases = self.get_load_cases(model=model)
        load_case_ids = [load_case.id() for load_case in load_cases]
        load_groups = self.get_load_groups(model=model)
        load_group_ids = [load_group.id() for load_group in load_groups]
        for element in elements + connections:
            element["loads"] = self.parse_element_loads(
                element=element,
                load_group_ids=load_group_ids,
                load_cases=load_cases,
            )
        load_combinations = self.get_load_combinations(model=model)
        if len(load_combinations):
            self.parse_combination_loads(elements + connections, load_combinations, load_case_ids)

        data["load_cases"] = [load_case.get_info() for load_case in load_cases]
        data["load_combinations"] = [load_combination.get_info() for load_combination in load_combinations]
        for combination in data["load_combinations"]:
            combination["factors"] = self.get_combination_factors(self.file.by_id(combination["id"]), load_case_ids)
            combination["load_cases"] = [
                item.Name
                for item in ifcopenshell.util.element.get_grouped_by(self.file.by_id(combination["id"]))
                if item.is_a("IfcStructuralLoadCase")
            ]

        # materials and profiles
        materials = set([item["material"] for item in elements])
        materialdb = dict(
            zip([self.get_ref_id(mat) for mat in materials], [self.parse_material(mat) for mat in materials])
        )
        for _, material in materialdb.items():
            material["related_elements"] = [
                item["ref_id"] for item in elements if material["id"] == item["material"].id()
            ]

        profiles = set([item["profile"] for item in elements if item["geometry_type"] == "Edge"])
        profiledb = dict(
            zip([self.get_ref_id(prof) for prof in profiles], [self.parse_profile(prof) for prof in profiles])
        )
        for _, profile in profiledb.items():
            profile["related_elements"] = [
                item["ref_id"]
                for item in elements
                if (item["geometry_type"] == "Edge" and profile["id"] == item["profile"].id())
            ]
        data["elements"] = elements
        data["connections"] = connections
        data["db"] = {"materials": materialdb, "profiles": profiledb}

        return json.loads(json.dumps(data, cls=IFC2JSONEncoder))

    # expose CRUD api functions
    # functions for meshes
    def get_meshes(self, model: ios.entity_instance | None = None):
        if model is not None:
            models = [model]
        else:
            models = self.get_models()
        if not self.folder_path.exists():
            return []

        meshes = []
        for model in models:
            for med_file in self.folder_path.glob(f"Model_{model.id()}*.med"):
                meshes.append({"name": med_file.stem, "model_id": model.id(), "med_path": str(med_file.resolve())})

        return meshes

    def create_mesh(self, model, parameters):
        model_id = model.id()
        if not self.folder_path.exists():
            self.folder_path.mkdir()

        template = self.env.get_template("salome/scriptSalome.py")
        mesh_name = f'Model_{model_id}_v{parameters["mesh_size"]}'

        med_path = self.folder_path / f"{mesh_name}.med"
        json_path = self.folder_path / f"Model_{model_id}.json"
        with json_path.open("w") as f:
            json.dump(self.parse_model(model), f, indent=4)

        rendered_script = template.render(
            mesh_size=parameters["mesh_size"],
            json_path=str(json_path.resolve()),
            med_path=str(med_path.resolve()),
            mesh_name=mesh_name,
        )

        # Write the rendered script to the new location
        script_path = self.folder_path / f'ScriptSalome_Model_{model_id}_v{parameters["mesh_size"]}.py'
        with open(script_path, "w") as f:
            f.write(rendered_script)

        if self.salome_path is not None:
            executable = Path(self.salome_path)
            subprocess.run(["python", executable, "-t", script_path])

            return {
                "name": mesh_name,
                "model_id": model.id(),
                "med_path": med_path,
            }
        else:
            print("Salome path not provided. Mesh operation aborted.")
            print(f"The salome script file path can be found in the return statement.")
            return {
                "name": mesh_name,
                "model_id": model.id(),
                "script_path": script_path,
            }

    def get_run_case_labels(self, data, target):
        cases = []
        if target in ["Any", "LoadCase"]:
            if len(data["load_cases"]):
                cases.append("LC")

        if target in ["Any", "LoadCombination"]:
            if len(data["load_combinations"]):
                cases.append("COMB")

        return cases

    def run_code_aster(self, mesh, target: str):
        model = self.file.by_id(mesh["model_id"])
        json_path = self.folder_path / f"Model_{model.id()}.json"

        # Read data from data file
        with open(json_path, "r") as f:
            data = json.load(f)
        cases = self.get_run_case_labels(data, target)
        run_label = "_".join(cases)

        comm_path = self.folder_path / f'{mesh["name"]}_{run_label}.comm'

        constructor = CommandFileConstructor(data)
        constructor.create_comm(comm_path, cases=cases)

        export_template = self.env.get_template("codeaster/export")
        export_content = export_template.render(
            model_name=mesh["name"],
            allocated_memory=7000.0,  # in MBs
            time_limit=900000.0,  # in seconds
            cases=cases,
            run_label=run_label,
        )
        export_path = self.folder_path / f"export"
        with open(export_path, "w") as f:
            f.write(export_content)

        subprocess.run(
            [
                "docker",
                "run",
                "-ti",
                "--rm",
                "-v",
                f"{self.folder_path.resolve()}:/home/aster/shared",
                "-w",
                "/home/aster/shared",
                "aethereng/ifc2ca",
                "as_run",
                "export",
            ]
        )
        return {"comm_path": comm_path, "export_path": export_path}

        # except Exception as e:
        #     # print(f"Exception `{e}` raised. Run operation aborted.")
        #     # print(f"The command and export file paths can be found in the return statement.")
        #     return {"Exception": e, "comm_path": comm_path, "export_path": export_path}

    def write_results_to_ifc(self, mesh, target, fields):
        model = self.file.by_id(mesh["model_id"])
        json_path = self.folder_path / f"Model_{model.id()}.json"

        # Read data from data file
        with open(json_path, "r") as f:
            data = json.load(f)
        cases = self.get_run_case_labels(data, target)
        model_name = mesh["name"]

        for case_instant in cases:
            rmed_path = self.folder_path / f"{model_name}_{case_instant}.rmed"

            ca2ifc.results_to_ifc(self.file, model, rmed_path, case_instant, fields, data)

    def save(self):
        self.file.write(self.path)

    def save_as(self, path: os.PathLike | str):
        self.file.write(path)

    def get_info(self):
        models = self.get_models()
        data = dict()
        for model in models:
            info = {
                "number_of_items": len(self.get_items(model)),
                "number_of_elements": len(self.get_elements(model)),
                "number_of_connections": len(self.get_connections(model)),
                "loads": None,
                "results": None,
            }
            if model.LoadedBy is not None:
                info["loads"] = {
                    "number_of_analysiscases": len(self.get_analysis_cases(model)),
                    "number_of_loadcases": len(self.get_analysis_load_cases(model)),
                    "number_of_loadcombinations": len(self.get_load_combinations(model)),
                }
            if model.HasResults is not None:
                info["results"] = {
                    "number_of_resultcases": len(self.get_result_cases(model)),
                }
            data[self.get_ref_id(model)] = info

        return data

    def toJSON(data):
        return json.dumps(data, indent=4, sort_keys=False, cls=IFC2JSONEncoder)


class IFC2JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        # print(type(obj), obj)
        if isinstance(obj, ios.entity_instance):
            return f"{obj.is_a()}|{obj.id()}"
            # return obj.get_info()
        if isinstance(obj, np.ndarray):
            return obj.tolist()

        # Let the base class default method raise the TypeError
        return json.JSONEncoder.default(self, obj)
