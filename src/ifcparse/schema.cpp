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

#include "schema.h"

#include "express.h"

#include <map>
#include <mutex>

#ifdef HAS_SCHEMA_2x3
#include "schemas/Ifc2x3.h"
#endif
#ifdef HAS_SCHEMA_4
#include "schemas/Ifc4.h"
#endif
#ifdef HAS_SCHEMA_4x1
#include "schemas/Ifc4x1.h"
#endif
#ifdef HAS_SCHEMA_4x2
#include "schemas/Ifc4x2.h"
#endif
#ifdef HAS_SCHEMA_4x3_rc1
#include "schemas/Ifc4x3_rc1.h"
#endif
#ifdef HAS_SCHEMA_4x3_rc2
#include "schemas/Ifc4x3_rc2.h"
#endif
#ifdef HAS_SCHEMA_4x3_rc3
#include "schemas/Ifc4x3_rc3.h"
#endif
#ifdef HAS_SCHEMA_4x3_rc4
#include "schemas/Ifc4x3_rc4.h"
#endif
#ifdef HAS_SCHEMA_4x3
#include "schemas/Ifc4x3.h"
#endif
#ifdef HAS_SCHEMA_4x3_tc1
#include "schemas/Ifc4x3_tc1.h"
#endif
#ifdef HAS_SCHEMA_4x3_add1
#include "schemas/Ifc4x3_add1.h"
#endif
#ifdef HAS_SCHEMA_4x3_add2
#include "schemas/Ifc4x3_add2.h"
#endif
#include "schemas/Header_section_schema.h"

bool ifcopenshell::declaration::is(const std::string& name) const {
    const std::string* name_ptr = &name;
    if (std::any_of(name.begin(), name.end(), [](char character) { return std::islower(character); })) {
        temp_string_() = name;
        boost::to_upper(temp_string_());
        name_ptr = &temp_string_();
    }

    if (name_upper_ == *name_ptr) {
        return true;
    }

    if ((this->as_entity() != nullptr) && (this->as_entity()->supertype() != nullptr)) {
        return this->as_entity()->supertype()->is(name);
    }
    if (this->as_type_declaration() != nullptr) {
        const ifcopenshell::named_type* named_type = this->as_type_declaration()->declared_type()->as_named_type();
        if (named_type != nullptr) {
            return named_type->is(name);
        }
    }

    return false;
}

bool ifcopenshell::declaration::is(const ifcopenshell::declaration& decl) const {
    if (this == &decl) {
        return true;
    }

    if (decl.as_select_type() != nullptr) {
        const auto& li = decl.as_select_type()->select_list();
        for (const auto* selected_decl : li) {
            if (is(*selected_decl)) {
                return true;
            }
        }
    }
    if ((this->as_entity() != nullptr) && (this->as_entity()->supertype() != nullptr)) {
        return this->as_entity()->supertype()->is(decl);
    }
    if (this->as_type_declaration() != nullptr) {
        const ifcopenshell::named_type* named_type = this->as_type_declaration()->declared_type()->as_named_type();
        if (named_type != nullptr) {
            return named_type->is(decl);
        }
    }

    return false;
}

bool ifcopenshell::named_type::is(const std::string& name) const {
    return declared_type()->is(name);
}

bool ifcopenshell::named_type::is(const ifcopenshell::declaration& decl) const {
    return declared_type()->is(decl);
}

ifcopenshell::entity::~entity() {
    for (const auto* attribute : attributes_) {
        delete attribute;
    }
    for (const auto* inverse_attribute : inverse_attributes_) {
        delete inverse_attribute;
    }
}
namespace {
	std::string schema_key(const std::string& schema_name) {
		return boost::to_upper_copy(schema_name);
	}

	ifcopenshell::plugin::module builtin_schema_module(const std::string& schema_name) {
		ifcopenshell::plugin::metadata metadata;
		metadata.kind_ = ifcopenshell::plugin::kind::parse_schema;
		metadata.id = "parse.schema." + boost::to_lower_copy(schema_name);
		metadata.schema = schema_name;
		return ifcopenshell::plugin::module::builtin(metadata);
	}

	void register_builtin_schemas(ifcopenshell::schema_registry& registry) {
		registry.bind("HEADER_SECTION_SCHEMA", &Header_section_schema::get_schema, &Header_section_schema::clear_schema, builtin_schema_module("HEADER_SECTION_SCHEMA"));
#ifdef HAS_SCHEMA_2x3
		registry.bind("IFC2X3", &Ifc2x3::get_schema, &Ifc2x3::clear_schema, builtin_schema_module("IFC2X3"));
#endif
#ifdef HAS_SCHEMA_4
		registry.bind("IFC4", &Ifc4::get_schema, &Ifc4::clear_schema, builtin_schema_module("IFC4"));
#endif
#ifdef HAS_SCHEMA_4x1
		registry.bind("IFC4X1", &Ifc4x1::get_schema, &Ifc4x1::clear_schema, builtin_schema_module("IFC4X1"));
#endif
#ifdef HAS_SCHEMA_4x2
		registry.bind("IFC4X2", &Ifc4x2::get_schema, &Ifc4x2::clear_schema, builtin_schema_module("IFC4X2"));
#endif
#ifdef HAS_SCHEMA_4x3_rc1
		registry.bind("IFC4X3_RC1", &Ifc4x3_rc1::get_schema, &Ifc4x3_rc1::clear_schema, builtin_schema_module("IFC4X3_RC1"));
#endif
#ifdef HAS_SCHEMA_4x3_rc2
		registry.bind("IFC4X3_RC2", &Ifc4x3_rc2::get_schema, &Ifc4x3_rc2::clear_schema, builtin_schema_module("IFC4X3_RC2"));
#endif
#ifdef HAS_SCHEMA_4x3_rc3
		registry.bind("IFC4X3_RC3", &Ifc4x3_rc3::get_schema, &Ifc4x3_rc3::clear_schema, builtin_schema_module("IFC4X3_RC3"));
#endif
#ifdef HAS_SCHEMA_4x3_rc4
		registry.bind("IFC4X3_RC4", &Ifc4x3_rc4::get_schema, &Ifc4x3_rc4::clear_schema, builtin_schema_module("IFC4X3_RC4"));
#endif
#ifdef HAS_SCHEMA_4x3
		registry.bind("IFC4X3", &Ifc4x3::get_schema, &Ifc4x3::clear_schema, builtin_schema_module("IFC4X3"));
#endif
#ifdef HAS_SCHEMA_4x3_tc1
		registry.bind("IFC4X3_TC1", &Ifc4x3_tc1::get_schema, &Ifc4x3_tc1::clear_schema, builtin_schema_module("IFC4X3_TC1"));
#endif
#ifdef HAS_SCHEMA_4x3_add1
		registry.bind("IFC4X3_ADD1", &Ifc4x3_add1::get_schema, &Ifc4x3_add1::clear_schema, builtin_schema_module("IFC4X3_ADD1"));
#endif
#ifdef HAS_SCHEMA_4x3_add2
		registry.bind("IFC4X3_ADD2", &Ifc4x3_add2::get_schema, &Ifc4x3_add2::clear_schema, builtin_schema_module("IFC4X3_ADD2"));
#endif
	}

}

ifcopenshell::schema_definition::schema_definition(const std::string& name, const std::vector<const declaration*>& declarations)
    : name_(name)
    , declarations_(declarations)
{
    std::sort(declarations_.begin(), declarations_.end(), declaration_by_index_sort());
    for (std::vector<const declaration*>::iterator it = declarations_.begin(); it != declarations_.end(); ++it) {
        (**it).schema_ = this;

        if ((**it).as_type_declaration() != nullptr) {
            type_declarations_.push_back((**it).as_type_declaration());
        }
        if ((**it).as_select_type() != nullptr) {
            select_types_.push_back((**it).as_select_type());
        }
        if ((**it).as_enumeration_type() != nullptr) {
            enumeration_types_.push_back((**it).as_enumeration_type());
        }
        if ((**it).as_entity() != nullptr) {
            entities_.push_back((**it).as_entity());
        }
    }
    register_schema(this);
}

ifcopenshell::schema_definition::~schema_definition() {
    for (std::vector<const declaration*>::const_iterator it = declarations_.begin(); it != declarations_.end(); ++it) {
        delete *it;
    }
}

void ifcopenshell::register_schema(schema_definition* schema) {
    schema_registry_instance().bind(schema);
}

ifcopenshell::schema_registry& ifcopenshell::schema_registry_instance() {
	static schema_registry registry;
	static std::once_flag once;
	std::call_once(once, register_builtin_schemas, std::ref(registry));
	return registry;
}

void ifcopenshell::schema_registry::bind(const std::string& schema_name, get_schema_fn get, clear_schema_fn clear, const plugin::module& module) {
	auto& entry = entries_[schema_key(schema_name)];
	entry.get_ = get;
	entry.clear_ = clear;
	entry.module_ = module;
}

void ifcopenshell::schema_registry::bind(schema_definition* schema) {
	auto& entry = entries_[schema_key(schema->name())];
	entry.schema_ = schema;
}

const ifcopenshell::schema_definition* ifcopenshell::schema_registry::get(const std::string& schema_name) {
	auto iter = entries_.find(schema_key(schema_name));
	if (iter == entries_.end()) {
		throw ifcopenshell::exception("No schema named " + schema_name);
	}
	if (!iter->second.schema_ && iter->second.get_) {
		iter->second.schema_ = &iter->second.get_();
	}
	if (!iter->second.schema_) {
		throw ifcopenshell::exception("No schema named " + schema_name);
	}
	return iter->second.schema_;
}

std::vector<std::string> ifcopenshell::schema_registry::names() const {
	std::vector<std::string> names;
	for (const auto& pair : entries_) {
		names.push_back(pair.first);
	}
	return names;
}

void ifcopenshell::schema_registry::clear() {
	for (auto& pair : entries_) {
		if (pair.second.clear_) {
			pair.second.clear_();
		}
		pair.second.schema_ = nullptr;
	}
}

const ifcopenshell::schema_definition* ifcopenshell::schema_by_name(const std::string& name) {
	return schema_registry_instance().get(name);
}

std::vector<std::string> ifcopenshell::schema_names() {
    return schema_registry_instance().names();
}

void ifcopenshell::clear_schemas() {
    schema_registry_instance().clear();
}
