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
    IfcEntityInstanceData read_from_spf_file(IfcParse::impl::in_memory_file_storage* storage, size_t s) {
        if (storage != nullptr) {
            parse_context pc;
            storage->tokens->Next();
            storage->load(-1, nullptr, pc, -1);
            return pc.construct(-1, *storage->references_to_resolve, nullptr, s, -1);
        } else {
            // std::unreachable();
            return IfcEntityInstanceData(in_memory_attribute_storage(10));
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
    : file_(file),
    file_description_(nullptr),
    file_name_(nullptr),
    file_schema_(nullptr)
{
    Header_section_schema::get_schema();

    if (file == nullptr) {
        // overwritten later in IfcFile::setDefaultHeaderValues() when we know the schema identifier
        file_description_ = new Header_section_schema::file_description({}, "");
        file_description_->file_ = file_;
        file_name_ = new Header_section_schema::file_name("", "", {}, {}, "", "", "");
        file_name_->file_ = file_;
        file_schema_ = new Header_section_schema::file_schema({});
        file_schema_->file_ = file_;
    } else {
        storage_ = std::visit([this](auto& m) -> decltype(storage_) {
            if constexpr (std::is_same_v<std::decay_t<decltype(m)>, impl::in_memory_file_storage>) {
                return &m;
            }
            return nullptr;
        }, file_->storage_);

        if (storage_ == nullptr) {
            file_description_ = Header_section_schema::get_schema().instantiate(&Header_section_schema::file_description::Class(), IfcEntityInstanceData(rocks_db_attribute_storage{}))->as<Header_section_schema::file_description>();
            file_description_->file_ = file_;
            file_name_ = Header_section_schema::get_schema().instantiate(&Header_section_schema::file_name::Class(), IfcEntityInstanceData(rocks_db_attribute_storage{}))->as<Header_section_schema::file_name>();
            file_name_->file_ = file_;
            file_schema_ = Header_section_schema::get_schema().instantiate(&Header_section_schema::file_schema::Class(), IfcEntityInstanceData(rocks_db_attribute_storage{}))->as<Header_section_schema::file_schema>();
            file_schema_->file_ = file_;
        }
    }
}

IfcParse::IfcSpfHeader::IfcSpfHeader(IfcParse::IfcSpfLexer* lexer)
{
    Header_section_schema::get_schema();

	storage_ = new impl::in_memory_file_storage;
	storage_->tokens = lexer;
    file_ = nullptr;

    // overwritten later in IfcFile::setDefaultHeaderValues() when we know the schema identifier
    file_description_ = new Header_section_schema::file_description({}, "");
    file_description_->file_ = file_;
    file_name_ = new Header_section_schema::file_name("", "", {}, {}, "", "", "");
    file_name_->file_ = file_;
    file_schema_ = new Header_section_schema::file_schema({});
    file_schema_->file_ = file_;
}

IfcParse::IfcSpfHeader::~IfcSpfHeader() {
    delete file_schema_;
    delete file_name_;
    delete file_description_;
}

void IfcParse::IfcSpfHeader::file(IfcParse::IfcFile* file)
{
    this->file_ = file;
    if (file != nullptr) {
        storage_ = std::visit([this](auto& m) -> decltype(storage_) {
            if constexpr (std::is_same_v<std::decay_t<decltype(m)>, impl::in_memory_file_storage>) {
                return &m;
            }
            return nullptr;
        }, file_->storage_);
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

    readTerminal(Header_section_schema::file_description::Class().name_uc(), NONE);
    delete file_description_;
    file_description_ = new Header_section_schema::file_description(read_from_spf_file(storage_, Header_section_schema::file_description::Class().attribute_count()));
    file_description_->file_ = file_;
    readSemicolon();

    readTerminal(Header_section_schema::file_name::Class().name_uc(), NONE);
    delete file_name_;
    file_name_ = new Header_section_schema::file_name(read_from_spf_file(storage_, Header_section_schema::file_name::Class().attribute_count()));
    file_name_->file_ = file_;
    readSemicolon();

    readTerminal(Header_section_schema::file_schema::Class().name_uc(), NONE);
    delete file_schema_;
    file_schema_ = new Header_section_schema::file_schema(read_from_spf_file(storage_, Header_section_schema::file_schema::Class().attribute_count()));
    file_schema_->file_ = file_;
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
    file_description()->toString(out, true);
    out << ";"
        << "\n";
    file_name()->toString(out, true);
    out << ";"
        << "\n";
    file_schema()->toString(out, true);
    out << ";"
        << "\n";
    out << ENDSEC << ";"
        << "\n";
    out << DATA << ";"
        << "\n";
}

const Header_section_schema::file_description* IfcParse::IfcSpfHeader::file_description() const { 
    if (file_description_ == nullptr) {
        std::visit([this](auto& m) {
            if constexpr (std::is_same_v<std::decay_t<decltype(m)>, impl::rocks_db_file_storage>) {
                file_description_ = new Header_section_schema::file_description(rocks_db_attribute_storage{});
            } else if constexpr (std::is_same_v<std::decay_t<decltype(m)>, impl::in_memory_file_storage>) {
                file_description_ = new Header_section_schema::file_description(in_memory_attribute_storage(Header_section_schema::file_description::Class().attribute_count()));
            }
        }, file_->storage_);
        file_description_->file_ = file_;
    }
    return file_description_; 
}

const Header_section_schema::file_name* IfcParse::IfcSpfHeader::file_name() const {
    if (file_name_ == nullptr) {
        std::visit([this](auto& m) {
            if constexpr (std::is_same_v<std::decay_t<decltype(m)>, impl::rocks_db_file_storage>) {
                file_name_ = new Header_section_schema::file_name(rocks_db_attribute_storage{});
            } else if constexpr (std::is_same_v<std::decay_t<decltype(m)>, impl::in_memory_file_storage>) {
                file_name_ = new Header_section_schema::file_name(in_memory_attribute_storage(Header_section_schema::file_name::Class().attribute_count()));
            }
        }, file_->storage_);
        file_name_->file_ = file_;
    }

    return file_name_; 
}

const Header_section_schema::file_schema* IfcParse::IfcSpfHeader::file_schema() const {
    if (file_schema_ == nullptr) {
        std::visit([this](auto& m) {
            if constexpr (std::is_same_v<std::decay_t<decltype(m)>, impl::rocks_db_file_storage>) {
                file_schema_ = new Header_section_schema::file_schema(rocks_db_attribute_storage{});
            } else if constexpr (std::is_same_v<std::decay_t<decltype(m)>, impl::in_memory_file_storage>) {
                file_schema_ = new Header_section_schema::file_schema(in_memory_attribute_storage(Header_section_schema::file_schema::Class().attribute_count()));
            }
        }, file_->storage_);
        file_schema_->file_ = file_;
    }

    return file_schema_; 
}

Header_section_schema::file_description* IfcParse::IfcSpfHeader::file_description() {
    if (file_description_ == nullptr) {
        std::visit([this](auto& m) {
            if constexpr (std::is_same_v<std::decay_t<decltype(m)>, impl::rocks_db_file_storage>) {
                file_description_ = new Header_section_schema::file_description(rocks_db_attribute_storage{});
            } else if constexpr (std::is_same_v<std::decay_t<decltype(m)>, impl::in_memory_file_storage>) {
                file_description_ = new Header_section_schema::file_description(in_memory_attribute_storage(Header_section_schema::file_description::Class().attribute_count()));
            }
        }, file_->storage_);
        file_description_->file_ = file_;
    }

    return file_description_; 
}

Header_section_schema::file_name* IfcParse::IfcSpfHeader::file_name() {
    if (file_name_ == nullptr) {
        std::visit([this](auto& m) {
            if constexpr (std::is_same_v<std::decay_t<decltype(m)>, impl::rocks_db_file_storage>) {
                file_name_ = new Header_section_schema::file_name(rocks_db_attribute_storage{});
            } else if constexpr (std::is_same_v<std::decay_t<decltype(m)>, impl::in_memory_file_storage>) {
                file_name_ = new Header_section_schema::file_name(in_memory_attribute_storage(Header_section_schema::file_name::Class().attribute_count()));
            }
        }, file_->storage_);
        file_name_->file_ = file_;
    }

    return file_name_; 
}

Header_section_schema::file_schema* IfcParse::IfcSpfHeader::file_schema() {
    if (file_schema_ == nullptr) {
        std::visit([this](auto& m) {
            if constexpr (std::is_same_v<std::decay_t<decltype(m)>, impl::rocks_db_file_storage>) {
                file_schema_ = new Header_section_schema::file_schema(rocks_db_attribute_storage{});
            } else if constexpr (std::is_same_v<std::decay_t<decltype(m)>, impl::in_memory_file_storage>) {
                file_schema_ = new Header_section_schema::file_schema(in_memory_attribute_storage(Header_section_schema::file_schema::Class().attribute_count()));
            }
        }, file_->storage_);
        file_schema_->file_ = file_;
    }

    return file_schema_; 
}
