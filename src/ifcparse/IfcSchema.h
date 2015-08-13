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

class declaration; 
class type_declaration; 
class select_type; 
class enumeration_type; 
class entity;

class parameter_type {
};

class named_type : public parameter_type {
protected:
	declaration* declared_type_;
public:
	named_type(declaration* declared_type)
		: declared_type_(declared_type) {}

	declaration* declared_type() const { return declared_type_; }
};

class simple_type : public parameter_type {
public:
	typedef enum { binary_type, boolean_type, integer_type, logical_type, number_type, real_type, string_type } data_type;
protected:
	data_type declared_type_;
public:
	simple_type(data_type declared_type)
		: declared_type_(declared_type) {}

	data_type declared_type() const { return declared_type_; }
};

class aggregation_type : public parameter_type {
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

	aggregate_type type_of_aggregation() const { type_of_aggregation_; }
	int bound1() const { return bound1_; }
	int bound2() const { return bound2_; }
	parameter_type* type_of_element() const { return type_of_element_; }
};

class declaration {
protected:
	std::string name_;

public:
	declaration(const std::string& name)
		: name_(name) {}

	const std::string& name() const { return name_; }

	virtual const type_declaration* as_type_declaration() const { return static_cast<type_declaration*>(0); }
	virtual const select_type* as_select_type() const { return static_cast<select_type*>(0); }
	virtual const enumeration_type* as_enumeration_type() const { return static_cast<enumeration_type*>(0); }
	virtual const entity* as_entity() const { return static_cast<entity*>(0); }
};

class type_declaration : public declaration {
protected:
	const parameter_type* declared_type_;

public:
	type_declaration(const std::string& name, const parameter_type* declared_type)
		: declaration(name)
		, declared_type_(declared_type)	{}

	const parameter_type* declared_type() const { return declared_type_; }

	virtual const type_declaration* as_type_declaration() const { return this; }
};

class select_type : public declaration {
protected:
	std::vector<const declaration*> select_list_;
public:
	select_type(const std::string& name, const std::vector<const declaration*>& select_list)
		: declaration(name)
		, select_list_(select_list)	{}

	const std::vector<const declaration*>& select_list() const { return select_list_; }

	virtual const select_type* as_select_type() const { return this; }
};

class enumeration_type : public declaration {
protected:
	std::vector<std::string> enumeration_items_;
public:
	enumeration_type(const std::string& name, const std::vector<std::string>& enumeration_items)
		: declaration(name)
		, enumeration_items_(enumeration_items)	{}

	const std::vector<std::string>& enumeration_items() const { return enumeration_items_; }

	virtual const enumeration_type* as_enumeration_type() const { return this; }
};

class entity : public declaration {
public:
	class attribute {
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

protected:
	const entity* supertype_; /* NB: IFC explicitly allows only single inheritance */
	std::vector<const entity*> subtypes_;

	std::vector<const attribute*> attributes_;
	std::vector<bool> derived_;
	
public:
	entity(const std::string& name, entity* supertype)
		: declaration(name)
		, supertype_(supertype)
	{}

	void set_subtypes(const std::vector<const entity*>& subtypes) {
		subtypes_ = subtypes;
	}

	void set_attributes(const std::vector<const attribute*>& attributes, const std::vector<bool>& derived) {
		attributes_ = attributes;
		derived_ = derived;
	}

	const std::vector<const entity*>& subtypes() const { return subtypes_; }
	const std::vector<const attribute*>& attributes() const { return attributes_; }
	const std::vector<bool>& derived() const { return derived_; }
	
	const std::vector<const attribute*> all_attributes() const {
		std::vector<const attribute*> attrs;
		attrs.reserve(derived_.size());
		std::vector<const attribute*>::iterator it = attrs.begin();
		if (supertype_) {
			const std::vector<const attribute*> supertype_attrs = supertype_->all_attributes();
			it = std::copy(supertype_attrs.begin(), supertype_attrs.end(), it);
		}
		std::copy(attributes_.begin(), attributes_.end(), it);
		return attrs;
	}

	virtual const entity* as_entity() const { return this; }
};

class schema_definition {
private:
	std::string name_;

	std::vector<const declaration*> declarations_;

	std::vector<const type_declaration*> type_declarations_;
	std::vector<const select_type*> select_types_;
	std::vector<const enumeration_type*> enumeration_types_;

	class declaration_by_name_cmp : public std::binary_function<const declaration*, const std::string&, bool> {
	public:
		bool operator()(const declaration* decl, const std::string& name) {
			return decl->name() < name;
		}
	};

public:
	schema_definition(const std::string& name, const std::vector<const declaration*>& declarations)
		: name_(name)
		, declarations_(declarations)
	{
		for (std::vector<const declaration*>::const_iterator it = declarations_.begin(); it != declarations_.end(); ++it) {
			if ((**it).as_type_declaration()) type_declarations_.push_back((**it).as_type_declaration());
			if ((**it).as_select_type()) select_types_.push_back((**it).as_select_type());
			if ((**it).as_enumeration_type()) enumeration_types_.push_back((**it).as_enumeration_type());
		}
	}

	~schema_definition() {
		for (std::vector<const declaration*>::const_iterator it = declarations_.begin(); it != declarations_.end(); ++it) {
			delete *it;
		}
	}

	const declaration* declaration_by_name(const std::string& name) {
		std::vector<const declaration*>::const_iterator it = std::lower_bound(declarations_.begin(), declarations_.end(), name, declaration_by_name_cmp());
		if (it == declarations_.end() || (**it).name() != name) {
			throw;
		} else {
			return *it;
		}
	}

	const std::vector<const declaration*>& declarations() { return declarations_; }
	const std::vector<const type_declaration*>& type_declarations() { return type_declarations_; }
	const std::vector<const select_type*>& select_types() { return select_types_; }
	const std::vector<const enumeration_type*>& enumeration_types() { return enumeration_types_; }
};

#endif