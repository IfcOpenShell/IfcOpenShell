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
#include <boost/dynamic_bitset.hpp>

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

			// SCALARS:
			int, 
			// A boolean argument, it will serialize to either .T. or .F.
			bool, 
			// A floating point argument, e.g. 12.3
			double,
			// A character string argument, e.g. 'IfcOpenShell'
			std::string,
			// A binary argument, e.g. "092A" -> 100100101010
			boost::dynamic_bitset<>,
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

			// AGGREGATES:
			// An aggregate of integers, e.g. (1,2,3)
			std::vector<int>,
			// An aggregate of floats, e.g. (12.3,4.) 
			std::vector<double>,
			// An aggregate of strings, e.g. ('Ifc','Open','Shell')
			std::vector<std::string>,
			// An aggregate of binaries, e.g. ("23B", "092A") -> (111011, 100100101010)
			std::vector<boost::dynamic_bitset<> >,
			// An aggregate of entity instances. It will either serialize to
			// e.g. (#1,#2,#3) or datatype identifier for simple types,
			// e.g. (IFCREAL(1.2),IFCINTEGER(3.))
			IfcEntityList::ptr,

			// AGGREGATES OF AGGREGATES:
			// An aggregate of an aggregate of ints. E.g. ((1, 2), (3))
			std::vector< std::vector<int> >,
			// An aggregate of an aggregate of floats. E.g. ((1., 2.3), (4.))
			std::vector< std::vector<double> >,
			// An aggregate of an aggregate of entities. E.g. ((#1, #2), (#3))
			IfcEntityListList::ptr
		> container;
	public:
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
		Argument* operator [] (unsigned int i) const;
		std::string toString(bool upper=false) const;
		unsigned int size() const;
		IfcUtil::ArgumentType type() const;
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
