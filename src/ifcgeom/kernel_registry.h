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

#ifndef KERNEL_REGISTRY_H
#define KERNEL_REGISTRY_H

#include "../ifcgeom/abstract_kernel.h"
#include "../plugin/plugin.h"

#include <boost/function.hpp>

#include <map>
#include <memory>
#include <string>
#include <vector>

namespace ifcopenshell {
	class file;

	namespace geom {
		namespace kernels {

			struct IFC_GEOM_API kernel_info {
				std::string backend_id;
				bool supports_boolean_operations = false;
			};

			class IFC_GEOM_API kernel_registry {
			public:
				typedef boost::function2<abstract_kernel*, ifcopenshell::file*, ifcopenshell::geom::settings&> create_fn;

				void bind(const kernel_info& info, create_fn create, const ifcopenshell::plugin::module& module = ifcopenshell::plugin::module());
				bool has(const std::string& backend_id) const;
				std::unique_ptr<abstract_kernel> create(const std::string& backend_id, ifcopenshell::file* file, ifcopenshell::geom::settings& settings) const;
				std::vector<kernel_info> kernels() const;

			private:
				struct entry {
					kernel_info info_;
					create_fn create_;
					ifcopenshell::plugin::module module_;
				};

				std::map<std::string, entry> entries_;
			};

			IFC_GEOM_API kernel_registry& kernel_registry_instance();
			IFC_GEOM_API std::unique_ptr<abstract_kernel> construct(ifcopenshell::file* file, const std::string& geometry_library, ifcopenshell::geom::settings& settings);

		}
	}
}

#endif
