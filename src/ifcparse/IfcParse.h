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

#include "aggregate_of_instance.h"
#include "Argument.h"
#include "ifc_parse_api.h"
#include "IfcBaseClass.h"
#include "IfcCharacterDecoder.h"
#include "IfcSpfStream.h"
#include "macros.h"

#include <boost/dynamic_bitset.hpp>
#include <boost/shared_ptr.hpp>
#include <cstring>
#include <iostream>
#include <string>
#include <vector>

#if defined(IFCOPENSHELL_BRANCH) && defined(IFCOPENSHELL_COMMIT)
#define IFCOPENSHELL_VERSION STRINGIFY(IFCOPENSHELL_BRANCH) "-" STRINGIFY(IFCOPENSHELL_COMMIT)
#else
#define IFCOPENSHELL_VERSION "0.8.0"
#endif

namespace IfcParse {

class IfcFile;
class IfcSpfLexer;

enum TokenType {
    Token_NONE,
    Token_STRING,
    Token_IDENTIFIER,
    Token_OPERATOR,
    Token_ENUMERATION,
    Token_KEYWORD,
    Token_INT,
    Token_BOOL,
    Token_FLOAT,
    Token_BINARY
};

struct Token {
    IfcSpfLexer* lexer; //TODO: remove it from here
    unsigned startPos;
    TokenType type;
    union {
        char value_char;     //types: OPERATOR
        int value_int;       //types: INT, IDENTIFIER
        double value_double; //types: FLOAT
    };

    Token() : lexer(0),
              startPos(0),
              type(Token_NONE) {}
    Token(IfcSpfLexer* _lexer, unsigned _startPos, unsigned /*_endPos*/, TokenType _type)
        : lexer(_lexer),
          startPos(_startPos),
          type(_type) {}
};

/// Provides functions to convert Tokens to binary data
/// Tokens are merely offsets to where they can be read in the file
class IFC_PARSE_API TokenFunc {
  private:
    static bool startsWith(const Token& token, char character);

  public:
    /// Returns the offset at which the token is read from the file
    // static unsigned int Offset(const Token& t);
    /// Returns whether the token can be interpreted as a string
    static bool isString(const Token& token);
    /// Returns whether the token can be interpreted as an identifier
    static bool isIdentifier(const Token& token);
    /// Returns whether the token can be interpreted as a syntactical operator
    static bool isOperator(const Token& token);
    /// Returns whether the token is a given operator
    static bool isOperator(const Token& token, char character);
    /// Returns whether the token can be interpreted as an enumerated value
    static bool isEnumeration(const Token& token);
    /// Returns whether the token can be interpreted as a datatype name
    static bool isKeyword(const Token& token);
    /// Returns whether the token can be interpreted as an integer
    static bool isInt(const Token& token);
    /// Returns whether the token can be interpreted as a boolean
    static bool isBool(const Token& token);
    /// Returns whether the token can be interpreted as a logical
    static bool isLogical(const Token& token);
    /// Returns whether the token can be interpreted as a floating point number
    static bool isFloat(const Token& token);
    /// Returns whether the token can be interpreted as a binary type
    static bool isBinary(const Token& token);
    /// Returns the token interpreted as an integer
    static int asInt(const Token& token);
    /// Returns the token interpreted as an identifier
    static int asIdentifier(const Token& token);
    /// Returns the token interpreted as an boolean (.T. or .F.)
    static bool asBool(const Token& token);
    /// Returns the token interpreted as an logical (.T. or .F. or .U.)
    static boost::logic::tribool asLogical(const Token& token);
    /// Returns the token as a floating point number
    static double asFloat(const Token& token);
    /// Returns the token as a string (without the dot or apostrophe)
    static std::string asString(const Token& token);
    /// Returns the token as a string in internal buffer (for optimization purposes)
    static const std::string& asStringRef(const Token& token);
    /// Returns the token as a string (without the dot or apostrophe)
    static boost::dynamic_bitset<> asBinary(const Token& token);
    /// Returns a string representation of the token (including the dot or apostrophe)
    static std::string toString(const Token& token);
};

//
// Functions for creating Tokens from an arbitary file offset
// The first 4 bits are reserved for Tokens of type ()=,;$*
//
Token OperatorTokenPtr(IfcSpfLexer* tokens, unsigned start, unsigned end);
Token GeneralTokenPtr(IfcSpfLexer* tokens, unsigned start, unsigned end);
Token NoneTokenPtr();

/// A stream of tokens to be read from a IfcSpfStream.
class IFC_PARSE_API IfcSpfLexer {
  private:
    IfcCharacterDecoder* decoder_;
    unsigned int skipWhitespace() const;
    unsigned int skipComment() const;

  public:
    std::string& GetTempString() const {
        static my_thread_local std::string string;
        return string;
    }
    IfcSpfStream* stream;
    IfcFile* file;
    IfcSpfLexer(IfcSpfStream* stream, IfcFile* file);
    Token Next();
    ~IfcSpfLexer();
    void TokenString(unsigned int offset, std::string& result);
};

IFC_PARSE_API IfcEntityInstanceData read(unsigned int index, IfcFile* file);

IFC_PARSE_API aggregate_of_instance::ptr traverse(IfcUtil::IfcBaseClass* instance, int max_level = -1);

IFC_PARSE_API aggregate_of_instance::ptr traverse_breadth_first(IfcUtil::IfcBaseClass* instance, int max_level = -1);
} // namespace IfcParse

IFC_PARSE_API std::ostream& operator<<(std::ostream& out, const IfcParse::IfcFile& file);

#endif
