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

#include <boost/dynamic_bitset.hpp>

#include "IfcUtil.h"

namespace IfcWrite {
	class IfcWritableEntity : public IfcAbstractEntity {
	private:
		std::map<int,bool> writemask;
		std::map<int,Argument*> args;
		IfcSchema::Type::Enum _type;
		int* _id;
		bool arg_writable(int i);
		void arg_writable(int i, bool b);
		template <typename T> void _setArgument(int i, const T&);
	public:
		IfcWritableEntity(IfcSchema::Type::Enum t);
		~IfcWritableEntity();

		int setId(int i=-1);
		IfcWritableEntity(IfcAbstractEntity* e);
		IfcEntityList::ptr getInverse(IfcSchema::Type::Enum type, int attribute_index);
		std::string datatype() const;
		Argument* getArgument (unsigned int i);
		unsigned int getArgumentCount() const;
		IfcSchema::Type::Enum type() const;
		bool is(IfcSchema::Type::Enum v) const;
		std::string toString(bool upper=false) const;
		unsigned int id();
		IfcWritableEntity* isWritable();

		void setArgument(int i, Argument* a);

		void setArgument(int i);
		void setArgumentDerived(int i);
		
		void setArgument(int i,int v);
		void setArgument(int i,bool v);
		void setArgument(int i,double v);
		void setArgument(int i,const std::string& v);
		void setArgument(int i,const boost::dynamic_bitset<>& v);
		void setArgument(int i,int v, const char* c);
		void setArgument(int i,IfcUtil::IfcBaseClass* v);

		void setArgument(int i,const std::vector<int>& v);
		void setArgument(int i,const std::vector<double>& v);
		void setArgument(int i,const std::vector<std::string>& v);
		void setArgument(int i,const std::vector< boost::dynamic_bitset<> >& v);
		void setArgument(int i,IfcEntityList::ptr v);
		
		void setArgument(int i,const std::vector< std::vector<int> >& v);
		void setArgument(int i,const std::vector< std::vector<double> >& v);
		void setArgument(int i,IfcEntityListList::ptr v);		
	};

}

#endif
