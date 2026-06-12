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
*																				*
* Example of curve rebar.														*
*																				*
********************************************************************************/

#include <iostream>
#include <string>
#include <fstream>

#include "ifcparse/macros.h"

#ifndef IfcSchema
#define IfcSchema Ifc2x3
#endif

#include INCLUDE_SCHEMA(ifcparse, IfcSchema)
#include INCLUDE_SCHEMA_DEFINITIONS(ifcparse, IfcSchema)

#include "ifcparse/IfcHierarchyHelper.h"

#include <boost/math/constants/constants.hpp>
const static double PI = boost::math::constants::pi<double>();

typedef std::string S;
typedef IfcParse::IfcGlobalId guid;
boost::none_t const null = boost::none;

#ifdef SCHEMA_HAS_IfcSegment
typedef IfcSchema::IfcSegment curve_segment_t;
#else
typedef IfcSchema::IfcCompositeCurveSegment curve_segment_t;
#endif

#ifdef SCHEMA_IfcReinforcingBar_HAS_PredefinedType
#define IFC_REINFORCING_BAR_TYPE IfcSchema::IfcReinforcingBarTypeEnum::IfcReinforcingBarType_LIGATURE
#else
#define IFC_REINFORCING_BAR_TYPE IfcSchema::IfcReinforcingBarRoleEnum::IfcReinforcingBarRole_LIGATURE
#endif

void create_curve_rebar(IfcHierarchyHelper<IfcSchema>& file)
{
	int dia = 24;
	int R = 3 * dia;
	int length = 12 * dia;

	double crossSectionarea = PI * dia * dia / 4;
	IfcSchema::IfcReinforcingBar* rebar = new IfcSchema::IfcReinforcingBar(
		guid(), 0, S("test"), null,
		null, 0, 0,
		null, S("SR24"),		//SteelGrade
		dia,						//diameter
		crossSectionarea,		//crossSectionarea = math.pi*(12.0/2)**2
		0,
		IFC_REINFORCING_BAR_TYPE,
		IfcSchema::IfcReinforcingBarSurfaceEnum::IfcReinforcingBarSurfaceEnum::IfcReinforcingBarSurface_PLAIN	//PLAIN or TEXTURED
		);

	file.addBuildingProduct(rebar);
	rebar->setOwnerHistory(file.getSingle<IfcSchema::IfcOwnerHistory>());

	curve_segment_t::list::ptr segments(new curve_segment_t::list());

	IfcSchema::IfcCartesianPoint* p1 = file.addTriplet<IfcSchema::IfcCartesianPoint>(0, 0, 1000.);
	IfcSchema::IfcCartesianPoint* p2 = file.addTriplet<IfcSchema::IfcCartesianPoint>(0, 0, 0);
	IfcSchema::IfcCartesianPoint* p3 = file.addTriplet<IfcSchema::IfcCartesianPoint>(0, R, 0);
	IfcSchema::IfcCartesianPoint* p4 = file.addTriplet<IfcSchema::IfcCartesianPoint>(0, R, -R);
	IfcSchema::IfcCartesianPoint* p5 = file.addTriplet<IfcSchema::IfcCartesianPoint>(0, R + length, -R);

	/*first segment - line */
	IfcSchema::IfcCartesianPoint::list::ptr points1(new IfcSchema::IfcCartesianPoint::list());
	points1->push(p1);
	points1->push(p2);
	file.addEntities(points1->generalize());
	IfcSchema::IfcPolyline* poly1 = new IfcSchema::IfcPolyline(points1);
	file.addEntity(poly1);

	IfcSchema::IfcCompositeCurveSegment* segment1 = new IfcSchema::IfcCompositeCurveSegment(IfcSchema::IfcTransitionCode::IfcTransitionCode_CONTINUOUS, true, poly1);
	file.addEntity(segment1);
	segments->push(segment1);

	/*second segment - arc */
	IfcSchema::IfcAxis2Placement3D* axis1 = new IfcSchema::IfcAxis2Placement3D(p3, file.addTriplet<IfcSchema::IfcDirection>(1, 0, 0), file.addTriplet<IfcSchema::IfcDirection>(0, 1, 0));
	file.addEntity(axis1);
	IfcSchema::IfcCircle* circle = new IfcSchema::IfcCircle(axis1, R);
	file.addEntity(circle);

	IfcSchema::IfcTrimmingSelect::list::ptr trim1(new IfcSchema::IfcTrimmingSelect::list);
    IfcSchema::IfcTrimmingSelect::list::ptr trim2(new IfcSchema::IfcTrimmingSelect::list);
	
	trim1->push(new IfcSchema::IfcParameterValue(180));
	trim1->push(p2);

	trim2->push(new IfcSchema::IfcParameterValue(270));
	trim2->push(p4);
	
	IfcSchema::IfcTrimmedCurve* trimmed_curve = new IfcSchema::IfcTrimmedCurve(circle, trim1, trim2, false, IfcSchema::IfcTrimmingPreference::IfcTrimmingPreference_PARAMETER);
	file.addEntity(trimmed_curve);

	IfcSchema::IfcCompositeCurveSegment* segment2 = new IfcSchema::IfcCompositeCurveSegment(IfcSchema::IfcTransitionCode::IfcTransitionCode_CONTSAMEGRADIENT, false, trimmed_curve);
	file.addEntity(segment2);
	segments->push(segment2);

	/*third segment - line */
	IfcSchema::IfcCartesianPoint::list::ptr points2(new IfcSchema::IfcCartesianPoint::list());
	points2->push(p4);
	points2->push(p5);
	file.addEntities(points2->generalize());
	IfcSchema::IfcPolyline* poly2 = new IfcSchema::IfcPolyline(points2);
	file.addEntity(poly2);

	IfcSchema::IfcCompositeCurveSegment* segment3 = new IfcSchema::IfcCompositeCurveSegment(IfcSchema::IfcTransitionCode::IfcTransitionCode_CONTINUOUS, true, poly2);
	file.addEntity(segment3);
	segments->push(segment3);

	IfcSchema::IfcCompositeCurve* curve = new IfcSchema::IfcCompositeCurve(segments, false);
	file.addEntity(curve);

	IfcSchema::IfcSweptDiskSolid* solid = new IfcSchema::IfcSweptDiskSolid(curve, dia / 2, null, 0, 1);

	IfcSchema::IfcRepresentation::list::ptr reps(new IfcSchema::IfcRepresentation::list());
	IfcSchema::IfcRepresentationItem::list::ptr items(new IfcSchema::IfcRepresentationItem::list());
	items->push(solid);
	IfcSchema::IfcShapeRepresentation* rep = new IfcSchema::IfcShapeRepresentation(
		file.getSingle<IfcSchema::IfcRepresentationContext>(), S("Body"), S("AdvancedSweptSolid"), items);
	reps->push(rep);

	IfcSchema::IfcProductDefinitionShape* shape = new IfcSchema::IfcProductDefinitionShape(null, null, reps);
	file.addEntity(shape);

	rebar->setRepresentation(shape);

	IfcSchema::IfcObjectPlacement* storey_placement = file.getSingle<IfcSchema::IfcBuildingStorey>()->ObjectPlacement();
	rebar->setObjectPlacement(file.addLocalPlacement(storey_placement, 0, 0, 0));
}

int main()
{
	IfcHierarchyHelper<IfcSchema> file;
	file.header().file_name()->setname("ifc_curve_rebar.ifc");
	create_curve_rebar(file);
	std::ofstream f("ifc_curve_rebar.ifc");
	f << file;

	return 0;
}
