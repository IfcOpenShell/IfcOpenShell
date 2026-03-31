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

#ifndef IFCSCHEMA_H
#define IFCSCHEMA_H

#include "exception.h"

#include <algorithm>
#include <boost/algorithm/string.hpp>
#include <cctype>
#include <iterator>
#include <string>
#include <vector>
#include <optional>

// Forward declarations
class instance_data;

namespace ifcopenshell {

class declaration;

class type_declaration;
class select_type;
class enumeration_type;
class entity;

class named_type;
class simple_type;
class aggregation_type;

class schema_definition;

class IFC_PARSE_API parameter_type {
  public:
    virtual ~parameter_type() {}

    virtual const named_type* as_named_type() const { return static_cast<named_type*>(0); }
    virtual const simple_type* as_simple_type() const { return static_cast<simple_type*>(0); }
    virtual const aggregation_type* as_aggregation_type() const { return static_cast<aggregation_type*>(0); }

    virtual bool is(const std::string& /*type_name*/) const { return false; }
    virtual bool is(const ifcopenshell::declaration& /*declaration*/) const { return false; }
};

class IFC_PARSE_API named_type : public parameter_type {
  protected:
    declaration* declared_type_;

  public:
    named_type(declaration* declared_type)
        : declared_type_(declared_type) {}

    declaration* declared_type() const { return declared_type_; }

    virtual const named_type* as_named_type() const { return this; }

    virtual bool is(const std::string& name) const;
    virtual bool is(const ifcopenshell::declaration& decl) const;
};

class IFC_PARSE_API simple_type : public parameter_type {
  public:
    typedef enum {
        binary_type,
        boolean_type,
        integer_type,
        logical_type,
        number_type,
        real_type,
        string_type,
        datatype_COUNT
    } data_type;

  protected:
    data_type declared_type_;

  public:
    simple_type(data_type declared_type)
        : declared_type_(declared_type) {}

    data_type declared_type() const { return declared_type_; }

    virtual const simple_type* as_simple_type() const { return this; }
};

class IFC_PARSE_API aggregation_type : public parameter_type {
  public:
    typedef enum {
        array_type,
        bag_type,
        list_type,
        set_type
    } aggregate_type;

  protected:
    aggregate_type type_of_aggregation_;
    int bound1_;
    int bound2_;
    parameter_type* type_of_element_;

  public:
    aggregation_type(aggregate_type type_of_aggregation, int bound1, int bound2, parameter_type* type_of_element)
        : type_of_aggregation_(type_of_aggregation),
          bound1_(bound1),
          bound2_(bound2),
          type_of_element_(type_of_element) {}

    virtual ~aggregation_type() { delete type_of_element_; }

    aggregate_type type_of_aggregation() const { return type_of_aggregation_; }
    int bound1() const { return bound1_; }
    int bound2() const { return bound2_; }
    parameter_type* type_of_element() const { return type_of_element_; }

    virtual const aggregation_type* as_aggregation_type() const { return this; }
};

class IFC_PARSE_API declaration {
    friend class schema_definition;

  protected:
    std::string name_, name_upper_;
    int index_in_schema_;
    mutable const schema_definition* schema_;

    std::string& temp_string_() const {
        static thread_local std::string string;
        return string;
    }

  public:
    declaration(const std::string& name, int index_in_schema)
        : name_(name),
          name_upper_(boost::to_upper_copy(name)),
          index_in_schema_(index_in_schema),
          schema_(0) {}

    virtual ~declaration() {}

    const std::string& name() const { return name_; }
    const std::string& name_uc() const { return name_upper_; }

    virtual const type_declaration* as_type_declaration() const { return static_cast<type_declaration*>(0); }
    virtual const select_type* as_select_type() const { return static_cast<select_type*>(0); }
    virtual const enumeration_type* as_enumeration_type() const { return static_cast<enumeration_type*>(0); }
    virtual const entity* as_entity() const { return static_cast<entity*>(0); }

    bool is(const std::string& name) const;
    bool is(const ifcopenshell::declaration& decl) const;

    int index_in_schema() const { return index_in_schema_; }

    int type() const { return index_in_schema_; }

    const schema_definition* schema() const { return schema_; }
};

class IFC_PARSE_API type_declaration : public declaration {
  protected:
    const parameter_type* declared_type_;

  public:
    type_declaration(const std::string& name, int index_in_schema, const parameter_type* declared_type)
        : declaration(name, index_in_schema),
          declared_type_(declared_type) {}

    virtual ~type_declaration() { delete declared_type_; }

    const parameter_type* declared_type() const { return declared_type_; }

    virtual const type_declaration* as_type_declaration() const { return this; }
};

class IFC_PARSE_API select_type : public declaration {
  protected:
    std::vector<const declaration*> select_list_;

  public:
    select_type(const std::string& name, int index_in_schema, const std::vector<const declaration*>& select_list)
        : declaration(name, index_in_schema),
          select_list_(select_list) {}

    const std::vector<const declaration*>& select_list() const { return select_list_; }

    virtual const select_type* as_select_type() const { return this; }
};

class IFC_PARSE_API enumeration_type : public declaration {
  protected:
    std::vector<std::string> enumeration_items_;

  public:
    enumeration_type(const std::string& name, int index_in_schema, const std::vector<std::string>& enumeration_items)
        : declaration(name, index_in_schema),
          enumeration_items_(enumeration_items) {}

    const std::vector<std::string>& enumeration_items() const { return enumeration_items_; }

    const char* lookup_enum_value(size_t i) const {
        if (i >= enumeration_items_.size()) {
            throw ifcopenshell::exception("Unable to find keyword in schema for index " + std::to_string(i));
        }
        return enumeration_items_[i].c_str();
    }

    size_t lookup_enum_offset(const std::string& value_name) const {
        size_t index = 0;
        for (auto it = enumeration_items_.begin(); it != enumeration_items_.end(); ++it, ++index) {
            if (value_name == *it) {
                return index;
            }
        }
        throw ifcopenshell::exception("Unable to find keyword in schema: " + value_name);
    }

    virtual const enumeration_type* as_enumeration_type() const { return this; }
};

class IFC_PARSE_API attribute {
  protected:
    std::string name_;
    const parameter_type* type_of_attribute_;
    bool optional_;

  public:
    attribute(const std::string& name, parameter_type* type_of_attribute, bool optional)
        : name_(name),
          type_of_attribute_(type_of_attribute),
          optional_(optional) {}

    ~attribute() { delete type_of_attribute_; }

    const std::string& name() const { return name_; }
    const parameter_type* type_of_attribute() const { return type_of_attribute_; }
    bool optional() const { return optional_; }
};

class IFC_PARSE_API inverse_attribute {
  public:
    typedef enum {
        bag_type,
        set_type,
        unspecified_type
    } aggregate_type;

  protected:
    std::string name_;
    aggregate_type type_of_aggregation_;
    int bound1_;
    int bound2_;
    const entity* entity_reference_;
    const attribute* attribute_reference_;

  public:
    inverse_attribute(const std::string& name,
                      aggregate_type type_of_aggregation,
                      int bound1,
                      int bound2,
                      const entity* entity_reference,
                      const attribute* attribute_reference)
        : name_(name),
          type_of_aggregation_(type_of_aggregation),
          bound1_(bound1),
          bound2_(bound2),
          entity_reference_(entity_reference),
          attribute_reference_(attribute_reference) {}

    const std::string& name() const { return name_; }
    aggregate_type type_of_aggregation() const { return type_of_aggregation_; }
    int bound1() const { return bound1_; }
    int bound2() const { return bound2_; }
    const entity* entity_reference() const { return entity_reference_; }
    const attribute* attribute_reference() const { return attribute_reference_; }
};

class IFC_PARSE_API entity : public declaration {
  protected:
    bool is_abstract_;
    const entity* supertype_; /* NB: IFC explicitly allows only single inheritance */
    std::vector<const entity*> subtypes_;

    std::vector<const attribute*> attributes_;
    mutable std::optional<std::vector<const attribute*>> all_attributes_;
    std::vector<bool> derived_;

    std::vector<const inverse_attribute*> inverse_attributes_;

    class attribute_by_name_cmp {
      private:
        std::string name_;

      public:
        attribute_by_name_cmp(const std::string attribute_name)
            : name_(attribute_name) {}
        bool operator()(const attribute* attribute_definition) {
            return attribute_definition->name() == name_;
        }
    };

    const attribute* attribute_by_index_(size_t& attribute_index) const {
        const attribute* attr = 0;
        if (supertype_ != nullptr) {
            attr = supertype_->attribute_by_index_(attribute_index);
        }
        if (attr == 0) {
            if (attribute_index < attributes_.size()) {
                attr = attributes_[attribute_index];
            }
            attribute_index -= attributes_.size();
        }
        return attr;
    }

  public:
    entity(const std::string& name, bool is_abstract, int index_in_schema, entity* supertype)
        : declaration(name, index_in_schema),
          is_abstract_(is_abstract),
          supertype_(supertype) {}

    virtual ~entity();

    bool is_abstract() const { return is_abstract_; }

    void set_subtypes(const std::vector<const entity*>& subtypes) {
        subtypes_ = subtypes;
    }

    void set_attributes(const std::vector<const attribute*>& attributes, const std::vector<bool>& derived) {
        attributes_ = attributes;
        derived_ = derived;
    }

    void set_inverse_attributes(const std::vector<const inverse_attribute*>& inverse_attributes) {
        inverse_attributes_ = inverse_attributes;
    }

    const std::vector<const entity*>& subtypes() const { return subtypes_; }
    const std::vector<const attribute*>& attributes() const { return attributes_; }
    const std::vector<bool>& derived() const { return derived_; }

    const std::vector<const attribute*>& all_attributes() const {
        if (!all_attributes_) {
            auto& attrs = all_attributes_.emplace();
            attrs.reserve(derived_.size());
            if (supertype_ != nullptr) {
                const std::vector<const attribute*> supertype_attrs = supertype_->all_attributes();
                std::copy(supertype_attrs.begin(), supertype_attrs.end(), std::back_inserter(attrs));
            }
            std::copy(attributes_.begin(), attributes_.end(), std::back_inserter(attrs));
        }
        return *all_attributes_;
    }

    const std::vector<const inverse_attribute*> all_inverse_attributes() const {
        std::vector<const inverse_attribute*> attrs;
        if (supertype_ != nullptr) {
            const std::vector<const inverse_attribute*> supertype_inv_attrs = supertype_->all_inverse_attributes();
            std::copy(supertype_inv_attrs.begin(), supertype_inv_attrs.end(), std::back_inserter(attrs));
        }
        std::copy(inverse_attributes_.begin(), inverse_attributes_.end(), std::back_inserter(attrs));
        return attrs;
    }

    const attribute* attribute_by_index(size_t index) const {
        const attribute* attr = attribute_by_index_(index);
        if (attr == 0) {
            throw ifcopenshell::exception("Attribute index out of bounds");
        }
        return attr;
    }

    size_t attribute_count() const {
        size_t super_count = 0;
        if (supertype_ != nullptr) {
            super_count = supertype_->attribute_count();
        }
        return super_count + attributes_.size();
    }

    ptrdiff_t attribute_index(const attribute* attribute_definition) const {
        const entity* current = this;
        ptrdiff_t index = -1;
        do {
            if (index > -1) {
                index += current->attributes().size();
            } else {
                std::vector<const attribute*>::const_iterator iter;
                iter = std::find(current->attributes().begin(), current->attributes().end(), attribute_definition);
                if (iter != current->attributes().end()) {
                    index = std::distance(current->attributes().begin(), iter);
                }
            }
        } while ((current = current->supertype_) != 0);
        return index;
    }

    ptrdiff_t attribute_index(const std::string& attr_name) const {
        const entity* current = this;
        ptrdiff_t index = -1;
        attribute_by_name_cmp cmp(attr_name);
        do {
            if (index > -1) {
                index += current->attributes().size();
            } else {
                std::vector<const attribute*>::const_iterator iter;
                iter = std::find_if(current->attributes().begin(), current->attributes().end(), cmp);
                if (iter != current->attributes().end()) {
                    index = std::distance(current->attributes().begin(), iter);
                }
            }
        } while ((current = current->supertype_) != 0);
        return index;
    }

    const entity* supertype() const { return supertype_; }

    virtual const entity* as_entity() const { return this; }
};

class IFC_PARSE_API schema_definition {
  private:
    std::string name_;

    std::vector<const declaration*> declarations_;

    std::vector<const type_declaration*> type_declarations_;
    std::vector<const select_type*> select_types_;
    std::vector<const enumeration_type*> enumeration_types_;
    std::vector<const entity*> entities_;

    class declaration_by_name_cmp {
      public:
        bool operator()(const declaration* declaration, const std::string& name) {
            return declaration->name_uc() < name;
        }
    };

    class declaration_by_index_sort {
      public:
        bool operator()(const declaration* lhs, const declaration* rhs) {
            return lhs->index_in_schema() < rhs->index_in_schema();
        }
    };

    std::string& temp_string_() const {
        static thread_local std::string string;
        return string;
    }

  public:
    schema_definition(const std::string& name, const std::vector<const declaration*>& declarations);

    ~schema_definition();

    const declaration* declaration_by_name(const std::string& name) const {
        const std::string* name_ptr = &name;
        if (std::any_of(name.begin(), name.end(), [](char character) { return std::islower(character); })) {
            temp_string_() = name;
            boost::to_upper(temp_string_());
            name_ptr = &temp_string_();
        }
        std::vector<const declaration*>::const_iterator iter = std::lower_bound(declarations_.begin(), declarations_.end(), *name_ptr, declaration_by_name_cmp());
        if (iter == declarations_.end() || (**iter).name_uc() != *name_ptr) {
            throw ifcopenshell::exception("Entity with name '" + name + "' not found in schema '" + name_ + "'");
        }
        return *iter;
    }

    const declaration* declaration_by_name(size_t declaration_index) const {
        return declarations_.at(declaration_index);
    }

    const std::vector<const declaration*>& declarations() const { return declarations_; }
    const std::vector<const type_declaration*>& type_declarations() const { return type_declarations_; }
    const std::vector<const select_type*>& select_types() const { return select_types_; }
    const std::vector<const enumeration_type*>& enumeration_types() const { return enumeration_types_; }
    const std::vector<const entity*>& entities() const { return entities_; }

    const std::string& name() const { return name_; }
};

IFC_PARSE_API const schema_definition* schema_by_name(const std::string& schema_name);

IFC_PARSE_API std::vector<std::string> schema_names();

IFC_PARSE_API void register_schema(schema_definition* schema);

IFC_PARSE_API void clear_schemas();
} // namespace ifcopenshell

#endif
