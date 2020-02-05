import json
import ifcopenshell

class IFC2CA:
    def __init__(self, filename):
        self.filename = filename
        self.file = None
        self.result = {}
        self.supports = []

    def convert(self):
        self.file = ifcopenshell.open(self.filename)
        for model in self.file.by_type('IfcStructuralAnalysisModel'):
            self.result = {
                'title': model.Name,
                'units': self.get_units(),
                'elements': self.get_elements(model),
                'mesh': { 'meshSize': 0.2 }, # TODO: unhardcode
                'supports': self.get_supports()
            }

    def get_units(self):
        # TODO: unhardcode
        units = {}
        for unit in self.file.by_type('IfcUnitAssignment')[0].Units:
            if unit.UnitType == 'LENGTHUNIT':
                units['length'] = 'm'
        units['force'] = 'N'
        units['angle'] = 'deg'
        return units

    def get_elements(self, model):
        elements = []
        for group in model.IsGroupedBy:
            for element in group.RelatedObjects:
                if not element.is_a('IfcStructuralMember'):
                    continue
                data = self.get_element_data(element)
                if data:
                    elements.append(data)
        return elements

    def get_element_data(self, element):
        representation = self.get_representation(element)
        material_profile = self.get_material_profile(element)
        if not representation or not material_profile:
            return
        for connection in element.ConnectedBy:
            if connection.RelatedStructuralConnection.AppliedCondition:
                self.supports.append(connection.RelatedStructuralConnection)
        return {
            'ifcName': element.is_a() + '|' + str(element.id()),
            'name': element.Name,
            'id': element.GlobalId,
            'geometryType': self.get_geometry_type(representation),
            'geometry': self.get_geometry(representation),
            'rotation': 0, # TODO: unhardcode
            'material': self.get_material_properties(material_profile),
            'section': self.get_material_section(material_profile),
            'elementType': 'EulerBeam' # TODO: unhardcode
        }

    def get_supports(self):
        supports = []
        for support in self.supports:
            supports.append({
                'ifcName': support.is_a() + '|' + str(support.id()),
                'name': support.Name,
                'id': support.GlobalId,
                'geometryType': self.get_support_geometry_type(support),
                'geometry': self.get_support_geometry(support),
                'appliedCondition': self.get_support_input(support)
            })
        return supports

    def get_support_geometry_type(self, support):
        if support.is_a('IfcStructuralPointConnection'):
            return 'point'

    def get_support_geometry(self, support):
        # TODO: make more robust
        return support.ObjectPlacement.RelativePlacement.Location.Coordinates

    def get_support_input(self, support):
        return {
            'dx': support.AppliedCondition.TranslationalStiffnessX.wrappedValue,
            'dy': support.AppliedCondition.TranslationalStiffnessY.wrappedValue,
            'dz': support.AppliedCondition.TranslationalStiffnessZ.wrappedValue,
            'drx': support.AppliedCondition.RotationalStiffnessX.wrappedValue,
            'dry': support.AppliedCondition.RotationalStiffnessY.wrappedValue,
            'drz': support.AppliedCondition.RotationalStiffnessZ.wrappedValue
        }
        print(support.AppliedCondition)

    def get_representation(self, element):
        if not element.Representation:
            return None
        for representation in element.Representation.Representations:
            rep = self.get_specific_representation(representation, 'Reference', 'Edge')
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

    def get_geometry_type(self, representation):
        if representation.Items[0].is_a('IfcEdgeCurve'):
            return 'curvedLine' # TODO: Is this correct?
        return 'straightLine'

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

    def get_material_properties(self, profile):
        psets = profile.Material.HasProperties
        return {
            'ifcName': profile.Material.is_a() + '|' + str(profile.Material.id()),
            'materialType': 'isotropic', # TODO: unhardcode
            'youngModulus': self.get_pset_property(psets, 'Pset_MaterialMechanical', 'YoungModulus'),
            'poissonRatio': self.get_pset_property(psets, 'Pset_MaterialMechanical', 'PoissonRatio'),
            'massDensity': self.get_pset_property(psets, 'Pset_MaterialCommon', 'MassDensity')
        }

    def get_pset_property(self, psets, pset_name, prop_name):
        for pset in psets:
            if pset.Name == pset_name:
                for prop in pset.Properties:
                    if prop.Name == prop_name:
                        return prop.NominalValue.wrappedValue

    def get_material_section(self, profile):
        if profile.Profile.is_a('IfcRectangleProfileDef'):
            return {
                'ifcName': profile.Profile.is_a() + '|' + str(profile.Profile.id()),
                'sectionType': 'rectangular',
                'sectionVariation': 'constant',
                'xDim': profile.Profile.XDim,
                'yDim': profile.Profile.YDim
            }

ifc2ca = IFC2CA('ifc2ca.blend.ifc')
ifc2ca.convert()
print(json.dumps(ifc2ca.result, indent=4))
