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
#include <functional>

namespace ifcopenshell {

class file;

class IFC_PARSE_API spf_header {
  private:
    ifcopenshell::file* file_;
    std::reference_wrapper<Logger> logger_;
	IfcParse::impl::in_memory_file_storage* storage_ = nullptr;

    std::array<shared_pointer_type, 3> header_entities_;

  public:
    explicit spf_header(ifcopenshell::file* file = nullptr, Logger& logger = Logger::Root());
    explicit spf_header(spf_lexer* lexer, Logger& logger = Logger::Root());

    void write(std::ostream& stream) const;

    ifcopenshell::file* owner_file() { return file_; }
    void owner_file(ifcopenshell::file* file);
    Logger& logger() const { return logger_.get(); }

    void set_file_description(const shared_pointer_type& description_data);
    void set_file_name(const shared_pointer_type& name_data);
    void set_file_schema(const shared_pointer_type& schema_data);

    void assign(const IfcSpfHeader& other);

    void write(std::ostream& out) const;

    Header_section_schema::file_description file_description();
    Header_section_schema::file_name file_name();
    Header_section_schema::file_schema file_schema();

    const Header_section_schema::file_description file_description() const;
    const Header_section_schema::file_name file_name() const;
    const Header_section_schema::file_schema file_schema() const;
};

} // namespace ifcopenshell

#endif
