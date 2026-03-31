#include "spf_header.h"

#include "file.h"

static const char* const ISO_10303_21 = "ISO-10303-21";
static const char* const HEADER = "HEADER";
static const char* const ENDSEC = "ENDSEC";
static const char* const DATA = "DATA";

using namespace ifcopenshell;

namespace {

std::shared_ptr<instance_data> make_header_entity(ifcopenshell::file* file, const ifcopenshell::entity& decl) {
    const bool in_memory = file == nullptr || std::visit([](auto& storage) {
        return std::is_same_v<std::decay_t<decltype(storage)>, ifcopenshell::impl::in_memory_file_storage>;
    }, file->storage_);

    if (in_memory) {
        return std::make_shared<instance_data>(file, &decl, 0, in_memory_attribute_storage(decl.attribute_count()));
    }

    return std::make_shared<instance_data>(file, &decl, 0, rocks_db_attribute_storage{});
}

} // namespace

ifcopenshell::spf_header::spf_header(ifcopenshell::file* file)
    : file_(file) {
    Header_section_schema::get_schema();

    header_entities_[0] = make_header_entity(file_, Header_section_schema::file_description::Class());
    header_entities_[1] = make_header_entity(file_, Header_section_schema::file_name::Class());
    header_entities_[2] = make_header_entity(file_, Header_section_schema::file_schema::Class());
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

void ifcopenshell::spf_header::file(ifcopenshell::file* file) {
    file_ = file;
}

void ifcopenshell::spf_header::set_file_description(const std::shared_ptr<instance_data>& data) {
    header_entities_[0] = data;
}

void ifcopenshell::spf_header::set_file_name(const std::shared_ptr<instance_data>& data) {
    header_entities_[1] = data;
}

void ifcopenshell::spf_header::set_file_schema(const std::shared_ptr<instance_data>& data) {
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
