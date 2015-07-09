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
 * Example that generates various representations from                          *
 * IfcArbitraryOpenProfileDefs and its subclass IfcCenterLineProfileDef         *
 *                                                                              *
 ********************************************************************************/

#include <string>
#include <iostream>
#include <fstream>

#include "../ifcparse/Ifc2x3.h"
#include "../ifcparse/IfcUtil.h"
#include "../ifcparse/IfcHierarchyHelper.h"

typedef std::string S;
typedef IfcParse::IfcGlobalId guid;
boost::none_t const null = boost::none;
static int i = 0;

void create_product_from_item(IfcHierarchyHelper& file, IfcSchema::IfcRepresentationItem* item, const std::string& s) {
	IfcSchema::IfcBuildingElementProxy* product = new IfcSchema::IfcBuildingElementProxy(
		guid(), 0, S("product"), null, null, 0, 0, null, null);
	file.addBuildingProduct(product);
	product->setOwnerHistory(file.getSingle<IfcSchema::IfcOwnerHistory>());

	product->setObjectPlacement(file.addLocalPlacement(0, 120 * i++));

	IfcSchema::IfcRepresentation::list::ptr reps (new IfcSchema::IfcRepresentation::list());
	IfcSchema::IfcRepresentationItem::list::ptr items (new IfcSchema::IfcRepresentationItem::list());
	items->push(item);

	if (s == "GeometricSet") {
		IfcSchema::IfcGeometricSet* set = new IfcSchema::IfcGeometricSet(items->generalize());
		file.addEntity(set);
		items = IfcSchema::IfcRepresentationItem::list::ptr(new IfcSchema::IfcRepresentationItem::list());
		items->push(set);
	}
		
	IfcSchema::IfcShapeRepresentation* rep = new IfcSchema::IfcShapeRepresentation(
		file.getSingle<IfcSchema::IfcRepresentationContext>(), S("Body"), s, items);
	reps->push(rep);

	IfcSchema::IfcProductDefinitionShape* shape = new IfcSchema::IfcProductDefinitionShape(boost::none, boost::none, reps);
	file.addEntity(rep);
	file.addEntity(shape);
		
	product->setRepresentation(shape);
}

void create_surfaces_from_profile(IfcHierarchyHelper& file, IfcSchema::IfcProfileDef* profile) {
	IfcSchema::IfcSurfaceOfLinearExtrusion* extrusion = new IfcSchema::IfcSurfaceOfLinearExtrusion(profile, file.addPlacement3d(), file.addTriplet<IfcSchema::IfcDirection>(0, 0, 1), 100.);
	file.addEntity(extrusion);

	IfcSchema::IfcAxis1Placement* ax1 = new IfcSchema::IfcAxis1Placement(file.addTriplet<IfcSchema::IfcCartesianPoint>(0,100,0), file.addTriplet<IfcSchema::IfcDirection>(1,0,0));
	IfcSchema::IfcSurfaceOfRevolution* revolution = new IfcSchema::IfcSurfaceOfRevolution(profile, file.addPlacement3d(), ax1);
	file.addEntity(ax1);
	file.addEntity(revolution);

	create_product_from_item(file, extrusion, "GeometricSet");
	create_product_from_item(file, revolution, "GeometricSet");
}

void create_solids_from_profile(IfcHierarchyHelper& file, IfcSchema::IfcProfileDef* profile) {
	IfcSchema::IfcExtrudedAreaSolid* extrusion = new IfcSchema::IfcExtrudedAreaSolid(profile, file.addPlacement3d(), file.addTriplet<IfcSchema::IfcDirection>(0, 0, 1), 100.);
	file.addEntity(extrusion);

	IfcSchema::IfcAxis1Placement* ax1 = new IfcSchema::IfcAxis1Placement(file.addTriplet<IfcSchema::IfcCartesianPoint>(0,100,0), file.addTriplet<IfcSchema::IfcDirection>(1,0,0));
	IfcSchema::IfcRevolvedAreaSolid* revolution1 = new IfcSchema::IfcRevolvedAreaSolid(profile, file.addPlacement3d(), ax1, 360.);
	IfcSchema::IfcRevolvedAreaSolid* revolution2 = new IfcSchema::IfcRevolvedAreaSolid(profile, file.addPlacement3d(), ax1, 90.);
	file.addEntity(ax1);
	file.addEntity(revolution1);
	file.addEntity(revolution2);

	create_product_from_item(file, extrusion, "SweptSolid");
	create_product_from_item(file, revolution1, "SweptSolid");
	create_product_from_item(file, revolution2, "SweptSolid");
}

void create_products_from_curve(IfcHierarchyHelper& file, IfcSchema::IfcBoundedCurve* curve) {
	IfcSchema::IfcArbitraryOpenProfileDef* open = new IfcSchema::IfcArbitraryOpenProfileDef(IfcSchema::IfcProfileTypeEnum::IfcProfileType_CURVE, null, curve);
	IfcSchema::IfcCenterLineProfileDef* center_line = new IfcSchema::IfcCenterLineProfileDef(IfcSchema::IfcProfileTypeEnum::IfcProfileType_AREA, null, curve, 10.);
	file.addEntity(open);
	file.addEntity(center_line);

	create_surfaces_from_profile(file, open);
	create_solids_from_profile(file, center_line);
}

int main(int argc, char** argv) {
	const char filename[] = "IfcArbitraryOpenProfileDef.ifc";
	IfcHierarchyHelper file;
	file.header().file_name().name(filename);

	double coords1[] = {-50.0, 0.0};
	double coords2[] = { 50.0, 0.0};
	IfcSchema::IfcCartesianPoint::list::ptr points (new IfcSchema::IfcCartesianPoint::list());
	points->push(new IfcSchema::IfcCartesianPoint(std::vector<double>(coords1, coords1+2)));
	points->push(new IfcSchema::IfcCartesianPoint(std::vector<double>(coords2, coords2+2)));
	file.addEntities(points->generalize());
	IfcSchema::IfcPolyline* poly = new IfcSchema::IfcPolyline(points);
	file.addEntity(poly);

	create_products_from_curve(file, poly);

	IfcSchema::IfcEllipse* ellipse = new IfcSchema::IfcEllipse(file.addPlacement2d(), 50., 25.);
	file.addEntity(ellipse);
	IfcEntityList::ptr trim1(new IfcEntityList);
	IfcEntityList::ptr trim2(new IfcEntityList);
	trim1->push(new IfcSchema::IfcParameterValue(  0.));
	trim2->push(new IfcSchema::IfcParameterValue(180.));
	IfcSchema::IfcTrimmedCurve* trim = new IfcSchema::IfcTrimmedCurve(ellipse, trim1, trim2, true, IfcSchema::IfcTrimmingPreference::IfcTrimmingPreference_PARAMETER);
	file.addEntity(trim);

	create_products_from_curve(file, trim);

	file.getSingle<Ifc2x3::IfcProject>()->setName("IfcArbitraryOpenProfileDef");

	std::ofstream f(filename);
	f << file;
}
