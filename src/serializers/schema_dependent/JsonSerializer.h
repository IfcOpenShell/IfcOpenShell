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
#include "../../serializers/JsonSerializer.h"

#define INCLUDE_PARENT_PARENT_DIR(x) STRINGIFY(../../ifcparse/x.h)
#include INCLUDE_PARENT_PARENT_DIR(IfcSchema)
#undef INCLUDE_PARENT_PARENT_DIR
#define INCLUDE_PARENT_PARENT_DIR(x) STRINGIFY(../../ifcparse/x-definitions.h)
#include INCLUDE_PARENT_PARENT_DIR(IfcSchema)

class POSTFIX_SCHEMA(JsonSerializer) : public JsonSerializer {
  private:
    IfcParse::IfcFile* file;

    // @todo
    ifcopenshell::geometry::Settings settings_;
    ifcopenshell::geometry::abstract_mapping* mapping_;

  public:
    POSTFIX_SCHEMA(JsonSerializer)(IfcParse::IfcFile* file, const std::string& json_filename, JsonSerializer::Dialect dialect, Logger& logger = Logger::Root())
        : JsonSerializer(0, "", dialect, logger), mapping_(ifcopenshell::geometry::impl::mapping_implementations().construct(file, settings_, logger))
    {
        this->file = file;
        this->json_filename = json_filename;
        this->dialect_ = dialect;
    }

    void finalize();
    void setFile(IfcParse::IfcFile*) {}
};

#endif

#endif
