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
#include "cgal_kernel.h"

#include <boost/dll/alias.hpp>

#ifdef IFOPSH_SIMPLE_KERNEL
#define cgal_plugin cgalsimple_plugin
#endif

namespace ifcopenshell {
	namespace geom {
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
				using kernel_type = cgal_kernel;
#endif

				plugin::abi_info plugin_abi() {
					return plugin::host_abi();
				}

				plugin::metadata plugin_metadata() {
					return kernel_plugin_metadata(plugin_name);
				}

				abstract_kernel* create_kernel(ifcopenshell::file*, ifcopenshell::geom::settings& settings, ifcopenshell::logger& logger) {
					return new kernel_type(settings, logger);
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

BOOST_DLL_ALIAS(ifcopenshell::geom::kernels::cgal_plugin::plugin_abi, ifcopenshell_plugin_abi_v1)
BOOST_DLL_ALIAS(ifcopenshell::geom::kernels::cgal_plugin::plugin_metadata, ifcopenshell_plugin_metadata_v1)
BOOST_DLL_ALIAS(ifcopenshell::geom::kernels::cgal_plugin::register_plugin, ifcopenshell_register_kernel_plugin_v1)

#ifdef __EMSCRIPTEN__
#define CAT(a, b) a##b
#define EXPAND_AND_CAT(a, b) CAT(a, b)
#define emscripten_register_kernel_plugin EXPAND_AND_CAT(ifcopenshell_emscripten_register_kernel_, IFCOPENSHELL_WASM_PLUGIN_ID)

extern "C" void emscripten_register_kernel_plugin(ifcopenshell::geom::kernels::kernel_registry* registry) {
	ifcopenshell::geom::kernels::cgal_plugin::register_plugin(
		*registry,
		ifcopenshell::plugin::module::builtin(ifcopenshell::geom::kernels::cgal_plugin::plugin_metadata()));
}
#endif
