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
static const char* const ENDSEC = "ENDSEC";
static const char* const DATA = "DATA";

using namespace IfcParse;

namespace {
    std::shared_ptr<InstanceData> read_from_spf_file(IfcParse::IfcFile* file, IfcParse::impl::in_memory_file_storage* storage, const IfcParse::entity* decl) {
        if (storage != nullptr) {
            parse_context pc;
            storage->tokens->Next();
            storage->load(-1, nullptr, pc, -1);
            return pc.construct(file, std::nullopt, *storage->references_to_resolve, decl, decl->as_entity()->attribute_count(), -1);
        } else {
            // std::unreachable();
            return nullptr;
        }
    }
} // namespace

void IfcSpfHeader::readSemicolon() {
    if (storage_ != nullptr) {
        if (!TokenFunc::isOperator(storage_->tokens->Next(), ';')) {
            throw IfcException(std::string("Expected ;"));
        }
    } else {
        // std::unreachable();
    }
}

void IfcSpfHeader::readTerminal(const std::string& term, Trail trail) {
    if (storage_ != nullptr) {
        if (TokenFunc::asStringRef(storage_->tokens->Next()) != term) {
            throw IfcException(std::string("Expected " + term));
        }
        if (trail == TRAILING_SEMICOLON) {
            readSemicolon();
        }
    } else {
        // std::unreachable();
    }
}

IfcParse::IfcSpfHeader::IfcSpfHeader(IfcParse::IfcFile* file)
    : file_(file)
{
    Header_section_schema::get_schema();

    // @todo This might still not work in IfcFile's uninitialized mode
     storage_ = std::visit([this](auto& m) -> decltype(storage_) {
        if constexpr (std::is_same_v<std::decay_t<decltype(m)>, impl::in_memory_file_storage>) {
            return &m;
        }
        return nullptr;
    }, file->storage_);
         
    const bool in_memory = storage_ != nullptr;

    if (in_memory) {
        header_entities_[0] = std::make_shared<InstanceData>(file, &Header_section_schema::file_description::Class(), 0, in_memory_attribute_storage(Header_section_schema::file_description::Class().attribute_count()));
        header_entities_[1] = std::make_shared<InstanceData>(file, &Header_section_schema::file_name::Class(), 0, in_memory_attribute_storage(Header_section_schema::file_name::Class().attribute_count()));
        header_entities_[2] = std::make_shared<InstanceData>(file, &Header_section_schema::file_schema::Class(), 0, in_memory_attribute_storage(Header_section_schema::file_schema::Class().attribute_count()));
    } else {
        header_entities_[0] = std::make_shared<InstanceData>(file, &Header_section_schema::file_description::Class(), 0, rocks_db_attribute_storage{});
        header_entities_[1] = std::make_shared<InstanceData>(file, &Header_section_schema::file_name::Class(), 0, rocks_db_attribute_storage{});
        header_entities_[2] = std::make_shared<InstanceData>(file, &Header_section_schema::file_schema::Class(), 0, rocks_db_attribute_storage{});
    }
}

IfcParse::IfcSpfHeader::IfcSpfHeader(IfcParse::IfcSpfLexer* lexer)
{
    Header_section_schema::get_schema();

	storage_ = new impl::in_memory_file_storage;
	storage_->tokens = lexer;
    file_ = nullptr;
}

IfcParse::IfcSpfHeader::~IfcSpfHeader() {
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

    readTerminal(Header_section_schema::file_description::Class().name_uc(), NONE);
    header_entities_[0] = read_from_spf_file(file_, storage_, &Header_section_schema::file_description::Class());
    readSemicolon();

    readTerminal(Header_section_schema::file_name::Class().name_uc(), NONE);
    header_entities_[1] = read_from_spf_file(file_, storage_, &Header_section_schema::file_name::Class());
    readSemicolon();

    readTerminal(Header_section_schema::file_schema::Class().name_uc(), NONE);
    header_entities_[2] = read_from_spf_file(file_, storage_, &Header_section_schema::file_schema::Class());
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
    file_description().toString(out, true);
    out << ";"
        << "\n";
    file_name().toString(out, true);
    out << ";"
        << "\n";
    file_schema().toString(out, true);
    out << ";"
        << "\n";
    out << ENDSEC << ";"
        << "\n";
    out << DATA << ";"
        << "\n";
}

void IfcParse::IfcSpfHeader::file(IfcParse::IfcFile* file) {
    file_ = file;
    if (file != nullptr) {
        storage_ = std::visit([this](auto& m) -> decltype(storage_) {
            if constexpr (std::is_same_v<std::decay_t<decltype(m)>, impl::in_memory_file_storage>) {
                return &m;
            }
            return nullptr;
        },
        file_->storage_);
    }
}

const Header_section_schema::file_description IfcParse::IfcSpfHeader::file_description() const { 
    return Header_section_schema::file_description(header_entities_[0]);
}

const Header_section_schema::file_name IfcParse::IfcSpfHeader::file_name() const {
    return Header_section_schema::file_name(header_entities_[1]);
}

const Header_section_schema::file_schema IfcParse::IfcSpfHeader::file_schema() const {
    return Header_section_schema::file_schema(header_entities_[2]);
}

Header_section_schema::file_description IfcParse::IfcSpfHeader::file_description() {
    return Header_section_schema::file_description(header_entities_[0]);
}

Header_section_schema::file_name IfcParse::IfcSpfHeader::file_name() {
    return Header_section_schema::file_name(header_entities_[1]);
}

Header_section_schema::file_schema IfcParse::IfcSpfHeader::file_schema() {
    return Header_section_schema::file_schema(header_entities_[2]);
}
