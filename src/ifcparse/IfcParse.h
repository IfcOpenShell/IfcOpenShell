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

class Ifc;

namespace IfcParse {

	class Entity;
	class Entities;
	typedef SHARED_PTR<Entity> EntityPtr;
	typedef SHARED_PTR<Entities> EntitiesPtr;

	class Argument {
	private:
		static std::vector<std::string> datatypes;
		static std::vector<std::string> enumstrings;
		static std::vector<std::string> argstrings;

		int _data;
		float _number;
		EntityPtr _entity;
	public:
		enum vartype { IDENTIFIER, STRING, NUMBER, OPERATOR, ENUMERATION, DATATYPE, SUB_ENTITY };
		vartype type;

		Argument(const std::string& s);
		Argument(const EntityPtr e);

		bool isOp(char op = 0) const;

		float f() const;
		int i() const;
		std::string s() const;
		bool b() const;
		EntityPtr r() const;

		std::string toString() const;

		std::string typeString() const;

		friend class ::Ifc;
	};

	class ArgumentList {
	private:
		std::vector<ArgumentList*> _levels;
		std::vector<ArgumentList*> _args;
		ArgumentList* _current;
		const Argument* _arg;
		void _push();
		bool _pop();
		void _append(const Argument* v);
	public:	
		ArgumentList();
		~ArgumentList();

		float f() const;
		int i() const;
		std::string s() const;
		bool b() const;
		EntityPtr ref() const;
		EntitiesPtr refs() const;
		ArgumentList* arg(int i) const;

		int count() const;	
		std::string toString() const;

		friend class Entity;
	};

	class Entity {
	private:
		inline bool term(char last);
	public:
		int id;
		IfcSchema::Enum::IfcTypes dt;
		ArgumentList* args;
		Argument* _dt;

		Entity(std::istream* ss, std::vector<int>& refs, bool sub = false);
		~Entity();

		ArgumentList* arg(int i) const;
		std::string toString() const;

		EntitiesPtr parents(IfcSchema::Enum::IfcTypes c = IfcSchema::Enum::ALL);
		EntitiesPtr parents(IfcSchema::Enum::IfcTypes c, int i, const std::string& a);
		bool isAssignment() const;
		std::string datatype() const;
	};

	class Entities {
	private:
		std::vector<EntityPtr> ls;
	public:
		int size;
		typedef std::vector<EntityPtr>::const_iterator it;
		void push(EntityPtr l);
		void pushs(EntitiesPtr l);
		it begin();
		it end();
		EntitiesPtr parents(IfcSchema::Enum::IfcTypes c = IfcSchema::Enum::ALL);
		EntitiesPtr parents(IfcSchema::Enum::IfcTypes c, int i, const std::string& a);
		Entities();
		EntityPtr operator[] (int i);
	};

	class File {
	public:
		std::map<IfcSchema::Enum::IfcTypes,EntitiesPtr> bytype;
		std::map<int,EntityPtr> byid;
		std::map<int,EntitiesPtr> byref;
		bool valid;

		File(std::string fn, bool debug = false);
		EntitiesPtr EntitiesByType(IfcSchema::Enum::IfcTypes t);
		EntitiesPtr EntitiesByReference(int id);
		EntityPtr EntityById(int id);
	};

	class IfcException : public std::exception {
	private:
		std::string w;
	public:
		IfcException(int id);
		IfcException();
		~IfcException() throw();
		virtual const char* what() const throw();
	};

}

typedef IfcParse::EntityPtr IfcEntity;
typedef IfcParse::EntitiesPtr IfcEntities;

float UnitPrefixToValue(const std::string& s);

class Ifc {
private:
	static IfcParse::File* f;
public:
	static IfcEntities EntitiesByType(IfcSchema::Enum::IfcTypes t);
	static IfcEntities EntitiesByReference(int id);
	static IfcEntity EntityById(int id);
	static bool Init(std::string fn);
	static void Dispose();
	static float LengthUnit;
	static float PlaneAngleUnit;
	static int CircleSegments;
};

#endif
