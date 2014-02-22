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

#include "../ifcparse/SharedPointer.h"
#include "../ifcparse/IfcCharacterDecoder.h"
#include "../ifcparse/IfcUtil.h"
#include "../ifcparse/IfcUntypedEntity.h"

#ifdef USE_IFC4
#include "../ifcparse/Ifc4.h"
#else
#include "../ifcparse/Ifc2x3.h"
#endif

#include "../ifcparse/IfcSpfStream.h"

namespace IfcParse {

	class Entity;
	class Entities;
	class IfcFile;
	typedef Entity* EntityPtr;
	typedef SHARED_PTR<Entities> EntitiesPtr;

	class Tokens;
	typedef std::pair<Tokens*,unsigned> Token;

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
		/// Returns whether the token can be interpreted as an syntactical operator
		static bool isOperator(const Token& t, char op = 0);
		/// Returns whether the token can be interpreted as an enumerated value
		static bool isEnumeration(const Token& t);
		/// Returns whether the token can be interpreted as an datatype name
		static bool isDatatype(const Token& t);
		/// Returns the token interpreted as an integer
		static int asInt(const Token& t);
		/// Returns the token interpreted as an boolean (.T. or .F.)
		static bool asBool(const Token& t);
		/// Returns the token as a floating point number
		static double asFloat(const Token& t);
		/// Returns the token as a string (without the dot or apostrophe)
		static std::string asString(const Token& t);
		/// Returns a string representation of the token (including the dot or apostrophe)
		static std::string toString(const Token& t);
	};

	//
	// Functions for creating Tokens from an arbitary file offset
	// The first 4 bits are reserved for Tokens of type ()=,;$*
	//
	Token TokenPtr(Tokens* tokens, unsigned int offset);
	Token TokenPtr(char c);	
	Token TokenPtr();

	/// A stream of tokens to be read from a IfcSpfStream.
	class Tokens {
	private:
		IfcCharacterDecoder* decoder;
	public:
		IfcSpfStream* stream;
		IfcFile* file;
		Tokens(IfcSpfStream* s, IfcFile* f);
		Token Next();
		~Tokens();
		std::string TokenString(unsigned int offset);
	};

	/// Argument of type list, e.g.
	/// #1=IfcDirection((1.,0.,0.));
	///                 ==========
	class ArgumentList: public Argument {
	private:
		std::vector<ArgumentPtr> list;
		void Push(ArgumentPtr l);
	public:
		ArgumentList(Tokens* t, std::vector<unsigned int>& ids);
		~ArgumentList();
		operator int() const;
		operator bool() const;
		operator double() const;
		operator std::string() const;
		operator std::vector<double>() const;
		operator std::vector<int>() const;
		operator std::vector<std::string>() const;
		operator IfcUtil::IfcSchemaEntity() const;
		//operator IfcUtil::IfcAbstractSelect::ptr() const;
		operator IfcEntities() const;
		unsigned int Size() const;
		ArgumentPtr operator [] (unsigned int i) const;
		std::string toString(bool upper=false) const;
		bool isNull() const;
	};

	/// Argument of type scalar or string, e.g.
	/// #1=IfcVector(#2,1.0);
	///              == ===
	class TokenArgument : public Argument {
	private:
		
	public: 
		Token token;
		TokenArgument(const Token& t);
		operator int() const;
		operator bool() const;
		operator double() const;
		operator std::string() const;
		operator std::vector<double>() const;
		operator std::vector<int>() const;
		operator std::vector<std::string>() const;
		operator IfcUtil::IfcSchemaEntity() const;
		//operator IfcUtil::IfcAbstractSelect::ptr() const;
		operator IfcEntities() const;
		unsigned int Size() const;
		ArgumentPtr operator [] (unsigned int i) const;
		std::string toString(bool upper=false) const;
		bool isNull() const;
	};

	/// Argument of an IFC simple type
	/// #1=IfcTrimmedCurve(#2,(IFCPARAMETERVALUE(0.)),(IFCPARAMETERVALUE(1.)),.T.,.PARAMETER.);
	///                        =====================   =====================
	class EntityArgument : public Argument {
	private:		
		IfcUntypedEntity* entity;		
	public:
		EntityArgument(IfcSchema::Type::Enum ty, const Token& t);
		~EntityArgument();
		operator int() const;
		operator bool() const;
		operator double() const;
		operator std::string() const;
		operator std::vector<double>() const;
		operator std::vector<int>() const;
		operator std::vector<std::string>() const;
		operator IfcUtil::IfcSchemaEntity() const;
		//operator IfcUtil::IfcAbstractSelect::ptr() const;
		operator IfcEntities() const;
		unsigned int Size() const;
		ArgumentPtr operator [] (unsigned int i) const;
		std::string toString(bool upper=false) const;
		bool isNull() const;
	};

	/// Entity defined in an IFC file, e.g.
	/// #1=IfcDirection((1.,0.,0.));
	/// ============================
	class Entity : public IfcAbstractEntity {
	private:
		//IfcFile* file;
		ArgumentPtr args;
		IfcSchema::Type::Enum _type;
	public:
		/// The EXPRESS ENTITY_INSTANCE_NAME
		unsigned int _id;
		/// The offset at which the entity is read
		unsigned int offset;		
		Entity(unsigned int i, IfcFile* t);
		Entity(unsigned int i, IfcFile* t, unsigned int o);
		~Entity();
		IfcEntities getInverse(IfcSchema::Type::Enum c = IfcSchema::Type::ALL);
		IfcEntities getInverse(IfcSchema::Type::Enum c, int i, const std::string& a);
		void Load(std::vector<unsigned int>& ids, bool seek=false);
		ArgumentPtr getArgument (unsigned int i);
		unsigned int getArgumentCount();
		std::string toString(bool upper=false);
		std::string datatype();
		IfcSchema::Type::Enum type() const;
		bool is(IfcSchema::Type::Enum v) const;
		unsigned int id();
		bool isWritable();
	};

typedef IfcUtil::IfcSchemaEntity IfcEntity;
//typedef IfcEntities IfcEntities;
typedef std::map<IfcSchema::Type::Enum,IfcEntities> MapEntitiesByType;
typedef std::map<unsigned int,IfcEntity> MapEntityById;
typedef std::map<std::string,IfcSchema::IfcRoot::ptr> MapEntityByGuid;
typedef std::map<unsigned int,IfcEntities> MapEntitiesByRef;
typedef std::map<unsigned int,unsigned int> MapOffsetById;

double UnitPrefixToValue( IfcSchema::IfcSIPrefix::IfcSIPrefix v );

}

std::ostream& operator<< (std::ostream& os, const IfcParse::IfcFile& f);

#endif
