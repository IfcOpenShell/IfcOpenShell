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
import json
from pathlib import Path

import numpy as np
from jinja2 import Environment, FileSystemLoader

flatten = itertools.chain.from_iterable

includeZeroLength1DSprings = False


class CommandFileConstructor:
    def __init__(self, data: dict):
        self.data = data
        self.env = Environment(loader=FileSystemLoader(Path(__file__).parent / "templates"))

    def getGroupName(self, name):
        if "|" in name:
            info = name.split("|")
            sortName = "".join(c for c in info[0] if c.isupper())
            return f"{sortName[2:]}_{info[1]}"
        else:
            return name

    def calculateConstraints(self, rel):
        gr1 = rel["groupName1"]
        gr2 = rel["groupName2"]
        o = np.array(rel["orientation"]).transpose().tolist()
        liaisons = {
            "groupNames": (gr1, gr1, gr1, gr2, gr2, gr2),
            "coeffs": [],
            "dofs": [],
        }
        stiffnesses = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        if not rel["appliedCondition"]:
            rel["appliedCondition"] = {
                "dx": True,
                "dy": True,
                "dz": True,
                "drx": True,
                "dry": True,
                "drz": True,
            }
        if isinstance(rel["appliedCondition"]["dx"], bool) and rel["appliedCondition"]["dx"]:
            liaisons["coeffs"].append((o[0][0], o[1][0], o[2][0], -o[0][0], -o[1][0], -o[2][0]))
            liaisons["dofs"].append(("DX", "DY", "DZ", "DX", "DY", "DZ"))
        elif isinstance(rel["appliedCondition"]["dx"], float) and rel["appliedCondition"]["dx"] > 0:
            stiffnesses[0] = rel["appliedCondition"]["dx"]

        if isinstance(rel["appliedCondition"]["dy"], bool) and rel["appliedCondition"]["dy"]:
            liaisons["coeffs"].append((o[0][1], o[1][1], o[2][1], -o[0][1], -o[1][1], -o[2][1]))
            liaisons["dofs"].append(("DX", "DY", "DZ", "DX", "DY", "DZ"))
        elif isinstance(rel["appliedCondition"]["dy"], float) and rel["appliedCondition"]["dy"] > 0:
            stiffnesses[1] = rel["appliedCondition"]["dy"]

        if isinstance(rel["appliedCondition"]["dz"], bool) and rel["appliedCondition"]["dz"]:
            liaisons["coeffs"].append((o[0][2], o[1][2], o[2][2], -o[0][2], -o[1][2], -o[2][2]))
            liaisons["dofs"].append(("DX", "DY", "DZ", "DX", "DY", "DZ"))
        elif isinstance(rel["appliedCondition"]["dz"], float) and rel["appliedCondition"]["dz"] > 0:
            stiffnesses[2] = rel["appliedCondition"]["dz"]

        if isinstance(rel["appliedCondition"]["drx"], bool) and rel["appliedCondition"]["drx"]:
            liaisons["coeffs"].append((o[0][0], o[1][0], o[2][0], -o[0][0], -o[1][0], -o[2][0]))
            liaisons["dofs"].append(("DRX", "DRY", "DRZ", "DRX", "DRY", "DRZ"))
        elif isinstance(rel["appliedCondition"]["drx"], float) and rel["appliedCondition"]["drx"] > 0:
            stiffnesses[3] = rel["appliedCondition"]["drx"]

        if isinstance(rel["appliedCondition"]["dry"], bool) and rel["appliedCondition"]["dry"]:
            liaisons["coeffs"].append((o[0][1], o[1][1], o[2][1], -o[0][1], -o[1][1], -o[2][1]))
            liaisons["dofs"].append(("DRX", "DRY", "DRZ", "DRX", "DRY", "DRZ"))
        elif isinstance(rel["appliedCondition"]["dry"], float) and rel["appliedCondition"]["dry"] > 0:
            stiffnesses[4] = rel["appliedCondition"]["dry"]

        if isinstance(rel["appliedCondition"]["drz"], bool) and rel["appliedCondition"]["drz"]:
            liaisons["coeffs"].append((o[0][2], o[1][2], o[2][2], -o[0][2], -o[1][2], -o[2][2]))
            liaisons["dofs"].append(("DRX", "DRY", "DRZ", "DRX", "DRY", "DRZ"))
        elif isinstance(rel["appliedCondition"]["drz"], float) and rel["appliedCondition"]["drz"] > 0:
            stiffnesses[5] = rel["appliedCondition"]["drz"]

        rel["liaisons"] = liaisons
        rel["stiffnesses"] = tuple(stiffnesses)

    def calculateRestraints(self, conn):
        group = self.getGroupName(conn["ref_id"])
        o = np.array(conn["orientation"]).transpose().tolist()
        liaisons = {"groupNames": (group, group, group), "coeffs": [], "dofs": []}
        stiffnesses = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

        if not conn["appliedCondition"]:
            conn["liaisons"] = liaisons
            conn["stiffnesses"] = tuple(stiffnesses)
            return

        if isinstance(conn["appliedCondition"]["dx"], bool) and conn["appliedCondition"]["dx"]:
            liaisons["coeffs"].append((o[0][0], o[1][0], o[2][0]))
            liaisons["dofs"].append(("DX", "DY", "DZ"))
        elif isinstance(conn["appliedCondition"]["dx"], float) and conn["appliedCondition"]["dx"] > 0:
            stiffnesses[0] = conn["appliedCondition"]["dx"]

        if isinstance(conn["appliedCondition"]["dy"], bool) and conn["appliedCondition"]["dy"]:
            liaisons["coeffs"].append((o[0][1], o[1][1], o[2][1]))
            liaisons["dofs"].append(("DX", "DY", "DZ"))
        elif isinstance(conn["appliedCondition"]["dy"], float) and conn["appliedCondition"]["dy"] > 0:
            stiffnesses[1] = conn["appliedCondition"]["dy"]

        if isinstance(conn["appliedCondition"]["dz"], bool) and conn["appliedCondition"]["dz"]:
            liaisons["coeffs"].append((o[0][2], o[1][2], o[2][2]))
            liaisons["dofs"].append(("DX", "DY", "DZ"))
        elif isinstance(conn["appliedCondition"]["dz"], float) and conn["appliedCondition"]["dz"] > 0:
            stiffnesses[2] = conn["appliedCondition"]["dz"]

        if isinstance(conn["appliedCondition"]["drx"], bool) and conn["appliedCondition"]["drx"]:
            liaisons["coeffs"].append((o[0][0], o[1][0], o[2][0]))
            liaisons["dofs"].append(("DRX", "DRY", "DRZ"))
        elif isinstance(conn["appliedCondition"]["drx"], float) and conn["appliedCondition"]["drx"] > 0:
            stiffnesses[3] = conn["appliedCondition"]["drx"]

        if isinstance(conn["appliedCondition"]["dry"], bool) and conn["appliedCondition"]["dry"]:
            liaisons["coeffs"].append((o[0][1], o[1][1], o[2][1]))
            liaisons["dofs"].append(("DRX", "DRY", "DRZ"))
        elif isinstance(conn["appliedCondition"]["dry"], float) and conn["appliedCondition"]["dry"] > 0:
            stiffnesses[4] = conn["appliedCondition"]["dry"]

        if isinstance(conn["appliedCondition"]["drz"], bool) and conn["appliedCondition"]["drz"]:
            liaisons["coeffs"].append((o[0][2], o[1][2], o[2][2]))
            liaisons["dofs"].append(("DRX", "DRY", "DRZ"))
        elif isinstance(conn["appliedCondition"]["drz"], float) and conn["appliedCondition"]["drz"] > 0:
            stiffnesses[5] = conn["appliedCondition"]["drz"]

        conn["liaisons"] = liaisons
        conn["stiffnesses"] = tuple(stiffnesses)

    def create_comm(self, path, cases):
        self.comm_path = Path(path)
        self.cases = cases

        data = self.data

        elements = data["elements"]
        connections = data["connections"]
        # --> Delete this reference data and repopulate it with the objects
        # while going through elements
        for conn in connections:
            conn["related_elements"] = []
            self.calculateRestraints(conn)
        for el in elements:
            for rel in el["connections"]:
                conn = next(c for c in connections if c["ref_id"] == rel["related_connection"])
                rel["conn_string"] = None
                if conn["geometry_type"] == "Vertex":
                    rel["conn_string"] = "_0DC_"
                    rel["springGroupName"] = (
                        self.getGroupName(rel["relating_element"])
                        + "_1DS_"
                        + self.getGroupName(rel["related_connection"])
                    )
                if conn["geometry_type"] == "Edge":
                    rel["conn_string"] = "_1DC_"
                    rel["springGroupName"] = None
                if conn["geometry_type"] == "Face":
                    rel["conn_string"] = "_2DC_"
                    rel["springGroupName"] = None

                rel["groupName1"] = (
                    self.getGroupName(rel["relating_element"])
                    + rel["conn_string"]
                    + self.getGroupName(rel["related_connection"])
                )
                if rel["eccentricity"]:
                    rel["groupName2"] = (
                        self.getGroupName(rel["related_connection"])
                        + "_0DC_"
                        + self.getGroupName(rel["relating_element"])
                    )
                    rel["index"] = len(conn["related_elements"]) + 1
                    rel["unifiedGroupName"] = self.getGroupName(rel["related_connection"]) + "_0DC_%g" % rel["index"]
                else:
                    rel["groupName2"] = self.getGroupName(rel["related_connection"])
                self.calculateConstraints(rel)
                conn["related_elements"].append(rel)
        # End <--

        materials = data["db"]["materials"]
        for _, material in materials.items():
            material["groupNames"] = tuple([self.getGroupName(rel) for rel in material["related_elements"]])

        profiles = data["db"]["profiles"]
        for _, profile in profiles.items():
            profile["groupNames"] = tuple([self.getGroupName(rel) for rel in profile["related_elements"]])

        edgeGroupNames = tuple([self.getGroupName(el["ref_id"]) for el in elements if el["geometry_type"] == "Edge"])
        faceGroupNames = tuple([self.getGroupName(el["ref_id"]) for el in elements if el["geometry_type"] == "Face"])
        point0DGroupNames = tuple(
            [self.getGroupName(el["ref_id"]) + "_0D" for el in connections if el["geometry_type"] == "Vertex"]
        )
        if includeZeroLength1DSprings:
            spring1DGroupNames = tuple(
                flatten(
                    [[rel["springGroupName"] for rel in el["connections"] if rel["springGroupName"]] for el in elements]
                )
            )
        point1DGroupNames = tuple(
            [self.getGroupName(el["ref_id"]) + "_0D" for el in connections if el["geometry_type"] == "Edge"]
        )

        rigidLinkGroupNames = []
        for conn in connections:
            conn["unifiedGroupNames"] = [
                rel["unifiedGroupName"] for rel in conn["related_elements"] if rel["eccentricity"]
            ]
            # if not conn['appliedCondition'] and len(conn['unifiedGroupNames']) == 1:
            #     conn['appliedCondition'] = {
            #         'dx': True,
            #         'dy': True,
            #         'dz': True
            #     }
            if len(conn["unifiedGroupNames"]):
                conn["unifiedGroupNames"].insert(0, self.getGroupName(conn["ref_id"]))
                conn["unifiedGroupNames"] = tuple(conn["unifiedGroupNames"])
            rigidLinkGroupNames.extend(
                [
                    self.getGroupName(rel["relating_element"]) + "_1DR_" + self.getGroupName(conn["ref_id"])
                    for rel in conn["related_elements"]
                    if rel["eccentricity"]
                ]
            )
        rigidLinkGroupNames = tuple(rigidLinkGroupNames)

        # Start of Writng Command File# Define file to write command file for code_aster
        with self.comm_path.open("w") as f:
            start_process = self.env.get_template("codeaster/start_process.py")
            f.write(start_process.render())

            read_mesh = self.env.get_template("codeaster/read_mesh.py")
            f.write(read_mesh.render())

            define_model = self.env.get_template("codeaster/define_model.py")
            f.write(
                define_model.render(
                    faceGroupNames=faceGroupNames,
                    edgeGroupNames=edgeGroupNames,
                    point0DGroupNames=point0DGroupNames,
                    point0DGroupNamesPlus=point0DGroupNames
                    + (spring1DGroupNames if includeZeroLength1DSprings else tuple()),
                    point1DGroupNames=point1DGroupNames,
                    rigidLinkGroupNames=rigidLinkGroupNames,
                )
            )

            define_materials = self.env.get_template("codeaster/define_materials.py")
            f.write(
                define_materials.render(
                    enumerate=enumerate,
                    materials=materials,
                    rigidLinkGroupNames=rigidLinkGroupNames,
                )
            )

            define_elements = self.env.get_template("codeaster/define_elements.py")
            f.write(
                define_elements.render(
                    len=len,
                    tuple=tuple,
                    getGroupName=self.getGroupName,
                    includeZeroLength1DSprings=includeZeroLength1DSprings,
                    profiles=profiles,
                    rigidLinkGroupNames=rigidLinkGroupNames,
                    beamElements=[el for el in elements if el["geometry_type"] == "Edge"],
                    shellElements=[el for el in elements if el["geometry_type"] == "Face"],
                    vertexConnections=[conn for conn in connections if conn["geometry_type"] == "Vertex"],
                    edgeConnections=[conn for conn in connections if conn["geometry_type"] == "Edge"],
                    # faceConnections=[conn for conn in connections if conn["geometry_type"] == "Face"],
                )
            )

            define_connections = self.env.get_template("codeaster/define_connections.py")
            f.write(
                define_connections.render(
                    len=len,
                    range=range,
                    tuple=tuple,
                    rigidLinkGroupNames=rigidLinkGroupNames,
                    vertexConnections=[conn for conn in connections if conn["geometry_type"] == "Vertex"],
                    edgeConnections=[conn for conn in connections if conn["geometry_type"] == "Edge"],
                    unifiedConnections=[conn for conn in connections if len(conn["unifiedGroupNames"]) > 1],
                )
            )

            for case_instant in self.cases:
                if case_instant == "LC":
                    define_loads = self.env.get_template("codeaster/define_loads.py")
                    f.write(
                        define_loads.render(
                            tuple=tuple,
                            analysis_time=f"analysis_time_{case_instant}",
                            load=f"load_{case_instant}",
                            load_key=f"loads{case_instant}",
                            start=1.0,
                            end=float(len(self.data["load_cases"])),
                            steps=len(self.data["load_cases"]) - 1,
                            getGroupName=self.getGroupName,
                            time=tuple([float(t) for t in (range(1, len(self.data["load_cases"]) + 1))]),
                            vertexLoadElements=[
                                item
                                for item in connections
                                if item["geometry_type"] == "Vertex" and item["loads"] is not None
                            ],
                            edgeLoadElements=[
                                item
                                for item in elements + connections
                                if item["geometry_type"] == "Edge" and item["loads"] is not None
                            ],
                            faceLoadElements=[
                                item
                                for item in elements + connections
                                if item["geometry_type"] == "Face" and item["loads"] is not None
                            ],
                        )
                    )

                elif case_instant == "COMB":
                    define_loads = self.env.get_template("codeaster/define_loads.py")
                    f.write(
                        define_loads.render(
                            tuple=tuple,
                            analysis_time=f"analysis_time_{case_instant}",
                            load=f"load_{case_instant}",
                            load_key=f"loads{case_instant}",
                            start=1.0,
                            end=float(len(self.data["load_combinations"])),
                            steps=len(self.data["load_combinations"]) - 1,
                            getGroupName=self.getGroupName,
                            time=tuple([float(t) for t in (range(1, len(self.data["load_combinations"]) + 1))]),
                            vertexLoadElements=[
                                item
                                for item in connections
                                if item["geometry_type"] == "Vertex" and item["loads"] is not None
                            ],
                            edgeLoadElements=[
                                item
                                for item in elements + connections
                                if item["geometry_type"] == "Edge" and item["loads"] is not None
                            ],
                            faceLoadElements=[
                                item
                                for item in elements + connections
                                if item["geometry_type"] == "Face" and item["loads"] is not None
                            ],
                        )
                    )

            for case_instant in self.cases:
                run_analysis = self.env.get_template("codeaster/run_analysis.py")
                if case_instant == "LC":
                    f.write(
                        run_analysis.render(
                            analysis_time="analysis_time_LC",
                            load=f"load_{case_instant}",
                            res_Bld=f"res_Bld_{case_instant}",
                        )
                    )
                elif case_instant == "COMB":
                    f.write(
                        run_analysis.render(
                            analysis_time="analysis_time_COMB",
                            load=f"load_{case_instant}",
                            res_Bld=f"res_Bld_{case_instant}",
                        )
                    )

            for case_instant in self.cases:
                export_results = self.env.get_template("codeaster/export_results.py")
                if case_instant == "LC":
                    f.write(
                        export_results.render(
                            unit_number=80,
                            res_Bld=f"res_Bld_{case_instant}",
                        )
                    )
                elif case_instant == "COMB":
                    f.write(
                        export_results.render(
                            unit_number=81,
                            res_Bld=f"res_Bld_{case_instant}",
                        )
                    )

            finish_process = self.env.get_template("codeaster/finish_process.py")
            f.write(finish_process.render())
