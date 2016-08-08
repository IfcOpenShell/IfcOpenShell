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

#ifndef IFCSIPREFIX
#define IFCSIPREFIX

#include "../ifcparse/IfcParse.h"
#include "ifc_parse_api.h"

namespace IfcParse {
    IFC_PARSE_API double IfcSIPrefixToValue(IfcSchema::IfcSIPrefix::IfcSIPrefix);
    IFC_PARSE_API double get_SI_equivalent(IfcSchema::IfcNamedUnit*);
}

#endif
