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

namespace IfcParse {

class HeaderEntity {
private:	
	ArgumentList* list;
protected:
	HeaderEntity(IfcSpfLexer* lexer) {
		std::vector<unsigned int> ids;
		list = new ArgumentList(lexer, ids);
	};
	Argument* getArgument(unsigned int i) const {
		return (*list)[i];
	}
};

class FileDescription : private HeaderEntity {
public:
	FileDescription(IfcSpfLexer* lexer) : HeaderEntity(lexer) {}
	std::vector<std::string> description() const { return *getArgument(0); }
	std::string implementation_level() const { return *getArgument(1); }
};

class FileName : private HeaderEntity  {
public:
	FileName(IfcSpfLexer* lexer) : HeaderEntity(lexer) {}
	std::string name() const { return *getArgument(0); }
	std::string time_stamp() const { return *getArgument(1); }
	std::vector<std::string> author() const { return *getArgument(2); }
	std::vector<std::string> organization() const { return *getArgument(3); }
	std::string preprocessor_version() const { return *getArgument(4); }
	std::string originating_system() const { return *getArgument(5); }
	std::string authorization()const  { return *getArgument(6); }
};

class FileSchema : private HeaderEntity  {
public:
	FileSchema(IfcSpfLexer* lexer) : HeaderEntity(lexer) {}
	std::vector<std::string> schema_identifiers() const { return *getArgument(0); }
};

class IfcSpfHeader {
private:
	IfcSpfLexer* _lexer;
	FileDescription* _file_description;
	FileName* _file_name;
	FileSchema* _file_schema;
	void readParen();
	void readSemicolon();\
	enum Trail {
		TRAILING_SEMICOLON,
		TRAILING_PAREN,
		NONE
	};
	void readTerminal(const std::string& term, Trail trail);
public:
	IfcSpfHeader() : _lexer(0), _file_description(0), _file_name(0), _file_schema(0) {}
	explicit IfcSpfHeader(IfcSpfLexer* lexer) : _lexer(lexer) {}
	
	IfcSpfLexer* lexer() { return _lexer; }
	void lexer(IfcSpfLexer* l) { _lexer = l; }
	
	void read();	
	bool tryRead();

	const FileDescription& file_description();
	const FileName& file_name();
	const FileSchema& file_schema();
};

}

#endif