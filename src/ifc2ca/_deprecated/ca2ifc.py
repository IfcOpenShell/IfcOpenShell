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

import json
import ifcopenshell
import ifcopenshell.guid
import os
from datetime import datetime


class CA2IFC:
    def __init__(self, inputFilename, outputFilename):
        self.inputFilename = inputFilename
        self.outputFilename = outputFilename
        self.data = None
        self.f = None
        self.reps = {}
        self.origin = None
        self.xAxis = None
        self.yAxis = None
        self.zAxis = None

    def convert(self):
        # load json file
        with open(self.inputFilename) as dataFile:
            self.data = json.load(dataFile)

        # initiate ifc file
        self.f = ifcopenshell.file()

        # create header
        self.create_header()

        # create global axes
        globalAxes = self.create_global_axes()
        localPlacement = self.f.createIfcLocalPlacement(None, globalAxes)

        # TODO: create units
        lengthUnit = self.f.createIfcSIUnit(None, "LENGTHUNIT", None, "METRE")
        unitAssignment = self.f.createIfcUnitAssignment((lengthUnit,))

        # create owner history
        ownerHistory = self.create_owner_history()

        # create representations and subrepresentations
        self.reps = self.create_reference_subrep(globalAxes)

        # create project and model
        project = self.f.createIfcProject(
            self.guid(), ownerHistory, "A Project", None, None, None, None, (self.reps["model"],), unitAssignment
        )
        model = self.f.createIfcStructuralAnalysisModel(
            self.guid(),
            ownerHistory,
            self.data["name"],
            None,
            None,
            "NOTDEFINED",
            globalAxes,
            None,
            None,
            localPlacement,
        )
        self.f.createIfcRelDeclares(self.guid(), ownerHistory, None, None, project, (model,))

        # create materials
        ifcMaterials = [None for _ in range(len(self.data["db"]["materials"]))]
        for i, material in enumerate(self.data["db"]["materials"]):
            ifcMaterials[i] = self.create_material(material)

        # create profiles
        ifcProfiles = [None for _ in range(len(self.data["db"]["profiles"]))]
        for i, profile in enumerate(self.data["db"]["profiles"]):
            ifcProfiles[i] = self.create_profile(profile)

        # create material-profile sets
        mpSets = list(
            set([el["material"] + "-" + el["profile"] for el in self.data["elements"] if el["geometryType"] == "line"])
        )
        ifcMaterialProfileSets = [None for _ in range(len(mpSets))]
        for i, mpSet in enumerate(mpSets):
            materialIndex = [mat["referenceName"] for mat in self.data["db"]["materials"]].index(mpSet.split("-")[0])
            profileIndex = [prof["referenceName"] for prof in self.data["db"]["profiles"]].index(mpSet.split("-")[1])
            material = ifcMaterials[materialIndex]
            profile = ifcProfiles[profileIndex]
            matProf = self.f.createIfcMaterialProfile(
                self.data["db"]["materials"][materialIndex]["name"]
                + " | "
                + self.data["db"]["profiles"][profileIndex]["profileName"],
                None,
                material,
                profile,
            )
            ifcMaterialProfileSets[i] = self.f.createIfcMaterialProfileSet(None, None, (matProf,))

        # create structural elements
        ifcElements = [None for _ in range(len(self.data["elements"]))]
        for i, el in enumerate(self.data["elements"]):
            # geometry - product definition shape
            prodDefShape = self.create_geometry(el)

            if el["geometryType"] == "line":
                # z axis TODO: group by elements
                localZAxis = self.f.createIfcDirection(tuple(el["orientation"][2]))
                # element
                ifcElements[i] = self.f.createIfcStructuralCurveMember(
                    self.guid(),
                    ownerHistory,
                    el["name"],
                    None,
                    None,
                    localPlacement,
                    prodDefShape,
                    el["predefinedType"],
                    localZAxis,
                )

            if el["geometryType"] == "surface":
                ifcElements[i] = self.f.createIfcStructuralSurfaceMember(
                    self.guid(),
                    ownerHistory,
                    el["name"],
                    None,
                    None,
                    localPlacement,
                    prodDefShape,
                    el["predefinedType"],
                    el["thickness"],
                )

        # create structural point connections
        ifcConnections = [None for _ in range(len(self.data["connections"]))]
        for i, conn in enumerate(self.data["connections"]):
            # geometry - product definition shape
            prodDefShape = self.create_geometry(conn)

            # boundary conditions
            if conn["appliedCondition"]:
                bc = self.create_applied_conditions(conn["appliedCondition"], conn["geometryType"])
                if conn["geometryType"] == "point":
                    appliedCondition = self.f.createIfcBoundaryNodeCondition(
                        None, bc["dx"], bc["dy"], bc["dz"], bc["drx"], bc["dry"], bc["drz"]
                    )
                if conn["geometryType"] == "line":
                    appliedCondition = self.f.createIfcBoundaryEdgeCondition(
                        None, bc["dx"], bc["dy"], bc["dz"], bc["drx"], bc["dry"], bc["drz"]
                    )
                if conn["geometryType"] == "surface":
                    appliedCondition = self.f.createIfcBoundaryFaceCondition(None, bc["dx"], bc["dy"], bc["dz"])
            else:
                appliedCondition = None

            if conn["geometryType"] == "point":
                # local axes
                localAxes = self.create_orientation(conn["orientation"])
                # connection
                ifcConnections[i] = self.f.createIfcStructuralPointConnection(
                    self.guid(),
                    ownerHistory,
                    conn["name"],
                    None,
                    None,
                    localPlacement,
                    prodDefShape,
                    appliedCondition,
                    localAxes,
                )

            if conn["geometryType"] == "line":
                # z axis TODO: group by elements
                localZAxis = self.f.createIfcDirection(tuple(conn["orientation"][2]))
                # connection
                ifcConnections[i] = self.f.createIfcStructuralCurveConnection(
                    self.guid(),
                    ownerHistory,
                    conn["name"],
                    None,
                    None,
                    localPlacement,
                    prodDefShape,
                    appliedCondition,
                    localZAxis,
                )

            if conn["geometryType"] == "surface":
                ifcConnections[i] = self.f.createIfcStructuralSurfaceConnection(
                    self.guid(), ownerHistory, conn["name"], None, None, localPlacement, prodDefShape, appliedCondition
                )

        # assign material-profile-sets
        for i, mpSet in enumerate(mpSets):
            groupOfElements = []
            for j, el in enumerate(self.data["elements"]):
                if el["geometryType"] == "line" and el["material"] + "-" + el["profile"] == mpSet:
                    groupOfElements.append(ifcElements[j])

            if groupOfElements:
                self.f.createIfcRelAssociatesMaterial(
                    self.guid(), ownerHistory, None, None, tuple(groupOfElements), ifcMaterialProfileSets[i]
                )

        # assign materials
        for i, mat in enumerate(self.data["db"]["materials"]):
            groupOfElements = []
            for j, el in enumerate(self.data["elements"]):
                if el["geometryType"] == "surface" and el["material"] == mat["referenceName"]:
                    groupOfElements.append(ifcElements[j])
            if groupOfElements:
                self.f.createIfcRelAssociatesMaterial(
                    self.guid(), ownerHistory, None, None, tuple(groupOfElements), ifcMaterials[i]
                )

        # create connections with elements
        for i, el in enumerate(self.data["elements"]):
            for conn in el["connections"]:
                j = [c["referenceName"] for c in self.data["connections"]].index(conn["relatedConnection"])
                geometryType = self.data["connections"][j]["geometryType"]

                if conn["appliedCondition"]:
                    bc = self.create_applied_conditions(conn["appliedCondition"], geometryType)
                    if geometryType == "point":
                        appliedCondition = self.f.createIfcBoundaryNodeCondition(
                            None, bc["dx"], bc["dy"], bc["dz"], bc["drx"], bc["dry"], bc["drz"]
                        )
                    if geometryType == "line":
                        appliedCondition = self.f.createIfcBoundaryEdgeCondition(
                            None, bc["dx"], bc["dy"], bc["dz"], bc["drx"], bc["dry"], bc["drz"]
                        )
                    if geometryType == "surface":
                        appliedCondition = self.f.createIfcBoundaryFaceCondition(None, bc["dx"], bc["dy"], bc["dz"])
                else:
                    appliedCondition = None

                # local axes
                localAxes = self.create_orientation(conn["orientation"])

                if geometryType == "point":
                    if not conn["eccentricity"]:
                        self.f.createIfcRelConnectsStructuralMember(
                            self.guid(),
                            ownerHistory,
                            None,
                            None,
                            ifcElements[i],
                            ifcConnections[j],
                            appliedCondition,
                            None,
                            None,
                            localAxes,
                        )
                    else:
                        pointOnElement = self.f.createIfcCartesianPoint(tuple(conn["eccentricity"]["pointOnElement"]))
                        vector = conn["eccentricity"]["vector"]
                        connPointEcc = self.f.createIfcConnectionPointEccentricity(
                            pointOnElement, None, vector[0], vector[1], vector[2]
                        )
                        self.f.createIfcRelConnectsWithEccentricity(
                            self.guid(),
                            ownerHistory,
                            None,
                            None,
                            ifcElements[i],
                            ifcConnections[j],
                            appliedCondition,
                            None,
                            None,
                            localAxes,
                            connPointEcc,
                        )

                if geometryType in ["line", "surface"]:
                    self.f.createIfcRelConnectsStructuralMember(
                        self.guid(),
                        ownerHistory,
                        None,
                        None,
                        ifcElements[i],
                        ifcConnections[j],
                        appliedCondition,
                        None,
                        None,
                        localAxes,
                    )

        # assign elements and connections to group
        self.f.createIfcRelAssignsToGroup(
            self.guid(), ownerHistory, None, None, tuple(ifcElements + ifcConnections), None, model
        )

        # finalize ifc file
        self.f.write(self.outputFilename)

    def guid(self):
        return ifcopenshell.guid.new()

    def create_header(self):
        self.f.wrapped_data.header.file_name.name = os.path.basename(self.outputFilename)

    def create_global_axes(self):
        self.xAxis = self.f.createIfcDirection((1.0, 0.0, 0.0))
        self.yAxis = self.f.createIfcDirection((0.0, 1.0, 0.0))
        self.zAxis = self.f.createIfcDirection((0.0, 0.0, 1.0))
        self.origin = self.f.createIfcCartesianPoint((0.0, 0.0, 0.0))
        axes = self.f.createIfcAxis2Placement3D(self.origin, self.zAxis, self.xAxis)

        return axes

    def create_orientation(self, orientation):
        xAxis = self.f.createIfcDirection(tuple(orientation[0]))
        zAxis = self.f.createIfcDirection(tuple(orientation[2]))
        axes = self.f.createIfcAxis2Placement3D(self.origin, zAxis, xAxis)

        return axes

    def create_owner_history(self):
        actor = self.f.createIfcActorRole("ENGINEER", None, None)
        person = self.f.createIfcPerson("Christovasilis", None, "Ioannis", None, None, None, (actor,))
        organization = self.f.createIfcOrganization(
            None,
            "IfcOpenShell",
            "IfcOpenShell, an open source (LGPL) software library that helps users and software developers to work with the IFC file format.",
        )
        p_o = self.f.createIfcPersonAndOrganization(person, organization)
        application = self.f.createIfcApplication(organization, "v0.0.x", "IFC2CA", "IFC2CA")
        timestamp = int(datetime.now().timestamp())
        ownerHistory = self.f.createIfcOwnerHistory(p_o, application, "READWRITE", None, None, None, None, timestamp)

        return ownerHistory

    def create_reference_subrep(self, globalAxes):
        modelRep = self.f.createIfcGeometricRepresentationContext(None, "Model", 3, 1.0e-05, globalAxes, None)
        bodySubRep = self.f.createIfcGeometricRepresentationSubContext(
            "Body", "Model", None, None, None, None, modelRep, None, "MODEL_VIEW", None
        )
        refSubRep = self.f.createIfcGeometricRepresentationSubContext(
            "Reference", "Model", None, None, None, None, modelRep, None, "GRAPH_VIEW", None
        )

        return {"model": modelRep, "body": bodySubRep, "reference": refSubRep}

    def create_material(self, material):
        ifcMaterial = self.f.createIfcMaterial(material["name"], None, material["category"])

        mechProps = []
        if "youngModulus" in material["mechProps"]:
            youngModulus = self.f.createIfcPropertySingleValue(
                "YoungModulus", None, self.f.createIfcModulusOfElasticityMeasure(material["mechProps"]["youngModulus"])
            )
            mechProps.append(youngModulus)
        if "shearModulus" in material["mechProps"]:
            shearModulus = self.f.createIfcPropertySingleValue(
                "ShearModulus", None, self.f.createIfcModulusOfElasticityMeasure(material["mechProps"]["shearModulus"])
            )
            mechProps.append(shearModulus)
        if "poissonRatio" in material["mechProps"]:
            poissonRatio = self.f.createIfcPropertySingleValue(
                "PoissonRatio", None, self.f.createIfcPositiveRatioMeasure(material["mechProps"]["poissonRatio"])
            )
            mechProps.append(poissonRatio)
        if mechProps:
            self.f.createIfcMaterialProperties(
                "Pset_MaterialMechanical", material["name"], tuple(mechProps), ifcMaterial
            )

        commonProps = []
        if "massDensity" in material["commonProps"]:
            massDensity = self.f.createIfcPropertySingleValue(
                "MassDensity", None, self.f.createIfcMassDensityMeasure(material["commonProps"]["massDensity"])
            )
            commonProps.append(massDensity)
        if commonProps:
            self.f.createIfcMaterialProperties("Pset_MaterialCommon", material["name"], tuple(commonProps), ifcMaterial)

        return ifcMaterial

    def create_profile(self, profile):
        if profile["profileShape"] == "rectangular":
            ifcProfile = self.f.createIfcRectangleProfileDef(
                profile["profileType"], profile["profileName"], None, profile["xDim"], profile["yDim"]
            )

        if profile["profileShape"] == "iSymmetrical":
            ifcProfile = self.f.createIfcIShapeProfileDef(
                profile["profileType"],
                profile["profileName"],
                None,
                profile["commonProps"]["overallWidth"],
                profile["commonProps"]["overallDepth"],
                profile["commonProps"]["webThickness"],
                profile["commonProps"]["flangeThickness"],
                profile["commonProps"]["filletRadius"],
            )

            mechProps = []
            if "massPerLength" in profile["mechProps"]:
                massPerLength = self.f.createIfcPropertySingleValue(
                    "MassPerLength", None, self.f.createIfcMassPerLengthMeasure(profile["mechProps"]["massPerLength"])
                )
                mechProps.append(massPerLength)
            if "crossSectionArea" in profile["mechProps"]:
                crossSectionArea = self.f.createIfcPropertySingleValue(
                    "CrossSectionArea", None, self.f.createIfcAreaMeasure(profile["mechProps"]["crossSectionArea"])
                )
                mechProps.append(crossSectionArea)
            if "momentOfInertiaY" in profile["mechProps"]:
                momentOfInertiaY = self.f.createIfcPropertySingleValue(
                    "MomentOfInertiaY",
                    None,
                    self.f.createIfcMomentOfInertiaMeasure(profile["mechProps"]["momentOfInertiaY"]),
                )
                mechProps.append(momentOfInertiaY)
            if "momentOfInertiaZ" in profile["mechProps"]:
                momentOfInertiaZ = self.f.createIfcPropertySingleValue(
                    "MomentOfInertiaZ",
                    None,
                    self.f.createIfcMomentOfInertiaMeasure(profile["mechProps"]["momentOfInertiaZ"]),
                )
                mechProps.append(momentOfInertiaZ)
            if "torsionalConstantX" in profile["mechProps"]:
                torsionalConstantX = self.f.createIfcPropertySingleValue(
                    "TorsionalConstantX",
                    None,
                    self.f.createIfcMomentOfInertiaMeasure(profile["mechProps"]["torsionalConstantX"]),
                )
                mechProps.append(torsionalConstantX)
            if mechProps:
                self.f.createIfcProfileProperties(
                    "Pset_ProfileMechanical", profile["profileName"], tuple(mechProps), ifcProfile
                )

        return ifcProfile

    def create_geometry(self, object):
        if object["geometryType"] == "point":
            point = self.f.createIfcCartesianPoint(tuple(object["geometry"]))
            vertex = self.f.createIfcVertexPoint(point)
            vertexTopologyRep = self.f.createIfcTopologyRepresentation(
                self.reps["reference"], "Reference", "Vertex", (vertex,)
            )
            vertexProdDefShape = self.f.createIfcProductDefinitionShape(None, None, (vertexTopologyRep,))

            return vertexProdDefShape

        if object["geometryType"] == "line":
            startPoint = self.f.createIfcCartesianPoint(tuple(object["geometry"][0]))
            startVertex = self.f.createIfcVertexPoint(startPoint)
            endPoint = self.f.createIfcCartesianPoint(tuple(object["geometry"][1]))
            endVertex = self.f.createIfcVertexPoint(endPoint)
            edge = self.f.createIfcEdge(startVertex, endVertex)
            edgeTopologyRep = self.f.createIfcTopologyRepresentation(
                self.reps["reference"], "Reference", "Edge", (edge,)
            )
            edgeProdDefShape = self.f.createIfcProductDefinitionShape(None, None, (edgeTopologyRep,))

            return edgeProdDefShape

        if object["geometryType"] == "surface":
            verts = [None for _ in range(len(object["geometry"]))]
            for i, p in enumerate(object["geometry"]):
                point = self.f.createIfcCartesianPoint(tuple(p))
                verts[i] = self.f.createIfcVertexPoint(point)

            orientedEdges = [None for _ in range(len(object["geometry"]))]
            for i, v in enumerate(verts):
                v2Index = (i + 1) if i < len(verts) - 1 else 0
                edge = self.f.createIfcEdge(v, verts[v2Index])
                orientedEdges[i] = self.f.createIfcOrientedEdge(None, None, edge, True)

            edgeLoop = self.f.createIfcEdgeLoop(tuple(orientedEdges))
            localAxes = self.create_orientation(object["orientation"])
            plane = self.f.createIfcPlane(localAxes)
            faceBound = self.f.createIfcFaceBound(edgeLoop, True)
            face = self.f.createIfcFaceSurface((faceBound,), plane, True)
            faceTopologyRep = self.f.createIfcTopologyRepresentation(
                self.reps["reference"], "Reference", "Face", (face,)
            )
            faceProdDefShape = self.f.createIfcProductDefinitionShape(None, None, (faceTopologyRep,))

            return faceProdDefShape

    def create_applied_conditions(self, bc, geometryType):
        for dof in ["dx", "dy", "dz"]:
            if isinstance(bc[dof], bool):
                bc[dof] = self.f.createIfcBoolean(bc[dof])
            else:
                if geometryType == "point":
                    bc[dof] = self.f.createIfcLinearStiffnessMeasure(bc[dof])
                if geometryType == "line":
                    bc[dof] = self.f.createIfcModulusOfLinearSubgradeReactionMeasure(bc[dof])
                if geometryType == "surface":
                    bc[dof] = self.f.createIfcModulusOfSubgradeReactionMeasure(bc[dof])

        for dof in ["drx", "dry", "drz"]:
            if isinstance(bc[dof], bool):
                bc[dof] = self.f.createIfcBoolean(bc[dof])
            else:
                if geometryType == "point":
                    bc[dof] = self.f.createIfcRotationalStiffnessMeasure(bc[dof])
                if geometryType == "line":
                    bc[dof] = self.f.createIfcModulusOfRotationalSubgradeReactionMeasure(bc[dof])

        return bc


if __name__ == "__main__":
    inputFilename = "grid_of_beams.json"
    outputFilename = "grid_of_beams.ifc"

    ca2ifc = CA2IFC(inputFilename, outputFilename)
    ca2ifc.convert()
