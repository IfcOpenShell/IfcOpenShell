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

#include "../opencascade_geometry_ifc_writer_plugin.h"

#include "../../../ifcgeom/kernels/opencascade/OpenCascadeConversionResult.h"
#include "../../../ifcparse/exception.h"
#include "../../../ifcparse/macros.h"

#include <boost/dll/alias.hpp>

express::Base POSTFIX_SCHEMA(serialise)(ifcopenshell::file& f, const TopoDS_Shape& shape, bool advanced);
express::Base POSTFIX_SCHEMA(tesselate)(ifcopenshell::file& f, const TopoDS_Shape& shape, double deflection);

namespace {
	const ifcopenshell::geometry::OpenCascadeShape& require_opencascade_shape(const IfcGeom::ConversionResultShape& shape) {
		const auto* oc_shape = dynamic_cast<const ifcopenshell::geometry::OpenCascadeShape*>(&shape);
		if (!oc_shape) {
			throw ifcopenshell::exception("OpenCascade geometry IFC writer requires an opencascade conversion result shape");
		}
		return *oc_shape;
	}

	express::Base serialise_adapter(ifcopenshell::file& f, const IfcGeom::ConversionResultShape& shape, bool advanced) {
		return POSTFIX_SCHEMA(serialise)(f, require_opencascade_shape(shape).shape(), advanced);
	}

	express::Base tesselate_adapter(ifcopenshell::file& f, const IfcGeom::ConversionResultShape& shape, double deflection) {
		return POSTFIX_SCHEMA(tesselate)(f, require_opencascade_shape(shape).shape(), deflection);
	}
}

namespace IfcGeom {
	namespace opencascade_geometry_ifc_writer_plugin {

		ifcopenshell::plugin::abi_info plugin_abi() {
			return ifcopenshell::plugin::host_abi();
		}

		ifcopenshell::plugin::metadata plugin_metadata() {
			return opencascade_geometry_ifc_writer_plugin_metadata(STRINGIFY(IfcSchema));
		}

		void register_plugin(opencascade_geometry_ifc_writer_registry& registry, const ifcopenshell::plugin::module& module) {
			registry.bind(STRINGIFY(IfcSchema), &serialise_adapter, &tesselate_adapter, module);
		}

	}
}

BOOST_DLL_ALIAS(IfcGeom::opencascade_geometry_ifc_writer_plugin::plugin_abi, ifcopenshell_plugin_abi_v1)
BOOST_DLL_ALIAS(IfcGeom::opencascade_geometry_ifc_writer_plugin::plugin_metadata, ifcopenshell_plugin_metadata_v1)
BOOST_DLL_ALIAS(IfcGeom::opencascade_geometry_ifc_writer_plugin::register_plugin, ifcopenshell_register_opencascade_geometry_ifc_writer_plugin_v1)
