
#include "../ifcparse/IfcSchema.h"
#include "../ifcparse/Header_section_schema.h"
#include <string>

using namespace std::string_literals;
using namespace IfcParse;

declaration* header_section_schema_types[5] = {nullptr};

const std::string strings[] = {"schema_name"s,"time_stamp_text"s,"file_description"s,"file_name"s,"file_schema"s,"description"s,"implementation_level"s,"name"s,"time_stamp"s,"author"s,"organization"s,"preprocessor_version"s,"originating_system"s,"authorisation"s,"schema_identifiers"s,"header_section_schema"s};


class header_section_schema_instance_factory : public IfcParse::instance_factory {
    virtual IfcUtil::IfcBaseClass* operator()(const IfcParse::declaration* decl, IfcEntityInstanceData&& data) const {
        switch(decl->index_in_schema()) {
            case 0: return new ::Header_section_schema::file_description(std::move(data));
            case 1: return new ::Header_section_schema::file_name(std::move(data));
            case 2: return new ::Header_section_schema::file_schema(std::move(data));
            case 3: return new ::Header_section_schema::schema_name(std::move(data));
            case 4: return new ::Header_section_schema::time_stamp_text(std::move(data));
            default: throw IfcParse::IfcException(decl->name() + " cannot be instantiated");
        }

    }
};

IfcParse::schema_definition* header_section_schema_populate_schema() {
    header_section_schema_types[3] = new type_declaration(strings[0], 3, new simple_type(simple_type::string_type));
    header_section_schema_types[4] = new type_declaration(strings[1], 4, new simple_type(simple_type::string_type));
    header_section_schema_types[0] = new entity(strings[2], false, 0, (entity*) 0);
    header_section_schema_types[1] = new entity(strings[3], false, 1, (entity*) 0);
    header_section_schema_types[2] = new entity(strings[4], false, 2, (entity*) 0);
    ((entity*)header_section_schema_types[0])->set_attributes({new attribute(strings[5], new aggregation_type(aggregation_type::list_type, 1, -1, new simple_type(simple_type::string_type)), false),new attribute(strings[6], new simple_type(simple_type::string_type), false)}, {false,false});
    ((entity*)header_section_schema_types[1])->set_attributes({new attribute(strings[7], new simple_type(simple_type::string_type), false),new attribute(strings[8], new named_type(header_section_schema_HEADER_SECTION_SCHEMA_types[4]_type), false),new attribute(strings[9], new aggregation_type(aggregation_type::list_type, 1, -1, new simple_type(simple_type::string_type)), false),new attribute(strings[10], new aggregation_type(aggregation_type::list_type, 1, -1, new simple_type(simple_type::string_type)), false),new attribute(strings[11], new simple_type(simple_type::string_type), false),new attribute(strings[12], new simple_type(simple_type::string_type), false),new attribute(strings[13], new simple_type(simple_type::string_type), false)}, {false,false,false,false,false,false,false});
    ((entity*)header_section_schema_types[2])->set_attributes({new attribute(strings[14], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(header_section_schema_HEADER_SECTION_SCHEMA_types[3]_type)), false)}, {false});
    return new schema_definition(strings[15], {header_section_schema_types[0],header_section_schema_types[1],header_section_schema_types[2],header_section_schema_types[3],header_section_schema_types[4]}, new header_section_schema_instance_factory());
}
static std::unique_ptr<schema_definition> schema;

void Header_section_schema::clear_schema() {
    schema.reset();
}

const schema_definition& Header_section_schema::get_schema() {
    if (!schema) {
        schema.reset(header_section_schema_populate_schema());
    }
    return *schema;
}

