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

#include "mapping.h"

#include "../../ifcparse/IfcLogger.h"

using namespace IfcUtil;

ifcopenshell::geometry::taxonomy::item* ifcopenshell::geometry::POSTFIX_SCHEMA(mapping)::map(const IfcBaseClass* l) {
#include "bind_convert_impl.i"
	Logger::Message(Logger::LOG_ERROR, "No operation defined for:", l);
	return nullptr;
}
