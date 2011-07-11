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

#include "../ifcparse/IfcEnum.h"

IfcSchema::Enum::IfcTypes IfcSchema::Enum::FromString(const std::string& a) {

#define IFC_PARSE_STR_ENUM
#include "../ifcparse/IfcSchema.h"
#undef IFC_PARSE_STR_ENUM

	return IfcUnknown;
}

std::string IfcSchema::Enum::ToString(IfcTypes t) {
	std::string r = "Ifc";
	r.reserve(64);

#define IFC_PARSE_ENUM_STR
#include "../ifcparse/IfcSchema.h"
#undef IFC_PARSE_ENUM_STR

	return "IfcUnknown";
}

bool IfcSchema::Enum::ShouldRender(IfcTypes t) {
	if ( t == IfcUnknown ) return false;
#define IFC_PARSE_RENDER
#include "../ifcparse/IfcSchema.h"
#undef IFC_PARSE_RENDER
	else return false;
}