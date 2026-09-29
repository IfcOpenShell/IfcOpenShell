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

#ifndef JSONSERIALIZERIMPL_H
#define JSONSERIALIZERIMPL_H

#ifdef WITH_GLTF

#include "../../ifcgeom/abstract_mapping.h"
#include "../../ifcparse/macros.h"
#include "../../serializers/json_serializer.h"

#define INCLUDE_PARENT_PARENT_DIR(x) STRINGIFY(../../ifcparse/schemas/x.h)
#include INCLUDE_PARENT_PARENT_DIR(IfcSchema)
#undef INCLUDE_PARENT_PARENT_DIR
#define INCLUDE_PARENT_PARENT_DIR(x) STRINGIFY(../../ifcparse/schemas/x-definitions.h)
#include INCLUDE_PARENT_PARENT_DIR(IfcSchema)

class POSTFIX_SCHEMA(json_serializer) : public json_serializer {
  private:
    ifcopenshell::file* file;

    // @todo
    ifcopenshell::geom::settings settings_;
    ifcopenshell::geom::abstract_mapping* mapping_;

  public:
    POSTFIX_SCHEMA(json_serializer)(ifcopenshell::file* file, const std::string& json_filename, json_serializer::Dialect dialect, ifcopenshell::logger& logger = ifcopenshell::logger::root())
        : json_serializer(0, "", dialect), mapping_(ifcopenshell::geom::impl::mapping_implementations().construct(file, settings_, logger))
    {
        this->file = file;
        this->json_filename = json_filename;
        this->dialect_ = dialect;
    }

    void finalize();
    void setFile(ifcopenshell::file&) {}
};

#endif

#endif
