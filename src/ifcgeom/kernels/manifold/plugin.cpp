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
#include "manifold_kernel.h"

#include <boost/dll/alias.hpp>

namespace ifcopenshell {
	namespace geom {
		namespace kernels {
			namespace manifold_plugin {

				plugin::abi_info plugin_abi() {
					return plugin::host_abi();
				}

				plugin::metadata plugin_metadata() {
					return kernel_plugin_metadata("manifold");
				}

				abstract_kernel* create_kernel(ifcopenshell::file*, ifcopenshell::geom::settings& settings, ifcopenshell::logger& logger) {
					return new manifold_kernel(settings, logger);
				}

				void register_plugin(kernel_registry& registry, const plugin::module& module) {
					kernel_info info;
					info.backend_id = "manifold";
					info.supports_boolean_operations = true;
					registry.bind(info, create_kernel, module);
				}

			}
		}
	}
}

BOOST_DLL_ALIAS(ifcopenshell::geom::kernels::manifold_plugin::plugin_abi, ifcopenshell_plugin_abi_v1)
BOOST_DLL_ALIAS(ifcopenshell::geom::kernels::manifold_plugin::plugin_metadata, ifcopenshell_plugin_metadata_v1)
BOOST_DLL_ALIAS(ifcopenshell::geom::kernels::manifold_plugin::register_plugin, ifcopenshell_register_kernel_plugin_v1)

#ifdef __EMSCRIPTEN__
#define CAT(a, b) a##b
#define EXPAND_AND_CAT(a, b) CAT(a, b)
#define emscripten_register_kernel_plugin EXPAND_AND_CAT(ifcopenshell_emscripten_register_kernel_, IFCOPENSHELL_WASM_PLUGIN_ID)

extern "C" void emscripten_register_kernel_plugin(ifcopenshell::geom::kernels::kernel_registry* registry) {
	ifcopenshell::geom::kernels::manifold_plugin::register_plugin(
		*registry,
		ifcopenshell::plugin::module::builtin(ifcopenshell::geom::kernels::manifold_plugin::plugin_metadata()));
}
#endif
