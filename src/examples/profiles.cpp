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

#include "ifcparse/macros.h"

#ifndef IfcSchema
#define IfcSchema Ifc2x3
#endif

#include INCLUDE_SCHEMA(ifcparse/schemas, IfcSchema)
#include INCLUDE_SCHEMA_DEFINITIONS(ifcparse/schemas, IfcSchema)

#include "ifcparse/hierarchy_helper.h"
#include "ifcparse/global_id.h"

typedef std::string S;
typedef ifcopenshell::global_id guid;
boost::none_t const null = (static_cast<boost::none_t>(0));

#ifdef SCHEMA_IfcUShapeProfileDef_HAS_CentreOfGravityInX
#define IFC_U_SHAPE_PROFILE_DEF_EXTRA_ARGS , null
#else
#define IFC_U_SHAPE_PROFILE_DEF_EXTRA_ARGS
#endif

#ifdef SCHEMA_IfcTShapeProfileDef_HAS_CentreOfGravityInY
#define IFC_T_SHAPE_PROFILE_DEF_EXTRA_ARGS , null
#else
#define IFC_T_SHAPE_PROFILE_DEF_EXTRA_ARGS
#endif

#ifdef SCHEMA_IfcIShapeProfileDef_HAS_FlangeEdgeRadius
#define IFC_I_SHAPE_PROFILE_DEF_EXTRA_ARGS , null, null
#else
#define IFC_I_SHAPE_PROFILE_DEF_EXTRA_ARGS
#endif

#ifdef SCHEMA_IfcAsymmetricIShapeProfileDef_HAS_BottomFlangeSlope
#define IFC_ASYMMETRIC_I_SHAPE_PROFILE_DEF_EXTRA_ARGS , null, null, null
#else
#define IFC_ASYMMETRIC_I_SHAPE_PROFILE_DEF_EXTRA_ARGS
#endif

#ifdef SCHEMA_IfcLShapeProfileDef_HAS_CentreOfGravityInX
#define IFC_L_SHAPE_PROFILE_DEF_EXTRA_ARGS , null, null
#else
#define IFC_L_SHAPE_PROFILE_DEF_EXTRA_ARGS
#endif

#ifdef SCHEMA_IfcCShapeProfileDef_HAS_CentreOfGravityInX
#define IFC_C_SHAPE_PROFILE_DEF_EXTRA_ARGS , null
#else
#define IFC_C_SHAPE_PROFILE_DEF_EXTRA_ARGS
#endif

void create_testcase_for(IfcSchema::IfcProfileDef::list::ptr profiles) {
	IfcSchema::IfcProfileDef* profile = *profiles->begin();
	const std::string profile_type = IfcSchema::Type::ToString(profile->type());
	const std::string filename = profile_type + ".ifc";
	
	hierarchy_helper file;
	file.filename(filename);
	
	int i = 0;
	for (IfcSchema::IfcProfileDef::list::it it = profiles->begin(); it != profiles->end(); ++it, ++i) {
		IfcSchema::IfcProfileDef* profile = *it;
		IfcSchema::IfcBuildingElementProxy* product = new IfcSchema::IfcBuildingElementProxy(
			guid(), 0, S("profile"), null, null, 0, 0, null, null);
		file.addBuildingProduct(product);
		file.getSingle<IfcSchema::IfcProject>()->setName(profile_type);
		product->setOwnerHistory(file.getSingle<IfcSchema::IfcOwnerHistory>());

		product->setObjectPlacement(file.addLocalPlacement(0, 100. * i));

		if (profile->is(IfcSchema::Type::IfcParameterizedProfileDef)) {
			((IfcSchema::IfcParameterizedProfileDef*) profile)->setPosition(file.addPlacement2d());
		}

		IfcSchema::IfcExtrudedAreaSolid* solid = new IfcSchema::IfcExtrudedAreaSolid(profile,
			file.addPlacement3d(), file.addTriplet<IfcSchema::IfcDirection>(0, 0, 1), 20.0);

		file.add_entity(profile);
		file.add_entity(solid);
		
		IfcSchema::IfcRepresentation::list::ptr reps (new IfcSchema::IfcRepresentation::list);
		IfcSchema::IfcRepresentationItem::list::ptr items (new IfcSchema::IfcRepresentationItem::list);
		
		items->push(solid);
		IfcSchema::IfcShapeRepresentation* rep = new IfcSchema::IfcShapeRepresentation(
			file.getSingle<IfcSchema::IfcRepresentationContext>(), S("Body"), S("SweptSolid"), items);
		reps->push(rep);

		IfcSchema::IfcProductDefinitionShape* shape = new IfcSchema::IfcProductDefinitionShape(0, 0, reps);
		file.add_entity(rep);
		file.add_entity(shape);
		
		product->setRepresentation(shape);
	}
	
	std::ofstream f(filename.c_str());
	f << file;
}

int main(int argc, char** argv) {
	{ IfcSchema::IfcProfileDef::list::ptr profiles (new IfcSchema::IfcProfileDef::list);
	profiles->push(new Ifc2x3::IfcUShapeProfileDef(
		IfcSchema::IfcProfileTypeEnum::IfcProfileType_AREA,
		null, 0,    50.0,    25.0,     5.0,     5.0,    null,    null,    null IFC_U_SHAPE_PROFILE_DEF_EXTRA_ARGS));
	profiles->push(new IfcSchema::IfcUShapeProfileDef(
		IfcSchema::IfcProfileTypeEnum::IfcProfileType_AREA,
		null, 0,    50.0,    25.0,     5.0,     5.0,     2.0,     2.0,    null IFC_U_SHAPE_PROFILE_DEF_EXTRA_ARGS));
	profiles->push(new IfcSchema::IfcUShapeProfileDef(
		IfcSchema::IfcProfileTypeEnum::IfcProfileType_AREA,
		null, 0,    50.0,    25.0,     5.0,     5.0,    null,    null,     4.0 IFC_U_SHAPE_PROFILE_DEF_EXTRA_ARGS));
	profiles->push(new IfcSchema::IfcUShapeProfileDef(
		IfcSchema::IfcProfileTypeEnum::IfcProfileType_AREA,
		null, 0,    50.0,    25.0,     5.0,     5.0,     1.0,     3.0,     6.0 IFC_U_SHAPE_PROFILE_DEF_EXTRA_ARGS));
	create_testcase_for(profiles); }
	
    { IfcSchema::IfcProfileDef::list::ptr profiles (new IfcSchema::IfcProfileDef::list);
	profiles->push(new Ifc2x3::IfcTShapeProfileDef(
		IfcSchema::IfcProfileTypeEnum::IfcProfileType_AREA,
		null, 0,    50.0,    25.0,     5.0,     5.0,    null,    null,    null,    null,    null IFC_T_SHAPE_PROFILE_DEF_EXTRA_ARGS));
	profiles->push(new IfcSchema::IfcTShapeProfileDef(
		IfcSchema::IfcProfileTypeEnum::IfcProfileType_AREA,
		null, 0,    50.0,    25.0,     5.0,     5.0,     2.0,     2.0,     2.0,    null,    null IFC_T_SHAPE_PROFILE_DEF_EXTRA_ARGS));
	profiles->push(new IfcSchema::IfcTShapeProfileDef(
		IfcSchema::IfcProfileTypeEnum::IfcProfileType_AREA,
		null, 0,    50.0,    25.0,     5.0,     5.0,    null,    null,    null,     2.0,     2.0 IFC_T_SHAPE_PROFILE_DEF_EXTRA_ARGS));
	profiles->push(new IfcSchema::IfcTShapeProfileDef(
		IfcSchema::IfcProfileTypeEnum::IfcProfileType_AREA,
		null, 0,    50.0,    25.0,     5.0,     5.0,     3.0,     2.0,     1.0,     2.0,     2.0 IFC_T_SHAPE_PROFILE_DEF_EXTRA_ARGS));
	create_testcase_for(profiles); }
	
    { IfcSchema::IfcProfileDef::list::ptr profiles (new IfcSchema::IfcProfileDef::list);
	profiles->push(new Ifc2x3::IfcZShapeProfileDef(
		IfcSchema::IfcProfileTypeEnum::IfcProfileType_AREA,
		null, 0,    50.0,    25.0,     5.0,     5.0,    null,    null));
	profiles->push(new Ifc2x3::IfcZShapeProfileDef(
		IfcSchema::IfcProfileTypeEnum::IfcProfileType_AREA,
		null, 0,    50.0,    25.0,     5.0,     5.0,     2.0,     2.0));
	create_testcase_for(profiles); }
	
    { IfcSchema::IfcProfileDef::list::ptr profiles (new IfcSchema::IfcProfileDef::list);
	profiles->push(new Ifc2x3::IfcEllipseProfileDef(
		IfcSchema::IfcProfileTypeEnum::IfcProfileType_AREA,
		null, 0,    25.0,    15.0));
	profiles->push(new Ifc2x3::IfcEllipseProfileDef(
		IfcSchema::IfcProfileTypeEnum::IfcProfileType_AREA,
		null, 0,    15.0,    25.0));
	create_testcase_for(profiles); }
	
	{ IfcSchema::IfcProfileDef::list::ptr profiles (new IfcSchema::IfcProfileDef::list);
	profiles->push(new IfcSchema::IfcIShapeProfileDef(
		IfcSchema::IfcProfileTypeEnum::IfcProfileType_AREA,
		null, 0,    25.0,    50.0,     5.0,     5.0,    null IFC_I_SHAPE_PROFILE_DEF_EXTRA_ARGS));
	profiles->push(new IfcSchema::IfcIShapeProfileDef(
		IfcSchema::IfcProfileTypeEnum::IfcProfileType_AREA,
		null, 0,    25.0,    50.0,     5.0,     5.0,     2.0 IFC_I_SHAPE_PROFILE_DEF_EXTRA_ARGS));
	profiles->push(new IfcSchema::IfcAsymmetricIShapeProfileDef(
		IfcSchema::IfcProfileTypeEnum::IfcProfileType_AREA,
		null, 0,    25.0,    50.0,     5.0,     5.0,     2.0, 20.0, 10.0, 5.0, null IFC_ASYMMETRIC_I_SHAPE_PROFILE_DEF_EXTRA_ARGS));
	create_testcase_for(profiles); }

    { IfcSchema::IfcProfileDef::list::ptr profiles (new IfcSchema::IfcProfileDef::list);
	profiles->push(new Ifc2x3::IfcLShapeProfileDef(
		IfcSchema::IfcProfileTypeEnum::IfcProfileType_AREA,
		null, 0,    50.0,    25.0,     5.0,     null,    null,    null IFC_L_SHAPE_PROFILE_DEF_EXTRA_ARGS));
	profiles->push(new IfcSchema::IfcLShapeProfileDef(
		IfcSchema::IfcProfileTypeEnum::IfcProfileType_AREA,
		null, 0,    50.0,    25.0,     5.0,     2.0,      2.0,    null IFC_L_SHAPE_PROFILE_DEF_EXTRA_ARGS));
	profiles->push(new IfcSchema::IfcLShapeProfileDef(
		IfcSchema::IfcProfileTypeEnum::IfcProfileType_AREA,
		null, 0,    50.0,    25.0,     5.0,     null,    null,     2.0 IFC_L_SHAPE_PROFILE_DEF_EXTRA_ARGS));
	profiles->push(new IfcSchema::IfcLShapeProfileDef(
		IfcSchema::IfcProfileTypeEnum::IfcProfileType_AREA,
		null, 0,    50.0,    25.0,     5.0,      1.0,     2.0,     2.0 IFC_L_SHAPE_PROFILE_DEF_EXTRA_ARGS));
	create_testcase_for(profiles); }
	
    { IfcSchema::IfcProfileDef::list::ptr profiles (new IfcSchema::IfcProfileDef::list);
	profiles->push(new Ifc2x3::IfcCShapeProfileDef(
		IfcSchema::IfcProfileTypeEnum::IfcProfileType_AREA,
		null, 0,    50.0,    25.0,     5.0,    10.0,    null IFC_C_SHAPE_PROFILE_DEF_EXTRA_ARGS));
	profiles->push(new IfcSchema::IfcCShapeProfileDef(
		IfcSchema::IfcProfileTypeEnum::IfcProfileType_AREA,
		null, 0,    50.0,    25.0,     5.0,    10.0,     2.0 IFC_C_SHAPE_PROFILE_DEF_EXTRA_ARGS));
	create_testcase_for(profiles); }

    { IfcSchema::IfcProfileDef::list::ptr profiles (new IfcSchema::IfcProfileDef::list);
	profiles->push(new Ifc2x3::IfcCircleProfileDef(
		IfcSchema::IfcProfileTypeEnum::IfcProfileType_AREA,
		null, 0,    25.0));
	profiles->push(new Ifc2x3::IfcCircleHollowProfileDef(
		IfcSchema::IfcProfileTypeEnum::IfcProfileType_AREA,
		null, 0,    25.0,     5.0));
	create_testcase_for(profiles); }
	
    { IfcSchema::IfcProfileDef::list::ptr profiles (new IfcSchema::IfcProfileDef::list);
	profiles->push(new Ifc2x3::IfcRectangleProfileDef(
		IfcSchema::IfcProfileTypeEnum::IfcProfileType_AREA,
		null, 0,    50.0,    25.0));
	profiles->push(new Ifc2x3::IfcRoundedRectangleProfileDef(
		IfcSchema::IfcProfileTypeEnum::IfcProfileType_AREA,
		null, 0,    50.0,    25.0,     5.0));
	profiles->push(new Ifc2x3::IfcRectangleHollowProfileDef(
		IfcSchema::IfcProfileTypeEnum::IfcProfileType_AREA,
		null, 0,    50.0,    25.0,     5.0,    null,    null));
	profiles->push(new Ifc2x3::IfcRectangleHollowProfileDef(
		IfcSchema::IfcProfileTypeEnum::IfcProfileType_AREA,
		null, 0,    50.0,    25.0,     5.0,     2.0,     4.0));
	create_testcase_for(profiles); }
	
    { IfcSchema::IfcProfileDef::list::ptr profiles (new IfcSchema::IfcProfileDef::list);
	profiles->push(new Ifc2x3::IfcTrapeziumProfileDef(
		IfcSchema::IfcProfileTypeEnum::IfcProfileType_AREA,
		null, 0,    50.0,    30.0,    25.0,     0.0));
	profiles->push(new Ifc2x3::IfcTrapeziumProfileDef(
		IfcSchema::IfcProfileTypeEnum::IfcProfileType_AREA,
		null, 0,    50.0,    60.0,    25.0,   -20.0));
	profiles->push(new Ifc2x3::IfcTrapeziumProfileDef(
		IfcSchema::IfcProfileTypeEnum::IfcProfileType_AREA,
		null, 0,    50.0,    10.0,    25.0,    30.0));
	create_testcase_for(profiles); }
}
