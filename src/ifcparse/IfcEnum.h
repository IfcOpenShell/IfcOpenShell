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

#ifndef IFC_ENUM_H
#define IFC_ENUM_H

#include <string>
#ifdef _MSC_VER
  #define strcasecmp _stricmp
#else
  #include <strings.h>
#endif

namespace IfcSchema {
	namespace Enum {

		enum IfcTypes {

#define IFC_PARSE_ENUM
#include "../ifcparse/IfcSchema.h"
#undef IFC_PARSE_ENUM

			IfcUnknown,
			IfcDontCare,
			ALL
		};
		IfcTypes FromString(const std::string& a);
		std::string ToString(IfcTypes t);
		bool ShouldRender(IfcTypes t);
	}
}
#endif
