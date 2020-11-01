from __future__ import division
from __future__ import print_function
import os
import time
import json
import salome
import salome_notebook
import salome_version
import numpy as np
import itertools

flatten = itertools.chain.from_iterable


class MODEL:
    def __init__(self, dataFilename, medFilename, meshSize):
        self.dataFilename = dataFilename
        self.medFilename = medFilename
        self.meshSize = meshSize
        self.tolLoc = 0
        self.mesh = None
        self.meshNodes = None
        self.create()

    def getGroupName(self, name):
        info = name.split("|")
        sortName = "".join(c for c in info[0] if c.isupper())
        return str(sortName + "_" + info[1])

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

    def create(self):
        # Read data from input file
        with open(self.dataFilename) as dataFile:
            data = json.load(dataFile)

        elements = data["elements"]
        connections = data["connections"]
        # --> Delete this reference data and repopulate it with the objects
        # while going through elements
        for conn in connections:
            conn["relatedElements"] = []
        # End <--

        meshSize = self.meshSize

        dec = 7  # 4 decimals for length in mm
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

            el["connObjs"] = [None for _ in el["connections"]]
            el["linkObjs"] = [None for _ in el["connections"]]
            el["linkPointObjs"] = [[None, None] for _ in el["connections"]]
            for j, rel in enumerate(el["connections"]):
                conn = [c for c in connections if c["ifcName"] == rel["relatedConnection"]][0]
                if rel["eccentricity"]:
                    rel["index"] = len(conn["relatedElements"]) + 1
                conn["relatedElements"].append(rel)

                if not rel["eccentricity"]:
                    el["connObjs"][j] = self.makeObject(conn["geometry"], conn["geometryType"])
                else:
                    if conn["geometryType"] == "point":
                        geometry = self.getLinkGeometry(rel["eccentricity"], el["orientation"], conn["geometry"])
                        el["connObjs"][j] = self.makeObject(geometry[0], conn["geometryType"])

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
                        print("Eccentricity defined for a %s geometryType" % conn["geometryType"])

            el["partObj"] = self.makePartition([el["elemObj"]] + el["connObjs"], el["geometryType"])

            el["elemObj"] = geompy.GetInPlace(el["partObj"], el["elemObj"])
            for j, rel in enumerate(el["connections"]):
                el["connObjs"][j] = geompy.GetInPlace(el["partObj"], el["connObjs"][j])

        for conn in connections:
            conn["connObj"] = self.makeObject(conn["geometry"], conn["geometryType"])

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
            # geompy.addToStudy(el['partObj'], self.getGroupName(el['ifcName']))
            geompy.addToStudyInFather(el["partObj"], el["elemObj"], self.getGroupName(el["ifcName"]))
            for j, rel in enumerate(el["connections"]):
                conn = [c for c in connections if c["ifcName"] == rel["relatedConnection"]][0]
                rel["conn_string"] = None
                if conn["geometryType"] == "point":
                    rel["conn_string"] = "_0DC_"
                if conn["geometryType"] == "line":
                    rel["conn_string"] = "_1DC_"
                if conn["geometryType"] == "surface":
                    rel["conn_string"] = "_2DC_"
                geompy.addToStudyInFather(
                    el["partObj"],
                    el["connObjs"][j],
                    self.getGroupName(el["ifcName"]) + rel["conn_string"] + self.getGroupName(rel["relatedConnection"]),
                )
                if rel["eccentricity"]:
                    pass
                    # geompy.addToStudy(el['linkObjs'][j], self.getGroupName(el['ifcName']) + '_1DR_' + self.getGroupName(rel['relatedConnection']))
                    # geompy.addToStudyInFather(el['linkObjs'][j], el['linkPointObjs'][j][0], self.getGroupName(rel['relatedConnection']) + '_0DC_' + self.getGroupName(el['ifcName']))
                    # geompy.addToStudyInFather(el['linkObjs'][j], el['linkPointObjs'][j][0], self.getGroupName(rel['relatedConnection']) + '_0DC_%g' % rel['index'])

        for conn in connections:
            # geompy.addToStudy(conn['connObj'], self.getGroupName(conn['ifcName']))
            geompy.addToStudyInFather(conn["connObj"], conn["connObj"], self.getGroupName(conn["ifcName"]))

        elapsed_time = time.time() - init_time
        init_time += elapsed_time
        print("Building Geometry Defined in %g sec" % (elapsed_time))

        if len([e for e in elements if e["geometryType"] == "line"]) > 0:
            buildingShapeType = "EDGE"
        if len([e for e in elements if e["geometryType"] == "surface"]) > 0:
            buildingShapeType = "FACE"

        # Define and add groups for all curve and surface members
        if len([e for e in elements if e["geometryType"] == "line"]) > 0:
            # Make compound of requested group
            compoundTemp = geompy.MakeCompound([e["elemObj"] for e in elements if e["geometryType"] == "line"])
            # Define group object and add to study
            curveCompound = geompy.GetInPlace(bldComp, compoundTemp)
            geompy.addToStudyInFather(bldComp, curveCompound, "CurveMembers")

        if len([e for e in elements if e["geometryType"] == "surface"]) > 0:
            # Make compound of requested group
            compoundTemp = geompy.MakeCompound([e["elemObj"] for e in elements if e["geometryType"] == "surface"])
            # Define group object and add to study
            surfaceCompound = geompy.GetInPlace(bldComp, compoundTemp)
            geompy.addToStudyInFather(bldComp, surfaceCompound, "SurfaceMembers")

        # Loop 3
        for el in elements:
            # el['partObj'] = geompy.RestoreGivenSubShapes(bldComp, [el['partObj']], GEOM.FSM_GetInPlace, False, False)[0]
            geompy.addToStudyInFather(bldComp, el["elemObj"], self.getGroupName(el["ifcName"]))

            for j, rel in enumerate(el["connections"]):
                geompy.addToStudyInFather(
                    bldComp,
                    el["connObjs"][j],
                    self.getGroupName(el["ifcName"]) + rel["conn_string"] + self.getGroupName(rel["relatedConnection"]),
                )
                if rel["eccentricity"]:  # point geometry
                    geompy.addToStudyInFather(
                        bldComp,
                        el["linkObjs"][j],
                        self.getGroupName(el["ifcName"]) + "_1DR_" + self.getGroupName(rel["relatedConnection"]),
                    )
                    geompy.addToStudyInFather(
                        bldComp,
                        el["linkPointObjs"][j][0],
                        self.getGroupName(rel["relatedConnection"]) + "_0DC_" + self.getGroupName(el["ifcName"]),
                    )
                    geompy.addToStudyInFather(
                        bldComp,
                        el["linkPointObjs"][j][1],
                        self.getGroupName(rel["relatedConnection"]) + "_0DC_%g" % rel["index"],
                    )

        for conn in connections:
            # conn['connObj'] = geompy.RestoreGivenSubShapes(bldComp, [conn['connObj']], GEOM.FSM_GetInPlace, False, False)[0]
            geompy.addToStudyInFather(bldComp, conn["connObj"], self.getGroupName(conn["ifcName"]))

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

        # Define and add groups for all curve and surface members
        if len([e for e in elements if e["geometryType"] == "line"]) > 0:
            tempgroup = bldMesh.GroupOnGeom(curveCompound, "CurveMembers", SMESH.EDGE)
            smesh.SetName(tempgroup, "CurveMembers")

        if len([e for e in elements if e["geometryType"] == "surface"]) > 0:
            tempgroup = bldMesh.GroupOnGeom(surfaceCompound, "SurfaceMembers", SMESH.FACE)
            smesh.SetName(tempgroup, "SurfaceMembers")

        # Define groups in Mesh
        for el in elements:
            if el["geometryType"] == "line":
                shapeType = SMESH.EDGE
            if el["geometryType"] == "surface":
                shapeType = SMESH.FACE
            tempgroup = bldMesh.GroupOnGeom(el["elemObj"], self.getGroupName(el["ifcName"]), shapeType)
            smesh.SetName(tempgroup, self.getGroupName(el["ifcName"]))

            for j, rel in enumerate(el["connections"]):
                tempgroup = bldMesh.GroupOnGeom(
                    el["connObjs"][j],
                    self.getGroupName(el["ifcName"]) + rel["conn_string"] + self.getGroupName(rel["relatedConnection"]),
                    SMESH.NODE,
                )
                smesh.SetName(
                    tempgroup,
                    self.getGroupName(el["ifcName"]) + rel["conn_string"] + self.getGroupName(rel["relatedConnection"]),
                )
                rel["node"] = (bldMesh.GetIDSource(tempgroup.GetNodeIDs(), SMESH.NODE)).GetIDs()[0]
                if rel["eccentricity"]:
                    tempgroup = bldMesh.GroupOnGeom(
                        el["linkObjs"][j],
                        self.getGroupName(el["ifcName"]) + "_1DR_" + self.getGroupName(rel["relatedConnection"]),
                        SMESH.EDGE,
                    )
                    smesh.SetName(
                        tempgroup,
                        self.getGroupName(el["ifcName"]) + "_1DR_" + self.getGroupName(rel["relatedConnection"]),
                    )

                    tempgroup = bldMesh.GroupOnGeom(
                        el["linkPointObjs"][j][0],
                        self.getGroupName(rel["relatedConnection"]) + "_0DC_" + self.getGroupName(el["ifcName"]),
                        SMESH.NODE,
                    )
                    smesh.SetName(
                        tempgroup,
                        self.getGroupName(rel["relatedConnection"]) + "_0DC_" + self.getGroupName(el["ifcName"]),
                    )
                    rel["eccNode"] = (bldMesh.GetIDSource(tempgroup.GetNodeIDs(), SMESH.NODE)).GetIDs()[0]

                    tempgroup = bldMesh.GroupOnGeom(
                        el["linkPointObjs"][j][1],
                        self.getGroupName(rel["relatedConnection"])
                        + "_0DC_"
                        + self.getGroupName(rel["relatedConnection"]),
                        SMESH.NODE,
                    )
                    smesh.SetName(tempgroup, self.getGroupName(rel["relatedConnection"]) + "_0DC_%g" % rel["index"])

        for conn in connections:
            tempgroup = bldMesh.GroupOnGeom(conn["connObj"], self.getGroupName(conn["ifcName"]), SMESH.NODE)
            smesh.SetName(tempgroup, self.getGroupName(conn["ifcName"]))
            nodesId = bldMesh.GetIDSource(tempgroup.GetNodeIDs(), SMESH.NODE)
            tempgroup = bldMesh.Add0DElementsToAllNodes(nodesId, self.getGroupName(conn["ifcName"]))
            smesh.SetName(tempgroup, self.getGroupName(conn["ifcName"] + "_0D"))
            if conn["geometryType"] == "point":
                conn["node"] = nodesId.GetIDs()[0]
            if conn["geometryType"] == "line":
                tempgroup = bldMesh.GroupOnGeom(conn["connObj"], self.getGroupName(conn["ifcName"]), SMESH.EDGE)
                smesh.SetName(tempgroup, self.getGroupName(conn["ifcName"]))
            if conn["geometryType"] == "surface":
                tempgroup = bldMesh.GroupOnGeom(conn["connObj"], self.getGroupName(conn["ifcName"]), SMESH.FACE)
                smesh.SetName(tempgroup, self.getGroupName(conn["ifcName"]))

        # create 1D SEG2 spring elements
        for el in elements:
            for j, rel in enumerate(el["connections"]):
                conn = [c for c in connections if c["ifcName"] == rel["relatedConnection"]][0]
                if conn["geometryType"] == "point":
                    grpName = bldMesh.CreateEmptyGroup(
                        SMESH.EDGE,
                        self.getGroupName(el["ifcName"]) + "_1DS_" + self.getGroupName(rel["relatedConnection"]),
                    )
                    smesh.SetName(
                        grpName,
                        self.getGroupName(el["ifcName"]) + "_1DS_" + self.getGroupName(rel["relatedConnection"]),
                    )
                    if not rel["eccentricity"]:
                        conn = [conn for conn in connections if conn["ifcName"] == rel["relatedConnection"]][0]
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
                    self.medFilename, auto_groups=0, minor=40, overwrite=1, meshPart=None, autoDimension=0
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
    fileNames = ["structure_01"]
    files = fileNames

    meshSize = 0.1

    for fileName in files:
        BASE_PATH = "/home/jesusbill/Dev-Projects/github.com/IfcOpenShell/analysis-models/models/"
        DATAFILENAME = BASE_PATH + fileName + "/" + fileName + ".json"
        MEDFILENAME = BASE_PATH + fileName + "/" + fileName + ".med"
        model = MODEL(DATAFILENAME, MEDFILENAME, meshSize)
