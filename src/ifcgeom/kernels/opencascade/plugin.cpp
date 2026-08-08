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
#include "opencascade_kernel.h"

#include <boost/dll/alias.hpp>

namespace ifcopenshell {
	namespace geom {
		namespace kernels {
			namespace opencascade_plugin {

				plugin::abi_info plugin_abi() {
					return plugin::host_abi();
				}

				plugin::metadata plugin_metadata() {
					return kernel_plugin_metadata("opencascade");
				}

				abstract_kernel* create_kernel(ifcopenshell::file*, ifcopenshell::geom::settings& settings) {
					return new ifcopenshell::geom::open_cascade_kernel(settings);
				}

				void register_plugin(kernel_registry& registry, const plugin::module& module) {
					kernel_info info;
					info.backend_id = "opencascade";
					info.supports_boolean_operations = true;
					registry.bind(info, create_kernel, module);
				}

			}
		}
	}
}

BOOST_DLL_ALIAS(ifcopenshell::geom::kernels::opencascade_plugin::plugin_abi, ifcopenshell_plugin_abi_v1)
BOOST_DLL_ALIAS(ifcopenshell::geom::kernels::opencascade_plugin::plugin_metadata, ifcopenshell_plugin_metadata_v1)
BOOST_DLL_ALIAS(ifcopenshell::geom::kernels::opencascade_plugin::register_plugin, ifcopenshell_register_kernel_plugin_v1)
