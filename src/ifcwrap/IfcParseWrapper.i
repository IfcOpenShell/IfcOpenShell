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

// A class declaration to silence SWIG warning about base classes being
// undefined, the constructor is private so that SWIG does not wrap them
class IfcEntityInstanceData {
private:
	IfcEntityInstanceData();
};

%ignore IfcParse::IfcFile::register_inverse;
%ignore IfcParse::IfcFile::unregister_inverse;
%ignore IfcParse::IfcFile::schema;
%ignore IfcParse::IfcFile::begin;
%ignore IfcParse::IfcFile::end;

%ignore parse_context;

%ignore operator<<;

%ignore IfcParse::FileDescription::FileDescription;
%ignore IfcParse::FileName::FileName;
%ignore IfcParse::FileSchema::FileSchema;
%ignore IfcParse::IfcFile::tokens;

%ignore IfcParse::IfcSpfHeader::IfcSpfHeader(IfcSpfLexer*);
%ignore IfcParse::IfcSpfHeader::lexer;
%ignore IfcParse::IfcSpfHeader::stream;
%ignore IfcParse::HeaderEntity::is;

%ignore IfcParse::IfcFile::type_iterator;

%ignore IfcUtil::IfcBaseClass::is;

%rename("by_id") instance_by_id;
%rename("by_type") instances_by_type;
%rename("by_type_excl_subtypes") instances_by_type_excl_subtypes;
%rename("entity_instance") IfcBaseClass;
%rename("file") IfcFile;
%rename("add") addEntity;
%rename("remove") removeEntity;

%{

template<typename T>
struct is_std_vector : std::false_type {};
template<typename T, typename Alloc>
struct is_std_vector<std::vector<T, Alloc>> : std::true_type {};
template<typename T>
constexpr bool is_std_vector_v = is_std_vector<T>::value;

template<typename T>
struct is_std_vector_vector : std::false_type {};
template<typename T, typename Alloc, typename Alloc2>
struct is_std_vector_vector<std::vector<std::vector<T, Alloc>, Alloc2>> : std::true_type {};
template<typename T>
constexpr bool is_std_vector_vector_v = is_std_vector_vector<T>::value;

%}

class attribute_value_derived {};
%{
class attribute_value_derived {};
%}

%extend attribute_value_derived {
	%pythoncode %{
		def __bool__(self): return False
		def __repr__(self): return '*'
	%}
}

%inline %{
static bool feature_use_attribute_value_derived = false;

void set_feature(const std::string& x, PyObject* v) {
	if (PyBool_Check(v) && x == "use_attribute_value_derived") {
		feature_use_attribute_value_derived = v == Py_True;
	} else {
		throw std::runtime_error("Invalid feature specification");
	}
}

PyObject* get_feature(const std::string& x) {
	if (x == "use_attribute_value_derived") {
		return PyBool_FromLong(feature_use_attribute_value_derived);
	} else {
		throw std::runtime_error("Invalid feature specification");
	}
}

%}

%{

static const std::string& helper_fn_declaration_get_name(const IfcParse::declaration* decl) {
	return decl->name();
}

static IfcUtil::ArgumentType helper_fn_attribute_type(const IfcUtil::IfcBaseClass* inst, unsigned i) {
	const IfcParse::parameter_type* pt = 0;
	if (inst->declaration().as_entity()) {
		pt = inst->declaration().as_entity()->attribute_by_index(i)->type_of_attribute();
		if (inst->declaration().as_entity()->derived()[i]) {
			return IfcUtil::Argument_DERIVED;
		}
	} else if (inst->declaration().as_type_declaration() && i == 0) {
		pt = inst->declaration().as_type_declaration()->declared_type();
	} else if (inst->declaration().as_enumeration_type() && i == 0) {
		// Enumeration is always from string in Python
		return IfcUtil::Argument_STRING;
	}

	if (pt == 0) {
		return IfcUtil::Argument_UNKNOWN;
	} else {
		return IfcUtil::from_parameter_type(pt);
	}
}
%}

%extend IfcParse::IfcFile {
	// Use to correlate to entity_instance.file_pointer, so that we
	// can trace file ownership of instances on the python side.
	size_t file_pointer() const {
		return reinterpret_cast<size_t>($self);
	}

	IfcUtil::IfcBaseClass* by_guid(const std::string& guid) {
		return $self->instance_by_guid(guid);
	}
	
	aggregate_of_instance::ptr get_inverse(IfcUtil::IfcBaseClass* e) {
		return $self->getInverse(e->as<IfcUtil::IfcBaseEntity>()->id(), 0, -1);
	}

	std::vector<int> get_inverse_indices(IfcUtil::IfcBaseClass* e) {
		return $self->get_inverse_indices(e->as<IfcUtil::IfcBaseEntity>()->id());
	}

	int get_total_inverses(IfcUtil::IfcBaseClass* e) {
		return $self->getTotalInverses(e->as<IfcUtil::IfcBaseEntity>()->id());
	}

	void write(const std::string& fn) {
		std::ofstream f(IfcUtil::path::from_utf8(fn).c_str());
		f << (*$self);
	}

	std::string to_string() {
		std::stringstream s;
		s << (*$self);
		return s.str();
	}

	std::vector<unsigned> entity_names() const {
		std::vector<unsigned> keys;
		keys.reserve(std::distance($self->begin(), $self->end()));
		for (IfcParse::IfcFile::entity_by_id_t::const_iterator it = $self->begin(); it != $self->end(); ++ it) {
			keys.push_back(it->first);
		}
		return keys;
	}

	std::vector<std::string> types() const {
		const size_t n = std::distance($self->types_begin(), $self->types_end());
		std::vector<std::string> ts;
		ts.reserve(n);
		std::transform($self->types_begin(), $self->types_end(), std::back_inserter(ts), helper_fn_declaration_get_name);
		return ts;
	}

	/*
	std::vector<std::string> types_with_super() const {
		const size_t n = std::distance($self->types_incl_super_begin(), $self->types_incl_super_end());
		std::vector<std::string> ts;
		ts.reserve(n);
		std::transform($self->types_incl_super_begin(), $self->types_incl_super_end(), std::back_inserter(ts), helper_fn_declaration_get_name);
		return ts;
	}
	*/

	std::string schema_name() const {
		if ($self->schema() == 0) return "";
		return $self->schema()->name();
	}

	%pythoncode %{
        # Hide the getters with read-only property implementations
        header = property(header)
        schema = property(schema_name)
	%}
}

%extend IfcUtil::IfcBaseClass {

	int get_attribute_category(const std::string& name) const {
		if (!$self->declaration().as_entity()) {
			return name == "wrappedValue";
		}
		
		{
		const std::vector<const IfcParse::attribute*> attrs = $self->declaration().as_entity()->all_attributes();
		std::vector<const IfcParse::attribute*>::const_iterator it = attrs.begin();
		for (; it != attrs.end(); ++it) {
			if ((*it)->name() == name) {
				return 1;
			}
		}
		}

		{
		const std::vector<const IfcParse::inverse_attribute*> attrs = $self->declaration().as_entity()->all_inverse_attributes();
		std::vector<const IfcParse::inverse_attribute*>::const_iterator it = attrs.begin();
		for (; it != attrs.end(); ++it) {
			if ((*it)->name() == name) {
				return 2;
			}
		}
		}

		return 0;
	}

	// id() is defined on IfcBaseEntity and not on IfcBaseClass, in order
	// to expose it to the Python wrapper it is simply duplicated here.
	// Same applies to the two methods reimplemented below.
	int id() const {
		return $self->as<IfcUtil::IfcBaseEntity>() != nullptr
			? $self->as<IfcUtil::IfcBaseEntity>()->id()
			: 0;
	}

	int __len__() const {
		if ($self->declaration().as_entity()) {
			return $self->declaration().as_entity()->attribute_count();
		} else {
			return 1;
		}
	}

	std::vector<std::string> get_attribute_names() const {
		if (!$self->declaration().as_entity()) {
			return std::vector<std::string>(1, "wrappedValue");
		}
		
		const std::vector<const IfcParse::attribute*> attrs = $self->declaration().as_entity()->all_attributes();
		
		std::vector<std::string> attr_names;
		attr_names.reserve(attrs.size());		
		
		std::vector<const IfcParse::attribute*>::const_iterator it = attrs.begin();
		for (; it != attrs.end(); ++it) {
			attr_names.push_back((*it)->name());
		}

		return attr_names;
	}

	std::vector<std::string> get_inverse_attribute_names() const {
		if (!$self->declaration().as_entity()) {
			return std::vector<std::string>(0);
		}

		const std::vector<const IfcParse::inverse_attribute*> attrs = $self->declaration().as_entity()->all_inverse_attributes();
		
		std::vector<std::string> attr_names;
		attr_names.reserve(attrs.size());		
		
		std::vector<const IfcParse::inverse_attribute*>::const_iterator it = attrs.begin();
		for (; it != attrs.end(); ++it) {
			attr_names.push_back((*it)->name());
		}

		return attr_names;
	}
	
	bool is_a(const std::string& s) {
		return self->declaration().is(s);
	}

	std::string is_a(bool with_schema=false) const {
		auto t = self->declaration().name();
		if (with_schema) {
			t = self->declaration().schema()->name() + "." + t;
		}
		return t;
	}

	AttributeValue get_argument(unsigned i) {
		return $self->data().get_attribute_value(i);
	}

	AttributeValue get_argument(const std::string& a) {
		auto i = $self->declaration().as_entity()->attribute_index(a);
		if (i == -1) {
			throw std::runtime_error("Attribute '" + a + "' not found on entity named " + $self->declaration().name());
		}
		return $self->data().get_attribute_value((unsigned)i);
	}

	bool __eq__(IfcUtil::IfcBaseClass* other) const {
		return $self->identity() == other->identity();
	}

	std::string __repr__() const {
	    std::ostringstream oss;
		$self->toString(oss);
        return oss.str();
	}

	std::string to_string(bool valid_spf) const {
		std::ostringstream oss;
		$self->toString(oss, valid_spf);
        return oss.str();
	}

	// Just something to have a somewhat sensible value to hash
	size_t file_pointer() const {
		return reinterpret_cast<size_t>($self->file_);
	}

	unsigned get_argument_index(const std::string& a) const {
		if ($self->declaration().as_entity()) {
			return $self->declaration().as_entity()->attribute_index(a);
		} else if (a == "wrappedValue") {
			return 0;
		} else {
			throw IfcParse::IfcException(a + " not found on " + $self->declaration().name());
		}
	}

	aggregate_of_instance::ptr get_inverse(const std::string& a) {
		if ($self->declaration().as_entity()) {
			return ((IfcUtil::IfcBaseEntity*)$self)->get_inverse(a);
		} else {
			throw IfcParse::IfcException(a + " not found on " + $self->declaration().name());
		}
	}

	const char* const get_argument_type(unsigned int i) const {
		return IfcUtil::ArgumentTypeToString(helper_fn_attribute_type($self, i));
	}

	const std::string& get_argument_name(unsigned int i) const {
		if ($self->declaration().as_entity()) {
			return $self->declaration().as_entity()->attribute_by_index(i)->name();
		} else if (i == 0) {
			static std::string WRAPPED = "wrappedValue";
			return WRAPPED;
		} else {
			throw IfcParse::IfcException(boost::lexical_cast<std::string>(i) + " out of bounds on " + $self->declaration().name());
		}
	}

	void setArgumentAsNull(unsigned int i) {
		bool is_optional = $self->declaration().as_entity()->attribute_by_index(i)->optional();
		if (is_optional) {
			self->set_attribute_value(i, Blank{});
		} else {
			throw IfcParse::IfcException("Attribute not set");
		}
	}

	void setArgumentAsInt(unsigned int i, int v) {
		IfcUtil::ArgumentType arg_type = helper_fn_attribute_type($self, i);
		if (arg_type == IfcUtil::Argument_INT) {
			self->set_attribute_value(i, v);	
		} else if ( (arg_type == IfcUtil::Argument_BOOL) && ( (v == 0) || (v == 1) ) ) {
			self->set_attribute_value(i, v);	
		} else {
			throw IfcParse::IfcException("Attribute not set");
		}
	}

	void setArgumentAsBool(unsigned int i, bool v) {
		IfcUtil::ArgumentType arg_type = helper_fn_attribute_type($self, i);
		if (arg_type == IfcUtil::Argument_BOOL) {
			self->set_attribute_value(i, v);	
		} else {
			throw IfcParse::IfcException("Attribute not set");
		}
	}

	void setArgumentAsLogical(unsigned int i, boost::logic::tribool v) {
		IfcUtil::ArgumentType arg_type = helper_fn_attribute_type($self, i);
		if (arg_type == IfcUtil::Argument_LOGICAL) {
			self->set_attribute_value(i, v);	
		} else {
			throw IfcParse::IfcException("Attribute not set");
		}
	}

	void setArgumentAsDouble(unsigned int i, double v) {
		IfcUtil::ArgumentType arg_type = helper_fn_attribute_type($self, i);
		if (arg_type == IfcUtil::Argument_DOUBLE) {
			self->set_attribute_value(i, v);	
		} else {
			throw IfcParse::IfcException("Attribute not set");
		}
	}

	void setArgumentAsString(unsigned int i, const std::string& a) {
		IfcUtil::ArgumentType arg_type = helper_fn_attribute_type($self, i);
		if (arg_type == IfcUtil::Argument_STRING) {
			self->set_attribute_value(i, a);	
		} else if (arg_type == IfcUtil::Argument_ENUMERATION) {
			const IfcParse::enumeration_type* enum_type = $self->declaration().schema()->declaration_by_name($self->declaration().type())->as_entity()->
			attribute_by_index(i)->type_of_attribute()->as_named_type()->declared_type()->as_enumeration_type();
			self->set_attribute_value(i, EnumerationReference(enum_type, enum_type->lookup_enum_offset(a)));
		} else if (arg_type == IfcUtil::Argument_BINARY) {
			if (IfcUtil::valid_binary_string(a)) {
				boost::dynamic_bitset<> bits(a);
				self->set_attribute_value(i, bits);
			} else {
				throw IfcParse::IfcException("String not a valid binary representation");
			}
		} else {
			throw IfcParse::IfcException("Attribute not set");
		}
	}

	void setArgumentAsAggregateOfInt(unsigned int i, const std::vector<int>& v) {
		IfcUtil::ArgumentType arg_type = helper_fn_attribute_type($self, i);
		if (arg_type == IfcUtil::Argument_AGGREGATE_OF_INT) {
			self->set_attribute_value(i, v);
		} else {
			throw IfcParse::IfcException("Attribute not set");
		}
	}

	void setArgumentAsAggregateOfDouble(unsigned int i, const std::vector<double>& v) {
		IfcUtil::ArgumentType arg_type = helper_fn_attribute_type($self, i);
		if (arg_type == IfcUtil::Argument_AGGREGATE_OF_DOUBLE) {
			self->set_attribute_value(i, v);
		} else {
			throw IfcParse::IfcException("Attribute not set");
		}
	}

	void setArgumentAsAggregateOfString(unsigned int i, const std::vector<std::string>& v) {
		IfcUtil::ArgumentType arg_type = helper_fn_attribute_type($self, i);
		if (arg_type == IfcUtil::Argument_AGGREGATE_OF_STRING) {
			self->set_attribute_value(i, v);
		} else if (arg_type == IfcUtil::Argument_AGGREGATE_OF_BINARY) {
			std::vector< boost::dynamic_bitset<> > bits;
			bits.reserve(v.size());
			for (std::vector<std::string>::const_iterator it = v.begin(); it != v.end(); ++it) {
				if (IfcUtil::valid_binary_string(*it)) {
					bits.push_back(boost::dynamic_bitset<>(*it));
				} else {
					throw IfcParse::IfcException("String not a valid binary representation");
				}			
			}
			self->set_attribute_value(i, bits);
		} else {
			throw IfcParse::IfcException("Attribute not set");
		}
	}

	void setArgumentAsEntityInstance(unsigned int i, IfcUtil::IfcBaseClass* v) {
		IfcUtil::ArgumentType arg_type = helper_fn_attribute_type($self, i);
		if (arg_type == IfcUtil::Argument_ENTITY_INSTANCE) {
			self->set_attribute_value(i, v);
		} else {
			throw IfcParse::IfcException("Attribute not set");
		}
	}

	void setArgumentAsAggregateOfEntityInstance(unsigned int i, aggregate_of_instance::ptr v) {
		IfcUtil::ArgumentType arg_type = helper_fn_attribute_type($self, i);
		if (arg_type == IfcUtil::Argument_AGGREGATE_OF_ENTITY_INSTANCE) {
			self->set_attribute_value(i, v);
		} else {
			throw IfcParse::IfcException("Attribute not set");
		}
	}

	void setArgumentAsAggregateOfAggregateOfInt(unsigned int i, const std::vector< std::vector<int> >& v) {
		IfcUtil::ArgumentType arg_type = helper_fn_attribute_type($self, i);
		if (arg_type == IfcUtil::Argument_AGGREGATE_OF_AGGREGATE_OF_INT) {
			self->set_attribute_value(i, v);
		} else {
			throw IfcParse::IfcException("Attribute not set");
		}
	}

	void setArgumentAsAggregateOfAggregateOfDouble(unsigned int i, const std::vector< std::vector<double> >& v) {
		IfcUtil::ArgumentType arg_type = helper_fn_attribute_type($self, i);
		if (arg_type == IfcUtil::Argument_AGGREGATE_OF_AGGREGATE_OF_DOUBLE) {
			self->set_attribute_value(i, v);
		} else {
			throw IfcParse::IfcException("Attribute not set");
		}
	}

	void setArgumentAsAggregateOfAggregateOfEntityInstance(unsigned int i, aggregate_of_aggregate_of_instance::ptr v) {
		IfcUtil::ArgumentType arg_type = helper_fn_attribute_type($self, i);
		if (arg_type == IfcUtil::Argument_AGGREGATE_OF_AGGREGATE_OF_ENTITY_INSTANCE) {
			self->set_attribute_value(i, v);
		} else {
			throw IfcParse::IfcException("Attribute not set");
		}
	}
}

// Expose FileDescription and FileName header entities
// to make them readable even if they were not filled properly before.
// Though it is invalid IFC, technically.
// FileSchema is not exposed as IFC file won't load if it's invalid.

%extend IfcParse::FileDescription {
    AttributeValue description() const { return $self->getArgument(0); }
    AttributeValue implementation_level() const { return $self->getArgument(1); }
};

%extend IfcParse::FileName {
    AttributeValue name() const { return $self->getArgument(0); }
    AttributeValue time_stamp() const { return $self->getArgument(1); }
    AttributeValue author() const { return $self->getArgument(2); }
    AttributeValue organization() const { return $self->getArgument(3); }
    AttributeValue preprocessor_version() const { return $self->getArgument(4); }
    AttributeValue originating_system() const { return $self->getArgument(5); }
    AttributeValue authorization() const { return $self->getArgument(6); }
};

%extend IfcParse::IfcSpfHeader {
	%pythoncode %{
        # Hide the getters with read-only property implementations
        file_description = property(file_description)
        file_name = property(file_name)
        file_schema = property(file_schema)
	%}
};

%extend IfcParse::FileDescription {
	%pythoncode %{
        # Hide the getters with read-write property implementations
        description = property(description, description)
        implementation_level = property(implementation_level, implementation_level)
	%}
};

%extend IfcParse::FileName {
	%pythoncode %{
        name = property(name, name)
        time_stamp = property(time_stamp, time_stamp)
        author = property(author, author)
        organization = property(organization, organization)
        preprocessor_version = property(preprocessor_version, preprocessor_version)
        originating_system = property(originating_system, originating_system)
        authorization = property(authorization, authorization)
	%}
};

%extend IfcParse::FileSchema {
	%pythoncode %{
        # Hide the getters with read-write property implementations
        schema_identifiers = property(schema_identifiers, schema_identifiers)
	%}
};

%include "../ifcparse/ifc_parse_api.h"
%include "../ifcparse/IfcSpfHeader.h"
%include "../ifcparse/IfcFile.h"
%include "../ifcparse/IfcBaseClass.h"
%include "../ifcparse/IfcSchema.h"

// The IfcFile* returned by open() is to be freed by SWIG/Python
%newobject open;
%newobject read;
%newobject parse_ifcxml;

%inline %{
	IfcParse::IfcFile* open(const std::string& fn) {
		IfcParse::IfcFile* f;
		Py_BEGIN_ALLOW_THREADS;
		f = new IfcParse::IfcFile(fn);
		Py_END_ALLOW_THREADS;
		return f;
	}

    IfcParse::IfcFile* read(const std::string& data) {
		char* copiedData = new char[data.length()];
		memcpy(copiedData, data.c_str(), data.length());
		IfcParse::IfcFile* f;
		Py_BEGIN_ALLOW_THREADS;
		f = new IfcParse::IfcFile((void *)copiedData, data.length());
		Py_END_ALLOW_THREADS;
		return f;
	}

	const char* version() {
		return IFCOPENSHELL_VERSION;
	}

	IfcUtil::IfcBaseClass* new_IfcBaseClass(const std::string& schema_identifier, const std::string& name) {
		const IfcParse::schema_definition* schema = IfcParse::schema_by_name(schema_identifier);
		const IfcParse::declaration* decl = schema->declaration_by_name(name);
        IfcEntityInstanceData data(storage_t(decl->as_entity() ? decl->as_entity()->attribute_count() : 1));
		return schema->instantiate(decl, std::move(data));
	}
%}

%extend IfcParse::named_type {
	%pythoncode %{
		def __repr__(self):
			return repr(self.declared_type())
	%}
}

%extend IfcParse::simple_type {
	%pythoncode %{
		def __repr__(self):
			return "<%s>" % self.declared_type()
	%}
}

%extend IfcParse::aggregation_type {
	std::string type_of_aggregation_string() const {
		static const char* const aggr_strings[] = {"array", "bag", "list", "set"};
		return aggr_strings[(int) $self->type_of_aggregation()];
	}
	%pythoncode %{
		def __repr__(self):
			format_bound = lambda i: "?" if i == -1 else str(i)
			return "<%s [%s:%s] of %r>" % (
				self.type_of_aggregation_string(),
				format_bound(self.bound1()),
				format_bound(self.bound2()),
				self.type_of_element()
			)
	%}
}

%extend IfcParse::type_declaration {
	%pythoncode %{
		def __repr__(self):
			return "<type %s: %r>" % (self.name(), self.declared_type())
	%}
	std::vector<std::string> argument_types() {
		std::vector<std::string> r;
		auto at = IfcUtil::Argument_UNKNOWN;
		auto pt = $self->declared_type();
		if (pt) {
			at = IfcUtil::from_parameter_type(pt);
		}
		r.push_back(IfcUtil::ArgumentTypeToString(at));
		return r;
	}
}

%extend IfcParse::select_type {
	%pythoncode %{
		def __repr__(self):
			return "<select %s: (%s)>" % (self.name(), " | ".join(map(repr, self.select_list())))
	%}
}

%extend IfcParse::enumeration_type {
	%pythoncode %{
		def __repr__(self):
			return "<enumeration %s: (%s)>" % (self.name(), ", ".join(self.enumeration_items()))
	%}
	std::vector<std::string> argument_types() {
		std::vector<std::string> r;
		r.push_back(IfcUtil::ArgumentTypeToString(IfcUtil::Argument_STRING));
		return r;
	}
}

%extend IfcParse::attribute {
	%pythoncode %{
		def __repr__(self):
			return "<attribute %s%s: %s>" % (self.name(), "?" if self.optional() else "", self.type_of_attribute())
	%}
}

%extend IfcParse::inverse_attribute {
	std::string type_of_aggregation_string() const {
		static const char* const aggr_strings[] = {"bag", "set", ""};
		return aggr_strings[(int) $self->type_of_aggregation()];
	}
	%pythoncode %{
		def __repr__(self):
			format_bound = lambda i: "?" if i == -1 else str(i)
			return "<inverse %s: %s [%s:%s] of %r for %r>" % (
				self.name(),
				self.type_of_aggregation_string(),
				format_bound(self.bound1()),
				format_bound(self.bound2()),
				self.entity_reference(),
				self.attribute_reference()
			)
	%}
}

%extend IfcParse::entity {
	%pythoncode %{
		def __repr__(self):
			return "<entity %s>" % (self.name())
	%}
	std::vector<std::string> argument_types() {
		size_t i = 0;
		std::vector<std::string> r;
		for (auto& attr : $self->all_attributes()) {
			auto at = IfcUtil::Argument_UNKNOWN;
			auto pt = attr->type_of_attribute();
			if ($self->derived()[i++]) {
				at = IfcUtil::Argument_DERIVED;
			} else if (!pt) {
				at = IfcUtil::Argument_UNKNOWN;
			} else {
				at = IfcUtil::from_parameter_type(pt);
			}
			r.push_back(IfcUtil::ArgumentTypeToString(at));
		}
		return r;
	}
}

%extend IfcParse::schema_definition {
	%pythoncode %{
		def __repr__(self):
			return "<schema %s>" % (self.name())
	%}
}

%{
	static std::stringstream ifcopenshell_log_stream;
%}
%init %{
	Logger::SetOutput(0, &ifcopenshell_log_stream);
%}
%inline %{
	std::string get_log() {
		std::string log = ifcopenshell_log_stream.str();
		ifcopenshell_log_stream.str("");
		return log;
	}
	void turn_on_detailed_logging() {
		Logger::SetOutput(&std::cout, &std::cout);
		Logger::Verbosity(Logger::LOG_DEBUG);
	}
	void turn_off_detailed_logging() {
		Logger::SetOutput(0, &ifcopenshell_log_stream);
		Logger::Verbosity(Logger::LOG_WARNING);
	}
	void set_log_format_json() {
		ifcopenshell_log_stream.str("");
		Logger::OutputFormat(Logger::FMT_JSON);
	}
	void set_log_format_text() {
		ifcopenshell_log_stream.str("");
		Logger::OutputFormat(Logger::FMT_PLAIN);
	}
%}

%{
	PyObject* get_info_cpp(IfcUtil::IfcBaseClass* v);

	// @todo refactor this to remove duplication with the typemap. 
	// except this is calls the above function in case of instances.
	PyObject* convert_cpp_attribute_to_python(AttributeValue arg) {
		return arg.array_->apply_visitor([](auto& v){
			using U = std::decay_t<decltype(v)>;
            if constexpr (is_std_vector_vector_v<U>) {
                return pythonize_vector2(v);
            } else if constexpr (is_std_vector_v<U>) {
				return pythonize_vector(v);
            } else if constexpr (std::is_same_v<U, EnumerationReference>) {
                return pythonize(std::string(v.value()));
			} else if constexpr (std::is_same_v<U, Derived>) {
				if (feature_use_attribute_value_derived) {
					return SWIG_NewPointerObj(new attribute_value_derived, SWIGTYPE_p_attribute_value_derived, SWIG_POINTER_OWN);
				} else {
					Py_INCREF(Py_None);
					return static_cast<PyObject*>(Py_None); 
				}
			} else if constexpr (std::is_same_v<U, IfcUtil::IfcBaseClass*>) {
				return get_info_cpp(v);
			} else if constexpr (std::is_same_v<U, aggregate_of_instance::ptr>) {
				auto r = PyTuple_New(v->size());
				for (unsigned i = 0; i < v->size(); ++i) {
					PyTuple_SetItem(r, i, get_info_cpp((*v)[i]));
				}
				return r;
			} else if constexpr (std::is_same_v<U, aggregate_of_aggregate_of_instance::ptr>) {
				auto rs = PyTuple_New(v->size());
				for (auto it = v->begin(); it != v->end(); ++it) {
					auto v_i = it;
					auto r = PyTuple_New(v_i->size());
					for (unsigned i = 0; i < v_i->size(); ++i) {
						PyTuple_SetItem(r, i, get_info_cpp((*v_i)[i]));
					}
					PyTuple_SetItem(rs, std::distance(v->begin(), it), r);
				}
				return rs;
            } else if constexpr (std::is_same_v<U, empty_aggregate_t> || std::is_same_v<U, empty_aggregate_of_aggregate_t> || std::is_same_v<U, Blank>) {
                Py_INCREF(Py_None);
				return static_cast<PyObject*>(Py_None); 
            } else {
				return pythonize(v);
			}
		}, arg.index_);
	}
%}
%inline %{
	PyObject* get_info_cpp(IfcUtil::IfcBaseClass* v) {
		PyObject *d = PyDict_New();

		if (v->declaration().as_entity()) {
			const std::vector<const IfcParse::attribute*> attrs = v->declaration().as_entity()->all_attributes();
			std::vector<const IfcParse::attribute*>::const_iterator it = attrs.begin();
			auto dit = v->declaration().as_entity()->derived().begin();
			for (; it != attrs.end(); ++it, ++dit) {
				const std::string& name_cpp = (*it)->name();
				auto name_py = pythonize(name_cpp);
				auto attr_type = *dit
					? IfcUtil::Argument_DERIVED
					: IfcUtil::from_parameter_type((*it)->type_of_attribute());
				auto value_cpp = v->data().get_attribute_value(std::distance(attrs.begin(), it));
				auto value_py = convert_cpp_attribute_to_python(value_cpp);
				PyDict_SetItem(d, name_py, value_py);
				Py_DECREF(name_py);
				Py_DECREF(value_py);
			}

			const std::string& id_cpp = "id";
			auto id_py = pythonize(id_cpp);
			auto id_v_py = pythonize(v->as<IfcUtil::IfcBaseEntity>()->id());
			PyDict_SetItem(d, id_py, id_v_py);
			Py_DECREF(id_py);
			Py_DECREF(id_v_py);
		} else {
			const std::string& name_cpp = "wrappedValue";
			auto name_py = pythonize(name_cpp);
			auto value_cpp = v->data().get_attribute_value(0);
			auto value_py = convert_cpp_attribute_to_python(value_cpp);
			PyDict_SetItem(d, name_py, value_py);
			Py_DECREF(name_py);
			Py_DECREF(value_py);
		}

		// @todo type and id can be static?
		const std::string& type_cpp = "type";
		auto type_py = pythonize(type_cpp);
		const std::string& type_v_cpp = v->declaration().name();
		auto type_v_py = pythonize(type_v_cpp);
		PyDict_SetItem(d, type_py, type_v_py);
		Py_DECREF(type_py);
		Py_DECREF(type_v_py);

		return d;
	}
%}

