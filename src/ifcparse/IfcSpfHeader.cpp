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

#include "../ifcparse/IfcFile.h"

#include "IfcSpfHeader.h"

static const char * const ISO_10303_21		= "ISO-10303-21";
static const char * const HEADER			= "HEADER";
static const char * const FILE_DESCRIPTION	= "FILE_DESCRIPTION";
static const char * const FILE_NAME			= "FILE_NAME";
static const char * const FILE_SCHEMA		= "FILE_SCHEMA";
static const char * const ENDSEC			= "ENDSEC";
static const char * const DATA				= "DATA";
// The following header entities are not normally encountered in IFC files and are not parsed.
// static const char * const FILE_POPULATION   = "FILE_POPULATION";
// static const char * const SECTION_LANGUAGE  = "SECTION_LANGUAGE";
// static const char * const SECTION_CONTEXT   = "SECTION_CONTEXT";

using namespace IfcParse;

HeaderEntity::HeaderEntity(const char * const datatype, IfcFile* file)
	: IfcEntityInstanceData(IfcSchema::Type::UNDEFINED, file), _datatype(datatype)
{
	if (file) {
		offset_in_file_ = file->stream->Tell();
		load();
	} else {
		initialized_ = true;
	}
}


void IfcSpfHeader::readSemicolon() {
	if (!TokenFunc::isOperator(file_->tokens->Next(), ';')) {
		throw IfcException(std::string("Expected ;"));
	}
}

void IfcSpfHeader::readParen() {
	if (!TokenFunc::isOperator(file_->tokens->Next(), '(')) {
		throw IfcException(std::string("Expected ("));
	}
}

void IfcSpfHeader::readTerminal(const std::string& term, Trail trail) {
	if (TokenFunc::asStringRef(file_->tokens->Next()) != term) {
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

	// | The header section of every exchange structure shall contain one 
	// | instance of each of the following entities: file_description, file_name, 
	// | and file_schema, and they shall appear in that order. Instances of 
	// | file_population, section_language and section_context may appear after 
	// | file_schema. If instances of user-defined header section entities are 
	// | present, they shall appear after the header section entity instances 
	// | defined in this section.
	// 
	// ISO 10303-21 Second edition 2002-01-15 p. 16

	readTerminal(FILE_DESCRIPTION, NONE);
	delete _file_description;
	_file_description = new FileDescription(file_);
	// readSemicolon();

	readTerminal(FILE_NAME, NONE);
	delete _file_name;
	_file_name = new FileName(file_);
	// readSemicolon();

	readTerminal(FILE_SCHEMA, NONE);
	delete _file_schema;
	_file_schema = new FileSchema(file_);
	// readSemicolon();
}

bool IfcSpfHeader::tryRead() {
	try {
		read();
		return true;
	} catch (const std::exception& e) {
		Logger::Error(e);
		return false;
	}
}

void IfcSpfHeader::write(std::ostream& os) const {
	os << ISO_10303_21 << ";" << "\n";
	os << HEADER << ";" << "\n";
	os << file_description().toString(true) << ";" << "\n";
	os << file_name().toString(true) << ";" << "\n";
	os << file_schema().toString(true) << ";" << "\n";
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

FileDescription::FileDescription(IfcFile* file) : HeaderEntity(FILE_DESCRIPTION, file) {}
FileName::FileName(IfcFile* file) : HeaderEntity(FILE_NAME, file) {}
FileSchema::FileSchema(IfcFile* file) : HeaderEntity(FILE_SCHEMA, file) {}