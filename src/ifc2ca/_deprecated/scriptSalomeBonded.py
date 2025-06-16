# Ifc2CA - IFC Code_Aster utility
# Copyright (C) 2020, 2021 Ioannis P. Christovasilis <ipc@aethereng.com>
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

import os
import time
import json
import salome
import salome_notebook
import salome_version
import numpy as np
import itertools
from pathlib import Path

flatten = itertools.chain.from_iterable


class MODEL:
    def __init__(self, dataFilename, medFilename, meshSize, zGround):
        self.dataFilename = dataFilename
        self.medFilename = medFilename
        self.meshSize = meshSize
        self.zGround = zGround
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

    def makeObject(self, geometry, geometryType):
        if geometryType == "point":
            return self.makePoint(geometry)
        if geometryType == "line":
            return self.makeLine(geometry)
        if geometryType == "surface":
            return self.makeFace(geometry)

    def makePartition(self, objects, geometryType):
        if geometryType == "point":
            shapeType = "VERTEX"
        if geometryType == "line":
            shapeType = "EDGE"
        if geometryType == "surface":
            shapeType = "FACE"
        return self.geompy.MakePartition(objects, [], [], [], self.geompy.ShapeType[shapeType], 0, [], 1)

    def getLinkGeometry(self, ecc, orientation, finalPoint):
        vector = np.array(orientation).transpose().dot(ecc["vector"])
        initialPoint = (np.array(finalPoint) - vector).tolist()
        return [initialPoint, finalPoint]

    def length(self, geometry):
        return (
            (geometry[1][0] - geometry[0][0]) ** 2
            + (geometry[1][1] - geometry[0][1]) ** 2
            + (geometry[1][2] - geometry[0][2]) ** 2
        ) ** 0.5

    def select(self, elements):
        zmin = -100
        zmax = 126300
        for el in elements:
            include = True
            for p in el["geometry"]:
                if p[2] < zmin or p[2] > zmax:
                    include = False
                    break
            el["include"] = include
        return [el for el in elements if el["include"]]

    def create(self):
        # Read data from input file
        with open(self.dataFilename) as dataFile:
            data = json.load(dataFile)

        # print(len(data['elements']))
        # elements = self.select(data['elements'])
        # print(len(elements))
        elements = data["elements"]
        connections = data["connections"]
        # --> Delete this reference data and repopulate it with the objects
        # while going through elements
        for conn in connections:
            conn["relatedElements"] = []
        # End <--

        meshSize = self.meshSize
        zGround = self.zGround

        dec = 5  # 4 decimals for length in mm
        tol = 10 ** (-dec - 3 + 1)

        self.tolLoc = tol * 10 * 2
        tolLoc = self.tolLoc

        NEW_SALOME = int(salome_version.getVersion()[0]) >= 9
        salome.salome_init()
        theStudy = salome.myStudy
        notebook = salome_notebook.NoteBook(theStudy)

        ###
        ### GEOM component
        ###
        import GEOM
        from salome.geom import geomBuilder
        import math
        import SALOMEDS

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

        if len([e for e in elements if e["geometryType"] == "line"]) > 0:
            buildingShapeType = "EDGE"
        if len([e for e in elements if e["geometryType"] == "surface"]) > 0:
            buildingShapeType = "FACE"

        ### Define entities ###
        start_time = time.time()
        print("Defining Object Geometry")
        init_time = start_time

        # Loop 1
        for el in elements:
            el["elemObj"] = self.makeObject(el["geometry"], el["geometryType"])

            el["linkObjs"] = [None for _ in el["connections"]]
            for j, rel in enumerate(el["connections"]):
                conn = next(c for c in connections if c["referenceName"] == rel["relatedConnection"])
                if rel["eccentricity"]:
                    rel["index"] = len(conn["relatedElements"]) + 1

                    geometry = self.getLinkGeometry(rel["eccentricity"], el["orientation"], conn["geometry"])
                    el["linkObjs"][j] = self.makeObject(geometry, "line")
                conn["relatedElements"].append(rel)

        # Make assemble of Building Object
        bldObjs = []
        bldObjs.extend([el["elemObj"] for el in elements])
        bldObjs.extend(flatten([[link for link in el["linkObjs"] if link] for el in elements]))

        # bldComp = geompy.MakeCompound(bldObjs)
        bldComp = geompy.MakePartition(bldObjs, [], [], [], self.geompy.ShapeType[buildingShapeType], 0, [], 1)
        geompy.addToStudy(bldComp, "bldComp")

        elapsed_time = time.time() - init_time
        init_time += elapsed_time
        print("Building Geometry Defined in %g sec" % (elapsed_time))

        # Define and add groups for all curve, surface and rigid members
        if len([e for e in elements if e["geometryType"] == "line"]) > 0:
            # Make compound of requested group
            compoundTemp = geompy.MakeCompound([e["elemObj"] for e in elements if e["geometryType"] == "line"])
            # Define group object and add to study
            curveCompound = geompy.GetInPlace(bldComp, compoundTemp, True)
            geompy.addToStudyInFather(bldComp, curveCompound, "CurveMembers")

        if len([e for e in elements if e["geometryType"] == "surface"]) > 0:
            # Make compound of requested group
            compoundTemp = geompy.MakeCompound([e["elemObj"] for e in elements if e["geometryType"] == "surface"])
            # Define group object and add to study
            surfaceCompound = geompy.GetInPlace(bldComp, compoundTemp, True)
            geompy.addToStudyInFather(bldComp, surfaceCompound, "SurfaceMembers")

        linkObjs = list(flatten([[obj for obj in el["linkObjs"] if obj] for el in elements]))
        if len(linkObjs) > 0:
            # Make compound of requested group
            compoundTemp = geompy.MakeCompound(linkObjs)
            # Define group object and add to study
            rigidCompound = geompy.GetInPlace(bldComp, compoundTemp, True)
            geompy.addToStudyInFather(bldComp, rigidCompound, "RigidMembers")

        for el in elements:
            # el['partObj'] = geompy.RestoreGivenSubShapes(bldComp, [el['partObj']], GEOM.FSM_GetInPlace, False, False)[0]
            el["elemObj"] = geompy.GetInPlace(bldComp, el["elemObj"], True)
            geompy.addToStudyInFather(bldComp, el["elemObj"], self.getGroupName(el["referenceName"]))

            for j, rel in enumerate(el["connections"]):
                if rel["eccentricity"]:  # point geometry
                    el["linkObjs"][j] = geompy.GetInPlace(bldComp, el["linkObjs"][j], True)
                    geompy.addToStudyInFather(
                        bldComp,
                        el["linkObjs"][j],
                        self.getGroupName(el["referenceName"]) + "_1DR_" + self.getGroupName(rel["relatedConnection"]),
                    )

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
        Local_Length_1 = Regular_1D.LocalLength(meshSize, None, tolLoc)

        if buildingShapeType == "FACE":
            NETGEN2D_ONLY = bldMesh.Triangle(algo=smeshBuilder.NETGEN_2D)
            NETGEN2D_Pars = NETGEN2D_ONLY.Parameters()
            NETGEN2D_Pars.SetMaxSize(meshSize)
            NETGEN2D_Pars.SetOptimize(1)
            NETGEN2D_Pars.SetFineness(2)
            NETGEN2D_Pars.SetMinSize(meshSize / 5.0)
            NETGEN2D_Pars.SetUseSurfaceCurvature(1)
            NETGEN2D_Pars.SetQuadAllowed(1)
            NETGEN2D_Pars.SetSecondOrder(0)
            NETGEN2D_Pars.SetFuseEdges(254)

        isDone = bldMesh.Compute()
        coincident_nodes_on_part = bldMesh.FindCoincidentNodesOnPart([bldMesh], tolLoc, [], 0)
        if coincident_nodes_on_part:
            # bldMesh.MergeNodes(coincident_nodes_on_part, [], 0)
            # print(f'{len(coincident_nodes_on_part)} Sets of Coincident Nodes Found and Merged')
            print(f"{len(coincident_nodes_on_part)} Sets of Coincident Nodes Found")
            print(f"{coincident_nodes_on_part}")

        ## Set names of Mesh objects
        smesh.SetName(Regular_1D.GetAlgorithm(), "Regular_1D")
        smesh.SetName(Local_Length_1, "Local_Length_1")

        if buildingShapeType == "FACE":
            smesh.SetName(NETGEN2D_ONLY.GetAlgorithm(), "NETGEN2D_ONLY")
            smesh.SetName(NETGEN2D_Pars, "NETGEN2D_Pars")

        smesh.SetName(bldMesh.GetMesh(), "bldMesh")

        elapsed_time = time.time() - init_time
        init_time += elapsed_time
        print("Meshing Operations Completed in %g sec" % (elapsed_time))

        # Define and add groups for all curve, surface and rigid members
        if len([e for e in elements if e["geometryType"] == "line"]) > 0:
            tempgroup = bldMesh.GroupOnGeom(curveCompound, "CurveMembers", SMESH.EDGE)
            smesh.SetName(tempgroup, "CurveMembers")

        if len([e for e in elements if e["geometryType"] == "surface"]) > 0:
            tempgroup = bldMesh.GroupOnGeom(surfaceCompound, "SurfaceMembers", SMESH.FACE)
            smesh.SetName(tempgroup, "SurfaceMembers")

        if len(linkObjs) > 0:
            tempgroup = bldMesh.GroupOnGeom(rigidCompound, "RigidMembers", SMESH.EDGE)
            smesh.SetName(tempgroup, "RigidMembers")

        # Define groups in Mesh
        for el in elements:
            if el["geometryType"] == "line":
                shapeType = SMESH.EDGE
            if el["geometryType"] == "surface":
                shapeType = SMESH.FACE
            tempgroup = bldMesh.GroupOnGeom(el["elemObj"], self.getGroupName(el["referenceName"]), shapeType)
            smesh.SetName(tempgroup, self.getGroupName(el["referenceName"]))

            for j, rel in enumerate(el["connections"]):
                if rel["eccentricity"]:
                    tempgroup = bldMesh.GroupOnGeom(
                        el["linkObjs"][j],
                        self.getGroupName(el["referenceName"]) + "_1DR_" + self.getGroupName(rel["relatedConnection"]),
                        SMESH.EDGE,
                    )
                    smesh.SetName(
                        tempgroup,
                        self.getGroupName(el["referenceName"]) + "_1DR_" + self.getGroupName(rel["relatedConnection"]),
                    )

        self.mesh = bldMesh
        self.meshNodes = bldMesh.GetNodesId()

        # Find ground supports and extract node coordinates
        grdSupps = bldMesh.CreateEmptyGroup(SMESH.NODE, "grdSupps")

        for node in self.meshNodes:
            coords = bldMesh.GetNodeXYZ(node)
            if abs(coords[2] - self.zGround) < tolLoc:
                grdSupps.Add([node])

        smesh.SetName(grdSupps, "grdSupps")

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

        if salome.sg.hasDesktop():
            if NEW_SALOME:
                salome.sg.updateObjBrowser()
            else:
                salome.sg.updateObjBrowser(1)

        elapsed_time = init_time - start_time
        print("ALL Operations Completed in %g sec" % (elapsed_time))


if __name__ == "__main__":
    fileNames = ["test"]
    files = fileNames

    meshSize = 0.5
    zGround = 0

    for fileName in files:
        BASE_PATH = Path("/home/jesusbill/Dev-Projects/github.com/IfcOpenShell/analysis-models/models/")
        DATAFILENAME = BASE_PATH / fileName / f"{fileName}.json"
        MEDFILENAME = BASE_PATH / fileName / f"{fileName}.med"
        model = MODEL(DATAFILENAME, str(MEDFILENAME), meshSize, zGround)
