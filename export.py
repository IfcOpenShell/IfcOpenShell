import ifcopenshell
import bpy

class IfcExporter():
    def __init__(self):
        self.template_file = '/home/dion/Projects/blender-bim-ifc/template.ifc'
        self.output_file = '/home/dion/Projects/blender-bim-ifc/output.ifc'

    def export(self):
        self.file = ifcopenshell.open(self.template_file)
        self.set_common_definitions()
        self.create_context()
        self.create_project()
        self.create_building()
        self.create_building_storey()
        self.create_products()
        self.file.write(self.output_file)

    def set_common_definitions(self):
        self.origin = self.file.by_type("IfcAxis2Placement3D")[0]
        # Owner history doesn't actually work like this, but for now, it does :)
        self.owner_history = self.file.by_type("ifcownerhistory")[0]

    def create_context(self):
        self.ifc_context = self.file.createIfcGeometricRepresentationContext(
            None, "Model",
            3, 1.0E-05,
            self.origin,
            self.file.createIfcDirection((0., 1., 0.)))

        self.ifc_subcontext = self.file.createIfcGeometricRepresentationSubContext(
            "Body", "Model",
            None, None, None, None,
            self.ifc_context, None, "MODEL_VIEW", None)

    def create_project(self):
        self.project = self.file.createIfcProject(
            ifcopenshell.guid.new(),
            self.owner_history,
            'Name', None,
            None, None, None, [self.ifc_context],
            self.file.by_type("IfcUnitAssignment")[0])

    def create_building(self):
        self.ifc_building_placement = self.file.createIfcLocalPlacement(None, self.origin)
        self.ifc_building = self.file.createIfcBuilding(
            ifcopenshell.guid.new(),
            self.owner_history, 'My building', None, None,
            self.ifc_building_placement,
            None, None, 'ELEMENT', None, None, None)
        self.file.createIfcRelAggregates(
            ifcopenshell.guid.new(),
            self.owner_history, None, None, self.project, [self.ifc_building])

    def create_building_storey(self):
        self.ifc_building_storey_placement = self.file.createIfcLocalPlacement(self.ifc_building_placement, self.origin)
        self.ifc_building_storey = self.file.createIfcBuildingStorey(
            ifcopenshell.guid.new(),
            self.owner_history, 'Ground floor', None, None,
            self.ifc_building_storey_placement, None, None, 'ELEMENT', None)
        self.file.createIfcRelAggregates(
            ifcopenshell.guid.new(),
            self.owner_history, None, None, self.ifc_building, [self.ifc_building_storey])

    def create_products(self):
        ifc_products = []

        for object in bpy.context.selected_objects:
            ifc_vertices = []
            ifc_faces = []
            for vertice in object.data.vertices:
                ifc_vertices.append(
                    self.file.createIfcCartesianPoint((vertice.co.x, vertice.co.y, vertice.co.z)))
            for polygon in object.data.polygons:
                ifc_faces.append(self.file.createIfcFace([
                    self.file.createIfcFaceOuterBound(
                        self.file.createIfcPolyLoop([ifc_vertices[vertice] for vertice in polygon.vertices]),
                        True)]))
                        
            representation = self.file.createIfcProductDefinitionShape(None, None,
                [self.file.createIfcShapeRepresentation(
                    self.ifc_subcontext, 'Body', 'Brep',
                    [self.file.createIfcFacetedBrep(self.file.createIfcClosedShell(ifc_faces))])])
                    
            placement = self.file.createIfcLocalPlacement(self.ifc_building_storey_placement,
                self.file.createIfcAxis2Placement3D(
                    self.file.createIfcCartesianPoint(
                        (object.location.x, object.location.y, object.location.z))))
                        
            ifc_products.append(self.file.createIfcBuildingElementProxy(
                ifcopenshell.guid.new(),
                self.owner_history, object.name, None, None, placement, representation, None, None))

        self.file.createIfcRelContainedInSpatialStructure(
            ifcopenshell.guid.new(), self.owner_history, None, None, ifc_products, self.ifc_building_storey)

ifc_exporter = IfcExporter()
ifc_exporter.export()
