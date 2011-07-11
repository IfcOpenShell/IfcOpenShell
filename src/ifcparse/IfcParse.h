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
 * its entities either by ID, by an IfcSchema::Enum::IfcType or by reference    * 
 *                                                                              *
 ********************************************************************************/

#ifndef IFCPARSE_H
#define IFCPARSE_H

#include <string>
#include <sstream>
#include <iostream>
#include <vector>
#include <fstream>
#include <cstring>
#include <map>
#include <exception>

// Pick a shared pointer implementation
#ifdef __GNUC__
#include <tr1/memory>
#define SHARED_PTR std::tr1::shared_ptr
#else
#ifdef _MSC_VER
#include <memory>
#define SHARED_PTR std::tr1::shared_ptr
#else
#include <boost/shared_ptr.hpp>
#define SHARED_PTR boost::shared_ptr
#endif
#endif

#include "../ifcparse/IfcEnum.h"

const int BUF_SIZE = (32 * 1024 * 1024);

namespace IfcParse {

	class Entity;
	class Entities;
	typedef SHARED_PTR<Entity> EntityPtr;
	typedef SHARED_PTR<Entities> EntitiesPtr;

	//
	// Reads a file in chunks of BUF_SIZE and provides 
	// functions to randomly access its contents
	//
	class File {
	private:
		std::ifstream stream;
		char* buffer;
		unsigned int ptr;
		unsigned int len;
		unsigned int offset;
		void ReadBuffer(bool inc=true);
	public:
		bool eof;
		unsigned int size;
		File(const std::string& fn);
		char Peek();
		char Read(unsigned int offset);
		void Inc();		
		void Close();
		void Seek(unsigned int offset);
		unsigned int Tell();
	};

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
		static float asFloat(Token t);
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
	public:
		Tokens(File* f);
		Token Next();
		std::string TokenString(unsigned int offset);
	};

	class Argument;
	typedef SHARED_PTR<Argument> ArgumentPtr;

	//
	// Base class of all kind of Arguments used in IFC entity defintions
	//
	class Argument {
	protected:
	public:
		virtual operator int() const = 0;
		virtual operator bool() const = 0;
		virtual operator float() const = 0;
		virtual operator std::string() const = 0;
		virtual operator EntityPtr() const = 0;
		virtual operator EntitiesPtr() const = 0;
		virtual unsigned int Size() const = 0;
		virtual ArgumentPtr operator [] (unsigned int i) const = 0;
		virtual std::string toString() const = 0;
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
		operator int() const;
		operator bool() const;
		operator float() const;
		operator std::string() const;
		operator EntityPtr() const;
		operator EntitiesPtr() const;
		unsigned int Size() const;
		ArgumentPtr operator [] (unsigned int i) const;
		std::string toString() const;
	};

	//
	// Argument of type scalar or string, e.g.
	// #1=IfcVector(#2,1.0);
	//              == ===
	//
	class TokenArgument : public Argument {
	private:
		Token token;
	public: 
		TokenArgument(Token t);
		operator int() const;
		operator bool() const;
		operator float() const;
		operator std::string() const;
		operator EntityPtr() const;
		operator EntitiesPtr() const;
		unsigned int Size() const;
		ArgumentPtr operator [] (unsigned int i) const;
		std::string toString() const;
	};

	//
	// Argument of an IFC type
	// #1=IfcTrimmedCurve(#2,(IFCPARAMETERVALUE(0.)),(IFCPARAMETERVALUE(1.)),.T.,.PARAMETER.);
	//                        =====================   =====================
	//
	class EntityArgument : public Argument {
	private:		
		EntityPtr entity;		
	public:
		EntityArgument(EntityPtr e);
		operator int() const;
		operator bool() const;
		operator float() const;
		operator std::string() const;
		operator EntityPtr() const;
		operator EntitiesPtr() const;
		unsigned int Size() const;
		ArgumentPtr operator [] (unsigned int i) const;
		std::string toString() const;
	};

	//
	// Entity defined in an IFC file, e.g.
	// #1=IfcDirection((1.,0.,0.));
	// ============================
	//
	class Entity {
	private:
		ArgumentPtr args;
		void Load(std::vector<unsigned int>& ids, bool seek);
	public:
		unsigned int id;
		unsigned int offset;
		IfcSchema::Enum::IfcTypes type;
		Entity(unsigned int i, Tokens* t, std::vector<unsigned int>& ids, bool parse = false);
		Entity(unsigned int i, Tokens* t, unsigned int o);
		EntitiesPtr parents(IfcSchema::Enum::IfcTypes c = IfcSchema::Enum::ALL);
		EntitiesPtr parents(IfcSchema::Enum::IfcTypes c, int i, const std::string& a);
		ArgumentPtr operator[] (unsigned int i);
		std::string toString();
		std::string Datatype() const;
	};

	//
	// A list of IFC entities
	//
	class Entities {
		std::vector<EntityPtr> ls;
	public:
		typedef std::vector<EntityPtr>::const_iterator it;
		void push(EntityPtr l);
		void push(EntitiesPtr l);
		it begin();
		it end();
		EntitiesPtr parents(IfcSchema::Enum::IfcTypes c = IfcSchema::Enum::ALL);
		EntitiesPtr parents(IfcSchema::Enum::IfcTypes c, int i, const std::string& a);
		EntityPtr operator[] (int i);
		int Size() const;
	};

	class IfcException : public std::exception {
	private:
		std::string error;
	public:
		IfcException(std::string e);
		const char* what() const throw();
	};
}

typedef IfcParse::EntityPtr IfcEntity;
typedef IfcParse::EntitiesPtr IfcEntities;
typedef std::map<IfcSchema::Enum::IfcTypes,IfcEntities> MapEntitiesByType;
typedef std::map<unsigned int,IfcEntity> MapEntityById;
typedef std::map<unsigned int,IfcEntities> MapEntitiesByRef;
typedef std::map<unsigned int,unsigned int> MapOffsetById;

//
// Several static convenience functions and variables
//
class Ifc {
private:
	static MapEntitiesByType bytype;
	static MapEntityById byid;
	static MapEntitiesByRef byref;
	static MapOffsetById offsets;
	static unsigned int lastId;
public:
	static IfcParse::File* file;
	static IfcParse::Tokens* tokens;
	static IfcEntities EntitiesByType(IfcSchema::Enum::IfcTypes t);
	static IfcEntities EntitiesByReference(int id);
	static IfcEntity EntityById(int id);
	static bool Init(const std::string& fn);
	static void Dispose();
	static float LengthUnit;
	static float PlaneAngleUnit;
	static int CircleSegments;
};

float UnitPrefixToValue(const std::string& s);

#endif
