/********************************************************************************
 *                                                                              *
 * This file is part of IfcOpenShell.                                           *
 *                                                                              *
 * IfcOpenShell is free software: you can redistribute it and/or modify         *
 * it under the terms of the Lesser GNU General Public License as published by  *
 * the Free Software Foundation, either version 3.0 of the License, or          *
 * (at your option) any later version.                                          *
 *                                                                              *
 * IfcOpenShell is distributed in the hope that it will be useful,              *
 * but WITHOUT ANY WARRANTY; without even the implied warranty of               *
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the                 *
 * Lesser GNU General Public License for more details.                          *
 *                                                                              *
 * You should have received a copy of the Lesser GNU General Public License     *
 * along with this program. If not, see <http://www.gnu.org/licenses/>.         *
 *                                                                              *
 ********************************************************************************/

#include <string>
#include <iostream>
#include <fstream>

#include <TColgp_Array2OfPnt.hxx>
#include <TColgp_Array1OfPnt.hxx>
#include <TColStd_Array1OfReal.hxx>
#include <TColStd_Array1OfInteger.hxx>

#include <Geom_BSplineSurface.hxx>
#include <BRepBuilderAPI_MakeFace.hxx>

#include "../ifcparse/Ifc2x3.h"
#include "../ifcparse/IfcUtil.h"
#include "../ifcparse/IfcHierarchyHelper.h"
#include "../ifcgeom/IfcGeom.h"

// Some convenience typedefs and definitions. 
typedef std::string S;
typedef IfcWrite::IfcGuidHelper guid;
typedef std::pair<double, double> XY;
boost::none_t const null = (static_cast<boost::none_t>(0));

// The creation of Nurbs-surface for the IfcSite mesh, to be implemented lateron
void createGroundShape(TopoDS_Shape& shape);

int main(int argc, char** argv) {

	// The IfcHierarchyHelper is a subclass of the regular IfcFile that provides several
	// convenience functions for working with geometry in IFC files.
	IfcHierarchyHelper file;

	// Start by adding a wall to the file, initially leaving most attributes blank.
	Ifc2x3::IfcWallStandardCase* south_wall = new Ifc2x3::IfcWallStandardCase(
		guid(), 			// GlobalId
		0, 					// OwnerHistory
		S("South wall"), 	// Name
		null, 				// Description
		null, 				// ObjectType
		0, 					// ObjectPlacement
		0, 					// Representation
		null				// Tag
	);
	file.addBuildingProduct(south_wall);

	// By adding a wall, a hierarchy has been automatically created that consists of the following
	// structure: IfcProject > IfcSite > IfcBuilding > IfcBuildingStorey > IfcWall

	// Lateron changing the name of the IfcProject can be done by obtaining a reference to the 
	// project, which has been created automatically.
	file.getSingle<Ifc2x3::IfcProject>()->setName("IfcOpenHouse");

	// An IfcOwnerHistory has been initialized as well, which should be assigned to the wall.
	south_wall->setOwnerHistory(file.getSingle<Ifc2x3::IfcOwnerHistory>());

	// The wall will be shaped as a box, with the dimensions specified in millimeters.
	Ifc2x3::IfcProductDefinitionShape* south_wall_shape = file.addBox(10000, 360, 3000);

	// The shape has to be assigned to the representation of the wall and is placed at the origin
	// of the coordinate system.
	south_wall->setRepresentation(south_wall_shape);
	south_wall->setObjectPlacement(file.addLocalPlacement());

	// A pale white colour is assigned to the wall.
	Ifc2x3::IfcPresentationStyleAssignment* wall_colour = file.setSurfaceColour(
		south_wall->Representation(), 0.75, 0.73, 0.68);

	// Now create a footing for the wall to rest on.
	Ifc2x3::IfcFooting* footing = new Ifc2x3::IfcFooting(guid(), file.getSingle<Ifc2x3::IfcOwnerHistory>(),
		S("Footing"), null, null, 0, 0, null, Ifc2x3::IfcFootingTypeEnum::IfcFootingType_STRIP_FOOTING);

	file.addBuildingProduct(footing);

	// The footing will span the entire floor plan of our building. The IfcRepresentationContext is
	// something that has been created automatically as well, but representations could have been 
	// assigned to a specific context, for example to add a two dimensional plan representation as well.
	footing->setRepresentation(file.addBox(10100, 5460, 2000, 0, 0, 0, file.getSingle<Ifc2x3::IfcRepresentationContext>()));
	footing->setObjectPlacement(file.addLocalPlacement(0, 2500, -2000));
	// The footing will have a dark gray colour
	Ifc2x3::IfcPresentationStyleAssignment* footing_colour = file.setSurfaceColour(footing->Representation(), 0.26, 0.22, 0.18);

	// IFC has two ways to apply boolean operations to geometry. IfcBooleanResults are commonly used 
	// to clip geometry to a surface, for example to a slanted roof. For openings that are filled 
	// with another element, for example a door or a window, an IfcOpeningElement is used instead.
	// An opening element is created with rectangular geometry
	Ifc2x3::IfcOpeningElement* west_opening = new Ifc2x3::IfcOpeningElement(guid(), file.getSingle<Ifc2x3::IfcOwnerHistory>(),
		null, null, null, file.addLocalPlacement(-2500, 0, 400),
		file.addBox(6000, 3630, 1600, 0, 0, 0, file.getSingle<Ifc2x3::IfcRepresentationContext>()), null);
	file.AddEntity(west_opening);

	// Relate the opening element to the wall.
	Ifc2x3::IfcRelVoidsElement* void_element = new Ifc2x3::IfcRelVoidsElement(guid(), file.getSingle<Ifc2x3::IfcOwnerHistory>(),
		null, null, south_wall, west_opening);
	file.AddEntity(void_element);

	// Now create an additional opening
	Ifc2x3::IfcOpeningElement* south_opening = new Ifc2x3::IfcOpeningElement(guid(), file.getSingle<Ifc2x3::IfcOwnerHistory>(),
		null, null, null, file.addLocalPlacement(3000, 0, 400),
		file.addBox(1860, 3000, 1600, 0, 0, 0, file.getSingle<Ifc2x3::IfcRepresentationContext>()), null);
	file.AddEntity(south_opening);
	file.AddEntity(new Ifc2x3::IfcRelVoidsElement(guid(), file.getSingle<Ifc2x3::IfcOwnerHistory>(), null, null, south_wall, south_opening));
	
	// Create a roof element
	Ifc2x3::IfcRoof* south_roof = new Ifc2x3::IfcRoof(guid(), file.getSingle<Ifc2x3::IfcOwnerHistory>(), S("South roof"), null, null, 
		0, 0, null, Ifc2x3::IfcRoofTypeEnum::IfcRoofType_GABLE_ROOF);
	
	// The roof geometry is slanted 45 degrees by specifying a direction for the box extrusion
	south_roof->setRepresentation(file.addBox(10200, 360, sqrt(2.0*2900*2900), 0, file.addPlacement3d(0, 0, 0, 0, 1, 0),
		file.addTriplet<Ifc2x3::IfcDirection>(0, -sqrt(0.5), sqrt(0.5)), file.getSingle<Ifc2x3::IfcRepresentationContext>()));
	south_roof->setObjectPlacement(file.addLocalPlacement(0, -400, 2700));
	file.addBuildingProduct(south_roof);

	// The same roof geometry is re-used on the north side of the roof, by inverting the X-axis of
	// the local placement the roof is rotated 180 degrees around the Z-axis
	Ifc2x3::IfcRoof* north_roof = new Ifc2x3::IfcRoof(guid(), file.getSingle<Ifc2x3::IfcOwnerHistory>(), S("North roof"),
		null, null, 0, 0, null, Ifc2x3::IfcRoofTypeEnum::IfcRoofType_GABLE_ROOF);
	north_roof->setOwnerHistory(file.getSingle<Ifc2x3::IfcOwnerHistory>());
	north_roof->setRepresentation(south_roof->Representation());
	north_roof->setObjectPlacement(file.addLocalPlacement(0, 5400, 2700, 0, 0, 1, -1, 0, 0));
	file.addBuildingProduct(north_roof);

	// By specifying a surface style for the south part of the roof, it gets assigned to the other 
	// roof part as well, because they share the same representation.
	file.setSurfaceColour(south_roof->Representation(), 0.24, 0.08, 0.04);

	// Copy the south wall to the north
	file.addBuildingProduct(new Ifc2x3::IfcWallStandardCase(guid(), file.getSingle<Ifc2x3::IfcOwnerHistory>(), S("North wall"),
		null, null, file.addLocalPlacement(0, 5000, 0), south_wall->Representation(), null));

	// Now create a wall on the east of the building, again starting with just a box shape
	Ifc2x3::IfcWallStandardCase* east_wall = new Ifc2x3::IfcWallStandardCase(guid(), file.getSingle<Ifc2x3::IfcOwnerHistory>(),
		S("East wall"), null, null, file.addLocalPlacement(4820, 2500, 0, 0, 0, 1, 0, 1, 0), file.addBox(5000, 360, 6000), null);
	file.addBuildingProduct(east_wall);

	// The east wall geometry is clipped using two IfcHalfSpaceSolids, created from an 
	// 'axis 3d placement' that specifies the plane against which the geometry is clipped.
	file.clipRepresentation(east_wall->Representation(), file.addPlacement3d(-2500, 0, 3000, -1, 0, 1), false);
	file.clipRepresentation(east_wall->Representation(), file.addPlacement3d(2500, 0, 3000, 1, 0, 1), false);

	file.setSurfaceColour(east_wall->Representation(), wall_colour);

	// The east wall is copied to the west location of the house
	Ifc2x3::IfcWallStandardCase* west_wall = new Ifc2x3::IfcWallStandardCase(guid(), file.getSingle<Ifc2x3::IfcOwnerHistory>(),
		S("West wall"), null, null, file.addLocalPlacement(-4820, 2500, 0, 0, 0, 1, 0, -1, 0), east_wall->Representation(), null);
	file.addBuildingProduct(west_wall);

	// The west wall is assigned an opening element we created for the south wall, opening elements are
	// not shared accross building elements, even if they share the same representation. Hence, the east
	// wall will not feature this opening.
	file.AddEntity(new Ifc2x3::IfcRelVoidsElement(guid(), file.getSingle<Ifc2x3::IfcOwnerHistory>(), null, null, west_wall, west_opening));
	
	// Up until now we have only used simple extrusions for the creation of the geometry. For the 
	// ground mesh of the IfcSite we will use a Nurbs surface created in Open Cascade. The surface 
	// will be tesselated using the deflection specified.
	TopoDS_Shape shape;
	createGroundShape(shape);
	IfcEntities geometrical_entities(new IfcEntityList());
	Ifc2x3::IfcProductDefinitionShape* ground_representation = IfcGeom::tesselate(shape, 100., geometrical_entities);
	file.getSingle<Ifc2x3::IfcSite>()->setRepresentation(ground_representation);
	file.AddEntities(geometrical_entities);
	Ifc2x3::IfcShapeRepresentation::list ground_reps = geometrical_entities->as<Ifc2x3::IfcShapeRepresentation>();
	for (Ifc2x3::IfcShapeRepresentation::it it = ground_reps->begin(); it != ground_reps->end(); ++it) {
		(*it)->setContextOfItems(file.getSingle<Ifc2x3::IfcRepresentationContext>());
	}
	file.setSurfaceColour(ground_representation, 0.15, 0.25, 0.05);

	// According to the Ifc2x3 schema an IfcWallStandardCase needs to have an IfcMaterialLayerSet
	// assigned. Note that this material definition is independent of the surface styles we have 
	// been assigning to the walls already. The surface styles determine the colour in the 
	// '3D viewport' of most applications.
	// Some BIM authoring applications, such as Autodesk Revit, ignore the geometrical representation
	// by and large and construct native walls using the layer thickness and reference line offset 
	// provided here.
	Ifc2x3::IfcMaterial* material = new Ifc2x3::IfcMaterial("Brick");
	Ifc2x3::IfcMaterialLayer* layer = new Ifc2x3::IfcMaterialLayer(material, 360, null);
	Ifc2x3::IfcMaterialLayer::list layers (new IfcTemplatedEntityList<Ifc2x3::IfcMaterialLayer>());
	layers->push(layer);
	Ifc2x3::IfcMaterialLayerSet* layer_set = new Ifc2x3::IfcMaterialLayerSet(layers, S("Wall"));
	Ifc2x3::IfcMaterialLayerSetUsage* layer_usage = new Ifc2x3::IfcMaterialLayerSetUsage(layer_set,
		Ifc2x3::IfcLayerSetDirectionEnum::IfcLayerSetDirection_AXIS2,
		Ifc2x3::IfcDirectionSenseEnum::IfcDirectionSense_POSITIVE, -180);

	Ifc2x3::IfcRelAssociatesMaterial* associates_material = new Ifc2x3::IfcRelAssociatesMaterial(guid(),
		file.getSingle<Ifc2x3::IfcOwnerHistory>(), null, null,
		file.EntitiesByType<Ifc2x3::IfcWallStandardCase>()->as<Ifc2x3::IfcRoot>(), layer_usage);

	file.AddEntity(material);
	file.AddEntity(layer);
	file.AddEntity(layer_set);	
	file.AddEntity(layer_usage);
	file.AddEntity(associates_material);

	// In addition, another common way to represent geometry in IFC files is to use extrusions of
	// planar areas bounded by a polygon.
	std::vector<XY> stair_points;
	stair_points.push_back(XY(  0,  0));
	stair_points.push_back(XY(250,  0));
	stair_points.push_back(XY(250, 200));
	stair_points.push_back(XY(500, 200));
	stair_points.push_back(XY(500, 400));
	stair_points.push_back(XY(  0, 400));
	Ifc2x3::IfcStairFlight* stair = new Ifc2x3::IfcStairFlight(guid(), file.getSingle<Ifc2x3::IfcOwnerHistory>(),
		null, null, null, file.addLocalPlacement(5050, 1000, 0, 0, 1, 0, 1, 0, 0),
		file.addExtrudedPolyline(stair_points, 1200), null, 2, 2, 0.2, 0.25);

	file.addBuildingProduct(stair);
	file.setSurfaceColour(stair->Representation(), footing_colour);

	Ifc2x3::IfcOpeningElement* door_opening = new Ifc2x3::IfcOpeningElement(guid(), file.getSingle<Ifc2x3::IfcOwnerHistory>(),
		null, null, null, file.addLocalPlacement(5000-180, 2500-900, 0), file.addBox(1000, 1000, 2200), null);
	file.AddEntity(door_opening);
	file.AddEntity(new Ifc2x3::IfcRelVoidsElement(guid(), file.getSingle<Ifc2x3::IfcOwnerHistory>(), null, null, east_wall, door_opening));

	// A single shape representation can contain multiple representiation items. This way a product
	// can be a composition of multiple solids. The following door will be composed of four boxes
	// which constitute the door and its frame.
	Ifc2x3::IfcDoor* door = new Ifc2x3::IfcDoor(guid(), file.getSingle<Ifc2x3::IfcOwnerHistory>(), null, null, null,
		file.addLocalPlacement(4800, 1600, 0, 0, 0, 1, 0, 1, 0), 0, null, 2200, 1000);
	door->setRepresentation(file.addBox(80, 80, 2120, 0, file.addPlacement3d(460, 0, 0)));
	Ifc2x3::IfcRepresentation::list door_representations = door->Representation()->Representations();
	Ifc2x3::IfcShapeRepresentation* door_body = 0;
	for (Ifc2x3::IfcRepresentation::it i = door_representations->begin(); i != door_representations->end(); ++i) {
		Ifc2x3::IfcRepresentation* rep = *i;
		if (rep->is(Ifc2x3::Type::IfcShapeRepresentation) && rep->RepresentationIdentifier() == "Body") {
			door_body = (Ifc2x3::IfcShapeRepresentation*) rep;
		}
	}
	file.addBox(door_body,  80, 80, 2120, 0, file.addPlacement3d(-460, 0,   0));
	file.addBox(door_body, 1000, 80,  80, 0, file.addPlacement3d(   0, 0, 2120));
	file.addBox(door_body, 860, 30, 2120);
	file.addBuildingProduct(door);
	file.setSurfaceColour(door->Representation(), 0.9, 0.9, 0.9);
	file.AddEntity(new Ifc2x3::IfcRelFillsElement(guid(), file.getSingle<Ifc2x3::IfcOwnerHistory>(), null, null, door_opening, door));

	// Surface styles are assigned to representation items, hence there is no real limitation to
	// assign different colours within the same representation. However, some viewers have 
	// difficulties rendering products with representation items with different surface styles. 
	// Therefore we will construct the window as a decomposition of beams and a plate, in which 
	// only the plate will have a transparent material assigned.

	// The window frame will consists of four seperate beams.
	// AutoCAD Architecture will create an internal window type for the IfcWindow created.
	// Therefore the OverallWidth and OverallHeight of the window attributes will need to
	// match the bounding box of the representation. Furthermore, the window placement needs
	// to align with the lowerleft corner of the constituent parts.
	Ifc2x3::IfcProductDefinitionShape::list frame_representations (new IfcTemplatedEntityList<Ifc2x3::IfcProductDefinitionShape>());
	frame_representations->push(file.addBox(1860, 90, 90));
	frame_representations->push(*frame_representations->begin()); // Add a reference to the shape created above
	frame_representations->push(file.addBox(90, 90, 1420));
	frame_representations->push(*(frame_representations->end()-1)); // Add a reference to the shape created above

	// The beams all have the same surface style assigned
	Ifc2x3::IfcPresentationStyleAssignment* frame_style = 0;
	for (Ifc2x3::IfcProductDefinitionShape::it i = frame_representations->begin(); i != frame_representations->end(); ++i) {
		if (frame_style) {
			file.setSurfaceColour(*i, frame_style);
		} else {
			frame_style = file.setSurfaceColour(*i, 0.5, 0.4, 0.3);
		}
	}

	// This window will be placed at five locations within the building. A list of placements is 
	// created and is iterated over to create all window instances.
	Ifc2x3::IfcLocalPlacement::list window_placements (new IfcTemplatedEntityList<Ifc2x3::IfcLocalPlacement>());
	window_placements->push(file.addLocalPlacement(2*-1770-430-930,   -45, 400));
	window_placements->push(file.addLocalPlacement(  -1770-430-930,   -45, 400));
	window_placements->push(file.addLocalPlacement(       -430-930,   -45, 400));
	window_placements->push(file.addLocalPlacement(       3000-930,   -45, 400));
	window_placements->push(file.addLocalPlacement(      -4855+45, 885-930, 400, 0, 0, 1, 0, 1, 0));
	
	for (Ifc2x3::IfcLocalPlacement::it it = window_placements->begin(); it != window_placements->end(); ++it) {
		
		// Create the window at the current location
		Ifc2x3::IfcLocalPlacement* place = *it;
		Ifc2x3::IfcWindow* window = new Ifc2x3::IfcWindow(guid(), file.getSingle<Ifc2x3::IfcOwnerHistory>(),
			null, null, null, place, 0, null, 1600, 1860);
		file.addBuildingProduct(window);		

		// Initalize a list of parts for the window to be composed of
		Ifc2x3::IfcObjectDefinition::list window_parts(new IfcTemplatedEntityList<Ifc2x3::IfcObjectDefinition>());

		// The placements for the beams are not shared accross the different windows because every
		// beam is placed relative to its parent window entity.
		Ifc2x3::IfcLocalPlacement::list frame_placements (new IfcTemplatedEntityList<Ifc2x3::IfcLocalPlacement>());
		frame_placements->push(file.addLocalPlacement( 930,45));
		frame_placements->push(file.addLocalPlacement( 930, 45, 1510));
		frame_placements->push(file.addLocalPlacement(-885+930, 45,  90));
		frame_placements->push(file.addLocalPlacement( 885+930, 45,  90));
		
		// Now iterate over the placements and representations of the beam and add them to list of parts
		Ifc2x3::IfcLocalPlacement::it frame_placement;
		Ifc2x3::IfcProductDefinitionShape::it frame_representation;
		for (frame_placement = frame_placements->begin(), frame_representation = frame_representations->begin();
			frame_placement != frame_placements->end() && frame_representation != frame_representations->end();
			++frame_placement, ++frame_representation)
		{
			Ifc2x3::IfcMember* frame_part = new Ifc2x3::IfcMember(guid(), file.getSingle<Ifc2x3::IfcOwnerHistory>(),
				null, null, null, *frame_placement, *frame_representation, null);
			file.AddEntity(frame_part);
			window_parts->push(frame_part);
			file.relatePlacements(window, frame_part);
		}

		// Add the glass plate to the list of parts
		Ifc2x3::IfcPlate* glass_part = new Ifc2x3::IfcPlate(guid(), file.getSingle<Ifc2x3::IfcOwnerHistory>(), null,
			null, null, file.addLocalPlacement(930, 45, 90), file.addBox(1680, 10, 1420), null);
		file.AddEntity(glass_part);
		window_parts->push(glass_part);
		file.relatePlacements(window, glass_part);
		file.setSurfaceColour(glass_part->Representation(), 0.6, 0.7, 0.75, 0.1);
		
		// Now create a decomposition relation between the window and the parts. Most viewers and authoring
		// tools will consider the window a single entity that can be selected as a whole.
		Ifc2x3::IfcRelDecomposes* decomposition = new Ifc2x3::IfcRelAggregates(guid(), file.getSingle<Ifc2x3::IfcOwnerHistory>(),
			null, null, window, window_parts);
		file.AddEntity(decomposition);		
	}

	// Finally create a file stream for our output and write the IFC file to it.
	std::ofstream f("IfcOpenHouse.ifc");
	f << file;
}

void createGroundShape(TopoDS_Shape& shape) {
	TColgp_Array2OfPnt cv (0, 4, 0, 4);
	cv.SetValue(0, 0, gp_Pnt(-10000, -10000, -4130));
	cv.SetValue(0, 1, gp_Pnt(-10000,  -4330, -4130));
	cv.SetValue(0, 2, gp_Pnt(-10000,      0, -5130));
	cv.SetValue(0, 3, gp_Pnt(-10000,   4330, -7130));
	cv.SetValue(0, 4, gp_Pnt(-10000,  10000, -7130));
	cv.SetValue(1, 0, gp_Pnt( -3330, -10000, -5130));
	cv.SetValue(1, 1, gp_Pnt( -7670,  -3670,  5000));
	cv.SetValue(1, 2, gp_Pnt( -9000,      0,  1000));
	cv.SetValue(1, 3, gp_Pnt( -7670,   7670,  6000));
	cv.SetValue(1, 4, gp_Pnt( -3330,  10000, -4130));
	cv.SetValue(2, 0, gp_Pnt(     0, -10000, -5530));
	cv.SetValue(2, 1, gp_Pnt(     0,  -3670,  3000));
	cv.SetValue(2, 2, gp_Pnt(     0,      0, -12000));
	cv.SetValue(2, 3, gp_Pnt(     0,   7670,  1500));
	cv.SetValue(2, 4, gp_Pnt(     0,  10000, -4130));
	cv.SetValue(3, 0, gp_Pnt(  3330, -10000, -6130));
	cv.SetValue(3, 1, gp_Pnt(  7670,  -3670,  6000));
	cv.SetValue(3, 2, gp_Pnt(  9000,      0,  5000));
	cv.SetValue(3, 3, gp_Pnt(  7670,   9000,  7000));
	cv.SetValue(3, 4, gp_Pnt(  3330,  10000, -4130));
	cv.SetValue(4, 0, gp_Pnt( 10000, -10000, -6130));
	cv.SetValue(4, 1, gp_Pnt( 10000,  -4330, -5130));
	cv.SetValue(4, 2, gp_Pnt( 10000,      0, -4130));
	cv.SetValue(4, 3, gp_Pnt( 10000,   4330, -4130));
	cv.SetValue(4, 4, gp_Pnt( 10000,  10000, -8130));
	TColStd_Array1OfReal knots(0, 1);
	knots(0) = 0;
	knots(1) = 1;		
	TColStd_Array1OfInteger mult(0, 1);
	mult(0) = 5;
	mult(1) = 5;	
	Handle(Geom_BSplineSurface) surf = new Geom_BSplineSurface(cv, knots, knots, mult, mult, 4, 4);
	shape = BRepBuilderAPI_MakeFace(surf, 1);
}