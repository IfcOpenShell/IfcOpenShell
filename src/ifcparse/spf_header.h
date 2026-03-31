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

#ifndef IFCSPFHEADER_H
#define IFCSPFHEADER_H

#include "ifc_parse_api.h"
#include "instance_data.h"
#include "schemas/Header_section_schema.h"

namespace ifcopenshell {

class file;

class IFC_PARSE_API spf_header {
  private:
    file* file_;

    std::array<std::shared_ptr<instance_data>, 3> header_entities_;

  public:
    explicit spf_header(ifcopenshell::file* owner_file);
    ~spf_header();

    void write(std::ostream& stream) const;

    ifcopenshell::file* file() { return file_; }
    void file(ifcopenshell::file* owner_file);

    void set_file_description(const std::shared_ptr<instance_data>& description_data);
    void set_file_name(const std::shared_ptr<instance_data>& name_data);
    void set_file_schema(const std::shared_ptr<instance_data>& schema_data);

    const Header_section_schema::file_description file_description() const;
    const Header_section_schema::file_name file_name() const;
    const Header_section_schema::file_schema file_schema() const;

    Header_section_schema::file_description file_description();
    Header_section_schema::file_name file_name();
    Header_section_schema::file_schema file_schema();
};

} // namespace ifcopenshell

#endif
