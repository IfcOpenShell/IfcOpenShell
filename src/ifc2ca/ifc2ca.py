import json
import ifcopenshell
import numpy as np

class IFC2CA:
    def __init__(self, filename):
        self.filename = filename
        self.file = None
        self.result = {}
        self.warnings = []

    def convert(self):
        self.file = ifcopenshell.open(self.filename)
        for model in self.file.by_type('IfcStructuralAnalysisModel'):
            elements = self.get_structural_items(model, item_type='IfcStructuralMember')
            connections = self.get_structural_items(model, item_type='IfcStructuralConnection')

            materialdb = []
            materials = list(dict.fromkeys([e['material'] for e in elements]))
            for mat in materials:
                id = int(mat.split('|')[1])
                material = self.get_material_properties(self.file.by_id(id))
                material['relatedElements'] = [e['ifcName'] for e in elements if 'material' in e and e['material'] == mat]
                materialdb.append(material)

            profiledb = []
            profiles = list(dict.fromkeys([e['profile'] for e in elements if 'profile' in e]))
            for prof in profiles:
                id = int(prof.split('|')[1])
                profile = self.get_profile_properties(self.file.by_id(id))
                profile['relatedElements'] = [e['ifcName'] for e in elements if 'profile' in e and e['profile'] == prof]
                profiledb.append(profile)

            self.result = {
                'ifcName': model.is_a() + '|' + str(model.id()),
                'name': model.Name,
                'id': model.GlobalId,
                'elements': elements,
                'connections': connections,
                'db': {
                    'materials': materialdb,
                    'profiles': profiledb
                },
                'warnings': self.warnings
            }

            print('Model %s converted' % model.Name)
            print('Number of elements: ', len(elements))
            print('Number of connections: ', len(connections))
            print('Number of materials: ', len(materialdb))
            print('Number of profiles: ', len(profiledb))
            print('')

            break

    def get_structural_items(self, model, item_type='IfcStructuralItem'):
        items = []
        for group in model.IsGroupedBy:
            for item in group.RelatedObjects:
                if not item.is_a(item_type):
                    continue
                data = self.get_item_data(item)
                if data:
                    items.append(data)
        return items

    def get_item_data(self, item):
        transformation = self.get_transformation(item.ObjectPlacement)

        if item.is_a('IfcStructuralCurveMember'):
            representation = self.get_representation(item, 'Edge')
            material_profile = self.get_material_profile(item)
            if not representation or not material_profile:
                print(representation, material_profile)
                return

            material = material_profile.Material
            profile = material_profile.Profile
            geometry = self.get_geometry(representation)
            orientation = self.get_1D_orientation(geometry, item.Axis)
            connections = self.get_connection_data(item.ConnectedBy)
            for conn in connections:
                if not conn['orientation']:
                    conn['orientation'] = orientation
            # --> Correct pointOnElement for eccentricity connection for ETABS files
            length = np.linalg.norm(np.array(geometry[1]) - np.array(geometry[0]))
            for c in connections:
                if c['eccentricity']:
                    if np.linalg.norm(np.array(c['eccentricity']['pointOnElement'])) > length:
                        # print('Eccentricity in %s corrected' % item.is_a() + '|' + str(item.id()))
                        self.warnings.append('Eccentricity in %s corrected' % (item.is_a() + '|' + str(item.id())))
                        c['eccentricity']['pointOnElement'][0] = length
            # End <--
            if transformation:
                geometry = self.transform_vectors(geometry, transformation)
                orientation = self.transform_vectors(orientation, transformation, include_translation=False)
                for c in connections:
                    c['orientation'] = self.transform_vectors(c['orientation'], transformation, include_translation=False)
                    if c['eccentricity']:
                        c['eccentricity']['vector'] = self.transform_vectors(c['eccentricity']['vector'], transformation, include_translation=False)

            return {
                'ifcName': item.is_a() + '|' + str(item.id()),
                'name': item.Name,
                'id': item.GlobalId,
                'geometryType': 'line',
                'predefinedType': item.PredefinedType,
                'geometry': geometry,
                'orientation': orientation,
                'material': material.is_a() + '|' + str(material.id()),
                'profile': profile.is_a() + '|' + str(profile.id()),
                'connections': connections
            }

        elif item.is_a('IfcStructuralSurfaceMember'):
            representation = self.get_representation(item, 'Face')
            material = self.get_material_profile(item)
            if not representation:
                print(representation)
                return

            geometry = self.get_geometry(representation)
            orientation = self.get_2D_orientation(representation)
            connections = self.get_connection_data(item.ConnectedBy)
            for conn in connections:
                if not conn['orientation']:
                    conn['orientation'] = orientation
            if transformation:
                geometry = self.transform_vectors(geometry, transformation)
                orientation = self.transform_vectors(orientation, transformation, include_translation=False)
                for c in connections:
                    c['orientation'] = self.transform_vectors(c['orientation'], transformation, include_translation=False)

            return {
                'ifcName': item.is_a() + '|' + str(item.id()),
                'name': item.Name,
                'id': item.GlobalId,
                'geometryType': 'surface',
                'predefinedType': item.PredefinedType,
                'thickness': item.Thickness,
                'geometry': geometry,
                'orientation': orientation,
                'material': material.is_a() + '|' + str(material.id()),
                'connections': connections
            }

        elif item.is_a('IfcStructuralPointConnection'):
            representation = self.get_representation(item, 'Vertex')
            if not representation:
                print(representation)
                return

            geometry = self.get_geometry(representation)
            orientation = self.get_0D_orientation(item.ConditionCoordinateSystem)
            if not orientation:
                orientation = np.eye(3).tolist()
            if transformation:
                geometry = self.transform_vectors(geometry, transformation)
                orientation = self.transform_vectors(orientation, transformation, include_translation=False)

            return {
                'ifcName': item.is_a() + '|' + str(item.id()),
                'name': item.Name,
                'id': item.GlobalId,
                'geometryType': 'point',
                'geometry': geometry,
                'orientation': orientation,
                'appliedCondition': self.get_connection_input(item),
                'relatedElements': [con.is_a() + '|' + str(con.id()) for con in item.ConnectsStructuralMembers]
            }

    def get_transformation(self, placement):
        if not placement:
            return None
        if placement.is_a('IfcLocalPlacement'):
            if placement.PlacementRelTo:
                print('Warning! Object Placement with PlacementRelTo attribute is not supported and will be neglected')
            axes = placement.RelativePlacement
            location = np.array(self.get_coordinate(axes.Location))
            if axes.Axis and axes.RefDirection:
                xAxis = np.array(axes.RefDirection.DirectionRatios) # this can be not accurate (in the xz plane)
                zAxis = np.array(axes.Axis.DirectionRatios)
                zAxis /= np.linalg.norm(zAxis)
                yAxis = np.cross(zAxis, xAxis)
                yAxis /= np.linalg.norm(yAxis)
                xAxis = np.cross(yAxis, zAxis)
                xAxis /= np.linalg.norm(xAxis)
            else:
                if np.allclose(location, np.array([0., 0., 0.])):
                    return None
                xAxis = np.array([1., 0., 0.])
                yAxis = np.array([0., 1., 0.])
                zAxis = np.array([0., 0., 1.])
            if (np.allclose(location, np.array([0., 0., 0.])) and
                np.allclose(xAxis, np.array([1., 0., 0.])) and
                np.allclose(yAxis, np.array([0., 1., 0.])) and
                np.allclose(zAxis, np.array([0., 0., 1.]))):
                return None
            return {
                'location': location,
                'rotationMatrix': np.array([xAxis, yAxis, zAxis]).transpose()
            }
        else:
            print('Warning! Object Placement is of type %s, which is not supported. Default considered' % placement.is_a())
            return None

    def get_representation(self, element, rep_type):
        if not element.Representation:
            return None
        for representation in element.Representation.Representations:
            rep = self.get_specific_representation(representation, 'Reference', rep_type)
            if rep:
                return rep
        else:
            # print('Trying without rep identifier')
            for representation in element.Representation.Representations:
                rep = self.get_specific_representation(representation, None, rep_type)
                if rep:
                    return rep

    def get_specific_representation(self, representation, rep_id, rep_type):
        if representation.RepresentationIdentifier == rep_id \
                and representation.RepresentationType == rep_type:
            return representation
        if representation.RepresentationType == 'MappedRepresentation':
            return self.get_specific_representation(
                representation.Items[0].MappingSource.MappedRepresentation,
                rep_id, rep_type)

    def get_geometry(self, representation):
        # Maybe IfcOpenShell can use create_shape here to simplify this, but
        # supposedly structural models are very simple anyway, so perhaps we
        # can do without it.
        item = representation.Items[0]
        if item.is_a('IfcEdge'):
            return [
                self.get_coordinate(item.EdgeStart.VertexGeometry),
                self.get_coordinate(item.EdgeEnd.VertexGeometry)
            ]

        elif item.is_a('IfcFaceSurface'):
            edges = item.Bounds[0].Bound.EdgeList
            coords = []
            for edge in edges:
                coords.append(self.get_coordinate(edge.EdgeElement.EdgeStart.VertexGeometry))
            return coords

        elif item.is_a('IfcVertexPoint'):
            return self.get_coordinate(item.VertexGeometry)

    def get_coordinate(self, point):
        if point.is_a('IfcCartesianPoint'):
            return list(point.Coordinates)

    def get_0D_orientation(self, axes):
        if axes and axes.Axis and axes.RefDirection:
            xAxis = np.array(axes.RefDirection.DirectionRatios) # this can be not strictly perpendicular (in the xz plane)
            zAxis = np.array(axes.Axis.DirectionRatios)
            zAxis /= np.linalg.norm(zAxis)
            yAxis = np.cross(zAxis, xAxis)
            yAxis /= np.linalg.norm(yAxis)
            xAxis = np.cross(yAxis, zAxis)
            xAxis /= np.linalg.norm(xAxis)

            return [xAxis.tolist(), yAxis.tolist(), zAxis.tolist()]
        else: # return None and copy the elements orientation
            return None

    def get_1D_orientation(self, geometry, zAxis):
        xAxis = np.array(geometry[1]) - np.array(geometry[0])
        xAxis /= np.linalg.norm(xAxis)
        zAxis = np.array(zAxis.DirectionRatios) # this can be not strictly perpendicular (in the xz plane)
        yAxis = np.cross(zAxis, xAxis)
        yAxis /= np.linalg.norm(yAxis)
        zAxis = np.cross(xAxis, yAxis)
        zAxis /= np.linalg.norm(zAxis)

        return [xAxis.tolist(), yAxis.tolist(), zAxis.tolist()]

    def get_2D_orientation(self, representation):
        item = representation.Items[0]
        if item.is_a('IfcFaceSurface'):
            item.SameSense
            axes = item.FaceSurface.Position
            orientation = self.get_0D_orientation(axes)
            if not item.SameSense:
                orientation = [[-v for v in vec] for vec in orientation]
            return orientation

    def transform_vectors(self, geometry, trsf, include_translation=True):
        if not any(isinstance(el, list) for el in geometry): # single point which contains no list
            geometry = [geometry]
        globalGeometry = []

        for p in geometry:
            gp = trsf['rotationMatrix'].dot(np.array(p))
            if include_translation:
                gp += trsf['location']
            globalGeometry.append(gp.tolist())

        if len(globalGeometry) == 1: # single point
            globalGeometry = globalGeometry[0]

        return globalGeometry

    def get_material_profile(self, element):
        if not element.HasAssociations:
            return None
        for association in element.HasAssociations:
            if not association.is_a('IfcRelAssociatesMaterial'):
                continue
            material = association.RelatingMaterial
            if material.is_a('IfcMaterialProfileSet'):
                # For now, we only deal with a single profile
                return material.MaterialProfiles[0]
            if material.is_a('IfcMaterialProfileSetUsage'):
                return material.ForProfileSet.MaterialProfiles[0]
            if material.is_a('IfcMaterial'):
                return material

    def get_material_properties(self, material):
        psets = material.HasProperties

        if self.get_pset_properties(psets, 'Pset_MaterialMechanical'):
            mechProps = self.get_pset_properties(psets, 'Pset_MaterialMechanical')
        else:
            mechProps = self.get_pset_properties(psets, None)

        if self.get_pset_properties(psets, 'Pset_MaterialCommon'):
            commonProps = self.get_pset_properties(psets, 'Pset_MaterialCommon')
        else:
            commonProps = self.get_pset_properties(psets, None)

        return {
            'ifcName': material.is_a() + '|' + str(material.id()),
            'name': material.Name,
            'mechProps': mechProps,
            'commonProps':commonProps
        }

    def get_pset_property(self, psets, pset_name, prop_name):
        for pset in psets:
            if pset.Name == pset_name or pset_name is None:
                for prop in pset.Properties:
                    if prop.Name == prop_name:
                        return prop.NominalValue.wrappedValue

    def get_pset_properties(self, psets, pset_name):
        for pset in psets:
            if pset.Name == pset_name or pset_name is None:
                d = {}
                for prop in pset.Properties:
                    propName = prop.Name[0].lower() + prop.Name[1:]
                    d[propName] = prop.NominalValue.wrappedValue
                return d

    def get_profile_properties(self, profile):
        if profile.is_a('IfcRectangleProfileDef'):
            return {
                'ifcName': profile.is_a() + '|' + str(profile.id()),
                'profileName': profile.ProfileName,
                'profileType': profile.ProfileType,
                'profileShape': 'rectangular',
                'xDim': profile.XDim,
                'yDim': profile.YDim
            }

        if profile.is_a('IfcIShapeProfileDef'):
            psets = profile.HasProperties

            if self.get_pset_properties(psets, 'Pset_ProfileMechanical'):
                mechProps = self.get_pset_properties(psets, 'Pset_ProfileMechanical')
            else:
                mechProps = self.get_i_section_properties(profile, 'iSymmetrical')

            return {
                'ifcName': profile.is_a() + '|' + str(profile.id()),
                'profileName': profile.ProfileName,
                'profileType': profile.ProfileType,
                'profileShape': 'iSymmetrical',
                'mechProps': mechProps,
                'commonProps': {
                    'flangeThickness': profile.FlangeThickness,
                    'webThickness': profile.WebThickness,
                    'overallDepth': profile.OverallDepth,
                    'overallWidth': profile.OverallWidth,
                    'filletRadius': profile.FilletRadius,
                }
            }

    def get_connection_data(self, itemList):
        return [{
            'ifcName': rel.is_a() + '|' + str(rel.id()),
            'id': rel.GlobalId,
            'relatingElement': rel.RelatingStructuralMember.is_a() + '|' + str(rel.RelatingStructuralMember.id()),
            'relatedConnection': rel.RelatedStructuralConnection.is_a() + '|' + str(rel.RelatedStructuralConnection.id()),
            'orientation': self.get_0D_orientation(rel.ConditionCoordinateSystem),
            'appliedCondition': self.get_connection_input(rel),
            'eccentricity': None if not rel.is_a('IfcRelConnectsWithEccentricity') else {
                    'vector': [
                        0.0 if not rel.ConnectionConstraint.EccentricityInX else rel.ConnectionConstraint.EccentricityInX,
                        0.0 if not rel.ConnectionConstraint.EccentricityInY else rel.ConnectionConstraint.EccentricityInY,
                        0.0 if not rel.ConnectionConstraint.EccentricityInZ else rel.ConnectionConstraint.EccentricityInZ
                    ],
                    'pointOnElement': self.get_coordinate(rel.ConnectionConstraint.PointOnRelatingElement)
                }
        } for rel in itemList]

    def get_connection_input(self, connection):
        if connection.AppliedCondition:
            return {
                'dx': connection.AppliedCondition.TranslationalStiffnessX.wrappedValue,
                'dy': connection.AppliedCondition.TranslationalStiffnessY.wrappedValue,
                'dz': connection.AppliedCondition.TranslationalStiffnessZ.wrappedValue,
                'drx': connection.AppliedCondition.RotationalStiffnessX.wrappedValue,
                'dry': connection.AppliedCondition.RotationalStiffnessY.wrappedValue,
                'drz': connection.AppliedCondition.RotationalStiffnessZ.wrappedValue
            }
        return connection.AppliedCondition

    def get_i_section_properties(self, profile, profileShape):
        if profileShape == 'iSymmetrical':
            tf = profile.FlangeThickness
            tw = profile.WebThickness
            h = profile.OverallDepth
            b = profile.OverallWidth

            A = b * h - (b - tw) * (h - 2 * tf)
            Iy = b * (h ** 3) / 12 - (b - tw) * ((h - 2 * tf) ** 3) / 12
            Iz = (2 * tf) * (b ** 3) / 12 + (h - 2 * tf) * (tw ** 3) / 12
            Jx = 1 / 3 * ((h - tf) * (tw ** 3) + 2 * b * (tf ** 3))

            return {
                'crossSectionArea': A,
                'momentOfInertiaY': Iy,
                'momentOfInertiaZ': Iz,
                'torsionalConstantX': Jx
            }

if __name__ == '__main__':
    fileNames = ['cantilever_01', 'portal_01']
    files = fileNames

    for fileName in files:
        BASE_PATH = '/home/jesusbill/Dev-Projects/github.com/IfcOpenShell/analysis-models/ifcFiles/'
        ifc2ca = IFC2CA(BASE_PATH + fileName + '.ifc')
        ifc2ca.convert()
        with open(BASE_PATH + fileName + '.json', 'w') as f:
            f.write(json.dumps(ifc2ca.result, indent = 4))
