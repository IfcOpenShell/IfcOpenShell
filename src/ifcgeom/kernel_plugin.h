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

#ifndef IFCOPENSHELL_KERNEL_PLUGIN_H
#define IFCOPENSHELL_KERNEL_PLUGIN_H

#include "../ifcgeom/kernel_registry.h"

#include <filesystem>

namespace ifcopenshell {
	namespace geom {
		namespace kernels {

			typedef void register_kernel_plugin_fn(kernel_registry&, const ifcopenshell::plugin::module&);

			IFC_GEOM_API const char* kernel_plugin_registration_symbol();
			IFC_GEOM_API ifcopenshell::plugin::metadata kernel_plugin_metadata(const std::string& plugin_name);
			IFC_GEOM_API std::filesystem::path kernel_plugin_directory();
			IFC_GEOM_API void load_kernel_plugins(kernel_registry& registry);
			IFC_GEOM_API bool load_kernel_plugin(kernel_registry& registry, const std::string& backend_id);

		}
	}
}

#endif
