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

#include "IfcSpfHeader.h"

#include "IfcFile.h"
#include "IfcLogger.h"

static const char* const ISO_10303_21 = "ISO-10303-21";
static const char* const HEADER = "HEADER";
static const char* const FILE_DESCRIPTION = "FILE_DESCRIPTION";
static const char* const FILE_NAME = "FILE_NAME";
static const char* const FILE_SCHEMA = "FILE_SCHEMA";
static const char* const ENDSEC = "ENDSEC";
static const char* const DATA = "DATA";
// The following header entities are not normally encountered in IFC files and are not parsed.
// static const char * const FILE_POPULATION   = "FILE_POPULATION";
// static const char * const SECTION_LANGUAGE  = "SECTION_LANGUAGE";
// static const char * const SECTION_CONTEXT   = "SECTION_CONTEXT";

using namespace IfcParse;

namespace {
    IfcEntityInstanceData read_from_file(IfcFile* f, size_t s) {
        parse_context pc;
        f->tokens->Next();
        f->load(-1, nullptr, pc, -1);
        return pc.construct(-1, f->references_to_resolve, nullptr, s);
    }
}

HeaderEntity::HeaderEntity(const char* const datatype, size_t size, IfcFile* file)
    : datatype_(datatype)
    , file_(file)
    , data_(file ? read_from_file(file, size) : IfcEntityInstanceData(storage_t(size)))
{}

HeaderEntity::~HeaderEntity() {
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
    delete file_description_;
    // readParen();
    file_description_ = new FileDescription(file_);
    readSemicolon();

    readTerminal(FILE_NAME, NONE);
    delete file_name_;
    // readParen();
    file_name_ = new FileName(file_);
    readSemicolon();

    readTerminal(FILE_SCHEMA, NONE);
    delete file_schema_;
    // readParen();
    file_schema_ = new FileSchema(file_);
    readSemicolon();
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

void IfcSpfHeader::write(std::ostream& out) const {
    out << ISO_10303_21 << ";"
        << "\n";
    out << HEADER << ";"
        << "\n";
    out << file_description().toString(true) << ";"
        << "\n";
    out << file_name().toString(true) << ";"
        << "\n";
    out << file_schema().toString(true) << ";"
        << "\n";
    out << ENDSEC << ";"
        << "\n";
    out << DATA << ";"
        << "\n";
}

const FileDescription& IfcSpfHeader::file_description() const {
    if (file_description_ == nullptr) {
        throw IfcException("File description not set");
    }
    return *file_description_;
}

const FileName& IfcSpfHeader::file_name() const {
    if (file_name_ == nullptr) {
        throw IfcException("File name not set");
    }
    return *file_name_;
}

const FileSchema& IfcSpfHeader::file_schema() const {
    if (file_schema_ == nullptr) {
        throw IfcException("File schema not set");
    }
    return *file_schema_;
}

FileDescription& IfcSpfHeader::file_description() {
    if (file_description_ == nullptr) {
        throw IfcException("File description not set");
    }
    return *file_description_;
}

FileName& IfcSpfHeader::file_name() {
    if (file_name_ == nullptr) {
        throw IfcException("File name not set");
    }
    return *file_name_;
}

FileSchema& IfcSpfHeader::file_schema() {
    if (file_schema_ == nullptr) {
        throw IfcException("File schema not set");
    }
    return *file_schema_;
}

FileDescription::FileDescription(IfcFile* file) : HeaderEntity(FILE_DESCRIPTION, 2, file) {}
FileName::FileName(IfcFile* file) : HeaderEntity(FILE_NAME, 7, file) {}
FileSchema::FileSchema(IfcFile* file) : HeaderEntity(FILE_SCHEMA, 1, file) {}
