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

#ifndef ARGUMENTTYPE_H
#define ARGUMENTTYPE_H

#include "ifc_parse_api.h"
#include "IfcSchema.h"

namespace IfcUtil {

enum ArgumentType {
    Argument_NULL,
    Argument_DERIVED,
    Argument_INT,
    Argument_BOOL,
    Argument_LOGICAL,
    Argument_DOUBLE,
    Argument_STRING,
    Argument_BINARY,
    Argument_ENUMERATION,
    Argument_ENTITY_INSTANCE,

    Argument_EMPTY_AGGREGATE,
    Argument_AGGREGATE_OF_INT,
    Argument_AGGREGATE_OF_DOUBLE,
    Argument_AGGREGATE_OF_STRING,
    Argument_AGGREGATE_OF_BINARY,
    Argument_AGGREGATE_OF_ENTITY_INSTANCE,

    Argument_AGGREGATE_OF_EMPTY_AGGREGATE,
    Argument_AGGREGATE_OF_AGGREGATE_OF_INT,
    Argument_AGGREGATE_OF_AGGREGATE_OF_DOUBLE,
    Argument_AGGREGATE_OF_AGGREGATE_OF_ENTITY_INSTANCE,

    Argument_UNKNOWN
};

IFC_PARSE_API ArgumentType from_parameter_type(const IfcParse::parameter_type*);
IFC_PARSE_API ArgumentType make_aggregate(ArgumentType elem_type);
} // namespace IfcUtil

#endif
