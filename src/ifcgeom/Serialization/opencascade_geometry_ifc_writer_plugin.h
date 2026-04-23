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

#ifndef IFCOPENSHELL_OPENCASCADE_GEOMETRY_IFC_WRITER_PLUGIN_H
#define IFCOPENSHELL_OPENCASCADE_GEOMETRY_IFC_WRITER_PLUGIN_H

#include "Serialization.h"

#include <filesystem>

namespace IfcGeom {

typedef void register_opencascade_geometry_ifc_writer_plugin_fn(opencascade_geometry_ifc_writer_registry&, const ifcopenshell::plugin::module&);

IFC_GEOMSERIALIZATION_API const char* opencascade_geometry_ifc_writer_plugin_registration_symbol();
IFC_GEOMSERIALIZATION_API ifcopenshell::plugin::metadata opencascade_geometry_ifc_writer_plugin_metadata(const std::string& schema_name);
IFC_GEOMSERIALIZATION_API std::filesystem::path opencascade_geometry_ifc_writer_plugin_directory();
IFC_GEOMSERIALIZATION_API void load_opencascade_geometry_ifc_writer_plugins(opencascade_geometry_ifc_writer_registry& registry);

}

#endif
