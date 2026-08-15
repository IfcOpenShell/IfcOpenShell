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

#include "../../tree_plugin.h"
#include "tree_backends.h"

#include <boost/dll/alias.hpp>

namespace ifcopenshell {
	namespace geom {
		namespace trees {
			namespace opencascade_brep_tree_plugin {

				plugin::abi_info plugin_abi() {
					return plugin::host_abi();
				}

				plugin::metadata plugin_metadata() {
					return tree_plugin_metadata("opencascade.brep");
				}

				abstract_tree* create_tree() {
					return new opencascade_tree_backends::brep_tree();
				}

				void register_plugin(tree_registry& registry, const plugin::module& module) {
					tree_info info;
					info.backend_id = "opencascade.brep";
					registry.bind(info, create_tree, module);
				}

			}
		}
	}
}

BOOST_DLL_ALIAS(ifcopenshell::geom::trees::opencascade_brep_tree_plugin::plugin_abi, ifcopenshell_plugin_abi_v1)
BOOST_DLL_ALIAS(ifcopenshell::geom::trees::opencascade_brep_tree_plugin::plugin_metadata, ifcopenshell_plugin_metadata_v1)
BOOST_DLL_ALIAS(ifcopenshell::geom::trees::opencascade_brep_tree_plugin::register_plugin, ifcopenshell_register_tree_plugin_v1)

#ifdef __EMSCRIPTEN__
#define CAT(a, b) a##b
#define EXPAND_AND_CAT(a, b) CAT(a, b)
#define emscripten_register_tree_plugin EXPAND_AND_CAT(ifcopenshell_emscripten_register_tree_, IFCOPENSHELL_WASM_PLUGIN_ID)

extern "C" void emscripten_register_tree_plugin(ifcopenshell::geom::trees::tree_registry* registry) {
	ifcopenshell::geom::trees::opencascade_brep_tree_plugin::register_plugin(
		*registry,
		ifcopenshell::plugin::module::builtin(ifcopenshell::geom::trees::opencascade_brep_tree_plugin::plugin_metadata()));
}
#endif
