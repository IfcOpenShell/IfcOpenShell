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
 * Example that generates profiles of trimmed ellipses.                         *
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

typedef struct {
	double r1;
	double r2;
	double t1;
	double t2;
} EllipsePie;

static int i = 0;

void create_testcase_for(IfcHierarchyHelper& file, const EllipsePie& pie, Ifc2x3::IfcTrimmingPreference::IfcTrimmingPreference pref) {
	const double deg = 1. / 180. * 3.141592653;
	double flt1[] = {0.                      , 0.                      };
	double flt2[] = {pie.r1 * cos(pie.t1*deg), pie.r2 * sin(pie.t1*deg)};
	double flt3[] = {pie.r1 * cos(pie.t2*deg), pie.r2 * sin(pie.t2*deg)};

	std::vector<double> coords1(flt1, flt1 + 2);
	std::vector<double> coords2(flt2, flt2 + 2);
	std::vector<double> coords3(flt3, flt3 + 2);
	
	Ifc2x3::IfcCartesianPoint* p1 = new Ifc2x3::IfcCartesianPoint(coords1);
	Ifc2x3::IfcCartesianPoint* p2 = new Ifc2x3::IfcCartesianPoint(coords2);
	Ifc2x3::IfcCartesianPoint* p3 = new Ifc2x3::IfcCartesianPoint(coords3);
	
	Ifc2x3::IfcCartesianPoint::list::ptr points(new Ifc2x3::IfcCartesianPoint::list());
	points->push(p3);
	points->push(p1);
	points->push(p2);
	file.addEntities(points->generalize());

	
	Ifc2x3::IfcEllipse* ellipse = new Ifc2x3::IfcEllipse(file.addPlacement2d(), pie.r1, pie.r2);
	file.addEntity(ellipse);
	IfcEntityList::ptr trim1(new IfcEntityList);
	IfcEntityList::ptr trim2(new IfcEntityList);
	if (pref == Ifc2x3::IfcTrimmingPreference::IfcTrimmingPreference_PARAMETER) {
		trim1->push(new Ifc2x3::IfcParameterValue(pie.t1));
		trim2->push(new Ifc2x3::IfcParameterValue(pie.t2));
	} else {
		trim1->push(p2);
		trim2->push(p3);
	}
	Ifc2x3::IfcTrimmedCurve* trim = new Ifc2x3::IfcTrimmedCurve(ellipse, trim1, trim2, true, pref);
	file.addEntity(trim);
	
	Ifc2x3::IfcCompositeCurveSegment::list::ptr segments(new Ifc2x3::IfcCompositeCurveSegment::list());
	Ifc2x3::IfcCompositeCurveSegment* s2 = new Ifc2x3::IfcCompositeCurveSegment(Ifc2x3::IfcTransitionCode::IfcTransitionCode_CONTINUOUS, true, trim);
	
	Ifc2x3::IfcPolyline* poly = new Ifc2x3::IfcPolyline(points);	
	file.addEntity(poly);
	Ifc2x3::IfcCompositeCurveSegment* s1 = new Ifc2x3::IfcCompositeCurveSegment(Ifc2x3::IfcTransitionCode::IfcTransitionCode_CONTINUOUS, true, poly);
	segments->push(s1);
	
	segments->push(s2);
	file.addEntities(segments->generalize());
	
	Ifc2x3::IfcCompositeCurve* ccurve = new Ifc2x3::IfcCompositeCurve(segments, false);
	Ifc2x3::IfcArbitraryClosedProfileDef* profile = new Ifc2x3::IfcArbitraryClosedProfileDef(Ifc2x3::IfcProfileTypeEnum::IfcProfileType_AREA, null, ccurve);
	file.addEntity(ccurve);
	file.addEntity(profile);

	IfcSchema::IfcBuildingElementProxy* product = new IfcSchema::IfcBuildingElementProxy(
		guid(), 0, S("profile"), null, null, 0, 0, null, null);
	file.addBuildingProduct(product);
	product->setOwnerHistory(file.getSingle<IfcSchema::IfcOwnerHistory>());

	product->setObjectPlacement(file.addLocalPlacement(0, 200 * i++));

	IfcSchema::IfcExtrudedAreaSolid* solid = new IfcSchema::IfcExtrudedAreaSolid(profile,
		file.addPlacement3d(), file.addTriplet<IfcSchema::IfcDirection>(0, 0, 1), 20.0);

	file.addEntity(solid);
		
	IfcSchema::IfcRepresentation::list::ptr reps (new IfcSchema::IfcRepresentation::list());
	IfcSchema::IfcRepresentationItem::list::ptr items (new IfcSchema::IfcRepresentationItem::list());
		
	items->push(solid);
	IfcSchema::IfcShapeRepresentation* rep = new IfcSchema::IfcShapeRepresentation(
		file.getSingle<IfcSchema::IfcRepresentationContext>(), S("Body"), S("SweptSolid"), items);
	reps->push(rep);

	IfcSchema::IfcProductDefinitionShape* shape = new IfcSchema::IfcProductDefinitionShape(boost::none, boost::none, reps);
	file.addEntity(rep);
	file.addEntity(shape);
		
	product->setRepresentation(shape);
}

int main(int argc, char** argv) {
	const std::string filename = "ellipse_pies.ifc";
	IfcHierarchyHelper file;
	{ EllipsePie pie = {80., 50.,  0., 150.};
	create_testcase_for(file, pie, Ifc2x3::IfcTrimmingPreference::IfcTrimmingPreference_PARAMETER);
	create_testcase_for(file, pie, Ifc2x3::IfcTrimmingPreference::IfcTrimmingPreference_CARTESIAN);}
	{ EllipsePie pie = {80,  50., 30., 300.};
	create_testcase_for(file, pie, Ifc2x3::IfcTrimmingPreference::IfcTrimmingPreference_PARAMETER);
	create_testcase_for(file, pie, Ifc2x3::IfcTrimmingPreference::IfcTrimmingPreference_CARTESIAN);}
	{ EllipsePie pie = {80,  50., 300., 30.};
	create_testcase_for(file, pie, Ifc2x3::IfcTrimmingPreference::IfcTrimmingPreference_PARAMETER);
	create_testcase_for(file, pie, Ifc2x3::IfcTrimmingPreference::IfcTrimmingPreference_CARTESIAN);}
	{ EllipsePie pie = {50., 80.,  0., 150.};
	create_testcase_for(file, pie, Ifc2x3::IfcTrimmingPreference::IfcTrimmingPreference_PARAMETER);
	create_testcase_for(file, pie, Ifc2x3::IfcTrimmingPreference::IfcTrimmingPreference_CARTESIAN);}
	{ EllipsePie pie = {50,  80., 30., 300.};
	create_testcase_for(file, pie, Ifc2x3::IfcTrimmingPreference::IfcTrimmingPreference_PARAMETER);
	create_testcase_for(file, pie, Ifc2x3::IfcTrimmingPreference::IfcTrimmingPreference_CARTESIAN);}
	{ EllipsePie pie = {50,  80., 300., 30.};
	create_testcase_for(file, pie, Ifc2x3::IfcTrimmingPreference::IfcTrimmingPreference_PARAMETER);
	create_testcase_for(file, pie, Ifc2x3::IfcTrimmingPreference::IfcTrimmingPreference_CARTESIAN);}
	std::ofstream f(filename.c_str());
	f << file;
}
