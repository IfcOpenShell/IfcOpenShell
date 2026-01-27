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

#define IfcSchema Ifc2x3
#include "ifcparse/Ifc2x3.h"
#include "ifcparse/IfcHierarchyHelper.h"

typedef std::string S;
typedef IfcParse::IfcGlobalId guid;
boost::none_t const null = boost::none;

void create_testcase_for(IfcSchema::IfcProfileDef::list::ptr profiles) {
	IfcSchema::IfcProfileDef* profile = *profiles->begin();
	const std::string& profile_type = profile->declaration().name();
	const std::string filename = profile_type + ".ifc";
	
	IfcHierarchyHelper<IfcSchema> file;
	file.header().file_name()->setname(filename);
	
	int i = 0;
	for (IfcSchema::IfcProfileDef::list::it it = profiles->begin(); it != profiles->end(); ++it, ++i) {
		IfcSchema::IfcProfileDef* profile = *it;
		IfcSchema::IfcBuildingElementProxy* product = new IfcSchema::IfcBuildingElementProxy(
			guid(), 0, S("profile"), null, null, 0, 0, null, null);
		file.addBuildingProduct(product);
		file.getSingle<IfcSchema::IfcProject>()->setName(profile_type);
		product->setOwnerHistory(file.getSingle<IfcSchema::IfcOwnerHistory>());

		product->setObjectPlacement(file.addLocalPlacement(0, 100. * i));

		if (profile->declaration().is(IfcSchema::IfcParameterizedProfileDef::Class())) {
			((IfcSchema::IfcParameterizedProfileDef*) profile)->setPosition(file.addPlacement2d());
		}

		IfcSchema::IfcExtrudedAreaSolid* solid = new IfcSchema::IfcExtrudedAreaSolid(profile,
			file.addPlacement3d(), file.addTriplet<IfcSchema::IfcDirection>(0, 0, 1), 20.0);

		file.addEntity(profile);
		file.addEntity(solid);
		
		IfcSchema::IfcRepresentation::list::ptr reps (new IfcSchema::IfcRepresentation::list);
		IfcSchema::IfcRepresentationItem::list::ptr items (new IfcSchema::IfcRepresentationItem::list);
		
		items->push(solid);
		IfcSchema::IfcShapeRepresentation* rep = new IfcSchema::IfcShapeRepresentation(
			file.getSingle<IfcSchema::IfcRepresentationContext>(), S("Body"), S("SweptSolid"), items);
		reps->push(rep);

		IfcSchema::IfcProductDefinitionShape* shape = new IfcSchema::IfcProductDefinitionShape(null, null, reps);
		file.addEntity(rep);
		file.addEntity(shape);
		
		product->setRepresentation(shape);
	}
	
	std::ofstream f(filename.c_str());
	f << file;
}

int main(int argc, char** argv) {
    IfcSchema::get_schema();  // Ensure schema is initialized
	{ IfcSchema::IfcProfileDef::list::ptr profiles (new IfcSchema::IfcProfileDef::list);
	profiles->push(new IfcSchema::IfcUShapeProfileDef(
		IfcSchema::IfcProfileTypeEnum::IfcProfileType_AREA,
		null, 0,    50.0,    25.0,     5.0,     5.0,    null,    null,    null,    null));
	profiles->push(new IfcSchema::IfcUShapeProfileDef(
		IfcSchema::IfcProfileTypeEnum::IfcProfileType_AREA,
		null, 0,    50.0,    25.0,     5.0,     5.0,     2.0,     2.0,    null,    null));
	profiles->push(new IfcSchema::IfcUShapeProfileDef(
		IfcSchema::IfcProfileTypeEnum::IfcProfileType_AREA,
		null, 0,    50.0,    25.0,     5.0,     5.0,    null,    null,     4.0,    null));
	profiles->push(new IfcSchema::IfcUShapeProfileDef(
		IfcSchema::IfcProfileTypeEnum::IfcProfileType_AREA,
		null, 0,    50.0,    25.0,     5.0,     5.0,     1.0,     3.0,     6.0,    null));
	create_testcase_for(profiles); }
	
    { IfcSchema::IfcProfileDef::list::ptr profiles (new IfcSchema::IfcProfileDef::list);
	profiles->push(new IfcSchema::IfcTShapeProfileDef(
		IfcSchema::IfcProfileTypeEnum::IfcProfileType_AREA,
		null, 0,    50.0,    25.0,     5.0,     5.0,    null,    null,    null,    null,    null,    null));
	profiles->push(new IfcSchema::IfcTShapeProfileDef(
		IfcSchema::IfcProfileTypeEnum::IfcProfileType_AREA,
		null, 0,    50.0,    25.0,     5.0,     5.0,     2.0,     2.0,     2.0,    null,    null,    null));
	profiles->push(new IfcSchema::IfcTShapeProfileDef(
		IfcSchema::IfcProfileTypeEnum::IfcProfileType_AREA,
		null, 0,    50.0,    25.0,     5.0,     5.0,    null,    null,    null,     2.0,     2.0,    null));
	profiles->push(new IfcSchema::IfcTShapeProfileDef(
		IfcSchema::IfcProfileTypeEnum::IfcProfileType_AREA,
		null, 0,    50.0,    25.0,     5.0,     5.0,     3.0,     2.0,     1.0,     2.0,     2.0,    null));
	create_testcase_for(profiles); }
	
    { IfcSchema::IfcProfileDef::list::ptr profiles (new IfcSchema::IfcProfileDef::list);
	profiles->push(new IfcSchema::IfcZShapeProfileDef(
		IfcSchema::IfcProfileTypeEnum::IfcProfileType_AREA,
		null, 0,    50.0,    25.0,     5.0,     5.0,    null,    null));
	profiles->push(new IfcSchema::IfcZShapeProfileDef(
		IfcSchema::IfcProfileTypeEnum::IfcProfileType_AREA,
		null, 0,    50.0,    25.0,     5.0,     5.0,     2.0,     2.0));
	create_testcase_for(profiles); }
	
    { IfcSchema::IfcProfileDef::list::ptr profiles (new IfcSchema::IfcProfileDef::list);
	profiles->push(new IfcSchema::IfcEllipseProfileDef(
		IfcSchema::IfcProfileTypeEnum::IfcProfileType_AREA,
		null, 0,    25.0,    15.0));
	profiles->push(new IfcSchema::IfcEllipseProfileDef(
		IfcSchema::IfcProfileTypeEnum::IfcProfileType_AREA,
		null, 0,    15.0,    25.0));
	create_testcase_for(profiles); }
	
    { IfcSchema::IfcProfileDef::list::ptr profiles (new IfcSchema::IfcProfileDef::list);
	profiles->push(new IfcSchema::IfcIShapeProfileDef(
		IfcSchema::IfcProfileTypeEnum::IfcProfileType_AREA,
		null, 0,    25.0,    50.0,     5.0,     5.0,    null));
	profiles->push(new IfcSchema::IfcIShapeProfileDef(
		IfcSchema::IfcProfileTypeEnum::IfcProfileType_AREA,
		null, 0,    25.0,    50.0,     5.0,     5.0,     2.0));
	profiles->push(new IfcSchema::IfcAsymmetricIShapeProfileDef(
		IfcSchema::IfcProfileTypeEnum::IfcProfileType_AREA,
		null, 0,    25.0,    50.0,     5.0,     5.0,     2.0, 20.0, 10.0, 5.0, null));
	create_testcase_for(profiles); }

    { IfcSchema::IfcProfileDef::list::ptr profiles (new IfcSchema::IfcProfileDef::list);
	profiles->push(new IfcSchema::IfcLShapeProfileDef(
		IfcSchema::IfcProfileTypeEnum::IfcProfileType_AREA,
		null, 0,    50.0,    25.0,     5.0,     null,    null,    null,    null,    null));
	profiles->push(new IfcSchema::IfcLShapeProfileDef(
		IfcSchema::IfcProfileTypeEnum::IfcProfileType_AREA,
		null, 0,    50.0,    25.0,     5.0,     2.0,      2.0,    null,    null,    null));
	profiles->push(new IfcSchema::IfcLShapeProfileDef(
		IfcSchema::IfcProfileTypeEnum::IfcProfileType_AREA,
		null, 0,    50.0,    25.0,     5.0,     null,    null,     2.0,    null,    null));
	profiles->push(new IfcSchema::IfcLShapeProfileDef(
		IfcSchema::IfcProfileTypeEnum::IfcProfileType_AREA,
		null, 0,    50.0,    25.0,     5.0,      1.0,     2.0,     2.0,    null,    null));
	create_testcase_for(profiles); }
	
    { IfcSchema::IfcProfileDef::list::ptr profiles (new IfcSchema::IfcProfileDef::list);
	profiles->push(new IfcSchema::IfcCShapeProfileDef(
		IfcSchema::IfcProfileTypeEnum::IfcProfileType_AREA,
		null, 0,    50.0,    25.0,     5.0,    10.0,    null,    null));
	profiles->push(new IfcSchema::IfcCShapeProfileDef(
		IfcSchema::IfcProfileTypeEnum::IfcProfileType_AREA,
		null, 0,    50.0,    25.0,     5.0,    10.0,     2.0,    null));
	create_testcase_for(profiles); }

    { IfcSchema::IfcProfileDef::list::ptr profiles (new IfcSchema::IfcProfileDef::list);
	profiles->push(new IfcSchema::IfcCircleProfileDef(
		IfcSchema::IfcProfileTypeEnum::IfcProfileType_AREA,
		null, 0,    25.0));
	profiles->push(new IfcSchema::IfcCircleHollowProfileDef(
		IfcSchema::IfcProfileTypeEnum::IfcProfileType_AREA,
		null, 0,    25.0,     5.0));
	create_testcase_for(profiles); }
	
    { IfcSchema::IfcProfileDef::list::ptr profiles (new IfcSchema::IfcProfileDef::list);
	profiles->push(new IfcSchema::IfcRectangleProfileDef(
		IfcSchema::IfcProfileTypeEnum::IfcProfileType_AREA,
		null, 0,    50.0,    25.0));
	profiles->push(new IfcSchema::IfcRoundedRectangleProfileDef(
		IfcSchema::IfcProfileTypeEnum::IfcProfileType_AREA,
		null, 0,    50.0,    25.0,     5.0));
	profiles->push(new IfcSchema::IfcRectangleHollowProfileDef(
		IfcSchema::IfcProfileTypeEnum::IfcProfileType_AREA,
		null, 0,    50.0,    25.0,     5.0,    null,    null));
	profiles->push(new IfcSchema::IfcRectangleHollowProfileDef(
		IfcSchema::IfcProfileTypeEnum::IfcProfileType_AREA,
		null, 0,    50.0,    25.0,     5.0,     2.0,     4.0));
	create_testcase_for(profiles); }
	
    { IfcSchema::IfcProfileDef::list::ptr profiles (new IfcSchema::IfcProfileDef::list);
	profiles->push(new IfcSchema::IfcTrapeziumProfileDef(
		IfcSchema::IfcProfileTypeEnum::IfcProfileType_AREA,
		null, 0,    50.0,    30.0,    25.0,     0.0));
	profiles->push(new IfcSchema::IfcTrapeziumProfileDef(
		IfcSchema::IfcProfileTypeEnum::IfcProfileType_AREA,
		null, 0,    50.0,    60.0,    25.0,   -20.0));
	profiles->push(new IfcSchema::IfcTrapeziumProfileDef(
		IfcSchema::IfcProfileTypeEnum::IfcProfileType_AREA,
		null, 0,    50.0,    10.0,    25.0,    30.0));
	create_testcase_for(profiles); }
}
