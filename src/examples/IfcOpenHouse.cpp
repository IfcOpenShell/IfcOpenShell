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

#include <BRepGProp.hxx>
#include <GProp_GProps.hxx>

#include <Precision.hxx>

#include "ifcparse/macros.h"

#ifndef IfcSchema
#define IfcSchema Ifc2x3
#endif

#include INCLUDE_SCHEMA(ifcparse, IfcSchema)
#include INCLUDE_SCHEMA_DEFINITIONS(ifcparse, IfcSchema)

#include "ifcparse/IfcBaseClass.h"
#include "ifcparse/IfcHierarchyHelper.h"

#include "../ifcgeom/Serialization/Serialization.h"

#if USE_VLD
#include <vld.h>
#endif

using namespace std::string_literals;

// Some convenience typedefs and definitions. 
typedef ifcopenshell::global_id guid;
typedef std::pair<double, double> XY;
#ifdef SCHEMA_HAS_IfcPresentationStyleAssignment
typedef IfcSchema::IfcPresentationStyleAssignment surface_style_t;
#else
typedef IfcSchema::IfcPresentationStyle surface_style_t;
#endif
boost::none_t const null = boost::none;

// The creation of Nurbs-surface for the IfcSite mesh, to be implemented lateron
void createGroundShape(TopoDS_Shape& shape);

int main() {

    // The hierarchy_helper is a subclass of the regular file that provides several
    // convenience functions for working with geometry in IFC files.
    hierarchy_helper<IfcSchema> file;
    file.header().file_name().setname("IfcOpenHouse.ifc");

	// Start by adding a wall to the file, initially leaving most attributes blank.
	IfcSchema::IfcWallStandardCase* south_wall = new IfcSchema::IfcWallStandardCase(
		guid(), 			// GlobalId
		0, 					// OwnerHistory
		"South wall"s,	 	// Name
		null, 				// Description
		null, 				// ObjectType
		0, 					// ObjectPlacement
		0, 					// Representation
		null				// Tag
#ifdef SCHEMA_IfcWall_HAS_PredefinedType
		, IfcSchema::IfcWallTypeEnum::IfcWallType_STANDARD
#endif
    file.addBuildingProduct(south_wall);

    // By adding a wall, a hierarchy has been automatically created that consists of the following
    // structure: IfcProject > IfcSite > IfcBuilding > IfcBuildingStorey > IfcWall

    // Lateron changing the name of the IfcProject can be done by obtaining a reference to the
    // project, which has been created automatically.
    file.getSingle<IfcSchema::IfcProject>().setName("IfcOpenHouse"s);

    // An IfcOwnerHistory has been initialized as well, which should be assigned to the wall.
    south_wall.setOwnerHistory(file.getSingle<IfcSchema::IfcOwnerHistory>());

    // The wall will be shaped as a box, with the dimensions specified in millimeters. The resulting
    // product definition will consist of both a body representation as well as an axis representation
    // that runs over the centerline of the box in the X-axis.
    auto south_wall_shape = file.addAxisBox(10000, 360, 3000);

    // Obtain a reference to the placement of the IfcBuildingStorey in order to create a hierarchy
    // of placements for the products
    auto storey_placement = file.getSingle<IfcSchema::IfcBuildingStorey>().ObjectPlacement();

    // The shape has to be assigned to the representation of the wall and is placed at the origin
    // of the coordinate system.
    south_wall.setRepresentation(south_wall_shape);
    south_wall.setObjectPlacement(file.addLocalPlacement(storey_placement));

	// A pale white colour is assigned to the wall.
	surface_style_t* wall_colour = setSurfaceColour(file, south_wall_shape, 0.75, 0.73, 0.68);

    // Now create a footing for the wall to rest on.
    auto footing = file.create<IfcSchema::IfcFooting>();
    footing.setGlobalId(guid());
    footing.setOwnerHistory(file.getSingle<IfcSchema::IfcOwnerHistory>());
    footing.setName("Footing");
    footing.setPredefinedType(IfcSchema::IfcFootingTypeEnum::IfcFootingType_STRIP_FOOTING);

    file.addBuildingProduct(footing);

	// The footing will span the entire floor plan of our building. The IfcRepresentationContext is
	// something that has been created automatically as well, but representations could have been 
	// assigned to a specific context, for example to add a two dimensional plan representation as well.
	footing->setRepresentation(file.addBox(10100, 5460, 2000));
	footing->setObjectPlacement(file.addLocalPlacement(storey_placement, 0, 2500, -2000));
	// The footing will have a dark gray colour
	surface_style_t* footing_colour = setSurfaceColour(file,footing->Representation(), 0.26, 0.22, 0.18);

    // IFC has two ways to apply boolean operations to geometry. IfcBooleanResults are commonly used
    // to clip geometry to a surface, for example to a slanted roof. For openings that are filled
    // with another element, for example a door or a window, an IfcOpeningElement is used instead.

	// An opening element is created with rectangular geometry:
	IfcSchema::IfcOpeningElement* west_opening = new IfcSchema::IfcOpeningElement(guid(), file.getSingle<IfcSchema::IfcOwnerHistory>(),
		null, null, null, file.addLocalPlacement(south_wall->ObjectPlacement(), -2500, 0, 400),
		file.addBox(6000, 3630, 1600), null
#ifdef SCHEMA_IfcOpeningElement_HAS_PredefinedType
		, IfcSchema::IfcOpeningElementTypeEnum::IfcOpeningElementType_OPENING
#endif

    // Relate the opening element to the wall.
    auto void_element = file.create<IfcSchema::IfcRelVoidsElement>();
    void_element.setGlobalId(guid());
    void_element.setOwnerHistory(file.getSingle<IfcSchema::IfcOwnerHistory>());
    void_element.setRelatingBuildingElement(south_wall);
    void_element.setRelatedOpeningElement(west_opening);

	// Now create an additional opening
	IfcSchema::IfcOpeningElement* south_opening = new IfcSchema::IfcOpeningElement(guid(), file.getSingle<IfcSchema::IfcOwnerHistory>(),
		null, null, null, file.addLocalPlacement(storey_placement, 3000, 0, 400),
		file.addBox(1860, 3000, 1600), null
#ifdef SCHEMA_IfcOpeningElement_HAS_PredefinedType
		, IfcSchema::IfcOpeningElementTypeEnum::IfcOpeningElementType_OPENING
#endif

    // Relate the opening element to the wall.
    auto void_element2 = file.create<IfcSchema::IfcRelVoidsElement>();
    void_element2.setGlobalId(guid());
    void_element2.setOwnerHistory(file.getSingle<IfcSchema::IfcOwnerHistory>());
    void_element2.setRelatingBuildingElement(south_wall);
    void_element2.setRelatedOpeningElement(south_opening);

	// CV-2x3-144: Roofs are aggregates and shall have at least one contained element and no own geometry
	IfcSchema::IfcSlab* south_roof_part = new IfcSchema::IfcSlab(guid(), file.getSingle<IfcSchema::IfcOwnerHistory>(), "South roof"s, 
		null, null, 0, 0, null, IfcSchema::IfcSlabTypeEnum::IfcSlabType_ROOF);
	
	// The geometry is instantiated by using IfcMappedItems. This way geometry definitions can
	// be reused while maintaining the cardinality constraint that the ShapeOfProduct relation
	// imposes on the IfcProductDefinitionShape. Note that this constrained is lifted in IFC4.
	south_roof_part->setRepresentation(file.addMappedItem(roof_rep));
	south_roof_part->setObjectPlacement(file.addLocalPlacement(roof->ObjectPlacement(), 0, -400, 2700));
	
	// The same roof geometry is re-used on the north side of the roof, by inverting the X-axis of
	// the local placement the roof is rotated 180 degrees around the Z-axis
	IfcSchema::IfcSlab* north_roof_part = new IfcSchema::IfcSlab(guid(), file.getSingle<IfcSchema::IfcOwnerHistory>(), "North roof"s,
		null, null, 0, 0, null, IfcSchema::IfcSlabTypeEnum::IfcSlabType_ROOF);
	north_roof_part->setOwnerHistory(file.getSingle<IfcSchema::IfcOwnerHistory>());
	north_roof_part->setRepresentation(file.addMappedItem(roof_rep));
	north_roof_part->setObjectPlacement(file.addLocalPlacement(roof->ObjectPlacement(), 0, 5400, 2700, 0, 0, 1, -1, 0, 0));
	
	IfcSchema::IfcObjectDefinition::list::ptr roof_parts(new IfcSchema::IfcObjectDefinition::list);
	roof_parts->push(south_roof_part);
	roof_parts->push(north_roof_part);
	IfcSchema::IfcRelDecomposes* roof_decomposition = new IfcSchema::IfcRelAggregates(guid(), file.getSingle<IfcSchema::IfcOwnerHistory>(),
			null, null, roof, roof_parts);
	file.addEntity(roof_decomposition);

	file.addBuildingProduct(south_roof_part);
	file.addBuildingProduct(north_roof_part);
	file.addBuildingProduct(roof);

	setSurfaceColour(file, roof_rep, 0.24, 0.08, 0.04);

	// Copy the south wall to the north
	IfcSchema::IfcWallStandardCase* north_wall = new IfcSchema::IfcWallStandardCase(guid(), file.getSingle<IfcSchema::IfcOwnerHistory>(), "North wall"s,
		null, null, file.addLocalPlacement(storey_placement, 0, 5000, 0), file.addAxisBox(10000, 360, 3000), null
#ifdef SCHEMA_IfcWall_HAS_PredefinedType
		, IfcSchema::IfcWallTypeEnum::IfcWallType_STANDARD
#endif	
	);
	file.addBuildingProduct(north_wall);
	setSurfaceColour(file,north_wall->Representation(), wall_colour);

    // The roof geometry is slanted 45 degrees by specifying a direction for the box extrusion
    auto roof_rep = file.addEmptyRepresentation();
    file.addBox(roof_rep, 10200, 360, sqrt(2.0 * 2900 * 2900), IfcSchema::IfcAxis2Placement2D{}, file.addPlacement3d(0, 0, 0, 0, 1, 0), file.addTriplet<IfcSchema::IfcDirection>(0, -sqrt(0.5), sqrt(0.5)));

    // CV-2x3-144: Roofs are aggregates and shall have at least one contained element and no own geometry
    auto south_roof_part = file.create<IfcSchema::IfcSlab>();
    south_roof_part.setGlobalId(guid());
    south_roof_part.setOwnerHistory(file.getSingle<IfcSchema::IfcOwnerHistory>());
    south_roof_part.setName("South roof");
    south_roof_part.setPredefinedType(IfcSchema::IfcSlabTypeEnum::IfcSlabType_ROOF);

    // The geometry is instantiated by using IfcMappedItems. This way geometry definitions can
    // be reused while maintaining the cardinality constraint that the ShapeOfProduct relation
    // imposes on the IfcProductDefinitionShape. Note that this constrained is lifted in IFC4.
    south_roof_part.setRepresentation(file.addMappedItem(roof_rep));
    south_roof_part.setObjectPlacement(file.addLocalPlacement(roof.ObjectPlacement(), 0, -400, 2700));

	// Now create a wall on the east of the building, again starting with just a box shape
	IfcSchema::IfcWallStandardCase* east_wall = new IfcSchema::IfcWallStandardCase(guid(), file.getSingle<IfcSchema::IfcOwnerHistory>(),
		"East wall"s, null, null, file.addLocalPlacement(storey_placement, 4820, 2500, 0, 0, 0, 1, 0, 1, 0), clipped_wall_body_reps[0], null
#ifdef SCHEMA_IfcWall_HAS_PredefinedType
		, IfcSchema::IfcWallTypeEnum::IfcWallType_STANDARD
#endif	
	);
	file.addBuildingProduct(east_wall);

	// The east wall is copied to the west location of the house
	IfcSchema::IfcWallStandardCase* west_wall = new IfcSchema::IfcWallStandardCase(guid(), file.getSingle<IfcSchema::IfcOwnerHistory>(),
		"West wall"s, null, null, file.addLocalPlacement(storey_placement, -4820, 2500, 0, 0, 0, 1, 0, -1, 0), clipped_wall_body_reps[1], null
#ifdef SCHEMA_IfcWall_HAS_PredefinedType
		, IfcSchema::IfcWallTypeEnum::IfcWallType_STANDARD
#endif	
	);
	file.addBuildingProduct(west_wall);

    file.addBuildingProduct(east_wall);

	// Not all viewers support opening elements with mapped representations, hence an exact copy of the
	// same subtraction box is instantiated for the otherwise identical opening element.
	IfcSchema::IfcOpeningElement* west_opening_copy = new IfcSchema::IfcOpeningElement(guid(), file.getSingle<IfcSchema::IfcOwnerHistory>(),
		null, null, null, file.addLocalPlacement(west_wall->ObjectPlacement(), 2500, -2500+4820, 400, 0, 0, 1, 0, 1, 0),
		file.addBox(6000, 3630, 1600), null
#ifdef SCHEMA_IfcOpeningElement_HAS_PredefinedType
		, IfcSchema::IfcOpeningElementTypeEnum::IfcOpeningElementType_OPENING
#endif	
	);
	file.addEntity(west_opening_copy);
	file.addEntity(new IfcSchema::IfcRelVoidsElement(guid(), file.getSingle<IfcSchema::IfcOwnerHistory>(), null, null, west_wall, west_opening_copy));
	
	// Up until now we have only used simple extrusions for the creation of the geometry. For the 
	// ground mesh of the IfcSite we will use a Nurbs surface created in Open Cascade. The surface 
	// will be tessellated using the deflection specified.
	TopoDS_Shape shape;
	createGroundShape(shape);
	auto ground_representation = IfcGeom::tesselate(file, shape, 100.).as<IfcSchema::IfcProductDefinitionShape>();
	file.getSingle<IfcSchema::IfcSite>().setRepresentation(ground_representation);

	GProp_GProps prop;
	BRepGProp::SurfaceProperties(shape, prop);
	const double site_area = prop.Mass() / 1000 / 1000;

	IfcSchema::IfcProperty::list::ptr properties(new IfcSchema::IfcProperty::list);
	properties->push(new IfcSchema::IfcPropertySingleValue("TotalArea", null, new IfcSchema::IfcAreaMeasure(site_area), 0));
	IfcSchema::IfcPropertySet* pset = new IfcSchema::IfcPropertySet(guid(), file.getSingle<IfcSchema::IfcOwnerHistory>(), "Pset_SiteCommon"s, null, properties);
#ifdef SCHEMA_HAS_IfcDefinitionSelect
	IfcSchema::IfcObjectDefinition::list::ptr related_objs(new IfcSchema::IfcObjectDefinition::list);
#else
	IfcSchema::IfcObject::list::ptr related_objs(new IfcSchema::IfcObject::list);
#endif
	related_objs->push(file.getSingle<IfcSchema::IfcSite>());
	IfcSchema::IfcRelDefinesByProperties* site_prop = new IfcSchema::IfcRelDefinesByProperties(guid(), file.getSingle<IfcSchema::IfcOwnerHistory>(), null, null, related_objs, pset);
	file.addEntity(site_prop);

	auto pset = file.create<IfcSchema::IfcPropertySet>();
    pset.setGlobalId(guid());
    pset.setOwnerHistory(file.getSingle<IfcSchema::IfcOwnerHistory>());
    pset.setName("Pset_SiteCommon");
    pset.setHasProperties({total_area});

	auto site_prop = file.create<IfcSchema::IfcRelDefinesByProperties>();
    site_prop.setGlobalId(guid());
    site_prop.setOwnerHistory(file.getSingle<IfcSchema::IfcOwnerHistory>());
    site_prop.setRelatedObjects({file.getSingle<IfcSchema::IfcSite>()});
    site_prop.setRelatingPropertyDefinition(pset);
	
	auto ground_reps = file.getSingle<IfcSchema::IfcSite>().Representation().Representations();
    for (auto& rep : ground_reps) {
        rep.setContextOfItems(file.getRepresentationContext("Model"));
	}
	file.add_entity(ground_representation);
	setSurfaceColour(file,ground_representation, 0.15, 0.25, 0.05);

	// According to the Ifc2x3 schema an IfcWallStandardCase needs to have an IfcMaterialLayerSet
	// assigned. Note that this material definition is independent of the surface styles we have 
	// been assigning to the walls already. The surface styles determine the colour in the 
	// '3D viewport' of most applications.
	// Some BIM authoring applications, such as Autodesk Revit, ignore the geometrical representation
	// by and large and construct native walls using the layer thickness and reference line offset 
	// provided here.
#ifdef SCHEMA_IfcMaterial_HAS_Description
	IfcSchema::IfcMaterial* material = new IfcSchema::IfcMaterial("Brick", null, null);
#else
	IfcSchema::IfcMaterial* material = new IfcSchema::IfcMaterial("Brick");
#endif
	IfcSchema::IfcMaterialLayer* layer = new IfcSchema::IfcMaterialLayer(
		material, 
		360, 
		null
#ifdef SCHEMA_IfcMaterialLayer_HAS_Name
		, null
		, null 
		, null
		, null
#endif
	);
	IfcSchema::IfcMaterialLayer::list::ptr layers (new aggregate_of<IfcSchema::IfcMaterialLayer>());
	layers->push(layer);
	IfcSchema::IfcMaterialLayerSet* layer_set = new IfcSchema::IfcMaterialLayerSet(
		layers, 
		"Wall"s
#ifdef SCHEMA_IfcMaterialLayerSet_HAS_Description
		, null
#endif
	);
	IfcSchema::IfcMaterialLayerSetUsage* layer_usage = new IfcSchema::IfcMaterialLayerSetUsage(
		layer_set,
		IfcSchema::IfcLayerSetDirectionEnum::IfcLayerSetDirection_AXIS2,
		IfcSchema::IfcDirectionSenseEnum::IfcDirectionSense_POSITIVE,
		-180
#ifdef SCHEMA_IfcMaterialLayerSetUsage_HAS_ReferenceExtent
		, null
#endif
	);

	IfcSchema::IfcRelAssociatesMaterial* associates_material = new IfcSchema::IfcRelAssociatesMaterial(
		guid(),
		file.getSingle<IfcSchema::IfcOwnerHistory>(), 
		null, 
		null,
#ifdef SCHEMA_HAS_IfcDefinitionSelect
		file.instances_by_type<IfcSchema::IfcWallStandardCase>()->as<IfcSchema::IfcDefinitionSelect>(),
#else
		file.instances_by_type<IfcSchema::IfcWallStandardCase>()->as<IfcSchema::IfcRoot>(),
#endif
		layer_usage);

	auto layer_set = file.create<IfcSchema::IfcMaterialLayerSet>();
    layer_set.setMaterialLayers({layer});
    layer_set.setLayerSetName("Wall");

	auto layer_usage = file.create<IfcSchema::IfcMaterialLayerSetUsage>();
    layer_usage.setForLayerSet(layer_set);
	layer_usage.setDirectionSense(IfcSchema::IfcDirectionSenseEnum::IfcDirectionSense_POSITIVE);
	layer_usage.setLayerSetDirection(IfcSchema::IfcLayerSetDirectionEnum::IfcLayerSetDirection_AXIS1);
    layer_usage.setOffsetFromReferenceLine(-180);

	auto associates_material = file.create<IfcSchema::IfcRelAssociatesMaterial>();
    associates_material.setGlobalId(guid());
	associates_material.setOwnerHistory(file.getSingle<IfcSchema::IfcOwnerHistory>());
	associates_material.setRelatedObjects({south_wall, north_wall, east_wall, west_wall});
    associates_material.setRelatingMaterial(layer_usage);

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
		null, null, null, file.addLocalPlacement(storey_placement, 5050, 1000, 0, 0, 1, 0, 1, 0, 0),
		file.addExtrudedPolyline(stair_points, 1200), null, 2, 2, 0.2, 0.25
#ifdef SCHEMA_IfcStairFlight_HAS_PredefinedType
		, IfcSchema::IfcStairFlightTypeEnum::IfcStairFlightType_STRAIGHT
#endif

	file.addBuildingProduct(stair);
	setSurfaceColour(file, stair.Representation(), footing_colour);

	IfcSchema::IfcOpeningElement* door_opening = new IfcSchema::IfcOpeningElement(guid(), file.getSingle<IfcSchema::IfcOwnerHistory>(),
		null, null, null, file.addLocalPlacement(storey_placement, 5000-180, 2500-900, 0), file.addBox(1000, 1000, 2200), null
#ifdef SCHEMA_IfcOpeningElement_HAS_PredefinedType
		, IfcSchema::IfcOpeningElementTypeEnum::IfcOpeningElementType_OPENING
#endif	
	);
	file.addEntity(door_opening);
	file.addEntity(new IfcSchema::IfcRelVoidsElement(guid(), file.getSingle<IfcSchema::IfcOwnerHistory>(), null, null, east_wall, door_opening));

	// A single shape representation can contain multiple representiation items. This way a product
	// can be a composition of multiple solids. The following door will be composed of four boxes
	// which constitute the door and its frame.
	IfcSchema::IfcDoor* door = new IfcSchema::IfcDoor(guid(), file.getSingle<IfcSchema::IfcOwnerHistory>(), null, null, null,
		file.addLocalPlacement(storey_placement, 4800, 1600, 0, 0, 0, 1, 0, 1, 0), 0, null, 2200, 1000
#ifdef SCHEMA_IfcDoor_HAS_PredefinedType
		, IfcSchema::IfcDoorTypeEnum::IfcDoorType_DOOR
		, IfcSchema::IfcDoorTypeOperationEnum::IfcDoorTypeOperation_SINGLE_SWING_LEFT
		, null
#endif

    door.setRepresentation(file.addBox(80, 80, 2120, IfcSchema::IfcAxis2Placement2D{}, file.addPlacement3d(460, 0, 0)));
    
    auto door_representations = door.Representation().Representations();
    IfcSchema::IfcShapeRepresentation door_body;
	for (auto& rep : door_representations) {
		if (rep.declaration().is(IfcSchema::IfcShapeRepresentation::Class()) && rep.RepresentationIdentifier().value_or("") == "Body") {
            door_body = rep.as<IfcSchema::IfcShapeRepresentation>();
		}
	}

	file.addBox(door_body,  80, 80, 2120, IfcSchema::IfcAxis2Placement2D{}, file.addPlacement3d(-460, 0,   0));
	file.addBox(door_body, 1000, 80,  80, IfcSchema::IfcAxis2Placement2D{}, file.addPlacement3d(   0, 0, 2120));
	file.addBox(door_body, 860, 30, 2120);
	file.addBuildingProduct(door);

#ifdef SCHEMA_HAS_IfcDoorType
	IfcSchema::IfcDoorType* door_type = new IfcSchema::IfcDoorType(guid(), file.getSingle<IfcSchema::IfcOwnerHistory>(), "Door type"s, null, null, null, null, null, null,
		IfcSchema::IfcDoorTypeEnum::IfcDoorType_DOOR, IfcSchema::IfcDoorTypeOperationEnum::IfcDoorTypeOperation_SINGLE_SWING_LEFT, false, null);
	file.addRelatedObject<IfcSchema::IfcRelDefinesByType>(door_type, door);
#elif defined(SCHEMA_HAS_IfcDoorStyle)
	IfcSchema::IfcDoorStyle* door_style = new IfcSchema::IfcDoorStyle(guid(), file.getSingle<IfcSchema::IfcOwnerHistory>(), "Door type"s, null, null, null, null, null,
		IfcSchema::IfcDoorStyleOperationEnum::IfcDoorStyleOperation_SINGLE_SWING_LEFT, IfcSchema::IfcDoorStyleConstructionEnum::IfcDoorStyleConstruction_WOOD, false, false);
	file.addRelatedObject<IfcSchema::IfcRelDefinesByType>(door_style, door);
#endif

	// Surface styles are assigned to representation items, hence there is no real limitation to
	// assign different colours within the same representation. However, some viewers have 
	// difficulties rendering products with representation items with different surface styles. 
	// Therefore we will construct the window as a decomposition of beams and a plate, in which 
	// only the plate will have a transparent material assigned.

	// The window frame will consists of four separate beams.
	// AutoCAD Architecture will create an internal window type for the IfcWindow created.
	// Therefore the OverallWidth and OverallHeight of the window attributes will need to
	// match the bounding box of the representation. Furthermore, the window placement needs
	// to align with the lowerleft corner of the constituent parts.
    std::vector<IfcSchema::IfcShapeRepresentation> frame_representations;
	
	auto horizontal_bar = file.addEmptyRepresentation();
	auto vertical_bar = file.addEmptyRepresentation();
	file.addBox(horizontal_bar, 1860, 90, 90);
	file.addBox(vertical_bar, 90, 90, 1420);

	frame_representations.push_back(horizontal_bar);
	frame_representations.push_back(horizontal_bar); // Add another reference to the horizontal bar created above
	frame_representations.push_back(vertical_bar);
	frame_representations.push_back(vertical_bar); // Add another reference to the vertical bar created above

	// The beams all have the same surface style assigned
	surface_style_t* frame_style = 0;
	for (IfcSchema::IfcShapeRepresentation::list::it i = frame_representations->begin(); i != frame_representations->end(); i += 2) {
		if (frame_style) {
			setSurfaceColour(file, *i, frame_style);
		} else {
			frame_style = setSurfaceColour(file,*i, 0.5, 0.4, 0.3);
		}
		// Because of the duplication the iterator is incremented twice
	}

	// This window will be placed at five locations within the building. A list of placements is 
	// created and is iterated over to create all window instances.
    std::vector<IfcSchema::IfcLocalPlacement> window_placements;
	window_placements.push_back(file.addLocalPlacement(storey_placement, 2*-1770-430-930,   -45, 400));
	window_placements.push_back(file.addLocalPlacement(storey_placement,   -1770-430-930,   -45, 400));
	window_placements.push_back(file.addLocalPlacement(storey_placement,        -430-930,   -45, 400));
	window_placements.push_back(file.addLocalPlacement(storey_placement,        3000-930,   -45, 400));
	window_placements.push_back(file.addLocalPlacement(storey_placement, -4855+45, 885-930, 400, 0, 0, 1, 0, 1, 0));
	
	for (IfcSchema::IfcLocalPlacement::list::it it = window_placements->begin(); it != window_placements->end(); ++it) {
		
		// Create the window at the current location
		IfcSchema::IfcLocalPlacement* place = *it;
		IfcSchema::IfcWindow* window = new IfcSchema::IfcWindow(guid(), file.getSingle<IfcSchema::IfcOwnerHistory>(),
			null, null, null, place, 0, null, 1600, 1860
#ifdef SCHEMA_IfcWindow_HAS_PredefinedType
			, IfcSchema::IfcWindowTypeEnum::IfcWindowType_WINDOW
			, IfcSchema::IfcWindowTypePartitioningEnum::IfcWindowTypePartitioning_SINGLE_PANEL
			, null
#endif
        file.addBuildingProduct(window);		

		// Initialize a list of parts for the window to be composed of
        std::vector<IfcSchema::IfcObjectDefinition> window_parts;

		// The placements for the beams are not shared across the different windows because every
		// beam is placed relative to its parent window entity.
        std::vector<IfcSchema::IfcLocalPlacement> frame_placements;
		frame_placements.push_back(file.addLocalPlacement(storey_placement,  930,45));
		frame_placements.push_back(file.addLocalPlacement(storey_placement,  930, 45, 1510));
		frame_placements.push_back(file.addLocalPlacement(storey_placement, -885+930, 45,  90));
		frame_placements.push_back(file.addLocalPlacement(storey_placement,  885+930, 45,  90));
		
		// Now iterate over the placements and representations of the beam and add them to list of parts
        std::vector<IfcSchema::IfcLocalPlacement>::const_iterator frame_placement;
        std::vector<IfcSchema::IfcShapeRepresentation>::const_iterator frame_representation;
		for (frame_placement = frame_placements.begin(), frame_representation = frame_representations.begin();
			frame_placement != frame_placements.end() && frame_representation != frame_representations.end();
			++frame_placement, ++frame_representation)
		{
			IfcSchema::IfcMember* frame_part = new IfcSchema::IfcMember(guid(), file.getSingle<IfcSchema::IfcOwnerHistory>(),
				null, null, null, *frame_placement, file.addMappedItem(*frame_representation), null
#ifdef SCHEMA_IfcMember_HAS_PredefinedType
				, IfcSchema::IfcMemberTypeEnum::IfcMemberType_MULLION
#endif
			window_parts.push_back(frame_part);
			file.relatePlacements(window, frame_part);
		}

		// Add the glass plate to the list of parts
		IfcSchema::IfcPlate* glass_part = new IfcSchema::IfcPlate(guid(), file.getSingle<IfcSchema::IfcOwnerHistory>(), null,
			null, null, file.addLocalPlacement(storey_placement, 930, 45, 90), file.addBox(1680, 10, 1420), null
#ifdef SCHEMA_IfcPlate_HAS_PredefinedType
			, IfcSchema::IfcPlateTypeEnum::IfcPlateType_SHEET
#endif

        window_parts.push_back(glass_part);
		file.relatePlacements(window, glass_part);
		setSurfaceColour(file, glass_part.Representation(), 0.6, 0.7, 0.75, 0.1);
		
		// Now create a decomposition relation between the window and the parts. Most viewers and authoring
		// tools will consider the window a single entity that can be selected as a whole.
        {

            auto rel = file.create<IfcSchema::IfcRelAggregates>();
            rel.setGlobalId(guid());
            rel.setOwnerHistory(file.getSingle<IfcSchema::IfcOwnerHistory>());
            rel.setRelatingObject(window);
            rel.setRelatedObjects(window_parts);
        }
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
	shape = BRepBuilderAPI_MakeFace(surf, Precision::Confusion());
#endif
}
