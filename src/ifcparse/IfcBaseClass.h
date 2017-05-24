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

#ifndef IFCBASECLASS_H
#define IFCBASECLASS_H

#include "ifc_parse_api.h"

#ifdef USE_IFC4
#include "../ifcparse/Ifc4enum.h"
#else
#include "../ifcparse/Ifc2x3enum.h"
#endif

#include "../ifcparse/IfcEntityInstanceData.h"

class Argument;

namespace IfcUtil {

	class IFC_PARSE_API IfcBaseClass {
	public:
		virtual ~IfcBaseClass() {}
		IfcEntityInstanceData* entity;
		virtual bool is(IfcSchema::Type::Enum v) const = 0;
		virtual IfcSchema::Type::Enum type() const = 0;

		virtual unsigned int getArgumentCount() const = 0;
		virtual IfcUtil::ArgumentType getArgumentType(unsigned int i) const = 0;
		virtual IfcSchema::Type::Enum getArgumentEntity(unsigned int i) const = 0;
		virtual Argument* getArgument(unsigned int i) const = 0;
		virtual const char* getArgumentName(unsigned int i) const = 0;

		template <class T>
		T* as() {
			return is(T::Class())
				? static_cast<T*>(this)
				: static_cast<T*>(0);
		}

		template <class T>
		const T* as() const {
			return is(T::Class())
				? static_cast<const T*>(this)
				: static_cast<const T*>(0);
		}
	};

	class IFC_PARSE_API IfcBaseEntity : public IfcBaseClass {
	public:
		Argument* getArgumentByName(const std::string& name) const;
		std::vector<std::string> getAttributeNames() const;
		std::vector<std::string> getInverseAttributeNames() const;
		unsigned id() const { return entity->id(); }
	};

	// TODO: Investigate whether these should be template classes instead
	class IFC_PARSE_API IfcBaseType : public IfcBaseEntity {
	public:
		unsigned int getArgumentCount() const;
		Argument* getArgument(unsigned int i) const;
		const char* getArgumentName(unsigned int i) const;
		IfcSchema::Type::Enum getArgumentEntity(unsigned int /*i*/) const { return IfcSchema::Type::UNDEFINED; }
	};

}

#endif
