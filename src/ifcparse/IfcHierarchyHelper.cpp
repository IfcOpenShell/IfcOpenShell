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

/********************************************************************************
 *                                                                              *
 * This class is a subclass of the regular IfcFile class that implements        *
 * several convenience functions for creating geometrical representations and   *
 * spatial containers.                                                          *
 *                                                                              *
 ********************************************************************************/

#include <time.h>

#include "../ifcparse/IfcHierarchyHelper.h"
	
IfcSchema::IfcAxis2Placement3D* IfcHierarchyHelper::addPlacement3d(
	double ox, double oy, double oz,
	double zx, double zy, double zz,
	double xx, double xy, double xz) 
{
		IfcSchema::IfcDirection* x = addTriplet<IfcSchema::IfcDirection>(xx, xy, xz);
		IfcSchema::IfcDirection* z = addTriplet<IfcSchema::IfcDirection>(zx, zy, zz);
		IfcSchema::IfcCartesianPoint* o = addTriplet<IfcSchema::IfcCartesianPoint>(ox, oy, oz);
		IfcSchema::IfcAxis2Placement3D* p3d = new IfcSchema::IfcAxis2Placement3D(o, z, x);
		addEntity(p3d);
		return p3d;
}

IfcSchema::IfcAxis2Placement2D* IfcHierarchyHelper::addPlacement2d(
	double ox, double oy,
	double xx, double xy) 
{
		IfcSchema::IfcDirection* x = addDoublet<IfcSchema::IfcDirection>(xx, xy);
		IfcSchema::IfcCartesianPoint* o = addDoublet<IfcSchema::IfcCartesianPoint>(ox, oy);
		IfcSchema::IfcAxis2Placement2D* p2d = new IfcSchema::IfcAxis2Placement2D(o, x);
		addEntity(p2d);
		return p2d;
}

IfcSchema::IfcLocalPlacement* IfcHierarchyHelper::addLocalPlacement(IfcSchema::IfcObjectPlacement* parent,
	double ox, double oy, double oz,
	double zx, double zy, double zz,
	double xx, double xy, double xz) 
{
		IfcSchema::IfcLocalPlacement* lp = new IfcSchema::IfcLocalPlacement(parent, 
			addPlacement3d(ox, oy, oz, zx, zy, zz, xx, xy, xz));

		addEntity(lp);
		return lp;
}

IfcSchema::IfcOwnerHistory* IfcHierarchyHelper::addOwnerHistory() {
	IfcSchema::IfcPerson* person = new IfcSchema::IfcPerson(boost::none, boost::none, std::string(""), 
		boost::none, boost::none, boost::none, boost::none, boost::none);

	IfcSchema::IfcOrganization* organization = new IfcSchema::IfcOrganization(boost::none, 
		"IfcOpenShell", boost::none, boost::none, boost::none);

	IfcSchema::IfcPersonAndOrganization* person_and_org = new IfcSchema::IfcPersonAndOrganization(person, organization, boost::none);
	IfcSchema::IfcApplication* application = new IfcSchema::IfcApplication(organization, 
		IFCOPENSHELL_VERSION, "IfcOpenShell", "IfcOpenShell");

	int timestamp = (int) time(0);
	IfcSchema::IfcOwnerHistory* owner_hist = new IfcSchema::IfcOwnerHistory(person_and_org, application, 
		boost::none, IfcSchema::IfcChangeActionEnum::IfcChangeAction_ADDED, timestamp, person_and_org, application, timestamp);

	addEntity(person);
	addEntity(organization);
	addEntity(person_and_org);
	addEntity(application);
	addEntity(owner_hist);

	return owner_hist;
}
	
IfcSchema::IfcProject* IfcHierarchyHelper::addProject(IfcSchema::IfcOwnerHistory* owner_hist) {
	IfcSchema::IfcRepresentationContext::list::ptr rep_contexts (new IfcSchema::IfcRepresentationContext::list);

	IfcEntityList::ptr units (new IfcEntityList);
	IfcSchema::IfcDimensionalExponents* dimexp = new IfcSchema::IfcDimensionalExponents(0, 0, 0, 0, 0, 0, 0);
	IfcSchema::IfcSIUnit* unit1 = new IfcSchema::IfcSIUnit(IfcSchema::IfcUnitEnum::IfcUnit_LENGTHUNIT, 
		IfcSchema::IfcSIPrefix::IfcSIPrefix_MILLI, IfcSchema::IfcSIUnitName::IfcSIUnitName_METRE);
	IfcSchema::IfcSIUnit* unit2a = new IfcSchema::IfcSIUnit(IfcSchema::IfcUnitEnum::IfcUnit_PLANEANGLEUNIT, 
		boost::none, IfcSchema::IfcSIUnitName::IfcSIUnitName_RADIAN);
	IfcSchema::IfcMeasureWithUnit* unit2b = new IfcSchema::IfcMeasureWithUnit(
		new IfcSchema::IfcPlaneAngleMeasure(0.017453293), unit2a);
	IfcSchema::IfcConversionBasedUnit* unit2 = new IfcSchema::IfcConversionBasedUnit(dimexp, 
		IfcSchema::IfcUnitEnum::IfcUnit_PLANEANGLEUNIT, "Degrees", unit2b);

	units->push(unit1);
	units->push(unit2);

	IfcSchema::IfcUnitAssignment* unit_assignment = new IfcSchema::IfcUnitAssignment(units);

	IfcSchema::IfcProject* project = new IfcSchema::IfcProject(IfcParse::IfcGlobalId(), owner_hist, boost::none, boost::none, 
		boost::none, boost::none, boost::none, rep_contexts, unit_assignment);

	addEntity(dimexp);
	addEntity(unit1);
	addEntity(unit2a);
	addEntity(unit2b);
	addEntity(unit2);
	addEntity(unit_assignment);
	addEntity(project);

	return project;
}

void IfcHierarchyHelper::relatePlacements(IfcSchema::IfcProduct* parent, IfcSchema::IfcProduct* product) {
	IfcSchema::IfcObjectPlacement* place = product->hasObjectPlacement() ? product->ObjectPlacement() : 0;
	if (place && place->is(IfcSchema::Type::IfcLocalPlacement)) {
		IfcSchema::IfcLocalPlacement* local_place = (IfcSchema::IfcLocalPlacement*) place;
		if (parent->hasObjectPlacement()) {
			local_place->setPlacementRelTo(parent->ObjectPlacement());
		}
	}
}
	
IfcSchema::IfcSite* IfcHierarchyHelper::addSite(IfcSchema::IfcProject* proj, IfcSchema::IfcOwnerHistory* owner_hist) {
	if (! owner_hist) {
		owner_hist = getSingle<IfcSchema::IfcOwnerHistory>();
	}
	if (! owner_hist) {
		owner_hist = addOwnerHistory();
	}
	if (! proj) {
		proj = getSingle<IfcSchema::IfcProject>();
	}
	if (! proj) {
		proj = addProject(owner_hist);
	}

	IfcSchema::IfcSite* site = new IfcSchema::IfcSite(IfcParse::IfcGlobalId(), owner_hist, boost::none, 
		boost::none, boost::none, addLocalPlacement(), 0, boost::none, 
		IfcSchema::IfcElementCompositionEnum::IfcElementComposition_ELEMENT, 
		boost::none, boost::none, boost::none, boost::none, 0);

	addEntity(site);
	addRelatedObject<IfcSchema::IfcRelAggregates>(proj, site);
	return site;
}
	
IfcSchema::IfcBuilding* IfcHierarchyHelper::addBuilding(IfcSchema::IfcSite* site, IfcSchema::IfcOwnerHistory* owner_hist) {
	if (! owner_hist) {
		owner_hist = getSingle<IfcSchema::IfcOwnerHistory>();
	}
	if (! owner_hist) {
		owner_hist = addOwnerHistory();
	}
	if (! site) {
		site = getSingle<IfcSchema::IfcSite>();
	}
	if (! site) {
		site = addSite(0, owner_hist);
	}
	IfcSchema::IfcBuilding* building = new IfcSchema::IfcBuilding(IfcParse::IfcGlobalId(), owner_hist, boost::none, boost::none, boost::none, 
		addLocalPlacement(), 0, boost::none, IfcSchema::IfcElementCompositionEnum::IfcElementComposition_ELEMENT, 
		boost::none, boost::none, 0);

	addEntity(building);
	addRelatedObject<IfcSchema::IfcRelAggregates>(site, building);
	relatePlacements(site, building);

	return building;
}

IfcSchema::IfcBuildingStorey* IfcHierarchyHelper::addBuildingStorey(IfcSchema::IfcBuilding* building, 
	IfcSchema::IfcOwnerHistory* owner_hist) 
{
	if (! owner_hist) {
		owner_hist = getSingle<IfcSchema::IfcOwnerHistory>();
	}
	if (! owner_hist) {
		owner_hist = addOwnerHistory();
	}
	if (! building) {
		building = getSingle<IfcSchema::IfcBuilding>();
	}
	if (! building) {
		building = addBuilding(0, owner_hist);
	}
	IfcSchema::IfcBuildingStorey* storey = new IfcSchema::IfcBuildingStorey(IfcParse::IfcGlobalId(), 
		owner_hist, boost::none, boost::none, boost::none, addLocalPlacement(), 0, boost::none, 
		IfcSchema::IfcElementCompositionEnum::IfcElementComposition_ELEMENT, boost::none);

	addEntity(storey);
	addRelatedObject<IfcSchema::IfcRelAggregates>(building, storey);
	relatePlacements(building, storey);

	return storey;
}

IfcSchema::IfcBuildingStorey* IfcHierarchyHelper::addBuildingProduct(IfcSchema::IfcProduct* product, 
	IfcSchema::IfcBuildingStorey* storey, IfcSchema::IfcOwnerHistory* owner_hist) 
{
	if (! owner_hist) {
		owner_hist = getSingle<IfcSchema::IfcOwnerHistory>();
	}
	if (! owner_hist) {
		owner_hist = addOwnerHistory();
	}
	if (! storey) {
		storey = getSingle<IfcSchema::IfcBuildingStorey>();
	}
	if (! storey) {
		storey = addBuildingStorey(0, owner_hist);
	}
	addEntity(product);
	// CV-2x3-158: Don't add decompositions directly to a building storey
	bool is_decomposition = false;
#ifdef USE_IFC4
	IfcSchema::IfcRelAggregates::list::ptr decomposes = product->Decomposes();
	for (IfcSchema::IfcRelAggregates::list::it it = decomposes->begin(); it != decomposes->end(); ++it) {
#else
	IfcSchema::IfcRelDecomposes::list::ptr decomposes = product->Decomposes();
	for (IfcSchema::IfcRelDecomposes::list::it it = decomposes->begin(); it != decomposes->end(); ++it) {
#endif
		if ((*it)->RelatingObject() != product) {
			is_decomposition = true;
			break;
		}
	}
	if (!is_decomposition) {
		addRelatedObject<IfcSchema::IfcRelContainedInSpatialStructure>(storey, product);
		relatePlacements(storey, product);
	}
	return storey;
}

void IfcHierarchyHelper::addExtrudedPolyline(IfcSchema::IfcShapeRepresentation* rep, const std::vector<std::pair<double, double> >& points, double h, 
	IfcSchema::IfcAxis2Placement2D* place, IfcSchema::IfcAxis2Placement3D* place2, 
	IfcSchema::IfcDirection* dir, IfcSchema::IfcRepresentationContext* context) 
{
	IfcSchema::IfcCartesianPoint::list::ptr cartesian_points (new IfcSchema::IfcCartesianPoint::list);
	for (std::vector<std::pair<double, double> >::const_iterator i = points.begin(); i != points.end(); ++i) {
		cartesian_points->push(addDoublet<IfcSchema::IfcCartesianPoint>(i->first, i->second));
	}
	if (cartesian_points->size()) cartesian_points->push(*cartesian_points->begin());
	IfcSchema::IfcPolyline* line = new IfcSchema::IfcPolyline(cartesian_points);
	IfcSchema::IfcArbitraryClosedProfileDef* profile = new IfcSchema::IfcArbitraryClosedProfileDef(
		IfcSchema::IfcProfileTypeEnum::IfcProfileType_AREA, boost::none, line);

	IfcSchema::IfcExtrudedAreaSolid* solid = new IfcSchema::IfcExtrudedAreaSolid(
		profile, place2 ? place2 : addPlacement3d(), dir ? dir : addTriplet<IfcSchema::IfcDirection>(0, 0, 1), h);

	IfcSchema::IfcRepresentationItem::list::ptr items = rep->Items();
	items->push(solid);
	rep->setItems(items);

	addEntity(line);
	addEntity(profile);
	addEntity(solid);
}

IfcSchema::IfcProductDefinitionShape* IfcHierarchyHelper::addExtrudedPolyline(const std::vector<std::pair<double, double> >& points, double h, 
	IfcSchema::IfcAxis2Placement2D* place, IfcSchema::IfcAxis2Placement3D* place2, IfcSchema::IfcDirection* dir, 
	IfcSchema::IfcRepresentationContext* context) 
{
	IfcSchema::IfcRepresentation::list::ptr reps (new IfcSchema::IfcRepresentation::list);
	IfcSchema::IfcRepresentationItem::list::ptr items (new IfcSchema::IfcRepresentationItem::list);
	IfcSchema::IfcShapeRepresentation* rep = new IfcSchema::IfcShapeRepresentation(context 
		? context 
		: getRepresentationContext("Model"), std::string("Body"), std::string("SweptSolid"), items);
	reps->push(rep);
	IfcSchema::IfcProductDefinitionShape* shape = new IfcSchema::IfcProductDefinitionShape(boost::none, boost::none, reps);
	addEntity(rep);
	addEntity(shape);
	addExtrudedPolyline(rep, points, h, place, place2, dir, context);

	return shape;
}

void IfcHierarchyHelper::addBox(IfcSchema::IfcShapeRepresentation* rep, double w, double d, double h, 
	IfcSchema::IfcAxis2Placement2D* place, IfcSchema::IfcAxis2Placement3D* place2, 
	IfcSchema::IfcDirection* dir, IfcSchema::IfcRepresentationContext* context) 
{
	if (false) {
		IfcSchema::IfcRectangleProfileDef* profile = new IfcSchema::IfcRectangleProfileDef(
			IfcSchema::IfcProfileTypeEnum::IfcProfileType_AREA, boost::none, place ? place : addPlacement2d(), w, d);
		IfcSchema::IfcExtrudedAreaSolid* solid = new IfcSchema::IfcExtrudedAreaSolid(profile, 
			place2 ? place2 : addPlacement3d(), dir ? dir : addTriplet<IfcSchema::IfcDirection>(0, 0, 1), h);

		addEntity(profile);
		addEntity(solid);
		IfcSchema::IfcRepresentationItem::list::ptr items = rep->Items();
		items->push(solid);
		rep->setItems(items);
	} else {
		std::vector<std::pair<double, double> > points;
		points.push_back(std::pair<double, double>(-w/2, -d/2));
		points.push_back(std::pair<double, double>(w/2, -d/2));
		points.push_back(std::pair<double, double>(w/2, d/2));
		points.push_back(std::pair<double, double>(-w/2, d/2));
		// The call to addExtrudedPolyline() closes the polyline
		addExtrudedPolyline(rep, points, h, place, place2, dir, context);
	}
}

void IfcHierarchyHelper::addAxis(IfcSchema::IfcShapeRepresentation* rep, double l, IfcSchema::IfcRepresentationContext* context) {
	IfcSchema::IfcCartesianPoint* p1 = addDoublet<IfcSchema::IfcCartesianPoint>(-l / 2., 0.);
	IfcSchema::IfcCartesianPoint* p2 = addDoublet<IfcSchema::IfcCartesianPoint>(+l / 2., 0.);
	IfcSchema::IfcCartesianPoint::list::ptr pts(new IfcSchema::IfcCartesianPoint::list);
	pts->push(p1); pts->push(p2);
	IfcSchema::IfcPolyline* poly = new IfcSchema::IfcPolyline(pts);
	addEntity(poly);
	
	IfcSchema::IfcRepresentationItem::list::ptr items = rep->Items();
	items->push(poly);
	rep->setItems(items);
}

IfcSchema::IfcProductDefinitionShape* IfcHierarchyHelper::addBox(double w, double d, double h, IfcSchema::IfcAxis2Placement2D* place, 
	IfcSchema::IfcAxis2Placement3D* place2, IfcSchema::IfcDirection* dir, IfcSchema::IfcRepresentationContext* context) 
{
	IfcSchema::IfcRepresentation::list::ptr reps (new IfcSchema::IfcRepresentation::list);
	IfcSchema::IfcRepresentationItem::list::ptr items (new IfcSchema::IfcRepresentationItem::list);		
	IfcSchema::IfcShapeRepresentation* rep = new IfcSchema::IfcShapeRepresentation(
		context ? context : getRepresentationContext("Model"), std::string("Body"), std::string("SweptSolid"), items);
	reps->push(rep);
	IfcSchema::IfcProductDefinitionShape* shape = new IfcSchema::IfcProductDefinitionShape(boost::none, boost::none, reps);
	addEntity(rep);
	addEntity(shape);
	addBox(rep, w, d, h, place, place2, dir, context);
	return shape;
}

IfcSchema::IfcProductDefinitionShape* IfcHierarchyHelper::addAxisBox(double w, double d, double h, IfcSchema::IfcRepresentationContext* context) 
{
	IfcSchema::IfcRepresentation::list::ptr reps(new IfcSchema::IfcRepresentation::list);
	IfcSchema::IfcRepresentationItem::list::ptr body_items(new IfcSchema::IfcRepresentationItem::list);
	IfcSchema::IfcRepresentationItem::list::ptr axis_items(new IfcSchema::IfcRepresentationItem::list);
	IfcSchema::IfcShapeRepresentation* body_rep = new IfcSchema::IfcShapeRepresentation(
		context ? context : getRepresentationContext("Model"), std::string("Body"), std::string("SweptSolid"), body_items);

	IfcSchema::IfcShapeRepresentation* axis_rep = new IfcSchema::IfcShapeRepresentation(
		context ? context : getRepresentationContext("Plan"), std::string("Axis"), std::string("Curve2D"), axis_items);

	reps->push(axis_rep);
	reps->push(body_rep);

	IfcSchema::IfcProductDefinitionShape* shape = new IfcSchema::IfcProductDefinitionShape(boost::none, boost::none, reps);
	addEntity(shape);
	addEntity(body_rep);
	addBox(body_rep, w, d, h, 0, 0, 0, context);
	addEntity(axis_rep);
	addAxis(axis_rep, w);
	
	return shape;
}

void IfcHierarchyHelper::clipRepresentation(IfcSchema::IfcProductRepresentation* shape, 
	IfcSchema::IfcAxis2Placement3D* place, bool agree) 
{
	IfcSchema::IfcRepresentation::list::ptr reps = shape->Representations();
	for (IfcSchema::IfcRepresentation::list::it j = reps->begin(); j != reps->end(); ++j) {
		clipRepresentation(*j, place, agree);
	}
}

void IfcHierarchyHelper::clipRepresentation(IfcSchema::IfcRepresentation* rep, 
	IfcSchema::IfcAxis2Placement3D* place, bool agree) 
{
	if (rep->RepresentationIdentifier() != "Body") return;
	IfcSchema::IfcPlane* plane = new IfcSchema::IfcPlane(place);
	IfcSchema::IfcHalfSpaceSolid* half_space = new IfcSchema::IfcHalfSpaceSolid(plane, agree);
	addEntity(plane);
	addEntity(half_space);
	rep->setRepresentationType("Clipping");		
	IfcSchema::IfcRepresentationItem::list::ptr items = rep->Items();
	IfcSchema::IfcRepresentationItem::list::ptr new_items (new IfcSchema::IfcRepresentationItem::list);
	for (IfcSchema::IfcRepresentationItem::list::it i = items->begin(); i != items->end(); ++i) {
		IfcSchema::IfcRepresentationItem* item = *i;
		IfcSchema::IfcBooleanClippingResult* clip = new IfcSchema::IfcBooleanClippingResult(
			IfcSchema::IfcBooleanOperator::IfcBooleanOperator_DIFFERENCE, item, half_space);
		addEntity(clip);
		new_items->push(clip);
	}
	rep->setItems(new_items);
}

IfcSchema::IfcPresentationStyleAssignment* IfcHierarchyHelper::addStyleAssignment(double r, double g, double b, double a) {
	IfcSchema::IfcColourRgb* colour = new IfcSchema::IfcColourRgb(boost::none, r, g, b);
	IfcSchema::IfcSurfaceStyleRendering* rendering = a == 1.0
		? new IfcSchema::IfcSurfaceStyleRendering(colour, boost::none, 0, 0, 0, 0, 
			0, 0, IfcSchema::IfcReflectanceMethodEnum::IfcReflectanceMethod_FLAT)
		: new IfcSchema::IfcSurfaceStyleRendering(colour, 1.0-a, 0, 0, 0, 0, 
			0, 0, IfcSchema::IfcReflectanceMethodEnum::IfcReflectanceMethod_FLAT);

	IfcEntityList::ptr styles(new IfcEntityList());
	styles->push(rendering);
	IfcSchema::IfcSurfaceStyle* surface_style = new IfcSchema::IfcSurfaceStyle(
		boost::none, IfcSchema::IfcSurfaceSide::IfcSurfaceSide_BOTH, styles);
	IfcEntityList::ptr surface_styles(new IfcEntityList());
	surface_styles->push(surface_style);
	IfcSchema::IfcPresentationStyleAssignment* style_assignment = 
		new IfcSchema::IfcPresentationStyleAssignment(surface_styles);
	addEntity(colour);
	addEntity(rendering);
	addEntity(surface_style);
	addEntity(style_assignment);
	return style_assignment;
}

IfcSchema::IfcPresentationStyleAssignment* IfcHierarchyHelper::setSurfaceColour(
	IfcSchema::IfcProductRepresentation* shape, double r, double g, double b, double a) 
{
	IfcSchema::IfcPresentationStyleAssignment* style_assignment = addStyleAssignment(r, g, b, a);
	setSurfaceColour(shape, style_assignment);
	return style_assignment;
}

IfcSchema::IfcPresentationStyleAssignment* IfcHierarchyHelper::setSurfaceColour(
	IfcSchema::IfcRepresentation* shape, double r, double g, double b, double a) 
{
	IfcSchema::IfcPresentationStyleAssignment* style_assignment = addStyleAssignment(r, g, b, a);
	setSurfaceColour(shape, style_assignment);
	return style_assignment;
}

void IfcHierarchyHelper::setSurfaceColour(IfcSchema::IfcProductRepresentation* shape, 
	IfcSchema::IfcPresentationStyleAssignment* style_assignment) 
{
	IfcSchema::IfcRepresentation::list::ptr reps = shape->Representations();
	for (IfcSchema::IfcRepresentation::list::it j = reps->begin(); j != reps->end(); ++j) {
		setSurfaceColour(*j, style_assignment);
	}
}

void IfcHierarchyHelper::setSurfaceColour(IfcSchema::IfcRepresentation* rep, 
	IfcSchema::IfcPresentationStyleAssignment* style_assignment) 
{
#ifdef USE_IFC4 
	IfcEntityList::ptr style_assignments (new IfcEntityList);
#else
	IfcSchema::IfcPresentationStyleAssignment::list::ptr style_assignments (new IfcSchema::IfcPresentationStyleAssignment::list);
#endif
	style_assignments->push(style_assignment);
	IfcSchema::IfcRepresentationItem::list::ptr items = rep->Items();
	for (IfcSchema::IfcRepresentationItem::list::it i = items->begin(); i != items->end(); ++i) {
		IfcSchema::IfcRepresentationItem* item = *i;
		IfcSchema::IfcStyledItem* styled_item = new IfcSchema::IfcStyledItem(item, style_assignments, boost::none);
		addEntity(styled_item);
	}
}

IfcSchema::IfcProductDefinitionShape* IfcHierarchyHelper::addMappedItem(
	IfcSchema::IfcShapeRepresentation* rep, 
	IfcSchema::IfcCartesianTransformationOperator3D* transform,
	IfcSchema::IfcProductDefinitionShape* def)
{
	IfcSchema::IfcRepresentationMap::list::ptr maps = rep->RepresentationMap();
	IfcSchema::IfcRepresentationMap* map;
	if (maps->size() == 1) {
		map = *maps->begin();
	} else {
		map = new IfcSchema::IfcRepresentationMap(addPlacement3d(), rep);
		addEntity(map);
	}

	IfcSchema::IfcRepresentation::list::ptr representations(new IfcSchema::IfcRepresentation::list);
	if (def) representations = def->Representations();

	if (!transform) {
		transform = new IfcSchema::IfcCartesianTransformationOperator3D(0, 0, addTriplet<IfcSchema::IfcCartesianPoint>(0,0,0), boost::none, 0);
		addEntity(transform);
	}
	IfcSchema::IfcMappedItem* item = new IfcSchema::IfcMappedItem(map, transform);
	IfcSchema::IfcRepresentationItem::list::ptr items(new IfcSchema::IfcRepresentationItem::list);
	items->push(item);
	IfcSchema::IfcRepresentation* new_rep = new IfcSchema::IfcShapeRepresentation(rep->ContextOfItems(), boost::none, std::string("MappedRepresentation"), items);
	if (rep->hasRepresentationIdentifier()) {
		new_rep->setRepresentationIdentifier(rep->RepresentationIdentifier());
	}	
	addEntity(item);
	addEntity(new_rep);
	representations->push(new_rep);
	if (!def) {
		def = new IfcSchema::IfcProductDefinitionShape(boost::none, boost::none, representations);
		addEntity(def);
	} else {
		def->setRepresentations(representations);
	}
	return def;
}

IfcSchema::IfcProductDefinitionShape* IfcHierarchyHelper::addMappedItem(
	IfcSchema::IfcShapeRepresentation::list::ptr reps, 
	IfcSchema::IfcCartesianTransformationOperator3D* transform)
{
	IfcSchema::IfcProductDefinitionShape* def = 0;
	for (IfcSchema::IfcShapeRepresentation::list::it it = reps->begin(); it != reps->end(); ++it) {
		def = addMappedItem(*it, transform, def);
	}
	return def;
}

IfcSchema::IfcShapeRepresentation* IfcHierarchyHelper::addEmptyRepresentation(const std::string& repid, const std::string& reptype) {
	IfcSchema::IfcRepresentationItem::list::ptr items(new IfcSchema::IfcRepresentationItem::list);
	IfcSchema::IfcShapeRepresentation* shape_rep = new IfcSchema::IfcShapeRepresentation(getRepresentationContext(reptype == "Curve2D" ? "Plan" : "Model"), repid, reptype, items);
	addEntity(shape_rep);
	return shape_rep;
}

IfcSchema::IfcGeometricRepresentationContext* IfcHierarchyHelper::getRepresentationContext(const std::string& s) {
	std::map<std::string, IfcSchema::IfcGeometricRepresentationContext*>::const_iterator it = contexts.find(s);
	if (it != contexts.end()) return it->second;
	else {
		IfcSchema::IfcProject* project = getSingle<IfcSchema::IfcProject>();
		IfcSchema::IfcRepresentationContext::list::ptr project_contexts = project->RepresentationContexts();
		IfcSchema::IfcGeometricRepresentationContext* context = new IfcSchema::IfcGeometricRepresentationContext(
			boost::none, s, 3, 1e-5, addPlacement3d(), addDoublet<IfcSchema::IfcDirection>(0, 1));
		addEntity(context);
		project_contexts->push(context);
		project->setRepresentationContexts(project_contexts);
		return contexts[s] = context;
	}
}