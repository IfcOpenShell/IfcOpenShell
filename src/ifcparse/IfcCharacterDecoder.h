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

#include "IfcSpfStream.h"

#include <string>

namespace IfcUtil {
std::wstring::value_type convert_codepage(int codepage, int index);
std::string convert_utf8(const std::wstring& string);
std::wstring convert_utf8(const std::string& string);
std::u32string convert_utf8_to_utf32(const std::string& string);
} // namespace IfcUtil

namespace IfcParse {

class IFC_PARSE_API IfcCharacterDecoder {
  private:
    IfcParse::IfcSpfStream* stream_;
    int codepage_;

  public:
    enum ConversionMode {
        SUBSTITUTE,
        UTF8,
        ESCAPE
    };
    static ConversionMode mode;
    static char substitution_character;
    IfcCharacterDecoder(IfcParse::IfcSpfStream* stream);
    ~IfcCharacterDecoder();
    // Only advances the underlying token stream read pointer
    // to the next token.
    void skip();
    // Gets a decoded string representation at the token stream
    // read pointer and advances the underlying token stream.
    operator std::string();
    // Gets a decoded string representation at the offset provided,
    // does not mutate the underlying token stream read pointer.
    std::string get(unsigned int&);
};

} // namespace IfcParse

namespace IfcParse {

class IFC_PARSE_API IfcCharacterEncoder {
  private:
    std::u32string str_;

  public:
    IfcCharacterEncoder(const std::string& input);
    operator std::string();
};

} // namespace IfcWrite

#endif
