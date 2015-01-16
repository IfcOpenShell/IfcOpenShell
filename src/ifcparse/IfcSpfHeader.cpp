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

#include "../ifcparse/IfcParse.h"

#include "IfcSpfHeader.h"

static const char * const ISO_10303_21		= "ISO-10303-21";
static const char * const HEADER			= "HEADER";
static const char * const FILE_DESCRIPTION	= "FILE_DESCRIPTION";
static const char * const FILE_NAME			= "FILE_NAME";
static const char * const FILE_SCHEMA		= "FILE_SCHEMA";
static const char * const FILE_POPULATION	= "FILE_POPULATION";
static const char * const SECTION_LANGUAGE	= "SECTION_LANGUAGE";
static const char * const SECTION_CONTEXT	= "SECTION_CONTEXT";
static const char * const ENDSEC			= "ENDSEC";
static const char * const DATA				= "DATA";

using namespace IfcParse;

void IfcSpfHeader::readSemicolon() {
	if (!TokenFunc::isOperator(_lexer->Next(), ';')) {
		throw IfcException(std::string("Expected ;"));
	}
}

void IfcSpfHeader::readParen() {
	if (!TokenFunc::isOperator(_lexer->Next(), '(')) {
		throw IfcException(std::string("Expected ("));
	}
}

void IfcSpfHeader::readTerminal(const std::string& term, Trail trail) {
	if (TokenFunc::asString(_lexer->Next()) != term) {
		throw IfcException(std::string("Expected " + term));
	}
	if (trail == TRAILING_SEMICOLON) {
		readSemicolon();
	} else if (trail == TRAILING_PAREN) {
		readParen();
	}
}

void IfcSpfHeader::read() {
	readTerminal(ISO_10303_21, TRAILING_SEMICOLON);
	readTerminal(HEADER, TRAILING_SEMICOLON);

	readTerminal(FILE_DESCRIPTION, TRAILING_PAREN);
	delete _file_description;
	_file_description = new FileDescription(_lexer);
	readSemicolon();

	readTerminal(FILE_NAME, TRAILING_PAREN);
	delete _file_name;
	_file_name = new FileName(_lexer);
	readSemicolon();

	readTerminal(FILE_SCHEMA, TRAILING_PAREN);
	delete _file_schema;
	_file_schema = new FileSchema(_lexer);
	readSemicolon();
}

bool IfcSpfHeader::tryRead() {
	try {
		read();
		return true;
	} catch(const IfcException&) { 
		return false;
	}		
}

void IfcSpfHeader::write(std::ostream& os) const {
	os << ISO_10303_21 << ";" << "\n";
	os << HEADER << ";" << "\n";
	os << file_description().toString(true) << "\n";
	os << file_name().toString(true) << "\n";
	os << file_schema().toString(true) << "\n";
	os << ENDSEC << ";" << "\n";
	os << DATA << ";" << "\n";
}


const FileDescription& IfcSpfHeader::file_description() const {
	if (_file_description) {
		return *_file_description; 
	} else {
		throw IfcException("File description not set");
	}
}

const FileName& IfcSpfHeader::file_name() const {
	if (_file_name) {
		return *_file_name; 
	} else {
		throw IfcException("File name not set");
	}
}

const FileSchema& IfcSpfHeader::file_schema() const {
	if (_file_schema) {
		return *_file_schema; 
	} else {
		throw IfcException("File schema not set");
	}
}

FileDescription& IfcSpfHeader::file_description() {
	if (_file_description) {
		return *_file_description; 
	} else {
		throw IfcException("File description not set");
	}
}

FileName& IfcSpfHeader::file_name() {
	if (_file_name) {
		return *_file_name; 
	} else {
		throw IfcException("File name not set");
	}
}

FileSchema& IfcSpfHeader::file_schema() {
	if (_file_schema) {
		return *_file_schema; 
	} else {
		throw IfcException("File schema not set");
	}
}

FileDescription::FileDescription(IfcSpfLexer* lexer) : HeaderEntity(FILE_DESCRIPTION, lexer) {}
FileName::FileName(IfcSpfLexer* lexer) : HeaderEntity(FILE_NAME, lexer) {}
FileSchema::FileSchema(IfcSpfLexer* lexer) : HeaderEntity(FILE_SCHEMA, lexer) {}