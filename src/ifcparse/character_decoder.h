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
 *                                                                               *
 * Implementation of character decoding as described in ISO 10303-21 table 2 and *
 * table 4                                                                       *
 *                                                                               *
 ********************************************************************************/

#ifndef IFCCHARACTERDECODER_H
#define IFCCHARACTERDECODER_H

#include "file_reader.h"
#include "logger.h"

#include <string>

namespace ifcopenshell {
IFC_PARSE_API std::u32string::value_type convert_codepage(int codepage, int index);
IFC_PARSE_API std::string convert_utf8(const std::u32string& string);
IFC_PARSE_API std::u32string convert_utf8(const std::string& string);
} // namespace ifcopenshell

namespace ifcopenshell {

template <typename Reader>
class IFC_PARSE_API character_decoder {
  private:
    Reader* stream_;
    logger& logger_;
    int codepage_;
    std::u32string builder_;

  public:
    enum ConversionMode {
        SUBSTITUTE,
        UTF8,
        ESCAPE
    };
    inline static ConversionMode mode = UTF8;
    inline static char substitution_character = '_';

    character_decoder(Reader* stream, logger& logger = ifcopenshell::logger::root());
    ~character_decoder();
    // Gets a decoded string representation at the token stream
    // read pointer and advances the underlying token stream.
    operator std::string();
    // Gets a decoded string representation at the offset provided,
    // does not mutate the underlying token stream read pointer.
    std::string get(size_t& offset);
};

class IFC_PARSE_API character_encoder {
  private:
    std::u32string str_;

  public:
    character_encoder(const std::string& input);
    operator std::string();
};

} // namespace ifcopenshell

#endif
