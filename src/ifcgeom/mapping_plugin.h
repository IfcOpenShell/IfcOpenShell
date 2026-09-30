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

#ifndef IFCOPENSHELL_MAPPING_PLUGIN_H
#define IFCOPENSHELL_MAPPING_PLUGIN_H

#include "../ifcgeom/abstract_mapping.h"

#include <filesystem>

namespace ifcopenshell {
	namespace geom {
		namespace impl {

			typedef void register_mapping_plugin_fn(mapping_registry&, const ifcopenshell::plugin::module&);

			IFC_GEOM_API const char* mapping_plugin_registration_symbol();
			IFC_GEOM_API ifcopenshell::plugin::metadata mapping_plugin_metadata(const std::string& schema_name);
			IFC_GEOM_API std::filesystem::path mapping_plugin_directory();
			IFC_GEOM_API void load_mapping_plugins(mapping_registry& registry);
			IFC_GEOM_API bool load_mapping_plugin(mapping_registry& registry, const std::string& schema_name);

		}
	}
}

#endif
