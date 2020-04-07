import json
import ifcopenshell

class IFC2CA:
    def __init__(self, filename):
        self.filename = filename
        self.file = None
        self.result = {}

    def convert(self):
        self.file = ifcopenshell.open(self.filename)
        for model in self.file.by_type('IfcStructuralAnalysisModel'):
            self.result = {
                'ifcName': model.is_a() + '|' + str(model.id()),
                'name': model.Name,
                'id': model.GlobalId,
                'elements': self.get_structural_items(model, item_type='IfcStructuralMember'),
                'connections': self.get_structural_items(model, item_type='IfcStructuralConnection')
            }

            print('Number of elements: ', len(self.result['elements']))
            print('Number of connections: ', len(self.result['connections']))

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
        if item.is_a('IfcStructuralCurveMember'):
            representation = self.get_representation(item, 'Edge')
            material_profile = self.get_material_profile(item)
            if not representation or not material_profile:
                print(representation, material_profile)
                return

            return {
                'ifcName': item.is_a() + '|' + str(item.id()),
                'name': item.Name,
                'id': item.GlobalId,
                'geometryType': 'line',
                'predefinedType': item.PredefinedType,
                'geometry': self.get_geometry(representation),
                'material': self.get_material_properties(material_profile.Material),
                'profile': self.get_profile_properties(material_profile.Profile),
                'connections': self.get_connection_data(item.ConnectedBy)
            }

        elif item.is_a('IfcStructuralSurfaceMember'):
            representation = self.get_representation(item, 'Face')
            material = self.get_material_profile(item)
            if not representation:
                print(representation)
                return

            return {
                'ifcName': item.is_a() + '|' + str(item.id()),
                'name': item.Name,
                'id': item.GlobalId,
                'geometryType': 'surface',
                'predefinedType': item.PredefinedType,
                'thickness': item.Thickness,
                'geometry': self.get_geometry(representation),
                'material': self.get_material_properties(material),
                'connections': self.get_connection_data(item.ConnectedBy)
            }

        elif item.is_a('IfcStructuralPointConnection'):
            representation = self.get_representation(item, 'Vertex')
            if not representation:
                print(representation)
                return

            return {
                'ifcName': item.is_a() + '|' + str(item.id()),
                'name': item.Name,
                'id': item.GlobalId,
                'geometryType': 'point',
                'geometry': self.get_geometry(representation),
                'appliedCondition': self.get_connection_input(item),
                'relatedElements': self.get_connection_data(item.ConnectsStructuralMembers)
            }

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
            return point.Coordinates

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
            'eccentricity': None if not rel.is_a('IfcRelConnectsWithEccentricity') else {
                    'inX': 0.0 if not rel.ConnectionConstraint.EccentricityInX else rel.ConnectionConstraint.EccentricityInX,
                    'inY': 0.0 if not rel.ConnectionConstraint.EccentricityInY else rel.ConnectionConstraint.EccentricityInY,
                    'inZ': 0.0 if not rel.ConnectionConstraint.EccentricityInZ else rel.ConnectionConstraint.EccentricityInZ,
                    'pointOnElement': self.get_coordinate(rel.ConnectionConstraint.PointOnRelatingElement)
                }
            # 'geometryPointIndex': None
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
    IFC_FILENAME = ''
    ifc2ca = IFC2CA(IFC_FILENAME)
    ifc2ca.convert()
    print(json.dumps(ifc2ca.result, indent=4))
