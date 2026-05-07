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

#include "../../kernel_plugin.h"
#include "CgalKernel.h"

#include <boost/dll/alias.hpp>

#ifdef IFOPSH_SIMPLE_KERNEL
#define cgal_plugin cgalsimple_plugin
#endif

namespace ifcopenshell {
	namespace geometry {
		namespace kernels {
		    namespace cgal_plugin {

#ifdef IFOPSH_SIMPLE_KERNEL
				constexpr const char* plugin_name = "cgalsimple";
				constexpr const char* backend_id = "cgal-simple";
				constexpr bool supports_boolean_operations = false;
				using kernel_type = SimpleCgalKernel;
#else
				constexpr const char* plugin_name = "cgal";
				constexpr const char* backend_id = "cgal";
				constexpr bool supports_boolean_operations = true;
				using kernel_type = CgalKernel;
#endif

				plugin::abi_info plugin_abi() {
					return plugin::host_abi();
				}

				plugin::metadata plugin_metadata() {
					return kernel_plugin_metadata(plugin_name);
				}

				AbstractKernel* create_kernel(ifcopenshell::file*, Settings& settings) {
					return new kernel_type(settings);
				}

				void register_plugin(kernel_registry& registry, const plugin::module& module) {
					kernel_info info;
					info.backend_id = backend_id;
					info.supports_boolean_operations = supports_boolean_operations;
					registry.bind(info, create_kernel, module);
				}

			}
		}
	}
}

BOOST_DLL_ALIAS(ifcopenshell::geometry::kernels::cgal_plugin::plugin_abi, ifcopenshell_plugin_abi_v1)
BOOST_DLL_ALIAS(ifcopenshell::geometry::kernels::cgal_plugin::plugin_metadata, ifcopenshell_plugin_metadata_v1)
BOOST_DLL_ALIAS(ifcopenshell::geometry::kernels::cgal_plugin::register_plugin, ifcopenshell_register_kernel_plugin_v1)
