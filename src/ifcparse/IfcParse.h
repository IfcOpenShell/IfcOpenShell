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
 * its entities either by ID, by an Ifc2x3::Type or by reference                * 
 *                                                                              *
 ********************************************************************************/

#ifndef IFCPARSE_H
#define IFCPARSE_H

#define IFCOPENSHELL_VERSION "0.3.0-rc2"

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
#include "../ifcparse/Ifc2x3.h"
#include "../ifcparse/IfcFile.h"

namespace IfcParse {

	class Entity;
	class Entities;
	typedef Entity* EntityPtr;
	typedef SHARED_PTR<Entities> EntitiesPtr;

	typedef unsigned int Token;

	//
	// Provides functions to convert Tokens to binary data
	// Tokens are merely offsets to where they can be read in the file
	//
	class TokenFunc {
	private:
		static bool startsWith(Token t, char c);
	public:
		static unsigned int Offset(Token t);
		static bool isString(Token t);
		static bool isIdentifier(Token t);
		static bool isOperator(Token t, char op = 0);
		static bool isEnumeration(Token t);
		static bool isDatatype(Token t);
		static int asInt(Token t);
		static bool asBool(Token t);
		static double asFloat(Token t);
		static std::string asString(Token t);
		static std::string toString(Token t);
	};

	//
	// Functions for creating Tokens from an arbitary file offset
	// The first 4 bits are reserved for Tokens of type ()=,;$*
	//
	Token TokenPtr(unsigned int offset);
	Token TokenPtr(char c);	
	Token TokenPtr();

	//
	// Interprets a file as a sequential stream of Tokens
	//
	class Tokens {
	private:
		File* file;
		IfcCharacterDecoder* decoder;
	public:
		Tokens(File* f);
		Token Next();
		~Tokens();
		std::string TokenString(unsigned int offset);
	};

	//
	// Argument of type list, e.g.
	// #1=IfcDirection((1.,0.,0.));
	//                 ==========
	//
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

	//
	// Argument of type scalar or string, e.g.
	// #1=IfcVector(#2,1.0);
	//              == ===
	//
	class TokenArgument : public Argument {
	private:
		
	public: 
		Token token;
		TokenArgument(Token t);
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

	//
	// Argument of an IFC type
	// #1=IfcTrimmedCurve(#2,(IFCPARAMETERVALUE(0.)),(IFCPARAMETERVALUE(1.)),.T.,.PARAMETER.);
	//                        =====================   =====================
	//
	class EntityArgument : public Argument {
	private:		
		IfcUtil::IfcArgumentSelect* entity;		
	public:
		EntityArgument(Ifc2x3::Type::Enum ty, Token t);
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

	//
	// Entity defined in an IFC file, e.g.
	// #1=IfcDirection((1.,0.,0.));
	// ============================
	//
	class Entity : public IfcAbstractEntity {
	private:
		ArgumentPtr args;
		Ifc2x3::Type::Enum _type;
	public:
		unsigned int _id;
		unsigned int offset;		
		Entity(unsigned int i, Tokens* t);
		Entity(unsigned int i, Tokens* t, unsigned int o);
		~Entity();
		IfcEntities getInverse(Ifc2x3::Type::Enum c = Ifc2x3::Type::ALL);
		IfcEntities getInverse(Ifc2x3::Type::Enum c, int i, const std::string& a);
		void Load(std::vector<unsigned int>& ids, bool seek=false);
		ArgumentPtr getArgument (unsigned int i);
		unsigned int getArgumentCount();
		std::string toString(bool upper=false);
		std::string datatype();
		Ifc2x3::Type::Enum type() const;
		bool is(Ifc2x3::Type::Enum v) const;
		unsigned int id();
	};
}

typedef IfcUtil::IfcSchemaEntity IfcEntity;
typedef IfcEntities IfcEntities;
typedef std::map<Ifc2x3::Type::Enum,IfcEntities> MapEntitiesByType;
typedef std::map<unsigned int,IfcEntity> MapEntityById;
typedef std::map<std::string,Ifc2x3::IfcRoot::ptr> MapEntityByGuid;
typedef std::map<unsigned int,IfcEntities> MapEntitiesByRef;
typedef std::map<unsigned int,unsigned int> MapOffsetById;

//
// Several static convenience functions and variables
//
class Ifc {
private:
	static MapEntityById byid;
	static MapEntitiesByType bytype;
	static MapEntitiesByRef byref;
	static MapEntityByGuid byguid;
	static MapOffsetById offsets;
	static unsigned int lastId;
	static std::ostream* log1;
	static std::ostream* log2;
	static std::stringstream log_stream;
public:
	static MapEntityById::const_iterator First();
	static MapEntityById::const_iterator Last();
	static void SetOutput(std::ostream* l1, std::ostream* l2);
	static void LogMessage(const std::string& type, const std::string& message, const IfcAbstractEntityPtr entity=0);
	static IfcParse::File* file;
	static IfcParse::Tokens* tokens;
	template <class T>
	static typename T::list EntitiesByType() {
		IfcEntities e = EntitiesByType(T::Class());
		typename T::list l ( new IfcTemplatedEntityList<T>() );
		if ( e && e->Size() )
		for ( IfcEntityList::it it = e->begin(); it != e->end(); ++ it ) {
			l->push(reinterpret_pointer_cast<IfcUtil::IfcBaseClass,T>(*it));
		}
		return l;
	}
	static IfcEntities EntitiesByType(Ifc2x3::Type::Enum t);
	static IfcEntities EntitiesByReference(int id);
	static IfcEntity EntityById(int id);
	static Ifc2x3::IfcRoot::ptr Ifc::EntityByGuid(const std::string& guid);
	static bool Init(const std::string& fn);
	static bool Init(std::istream& fn, int len);
	static bool Init(void* data, int len);
	static bool Init(IfcParse::File* f);
	static std::string GetLog();
	static void Dispose();
	static bool hasPlaneAngleUnit;
	static double LengthUnit;
	static double PlaneAngleUnit;
	static int CircleSegments;
};

double UnitPrefixToValue( Ifc2x3::IfcSIPrefix::IfcSIPrefix v );

#endif
