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

#define IFCOPENSHELL_VERSION "0.5.0-dev"

#include <string>
#include <sstream>
#include <iostream>
#include <vector>
#include <fstream>
#include <cstring>
#include <map>

#include <boost/shared_ptr.hpp>
#include <boost/dynamic_bitset.hpp>

#include "ifc_parse_api.h"

#include "../ifcparse/IfcCharacterDecoder.h"
#include "../ifcparse/IfcBaseClass.h"
#include "../ifcparse/IfcLogger.h"
#include "../ifcparse/Argument.h"

#ifdef USE_IFC4
#include "../ifcparse/Ifc4.h"
#else
#include "../ifcparse/Ifc2x3.h"
#endif

#include "../ifcparse/IfcSpfStream.h"

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
			bool value_bool;      //types: BOOL
			char value_char;      //types: OPERATOR
			int value_int;        //types: INT, IDENTIFIER
			double value_double;  //types: FLOAT
		};

		Token() : lexer(0), startPos(0), type(Token_NONE) {}
		Token(IfcSpfLexer* _lexer, unsigned _startPos, unsigned /*_endPos*/, TokenType _type)
			: lexer(_lexer), startPos(_startPos), type(_type) {}
	};

	/// Provides functions to convert Tokens to binary data
	/// Tokens are merely offsets to where they can be read in the file
	class IFC_PARSE_API TokenFunc {
	private:
		static bool startsWith(const Token& t, char c);
	public:
		/// Returns the offset at which the token is read from the file
		// static unsigned int Offset(const Token& t);
		/// Returns whether the token can be interpreted as a string
		static bool isString(const Token& t);
		/// Returns whether the token can be interpreted as an identifier
		static bool isIdentifier(const Token& t);
		/// Returns whether the token can be interpreted as a syntactical operator
		static bool isOperator(const Token& t);
		/// Returns whether the token is a given operator
		static bool isOperator(const Token& t, char op);
		/// Returns whether the token can be interpreted as an enumerated value
		static bool isEnumeration(const Token& t);
		/// Returns whether the token can be interpreted as a datatype name
		static bool isKeyword(const Token& t);
		/// Returns whether the token can be interpreted as an integer
		static bool isInt(const Token& t);
		/// Returns whether the token can be interpreted as a boolean
		static bool isBool(const Token& t);
		/// Returns whether the token can be interpreted as a floating point number
		static bool isFloat(const Token& t);
		/// Returns whether the token can be interpreted as a binary type
		static bool isBinary(const Token& t);
		/// Returns the token interpreted as an integer
		static int asInt(const Token& t);
		/// Returns the token interpreted as an identifier
		static int asIdentifier(const Token& t);
		/// Returns the token interpreted as an boolean (.T. or .F.)
		static bool asBool(const Token& t);
		/// Returns the token as a floating point number
		static double asFloat(const Token& t);
		/// Returns the token as a string (without the dot or apostrophe)
		static std::string asString(const Token& t);
		/// Returns the token as a string in internal buffer (for optimization purposes)
		static const std::string &asStringRef(const Token& t);
		/// Returns the token as a string (without the dot or apostrophe)
		static boost::dynamic_bitset<> asBinary(const Token& t);
		/// Returns a string representation of the token (including the dot or apostrophe)
		static std::string toString(const Token& t);
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
		IfcCharacterDecoder* decoder;
		//storage for temporary string without allocation
		mutable std::string _tempString;
		unsigned int skipWhitespace();
		unsigned int skipComment();
	public:
		std::string &GetTempString() const { return _tempString; }
		IfcSpfStream* stream;
		IfcFile* file;
		IfcSpfLexer(IfcSpfStream* s, IfcFile* f);
		Token Next();
		~IfcSpfLexer();
		void TokenString(unsigned int offset, std::string &result);
	};

	/// Argument of type list, e.g.
	/// #1=IfcDirection((1.,0.,0.));
	///                 ==========
	class IFC_PARSE_API ArgumentList: public Argument {
	private:
		std::vector<Argument*> list;
		void push(Argument* l);
	public:
		~ArgumentList();

		void read(IfcSpfLexer* t, std::vector<unsigned int>& ids);

		IfcUtil::ArgumentType type() const;
		
		operator std::vector<int>() const;
		operator std::vector<double>() const;
		operator std::vector<std::string>() const;
		operator std::vector<boost::dynamic_bitset<> >() const;
		operator IfcEntityList::ptr() const;

		operator std::vector< std::vector<int> >() const;
		operator std::vector< std::vector<double> >() const;
		operator IfcEntityListList::ptr() const;

		bool isNull() const;
		unsigned int size() const;

		Argument* operator [] (unsigned int i) const;
		void set(unsigned int i, Argument*);

		std::string toString(bool upper=false) const;

		std::vector<Argument*>& arguments() { return list; }
	};


	/// Argument being null, e.g. '$'
	///              == ===
	class IFC_PARSE_API NullArgument : public Argument {
	public:
		NullArgument() {}
		IfcUtil::ArgumentType type() const { return IfcUtil::Argument_NULL; }
		bool isNull() const { return true; }
		unsigned int size() const { return 1; }
		Argument* operator [] (unsigned int /*i*/) const { throw IfcException("Argument is not a list of attributes"); }
		std::string toString(bool /*upper=false*/) const { return "$"; }
	};

	/// Argument of type scalar or string, e.g.
	/// #1=IfcVector(#2,1.0);
	///              == ===
	class IFC_PARSE_API TokenArgument : public Argument {
	private:
		
	public: 
		Token token;
		TokenArgument(const Token& t);

		IfcUtil::ArgumentType type() const;

		operator int() const;
		operator bool() const;
		operator double() const;
		operator std::string() const;
		operator boost::dynamic_bitset<>() const;
		operator IfcUtil::IfcBaseClass*() const;

		bool isNull() const;
		unsigned int size() const;

		Argument* operator [] (unsigned int i) const;
		std::string toString(bool upper=false) const;		
	};

	/// Argument of an IFC simple type
	/// #1=IfcTrimmedCurve(#2,(IFCPARAMETERVALUE(0.)),(IFCPARAMETERVALUE(1.)),.T.,.PARAMETER.);
	///                        =====================   =====================
	class IFC_PARSE_API EntityArgument : public Argument {
	private:		
		IfcUtil::IfcBaseClass* entity;
	public:
		EntityArgument(const Token& t);
		~EntityArgument();

		IfcUtil::ArgumentType type() const;

		operator IfcUtil::IfcBaseClass*() const;

		bool isNull() const;
		unsigned int size() const;

		Argument* operator [] (unsigned int i) const;
		std::string toString(bool upper=false) const;
	};
	
	IFC_PARSE_API IfcEntityInstanceData* read(unsigned int i, IfcFile* t, boost::optional<unsigned> offset = boost::none);

	IFC_PARSE_API IfcEntityList::ptr traverse(IfcUtil::IfcBaseClass* instance, int max_level = -1);
}

IFC_PARSE_API std::ostream& operator<< (std::ostream& os, const IfcParse::IfcFile& f);

#endif
