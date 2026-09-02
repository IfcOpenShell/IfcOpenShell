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

#ifndef IFCGEOMRENDERSTYLES_H
#define IFCGEOMRENDERSTYLES_H

#include "../ifcgeom/ifc_geom_api.h"
#include "../ifcgeom/taxonomy.h"

#include <boost/algorithm/string/case_conv.hpp>
#include <boost/algorithm/string/replace.hpp>
#include <boost/optional.hpp>

#include <sstream>
#include <memory>

namespace IfcParse {
	class declaration;
}

namespace IfcGeom {
	// Looks up the default (fallback) style registered for `ifc_type`. When no style is
	// registered for that exact type and `decl` is provided, the type's supertype chain
	// (as defined by the IFC schema) is walked until a registered ancestor is found, so
	// e.g. IfcSlabStandardCase inherits the style registered for IfcSlab. Falls back to
	// the generic default style ("*" in a --default-material-file, or a fixed grey) when
	// neither the type nor any of its supertypes have a registered style.
	IFC_GEOM_API const ifcopenshell::geometry::taxonomy::style::ptr& get_default_style(const std::string& ifc_type, const IfcParse::declaration* decl = nullptr);

	IFC_GEOM_API ifcopenshell::geometry::taxonomy::style::ptr& update_default_style(const std::string& ifc_type);

	IFC_GEOM_API void set_default_style_file(const std::string& json_file);
}

#endif
