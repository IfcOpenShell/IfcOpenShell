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

#include <Standard_Version.hxx>

#ifdef USE_IFC4
#include "../ifcparse/Ifc4.h"
#else
#include "../ifcparse/Ifc2x3.h"
#endif

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
	file.filename("IfcOpenHouse.ifc");

	// Start by adding a wall to the file, initially leaving most attributes blank.
	IfcSchema::IfcWallStandardCase* south_wall = new IfcSchema::IfcWallStandardCase(
		guid(), 			// GlobalId
		0, 					// OwnerHistory
		S("South wall"), 	// Name
		null, 				// Description
		null, 				// ObjectType
		0, 					// ObjectPlacement
		0, 					// Representation
		null				// Tag
#ifdef USE_IFC4
		, IfcSchema::IfcWallTypeEnum::IfcWallType_STANDARD
#endif
	);
	file.addBuildingProduct(south_wall);

	// By adding a wall, a hierarchy has been automatically created that consists of the following
	// structure: IfcProject > IfcSite > IfcBuilding > IfcBuildingStorey > IfcWall

	// Lateron changing the name of the IfcProject can be done by obtaining a reference to the 
	// project, which has been created automatically.
	file.getSingle<IfcSchema::IfcProject>()->setName("IfcOpenHouse");

	// An IfcOwnerHistory has been initialized as well, which should be assigned to the wall.
	south_wall->setOwnerHistory(file.getSingle<IfcSchema::IfcOwnerHistory>());

	// The wall will be shaped as a box, with the dimensions specified in millimeters.
	IfcSchema::IfcProductDefinitionShape* south_wall_shape = file.addBox(10000, 360, 3000);

	// The shape has to be assigned to the representation of the wall and is placed at the origin
	// of the coordinate system.
	south_wall->setRepresentation(south_wall_shape);
	south_wall->setObjectPlacement(file.addLocalPlacement());

	// A pale white colour is assigned to the wall.
	IfcSchema::IfcPresentationStyleAssignment* wall_colour = file.setSurfaceColour(
		south_wall->Representation(), 0.75, 0.73, 0.68);

	// Now create a footing for the wall to rest on.
	IfcSchema::IfcFooting* footing = new IfcSchema::IfcFooting(guid(), file.getSingle<IfcSchema::IfcOwnerHistory>(),
		S("Footing"), null, null, 0, 0, null, IfcSchema::IfcFootingTypeEnum::IfcFootingType_STRIP_FOOTING);

	file.addBuildingProduct(footing);

	// The footing will span the entire floor plan of our building. The IfcRepresentationContext is
	// something that has been created automatically as well, but representations could have been 
	// assigned to a specific context, for example to add a two dimensional plan representation as well.
	footing->setRepresentation(file.addBox(10100, 5460, 2000, 0, 0, 0, file.getSingle<IfcSchema::IfcRepresentationContext>()));
	footing->setObjectPlacement(file.addLocalPlacement(0, 2500, -2000));
	// The footing will have a dark gray colour
	IfcSchema::IfcPresentationStyleAssignment* footing_colour = file.setSurfaceColour(footing->Representation(), 0.26, 0.22, 0.18);

	// IFC has two ways to apply boolean operations to geometry. IfcBooleanResults are commonly used 
	// to clip geometry to a surface, for example to a slanted roof. For openings that are filled 
	// with another element, for example a door or a window, an IfcOpeningElement is used instead.
	// An opening element is created with rectangular geometry
	IfcSchema::IfcOpeningElement* west_opening = new IfcSchema::IfcOpeningElement(guid(), file.getSingle<IfcSchema::IfcOwnerHistory>(),
		null, null, null, file.addLocalPlacement(-2500, 0, 400),
		file.addBox(6000, 3630, 1600, 0, 0, 0, file.getSingle<IfcSchema::IfcRepresentationContext>()), null
#ifdef USE_IFC4
		, IfcSchema::IfcOpeningElementTypeEnum::IfcOpeningElementType_OPENING
#endif
	);
	file.AddEntity(west_opening);

	// Relate the opening element to the wall.
	IfcSchema::IfcRelVoidsElement* void_element = new IfcSchema::IfcRelVoidsElement(guid(), file.getSingle<IfcSchema::IfcOwnerHistory>(),
		null, null, south_wall, west_opening);
	file.AddEntity(void_element);

	// Now create an additional opening
	IfcSchema::IfcOpeningElement* south_opening = new IfcSchema::IfcOpeningElement(guid(), file.getSingle<IfcSchema::IfcOwnerHistory>(),
		null, null, null, file.addLocalPlacement(3000, 0, 400),
		file.addBox(1860, 3000, 1600, 0, 0, 0, file.getSingle<IfcSchema::IfcRepresentationContext>()), null
#ifdef USE_IFC4
		, IfcSchema::IfcOpeningElementTypeEnum::IfcOpeningElementType_OPENING
#endif
	);
	file.AddEntity(south_opening);
	file.AddEntity(new IfcSchema::IfcRelVoidsElement(guid(), file.getSingle<IfcSchema::IfcOwnerHistory>(), null, null, south_wall, south_opening));
	
	// Create a roof element
	IfcSchema::IfcRoof* south_roof = new IfcSchema::IfcRoof(guid(), file.getSingle<IfcSchema::IfcOwnerHistory>(), S("South roof"), null, null, 
		0, 0, null, IfcSchema::IfcRoofTypeEnum::IfcRoofType_GABLE_ROOF);
	
	// The roof geometry is slanted 45 degrees by specifying a direction for the box extrusion
	south_roof->setRepresentation(file.addBox(10200, 360, sqrt(2.0*2900*2900), 0, file.addPlacement3d(0, 0, 0, 0, 1, 0),
		file.addTriplet<IfcSchema::IfcDirection>(0, -sqrt(0.5), sqrt(0.5)), file.getSingle<IfcSchema::IfcRepresentationContext>()));
	south_roof->setObjectPlacement(file.addLocalPlacement(0, -400, 2700));
	file.addBuildingProduct(south_roof);

	// The same roof geometry is re-used on the north side of the roof, by inverting the X-axis of
	// the local placement the roof is rotated 180 degrees around the Z-axis
	IfcSchema::IfcRoof* north_roof = new IfcSchema::IfcRoof(guid(), file.getSingle<IfcSchema::IfcOwnerHistory>(), S("North roof"),
		null, null, 0, 0, null, IfcSchema::IfcRoofTypeEnum::IfcRoofType_GABLE_ROOF);
	north_roof->setOwnerHistory(file.getSingle<IfcSchema::IfcOwnerHistory>());
	north_roof->setRepresentation(south_roof->Representation());
	north_roof->setObjectPlacement(file.addLocalPlacement(0, 5400, 2700, 0, 0, 1, -1, 0, 0));
	file.addBuildingProduct(north_roof);

	// By specifying a surface style for the south part of the roof, it gets assigned to the other 
	// roof part as well, because they share the same representation.
	file.setSurfaceColour(south_roof->Representation(), 0.24, 0.08, 0.04);

	// Copy the south wall to the north
	file.addBuildingProduct(new IfcSchema::IfcWallStandardCase(guid(), file.getSingle<IfcSchema::IfcOwnerHistory>(), S("North wall"),
		null, null, file.addLocalPlacement(0, 5000, 0), south_wall->Representation(), null
#ifdef USE_IFC4
		, IfcSchema::IfcWallTypeEnum::IfcWallType_STANDARD
#endif	
	));

	// Now create a wall on the east of the building, again starting with just a box shape
	IfcSchema::IfcWallStandardCase* east_wall = new IfcSchema::IfcWallStandardCase(guid(), file.getSingle<IfcSchema::IfcOwnerHistory>(),
		S("East wall"), null, null, file.addLocalPlacement(4820, 2500, 0, 0, 0, 1, 0, 1, 0), file.addBox(5000, 360, 6000), null
#ifdef USE_IFC4
		, IfcSchema::IfcWallTypeEnum::IfcWallType_STANDARD
#endif	
	);
	file.addBuildingProduct(east_wall);

	// The east wall geometry is clipped using two IfcHalfSpaceSolids, created from an 
	// 'axis 3d placement' that specifies the plane against which the geometry is clipped.
	file.clipRepresentation(east_wall->Representation(), file.addPlacement3d(-2500, 0, 3000, -1, 0, 1), false);
	file.clipRepresentation(east_wall->Representation(), file.addPlacement3d(2500, 0, 3000, 1, 0, 1), false);

	file.setSurfaceColour(east_wall->Representation(), wall_colour);

	// The east wall is copied to the west location of the house
	IfcSchema::IfcWallStandardCase* west_wall = new IfcSchema::IfcWallStandardCase(guid(), file.getSingle<IfcSchema::IfcOwnerHistory>(),
		S("West wall"), null, null, file.addLocalPlacement(-4820, 2500, 0, 0, 0, 1, 0, -1, 0), east_wall->Representation(), null
#ifdef USE_IFC4
		, IfcSchema::IfcWallTypeEnum::IfcWallType_STANDARD
#endif	
	);
	file.addBuildingProduct(west_wall);

	// The west wall is assigned an opening element we created for the south wall, opening elements are
	// not shared accross building elements, even if they share the same representation. Hence, the east
	// wall will not feature this opening.
	// NB: an Opening Element can only be used to create a single void within a single Element, as per:
	// http://www.buildingsmart-tech.org/ifc/IFC2x3/TC1/html/ifcproductextension/lexical/ifcfeatureelementsubtraction.htm
	IfcSchema::IfcOpeningElement* west_opening_copy = new IfcSchema::IfcOpeningElement(guid(), file.getSingle<IfcSchema::IfcOwnerHistory>(),
		null, null, null, west_opening->ObjectPlacement(), west_opening->Representation(), null
#ifdef USE_IFC4
		, IfcSchema::IfcOpeningElementTypeEnum::IfcOpeningElementType_OPENING
#endif	
	);
	file.AddEntity(west_opening_copy);
	file.AddEntity(new IfcSchema::IfcRelVoidsElement(guid(), file.getSingle<IfcSchema::IfcOwnerHistory>(), null, null, west_wall, west_opening_copy));
	
	// Up until now we have only used simple extrusions for the creation of the geometry. For the 
	// ground mesh of the IfcSite we will use a Nurbs surface created in Open Cascade. The surface 
	// will be tesselated using the deflection specified.
	TopoDS_Shape shape;
	createGroundShape(shape);
	IfcEntities geometrical_entities(new IfcEntityList());
	IfcSchema::IfcProductDefinitionShape* ground_representation = IfcGeom::tesselate(shape, 100., geometrical_entities);
	file.getSingle<IfcSchema::IfcSite>()->setRepresentation(ground_representation);
	file.AddEntities(geometrical_entities);
	IfcSchema::IfcShapeRepresentation::list ground_reps = geometrical_entities->as<IfcSchema::IfcShapeRepresentation>();
	for (IfcSchema::IfcShapeRepresentation::it it = ground_reps->begin(); it != ground_reps->end(); ++it) {
		(*it)->setContextOfItems(file.getSingle<IfcSchema::IfcRepresentationContext>());
	}
	file.setSurfaceColour(ground_representation, 0.15, 0.25, 0.05);

	// According to the Ifc2x3 schema an IfcWallStandardCase needs to have an IfcMaterialLayerSet
	// assigned. Note that this material definition is independent of the surface styles we have 
	// been assigning to the walls already. The surface styles determine the colour in the 
	// '3D viewport' of most applications.
	// Some BIM authoring applications, such as Autodesk Revit, ignore the geometrical representation
	// by and large and construct native walls using the layer thickness and reference line offset 
	// provided here.
#ifdef USE_IFC4
	IfcSchema::IfcMaterial* material = new IfcSchema::IfcMaterial("Brick", null, null);
#else
	IfcSchema::IfcMaterial* material = new IfcSchema::IfcMaterial("Brick");
#endif
	IfcSchema::IfcMaterialLayer* layer = new IfcSchema::IfcMaterialLayer(
		material, 
		360, 
		null
#ifdef USE_IFC4
		, null
		, null 
		, null
		, null
#endif
	);
	IfcSchema::IfcMaterialLayer::list layers (new IfcTemplatedEntityList<IfcSchema::IfcMaterialLayer>());
	layers->push(layer);
	IfcSchema::IfcMaterialLayerSet* layer_set = new IfcSchema::IfcMaterialLayerSet(
		layers, 
		S("Wall")
#ifdef USE_IFC4
		, null
#endif
	);
	IfcSchema::IfcMaterialLayerSetUsage* layer_usage = new IfcSchema::IfcMaterialLayerSetUsage(
		layer_set,
		IfcSchema::IfcLayerSetDirectionEnum::IfcLayerSetDirection_AXIS2,
		IfcSchema::IfcDirectionSenseEnum::IfcDirectionSense_POSITIVE,
		-180
#ifdef USE_IFC4
		, null
#endif
	);

	IfcSchema::IfcRelAssociatesMaterial* associates_material = new IfcSchema::IfcRelAssociatesMaterial(
		guid(),
		file.getSingle<IfcSchema::IfcOwnerHistory>(), 
		null, 
		null,
#ifdef USE_IFC4
		file.EntitiesByType<IfcSchema::IfcWallStandardCase>()->generalize(),
#else
		file.EntitiesByType<IfcSchema::IfcWallStandardCase>()->as<IfcSchema::IfcRoot>(),
#endif
		layer_usage);

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
	IfcSchema::IfcStairFlight* stair = new IfcSchema::IfcStairFlight(guid(), file.getSingle<IfcSchema::IfcOwnerHistory>(),
		null, null, null, file.addLocalPlacement(5050, 1000, 0, 0, 1, 0, 1, 0, 0),
		file.addExtrudedPolyline(stair_points, 1200), null, 2, 2, 0.2, 0.25
#ifdef USE_IFC4
		, IfcSchema::IfcStairFlightTypeEnum::IfcStairFlightType_STRAIGHT
#endif
	);

	file.addBuildingProduct(stair);
	file.setSurfaceColour(stair->Representation(), footing_colour);

	IfcSchema::IfcOpeningElement* door_opening = new IfcSchema::IfcOpeningElement(guid(), file.getSingle<IfcSchema::IfcOwnerHistory>(),
		null, null, null, file.addLocalPlacement(5000-180, 2500-900, 0), file.addBox(1000, 1000, 2200), null
#ifdef USE_IFC4
		, IfcSchema::IfcOpeningElementTypeEnum::IfcOpeningElementType_OPENING
#endif	
	);
	file.AddEntity(door_opening);
	file.AddEntity(new IfcSchema::IfcRelVoidsElement(guid(), file.getSingle<IfcSchema::IfcOwnerHistory>(), null, null, east_wall, door_opening));

	// A single shape representation can contain multiple representiation items. This way a product
	// can be a composition of multiple solids. The following door will be composed of four boxes
	// which constitute the door and its frame.
	IfcSchema::IfcDoor* door = new IfcSchema::IfcDoor(guid(), file.getSingle<IfcSchema::IfcOwnerHistory>(), null, null, null,
		file.addLocalPlacement(4800, 1600, 0, 0, 0, 1, 0, 1, 0), 0, null, 2200, 1000
#ifdef USE_IFC4
		, IfcSchema::IfcDoorTypeEnum::IfcDoorType_DOOR
		, IfcSchema::IfcDoorTypeOperationEnum::IfcDoorTypeOperation_SINGLE_SWING_LEFT
		, null
#endif
	);
	door->setRepresentation(file.addBox(80, 80, 2120, 0, file.addPlacement3d(460, 0, 0)));
	IfcSchema::IfcRepresentation::list door_representations = door->Representation()->Representations();
	IfcSchema::IfcShapeRepresentation* door_body = 0;
	for (IfcSchema::IfcRepresentation::it i = door_representations->begin(); i != door_representations->end(); ++i) {
		IfcSchema::IfcRepresentation* rep = *i;
		if (rep->is(IfcSchema::Type::IfcShapeRepresentation) && rep->RepresentationIdentifier() == "Body") {
			door_body = (IfcSchema::IfcShapeRepresentation*) rep;
		}
	}
	file.addBox(door_body,  80, 80, 2120, 0, file.addPlacement3d(-460, 0,   0));
	file.addBox(door_body, 1000, 80,  80, 0, file.addPlacement3d(   0, 0, 2120));
	file.addBox(door_body, 860, 30, 2120);
	file.addBuildingProduct(door);
	file.setSurfaceColour(door->Representation(), 0.9, 0.9, 0.9);
	file.AddEntity(new IfcSchema::IfcRelFillsElement(guid(), file.getSingle<IfcSchema::IfcOwnerHistory>(), null, null, door_opening, door));

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
	IfcSchema::IfcProductDefinitionShape::list frame_representations (new IfcTemplatedEntityList<IfcSchema::IfcProductDefinitionShape>());
	frame_representations->push(file.addBox(1860, 90, 90));
	frame_representations->push(*frame_representations->begin()); // Add a reference to the shape created above
	frame_representations->push(file.addBox(90, 90, 1420));
	frame_representations->push(*(frame_representations->end()-1)); // Add a reference to the shape created above

	// The beams all have the same surface style assigned
	IfcSchema::IfcPresentationStyleAssignment* frame_style = 0;
	for (IfcSchema::IfcProductDefinitionShape::it i = frame_representations->begin(); i != frame_representations->end(); ++i) {
		if (frame_style) {
			file.setSurfaceColour(*i, frame_style);
		} else {
			frame_style = file.setSurfaceColour(*i, 0.5, 0.4, 0.3);
		}
	}

	// This window will be placed at five locations within the building. A list of placements is 
	// created and is iterated over to create all window instances.
	IfcSchema::IfcLocalPlacement::list window_placements (new IfcTemplatedEntityList<IfcSchema::IfcLocalPlacement>());
	window_placements->push(file.addLocalPlacement(2*-1770-430-930,   -45, 400));
	window_placements->push(file.addLocalPlacement(  -1770-430-930,   -45, 400));
	window_placements->push(file.addLocalPlacement(       -430-930,   -45, 400));
	window_placements->push(file.addLocalPlacement(       3000-930,   -45, 400));
	window_placements->push(file.addLocalPlacement(      -4855+45, 885-930, 400, 0, 0, 1, 0, 1, 0));
	
	for (IfcSchema::IfcLocalPlacement::it it = window_placements->begin(); it != window_placements->end(); ++it) {
		
		// Create the window at the current location
		IfcSchema::IfcLocalPlacement* place = *it;
		IfcSchema::IfcWindow* window = new IfcSchema::IfcWindow(guid(), file.getSingle<IfcSchema::IfcOwnerHistory>(),
			null, null, null, place, 0, null, 1600, 1860
#ifdef USE_IFC4
			, IfcSchema::IfcWindowTypeEnum::IfcWindowType_WINDOW
			, IfcSchema::IfcWindowTypePartitioningEnum::IfcWindowTypePartitioning_SINGLE_PANEL
			, null
#endif
	);
		file.addBuildingProduct(window);		

		// Initalize a list of parts for the window to be composed of
		IfcSchema::IfcObjectDefinition::list window_parts(new IfcTemplatedEntityList<IfcSchema::IfcObjectDefinition>());

		// The placements for the beams are not shared accross the different windows because every
		// beam is placed relative to its parent window entity.
		IfcSchema::IfcLocalPlacement::list frame_placements (new IfcTemplatedEntityList<IfcSchema::IfcLocalPlacement>());
		frame_placements->push(file.addLocalPlacement( 930,45));
		frame_placements->push(file.addLocalPlacement( 930, 45, 1510));
		frame_placements->push(file.addLocalPlacement(-885+930, 45,  90));
		frame_placements->push(file.addLocalPlacement( 885+930, 45,  90));
		
		// Now iterate over the placements and representations of the beam and add them to list of parts
		IfcSchema::IfcLocalPlacement::it frame_placement;
		IfcSchema::IfcProductDefinitionShape::it frame_representation;
		for (frame_placement = frame_placements->begin(), frame_representation = frame_representations->begin();
			frame_placement != frame_placements->end() && frame_representation != frame_representations->end();
			++frame_placement, ++frame_representation)
		{
			IfcSchema::IfcMember* frame_part = new IfcSchema::IfcMember(guid(), file.getSingle<IfcSchema::IfcOwnerHistory>(),
				null, null, null, *frame_placement, *frame_representation, null
#ifdef USE_IFC4
				, IfcSchema::IfcMemberTypeEnum::IfcMemberType_MULLION
#endif
			);
			file.AddEntity(frame_part);
			window_parts->push(frame_part);
			file.relatePlacements(window, frame_part);
		}

		// Add the glass plate to the list of parts
		IfcSchema::IfcPlate* glass_part = new IfcSchema::IfcPlate(guid(), file.getSingle<IfcSchema::IfcOwnerHistory>(), null,
			null, null, file.addLocalPlacement(930, 45, 90), file.addBox(1680, 10, 1420), null
#ifdef USE_IFC4
			, IfcSchema::IfcPlateTypeEnum::IfcPlateType_SHEET
#endif
		);
		file.AddEntity(glass_part);
		window_parts->push(glass_part);
		file.relatePlacements(window, glass_part);
		file.setSurfaceColour(glass_part->Representation(), 0.6, 0.7, 0.75, 0.1);
		
		// Now create a decomposition relation between the window and the parts. Most viewers and authoring
		// tools will consider the window a single entity that can be selected as a whole.
		IfcSchema::IfcRelDecomposes* decomposition = new IfcSchema::IfcRelAggregates(guid(), file.getSingle<IfcSchema::IfcOwnerHistory>(),
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
#if OCC_VERSION_HEX < 0x60502
	shape = BRepBuilderAPI_MakeFace(surf);
#else
	shape = BRepBuilderAPI_MakeFace(surf, 1);
#endif
}
