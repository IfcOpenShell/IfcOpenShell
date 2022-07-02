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

#include <boost/optional.hpp>
#include <boost/shared_ptr.hpp>

#include <vector>

class Argument;
class aggregate_of_instance;
namespace IfcParse {
	class IfcFile;
}

class IFC_PARSE_API IfcEntityInstanceData {
public:
	// Public for backwards compatibility
	IfcParse::IfcFile* file;
protected:
	unsigned id_;
	const IfcParse::declaration* type_;
	mutable Argument** attributes_;
	unsigned offset_in_file_;

public:
	IfcEntityInstanceData(const IfcParse::declaration* type, IfcParse::IfcFile* file_, unsigned id = 0, unsigned offset_in_file = 0)
		: file(file_), id_(id), type_(type), attributes_(0), offset_in_file_(offset_in_file)
	{}

   IfcEntityInstanceData(IfcParse::IfcFile* file_, size_t size)
      : file(file_), id_(0), type_(0), attributes_(new Argument*[size] {0}), offset_in_file_(0)
	{}

   IfcEntityInstanceData(const IfcParse::declaration* type)
      : file(0), id_(0), type_(type), attributes_(new Argument*[getArgumentCount()]{ 0 }), offset_in_file_(0)
   {}

	void load() const;

	IfcEntityInstanceData(const IfcEntityInstanceData& e);

	virtual ~IfcEntityInstanceData();

	boost::shared_ptr<aggregate_of_instance> getInverse (const IfcParse::declaration* type, int attribute_index) const;

	Argument* getArgument(size_t i) const;

	// NB: This makes a copy of the argument if make_copy is set
	void setArgument(size_t i, Argument* a, IfcUtil::ArgumentType attr_type = IfcUtil::Argument_UNKNOWN, bool make_copy = false);

	virtual size_t getArgumentCount() const {
		if (type_ == 0) {
			return 0;
		}
		if (type_->as_entity()) {
			return type_->as_entity()->attribute_count();
		} else {
			return 1;
		}
	}

	void clearArguments();

	const IfcParse::declaration* type() const {
		return type_;
	}

	std::string toString(bool upper = false) const;

	unsigned int id() const { return id_; }
	unsigned int offset_in_file() const { return offset_in_file_; }

	// NB: const ommitted for lazy loading
	Argument**& attributes() const { return attributes_; }

	unsigned set_id(boost::optional<unsigned> i = boost::none);
};

#endif
