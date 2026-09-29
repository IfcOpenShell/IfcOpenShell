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

/********************************************************************************
 *                                                                              *
 * This file has been generated from header_schema.exp. Do not make modifications*
 * but instead modify the python script that has been used to generate this.    *
 *                                                                              *
 ********************************************************************************/

#include "../../ifcparse/schema.h"
#include "../../ifcparse/schemas/Header_section_schema.h"
#include <string>

using namespace std::string_literals;
using namespace ifcopenshell;

declaration* HEADER_SECTION_SCHEMA_types[5] = {nullptr};
ifcopenshell::schema_definition* HEADER_SECTION_SCHEMA_populate_schema() {

const std::string strings[] = {"schema_name"s,"time_stamp_text"s,"file_description"s,"file_name"s,"file_schema"s,"description"s,"implementation_level"s,"name"s,"time_stamp"s,"author"s,"organization"s,"preprocessor_version"s,"originating_system"s,"authorization"s,"schema_identifiers"s,"HEADER_SECTION_SCHEMA"s};

    HEADER_SECTION_SCHEMA_types[3] = new type_declaration(strings[0], 3, new simple_type(simple_type::string_type));
    HEADER_SECTION_SCHEMA_types[4] = new type_declaration(strings[1], 4, new simple_type(simple_type::string_type));
    HEADER_SECTION_SCHEMA_types[0] = new entity(strings[2], false, 0, (entity*) 0);
    HEADER_SECTION_SCHEMA_types[1] = new entity(strings[3], false, 1, (entity*) 0);
    HEADER_SECTION_SCHEMA_types[2] = new entity(strings[4], false, 2, (entity*) 0);
    ((entity*)HEADER_SECTION_SCHEMA_types[0])->set_attributes({new attribute(strings[5], new aggregation_type(aggregation_type::list_type, 1, -1, new simple_type(simple_type::string_type)), false),new attribute(strings[6], new simple_type(simple_type::string_type), false)}, {false,false});
    ((entity*)HEADER_SECTION_SCHEMA_types[1])->set_attributes({new attribute(strings[7], new simple_type(simple_type::string_type), false),new attribute(strings[8], new named_type(HEADER_SECTION_SCHEMA_types[4]), false),new attribute(strings[9], new aggregation_type(aggregation_type::list_type, 1, -1, new simple_type(simple_type::string_type)), false),new attribute(strings[10], new aggregation_type(aggregation_type::list_type, 1, -1, new simple_type(simple_type::string_type)), false),new attribute(strings[11], new simple_type(simple_type::string_type), false),new attribute(strings[12], new simple_type(simple_type::string_type), false),new attribute(strings[13], new simple_type(simple_type::string_type), false)}, {false,false,false,false,false,false,false});
    ((entity*)HEADER_SECTION_SCHEMA_types[2])->set_attributes({new attribute(strings[14], new aggregation_type(aggregation_type::list_type, 1, -1, new named_type(HEADER_SECTION_SCHEMA_types[3])), false)}, {false});
    return new schema_definition(strings[15], {HEADER_SECTION_SCHEMA_types[0],HEADER_SECTION_SCHEMA_types[1],HEADER_SECTION_SCHEMA_types[2],HEADER_SECTION_SCHEMA_types[3],HEADER_SECTION_SCHEMA_types[4]});
}
static std::unique_ptr<schema_definition> schema;

void Header_section_schema::clear_schema() {
    schema.reset();
}

const schema_definition& Header_section_schema::get_schema() {
    if (!schema) {
        schema.reset(HEADER_SECTION_SCHEMA_populate_schema());
    }
    return *schema;
}

