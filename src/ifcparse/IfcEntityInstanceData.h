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

#ifndef IFCENTITYINSTANCEDATA_H
#define IFCENTITYINSTANCEDATA_H

#include "../ifcparse/ArgumentType.h"

#include <boost/shared_ptr.hpp>

#include <vector>

class Argument;
class IfcEntityList;
namespace IfcParse {
	class IfcFile;
}

class IFC_PARSE_API IfcEntityInstanceData {
public:
	// Public for backwards compatibility
	IfcParse::IfcFile* file;
protected:
	unsigned id_;
	IfcSchema::Type::Enum type_;
	mutable std::vector<Argument*> attributes_;

	// To reduce memory footprint, these two could potentially be combined,
	// e.g. initialized_ <-> offset_in_file_ == 0, but it would imply that
	// instances cannot be located at the beginning of the file. Officially
	// there should be a header anyways.
	mutable bool initialized_;
	unsigned offset_in_file_;

public:
	IfcEntityInstanceData(IfcSchema::Type::Enum type, IfcParse::IfcFile* file_, unsigned id = 0, unsigned offset_in_file = 0)
		: file(file_), id_(id), type_(type), initialized_(false), offset_in_file_(offset_in_file)
	{}

	IfcEntityInstanceData(IfcSchema::Type::Enum type)
		: file(0), id_(0), type_(type), initialized_(true)
	{}

	/*
	IfcEntityInstanceData(IfcParse::IfcFile* file = 0, unsigned id = 0, IfcSchema::Type::Enum type = IfcSchema::Type::UNDEFINED, unsigned offset_in_file = 0, size_t n)
	: file_(file), id_(0), type_(type), initialized_(false)
	{
	attributes_.reserve(n);
	}

	IfcEntityInstanceData(IfcParse::IfcFile* file = 0, unsigned id = 0, IfcSchema::Type::Enum type = IfcSchema::Type::UNDEFINED, const std::vector<Argument*>& attributes)
	: file_(file), id_(0), type_(type), attributes_(attributes), initialized_(true)
	{}
	*/

	void load() const;

	IfcEntityInstanceData(const IfcEntityInstanceData& e);

	~IfcEntityInstanceData();

	boost::shared_ptr<IfcEntityList> getInverse(IfcSchema::Type::Enum type, int attribute_index);

	Argument* getArgument(unsigned int i) const;

	// NB: This makes a copy of the argument
	void setArgument(unsigned int i, Argument* a, IfcUtil::ArgumentType attr_type = IfcUtil::Argument_UNKNOWN);

	unsigned int getArgumentCount() const {
		if (!initialized_) {
			load();
		}
		return (unsigned int)attributes_.size();
	}

	IfcSchema::Type::Enum type() const {
		return type_;
	}

	std::string toString(bool upper = false) const;

	unsigned int id() const { return id_; }
	unsigned int offset_in_file() const { return offset_in_file_; }

	// NB: const ommitted for lazy loading
	std::vector<Argument*>& attributes() const { return attributes_; }

	unsigned set_id(boost::optional<unsigned> i = boost::none);
};

#endif
