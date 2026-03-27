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

/********************************************************************************
 *                                                                              *
 * This file provides functions for loading an IFC file into memory and access  *
 * its entities either by ID, by an IfcSchema::Type or by reference             * 
 *                                                                              *
 ********************************************************************************/

#ifndef IFCPARSE_H
#define IFCPARSE_H

#include "Argument.h"
#include "ifc_parse_api.h"
#include "express.h"
#include "IfcCharacterDecoder.h"
#include "FileReader.h"
#include "macros.h"
#include "storage.h"

#include <boost/dynamic_bitset.hpp>
#include <boost/shared_ptr.hpp>
#include <cstring>
#include <iostream>
#include <string>
#include <vector>


extern const char *IFCOPENSHELL_VERSION;

namespace IfcParse {

/// A stream of tokens to be read from a FileReader.
template <typename Reader>
class IFC_PARSE_API IfcSpfLexer {
  private:
    IfcCharacterDecoder<Reader>* decoder_;
    size_t skipWhitespace() const;
    size_t skipComment() const;

    mutable std::vector<std::unique_ptr<std::array<std::string, 16>>> stringpool_;
    mutable size_t pool_index = 0;

  public:
    std::string& getTempString() const;
    void resetPool() const {
        pool_index = 0;
    }
    void popPoolEntry() {
        if (pool_index > 0) {
            --pool_index;
        }
    }

    Reader* stream;
    // IfcFile* file;
    IfcSpfLexer(Reader* stream);
    Token Next();
    ~IfcSpfLexer();
    // void TokenString(size_t offset, std::string& result);
};

IFC_PARSE_API std::vector<express::Base> traverse(const express::Base& instance, int max_level = -1);

IFC_PARSE_API std::vector<express::Base> traverse_breadth_first(const express::Base& instance, int max_level = -1);
} // namespace IfcParse

IFC_PARSE_API std::ostream& operator<<(std::ostream& out, const IfcParse::IfcFile& file);

#endif
