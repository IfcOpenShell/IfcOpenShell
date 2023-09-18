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

#ifndef IFCOPENSHELL_MACROS_H
#define IFCOPENSHELL_MACROS_H

#define POSTFIX_SCHEMA__(a, b) a##_##b
#define POSTFIX_SCHEMA_(a, b) POSTFIX_SCHEMA__(a, b)
#define POSTFIX_SCHEMA(t) POSTFIX_SCHEMA_(t, IfcSchema)

#define STRINGIFY_(x) #x
#define STRINGIFY(x) STRINGIFY_(x)

#define MAKE_INIT_FN__(a, b) init_##a##_##b
#define MAKE_INIT_FN_(a, b) MAKE_INIT_FN__(a, b)
#define MAKE_INIT_FN(t) MAKE_INIT_FN_(t, IfcSchema)

#endif
