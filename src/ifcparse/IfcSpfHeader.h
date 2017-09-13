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
 
#ifndef IFCSPFHEADER_H
#define IFCSPFHEADER_H

#include "ifc_parse_api.h"

#include "../ifcparse/IfcSpfStream.h"
#include "../ifcparse/IfcWrite.h"

namespace IfcParse {

class IFC_PARSE_API HeaderEntity : public IfcEntityInstanceData {
private:	
	const char * const _datatype;

	HeaderEntity(const HeaderEntity&); //N/A
	HeaderEntity& operator =(const HeaderEntity&); //N/A
protected:
	HeaderEntity(const char * const datatype, IfcParse::IfcFile* file);

	void setValue(unsigned int i, const std::string& s) {
		IfcWrite::IfcWriteArgument* argument = new IfcWrite::IfcWriteArgument;
		argument->set(s);
		setArgument(i, argument);
	}

	void setValue(unsigned int i, const std::vector<std::string>& s) {
		IfcWrite::IfcWriteArgument* argument = new IfcWrite::IfcWriteArgument;
		argument->set(s);
		setArgument(i, argument);
	}

public:

	std::string toString(bool upper=false) const {
		std::stringstream ss;
		// Unfortunately this is duplicated from IfcEntityInstanceData::toString()
		ss << _datatype << "(";
		std::vector<Argument*>::const_iterator it = attributes_.begin();
		for (; it != attributes_.end(); ++it) {
			if (it != attributes_.begin()) {
				ss << ",";
			}
			ss << (*it)->toString(upper);
		}
		ss << ")";
		return ss.str();
	}
};

class IFC_PARSE_API FileDescription : public HeaderEntity {
public:
	explicit FileDescription(IfcFile* = 0);

	std::vector<std::string> description() const { return *getArgument(0); }
	std::string implementation_level() const { return *getArgument(1); }

	void description(const std::vector<std::string>& value) { setValue(0, value); }
	void implementation_level(const std::string& value) { setValue(1, value); }
};

class IFC_PARSE_API FileName : public HeaderEntity  {
public:
	explicit FileName(IfcFile* = 0);

	std::string name() const { return *getArgument(0); }
	std::string time_stamp() const { return *getArgument(1); }
	std::vector<std::string> author() const { return *getArgument(2); }
	std::vector<std::string> organization() const { return *getArgument(3); }
	std::string preprocessor_version() const { return *getArgument(4); }
	std::string originating_system() const { return *getArgument(5); }
	std::string authorization() const { return *getArgument(6); }

	void name(const std::string& value) { setValue(0, value); }
	void time_stamp(const std::string& value) { setValue(1, value); }
	void author(const std::vector<std::string>& value) { setValue(2, value); }
	void organization(const std::vector<std::string>& value) { setValue(3, value); }
	void preprocessor_version(const std::string& value) { setValue(4, value); }
	void originating_system(const std::string& value) { setValue(5, value); }
	void authorization(const std::string& value) { setValue(6, value); }
};

class IFC_PARSE_API FileSchema : public HeaderEntity  {
public:
	explicit FileSchema(IfcFile* = 0);

	std::vector<std::string> schema_identifiers() const { return *getArgument(0); }

	void schema_identifiers(const std::vector<std::string>& value) { setValue(0, value); }
};

class IFC_PARSE_API IfcSpfHeader {
private:
	IfcFile* file_;
	FileDescription* _file_description;
	FileName* _file_name;
	FileSchema* _file_schema;
	void readParen();
	void readSemicolon();
	enum Trail {
		TRAILING_SEMICOLON,
		TRAILING_PAREN,
		NONE
	};
	void readTerminal(const std::string& term, Trail trail);
public:
	explicit IfcSpfHeader(IfcParse::IfcFile* file = 0)
		: file_(file), _file_description(0), _file_name(0), _file_schema(0) 
	{
		_file_description = new FileDescription(file_);
		_file_name = new FileName(file_);
		_file_schema = new FileSchema(file_);
	}

	~IfcSpfHeader()
	{
		delete _file_schema;
		delete _file_name;
		delete _file_description;
	}

	IfcParse::IfcFile* file() { return file_; }
	void file(IfcParse::IfcFile * file) { file_ = file; }

	void read();	
	bool tryRead();
	
	void write(std::ostream& os) const;

	const FileDescription& file_description() const;
	const FileName& file_name() const;
	const FileSchema& file_schema() const;

	FileDescription& file_description();
	FileName& file_name();
	FileSchema& file_schema();
};

}

#endif
