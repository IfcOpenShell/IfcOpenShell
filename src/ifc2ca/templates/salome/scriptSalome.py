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
import os
import time
from pathlib import Path

import numpy as np
import salome
import salome_notebook
import salome_version

flatten = itertools.chain.from_iterable

mesh_size = {{ mesh_size }}
med_path = r"{{ med_path }}"
json_path = r"{{ json_path }}"

with open(json_path, "r") as f:
    data = json.load(f)


class MODEL:
    def __init__(self):
        self.medFilename = med_path
        self.mesh_size = mesh_size
        self.tolLoc = 0
        self.mesh = None
        self.meshNodes = None
        self.create()

    def getGroupName(self, name):
        if "|" in name:
            info = name.split("|")
            sortName = "".join(c for c in info[0] if c.isupper())
            return f"{sortName[2:]}_{info[1]}"
        else:
            return name

    def makePoint(self, pl):
        """Function to define a Point from
        a polyline (list of 1 point)"""

        (x, y, z) = pl
        return self.geompy.MakeVertex(x, y, z)

    def makeLine(self, pl):
        """Function to define a Line from
        a polyline (list of 2 points)"""

        (x, y, z) = pl[0]
        P1 = self.geompy.MakeVertex(x, y, z)
        (x, y, z) = pl[1]
        P2 = self.geompy.MakeVertex(x, y, z)

        return self.geompy.MakeLineTwoPnt(P1, P2)

    def makeFace(self, pl):
        """Function to define a Face from
        a polyline (list of points)"""

        pointList = [None for _ in range(len(pl))]
        for ip, (x, y, z) in enumerate(pl):
            pointList[ip] = self.geompy.MakeVertex(x, y, z)

        LineList = [None for _ in range(len(pl))]
        for ip, P2 in enumerate(pointList):
            P1 = pointList[ip - 1]
            LineList[ip] = self.geompy.MakeLineTwoPnt(P1, P2)

        return self.geompy.MakeFaceWires(LineList, 1)

    def makeObject(self, geometry, geometry_type):
        if geometry_type == "Vertex":
            return self.makePoint(geometry)
        if geometry_type == "Edge":
            return self.makeLine(geometry)
        if geometry_type == "Face":
            return self.makeFace(geometry)

    def makePartition(self, objects, geometry_type):
        if geometry_type == "Vertex":
            shapeType = "VERTEX"
        if geometry_type == "Edge":
            shapeType = "EDGE"
        if geometry_type == "Face":
            shapeType = "FACE"
        return self.geompy.MakePartition(objects, [], [], [], self.geompy.ShapeType[shapeType], 0, [], 1)

    def length(self, geometry):
        return (
            (geometry[1][0] - geometry[0][0]) ** 2
            + (geometry[1][1] - geometry[0][1]) ** 2
            + (geometry[1][2] - geometry[0][2]) ** 2
        ) ** 0.5

    def create(self):
        # Read data from input file
        # data = data

        self.elements = elements = data["elements"]
        self.connections = connections = data["connections"]
        # --> Delete this reference data and repopulate it with the objects
        # while going through elements
        for conn in connections:
            conn["related_elements"] = []
        # End <--

        mesh_size = self.mesh_size

        dec = 7  # 4 decimals for length in mm
        tol = 10 ** (-dec - 3 + 1)

        self.tolLoc = tol * 10 * 2
        tolLoc = self.tolLoc

        self.NEW_SALOME = NEW_SALOME = int(salome_version.getVersion()[0]) >= 9
        salome.salome_init()
        theStudy = salome.myStudy
        notebook = salome_notebook.NoteBook(theStudy)

        ###
        ### GEOM component
        ###
        import math

        import GEOM
        import SALOMEDS
        from salome.geom import geomBuilder

        gg = salome.ImportComponentGUI("GEOM")
        if NEW_SALOME:
            geompy = geomBuilder.New()
        else:
            geompy = geomBuilder.New(theStudy)
        self.geompy = geompy

        O = geompy.MakeVertex(0, 0, 0)
        OX = geompy.MakeVectorDXDYDZ(1, 0, 0)
        OY = geompy.MakeVectorDXDYDZ(0, 1, 0)
        OZ = geompy.MakeVectorDXDYDZ(0, 0, 1)
        geompy.addToStudy(O, "O")
        geompy.addToStudy(OX, "OX")
        geompy.addToStudy(OY, "OY")
        geompy.addToStudy(OZ, "OZ")

        if len([e for e in elements if e["geometry_type"] == "Edge"]) > 0:
            buildingShapeType = "EDGE"
        if len([e for e in elements if e["geometry_type"] == "Face"]) > 0:
            buildingShapeType = "FACE"

        ### Define entities ###
        start_time = time.time()
        print("Defining Object Geometry")
        init_time = start_time

        # Loop 1
        for el in elements:
            el["elemObj"] = self.makeObject(el["geometry"], el["geometry_type"])

            el["connObjs"] = [None for _ in el["connections"]]
            el["linkObjs"] = [None for _ in el["connections"]]
            el["linkPointObjs"] = [[None, None] for _ in el["connections"]]
            for j, rel in enumerate(el["connections"]):
                conn = [c for c in connections if c["ref_id"] == rel["related_connection"]][0]
                if rel["eccentricity"]:
                    rel["index"] = len(conn["related_elements"]) + 1
                conn["related_elements"].append(rel)

                if not rel["eccentricity"]:
                    el["connObjs"][j] = self.makeObject(conn["geometry"], conn["geometry_type"])
                else:
                    if conn["geometry_type"] == "Vertex":
                        geometry = rel["eccentricity"]["point_on_element"], conn["geometry"]
                        el["connObjs"][j] = self.makeObject(geometry[0], conn["geometry_type"])

                        el["linkPointObjs"][j][0] = self.geompy.MakeVertex(
                            geometry[0][0], geometry[0][1], geometry[0][2]
                        )
                        el["linkPointObjs"][j][1] = self.geompy.MakeVertex(
                            geometry[1][0], geometry[1][1], geometry[1][2]
                        )
                        el["linkObjs"][j] = self.geompy.MakeLineTwoPnt(
                            el["linkPointObjs"][j][0], el["linkPointObjs"][j][1]
                        )
                    else:
                        print("Eccentricity defined for a %s geometry_type" % conn["geometry_type"])
            el["partObj"] = self.makePartition([el["elemObj"]] + el["connObjs"], el["geometry_type"])
            el["elemObj"] = geompy.GetInPlace(el["partObj"], el["elemObj"], True)
            for j, rel in enumerate(el["connections"]):
                el["connObjs"][j] = geompy.GetInPlace(el["partObj"], el["connObjs"][j], True)
        for conn in connections:
            conn["connObj"] = self.makeObject(conn["geometry"], conn["geometry_type"])

        # Make assemble of Building Object
        bldObjs = []
        bldObjs.extend([el["partObj"] for el in elements])
        bldObjs.extend(flatten([[link for link in el["linkObjs"] if link] for el in elements]))
        bldObjs.extend([conn["connObj"] for conn in connections])

        bldComp = geompy.MakeCompound(bldObjs)
        # bldComp = geompy.MakePartition(bldObjs, [], [], [], self.geompy.ShapeType[buildingShapeType], 0, [], 1)
        geompy.addToStudy(bldComp, "bldComp")

        # Loop 2
        for el in elements:
            # geompy.addToStudy(el['partObj'], self.getGroupName(el['ref_id']))
            geompy.addToStudyInFather(el["partObj"], el["elemObj"], self.getGroupName(el["ref_id"]))
            for j, rel in enumerate(el["connections"]):
                conn = [c for c in connections if c["ref_id"] == rel["related_connection"]][0]
                rel["conn_string"] = None
                if conn["geometry_type"] == "Vertex":
                    rel["conn_string"] = "_0DC_"
                if conn["geometry_type"] == "Edge":
                    rel["conn_string"] = "_1DC_"
                if conn["geometry_type"] == "Face":
                    rel["conn_string"] = "_2DC_"
                geompy.addToStudyInFather(
                    el["partObj"],
                    el["connObjs"][j],
                    self.getGroupName(el["ref_id"]) + rel["conn_string"] + self.getGroupName(rel["related_connection"]),
                )
                if rel["eccentricity"]:
                    pass
                    # geompy.addToStudy(el['linkObjs'][j], self.getGroupName(el['ref_id']) + '_1DR_' + self.getGroupName(rel['related_connection']))
                    # geompy.addToStudyInFather(el['linkObjs'][j], el['linkPointObjs'][j][0], self.getGroupName(rel['related_connection']) + '_0DC_' + self.getGroupName(el['ref_id']))
                    # geompy.addToStudyInFather(el['linkObjs'][j], el['linkPointObjs'][j][0], self.getGroupName(rel['related_connection']) + '_0DC_%g' % rel['index'])

        for conn in connections:
            # geompy.addToStudy(conn['connObj'], self.getGroupName(conn['ref_id']))
            geompy.addToStudyInFather(conn["connObj"], conn["connObj"], self.getGroupName(conn["ref_id"]))

        elapsed_time = time.time() - init_time
        init_time += elapsed_time
        print("Building Geometry Defined in %g sec" % (elapsed_time))

        # Define and add groups for all curve and surface members
        if len([e for e in elements if e["geometry_type"] == "Edge"]) > 0:
            # Make compound of requested group
            compoundTemp = geompy.MakeCompound([e["elemObj"] for e in elements if e["geometry_type"] == "Edge"])
            # Define group object and add to study
            curveCompound = geompy.GetInPlace(bldComp, compoundTemp, True)
            geompy.addToStudyInFather(bldComp, curveCompound, "CurveMembers")

        rigid_links = list(flatten([[link for link in el["linkObjs"] if link] for el in elements]))
        if len(rigid_links) > 0:
            # Make compound of requested group
            compoundTemp = geompy.MakeCompound(rigid_links)
            # Define group object and add to study
            rigidLinkCompound = geompy.GetInPlace(bldComp, compoundTemp, True)
            geompy.addToStudyInFather(bldComp, rigidLinkCompound, "RigidLinks")

        if len([e for e in elements if e["geometry_type"] == "Face"]) > 0:
            # Make compound of requested group
            compoundTemp = geompy.MakeCompound([e["elemObj"] for e in elements if e["geometry_type"] == "Face"])
            # Define group object and add to study
            surfaceCompound = geompy.GetInPlace(bldComp, compoundTemp, True)
            geompy.addToStudyInFather(bldComp, surfaceCompound, "SurfaceMembers")

        # Loop 3
        for el in elements:
            # el['partObj'] = geompy.RestoreGivenSubShapes(bldComp, [el['partObj']], GEOM.FSM_GetInPlace, False, False)[0]
            geompy.addToStudyInFather(bldComp, el["elemObj"], self.getGroupName(el["ref_id"]))

            for j, rel in enumerate(el["connections"]):
                geompy.addToStudyInFather(
                    bldComp,
                    el["connObjs"][j],
                    self.getGroupName(el["ref_id"]) + rel["conn_string"] + self.getGroupName(rel["related_connection"]),
                )
                if rel["eccentricity"]:  # point geometry
                    geompy.addToStudyInFather(
                        bldComp,
                        el["linkObjs"][j],
                        self.getGroupName(el["ref_id"]) + "_1DR_" + self.getGroupName(rel["related_connection"]),
                    )
                    geompy.addToStudyInFather(
                        bldComp,
                        el["linkPointObjs"][j][0],
                        self.getGroupName(rel["related_connection"]) + "_0DC_" + self.getGroupName(el["ref_id"]),
                    )
                    geompy.addToStudyInFather(
                        bldComp,
                        el["linkPointObjs"][j][1],
                        self.getGroupName(rel["related_connection"]) + "_0DC_%g" % rel["index"],
                    )

        for conn in connections:
            # conn['connObj'] = geompy.RestoreGivenSubShapes(bldComp, [conn['connObj']], GEOM.FSM_GetInPlace, False, False)[0]
            geompy.addToStudyInFather(bldComp, conn["connObj"], self.getGroupName(conn["ref_id"]))

        elapsed_time = time.time() - init_time
        init_time += elapsed_time
        print("Building Geometry Groups Defined in %g sec" % (elapsed_time))

        ###
        ### SMESH component
        ###

        import SMESH
        from salome.smesh import smeshBuilder

        print("Defining Mesh Components")

        if NEW_SALOME:
            smesh = smeshBuilder.New()
        else:
            smesh = smeshBuilder.New(theStudy)
        bldMesh = smesh.Mesh(bldComp)
        Regular_1D = bldMesh.Segment()
        Local_Length_1 = Regular_1D.LocalLength(mesh_size, None, tolLoc)

        if buildingShapeType == "FACE":
            NETGEN2D_ONLY = bldMesh.Triangle(algo=smeshBuilder.NETGEN_2D)
            NETGEN2D_Pars = NETGEN2D_ONLY.Parameters()
            NETGEN2D_Pars.SetMaxSize(mesh_size)
            NETGEN2D_Pars.SetOptimize(1)
            NETGEN2D_Pars.SetFineness(2)
            NETGEN2D_Pars.SetMinSize(mesh_size / 5.0)
            NETGEN2D_Pars.SetUseSurfaceCurvature(1)
            NETGEN2D_Pars.SetQuadAllowed(1)
            NETGEN2D_Pars.SetSecondOrder(0)
            NETGEN2D_Pars.SetFuseEdges(254)

        isDone = bldMesh.Compute()

        ## Set names of Mesh objects
        smesh.SetName(Regular_1D.GetAlgorithm(), "Regular_1D")
        smesh.SetName(Local_Length_1, "Local_Length_1")

        if buildingShapeType == "FACE":
            smesh.SetName(NETGEN2D_ONLY.GetAlgorithm(), "NETGEN2D_ONLY")
            smesh.SetName(NETGEN2D_Pars, "NETGEN2D_Pars")

        smesh.SetName(bldMesh.GetMesh(), "{{ mesh_name }}")

        elapsed_time = time.time() - init_time
        init_time += elapsed_time
        print("Meshing Operations Completed in %g sec" % (elapsed_time))

        # Define and add groups for all curve and surface members
        if len([e for e in elements if e["geometry_type"] == "Edge"]) > 0:
            tempgroup = bldMesh.GroupOnGeom(curveCompound, "CurveMembers", SMESH.EDGE)
            smesh.SetName(tempgroup, "CurveMembers")

        if len(rigid_links) > 0:
            tempgroup = bldMesh.GroupOnGeom(rigidLinkCompound, "RigidLinks", SMESH.EDGE)
            smesh.SetName(tempgroup, "RigidLinks")

        if len([e for e in elements if e["geometry_type"] == "Face"]) > 0:
            tempgroup = bldMesh.GroupOnGeom(surfaceCompound, "SurfaceMembers", SMESH.FACE)
            smesh.SetName(tempgroup, "SurfaceMembers")

        # Define groups in Mesh
        for el in elements:
            if el["geometry_type"] == "Edge":
                shapeType = SMESH.EDGE
            if el["geometry_type"] == "Face":
                shapeType = SMESH.FACE
            tempgroup = bldMesh.GroupOnGeom(el["elemObj"], self.getGroupName(el["ref_id"]), shapeType)
            smesh.SetName(tempgroup, self.getGroupName(el["ref_id"]))
            # tempgroup = bldMesh.GroupOnGeom(el["elemObj"], self.getGroupName(el["ref_id"]), SMESH.NODE)
            # smesh.SetName(tempgroup, self.getGroupName(el["ref_id"]))

            for j, rel in enumerate(el["connections"]):
                tempgroup = bldMesh.GroupOnGeom(
                    el["connObjs"][j],
                    self.getGroupName(el["ref_id"]) + rel["conn_string"] + self.getGroupName(rel["related_connection"]),
                    SMESH.NODE,
                )
                smesh.SetName(
                    tempgroup,
                    self.getGroupName(el["ref_id"]) + rel["conn_string"] + self.getGroupName(rel["related_connection"]),
                )
                rel["node"] = (bldMesh.GetIDSource(tempgroup.GetNodeIDs(), SMESH.NODE)).GetIDs()[0]
                if rel["eccentricity"]:
                    tempgroup = bldMesh.GroupOnGeom(
                        el["linkObjs"][j],
                        self.getGroupName(el["ref_id"]) + "_1DR_" + self.getGroupName(rel["related_connection"]),
                        SMESH.EDGE,
                    )
                    smesh.SetName(
                        tempgroup,
                        self.getGroupName(el["ref_id"]) + "_1DR_" + self.getGroupName(rel["related_connection"]),
                    )

                    tempgroup = bldMesh.GroupOnGeom(
                        el["linkPointObjs"][j][0],
                        self.getGroupName(rel["related_connection"]) + "_0DC_" + self.getGroupName(el["ref_id"]),
                        SMESH.NODE,
                    )
                    smesh.SetName(
                        tempgroup,
                        self.getGroupName(rel["related_connection"]) + "_0DC_" + self.getGroupName(el["ref_id"]),
                    )
                    rel["eccNode"] = (bldMesh.GetIDSource(tempgroup.GetNodeIDs(), SMESH.NODE)).GetIDs()[0]

                    tempgroup = bldMesh.GroupOnGeom(
                        el["linkPointObjs"][j][1],
                        self.getGroupName(rel["related_connection"])
                        + "_0DC_"
                        + self.getGroupName(rel["related_connection"]),
                        SMESH.NODE,
                    )
                    smesh.SetName(
                        tempgroup,
                        self.getGroupName(rel["related_connection"]) + "_0DC_%g" % rel["index"],
                    )

        for conn in connections:
            tempgroup = bldMesh.GroupOnGeom(conn["connObj"], self.getGroupName(conn["ref_id"]), SMESH.NODE)
            smesh.SetName(tempgroup, self.getGroupName(conn["ref_id"]))
            nodesId = bldMesh.GetIDSource(tempgroup.GetNodeIDs(), SMESH.NODE)
            tempgroup = bldMesh.Add0DElementsToAllNodes(nodesId, self.getGroupName(conn["ref_id"]))
            smesh.SetName(tempgroup, self.getGroupName(conn["ref_id"] + "_0D"))
            if conn["geometry_type"] == "Vertex":
                conn["node"] = nodesId.GetIDs()[0]
            if conn["geometry_type"] == "Edge":
                tempgroup = bldMesh.GroupOnGeom(conn["connObj"], self.getGroupName(conn["ref_id"]), SMESH.EDGE)
                smesh.SetName(tempgroup, self.getGroupName(conn["ref_id"]))
            if conn["geometry_type"] == "Face":
                tempgroup = bldMesh.GroupOnGeom(conn["connObj"], self.getGroupName(conn["ref_id"]), SMESH.FACE)
                smesh.SetName(tempgroup, self.getGroupName(conn["ref_id"]))

        # create 1D SEG2 spring elements
        for el in elements:
            for j, rel in enumerate(el["connections"]):
                conn = [c for c in connections if c["ref_id"] == rel["related_connection"]][0]
                if conn["geometry_type"] == "Vertex":
                    grpName = bldMesh.CreateEmptyGroup(
                        SMESH.EDGE,
                        self.getGroupName(el["ref_id"]) + "_1DS_" + self.getGroupName(rel["related_connection"]),
                    )
                    smesh.SetName(
                        grpName,
                        self.getGroupName(el["ref_id"]) + "_1DS_" + self.getGroupName(rel["related_connection"]),
                    )
                    if not rel["eccentricity"]:
                        conn = [conn for conn in connections if conn["ref_id"] == rel["related_connection"]][0]
                        grpName.Add([bldMesh.AddEdge([conn["node"], rel["node"]])])
                    else:
                        grpName.Add([bldMesh.AddEdge([rel["eccNode"], rel["node"]])])

        self.mesh = bldMesh
        self.meshNodes = bldMesh.GetNodesId()

        elapsed_time = time.time() - init_time
        init_time += elapsed_time
        print("Mesh Groups Defined in %g sec" % (elapsed_time))

        try:
            if NEW_SALOME:
                bldMesh.ExportMED(
                    self.medFilename,
                    auto_groups=0,
                    minor=40,
                    overwrite=1,
                    meshPart=None,
                    autoDimension=0,
                )
            else:
                bldMesh.ExportMED(self.medFilename, 0, SMESH.MED_V2_2, 1, None, 0)
        except:
            print("ExportMED() failed. Invalid file name?")

        # if salome.sg.hasDesktop():
        #     if NEW_SALOME:
        #         salome.sg.updateObjBrowser()
        #     else:
        #         salome.sg.updateObjBrowser(1)

        elapsed_time = init_time - start_time
        print("ALL Operations Completed in %g sec" % (elapsed_time))


model = MODEL()

for el in model.elements:
    for j, conn in enumerate(el["connections"]):
        d = model.geompy.MinDistance(el["elemObj"], el["connObjs"][j])
        if d > 0:
            print(f'NOTE: Element {el["ref_id"]} and connection {conn["ref_id"]} have a distance of {d}')
        # elif d == 0:
        #     print(
        #         f'SUCCESS: Element {el["ref_id"]} and connection {conn["ref_id"]} have a distance of {d}'
        #     )

if salome.sg.hasDesktop():
    if model.NEW_SALOME:
        salome.sg.updateObjBrowser()
    else:
        salome.sg.updateObjBrowser(1)
