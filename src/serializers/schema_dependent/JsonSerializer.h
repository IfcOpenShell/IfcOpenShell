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

#include <nlohmann/json.hpp>
#include "../../ifcparse/macros.h"
#include "../../serializers/JsonSerializer.h"

#define INCLUDE_PARENT_PARENT_DIR(x) STRINGIFY(../../ifcparse/x.h)
#include INCLUDE_PARENT_PARENT_DIR(IfcSchema)

class MAKE_TYPE_NAME(JsonSerializer) : public JsonSerializer {
private:
	IfcParse::IfcFile* file;

public:
	MAKE_TYPE_NAME(JsonSerializer)(IfcParse::IfcFile* file, const std::string& json_filename)
		: JsonSerializer(0, "")
	{
		this->file = file;
		this->json_filename = json_filename;
	}

	void finalize();
    void writeIfcHeader(nlohmann::json::reference ifc);
	void setFile(IfcParse::IfcFile*) {}
};

#endif
