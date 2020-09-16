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

#include <string>
#include <vector>
#include <algorithm>
#include <iterator>

#include <boost/algorithm/string.hpp>

#include "../ifcparse/IfcException.h"

// Forward declarations
class IfcEntityInstanceData;

namespace IfcUtil {
	class IfcBaseClass;
}

namespace IfcParse {

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
		virtual const named_type* as_named_type() const { return static_cast<named_type*>(0); }
		virtual const simple_type* as_simple_type() const { return static_cast<simple_type*>(0); }
		virtual const aggregation_type* as_aggregation_type() const { return static_cast<aggregation_type*>(0); }

		virtual bool is(const std::string& /*name*/) const { return false; }
		virtual bool is(const IfcParse::declaration& /*decl*/) const { return false; }
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
		virtual bool is(const IfcParse::declaration& decl) const;
	};

	class IFC_PARSE_API simple_type : public parameter_type {
	public:
		typedef enum { binary_type, boolean_type, integer_type, logical_type, number_type, real_type, string_type, datatype_COUNT } data_type;
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
		typedef enum { array_type, bag_type, list_type, set_type } aggregate_type;
	protected:
		aggregate_type type_of_aggregation_;
		int bound1_, bound2_;
		parameter_type* type_of_element_;
	public:
		aggregation_type(aggregate_type type_of_aggregation, int bound1, int bound2, parameter_type* type_of_element)
			: type_of_aggregation_(type_of_aggregation)
			, bound1_(bound1)
			, bound2_(bound2)
			, type_of_element_(type_of_element)
		{}

		aggregate_type type_of_aggregation() const { return type_of_aggregation_; }
		int bound1() const { return bound1_; }
		int bound2() const { return bound2_; }
		parameter_type* type_of_element() const { return type_of_element_; }

		virtual const aggregation_type* as_aggregation_type() const { return this; }
	};

	class IFC_PARSE_API declaration {
		friend class schema_definition;

	protected:
		std::string name_, name_lower_;
		int index_in_schema_;
		mutable const schema_definition* schema_;

	public:		
		declaration(const std::string& name, int index_in_schema)
			: name_(name)
			, name_lower_(boost::to_lower_copy(name))
			, index_in_schema_(index_in_schema)
			, schema_(0)
		{}

		virtual ~declaration() {}

		const std::string& name() const { return name_; }
		const std::string& name_lc() const { return name_lower_; }

		virtual const type_declaration* as_type_declaration() const { return static_cast<type_declaration*>(0); }
		virtual const select_type* as_select_type() const { return static_cast<select_type*>(0); }
		virtual const enumeration_type* as_enumeration_type() const { return static_cast<enumeration_type*>(0); }
		virtual const entity* as_entity() const { return static_cast<entity*>(0); }

		bool is(const std::string& name) const;
		bool is(const IfcParse::declaration& decl) const;

		int index_in_schema() const { return index_in_schema_; }

		int type() const { return index_in_schema_; }

		const schema_definition* schema() const { return schema_; }
	};

	class IFC_PARSE_API type_declaration : public declaration {
	protected:
		const parameter_type* declared_type_;

	public:
		type_declaration(const std::string& name, int index_in_schema, const parameter_type* declared_type)
			: declaration(name, index_in_schema)
			, declared_type_(declared_type)	{}

		const parameter_type* declared_type() const { return declared_type_; }

		virtual const type_declaration* as_type_declaration() const { return this; }
	};

	class IFC_PARSE_API select_type : public declaration {
	protected:
		std::vector<const declaration*> select_list_;
	public:
		select_type(const std::string& name, int index_in_schema, const std::vector<const declaration*>& select_list)
			: declaration(name, index_in_schema)
			, select_list_(select_list)	{}

		const std::vector<const declaration*>& select_list() const { return select_list_; }

		virtual const select_type* as_select_type() const { return this; }
	};

	class IFC_PARSE_API enumeration_type : public declaration {
	protected:
		std::vector<std::string> enumeration_items_;
	public:
		enumeration_type(const std::string& name, int index_in_schema, const std::vector<std::string>& enumeration_items)
			: declaration(name, index_in_schema)
			, enumeration_items_(enumeration_items)	{}

		const std::vector<std::string>& enumeration_items() const { return enumeration_items_; }

		virtual const enumeration_type* as_enumeration_type() const { return this; }
	};

	class IFC_PARSE_API attribute {
	protected:
		std::string name_;
		const parameter_type* type_of_attribute_;
		bool optional_;

	public:
		attribute(const std::string& name, parameter_type* type_of_attribute, bool optional)
			: name_(name)
			, type_of_attribute_(type_of_attribute)
			, optional_(optional) {}

		const std::string& name() const { return name_; }
		const parameter_type* type_of_attribute() const { return type_of_attribute_; }
		bool optional() const { return optional_; }
	};

	class IFC_PARSE_API inverse_attribute {
	public:
		typedef enum { bag_type, set_type, unspecified_type } aggregate_type;
	protected:
		std::string name_;
		aggregate_type type_of_aggregation_;
		int bound1_, bound2_;
		const entity* entity_reference_;
		const attribute* attribute_reference_;
	public:
		inverse_attribute(const std::string& name, aggregate_type type_of_aggregation, int bound1, int bound2, const entity* entity_reference, const attribute* attribute_reference)
			: name_(name)
			, type_of_aggregation_(type_of_aggregation)
			, bound1_(bound1)
			, bound2_(bound2)
			, entity_reference_(entity_reference)
			, attribute_reference_(attribute_reference) {}

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
		std::vector<bool> derived_;

		std::vector<const inverse_attribute*> inverse_attributes_;

		class attribute_by_name_cmp {
		private:
			std::string name_;
		public:
			attribute_by_name_cmp(const std::string name)
				: name_(name) {}
			bool operator()(const attribute* attr) {
				return attr->name() == name_;
			}
		};

		const attribute* attribute_by_index_(size_t& index) const {
			const attribute* attr = 0;
			if (supertype_) {
				attr = supertype_->attribute_by_index_(index);
			}
			if (attr == 0) {
				if (index < attributes_.size()) {
					attr = attributes_[index];
				}
				index -= attributes_.size();
			}
			return attr;
		}

	public:
		entity(const std::string& name, bool is_abstract, int index_in_schema, entity* supertype)
			: declaration(name, index_in_schema)
			, is_abstract_(is_abstract)
			, supertype_(supertype)
		{}

		bool is(const std::string& name) const {
			if (name == name_) return true;
			else if (supertype_) return supertype_->is(name);
			else return false;
		}

		bool is(const IfcParse::declaration& decl) const {
			if (this == &decl) return true;
			else if (supertype_) return supertype_->is(decl);
			else return false;
		}

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
	
		const std::vector<const attribute*> all_attributes() const {
			std::vector<const attribute*> attrs;
			attrs.reserve(derived_.size());
			if (supertype_) {
				const std::vector<const attribute*> supertype_attrs = supertype_->all_attributes();
				std::copy(supertype_attrs.begin(), supertype_attrs.end(), std::back_inserter(attrs));
			}
			std::copy(attributes_.begin(), attributes_.end(), std::back_inserter(attrs));
			return attrs;
		}

		const std::vector<const inverse_attribute*> all_inverse_attributes() const {
			std::vector<const inverse_attribute*> attrs;
			if (supertype_) {
				const std::vector<const inverse_attribute*> supertype_inv_attrs = supertype_->all_inverse_attributes();
				std::copy(supertype_inv_attrs.begin(), supertype_inv_attrs.end(), std::back_inserter(attrs));
			}
			std::copy(inverse_attributes_.begin(), inverse_attributes_.end(), std::back_inserter(attrs));
			return attrs;
		}

		const attribute* attribute_by_index(size_t index) const {
			const attribute* attr = attribute_by_index_(index);
			if (attr == 0) {
				throw IfcParse::IfcException("Attribute index out of bounds");
			}
			return attr;
		}

		size_t attribute_count() const {
			size_t super_count = 0;
			if (supertype_) {
				super_count = supertype_->attribute_count();
			}
			return super_count + attributes_.size();
		}

		ptrdiff_t attribute_index(const attribute* attr) const {
			const entity* current = this;
			ptrdiff_t index = -1;
			do {
				if (index > -1) {
					index += current->attributes().size();
				} else {
					std::vector<const attribute*>::const_iterator it;
					it = std::find(current->attributes().begin(), current->attributes().end(), attr);
					if (it != current->attributes().end()) {
						index = std::distance(current->attributes().begin(), it);
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
					std::vector<const attribute*>::const_iterator it;
					it = std::find_if(current->attributes().begin(), current->attributes().end(), cmp);
					if (it != current->attributes().end()) {
						index = std::distance(current->attributes().begin(), it);
					}
				}
			} while ((current = current->supertype_) != 0);
			return index;
		}

		const entity* supertype() const { return supertype_; }

		virtual const entity* as_entity() const { return this; }
	};

	class instance_factory {
	public:
		virtual IfcUtil::IfcBaseClass* operator()(IfcEntityInstanceData* data) const = 0;
	};

	class schema_definition {
	private:
		std::string name_;

		std::vector<const declaration*> declarations_;

		std::vector<const type_declaration*> type_declarations_;
		std::vector<const select_type*> select_types_;
		std::vector<const enumeration_type*> enumeration_types_;
		std::vector<const entity*> entities_;

		class declaration_by_name_cmp {
		public:
			bool operator()(const declaration* decl, const std::string& name) {
				return decl->name_lc() < name;
			}
		};

		class declaration_by_index_sort  {
		public:
			bool operator()(const declaration* a, const declaration* b) {
				return a->index_in_schema() < b->index_in_schema();
			}
		};

		instance_factory* factory_;

	public:
		
		schema_definition(const std::string& name, const std::vector<const declaration*>& declarations, instance_factory* factory);

		~schema_definition();

		const declaration* declaration_by_name(const std::string& name) const {
			const std::string name_lower = boost::to_lower_copy(name);
			std::vector<const declaration*>::const_iterator it = std::lower_bound(declarations_.begin(), declarations_.end(), name_lower, declaration_by_name_cmp());
			if (it == declarations_.end() || (**it).name_lc() != name_lower) {
				throw IfcParse::IfcException("Entity with '" + name + "' not found");
			} else {
				return *it;
			}
		}

		const declaration* declaration_by_name(int name) const {
			return declarations_[name];
		}

		const std::vector<const declaration*>& declarations() const { return declarations_; }
		const std::vector<const type_declaration*>& type_declarations() const { return type_declarations_; }
		const std::vector<const select_type*>& select_types() const { return select_types_; }
		const std::vector<const enumeration_type*>& enumeration_types() const { return enumeration_types_; }
		const std::vector<const entity*>& entities() const { return entities_; }

		const std::string& name() const { return name_; }

		IfcUtil::IfcBaseClass* instantiate(IfcEntityInstanceData* data) const;
	};

	const schema_definition* schema_by_name(const std::string&);

	void register_schema(schema_definition*);
}

#endif
