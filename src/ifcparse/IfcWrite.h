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

#include "IfcUtil.h"
#include "IfcParse.h"

namespace IfcWrite {

	/// A placeholder class for grouping functionality geared towards writing IFC files
	class IfcWriteArgument : public Argument {

	};

	/// A null argument. It will always serialize to $
	class IfcWriteNullArgument : public IfcWriteArgument {
	public:
		operator int() const;
		operator bool() const;
		operator double() const;
		operator std::string() const;
		operator std::vector<double>() const;
		operator std::vector<int>() const;
		operator std::vector<std::string>() const;
		operator IfcUtil::IfcSchemaEntity() const;
		operator IfcEntities() const;
		bool isNull() const;
		ArgumentPtr operator [] (unsigned int i) const;
		std::string toString(bool upper=false) const;
		unsigned int Size() const;
	};
	
	/// An entity list argument. It will serialize to (#1,#2,#3)
	/// with possibly a datatype identifier for SELECT types, e.g:
	/// (IFCREAL(1.0),IFCINTEGER(1))
	class IfcWriteEntityListArgument : public IfcWriteArgument {
	private:
		IfcEntities value;
	public:
		IfcWriteEntityListArgument(const IfcEntities& v);
		operator int() const;
		operator bool() const;
		operator double() const;
		operator std::string() const;
		operator std::vector<double>() const;
		operator std::vector<int>() const;
		operator std::vector<std::string>() const;
		operator IfcUtil::IfcSchemaEntity() const;
		operator IfcEntities() const;
		bool isNull() const;
		unsigned int Size() const;
		ArgumentPtr operator [] (unsigned int i) const;
		std::string toString(bool upper=false) const;
	};

	/// An enumeration argument. It will serialize to e.g:
	/// .USERDEFINED. To initialize the argument a string representation
	/// has to be explicitely passed of the enumeration value which
	/// is stored internally as an integer. The argument itself
	/// does not keep track of what schema enumeration type is
	/// represented.
	class IfcWriteEnumerationArgument : public IfcWriteArgument {
	private:
		int data;
		const char* enumeration_value;
	public:
		IfcWriteEnumerationArgument(int v, const char* c);
		operator int() const;
		operator bool() const;
		operator double() const;
		operator std::string() const;
		operator std::vector<double>() const;
		operator std::vector<int>() const;
		operator std::vector<std::string>() const;
		operator IfcUtil::IfcSchemaEntity() const;
		operator IfcEntities() const;
		bool isNull() const;
		ArgumentPtr operator [] (unsigned int i) const;
		std::string toString(bool upper=false) const;
		unsigned int Size() const;
	};
	
	/// An argument for all remaining types of arguments. For example:
	/// #123 | 1 | 'Value' | (1.0,2.0,3.0). All data is casted to a 
	/// void pointer.
	class IfcWriteIntegralArgument : public IfcWriteArgument {
	private:
		void* data;
		IfcUtil::ArgumentType type;
	public:
		IfcWriteIntegralArgument(int v);
		IfcWriteIntegralArgument(bool v);
		IfcWriteIntegralArgument(double v);
		IfcWriteIntegralArgument(const std::string& v);
		IfcWriteIntegralArgument(const std::vector<int> v);
		IfcWriteIntegralArgument(const std::vector<double> v);
		IfcWriteIntegralArgument(const std::vector<std::string> v);
		IfcWriteIntegralArgument(IfcUtil::IfcSchemaEntity v);
		~IfcWriteIntegralArgument();
		operator int() const;
		operator bool() const;
		operator double() const;
		operator std::string() const;
		operator std::vector<double>() const;
		operator std::vector<int>() const;
		operator std::vector<std::string>() const;
		operator IfcUtil::IfcSchemaEntity() const;
		operator IfcEntities() const;
		bool isNull() const;
		unsigned int Size() const;
		ArgumentPtr operator [] (unsigned int i) const;
		std::string toString(bool upper=false) const;
	};

	/// An entity to help with passing of SELECT arguments that
	/// consist of simple types, for example useful to initialize
	/// a new IfcProperty.
	/// Proper memory management is difficult for now, so beware.
	class IfcSelectHelperEntity : public IfcAbstractEntity {
	private:
		Ifc2x3::Type::Enum _type;
		IfcWriteArgument* arg;
	public:
		// FIXME: Make this a non-pointer argument and implement a copy constructor
		IfcSelectHelperEntity(Ifc2x3::Type::Enum t, IfcWriteArgument* a) : _type(t), arg(a) {}
		IfcEntities getInverse(Ifc2x3::Type::Enum,int,const std::string &);
		IfcEntities getInverse(Ifc2x3::Type::Enum);
		std::string datatype();
		ArgumentPtr getArgument(unsigned int i);
		unsigned int getArgumentCount();
		Ifc2x3::Type::Enum type() const;
		bool is(Ifc2x3::Type::Enum t) const;
		std::string toString(bool upper = false);
		unsigned int id();
		bool isWritable();
	};

	/// A helper class for passing of SELECT arguments that
	/// consist of simple types, for example useful to initialize
	/// a new IfcProperty.
	/// Proper memory management is difficult for now, so beware.
	class IfcSelectHelper : public IfcUtil::IfcBaseClass {
	public:
		IfcSelectHelper(const std::string& v, Ifc2x3::Type::Enum t=Ifc2x3::Type::IfcText);
		IfcSelectHelper(const char* const v, Ifc2x3::Type::Enum t=Ifc2x3::Type::IfcText);
		IfcSelectHelper(int v, Ifc2x3::Type::Enum t=Ifc2x3::Type::IfcInteger);
		IfcSelectHelper(float v, Ifc2x3::Type::Enum t=Ifc2x3::Type::IfcReal);
		IfcSelectHelper(bool v, Ifc2x3::Type::Enum t=Ifc2x3::Type::IfcBoolean);
		bool is(Ifc2x3::Type::Enum t) const;
		Ifc2x3::Type::Enum type() const;
	};
	
	/// A helper class for the creation of IFC GlobalIds.
	/// At this moment an actual UUID is not generated according to
	/// the ISO standard, but merely a sequence of random characters.
	class IfcGuidHelper {
	private:
		std::string data;
		static bool seeded;
	public:
		static const unsigned int length = 22;
		IfcGuidHelper();
		operator std::string() const;
	};

}

#endif