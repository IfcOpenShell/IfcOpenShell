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

#include "../ifcparse/IfcSpfStream.h"
#include "../ifcparse/IfcWrite.h"

namespace IfcParse {

class HeaderEntity : public IfcAbstractEntity {
private:	
	ArgumentList* _list;
	const char * const _datatype;
protected:
	HeaderEntity(const char * const datatype, IfcSpfLexer* lexer) 
		: _datatype(datatype), _list(0)
	{
		std::vector<unsigned int> ids;
		_list = new ArgumentList();
		if (lexer) {
			_list->read(lexer, ids);
		}
	}

	~HeaderEntity() {
		delete _list;
	}

	void setArgument(unsigned int i, const std::string& s) {
		IfcWrite::IfcWriteArgument* argument = new IfcWrite::IfcWriteArgument(this);
		argument->set(s);
		_list->set(i, argument);
	}

	void setArgument(unsigned int i, const std::vector<std::string>& s) {
		IfcWrite::IfcWriteArgument* argument = new IfcWrite::IfcWriteArgument(this);
		argument->set(s);
		_list->set(i, argument);
	}

public:
	Argument* getArgument(unsigned int i) const {
		return (*_list)[i];
	}

	Argument* getArgument(unsigned int i) {
		return (*_list)[i];
	}

	IfcEntityList::ptr getInverse(IfcSchema::Type::Enum type, int attribute_index) {
		return IfcEntityList::ptr(new IfcEntityList);
	}

	std::string datatype() const {
		return _datatype;
	}
	
	unsigned int getArgumentCount() const {
		return _list->size();
	}

	IfcSchema::Type::Enum type() const {
		return (IfcSchema::Type::Enum) -1;
	}

	bool is(IfcSchema::Type::Enum v) const {
		return false;
	}

	std::string toString(bool upper=false) const {
		std::stringstream ss;
		ss << _datatype << _list->toString(upper) << ";";
		return ss.str();
	}
	
	unsigned int id() {
		return 0;
	}

	IfcWrite::IfcWritableEntity* isWritable() {
		return 0;
	}
};

class FileDescription : public HeaderEntity {
public:
	explicit FileDescription(IfcSpfLexer* = 0);

	std::vector<std::string> description() const { return *getArgument(0); }
	std::string implementation_level() const { return *getArgument(1); }

	void description(const std::vector<std::string>& value) { setArgument(0, value); }
	void implementation_level(const std::string& value) { setArgument(1, value); }
};

class FileName : public HeaderEntity  {
public:
	explicit FileName(IfcSpfLexer* = 0);

	std::string name() const { return *getArgument(0); }
	std::string time_stamp() const { return *getArgument(1); }
	std::vector<std::string> author() const { return *getArgument(2); }
	std::vector<std::string> organization() const { return *getArgument(3); }
	std::string preprocessor_version() const { return *getArgument(4); }
	std::string originating_system() const { return *getArgument(5); }
	std::string authorization() const { return *getArgument(6); }

	void name(const std::string& value) { setArgument(0, value); }
	void time_stamp(const std::string& value) { setArgument(1, value); }
	void author(const std::vector<std::string>& value) { setArgument(2, value); }
	void organization(const std::vector<std::string>& value) { setArgument(3, value); }
	void preprocessor_version(const std::string& value) { setArgument(4, value); }
	void originating_system(const std::string& value) { setArgument(5, value); }
	void authorization(const std::string& value) { setArgument(6, value); }
};

class FileSchema : public HeaderEntity  {
public:
	explicit FileSchema(IfcSpfLexer* = 0);

	std::vector<std::string> schema_identifiers() const { return *getArgument(0); }

	void schema_identifiers(const std::vector<std::string>& value) { setArgument(0, value); }
};

class IfcSpfHeader {
private:
	IfcSpfLexer* _lexer;
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
	explicit IfcSpfHeader(IfcSpfLexer* lexer = 0)
		: _lexer(lexer), _file_description(0), _file_name(0), _file_schema(0) 
	{
		_file_description = new FileDescription();
		_file_name = new FileName();
		_file_schema = new FileSchema();
	}
	
	IfcSpfLexer* lexer() { return _lexer; }
	void lexer(IfcSpfLexer* l) { _lexer = l; }

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