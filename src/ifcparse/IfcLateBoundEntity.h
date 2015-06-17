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

#ifndef IFCLATEBOUNDENTITY_H
#define IFCLATEBOUNDENTITY_H

#include <string>

#include "../ifcparse/IfcUtil.h"
#include "../ifcparse/IfcWrite.h"
#include "../ifcparse/IfcWritableEntity.h"

namespace IfcParse {
	
	// TODO: Somehow these methods should become part of IfcBaseEntity directly so
	// that in the IfcFile class the distinction what entity type to be created is 
	// no longer necessary and weird diagonal casts when creating geometry from
	// IfcLateBoundEntities are eliminated.
	class IfcLateBoundEntity : public IfcUtil::IfcBaseEntity {
	private:
		IfcSchema::Type::Enum _type;
		IfcWrite::IfcWritableEntity* writable_entity();
		void invalid_argument(unsigned int i, const std::string& t);
	public:
		IfcLateBoundEntity(const std::string& s);
		IfcLateBoundEntity(IfcAbstractEntity* e);
		
		bool is(IfcSchema::Type::Enum v) const;
		IfcSchema::Type::Enum type() const;	
		bool is_a(const std::string& s) const;
		std::string is_a() const;

		unsigned int id() const;
		unsigned int getArgumentCount() const;
		IfcUtil::ArgumentType getArgumentType(unsigned int i) const;
		IfcSchema::Type::Enum getArgumentEntity(unsigned int i) const;
		Argument* getArgument(unsigned int i) const;
		const char* getArgumentName(unsigned int i) const;
		unsigned getArgumentIndex(const std::string& a) const;
		bool getArgumentOptionality(unsigned int i) const;

		IfcEntityList::ptr get_inverse(const std::string& a);

		std::vector<std::string> getAttributeNames() const;
		std::vector<std::string> getInverseAttributeNames() const;

		void setArgumentAsNull(unsigned int i);
		void setArgumentAsInt(unsigned int i, int v);
		void setArgumentAsBool(unsigned int i, bool v);
		void setArgumentAsDouble(unsigned int i, double v);
		void setArgumentAsString(unsigned int i, const std::string& v);
		void setArgumentAsEntityInstance(unsigned int i, IfcLateBoundEntity* v);
		
		void setArgumentAsAggregateOfInt(unsigned int i, const std::vector<int>& v);
		void setArgumentAsAggregateOfDouble(unsigned int i, const std::vector<double>& v);
		void setArgumentAsAggregateOfString(unsigned int i, const std::vector<std::string>& v);
		void setArgumentAsAggregateOfEntityInstance(unsigned int i, IfcEntityList::ptr v);
		
		void setArgumentAsAggregateOfAggregateOfInt(unsigned int i, const std::vector< std::vector<int> >& v);
		void setArgumentAsAggregateOfAggregateOfDouble(unsigned int i, const std::vector< std::vector<double> >& v);
		void setArgumentAsAggregateOfAggregateOfEntityInstance(unsigned int i, IfcEntityListList::ptr v);

		std::string toString();

		bool is_valid();
	};

}

#endif