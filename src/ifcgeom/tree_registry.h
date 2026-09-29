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

#ifndef IFCOPENSHELL_TREE_REGISTRY_H
#define IFCOPENSHELL_TREE_REGISTRY_H

#include "tree.h"
#include "../plugin/plugin.h"

#include <functional>
#include <map>
#include <memory>
#include <string>

namespace ifcopenshell {
	class file;

	namespace geom {
		class settings;

		namespace trees {

			struct IFC_GEOM_API tree_info {
				std::string backend_id;
			};

			class IFC_GEOM_API tree_registry {
			public:
				typedef std::function<tree*()> create_fn;

				void bind(const tree_info& info, create_fn create, const ifcopenshell::plugin::module& module = ifcopenshell::plugin::module());
				bool has(const std::string& backend_id) const;
				std::unique_ptr<tree> create(const std::string& backend_id) const;

			private:
				struct entry {
					ifcopenshell::plugin::module module_;
					tree_info info_;
					create_fn create_;
				};

				std::map<std::string, entry> entries_;
			};

			IFC_GEOM_API tree_registry& tree_registry_instance();
			IFC_GEOM_API std::unique_ptr<tree> construct(const std::string& backend_id);

		}
	}
}

#endif
