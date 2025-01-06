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

#ifndef XMLSERIALIZERIMPL_H
#define XMLSERIALIZERIMPL_H

#include "../../ifcgeom/abstract_mapping.h"
#include "../../ifcparse/macros.h"
#include "../../serializers/XmlSerializer.h"

#define INCLUDE_PARENT_PARENT_DIR(x) STRINGIFY(../../ifcparse/x.h)
#include INCLUDE_PARENT_PARENT_DIR(IfcSchema)
#undef INCLUDE_PARENT_PARENT_DIR
#define INCLUDE_PARENT_PARENT_DIR(x) STRINGIFY(../../ifcparse/x-definitions.h)
#include INCLUDE_PARENT_PARENT_DIR(IfcSchema)

class POSTFIX_SCHEMA(XmlSerializer) : public XmlSerializer {
private:
	IfcParse::IfcFile* file;

	// @todo
	ifcopenshell::geometry::Settings settings_;
	ifcopenshell::geometry::abstract_mapping* mapping_;

public:
	POSTFIX_SCHEMA(XmlSerializer)(IfcParse::IfcFile* file, const std::string& xml_filename)
		: XmlSerializer(0, "")
		, mapping_(ifcopenshell::geometry::impl::mapping_implementations().construct(file, settings_))
	{
		this->file = file;
		this->xml_filename = xml_filename;
	}

	void finalize();
	void setFile(IfcParse::IfcFile*) {}
};

#endif