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

#include "../mapping_plugin.h"
#include "mapping.h"

#include <boost/dll/alias.hpp>

namespace ifcopenshell {
	namespace geometry {
		namespace impl {
			namespace mapping_plugin {

				namespace {
					struct POSTFIX_SCHEMA(factory_t) {
						abstract_mapping* operator()(ifcopenshell::file* file, Settings& settings) const {
							return new POSTFIX_SCHEMA(mapping)(file, settings);
						}
					};
				}

				plugin::abi_info plugin_abi() {
					return plugin::host_abi();
				}

				plugin::metadata plugin_metadata() {
					return mapping_plugin_metadata(STRINGIFY(IfcSchema));
				}

				void register_plugin(mapping_registry& registry, const plugin::module& module) {
					POSTFIX_SCHEMA(factory_t) factory;
					registry.bind(STRINGIFY(IfcSchema), factory, module);
				}

			}
		}
	}
}

BOOST_DLL_ALIAS(ifcopenshell::geometry::impl::mapping_plugin::plugin_abi, ifcopenshell_plugin_abi_v1)
BOOST_DLL_ALIAS(ifcopenshell::geometry::impl::mapping_plugin::plugin_metadata, ifcopenshell_plugin_metadata_v1)
BOOST_DLL_ALIAS(ifcopenshell::geometry::impl::mapping_plugin::register_plugin, ifcopenshell_register_mapping_plugin_v1)
