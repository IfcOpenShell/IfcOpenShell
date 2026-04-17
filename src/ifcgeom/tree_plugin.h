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

#ifndef IFCOPENSHELL_TREE_PLUGIN_H
#define IFCOPENSHELL_TREE_PLUGIN_H

#include "tree_registry.h"

#include <filesystem>

namespace ifcopenshell {
	namespace geometry {
		namespace trees {

			typedef void register_tree_plugin_fn(tree_registry&, const ifcopenshell::plugin::module&);

			IFC_GEOM_API const char* tree_plugin_registration_symbol();
			IFC_GEOM_API ifcopenshell::plugin::metadata tree_plugin_metadata(const std::string& plugin_name);
			IFC_GEOM_API std::filesystem::path tree_plugin_directory();
			IFC_GEOM_API void load_tree_plugins(tree_registry& registry);

		}
	}
}

#endif
