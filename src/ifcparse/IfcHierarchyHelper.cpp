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
	
Ifc2x3::IfcAxis2Placement3D* IfcHierarchyHelper::addPlacement3d(
	double ox, double oy, double oz,
	double zx, double zy, double zz,
	double xx, double xy, double xz) 
{
		Ifc2x3::IfcDirection* x = addTriplet<Ifc2x3::IfcDirection>(xx, xy, xz);
		Ifc2x3::IfcDirection* z = addTriplet<Ifc2x3::IfcDirection>(zx, zy, zz);
		Ifc2x3::IfcCartesianPoint* o = addTriplet<Ifc2x3::IfcCartesianPoint>(ox, oy, oz);
		Ifc2x3::IfcAxis2Placement3D* p3d = new Ifc2x3::IfcAxis2Placement3D(o, z, x);
		AddEntity(p3d);
		return p3d;
}

Ifc2x3::IfcAxis2Placement2D* IfcHierarchyHelper::addPlacement2d(
	double ox, double oy,
	double xx, double xy) 
{
		Ifc2x3::IfcDirection* x = addDoublet<Ifc2x3::IfcDirection>(xx, xy);
		Ifc2x3::IfcCartesianPoint* o = addDoublet<Ifc2x3::IfcCartesianPoint>(ox, oy);
		Ifc2x3::IfcAxis2Placement2D* p2d = new Ifc2x3::IfcAxis2Placement2D(o, x);
		AddEntity(p2d);
		return p2d;
}

Ifc2x3::IfcLocalPlacement* IfcHierarchyHelper::addLocalPlacement(
	double ox, double oy, double oz,
	double zx, double zy, double zz,
	double xx, double xy, double xz) 
{
		Ifc2x3::IfcLocalPlacement* lp = new Ifc2x3::IfcLocalPlacement(0, 
			addPlacement3d(ox, oy, oz, zx, zy, zz, xx, xy, xz));

		AddEntity(lp);
		return lp;
}

Ifc2x3::IfcOwnerHistory* IfcHierarchyHelper::addOwnerHistory() {
	Ifc2x3::IfcPerson* person = new Ifc2x3::IfcPerson(boost::none, boost::none, std::string(""), 
		boost::none, boost::none, boost::none, boost::none, boost::none);

	Ifc2x3::IfcOrganization* organization = new Ifc2x3::IfcOrganization(boost::none, 
		"IfcOpenShell", boost::none, boost::none, boost::none);

	Ifc2x3::IfcPersonAndOrganization* person_and_org = new Ifc2x3::IfcPersonAndOrganization(person, organization, boost::none);
	Ifc2x3::IfcApplication* application = new Ifc2x3::IfcApplication(organization, 
		IFCOPENSHELL_VERSION, "IfcOpenShell", "IfcOpenShell");

	int timestamp = (int) time(0);
	Ifc2x3::IfcOwnerHistory* owner_hist = new Ifc2x3::IfcOwnerHistory(person_and_org, application, 
		boost::none, Ifc2x3::IfcChangeActionEnum::IfcChangeAction_ADDED, boost::none, person_and_org, application, timestamp);

	AddEntity(person);
	AddEntity(organization);
	AddEntity(person_and_org);
	AddEntity(application);
	AddEntity(owner_hist);

	return owner_hist;
}
	
Ifc2x3::IfcProject* IfcHierarchyHelper::addProject(Ifc2x3::IfcOwnerHistory* owner_hist) {
	Ifc2x3::IfcRepresentationContext::list rep_contexts (new IfcTemplatedEntityList<Ifc2x3::IfcRepresentationContext>());
	Ifc2x3::IfcGeometricRepresentationContext* rep_context = new Ifc2x3::IfcGeometricRepresentationContext(
		std::string("Plan"), std::string("Model"), 3, 1e-5, addPlacement3d(), addTriplet<Ifc2x3::IfcDirection>(0, 1, 0));

	rep_contexts->push(rep_context);

	IfcEntities units (new IfcEntityList());
	Ifc2x3::IfcDimensionalExponents* dimexp = new Ifc2x3::IfcDimensionalExponents(0, 0, 0, 0, 0, 0, 0);
	Ifc2x3::IfcSIUnit* unit1 = new Ifc2x3::IfcSIUnit(Ifc2x3::IfcUnitEnum::IfcUnit_LENGTHUNIT, 
		Ifc2x3::IfcSIPrefix::IfcSIPrefix_MILLI, Ifc2x3::IfcSIUnitName::IfcSIUnitName_METRE);
	Ifc2x3::IfcSIUnit* unit2a = new Ifc2x3::IfcSIUnit(Ifc2x3::IfcUnitEnum::IfcUnit_PLANEANGLEUNIT, 
		boost::none, Ifc2x3::IfcSIUnitName::IfcSIUnitName_RADIAN);
	Ifc2x3::IfcMeasureWithUnit* unit2b = new Ifc2x3::IfcMeasureWithUnit(
		new IfcWrite::IfcSelectHelper(0.017453293, Ifc2x3::Type::IfcPlaneAngleMeasure), unit2a);
	Ifc2x3::IfcConversionBasedUnit* unit2 = new Ifc2x3::IfcConversionBasedUnit(dimexp, 
		Ifc2x3::IfcUnitEnum::IfcUnit_PLANEANGLEUNIT, "Degrees", unit2b);

	units->push(unit1);
	units->push(unit2);

	Ifc2x3::IfcUnitAssignment* unit_assignment = new Ifc2x3::IfcUnitAssignment(units);

	Ifc2x3::IfcProject* project = new Ifc2x3::IfcProject(IfcWrite::IfcGuidHelper(), owner_hist, boost::none, boost::none, 
		boost::none, boost::none, boost::none, rep_contexts, unit_assignment);

	AddEntity(rep_context);
	AddEntity(dimexp);
	AddEntity(unit1);
	AddEntity(unit2a);
	AddEntity(unit2b);
	AddEntity(unit2);
	AddEntity(unit_assignment);
	AddEntity(project);

	return project;
}

void IfcHierarchyHelper::relatePlacements(Ifc2x3::IfcProduct* parent, Ifc2x3::IfcProduct* product) {
	Ifc2x3::IfcObjectPlacement* place = product->hasObjectPlacement() ? product->ObjectPlacement() : 0;
	if (place && place->is(Ifc2x3::Type::IfcLocalPlacement)) {
		Ifc2x3::IfcLocalPlacement* local_place = (Ifc2x3::IfcLocalPlacement*) place;
		if (parent->hasObjectPlacement()) {
			local_place->setPlacementRelTo(parent->ObjectPlacement());
		}
	}
}
	
Ifc2x3::IfcSite* IfcHierarchyHelper::addSite(Ifc2x3::IfcProject* proj, Ifc2x3::IfcOwnerHistory* owner_hist) {
	if (! owner_hist) {
		owner_hist = getSingle<Ifc2x3::IfcOwnerHistory>();
	}
	if (! owner_hist) {
		owner_hist = addOwnerHistory();
	}
	if (! proj) {
		proj = getSingle<Ifc2x3::IfcProject>();
	}
	if (! proj) {
		proj = addProject(owner_hist);
	}

	Ifc2x3::IfcSite* site = new Ifc2x3::IfcSite(IfcWrite::IfcGuidHelper(), owner_hist, boost::none, 
		boost::none, boost::none, addLocalPlacement(), 0, boost::none, 
		Ifc2x3::IfcElementCompositionEnum::IfcElementComposition_ELEMENT, 
		boost::none, boost::none, boost::none, boost::none, 0);

	AddEntity(site);
	addRelatedObject<Ifc2x3::IfcRelAggregates>(proj, site);
	return site;
}
	
Ifc2x3::IfcBuilding* IfcHierarchyHelper::addBuilding(Ifc2x3::IfcSite* site, Ifc2x3::IfcOwnerHistory* owner_hist) {
	if (! owner_hist) {
		owner_hist = getSingle<Ifc2x3::IfcOwnerHistory>();
	}
	if (! owner_hist) {
		owner_hist = addOwnerHistory();
	}
	if (! site) {
		site = getSingle<Ifc2x3::IfcSite>();
	}
	if (! site) {
		site = addSite(0, owner_hist);
	}
	Ifc2x3::IfcBuilding* building = new Ifc2x3::IfcBuilding(IfcWrite::IfcGuidHelper(), owner_hist, boost::none, boost::none, boost::none, 
		addLocalPlacement(), 0, boost::none, Ifc2x3::IfcElementCompositionEnum::IfcElementComposition_ELEMENT, 
		boost::none, boost::none, 0);

	AddEntity(building);
	addRelatedObject<Ifc2x3::IfcRelAggregates>(site, building);
	relatePlacements(site, building);

	return building;
}

Ifc2x3::IfcBuildingStorey* IfcHierarchyHelper::addBuildingStorey(Ifc2x3::IfcBuilding* building, 
	Ifc2x3::IfcOwnerHistory* owner_hist) 
{
	if (! owner_hist) {
		owner_hist = getSingle<Ifc2x3::IfcOwnerHistory>();
	}
	if (! owner_hist) {
		owner_hist = addOwnerHistory();
	}
	if (! building) {
		building = getSingle<Ifc2x3::IfcBuilding>();
	}
	if (! building) {
		building = addBuilding(0, owner_hist);
	}
	Ifc2x3::IfcBuildingStorey* storey = new Ifc2x3::IfcBuildingStorey(IfcWrite::IfcGuidHelper(), 
		owner_hist, boost::none, boost::none, boost::none, addLocalPlacement(), 0, boost::none, 
		Ifc2x3::IfcElementCompositionEnum::IfcElementComposition_ELEMENT, boost::none);

	AddEntity(storey);
	addRelatedObject<Ifc2x3::IfcRelAggregates>(building, storey);
	relatePlacements(building, storey);

	return storey;
}

Ifc2x3::IfcBuildingStorey* IfcHierarchyHelper::addBuildingProduct(Ifc2x3::IfcProduct* product, 
	Ifc2x3::IfcBuildingStorey* storey, Ifc2x3::IfcOwnerHistory* owner_hist) 
{
	if (! owner_hist) {
		owner_hist = getSingle<Ifc2x3::IfcOwnerHistory>();
	}
	if (! owner_hist) {
		owner_hist = addOwnerHistory();
	}
	if (! storey) {
		storey = getSingle<Ifc2x3::IfcBuildingStorey>();
	}
	if (! storey) {
		storey = addBuildingStorey(0, owner_hist);
	}
	AddEntity(product);
	addRelatedObject<Ifc2x3::IfcRelContainedInSpatialStructure>(storey, product);
	relatePlacements(storey, product);
	return storey;
}

void IfcHierarchyHelper::addExtrudedPolyline(Ifc2x3::IfcShapeRepresentation* rep, const std::vector<std::pair<double, double> >& points, double h, 
	Ifc2x3::IfcAxis2Placement2D* place, Ifc2x3::IfcAxis2Placement3D* place2, 
	Ifc2x3::IfcDirection* dir, Ifc2x3::IfcRepresentationContext* context) 
{
	Ifc2x3::IfcCartesianPoint::list cartesian_points (new IfcTemplatedEntityList<Ifc2x3::IfcCartesianPoint>());
	for (std::vector<std::pair<double, double> >::const_iterator i = points.begin(); i != points.end(); ++i) {
		cartesian_points->push(addDoublet<Ifc2x3::IfcCartesianPoint>(i->first, i->second));
	}
	if (cartesian_points->Size()) cartesian_points->push(*cartesian_points->begin());
	Ifc2x3::IfcPolyline* line = new Ifc2x3::IfcPolyline(cartesian_points);
	Ifc2x3::IfcArbitraryClosedProfileDef* profile = new Ifc2x3::IfcArbitraryClosedProfileDef(
		Ifc2x3::IfcProfileTypeEnum::IfcProfileType_AREA, boost::none, line);

	Ifc2x3::IfcExtrudedAreaSolid* solid = new Ifc2x3::IfcExtrudedAreaSolid(
		profile, place2 ? place2 : addPlacement3d(), dir ? dir : addTriplet<Ifc2x3::IfcDirection>(0, 0, 1), h);

	Ifc2x3::IfcRepresentationItem::list items = rep->Items();
	items->push(solid);
	rep->setItems(items);

	AddEntity(line);
	AddEntity(profile);
	AddEntity(solid);
}

Ifc2x3::IfcProductDefinitionShape* IfcHierarchyHelper::addExtrudedPolyline(const std::vector<std::pair<double, double> >& points, double h, 
	Ifc2x3::IfcAxis2Placement2D* place, Ifc2x3::IfcAxis2Placement3D* place2, Ifc2x3::IfcDirection* dir, 
	Ifc2x3::IfcRepresentationContext* context) 
{
	Ifc2x3::IfcRepresentation::list reps (new IfcTemplatedEntityList<Ifc2x3::IfcRepresentation>());
	Ifc2x3::IfcRepresentationItem::list items (new IfcTemplatedEntityList<Ifc2x3::IfcRepresentationItem>());
	Ifc2x3::IfcShapeRepresentation* rep = new Ifc2x3::IfcShapeRepresentation(context 
		? context 
		: getSingle<Ifc2x3::IfcRepresentationContext>(), std::string("Body"), std::string("SweptSolid"), items);
	reps->push(rep);
	Ifc2x3::IfcProductDefinitionShape* shape = new Ifc2x3::IfcProductDefinitionShape(0, 0, reps);		
	AddEntity(rep);
	AddEntity(shape);
	addExtrudedPolyline(rep, points, h, place, place2, dir, context);

	return shape;
}

void IfcHierarchyHelper::addBox(Ifc2x3::IfcShapeRepresentation* rep, double w, double d, double h, 
	Ifc2x3::IfcAxis2Placement2D* place, Ifc2x3::IfcAxis2Placement3D* place2, 
	Ifc2x3::IfcDirection* dir, Ifc2x3::IfcRepresentationContext* context) 
{
	if (false) {
		Ifc2x3::IfcRectangleProfileDef* profile = new Ifc2x3::IfcRectangleProfileDef(
			Ifc2x3::IfcProfileTypeEnum::IfcProfileType_AREA, 0, place ? place : addPlacement2d(), w, d);
		Ifc2x3::IfcExtrudedAreaSolid* solid = new Ifc2x3::IfcExtrudedAreaSolid(profile, 
			place2 ? place2 : addPlacement3d(), dir ? dir : addTriplet<Ifc2x3::IfcDirection>(0, 0, 1), h);

		AddEntity(profile);
		AddEntity(solid);
		Ifc2x3::IfcRepresentationItem::list items = rep->Items();
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

Ifc2x3::IfcProductDefinitionShape* IfcHierarchyHelper::addBox(double w, double d, double h, Ifc2x3::IfcAxis2Placement2D* place, 
	Ifc2x3::IfcAxis2Placement3D* place2, Ifc2x3::IfcDirection* dir, Ifc2x3::IfcRepresentationContext* context) 
{
	Ifc2x3::IfcRepresentation::list reps (new IfcTemplatedEntityList<Ifc2x3::IfcRepresentation>());
	Ifc2x3::IfcRepresentationItem::list items (new IfcTemplatedEntityList<Ifc2x3::IfcRepresentationItem>());		
	Ifc2x3::IfcShapeRepresentation* rep = new Ifc2x3::IfcShapeRepresentation(
		context ? context : getSingle<Ifc2x3::IfcRepresentationContext>(), std::string("Body"), std::string("SweptSolid"), items);
	reps->push(rep);
	Ifc2x3::IfcProductDefinitionShape* shape = new Ifc2x3::IfcProductDefinitionShape(0, 0, reps);		
	AddEntity(rep);
	AddEntity(shape);
	addBox(rep, w, d, h, place, place2, dir, context);
	return shape;
}

void IfcHierarchyHelper::clipRepresentation(Ifc2x3::IfcProductRepresentation* shape, 
	Ifc2x3::IfcAxis2Placement3D* place, bool agree) 
{
	Ifc2x3::IfcPlane* plane = new Ifc2x3::IfcPlane(place);
	Ifc2x3::IfcHalfSpaceSolid* half_space = new Ifc2x3::IfcHalfSpaceSolid(plane, agree);
	Ifc2x3::IfcRepresentation::list reps = shape->Representations();
	for (Ifc2x3::IfcRepresentation::it j = reps->begin(); j != reps->end(); ++j) {
		Ifc2x3::IfcRepresentation* rep = *j;
		if (rep->RepresentationIdentifier() != "Body") continue;
		rep->setRepresentationType("Clipping");		
		Ifc2x3::IfcRepresentationItem::list items = rep->Items();
		Ifc2x3::IfcRepresentationItem::list new_items (new IfcTemplatedEntityList<Ifc2x3::IfcRepresentationItem>());
		AddEntity(plane);
		AddEntity(half_space);
		for (Ifc2x3::IfcRepresentationItem::it i = items->begin(); i != items->end(); ++i) {
			Ifc2x3::IfcRepresentationItem* item = *i;
			Ifc2x3::IfcBooleanClippingResult* clip = new Ifc2x3::IfcBooleanClippingResult(
				Ifc2x3::IfcBooleanOperator::IfcBooleanOperator_DIFFERENCE, item, half_space);
			AddEntity(clip);
			new_items->push(clip);
		}
		rep->setItems(new_items);
	}
}

Ifc2x3::IfcPresentationStyleAssignment* IfcHierarchyHelper::setSurfaceColour(
	Ifc2x3::IfcProductRepresentation* shape, double r, double g, double b, double a) 
{
	Ifc2x3::IfcColourRgb* colour = new Ifc2x3::IfcColourRgb(boost::none, r, g, b);
	Ifc2x3::IfcSurfaceStyleRendering* rendering = a == 1.0
		? new Ifc2x3::IfcSurfaceStyleRendering(colour, boost::none, boost::none, boost::none, boost::none, boost::none, 
			boost::none, boost::none, Ifc2x3::IfcReflectanceMethodEnum::IfcReflectanceMethod_FLAT)
		: new Ifc2x3::IfcSurfaceStyleRendering(colour, 1.0-a, boost::none, boost::none, boost::none, boost::none, 
			boost::none, boost::none, Ifc2x3::IfcReflectanceMethodEnum::IfcReflectanceMethod_FLAT);

	IfcEntities styles(new IfcEntityList());
	styles->push(rendering);
	Ifc2x3::IfcSurfaceStyle* surface_style = new Ifc2x3::IfcSurfaceStyle(
		boost::none, Ifc2x3::IfcSurfaceSide::IfcSurfaceSide_BOTH, styles);
	IfcEntities surface_styles(new IfcEntityList());
	surface_styles->push(surface_style);
	Ifc2x3::IfcPresentationStyleAssignment* style_assignment = 
		new Ifc2x3::IfcPresentationStyleAssignment(surface_styles);
	AddEntity(colour);
	AddEntity(rendering);
	AddEntity(surface_style);
	AddEntity(style_assignment);
	setSurfaceColour(shape, style_assignment);
	return style_assignment;
}

void IfcHierarchyHelper::setSurfaceColour(Ifc2x3::IfcProductRepresentation* shape, 
	Ifc2x3::IfcPresentationStyleAssignment* style_assignment) 
{
	Ifc2x3::IfcPresentationStyleAssignment::list style_assignments (new IfcTemplatedEntityList<Ifc2x3::IfcPresentationStyleAssignment>());
	style_assignments->push(style_assignment);
	Ifc2x3::IfcRepresentation::list reps = shape->Representations();
	for (Ifc2x3::IfcRepresentation::it j = reps->begin(); j != reps->end(); ++j) {
		Ifc2x3::IfcRepresentation* rep = *j;
		if (rep->RepresentationIdentifier() != "Body" && rep->RepresentationIdentifier() != "Facetation") continue;
		Ifc2x3::IfcRepresentationItem::list items = rep->Items();
		for (Ifc2x3::IfcRepresentationItem::it i = items->begin(); i != items->end(); ++i) {
			Ifc2x3::IfcRepresentationItem* item = *i;
			Ifc2x3::IfcStyledItem* styled_item = new Ifc2x3::IfcStyledItem(item, style_assignments, boost::none);
			AddEntity(styled_item);
		}
	}
}
