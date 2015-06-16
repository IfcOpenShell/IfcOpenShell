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

#include <boost/dynamic_bitset.hpp>

#include "../ifcparse/SharedPointer.h"
#include "../ifcparse/IfcCharacterDecoder.h"
#include "../ifcparse/IfcUtil.h"

#ifdef USE_IFC4
#include "../ifcparse/Ifc4.h"
#else
#include "../ifcparse/Ifc2x3.h"
#endif

#include "../ifcparse/IfcSpfStream.h"

namespace IfcParse {

	class Entity;
	class IfcFile;
	class IfcSpfLexer;

	typedef std::pair<IfcSpfLexer*, unsigned> Token;

	/// Provides functions to convert Tokens to binary data
	/// Tokens are merely offsets to where they can be read in the file
	class TokenFunc {
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
		static bool isOperator(const Token& t, char op = 0);
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
		/// Returns the token interpreted as an boolean (.T. or .F.)
		static bool asBool(const Token& t);
		/// Returns the token as a floating point number
		static double asFloat(const Token& t);
		/// Returns the token as a string (without the dot or apostrophe)
		static std::string asString(const Token& t);
		/// Returns the token as a string (without the dot or apostrophe)
		static boost::dynamic_bitset<> asBinary(const Token& t);
		/// Returns a string representation of the token (including the dot or apostrophe)
		static std::string toString(const Token& t);
	};

	//
	// Functions for creating Tokens from an arbitary file offset
	// The first 4 bits are reserved for Tokens of type ()=,;$*
	//
	Token TokenPtr(IfcSpfLexer* tokens, unsigned int offset);
	Token TokenPtr(char c);	
	Token TokenPtr();

	/// A stream of tokens to be read from a IfcSpfStream.
	class IfcSpfLexer {
	private:
		IfcCharacterDecoder* decoder;
		unsigned int skipWhitespace();
		unsigned int skipComment();
	public:
		IfcSpfStream* stream;
		IfcFile* file;
		IfcSpfLexer(IfcSpfStream* s, IfcFile* f);
		Token Next();
		~IfcSpfLexer();
		std::string TokenString(unsigned int offset);
	};

	/// Argument of type list, e.g.
	/// #1=IfcDirection((1.,0.,0.));
	///                 ==========
	class ArgumentList: public Argument {
	private:
		std::vector<Argument*> list;
		void push(Argument* l);
	public:
		~ArgumentList();

		void read(IfcSpfLexer* t, std::vector<unsigned int>& ids);

		IfcUtil::ArgumentType type() const;
		
		operator int() const;
		operator bool() const;
		operator double() const;
		operator std::string() const;
		operator boost::dynamic_bitset<>() const;
		operator IfcUtil::IfcBaseClass*() const;

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
	};

	/// Argument of type scalar or string, e.g.
	/// #1=IfcVector(#2,1.0);
	///              == ===
	class TokenArgument : public Argument {
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
		std::string toString(bool upper=false) const;		
	};

	/// Argument of an IFC simple type
	/// #1=IfcTrimmedCurve(#2,(IFCPARAMETERVALUE(0.)),(IFCPARAMETERVALUE(1.)),.T.,.PARAMETER.);
	///                        =====================   =====================
	class EntityArgument : public Argument {
	private:		
		IfcUtil::IfcBaseClass* entity;
	public:
		EntityArgument(const Token& t);
		~EntityArgument();

		IfcUtil::ArgumentType type() const;

		operator int() const;
		operator bool() const;
		operator double() const;
		operator std::string() const;
		operator boost::dynamic_bitset<>() const;
		operator IfcUtil::IfcBaseClass*() const;

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
		std::string toString(bool upper=false) const;
	};

	/// Entity defined in an IFC file, e.g.
	/// #1=IfcDirection((1.,0.,0.));
	/// ============================
	class Entity : public IfcAbstractEntity {
	private:
		mutable ArgumentList* args;
		mutable IfcSchema::Type::Enum _type;
	public:
		/// The EXPRESS ENTITY_INSTANCE_NAME
		unsigned int _id;
		/// The offset at which the entity is read
		unsigned int offset;		
		Entity(unsigned int i, IfcFile* t);
		Entity(unsigned int i, IfcFile* t, unsigned int o);
		~Entity();
		IfcEntityList::ptr getInverse(IfcSchema::Type::Enum type, int attribute_index);
		void Load(std::vector<unsigned int>& ids, bool seek=false) const;
		Argument* getArgument (unsigned int i);
		unsigned int getArgumentCount() const;
		std::string toString(bool upper=false) const;
		std::string datatype() const;
		IfcSchema::Type::Enum type() const;
		bool is(IfcSchema::Type::Enum v) const;
		unsigned int id();
		IfcWrite::IfcWritableEntity* isWritable();
	};

}

std::ostream& operator<< (std::ostream& os, const IfcParse::IfcFile& f);

#endif
