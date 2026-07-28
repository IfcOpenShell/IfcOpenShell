#include "spf_header.h"

#include "file.h"
#include "logger.h"

static const char* const ISO_10303_21 = "ISO-10303-21";
static const char* const HEADER = "HEADER";
static const char* const ENDSEC = "ENDSEC";
static const char* const DATA = "DATA";

using namespace ifcopenshell;

namespace {

shared_pointer_type make_header_entity(ifcopenshell::file* file, const ifcopenshell::entity& decl, ::logger& logger) {
    static_cast<void>(logger);
    const bool in_memory = file == nullptr || std::visit([](auto& storage) {
        return std::is_same_v<std::decay_t<decltype(storage)>, ifcopenshell::impl::in_memory_file_storage>;
    }, file->storage_);

    if (in_memory) {
        return ifcopenshell::make_pointer_type<instance_data>(file, &decl, 0, in_memory_attribute_storage(decl.attribute_count()));
    }

    return ifcopenshell::make_pointer_type<instance_data>(file, &decl, 0, rocks_db_attribute_storage{});
}

} // namespace

ifcopenshell::spf_header::spf_header(ifcopenshell::file* file, ::logger* logger)
    : file_(file)
    , logger_(logger_or_root(logger)) {
    Header_section_schema::get_schema();

    header_entities_[0] = make_header_entity(file_, Header_section_schema::file_description::Class(), logger_);
    header_entities_[1] = make_header_entity(file_, Header_section_schema::file_name::Class(), logger_);
    header_entities_[2] = make_header_entity(file_, Header_section_schema::file_schema::Class(), logger_);
}

ifcopenshell::spf_header::~spf_header() = default;

void spf_header::write(std::ostream& out) const {
    out << ISO_10303_21 << ";"
        << "\n";
    out << HEADER << ";"
        << "\n";
    file_description().to_string(out, true);
    out << ";"
        << "\n";
    file_name().to_string(out, true);
    out << ";"
        << "\n";
    file_schema().to_string(out, true);
    out << ";"
        << "\n";
    out << ENDSEC << ";"
        << "\n";
    out << DATA << ";"
        << "\n";
}

void ifcopenshell::spf_header::owner_file(ifcopenshell::file* file) {
    file_ = file;
}

void ifcopenshell::spf_header::set_file_description(const shared_pointer_type& data) {
    header_entities_[0] = data;
}

void ifcopenshell::spf_header::set_file_name(const shared_pointer_type& data) {
    header_entities_[1] = data;
}

void ifcopenshell::spf_header::set_file_schema(const shared_pointer_type& data) {
    header_entities_[2] = data;
}

const Header_section_schema::file_description ifcopenshell::spf_header::file_description() const {
    return Header_section_schema::file_description(header_entities_[0]);
}

const Header_section_schema::file_name ifcopenshell::spf_header::file_name() const {
    return Header_section_schema::file_name(header_entities_[1]);
}

const Header_section_schema::file_schema ifcopenshell::spf_header::file_schema() const {
    return Header_section_schema::file_schema(header_entities_[2]);
}

Header_section_schema::file_description ifcopenshell::spf_header::file_description() {
    return Header_section_schema::file_description(header_entities_[0]);
}

Header_section_schema::file_name ifcopenshell::spf_header::file_name() {
    return Header_section_schema::file_name(header_entities_[1]);
}

Header_section_schema::file_schema ifcopenshell::spf_header::file_schema() {
    return Header_section_schema::file_schema(header_entities_[2]);
}

void ifcopenshell::spf_header::assign(const spf_header& other) {
    if (this != &other) {
        auto copy_inst = [](express::Entity& new_entity, const express::Entity& entity) {
            for (size_t i = 0; i < entity.declaration().as_entity()->attribute_count(); ++i) {
                entity.get_attribute_value(i).apply_visitor([i, &entity, &new_entity](const auto& v) {
                    using U = std::decay_t<decltype(v)>;
                    if constexpr (std::is_same_v<U, express::Base>) {
                    } else if constexpr (std::is_same_v<U, std::vector<express::Base>>) {
                    } else if constexpr (std::is_same_v<U, std::vector<std::vector<express::Base>>>) {
                    } else {
                        new_entity.set_attribute_value(i, v);
                    }
                });
            }
        };

        for (size_t i = 0; i < header_entities_.size(); ++i) {
            express::Entity tmp(header_entities_[i]);
            copy_inst(tmp, express::Entity(other.header_entities_[i]));
        }
    }
}
