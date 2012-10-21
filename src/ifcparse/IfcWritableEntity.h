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
 * An IfcWritableEntity can be constructed from a regular IfcParse entity to be *
 * able to modify the data in existing IFC files.                               *
 *                                                                              *
 ********************************************************************************/

#ifndef IFCWRITABLEENTITY_H
#define IFCWRITABLEENTITY_H

#include <map>

#include "IfcUtil.h"

namespace IfcWrite {
	class IfcWritableEntity : public IfcAbstractEntity {
	private:
		std::map<int,bool> writemask;
		std::map<int,ArgumentPtr> args;
		Ifc2x3::Type::Enum _type;
		int* _id;
		bool arg_writable(int i);
		void arg_writable(int i, bool b);
	public:
		IfcWritableEntity(Ifc2x3::Type::Enum t);
		int setId(int i=-1);
		IfcWritableEntity(IfcAbstractEntity* e);
		IfcEntities getInverse(Ifc2x3::Type::Enum c = Ifc2x3::Type::ALL);
		IfcEntities getInverse(Ifc2x3::Type::Enum c, int i, const std::string& a);
		std::string datatype();
		ArgumentPtr getArgument (unsigned int i);
		unsigned int getArgumentCount();
		Ifc2x3::Type::Enum type() const;
		bool is(Ifc2x3::Type::Enum v) const;
		std::string toString(bool upper=false);
		unsigned int id();
		bool isWritable();
        void setArgument(int i);
		void setArgument(int i,int v);
		void setArgument(int i,int v, const char* c);
		void setArgument(int i,const std::string& v);
		void setArgument(int i,double v);
		void setArgument(int i,IfcUtil::IfcSchemaEntity v);
		void setArgument(int i,IfcEntities v);
		void setArgument(int i,const std::vector<double>& v);
		void setArgument(int i,const std::vector<std::string>& v);
		void setArgument(int i,const std::vector<int>& v);
	};

}

#endif
