import os
import time
import json
import salome
import salome_notebook
import salome_version
from pprint import pprint

class MODEL(object):
    def __init__(self, filename, meshSize):
        self.filename = filename
        self.meshSize = meshSize
        self.tolLoc = 0
        self.mesh = None
        self.create(filename)

    def getGroupName(self, name):
        info = name.split('|')
        sortName = ''.join(c for c in info[0] if c.isupper())
        return str(sortName + '_' + info[1])

    def makePoint(self, pl):
        '''Function to define a Point from
            a polyline (list of 1 point)'''

        (x, y, z) = pl
        return self.geompy.MakeVertex(x, y, z)

    def makeLine(self, pl):
        '''Function to define a Line from
            a polyline (list of 2 points)'''

        (x, y, z) = pl[0]
        P1 = self.geompy.MakeVertex(x, y, z)
        (x, y, z) = pl[1]
        P2 = self.geompy.MakeVertex(x, y, z)

        return self.geompy.MakeLineTwoPnt(P1, P2)

    def makeFace(self, pl):
        '''Function to define a Face from
            a polyline (list of points)'''

        pointList = [None for _ in range(len(pl))]
        for ip, (x, y, z) in enumerate(pl):
            pointList[ip] = self.geompy.MakeVertex(x, y, z)

        LineList = [None for _ in range(len(pl))]
        for ip, P2 in enumerate(pointList):
            P1 = pointList[ip - 1]
            LineList[ip] = self.geompy.MakeLineTwoPnt(P1, P2)

        return self.geompy.MakeFaceWires(LineList, 1)

    def makeObject(self, geometry, geometryType):
        if geometryType == 'point':
            return self.makePoint(geometry)
        if geometryType == 'line':
            return self.makeLine(geometry)
        if geometryType == 'surface':
            return self.makeFace(geometry)

    def makePartition(self, objects, geometryType):
        if geometryType == 'point':
            shapeType = 'VERTEX'
        if geometryType == 'line':
            shapeType = 'EDGE'
        if geometryType == 'surface':
            shapeType = 'FACE'
        return self.geompy.MakePartition(objects, [], [], [], self.geompy.ShapeType[shapeType], 0, [], 1)

    def findIntersection(self, geometry, ecc):
        # TO DO: implement a more general procedure - understand better how it works
        if ecc['inX'] >= 0:
            return geometry[1]
        else:
            return geometry[0]
        # elemLength = self.length(geometry)
        # pLocal = [
        #     (ecc['pointOnElement'][0] - ecc['inX']) / elemLength,
        #     (ecc['pointOnElement'][1] - ecc['inY']) / elemLength,
        #     (ecc['pointOnElement'][2] - ecc['inZ']) / elemLength
        # ]
        # pLocalX = pLocal[0]
        #
        # if abs(pLocalX) < self.tolLoc*100:
        #     return geometry[0]
        # elif abs(pLocalX - 1) < self.tolLoc*100:
        #     return geometry[1]
        # elif pLocalX > 0 and pLocalX < 1:
        #     return [
        #         (1 - pLocalX) * geometry[0][0] + pLocalX * geometry[1][0],
        #         (1 - pLocalX) * geometry[0][1] + pLocalX * geometry[1][1],
        #         (1 - pLocalX) * geometry[0][2] + pLocalX * geometry[1][2]
        #     ]
        # else:
        #     pprint('Warning: Connection point not identified with a tight tolerance.')
        #     pprint('Tolerance needed is: %.2f' % max(abs(pLocalX), abs(pLocalX - 1)))
        #     tolMax = 0.1
        #     if abs(pLocalX) < tolMax:
        #         return geometry[0]
        #     elif abs(pLocalX - 1) < tolMax:
        #         return geometry[1]
        #     else:
        #         pprint('Error: Connection point not identified with a tolerance of 10%')

    def length(self, geometry):
        return ((
            (geometry[1][0] - geometry[0][0]) ** 2 + \
            (geometry[1][1] - geometry[0][1]) ** 2 + \
            (geometry[1][2] - geometry[0][2]) ** 2 \
            ) ** 0.5)

    def create(self, FILENAME):
        # Read data from input file
        with open(FILENAME) as dataFile:
            data = json.load(dataFile)

        elements = data['elements']
        connections = data['connections']

        meshSize = self.meshSize

        dec = 7  # 4 decimals for length in mm
        tol = 10**(-dec-3+1)

        self.tolLoc = tol*10*2
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

        gg = salome.ImportComponentGUI('GEOM')
        if NEW_SALOME:
            geompy = geomBuilder.New()
        else:
            geompy = geomBuilder.New(theStudy)
        self.geompy = geompy

        O = geompy.MakeVertex(0, 0, 0)
        OX = geompy.MakeVectorDXDYDZ(1, 0, 0)
        OY = geompy.MakeVectorDXDYDZ(0, 1, 0)
        OZ = geompy.MakeVectorDXDYDZ(0, 0, 1)
        geompy.addToStudy( O, 'O' )
        geompy.addToStudy( OX, 'OX' )
        geompy.addToStudy( OY, 'OY' )
        geompy.addToStudy( OZ, 'OZ' )

        if len([e for e in elements if e['geometryType'] == 'line']) > 0:
            buildingShapeType = 'EDGE'
        if len([e for e in elements if e['geometryType'] == 'surface']) > 0:
            buildingShapeType = 'FACE'

        ### Define entities ###
        start_time = time.time()
        pprint('Defining Object Geometry')
        init_time = start_time

        # Loop 1
        for el in elements:
            el['elemObj'] = self.makeObject(el['geometry'], str(el['geometryType']))

            el['connObjs'] = [None for _ in el['connections']]
            el['linkObjs'] = [None for _ in el['connections']]
            for j,rel in enumerate(el['connections']):
                conn = [c for c in connections if c['ifcName'] == rel['relatedConnection']][0]
                el['connObjs'][j] = self.makeObject(conn['geometry'], str(conn['geometryType']))
                if rel['eccentricity']:
                    pointOnElement = self.findIntersection(el['geometry'], rel['eccentricity'])
                    geometry = [pointOnElement, conn['geometry']]
                    el['linkObjs'][j] = self.makeObject(geometry, 'line')

            el['partObj'] = self.makePartition([el['elemObj']] + el['connObjs'] + [e for e in el['linkObjs'] if e], str(el['geometryType']))

            el['elemObj'] = geompy.GetInPlace(el['partObj'], el['elemObj'])
            for j,rel in enumerate(el['connections']):
                el['connObjs'][j] = geompy.GetInPlace(el['partObj'], el['connObjs'][j])
                if rel['eccentricity']:
                    el['linkObjs'][j] = geompy.GetInPlace(el['partObj'], el['linkObjs'][j])

        # for conn in connections:
        #     if conn['appliedCondition']:
        #         conn['connObj'] = self.makeObject(conn['geometry'], str(conn['geometryType']))

        # Make assemble of Building Object
        bldObjs = []
        bldObjs.extend([el['partObj'] for el in elements])
        # bldObjs.extend([conn['connObj'] for conn in connections if conn['appliedCondition']])

        bldComp = geompy.MakeCompound(bldObjs)
        geompy.addToStudy(bldComp, 'bldComp')

        # Loop 2
        for el in elements:
            # geompy.addToStudy(el['partObj'], self.getGroupName(str(el['ifcName'])))

            geompy.addToStudyInFather(el['partObj'], el['elemObj'], self.getGroupName(str(el['ifcName'])))
            for j,rel in enumerate(el['connections']):
                geompy.addToStudyInFather(el['partObj'], el['connObjs'][j], self.getGroupName(str(el['ifcName'])) + '_0D_to_' + self.getGroupName(str(rel['relatedConnection'])))
                if rel['eccentricity']:
                    geompy.addToStudyInFather(el['partObj'], el['linkObjs'][j], self.getGroupName(str(el['ifcName'])) + '_1D_to_' + self.getGroupName(str(rel['relatedConnection'])))

        # for conn in connections:
        #     if conn['appliedCondition']:
        #         # geompy.addToStudy(conn['connObj'], self.getGroupName(str(conn['ifcName'])))
        #         geompy.addToStudyInFather(conn['connObj'], conn['connObj'], self.getGroupName(str(conn['ifcName'])))

        elapsed_time = time.time() - init_time
        init_time += elapsed_time
        pprint('Building Geometry Defined in %g sec' % (elapsed_time))

        # Loop 3
        for el in elements:
            # el['partObj'] = geompy.RestoreGivenSubShapes(bldComp, [el['partObj']], GEOM.FSM_GetInPlace, False, False)[0]
            geompy.addToStudyInFather(bldComp, el['elemObj'], self.getGroupName(str(el['ifcName'])))

            for j,rel in enumerate(el['connections']):
                geompy.addToStudyInFather(bldComp, el['connObjs'][j], self.getGroupName(str(el['ifcName'])) + '_0D_to_' + self.getGroupName(str(rel['relatedConnection'])))
                if rel['eccentricity']:
                    el['linkObjs'][j].SetColor(SALOMEDS.Color(0, 0, 0))
                    geompy.addToStudyInFather(bldComp, el['linkObjs'][j], self.getGroupName(str(el['ifcName'])) + '_1D_to_' + self.getGroupName(str(rel['relatedConnection'])))

        # for conn in connections:
        #     if conn['appliedCondition']:
        #         # conn['connObj'] = geompy.RestoreGivenSubShapes(bldComp, [conn['connObj']], GEOM.FSM_GetInPlace, False, False)[0]
        #         geompy.addToStudyInFather(bldComp, conn['connObj'], self.getGroupName(str(conn['ifcName'])))

        elapsed_time = time.time() - init_time
        init_time += elapsed_time
        pprint('Building Geometry Groups Defined in %g sec' % (elapsed_time))

        ###
        ### SMESH component
        ###

        import SMESH
        from salome.smesh import smeshBuilder

        pprint('Defining Mesh Components')

        if NEW_SALOME:
            smesh = smeshBuilder.New()
        else:
            smesh = smeshBuilder.New(theStudy)
        Mesh_1 = smesh.Mesh(bldComp)
        Regular1D = Mesh_1.Segment()
        Local_Length_1 = Regular1D.LocalLength(meshSize, None, tolLoc)

        if buildingShapeType == 'FACE':
            NETGEN2D_ONLY = Mesh_1.Triangle(algo=smeshBuilder.NETGEN_2D)
            NETGEN2D_Pars = NETGEN2D_ONLY.Parameters()
            NETGEN2D_Pars.SetMaxSize(meshSize)
            NETGEN2D_Pars.SetOptimize(1)
            NETGEN2D_Pars.SetFineness(2)
            NETGEN2D_Pars.SetMinSize(meshSize/5.0)
            NETGEN2D_Pars.SetUseSurfaceCurvature(1)
            NETGEN2D_Pars.SetQuadAllowed(1)
            NETGEN2D_Pars.SetSecondOrder(0)
            NETGEN2D_Pars.SetFuseEdges(254)

        isDone = Mesh_1.Compute()

        ## Set names of Mesh objects
        smesh.SetName(Regular1D.GetAlgorithm(), 'Regular1D')
        smesh.SetName(Local_Length_1, 'Local_Length_1')

        if buildingShapeType == 'FACE':
            smesh.SetName(NETGEN2D_ONLY.GetAlgorithm(), 'NETGEN2D_ONLY')
            smesh.SetName(NETGEN2D_Pars, 'NETGEN2D_Pars')

        smesh.SetName(Mesh_1.GetMesh(), 'bldMesh')

        elapsed_time = time.time() - init_time
        init_time += elapsed_time
        pprint('Meshing Operations Completed in %g sec' % (elapsed_time))

        # Define groups in Mesh
        for el in elements:
            if el['geometryType'] == 'line':
                shapeType = SMESH.EDGE
            if el['geometryType'] == 'surface':
                shapeType = SMESH.FACE
            tempgroup = Mesh_1.GroupOnGeom(el['elemObj'], self.getGroupName(str(el['ifcName'])), shapeType)
            smesh.SetName(tempgroup, self.getGroupName(str(el['ifcName'])))

            for j,rel in enumerate(el['connections']):
                tempgroup = Mesh_1.GroupOnGeom(el['connObjs'][j], self.getGroupName(str(el['ifcName'])) + '_0D_to_' + self.getGroupName(str(rel['relatedConnection'])), SMESH.NODE)
                smesh.SetName(tempgroup, self.getGroupName(str(el['ifcName'])) + '_0D_to_' + self.getGroupName(str(rel['relatedConnection'])))
                if rel['eccentricity']:
                    tempgroup = Mesh_1.GroupOnGeom(el['linkObjs'][j], self.getGroupName(str(el['ifcName'])) + '_1D_to_' + self.getGroupName(str(rel['relatedConnection'])), SMESH.EDGE)
                    smesh.SetName(tempgroup, self.getGroupName(str(el['ifcName'])) + '_1D_to_' + self.getGroupName(str(rel['relatedConnection'])))

        # for conn in connections:
        #     if conn['appliedCondition']:
        #         tempgroup = Mesh_1.GroupOnGeom(conn['connObj'], self.getGroupName(str(conn['ifcName'])), SMESH.NODE)
        #         smesh.SetName(tempgroup, self.getGroupName(str(conn['ifcName'])))

        self.mesh = Mesh_1

        elapsed_time = time.time() - init_time
        init_time += elapsed_time
        pprint('Mesh Groups Defined in %g sec' % (elapsed_time))

        if salome.sg.hasDesktop():
            if NEW_SALOME:
                salome.sg.updateObjBrowser()
            else:
                salome.sg.updateObjBrowser(1)


        elapsed_time = init_time - start_time
        pprint('ALL Operations Completed in %g sec' % (elapsed_time))

if __name__ == '__main__':
    fileNames = ['cantilever_01', 'beam_01', 'portal_01', 'building_01', 'building-frame_01'];
    files = [fileNames[3]]
    meshSize = 200

    for fileName in files:
        # BASE_PATH = os.path.dirname(os.path.realpath('__file__'))
        BASE_PATH = '/home/jesusbill/Dev-Projects/github.com/Jesusbill/ifc2ca'
        FILENAME = BASE_PATH + '/examples/' + fileName + '/' + fileName + '.json'
        FILENAMEMED = BASE_PATH + '/examples/' + fileName + '/bldMesh.med'
        model = MODEL(FILENAME, meshSize)
