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

#ifdef USE_IFC4
#include "../ifcparse/Ifc4.h"
#else
#include "../ifcparse/Ifc2x3.h"
#endif

#include "../ifcparse/IfcFile.h"

namespace IfcParse {

	class Entity;
	class IfcFile;
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
		/// Returns whether the token can be interpreted as a syntactical operator
		static bool isOperator(const Token& t, char op = 0);
		/// Returns whether the token can be interpreted as an enumerated value
		static bool isEnumeration(const Token& t);
		/// Returns whether the token can be interpreted as a datatype name
		static bool isDatatype(const Token& t);
		/// Returns whether the token can be interpreted as an integer
		static bool isInt(const Token& t);
		/// Returns whether the token can be interpreted as a boolean
		static bool isBool(const Token& t);
		/// Returns whether the token can be interpreted as a floating point number
		static bool isFloat(const Token& t);
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
		unsigned int skipWhitespace();
		unsigned int skipComment();
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
		std::vector<Argument*> list;
		void Push(Argument* l);
	public:
		ArgumentList(Tokens* t, std::vector<unsigned int>& ids);
		~ArgumentList();

		IfcUtil::ArgumentType type() const;
		
		operator int() const;
		operator bool() const;
		operator double() const;
		operator std::string() const;
		operator std::vector<double>() const;
		operator std::vector<int>() const;
		operator std::vector<std::string>() const;
		operator IfcUtil::IfcBaseClass*() const;
		operator IfcEntityList::ptr() const;
        operator IfcEntityListList::ptr() const;
		unsigned int Size() const;
		Argument* operator [] (unsigned int i) const;
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

		IfcUtil::ArgumentType type() const;

		operator int() const;
		operator bool() const;
		operator double() const;
		operator std::string() const;
		operator std::vector<double>() const;
		operator std::vector<int>() const;
		operator std::vector<std::string>() const;
		operator IfcUtil::IfcBaseClass*() const;
		operator IfcEntityList::ptr() const;
        operator IfcEntityListList::ptr() const;
		unsigned int Size() const;
		Argument* operator [] (unsigned int i) const;
		std::string toString(bool upper=false) const;
		bool isNull() const;
	};

	/// Argument of an IFC simple type
	/// #1=IfcTrimmedCurve(#2,(IFCPARAMETERVALUE(0.)),(IFCPARAMETERVALUE(1.)),.T.,.PARAMETER.);
	///                        =====================   =====================
	class EntityArgument : public Argument {
	private:		
		IfcUtil::IfcArgumentSelect* entity;		
	public:
		EntityArgument(IfcSchema::Type::Enum ty, const Token& t);
		~EntityArgument();

		IfcUtil::ArgumentType type() const;

		operator int() const;
		operator bool() const;
		operator double() const;
		operator std::string() const;
		operator std::vector<double>() const;
		operator std::vector<int>() const;
		operator std::vector<std::string>() const;
		operator IfcUtil::IfcBaseClass*() const;
		operator IfcEntityList::ptr() const;
        operator IfcEntityListList::ptr() const;
		unsigned int Size() const;
		Argument* operator [] (unsigned int i) const;
		std::string toString(bool upper=false) const;
		bool isNull() const;
	};

	/// Entity defined in an IFC file, e.g.
	/// #1=IfcDirection((1.,0.,0.));
	/// ============================
	class Entity : public IfcAbstractEntity {
	private:
		mutable Argument* args;
		mutable IfcSchema::Type::Enum _type;
	public:
		/// The EXPRESS ENTITY_INSTANCE_NAME
		unsigned int _id;
		/// The offset at which the entity is read
		unsigned int offset;		
		Entity(unsigned int i, IfcFile* t);
		Entity(unsigned int i, IfcFile* t, unsigned int o);
		~Entity();
		IfcEntityList::ptr getInverse(IfcSchema::Type::Enum c = IfcSchema::Type::ALL);
		IfcEntityList::ptr getInverse(IfcSchema::Type::Enum c, int i, const std::string& a);
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

typedef std::map<IfcSchema::Type::Enum, IfcEntityList::ptr> MapEntitiesByType;
typedef std::map<unsigned int, IfcUtil::IfcBaseClass*> MapEntityById;
typedef std::map<std::string, IfcSchema::IfcRoot*> MapEntityByGuid;
typedef std::map<unsigned int, IfcEntityList::ptr> MapEntitiesByRef;
typedef std::map<unsigned int, unsigned int> MapOffsetById;

/// This class provides several static convenience functions and variables
/// and provide access to the entities in an IFC file
class IfcFile {
private:
	MapEntityById byid;
	MapEntitiesByType bytype;
	MapEntitiesByRef byref;
	MapEntityByGuid byguid;
	MapOffsetById offsets;
	unsigned int lastId;
	unsigned int MaxId;
	std::string _filename;
	std::string _timestamp;
	std::string _author;
	std::string _author_email;
	std::string _author_organisation;
	void initTimestamp();
public:
	typedef MapEntityById::const_iterator const_iterator;
	IfcFile();
	~IfcFile();
	/// Returns the first entity in the file, this probably is the entity with the lowest id (EXPRESS ENTITY_INSTANCE_NAME)
	const_iterator begin() const;
	/// Returns the last entity in the file, this probably is the entity with the highes id (EXPRESS ENTITY_INSTANCE_NAME)
	const_iterator end() const;
	IfcParse::IfcSpfStream* file;
	IfcParse::Tokens* tokens;
	/// Returns all entities in the file that match the template argument.
	/// NOTE: This also returns subtypes of the requested type, for example:
	/// IfcWall will also return IfcWallStandardCase entities
	template <class T>
	typename T::list::ptr EntitiesByType() {
		IfcEntityList::ptr e = EntitiesByType(T::Class());
		typename T::list::ptr l(new typename T::list);
		if (e && e->Size()) {
			for ( IfcEntityList::it it = e->begin(); it != e->end(); ++ it ) {
				l->push((T*)*it);
			}
		}
		return l;
	}
	/// Returns all entities in the file that match the positional argument.
	/// NOTE: This also returns subtypes of the requested type, for example:
	/// IfcWall will also return IfcWallStandardCase entities
	IfcEntityList::ptr EntitiesByType(IfcSchema::Type::Enum t);
	/// Returns all entities in the file that match the positional argument.
	/// NOTE: This also returns subtypes of the requested type, for example:
	/// IfcWall will also return IfcWallStandardCase entities
	IfcEntityList::ptr EntitiesByType(const std::string& t);
	/// Returns all entities in the file that reference the id
	IfcEntityList::ptr EntitiesByReference(int id);
	/// Returns the entity with the specified id
	IfcUtil::IfcBaseClass* EntityById(int id);
	/// Returns the entity with the specified GlobalId
	IfcSchema::IfcRoot* EntityByGuid(const std::string& guid);
	bool Init(const std::string& fn);
	bool Init(std::istream& fn, int len);
	bool Init(void* data, int len);
	bool Init(IfcParse::IfcSpfStream* f);
	unsigned int FreshId() { MaxId ++; return MaxId; }
	void AddEntity(IfcUtil::IfcBaseClass* entity);
	void AddEntities(IfcEntityList::ptr es);

	void filename(const std::string& s);
	std::string filename() const;
	void timestamp(const std::string& s);
	std::string timestamp() const;
	void author(const std::string& name, const std::string& email, const std::string& organisation);
	std::string authorName() const;
	std::string authorEmail() const;
	std::string authorOrganisation() const;
};

}

std::ostream& operator<< (std::ostream& os, const IfcParse::IfcFile& f);

#endif
