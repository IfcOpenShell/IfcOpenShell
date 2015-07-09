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
 * Example that generates extrusions of parameterized profiles.                 *
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

int main(int argc, char** argv) {
	const char filename[] = "IfcCompositeProfileDef.ifc";
	IfcHierarchyHelper file;
	file.header().file_name().name(filename);

	double coords1[] = {100.0, 0.0};
	double coords2[] = {200.0, 0.0};
	double coords3[] = {300.0, 0.0};

	IfcSchema::IfcProfileDef::list::ptr profiles (new IfcSchema::IfcProfileDef::list());

	IfcSchema::IfcCartesianTransformationOperator2D* transform1 = new IfcSchema::IfcCartesianTransformationOperator2D(file.addDoublet<IfcSchema::IfcDirection>(1, 0), file.addDoublet<IfcSchema::IfcDirection>(0, -1), file.addDoublet<IfcSchema::IfcCartesianPoint>(40, 0), null);
	IfcSchema::IfcCartesianTransformationOperator2D* transform2 = new IfcSchema::IfcCartesianTransformationOperator2D(file.addDoublet<IfcSchema::IfcDirection>(0, -1), file.addDoublet<IfcSchema::IfcDirection>(1, 0), file.addDoublet<IfcSchema::IfcCartesianPoint>(40, 0), 0.3);
	
	IfcSchema::IfcProfileDef* p1 = new Ifc2x3::IfcIShapeProfileDef(
		IfcSchema::IfcProfileTypeEnum::IfcProfileType_AREA,
		null, file.addPlacement2d(),    25.0,    50.0,     5.0,     5.0,     2.0);

	IfcSchema::IfcProfileDef* p2 = new Ifc2x3::IfcLShapeProfileDef(
		IfcSchema::IfcProfileTypeEnum::IfcProfileType_AREA,
		null, file.addPlacement2d(),    50.0,    25.0,     5.0,      1.0,     2.0,     2.0,    null,    null);

	IfcSchema::IfcProfileDef* p3 = new Ifc2x3::IfcTShapeProfileDef(
		IfcSchema::IfcProfileTypeEnum::IfcProfileType_AREA,
		null, file.addPlacement2d(),    50.0,    40.0,    10.0,     10.0,     3.0,     2.0,     1.0,     2.0,     2.0,    null);

	IfcSchema::IfcProfileDef* p4 = new Ifc2x3::IfcCShapeProfileDef(
		IfcSchema::IfcProfileTypeEnum::IfcProfileType_AREA,
		null, file.addPlacement2d(80.),    50.0,    25.0,     5.0,    10.0,     2.0,    null);

	file.addEntity(p2);
	file.addEntity(p3);
	
	file.addEntity(transform1);
	file.addEntity(transform2);
	
	IfcSchema::IfcDerivedProfileDef* p5 = new IfcSchema::IfcDerivedProfileDef(IfcSchema::IfcProfileTypeEnum::IfcProfileType_AREA, null, p2, transform1, null);
	IfcSchema::IfcDerivedProfileDef* p6 = new IfcSchema::IfcDerivedProfileDef(IfcSchema::IfcProfileTypeEnum::IfcProfileType_AREA, null, p3, transform2, null);
	
	profiles->push(p1);
	profiles->push(p5);
	profiles->push(p6);
	profiles->push(p4);

	file.addEntities(profiles->generalize());

	IfcSchema::IfcCompositeProfileDef* composite = new IfcSchema::IfcCompositeProfileDef(IfcSchema::IfcProfileTypeEnum::IfcProfileType_AREA, S("IFC"), profiles, null);

	IfcSchema::IfcBuildingElementProxy* product = new IfcSchema::IfcBuildingElementProxy(
			guid(), 0, S("profile"), null, null, 0, 0, null, null);

	file.addBuildingProduct(product);

	product->setOwnerHistory(file.getSingle<IfcSchema::IfcOwnerHistory>());

	product->setObjectPlacement(file.addLocalPlacement());

	IfcSchema::IfcExtrudedAreaSolid* solid = new IfcSchema::IfcExtrudedAreaSolid(composite,
		file.addPlacement3d(), file.addTriplet<IfcSchema::IfcDirection>(0, 0, 1), 20.0);

	file.addEntity(composite);
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

	file.getSingle<IfcSchema::IfcProject>()->setName("IfcCompositeProfileDef");

	std::ofstream f(filename);
	f << file;
}
