import ifcopenshell
import bpy

template_file = '/home/dion/Projects/blender-bim-ifc/template.ifc'
output_file = '/home/dion/Projects/blender-bim-ifc/output.ifc'
f = ifcopenshell.open(template_file)

origin = f.by_type("IfcAxis2Placement3D")[0]
owner_history = f.by_type("ifcownerhistory")[0]

context = f.createIfcGeometricRepresentationContext(
    None, "Model",
    3, 1.0E-05,
    origin,
    f.createIfcDirection((0., 1., 0.)))

subcontext = f.createIfcGeometricRepresentationSubContext(
    "Body", "Model",
    None, None, None, None,
    context, None, "MODEL_VIEW", None)

project = f.createIfcProject(
    ifcopenshell.guid.new(),
    owner_history,
    'Name', None,
    None, None, None, [context],
    f.by_type("IfcUnitAssignment")[0])

building_placement = f.createIfcLocalPlacement(None, origin)

building = f.createIfcBuilding(
    ifcopenshell.guid.new(),
    owner_history, 'My building', None, None,
    building_placement,
    None, None, 'ELEMENT', None, None, None)
    
building_storey_placement = f.createIfcLocalPlacement(building_placement, origin)

building_storey = f.createIfcBuildingStorey(
    ifcopenshell.guid.new(),
    owner_history, 'Ground floor', None, None,
    building_storey_placement, None, None, 'ELEMENT', None)
    
f.createIfcRelAggregates(
    ifcopenshell.guid.new(),
    owner_history, None, None, building, [building_storey])
    
f.createIfcRelAggregates(
    ifcopenshell.guid.new(),
    owner_history, None, None, project, [building])

ifc_products = []

for object in bpy.context.selected_objects:
    ifc_vertices = []
    ifc_faces = []
    for vertice in object.data.vertices:
        ifc_vertices.append(
            f.createIfcCartesianPoint((vertice.co.x, vertice.co.y, vertice.co.z)))
    for polygon in object.data.polygons:
        ifc_faces.append(f.createIfcFace([
            f.createIfcFaceOuterBound(
                f.createIfcPolyLoop([ifc_vertices[vertice] for vertice in polygon.vertices]),
                True)]))
                
    representation = f.createIfcProductDefinitionShape(None, None,
        [f.createIfcShapeRepresentation(
            subcontext, 'Body', 'Brep',
            [f.createIfcFacetedBrep(f.createIfcClosedShell(ifc_faces))])])
            
    placement = f.createIfcLocalPlacement(building_storey_placement,
        f.createIfcAxis2Placement3D(
            f.createIfcCartesianPoint(
                (object.location.x, object.location.y, object.location.z))))
                
    ifc_products.append(f.createIfcBuildingElementProxy(
        ifcopenshell.guid.new(),
        owner_history, object.name, None, None, placement, representation, None, None))
        
f.createIfcRelContainedInSpatialStructure(
    ifcopenshell.guid.new(), owner_history, None, None, ifc_products, building_storey)

f.write(output_file)