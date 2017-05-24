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

#ifndef IFCENTITYDESCRIPTOR_H
#define IFCENTITYDESCRIPTOR_H

#include <string>
#include <vector>
#include <sstream>
#include <iostream>
#include <algorithm>

#include <boost/shared_ptr.hpp>

#include "../ifcparse/IfcBaseClass.h"
#include "../ifcparse/IfcException.h"

#ifdef USE_IFC4
#include "../ifcparse/Ifc4enum.h"
#else
#include "../ifcparse/Ifc2x3enum.h"
#endif

namespace IfcUtil {

	class IFC_PARSE_API IfcEnumerationDescriptor {
	private:
		IfcSchema::Type::Enum type;
		std::vector<std::string> values;
	public:
		IfcEnumerationDescriptor(IfcSchema::Type::Enum type, const std::vector<std::string>& values)
			: type(type), values(values) {}
		std::pair<const char*, int> getIndex(const std::string& value) const {
			std::vector<std::string>::const_iterator it = std::find(values.begin(), values.end(), value);
			if (it != values.end()) {
				return std::make_pair(it->c_str(), (int)std::distance(it, values.begin()));
			} else {
				throw IfcParse::IfcException("Invalid enumeration value");
			}
		}
		const std::vector<std::string>& getValues() {
			return values;
		}
		IfcSchema::Type::Enum getType() {
			return type;
		}
	};

	class IFC_PARSE_API IfcEntityDescriptor {
	public:
		class IfcArgumentDescriptor
		{
		public:
			std::string name;
			bool optional;
			ArgumentType argument_type;
			IfcSchema::Type::Enum data_type;
			IfcArgumentDescriptor(const std::string& name, bool optional, ArgumentType argument_type, IfcSchema::Type::Enum data_type)
				: name(name), optional(optional), argument_type(argument_type), data_type(data_type) {}
		};
	private:
		IfcSchema::Type::Enum type;
		IfcEntityDescriptor* parent;
		std::vector<IfcArgumentDescriptor> arguments;
		unsigned argument_start() const {
			return parent ? parent->getArgumentCount() : 0;
		}
		const IfcArgumentDescriptor& get_argument(unsigned i) const {
			if (i < arguments.size()) return arguments[i];
			else throw IfcParse::IfcAttributeOutOfRangeException("Argument index out of range");
		}
	public:
		IfcEntityDescriptor(IfcSchema::Type::Enum type, IfcEntityDescriptor* parent)
			: type(type), parent(parent) {}
		void add(const std::string& name, bool optional, ArgumentType argument_type, IfcSchema::Type::Enum data_type = IfcSchema::Type::UNDEFINED) {
			arguments.push_back(IfcArgumentDescriptor(name, optional, argument_type, data_type));
		}
		unsigned getArgumentCount() const {
			return (parent ? parent->getArgumentCount() : 0) + (unsigned)arguments.size();
		}
		const std::string& getArgumentName(unsigned i) const {
			const unsigned a = argument_start();
			return i < a
				? parent->getArgumentName(i)
				: get_argument(i-a).name;
		}
		ArgumentType getArgumentType(unsigned i) const {
			const unsigned a = argument_start();
			return i < a
				? parent->getArgumentType(i)
				: get_argument(i-a).argument_type;
		}
		bool getArgumentOptional(unsigned i) const {
			const unsigned a = argument_start();
			return i < a
				? parent->getArgumentOptional(i)
				: get_argument(i-a).optional;
		}
		IfcSchema::Type::Enum getArgumentEntity(unsigned i) const {
			const unsigned a = argument_start();
			return i < a
				? parent->getArgumentEntity(i)
				: get_argument(i-a).data_type;
		}
		unsigned getArgumentIndex(const std::string& s) const {
			unsigned a = argument_start();
			for(std::vector<IfcArgumentDescriptor>::const_iterator i = arguments.begin(); i != arguments.end(); ++i) {
				if (i->name == s) return a;
				a++;
			}
			if (parent) return parent->getArgumentIndex(s);
			throw IfcParse::IfcException(std::string("Argument ") + s + " not found on " + IfcSchema::Type::ToString(type));
		}		
	};   
}

#endif
