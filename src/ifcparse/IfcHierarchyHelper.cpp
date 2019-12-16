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

template <typename Schema>
typename Schema::IfcAxis2Placement3D* IfcHierarchyHelper<Schema>::addPlacement3d(
	double ox, double oy, double oz,
	double zx, double zy, double zz,
	double xx, double xy, double xz) 
{
		typename Schema::IfcDirection* x = addTriplet<typename Schema::IfcDirection>(xx, xy, xz);
		typename Schema::IfcDirection* z = addTriplet<typename Schema::IfcDirection>(zx, zy, zz);
		typename Schema::IfcCartesianPoint* o = addTriplet<typename Schema::IfcCartesianPoint>(ox, oy, oz);
		typename Schema::IfcAxis2Placement3D* p3d = new typename Schema::IfcAxis2Placement3D(o, z, x);
		addEntity(p3d);
		return p3d;
}

template <typename Schema>
typename Schema::IfcAxis2Placement2D* IfcHierarchyHelper<Schema>::addPlacement2d(
	double ox, double oy,
	double xx, double xy) 
{
		typename Schema::IfcDirection* x = addDoublet<typename Schema::IfcDirection>(xx, xy);
		typename Schema::IfcCartesianPoint* o = addDoublet<typename Schema::IfcCartesianPoint>(ox, oy);
		typename Schema::IfcAxis2Placement2D* p2d = new typename Schema::IfcAxis2Placement2D(o, x);
		addEntity(p2d);
		return p2d;
}

template <typename Schema>
typename Schema::IfcLocalPlacement* IfcHierarchyHelper<Schema>::addLocalPlacement(typename Schema::IfcObjectPlacement* parent,
	double ox, double oy, double oz,
	double zx, double zy, double zz,
	double xx, double xy, double xz) 
{
		typename Schema::IfcLocalPlacement* lp = new typename Schema::IfcLocalPlacement(parent, 
			addPlacement3d(ox, oy, oz, zx, zy, zz, xx, xy, xz));

		addEntity(lp);
		return lp;
}

template <typename Schema>
typename Schema::IfcOwnerHistory* IfcHierarchyHelper<Schema>::addOwnerHistory() {
	typename Schema::IfcPerson* person = new typename Schema::IfcPerson(boost::none, boost::none, std::string(""), 
		boost::none, boost::none, boost::none, boost::none, boost::none);

	typename Schema::IfcOrganization* organization = new typename Schema::IfcOrganization(boost::none, 
		"IfcOpenShell", boost::none, boost::none, boost::none);

	typename Schema::IfcPersonAndOrganization* person_and_org = new typename Schema::IfcPersonAndOrganization(person, organization, boost::none);
	typename Schema::IfcApplication* application = new typename Schema::IfcApplication(organization, 
		IFCOPENSHELL_VERSION, "IfcOpenShell", "IfcOpenShell");

	int timestamp = (int) time(0);
	typename Schema::IfcOwnerHistory* owner_hist = new typename Schema::IfcOwnerHistory(person_and_org, application, 
		boost::none, Schema::IfcChangeActionEnum::IfcChangeAction_ADDED, timestamp, person_and_org, application, timestamp);

	addEntity(person);
	addEntity(organization);
	addEntity(person_and_org);
	addEntity(application);
	addEntity(owner_hist);

	return owner_hist;
}

template <typename Schema>
typename Schema::IfcProject* IfcHierarchyHelper<Schema>::addProject(typename Schema::IfcOwnerHistory* owner_hist) {
	typename Schema::IfcRepresentationContext::list::ptr rep_contexts (new typename Schema::IfcRepresentationContext::list);

	IfcEntityList::ptr units (new IfcEntityList);
	typename Schema::IfcDimensionalExponents* dimexp = new typename Schema::IfcDimensionalExponents(0, 0, 0, 0, 0, 0, 0);
	typename Schema::IfcSIUnit* unit1 = new typename Schema::IfcSIUnit(Schema::IfcUnitEnum::IfcUnit_LENGTHUNIT, 
		Schema::IfcSIPrefix::IfcSIPrefix_MILLI, Schema::IfcSIUnitName::IfcSIUnitName_METRE);
	typename Schema::IfcSIUnit* unit2a = new typename Schema::IfcSIUnit(Schema::IfcUnitEnum::IfcUnit_PLANEANGLEUNIT, 
		boost::none, Schema::IfcSIUnitName::IfcSIUnitName_RADIAN);
	typename Schema::IfcMeasureWithUnit* unit2b = new typename Schema::IfcMeasureWithUnit(
		new typename Schema::IfcPlaneAngleMeasure(0.017453293), unit2a);
	typename Schema::IfcConversionBasedUnit* unit2 = new typename Schema::IfcConversionBasedUnit(dimexp, 
		Schema::IfcUnitEnum::IfcUnit_PLANEANGLEUNIT, "Degrees", unit2b);

	units->push(unit1);
	units->push(unit2);

	typename Schema::IfcUnitAssignment* unit_assignment = new typename Schema::IfcUnitAssignment(units);

	typename Schema::IfcProject* project = new typename Schema::IfcProject(IfcParse::IfcGlobalId(), owner_hist, boost::none, boost::none, 
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

template <typename Schema>
void IfcHierarchyHelper<Schema>::relatePlacements(typename Schema::IfcProduct* parent, typename Schema::IfcProduct* product) {
	typename Schema::IfcObjectPlacement* place = product->hasObjectPlacement() ? product->ObjectPlacement() : 0;
	if (place && place->declaration().is(Schema::IfcLocalPlacement::Class())) {
		typename Schema::IfcLocalPlacement* local_place = (typename Schema::IfcLocalPlacement*) place;
		if (parent->hasObjectPlacement()) {
			local_place->setPlacementRelTo(parent->ObjectPlacement());
		}
	}
}

template <typename Schema>
typename Schema::IfcSite* IfcHierarchyHelper<Schema>::addSite(typename Schema::IfcProject* proj, typename Schema::IfcOwnerHistory* owner_hist) {
	if (! owner_hist) {
		owner_hist = getSingle<typename Schema::IfcOwnerHistory>();
	}
	if (! owner_hist) {
		owner_hist = addOwnerHistory();
	}
	if (! proj) {
		proj = getSingle<typename Schema::IfcProject>();
	}
	if (! proj) {
		proj = addProject(owner_hist);
	}

	typename Schema::IfcSite* site = new typename Schema::IfcSite(IfcParse::IfcGlobalId(), owner_hist, boost::none, 
		boost::none, boost::none, addLocalPlacement(), 0, boost::none, 
		Schema::IfcElementCompositionEnum::IfcElementComposition_ELEMENT, 
		boost::none, boost::none, boost::none, boost::none, 0);

	addEntity(site);
	addRelatedObject<typename Schema::IfcRelAggregates>(proj, site);
	return site;
}

template <typename Schema>
typename Schema::IfcBuilding* IfcHierarchyHelper<Schema>::addBuilding(typename Schema::IfcSite* site, typename Schema::IfcOwnerHistory* owner_hist) {
	if (! owner_hist) {
		owner_hist = getSingle<typename Schema::IfcOwnerHistory>();
	}
	if (! owner_hist) {
		owner_hist = addOwnerHistory();
	}
	if (! site) {
		site = getSingle<typename Schema::IfcSite>();
	}
	if (! site) {
		site = addSite(0, owner_hist);
	}
	typename Schema::IfcBuilding* building = new typename Schema::IfcBuilding(IfcParse::IfcGlobalId(), owner_hist, boost::none, boost::none, boost::none, 
		addLocalPlacement(), 0, boost::none, Schema::IfcElementCompositionEnum::IfcElementComposition_ELEMENT, 
		boost::none, boost::none, 0);

	addEntity(building);
	addRelatedObject<typename Schema::IfcRelAggregates>(site, building);
	relatePlacements(site, building);

	return building;
}

template <typename Schema>
typename Schema::IfcBuildingStorey* IfcHierarchyHelper<Schema>::addBuildingStorey(typename Schema::IfcBuilding* building, 
	typename Schema::IfcOwnerHistory* owner_hist) 
{
	if (! owner_hist) {
		owner_hist = getSingle<typename Schema::IfcOwnerHistory>();
	}
	if (! owner_hist) {
		owner_hist = addOwnerHistory();
	}
	if (! building) {
		building = getSingle<typename Schema::IfcBuilding>();
	}
	if (! building) {
		building = addBuilding(0, owner_hist);
	}
	typename Schema::IfcBuildingStorey* storey = new typename Schema::IfcBuildingStorey(IfcParse::IfcGlobalId(), 
		owner_hist, boost::none, boost::none, boost::none, addLocalPlacement(), 0, boost::none, 
		Schema::IfcElementCompositionEnum::IfcElementComposition_ELEMENT, boost::none);

	addEntity(storey);
	addRelatedObject<typename Schema::IfcRelAggregates>(building, storey);
	relatePlacements(building, storey);

	return storey;
}

template <typename Schema>
typename Schema::IfcBuildingStorey* IfcHierarchyHelper<Schema>::addBuildingProduct(typename Schema::IfcProduct* product, 
	typename Schema::IfcBuildingStorey* storey, typename Schema::IfcOwnerHistory* owner_hist) 
{
	if (! owner_hist) {
		owner_hist = getSingle<typename Schema::IfcOwnerHistory>();
	}
	if (! owner_hist) {
		owner_hist = addOwnerHistory();
	}
	if (! storey) {
		storey = getSingle<typename Schema::IfcBuildingStorey>();
	}
	if (! storey) {
		storey = addBuildingStorey(0, owner_hist);
	}
	addEntity(product);

	// CV-2x3-158: Don't add decompositions directly to a building storey
	const bool is_decomposition = product->Decomposes()->size() > 0;

	if (!is_decomposition) {
		addRelatedObject<typename Schema::IfcRelContainedInSpatialStructure>(storey, product);
		relatePlacements(storey, product);
	}
	return storey;
}

template <typename Schema>
void IfcHierarchyHelper<Schema>::addExtrudedPolyline(typename Schema::IfcShapeRepresentation* rep, const std::vector<std::pair<double, double> >& points, double h, 
	typename Schema::IfcAxis2Placement2D* /*place*/, typename Schema::IfcAxis2Placement3D* place2, 
	typename Schema::IfcDirection* dir, typename Schema::IfcRepresentationContext* /*context*/) 
{
	typename Schema::IfcCartesianPoint::list::ptr cartesian_points (new typename Schema::IfcCartesianPoint::list);
	for (std::vector<std::pair<double, double> >::const_iterator i = points.begin(); i != points.end(); ++i) {
		cartesian_points->push(addDoublet<typename Schema::IfcCartesianPoint>(i->first, i->second));
	}
	if (cartesian_points->size()) cartesian_points->push(*cartesian_points->begin());
	typename Schema::IfcPolyline* line = new typename Schema::IfcPolyline(cartesian_points);
	typename Schema::IfcArbitraryClosedProfileDef* profile = new typename Schema::IfcArbitraryClosedProfileDef(
		Schema::IfcProfileTypeEnum::IfcProfileType_AREA, boost::none, line);

	typename Schema::IfcExtrudedAreaSolid* solid = new typename Schema::IfcExtrudedAreaSolid(
		profile, place2 ? place2 : addPlacement3d(), dir ? dir : addTriplet<typename Schema::IfcDirection>(0, 0, 1), h);

	typename Schema::IfcRepresentationItem::list::ptr items = rep->Items();
	items->push(solid);
	rep->setItems(items);

	addEntity(line);
	addEntity(profile);
	addEntity(solid);
}

template <typename Schema>
typename Schema::IfcProductDefinitionShape* IfcHierarchyHelper<Schema>::addExtrudedPolyline(const std::vector<std::pair<double, double> >& points, double h, 
	typename Schema::IfcAxis2Placement2D* place, typename Schema::IfcAxis2Placement3D* place2, typename Schema::IfcDirection* dir, 
	typename Schema::IfcRepresentationContext* context) 
{
	typename Schema::IfcRepresentation::list::ptr reps (new typename Schema::IfcRepresentation::list);
	typename Schema::IfcRepresentationItem::list::ptr items (new typename Schema::IfcRepresentationItem::list);
	typename Schema::IfcShapeRepresentation* rep = new typename Schema::IfcShapeRepresentation(context 
		? context 
		: getRepresentationContext("Model"), std::string("Body"), std::string("SweptSolid"), items);
	reps->push(rep);
	typename Schema::IfcProductDefinitionShape* shape = new typename Schema::IfcProductDefinitionShape(boost::none, boost::none, reps);
	addEntity(rep);
	addEntity(shape);
	addExtrudedPolyline(rep, points, h, place, place2, dir, context);

	return shape;
}

template <typename Schema>
void IfcHierarchyHelper<Schema>::addBox(typename Schema::IfcShapeRepresentation* rep, double w, double d, double h, 
	typename Schema::IfcAxis2Placement2D* place, typename Schema::IfcAxis2Placement3D* place2, 
	typename Schema::IfcDirection* dir, typename Schema::IfcRepresentationContext* context) 
{
	if (false) { // TODO What's this?
		typename Schema::IfcRectangleProfileDef* profile = new typename Schema::IfcRectangleProfileDef(
			Schema::IfcProfileTypeEnum::IfcProfileType_AREA, boost::none, place ? place : addPlacement2d(), w, d);
		typename Schema::IfcExtrudedAreaSolid* solid = new typename Schema::IfcExtrudedAreaSolid(profile, 
			place2 ? place2 : addPlacement3d(), dir ? dir : addTriplet<typename Schema::IfcDirection>(0, 0, 1), h);

		addEntity(profile);
		addEntity(solid);
		typename Schema::IfcRepresentationItem::list::ptr items = rep->Items();
		items->push(solid);
		rep->setItems(items);
	} else {
		std::vector<std::pair<double, double> > points;
		points.push_back(std::make_pair(-w/2, -d/2));
		points.push_back(std::make_pair(w/2, -d/2));
		points.push_back(std::make_pair(w/2, d/2));
		points.push_back(std::make_pair(-w/2, d/2));
		// The call to addExtrudedPolyline() closes the polyline
		addExtrudedPolyline(rep, points, h, place, place2, dir, context);
	}
}

template <typename Schema>
void IfcHierarchyHelper<Schema>::addAxis(typename Schema::IfcShapeRepresentation* rep, double l, typename Schema::IfcRepresentationContext* /*context*/) {
	typename Schema::IfcCartesianPoint* p1 = addDoublet<typename Schema::IfcCartesianPoint>(-l / 2., 0.);
	typename Schema::IfcCartesianPoint* p2 = addDoublet<typename Schema::IfcCartesianPoint>(+l / 2., 0.);
	typename Schema::IfcCartesianPoint::list::ptr pts(new typename Schema::IfcCartesianPoint::list);
	pts->push(p1); pts->push(p2);
	typename Schema::IfcPolyline* poly = new typename Schema::IfcPolyline(pts);
	addEntity(poly);
	
	typename Schema::IfcRepresentationItem::list::ptr items = rep->Items();
	items->push(poly);
	rep->setItems(items);
}

template <typename Schema>
typename Schema::IfcProductDefinitionShape* IfcHierarchyHelper<Schema>::addBox(double w, double d, double h, typename Schema::IfcAxis2Placement2D* place, 
	typename Schema::IfcAxis2Placement3D* place2, typename Schema::IfcDirection* dir, typename Schema::IfcRepresentationContext* context) 
{
	typename Schema::IfcRepresentation::list::ptr reps (new typename Schema::IfcRepresentation::list);
	typename Schema::IfcRepresentationItem::list::ptr items (new typename Schema::IfcRepresentationItem::list);		
	typename Schema::IfcShapeRepresentation* rep = new typename Schema::IfcShapeRepresentation(
		context ? context : getRepresentationContext("Model"), std::string("Body"), std::string("SweptSolid"), items);
	reps->push(rep);
	typename Schema::IfcProductDefinitionShape* shape = new typename Schema::IfcProductDefinitionShape(boost::none, boost::none, reps);
	addEntity(rep);
	addEntity(shape);
	addBox(rep, w, d, h, place, place2, dir, context);
	return shape;
}

template <typename Schema>
typename Schema::IfcProductDefinitionShape* IfcHierarchyHelper<Schema>::addAxisBox(double w, double d, double h, typename Schema::IfcRepresentationContext* context) 
{
	typename Schema::IfcRepresentation::list::ptr reps(new typename Schema::IfcRepresentation::list);
	typename Schema::IfcRepresentationItem::list::ptr body_items(new typename Schema::IfcRepresentationItem::list);
	typename Schema::IfcRepresentationItem::list::ptr axis_items(new typename Schema::IfcRepresentationItem::list);
	typename Schema::IfcShapeRepresentation* body_rep = new typename Schema::IfcShapeRepresentation(
		context ? context : getRepresentationContext("Model"), std::string("Body"), std::string("SweptSolid"), body_items);

	typename Schema::IfcShapeRepresentation* axis_rep = new typename Schema::IfcShapeRepresentation(
		context ? context : getRepresentationContext("Plan"), std::string("Axis"), std::string("Curve2D"), axis_items);

	reps->push(axis_rep);
	reps->push(body_rep);

	typename Schema::IfcProductDefinitionShape* shape = new typename Schema::IfcProductDefinitionShape(boost::none, boost::none, reps);
	addEntity(shape);
	addEntity(body_rep);
	addBox(body_rep, w, d, h, 0, 0, 0, context);
	addEntity(axis_rep);
	addAxis(axis_rep, w);
	
	return shape;
}

template <typename Schema>
void IfcHierarchyHelper<Schema>::clipRepresentation(typename Schema::IfcProductRepresentation* shape, 
	typename Schema::IfcAxis2Placement3D* place, bool agree) 
{
	typename Schema::IfcRepresentation::list::ptr reps = shape->Representations();
	for (typename Schema::IfcRepresentation::list::it j = reps->begin(); j != reps->end(); ++j) {
		clipRepresentation(*j, place, agree);
	}
}

template <typename Schema>
void IfcHierarchyHelper<Schema>::clipRepresentation(typename Schema::IfcRepresentation* rep, 
	typename Schema::IfcAxis2Placement3D* place, bool agree) 
{
	if (rep->RepresentationIdentifier() != "Body") return;
	typename Schema::IfcPlane* plane = new typename Schema::IfcPlane(place);
	typename Schema::IfcHalfSpaceSolid* half_space = new typename Schema::IfcHalfSpaceSolid(plane, agree);
	addEntity(plane);
	addEntity(half_space);
	rep->setRepresentationType("Clipping");		
	typename Schema::IfcRepresentationItem::list::ptr items = rep->Items();
	typename Schema::IfcRepresentationItem::list::ptr new_items (new typename Schema::IfcRepresentationItem::list);
	for (typename Schema::IfcRepresentationItem::list::it i = items->begin(); i != items->end(); ++i) {
		typename Schema::IfcRepresentationItem* item = *i;
		typename Schema::IfcBooleanClippingResult* clip = new typename Schema::IfcBooleanClippingResult(
			Schema::IfcBooleanOperator::IfcBooleanOperator_DIFFERENCE, item, half_space);
		addEntity(clip);
		new_items->push(clip);
	}
	rep->setItems(new_items);
}

template <typename Schema>
typename Schema::IfcPresentationStyleAssignment* IfcHierarchyHelper<Schema>::addStyleAssignment(double r, double g, double b, double a) {
	typename Schema::IfcColourRgb* colour = new typename Schema::IfcColourRgb(boost::none, r, g, b);
	typename Schema::IfcSurfaceStyleRendering* rendering = a == 1.0
		? new typename Schema::IfcSurfaceStyleRendering(colour, boost::none, 0, 0, 0, 0, 
			0, 0, Schema::IfcReflectanceMethodEnum::IfcReflectanceMethod_FLAT)
		: new typename Schema::IfcSurfaceStyleRendering(colour, 1.0-a, 0, 0, 0, 0, 
			0, 0, Schema::IfcReflectanceMethodEnum::IfcReflectanceMethod_FLAT);

	IfcEntityList::ptr styles(new IfcEntityList());
	styles->push(rendering);
	typename Schema::IfcSurfaceStyle* surface_style = new typename Schema::IfcSurfaceStyle(
		boost::none, Schema::IfcSurfaceSide::IfcSurfaceSide_BOTH, styles);
	IfcEntityList::ptr surface_styles(new IfcEntityList());
	surface_styles->push(surface_style);
	typename Schema::IfcPresentationStyleAssignment* style_assignment = 
		new typename Schema::IfcPresentationStyleAssignment(surface_styles);
	addEntity(colour);
	addEntity(rendering);
	addEntity(surface_style);
	addEntity(style_assignment);
	return style_assignment;
}

template <typename Schema>
typename Schema::IfcPresentationStyleAssignment* IfcHierarchyHelper<Schema>::setSurfaceColour(
	typename Schema::IfcProductRepresentation* shape, double r, double g, double b, double a) 
{
	typename Schema::IfcPresentationStyleAssignment* style_assignment = addStyleAssignment(r, g, b, a);
	setSurfaceColour(shape, style_assignment);
	return style_assignment;
}

template <typename Schema>
typename Schema::IfcPresentationStyleAssignment* IfcHierarchyHelper<Schema>::setSurfaceColour(
	typename Schema::IfcRepresentation* shape, double r, double g, double b, double a) 
{
	typename Schema::IfcPresentationStyleAssignment* style_assignment = addStyleAssignment(r, g, b, a);
	setSurfaceColour(shape, style_assignment);
	return style_assignment;
}

template <typename Schema>
void IfcHierarchyHelper<Schema>::setSurfaceColour(typename Schema::IfcProductRepresentation* shape, 
	typename Schema::IfcPresentationStyleAssignment* style_assignment) 
{
	typename Schema::IfcRepresentation::list::ptr reps = shape->Representations();
	for (typename Schema::IfcRepresentation::list::it j = reps->begin(); j != reps->end(); ++j) {
		setSurfaceColour(*j, style_assignment);
	}
}

Ifc2x3::IfcStyledItem* create_styled_item(Ifc2x3::IfcRepresentationItem* item, Ifc2x3::IfcPresentationStyleAssignment* style_assignment) {
	Ifc2x3::IfcPresentationStyleAssignment::list::ptr style_assignments(new Ifc2x3::IfcPresentationStyleAssignment::list);
	style_assignments->push(style_assignment);
	return new Ifc2x3::IfcStyledItem(item, style_assignments, boost::none);
}

Ifc4::IfcStyledItem* create_styled_item(Ifc4::IfcRepresentationItem* item, Ifc4::IfcPresentationStyleAssignment* style_assignment) {
	IfcEntityList::ptr style_assignments(new IfcEntityList);
	style_assignments->push(style_assignment);
	return new Ifc4::IfcStyledItem(item, style_assignments, boost::none);
}

Ifc4x1::IfcStyledItem* create_styled_item(Ifc4x1::IfcRepresentationItem* item, Ifc4x1::IfcPresentationStyleAssignment* style_assignment) {
	IfcEntityList::ptr style_assignments(new IfcEntityList);
	style_assignments->push(style_assignment);
	return new Ifc4x1::IfcStyledItem(item, style_assignments, boost::none);
}

Ifc4x2::IfcStyledItem* create_styled_item(Ifc4x2::IfcRepresentationItem* item, Ifc4x2::IfcPresentationStyleAssignment* style_assignment) {
	IfcEntityList::ptr style_assignments(new IfcEntityList);
	style_assignments->push(style_assignment);
	return new Ifc4x2::IfcStyledItem(item, style_assignments, boost::none);
}
template <typename Schema>
void IfcHierarchyHelper<Schema>::setSurfaceColour(typename Schema::IfcRepresentation* rep, 
	typename Schema::IfcPresentationStyleAssignment* style_assignment) 
{
	typename Schema::IfcRepresentationItem::list::ptr items = rep->Items();
	for (typename Schema::IfcRepresentationItem::list::it i = items->begin(); i != items->end(); ++i) {
		typename Schema::IfcRepresentationItem* item = *i;
		typename Schema::IfcStyledItem* styled_item = create_styled_item(item, style_assignment);
		addEntity(styled_item);
	}
}

template <typename Schema>
typename Schema::IfcProductDefinitionShape* IfcHierarchyHelper<Schema>::addMappedItem(
	typename Schema::IfcShapeRepresentation* rep, 
	typename Schema::IfcCartesianTransformationOperator3D* transform,
	typename Schema::IfcProductDefinitionShape* def)
{
	typename Schema::IfcRepresentationMap::list::ptr maps = rep->RepresentationMap();
	typename Schema::IfcRepresentationMap* map;
	if (maps->size() == 1) {
		map = *maps->begin();
	} else {
		map = new typename Schema::IfcRepresentationMap(addPlacement3d(), rep);
		addEntity(map);
	}

	typename Schema::IfcRepresentation::list::ptr representations(new typename Schema::IfcRepresentation::list);
	if (def) representations = def->Representations();

	if (!transform) {
		transform = new typename Schema::IfcCartesianTransformationOperator3D(0, 0, addTriplet<typename Schema::IfcCartesianPoint>(0,0,0), boost::none, 0);
		addEntity(transform);
	}
	typename Schema::IfcMappedItem* item = new typename Schema::IfcMappedItem(map, transform);
	typename Schema::IfcRepresentationItem::list::ptr items(new typename Schema::IfcRepresentationItem::list);
	items->push(item);
	typename Schema::IfcRepresentation* new_rep = new typename Schema::IfcShapeRepresentation(rep->ContextOfItems(), boost::none, std::string("MappedRepresentation"), items);
	if (rep->hasRepresentationIdentifier()) {
		new_rep->setRepresentationIdentifier(rep->RepresentationIdentifier());
	}	
	addEntity(item);
	addEntity(new_rep);
	representations->push(new_rep);
	if (!def) {
		def = new typename Schema::IfcProductDefinitionShape(boost::none, boost::none, representations);
		addEntity(def);
	} else {
		def->setRepresentations(representations);
	}
	return def;
}

template <typename Schema>
typename Schema::IfcProductDefinitionShape* IfcHierarchyHelper<Schema>::addMappedItem(
	typename Schema::IfcShapeRepresentation::list::ptr reps, 
	typename Schema::IfcCartesianTransformationOperator3D* transform)
{
	typename Schema::IfcProductDefinitionShape* def = 0;
	for (typename Schema::IfcShapeRepresentation::list::it it = reps->begin(); it != reps->end(); ++it) {
		def = addMappedItem(*it, transform, def);
	}
	return def;
}

template <typename Schema>
typename Schema::IfcShapeRepresentation* IfcHierarchyHelper<Schema>::addEmptyRepresentation(const std::string& repid, const std::string& reptype) {
	typename Schema::IfcRepresentationItem::list::ptr items(new typename Schema::IfcRepresentationItem::list);
	typename Schema::IfcShapeRepresentation* shape_rep = new typename Schema::IfcShapeRepresentation(getRepresentationContext(reptype == "Curve2D" ? "Plan" : "Model"), repid, reptype, items);
	addEntity(shape_rep);
	return shape_rep;
}

template <typename Schema>
typename Schema::IfcGeometricRepresentationContext* IfcHierarchyHelper<Schema>::getRepresentationContext(const std::string& s) {
	typename std::map<std::string, typename Schema::IfcGeometricRepresentationContext*>::const_iterator it = contexts.find(s);
	if (it != contexts.end()) return it->second;
	else {
		typename Schema::IfcProject* project = getSingle<typename Schema::IfcProject>();
		if (!project) {
			project = addProject();
		}
		typename Schema::IfcRepresentationContext::list::ptr project_contexts = project->RepresentationContexts();
		typename Schema::IfcGeometricRepresentationContext* context = new typename Schema::IfcGeometricRepresentationContext(
			boost::none, s, 3, 1e-5, addPlacement3d(), addDoublet<typename Schema::IfcDirection>(0, 1));
		addEntity(context);
		project_contexts->push(context);
		project->setRepresentationContexts(project_contexts);
		return contexts[s] = context;
	}
}

template IFC_PARSE_API class IfcHierarchyHelper<Ifc2x3>;
template IFC_PARSE_API class IfcHierarchyHelper<Ifc4>;
template IFC_PARSE_API class IfcHierarchyHelper<Ifc4x1>;
template IFC_PARSE_API class IfcHierarchyHelper<Ifc4x2>;
