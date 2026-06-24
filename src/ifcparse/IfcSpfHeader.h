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
#include "IfcEntityInstanceData.h"
#include "Header_section_schema.h"
#include "storage.h"

#include <functional>

namespace IfcParse {

class IfcFile;

class IFC_PARSE_API IfcSpfHeader {
  private:
    IfcFile* file_;
    std::reference_wrapper<Logger> logger_;
	IfcParse::impl::in_memory_file_storage* storage_ = nullptr;

    mutable Header_section_schema::file_description* file_description_;
    mutable Header_section_schema::file_name* file_name_;
    mutable Header_section_schema::file_schema* file_schema_;
    void readSemicolon();
    enum Trail {
        TRAILING_SEMICOLON,
        NONE
    };
    void readTerminal(const std::string& term, Trail trail);

  public:
    explicit IfcSpfHeader(IfcParse::IfcFile* file = nullptr, Logger& logger = Logger::Root());
    explicit IfcSpfHeader(IfcParse::IfcSpfLexer* lexer, Logger& logger = Logger::Root());

    ~IfcSpfHeader();

    IfcParse::IfcFile* file() { return file_; }
    void file(IfcParse::IfcFile* file);
    Logger& logger() const { return logger_.get(); }

    void read();
    bool tryRead();

    void assign(const IfcSpfHeader& other);

    void write(std::ostream& out) const;

    const Header_section_schema::file_description* file_description() const;
    const Header_section_schema::file_name* file_name() const;
    const Header_section_schema::file_schema* file_schema() const;

    Header_section_schema::file_description* file_description();
    Header_section_schema::file_name* file_name();
    Header_section_schema::file_schema* file_schema();
};

} // namespace IfcParse

#endif
