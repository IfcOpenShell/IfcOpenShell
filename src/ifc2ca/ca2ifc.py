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

import itertools

import ifcopenshell as ios
import meshio
import numpy as np

flatten = itertools.chain.from_iterable


def get_element_data(model, name, element):
    if element["geometry_type"] == "Edge":
        for i, cell_block in enumerate(model.cells):
            if cell_block.type == "line":
                cell_tags = model.cell_data["cell_tags"][i]
                break
        rows = []
        for i_row, i in enumerate(cell_tags):
            if i == 0:
                continue
            tags = model.cell_tags[i]
            for tag in tags:
                if tag == name:
                    # print(i_row, i)
                    rows.append(i_row)
                    break

        points = list(set(flatten([cell_block.data[c] for c in rows])))
        points.sort(key=lambda p: np.linalg.norm(model.points[p] - np.array(element["origin"])))
        coords = [np.round(model.points[p], 4).tolist() for p in points]
        local_coords = [
            [float(round(np.linalg.norm(model.points[p] - np.array(element["origin"])), 4))] for p in points
        ]

        return {
            "name": name,
            "points": points,
            "coords": coords,
            "local_coords": local_coords,
        }

    elif element["geometry_type"] == "Face":
        triangle_cell_tags = None
        quad_cell_tags = None
        for i, cell_block in enumerate(model.cells):
            if cell_block.type == "triangle":
                triangle_cell_tags = model.cell_data["cell_tags"][i]
                break

        if triangle_cell_tags is not None:
            rows = []
            for i_row, i in enumerate(triangle_cell_tags):
                if i == 0:
                    continue
                tags = model.cell_tags[i]
                for tag in tags:
                    if tag == name:
                        # print(i_row, i)
                        rows.append(i_row)
                        break
            if not len(rows):
                points = []
            else:
                points = list(flatten([cell_block.data[c] for c in rows]))

        for i, cell_block in enumerate(model.cells):
            if cell_block.type == "quad":
                quad_cell_tags = model.cell_data["cell_tags"][i]
                break

        if quad_cell_tags is not None:
            rows = []
            for i_row, i in enumerate(quad_cell_tags):
                if i == 0:
                    continue
                tags = model.cell_tags[i]
                for tag in tags:
                    if tag == name:
                        # print(i_row, i)
                        rows.append(i_row)
                        break
            if len(rows):
                points.extend(list(flatten([cell_block.data[c] for c in rows])))

        points = list(set(points))
        points.sort()
        coords = [model.points[p].tolist() for p in points]
        local_coords = [
            np.round(np.array(element["orientation"]).dot(model.points[p] - np.array(element["origin"])), 4).tolist()[
                :2
            ]
            for p in points
        ]

        return {
            "name": name,
            "points": points,
            "coords": coords,
            "local_coords": local_coords,
        }


def get_element_result_data(model, field_label, name, element, field_type):
    points = get_element_data(model, name, element)["points"]
    if field_type == "InternalForces":
        if element["geometry_type"] == "Edge":
            return {
                "N": [round(model.point_data[field_label][p][0], 4) for p in points],
                "VY": [round(model.point_data[field_label][p][1], 4) for p in points],
                "VZ": [round(model.point_data[field_label][p][2], 4) for p in points],
                "MT": [round(model.point_data[field_label][p][3], 4) for p in points],
                "MFY": [round(model.point_data[field_label][p][4], 4) for p in points],
                "MFZ": [round(model.point_data[field_label][p][5], 4) for p in points],
            }

        elif element["geometry_type"] == "Face":
            if len(model.point_data[field_label][points[0]]) == 8:
                offset = 0
            elif len(model.point_data[field_label][points[0]]) == 14:
                offset = 6
            else:
                assert (
                    False
                ), f"Internal force field with {len(model.point_data[field_label][points[0]])} field values for {field_label} and {element['Name']} "

            return {
                "NXX": [round(model.point_data[field_label][p][offset + 0], 4) for p in points],
                "NYY": [round(model.point_data[field_label][p][offset + 1], 4) for p in points],
                "NXY": [round(model.point_data[field_label][p][offset + 2], 4) for p in points],
                "MXX": [round(model.point_data[field_label][p][offset + 3], 4) for p in points],
                "MYY": [round(model.point_data[field_label][p][offset + 4], 4) for p in points],
                "MXY": [round(model.point_data[field_label][p][offset + 5], 4) for p in points],
                "QX": [round(model.point_data[field_label][p][offset + 6], 4) for p in points],
                "QY": [round(model.point_data[field_label][p][offset + 7], 4) for p in points],
            }

    if field_type == "Displacements":
        return {
            "DX": [round(model.point_data[field_label][p][0], 4) for p in points],
            "DY": [round(model.point_data[field_label][p][1], 4) for p in points],
            "DZ": [round(model.point_data[field_label][p][2], 4) for p in points],
            "DRX": [round(model.point_data[field_label][p][3], 4) for p in points],
            "DRY": [round(model.point_data[field_label][p][4], 4) for p in points],
            "DRZ": [round(model.point_data[field_label][p][5], 4) for p in points],
        }


def results_to_ifc(ifc_file, ifc_model, rmed_path, global_case, field_types, data):
    if not rmed_path.exists():
        print(f"Med file with results not found for case_instant: {global_case}")
        return

    result = meshio.read(rmed_path, "med")
    if global_case == "LC":
        model_cases = data["load_cases"]
    elif global_case == "COMB":
        model_cases = data["load_combinations"]
    for field in field_types:
        if field == "InternalForces":
            _parsed_data = internal_forces_to_ifc(ifc_file, ifc_model, result, model_cases, data["elements"])
        elif field == "Displacements":
            _parsed_data = displacements_to_ifc(ifc_file, ifc_model, result, model_cases, data["elements"])


def internal_forces_to_ifc(ifc_file, ifc_model, result, model_cases, elements):
    result_cases = [dict() for _ in model_cases]
    field_cases = [f"ELEMENT_FORCE[{i}] - {i + 1}" for i in range(len(result_cases))]

    # Create Result Groups for load case_instance combinations
    for iCase, case_instance in enumerate(model_cases):
        result_cases[iCase]["case_instance"] = ifc_file.create_entity(
            "IfcStructuralResultGroup",
            **{
                "GlobalId": ios.guid.new(),
                "Name": "Internal Forces for " + case_instance["Name"],
                "TheoryType": "FIRST_ORDER_THEORY",
                "ResultForLoadGroup": ifc_file.by_id(case_instance["id"]),
                "IsLinear": True,
            },
        )

        result_cases[iCase]["assignment"] = ifc_file.create_entity(
            "IfcRelAssignsToGroup",
            **{
                "GlobalId": ios.guid.new(),
                "RelatedObjects": [],
                "RelatingGroup": result_cases[iCase]["case_instance"],
            },
        )

    if ifc_model.HasResults:
        ifc_model.HasResults += tuple([result["case_instance"] for result in result_cases])
    else:
        ifc_model.HasResults = tuple([result["case_instance"] for result in result_cases])

    data = []
    for _, element in enumerate(elements):
        group_name = getGroupName(element["ref_id"])
        name = element["Name"]
        info = get_element_data(result, group_name, element)
        assert len(info["coords"]) >= 2
        for iCase, field_case in enumerate(field_cases):
            forces = get_element_result_data(result, field_case, group_name, element, field_type="InternalForces")
            reaction = ifc_file.create_entity(
                "IfcStructuralCurveReaction" if element["geometry_type"] == "Edge" else "IfcStructuralSurfaceReaction",
                **{
                    "GlobalId": ios.guid.new(),
                    "Name": "Internal Forces for " + model_cases[iCase]["Name"] + f" on {name}",
                    # "AppliedLoad": load["ifcLoad"],
                    "GlobalOrLocal": "LOCAL_COORDS",
                    "PredefinedType": "DISCRETE",
                },
            )
            result_cases[iCase]["assignment"].RelatedObjects += (reaction,)

            ifc_file.create_entity(
                "IfcRelConnectsStructuralActivity",
                **{
                    "GlobalId": ios.guid.new(),
                    "RelatingElement": ifc_file.by_id(element["id"]),
                    "RelatedStructuralActivity": reaction,
                },
            )

            reaction.AppliedLoad = ifc_file.create_entity(
                "IfcStructuralLoadConfiguration",
                **{
                    "Name": "Internal Forces for " + model_cases[iCase]["Name"] + f" on {name}",
                    "Values": [],
                    "Locations": tuple([tuple(node) for node in info["local_coords"]]),
                },
            )

            if element["geometry_type"] == "Edge":
                for iNode, node in enumerate(info["coords"]):
                    location = f"({node[0]}, {node[1]}, {node[2]})"
                    distance = info["local_coords"][iNode][0]

                    N = forces["N"][iNode]
                    VY = forces["VY"][iNode]
                    VZ = forces["VZ"][iNode]
                    MT = forces["MT"][iNode]
                    MFY = forces["MFY"][iNode]
                    MFZ = forces["MFZ"][iNode]

                    data.append([name, f"LCC-{iCase + 1} @ {distance}", location, N, VY, VZ, MT, MFY, MFZ])

                    pointValue = ifc_file.create_entity(
                        "IfcStructuralLoadSingleForce",
                        **{
                            "Name": "Internal Forces for " + model_cases[iCase]["Name"] + f" @ {distance} on {name}",
                            "ForceX": N,
                            "ForceY": VY,
                            "ForceZ": VZ,
                            "MomentX": MT,
                            "MomentY": MFY,
                            "MomentZ": MFZ,
                        },
                    )
                    reaction.AppliedLoad.Values += (pointValue,)

            elif element["geometry_type"] == "Face":
                for iNode, node in enumerate(info["coords"]):
                    location = f"({node[0]}, {node[1]}, {node[2]})"
                    distance = tuple(info["local_coords"][iNode])

                    NXX = forces["NXX"][iNode]
                    NYY = forces["NYY"][iNode]
                    NXY = forces["NXY"][iNode]
                    MXX = forces["MXX"][iNode]
                    MYY = forces["MYY"][iNode]
                    MXY = forces["MXY"][iNode]

                    data.append([name, f"LCC-{iCase + 1} @ {distance}", location, NXX, NYY, NXY, MXX, MYY, MXY])

                    pointValue = ifc_file.create_entity(
                        "IfcStructuralLoadSingleForce",
                        **{
                            "Name": "Internal Forces for " + model_cases[iCase]["Name"] + f" @ {distance} on {name}",
                            "ForceX": NXX,
                            "ForceY": NYY,
                            "ForceZ": NXY,
                            "MomentX": MXX,
                            "MomentY": MYY,
                            "MomentZ": MXY,
                        },
                    )
                    reaction.AppliedLoad.Values += (pointValue,)

    return data


def displacements_to_ifc(ifc_file, ifc_model, result, model_cases, elements):
    result_cases = [dict() for _ in model_cases]
    field_cases = [f"MODEL_DISP[{i}] - {i + 1}" for i in range(len(result_cases))]

    # Create Result Groups for load case_instance combinations
    for iCase, case_instance in enumerate(model_cases):
        result_cases[iCase]["case_instance"] = ifc_file.create_entity(
            "IfcStructuralResultGroup",
            **{
                "GlobalId": ios.guid.new(),
                "Name": "Global Displacements for " + case_instance["Name"],
                "TheoryType": "FIRST_ORDER_THEORY",
                "ResultForLoadGroup": ifc_file.by_id(case_instance["id"]),
                "IsLinear": True,
            },
        )

        result_cases[iCase]["assignment"] = ifc_file.create_entity(
            "IfcRelAssignsToGroup",
            **{
                "GlobalId": ios.guid.new(),
                "RelatedObjects": [],
                "RelatingGroup": result_cases[iCase]["case_instance"],
            },
        )

    if ifc_model.HasResults:
        ifc_model.HasResults += tuple([result["case_instance"] for result in result_cases])
    else:
        ifc_model.HasResults = tuple([result["case_instance"] for result in result_cases])

    data = []
    for _, element in enumerate(elements):
        group_name = getGroupName(element["ref_id"])
        name = element["Name"]
        info = get_element_data(result, group_name, element)
        assert len(info["coords"]) >= 2
        for iCase, case_instance in enumerate(field_cases):
            displacements = get_element_result_data(
                result, case_instance, group_name, element, field_type="Displacements"
            )
            reaction = ifc_file.create_entity(
                "IfcStructuralCurveReaction" if element["geometry_type"] == "Edge" else "IfcStructuralSurfaceReaction",
                **{
                    "GlobalId": ios.guid.new(),
                    "Name": "Global Displacements for " + model_cases[iCase]["Name"] + f" on {name}",
                    # "AppliedLoad": load["ifcLoad"],
                    "GlobalOrLocal": "LOCAL_COORDS",
                    "PredefinedType": "DISCRETE",
                },
            )
            result_cases[iCase]["assignment"].RelatedObjects += (reaction,)

            ifc_file.create_entity(
                "IfcRelConnectsStructuralActivity",
                **{
                    "GlobalId": ios.guid.new(),
                    "RelatingElement": ifc_file.by_id(element["id"]),
                    "RelatedStructuralActivity": reaction,
                },
            )

            reaction.AppliedLoad = ifc_file.create_entity(
                "IfcStructuralLoadConfiguration",
                **{
                    "Name": "Global Displacements for " + model_cases[iCase]["Name"] + f" on {name}",
                    "Values": [],
                    "Locations": tuple([tuple(node) for node in info["local_coords"]]),
                },
            )

            if element["geometry_type"] == "Edge":
                for iNode, node in enumerate(info["coords"]):
                    location = f"({node[0]}, {node[1]}, {node[2]})"
                    distance = info["local_coords"][iNode][0]

                    DX = displacements["DX"][iNode]
                    DY = displacements["DY"][iNode]
                    DZ = displacements["DZ"][iNode]
                    DRX = displacements["DRX"][iNode]
                    DRY = displacements["DRY"][iNode]
                    DRZ = displacements["DRZ"][iNode]

                    data.append([name, f"LCC-{iCase + 1} @ {distance}", location, DX, DY, DZ, DRX, DRY, DRZ])

                    pointValue = ifc_file.create_entity(
                        "IfcStructuralLoadSingleDisplacement",
                        **{
                            "Name": "Global Displacements for "
                            + model_cases[iCase]["Name"]
                            + f" @ {distance} on {name}",
                            "DisplacementX": DX,
                            "DisplacementY": DY,
                            "DisplacementZ": DZ,
                            "RotationalDisplacementRX": DRX,
                            "RotationalDisplacementRY": DRY,
                            "RotationalDisplacementRZ": DRZ,
                        },
                    )
                    reaction.AppliedLoad.Values += (pointValue,)

            elif element["geometry_type"] == "Face":
                for iNode, node in enumerate(info["coords"]):
                    location = f"({node[0]}, {node[1]}, {node[2]})"
                    distance = tuple(info["local_coords"][iNode])

                    DX = displacements["DX"][iNode]
                    DY = displacements["DY"][iNode]
                    DZ = displacements["DZ"][iNode]
                    DRX = displacements["DRX"][iNode]
                    DRY = displacements["DRY"][iNode]
                    DRZ = displacements["DRZ"][iNode]

                    data.append([name, f"LCC-{iCase + 1} @ {distance}", location, DX, DY, DZ, DRX, DRY, DRZ])

                    pointValue = ifc_file.create_entity(
                        "IfcStructuralLoadSingleDisplacement",
                        **{
                            "Name": "Global Displacements for "
                            + model_cases[iCase]["Name"]
                            + f" @ {distance} on {name}",
                            "DisplacementX": DX,
                            "DisplacementY": DY,
                            "DisplacementZ": DZ,
                            "RotationalDisplacementRX": DRX,
                            "RotationalDisplacementRY": DRY,
                            "RotationalDisplacementRZ": DRZ,
                        },
                    )
                    reaction.AppliedLoad.Values += (pointValue,)

    return data


def getGroupName(name):
    if "|" in name:
        info = name.split("|")
        sortName = "".join(c for c in info[0] if c.isupper())
        return f"{sortName[2:]}_{info[1]}"
    else:
        return name
