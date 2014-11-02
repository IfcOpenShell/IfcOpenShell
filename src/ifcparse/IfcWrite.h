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
 * This namespace provides implementations of Argument and Entity that use STL  *
 * containers for their datatypes and are not just lazy references to the       *
 * IFC-SPF file. Therefore they can be modified by the client application.      *
 *                                                                              *
 ********************************************************************************/

#ifndef IFCWRITE_H
#define IFCWRITE_H

#include <boost/variant.hpp>
#include <boost/optional.hpp>

#include "../ifcparse/IfcUtil.h"
#include "../ifcparse/IfcParse.h"

namespace IfcWrite {

	/// This class is a writable container for attributes. A fundamental
	/// difference with the attribute types counterparts defined in the 
	/// IfcParse namespace is that this class has a Boost.Variant member
	/// for storing its value, whereas the IfcParse classes only contain
	/// lazy references to byte offsets in the IFC-SPF file.
	class IfcWriteArgument : public Argument {
	public:
		class EnumerationReference {
		public:
			int data;
			const char* enumeration_value;
			EnumerationReference(int data, const char* enumeration_value)
				: data(data), enumeration_value(enumeration_value) {}
		};		
		class Derived {};
	private:
		IfcAbstractEntity* entity;
		boost::variant<
			// A null argument, it will always serialize to $
			boost::none_t,
			// A derived argument, it will always serialize to *
			Derived,
			// An integer argument, e.g. 123  
			int, 
			// A boolean argument, it will serialize to either .T. or .F.
			bool, 
			// A floating point argument, e.g. 12.3
			double,
			// A character string argument, e.g. 'IfcOpenShell'
			std::string, 
			// A list of integers, e.g. (1,2,3)
			std::vector<int>,
			// A list of floats, e.g. (12.3,4.) 
			std::vector<double>,
			// A list of strings, e.g. ('Ifc','Open','Shell')
			std::vector<std::string>,
			// An enumeration argument, e.g. .USERDEFINED. 
			// To initialize the argument a string representation
			// has to be explicitely passed of the enumeration value
			// which is stored internally as an integer. The argument
			// itself does not keep track of what schema enumeration
			// type is represented.
			EnumerationReference,
			// An entity instance argument. It will either serialize to
			// e.g. #123 or datatype identifier for simple types, e.g. 
			// IFCREAL(12.3)
			IfcUtil::IfcBaseClass*,
			// An entity list argument. It will either serialize to
			// e.g. (#1,#2,#3) or datatype identifier for simple types,
			// e.g. (IFCREAL(1.2),IFCINTEGER(3.))
			IfcEntityList::ptr,
			// A list of list of entities. E.g. ((#1, #2), (#3))
			IfcEntityListList::ptr
		> container;
	public:
		enum argument_type {
			argument_type_null,
			argument_type_derived,
			argument_type_int, 
			argument_type_bool, 
			argument_type_double, 
			argument_type_string, 
			argument_type_vector_int,
			argument_type_vector_double,
			argument_type_vector_string,
			argument_type_enumeration,
			argument_type_entity,
			argument_type_entity_list,
			argument_type_entity_list_list
		};
		IfcWriteArgument(IfcAbstractEntity* e) : entity(e) {}
		template <typename T> const T& as() const {
			if (const T* val = boost::get<T>(&container)) {
				return *val;
			} else {
				throw IfcParse::IfcException("Invalid cast");
			}
		}
		template <typename T> void set(const T& t) {
			container = t;
		}
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
		bool isNull() const;
		Argument* operator [] (unsigned int i) const;
		std::string toString(bool upper=false) const;
		unsigned int Size() const;
		argument_type argumentType() const;
		IfcUtil::ArgumentType IfcWriteArgument::type() const;
	};

	/// An entity to help with passing of SELECT arguments that
	/// consist of simple types, for example useful to initialize
	/// a new IfcProperty.
	/// Proper memory management is difficult for now, so beware.
	class IfcSelectHelperEntity : public IfcAbstractEntity {
	private:
		IfcSchema::Type::Enum _type;
		IfcWriteArgument* arg;
	public:
		// FIXME: Make this a non-pointer argument and implement a copy constructor
		IfcSelectHelperEntity(IfcSchema::Type::Enum t, IfcWriteArgument* a) : _type(t), arg(a) {}
		IfcEntityList::ptr getInverse(IfcSchema::Type::Enum,int,const std::string &);
		IfcEntityList::ptr getInverse(IfcSchema::Type::Enum);
		std::string datatype() const;
		Argument* getArgument(unsigned int i);
		unsigned int getArgumentCount() const;
		IfcSchema::Type::Enum type() const;
		bool is(IfcSchema::Type::Enum t) const;
		std::string toString(bool upper = false) const;
		unsigned int id();
		IfcWritableEntity* isWritable();
	};

	/// A helper class for passing of SELECT arguments that
	/// consist of simple types, for example useful to initialize
	/// a new IfcProperty.
	/// Proper memory management is difficult for now, so beware.
	class IfcSelectHelper : public IfcUtil::IfcBaseClass {
	public:
		IfcSelectHelper(const std::string& v, IfcSchema::Type::Enum t=IfcSchema::Type::IfcText);
		IfcSelectHelper(const char* const v, IfcSchema::Type::Enum t=IfcSchema::Type::IfcText);
		IfcSelectHelper(int v, IfcSchema::Type::Enum t=IfcSchema::Type::IfcInteger);
		IfcSelectHelper(double v, IfcSchema::Type::Enum t=IfcSchema::Type::IfcReal);
		IfcSelectHelper(bool v, IfcSchema::Type::Enum t=IfcSchema::Type::IfcBoolean);
		bool is(IfcSchema::Type::Enum t) const;
		IfcSchema::Type::Enum type() const;
	};
	
	/// A helper class for the creation of IFC GlobalIds.
	class IfcGuidHelper {
	private:
		std::string data;
		static bool seeded;
	public:
		static const unsigned int length = 22;
		IfcGuidHelper();
		operator std::string() const;
	};

	// Accumulates all schema instances created from constructors
	// This way they can be added in a single batch to the IfcFile
	class EntityBuffer {
	private:
		IfcEntityList::ptr buffer;
		static EntityBuffer* i;
		static EntityBuffer* instance();
	public:
		static IfcEntityList::ptr Get();
		static void Clear();
		static void Add(IfcUtil::IfcBaseClass* e);
	};

}

#endif
