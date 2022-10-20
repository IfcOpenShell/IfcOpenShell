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
	IfcUtil::IfcBaseClass* by_guid(const std::string& guid) {
		return $self->instance_by_guid(guid);
	}
	
	aggregate_of_instance::ptr get_inverse(IfcUtil::IfcBaseClass* e) {
		return $self->getInverse(e->data().id(), 0, -1);
	}

	std::vector<int> get_inverse_indices(IfcUtil::IfcBaseClass* e) {
		return $self->get_inverse_indices(e->data().id());
	}

	int get_total_inverses(IfcUtil::IfcBaseClass* e) {
		return $self->getTotalInverses(e->data().id());
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

	std::vector<std::string> types_with_super() const {
		const size_t n = std::distance($self->types_incl_super_begin(), $self->types_incl_super_end());
		std::vector<std::string> ts;
		ts.reserve(n);
		std::transform($self->types_incl_super_begin(), $self->types_incl_super_end(), std::back_inserter(ts), helper_fn_declaration_get_name);
		return ts;
	}

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
		return $self->data().id();
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

	std::pair<IfcUtil::ArgumentType,Argument*> get_argument(unsigned i) {
		return std::pair<IfcUtil::ArgumentType,Argument*>($self->data().getArgument(i)->type(), $self->data().getArgument(i));
	}

	std::pair<IfcUtil::ArgumentType,Argument*> get_argument(const std::string& a) {
		unsigned i = $self->declaration().as_entity()->attribute_index(a);
		return std::pair<IfcUtil::ArgumentType,Argument*>($self->data().getArgument(i)->type(), $self->data().getArgument(i));
	}

	bool __eq__(IfcUtil::IfcBaseClass* other) const {
		return $self->identity() == other->identity();
	}

	std::string __repr__() const {
		return $self->data().toString();
	}

	std::string to_string(bool valid_spf) const {
		return $self->data().toString(valid_spf);
	}

	// Just something to have a somewhat sensible value to hash
	size_t file_pointer() const {
		return reinterpret_cast<size_t>($self->data().file);
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
			self->data().setArgument(i, new IfcWrite::IfcWriteArgument());
		} else {
			throw IfcParse::IfcException("Attribute not set");
		}
	}

	void setArgumentAsInt(unsigned int i, int v) {
		IfcUtil::ArgumentType arg_type = helper_fn_attribute_type($self, i);
		if (arg_type == IfcUtil::Argument_INT) {
			IfcWrite::IfcWriteArgument* arg = new IfcWrite::IfcWriteArgument();
			arg->set(v);
			self->data().setArgument(i, arg);	
		} else if ( (arg_type == IfcUtil::Argument_BOOL) && ( (v == 0) || (v == 1) ) ) {
			IfcWrite::IfcWriteArgument* arg = new IfcWrite::IfcWriteArgument();
			arg->set(v == 1);
			self->data().setArgument(i, arg);	
		} else {
			throw IfcParse::IfcException("Attribute not set");
		}
	}

	void setArgumentAsBool(unsigned int i, bool v) {
		IfcUtil::ArgumentType arg_type = helper_fn_attribute_type($self, i);
		if (arg_type == IfcUtil::Argument_BOOL) {
			IfcWrite::IfcWriteArgument* arg = new IfcWrite::IfcWriteArgument();
			arg->set(v);
			self->data().setArgument(i, arg);	
		} else {
			throw IfcParse::IfcException("Attribute not set");
		}
	}

	void setArgumentAsLogical(unsigned int i, boost::logic::tribool v) {
		IfcUtil::ArgumentType arg_type = helper_fn_attribute_type($self, i);
		if (arg_type == IfcUtil::Argument_LOGICAL) {
			IfcWrite::IfcWriteArgument* arg = new IfcWrite::IfcWriteArgument();
			arg->set(v);
			self->data().setArgument(i, arg);	
		} else {
			throw IfcParse::IfcException("Attribute not set");
		}
	}

	void setArgumentAsDouble(unsigned int i, double v) {
		IfcUtil::ArgumentType arg_type = helper_fn_attribute_type($self, i);
		if (arg_type == IfcUtil::Argument_DOUBLE) {
			IfcWrite::IfcWriteArgument* arg = new IfcWrite::IfcWriteArgument();
			arg->set(v);
			self->data().setArgument(i, arg);	
		} else {
			throw IfcParse::IfcException("Attribute not set");
		}
	}

	void setArgumentAsString(unsigned int i, const std::string& a) {
		IfcUtil::ArgumentType arg_type = helper_fn_attribute_type($self, i);
		if (arg_type == IfcUtil::Argument_STRING) {
			IfcWrite::IfcWriteArgument* arg = new IfcWrite::IfcWriteArgument();
			arg->set(a);
			self->data().setArgument(i, arg);	
		} else if (arg_type == IfcUtil::Argument_ENUMERATION) {
			const IfcParse::enumeration_type* enum_type = $self->declaration().schema()->declaration_by_name($self->declaration().type())->as_entity()->
			attribute_by_index(i)->type_of_attribute()->as_named_type()->declared_type()->as_enumeration_type();
		
			std::vector<std::string>::const_iterator it = std::find(
				enum_type->enumeration_items().begin(), 
				enum_type->enumeration_items().end(), 
				a);
		
			if (it == enum_type->enumeration_items().end()) {
				throw IfcParse::IfcException(a + " does not name a valid item for " + enum_type->name());
			}

			IfcWrite::IfcWriteArgument* arg = new IfcWrite::IfcWriteArgument();
			arg->set(IfcWrite::IfcWriteArgument::EnumerationReference(it - enum_type->enumeration_items().begin(), it->c_str()));
			self->data().setArgument(i, arg);
		} else if (arg_type == IfcUtil::Argument_BINARY) {
			if (IfcUtil::valid_binary_string(a)) {
				boost::dynamic_bitset<> bits(a);
				IfcWrite::IfcWriteArgument* arg = new IfcWrite::IfcWriteArgument();
				arg->set(bits);
				self->data().setArgument(i, arg);
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
			IfcWrite::IfcWriteArgument* arg = new IfcWrite::IfcWriteArgument();
			arg->set(v);
			self->data().setArgument(i, arg);
		} else {
			throw IfcParse::IfcException("Attribute not set");
		}
	}

	void setArgumentAsAggregateOfDouble(unsigned int i, const std::vector<double>& v) {
		IfcUtil::ArgumentType arg_type = helper_fn_attribute_type($self, i);
		if (arg_type == IfcUtil::Argument_AGGREGATE_OF_DOUBLE) {
			IfcWrite::IfcWriteArgument* arg = new IfcWrite::IfcWriteArgument();
			arg->set(v);
			self->data().setArgument(i, arg);
		} else {
			throw IfcParse::IfcException("Attribute not set");
		}
	}

	void setArgumentAsAggregateOfString(unsigned int i, const std::vector<std::string>& v) {
		IfcUtil::ArgumentType arg_type = helper_fn_attribute_type($self, i);
		if (arg_type == IfcUtil::Argument_AGGREGATE_OF_STRING) {
			IfcWrite::IfcWriteArgument* arg = new IfcWrite::IfcWriteArgument();
			arg->set(v);
			self->data().setArgument(i, arg);
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
			IfcWrite::IfcWriteArgument* arg = new IfcWrite::IfcWriteArgument();
			arg->set(bits);
			self->data().setArgument(i, arg);
		} else {
			throw IfcParse::IfcException("Attribute not set");
		}
	}

	void setArgumentAsEntityInstance(unsigned int i, IfcUtil::IfcBaseClass* v) {
		IfcUtil::ArgumentType arg_type = helper_fn_attribute_type($self, i);
		if (arg_type == IfcUtil::Argument_ENTITY_INSTANCE) {
			IfcWrite::IfcWriteArgument* arg = new IfcWrite::IfcWriteArgument();
			arg->set(v);
			self->data().setArgument(i, arg);
		} else {
			throw IfcParse::IfcException("Attribute not set");
		}
	}

	void setArgumentAsAggregateOfEntityInstance(unsigned int i, aggregate_of_instance::ptr v) {
		IfcUtil::ArgumentType arg_type = helper_fn_attribute_type($self, i);
		if (arg_type == IfcUtil::Argument_AGGREGATE_OF_ENTITY_INSTANCE) {
			IfcWrite::IfcWriteArgument* arg = new IfcWrite::IfcWriteArgument();
			arg->set(v);
			self->data().setArgument(i, arg);
		} else {
			throw IfcParse::IfcException("Attribute not set");
		}
	}

	void setArgumentAsAggregateOfAggregateOfInt(unsigned int i, const std::vector< std::vector<int> >& v) {
		IfcUtil::ArgumentType arg_type = helper_fn_attribute_type($self, i);
		if (arg_type == IfcUtil::Argument_AGGREGATE_OF_AGGREGATE_OF_INT) {
			IfcWrite::IfcWriteArgument* arg = new IfcWrite::IfcWriteArgument();
			arg->set(v);
			self->data().setArgument(i, arg);
		} else {
			throw IfcParse::IfcException("Attribute not set");
		}
	}

	void setArgumentAsAggregateOfAggregateOfDouble(unsigned int i, const std::vector< std::vector<double> >& v) {
		IfcUtil::ArgumentType arg_type = helper_fn_attribute_type($self, i);
		if (arg_type == IfcUtil::Argument_AGGREGATE_OF_AGGREGATE_OF_DOUBLE) {
			IfcWrite::IfcWriteArgument* arg = new IfcWrite::IfcWriteArgument();
			arg->set(v);
			self->data().setArgument(i, arg);
		} else {
			throw IfcParse::IfcException("Attribute not set");
		}
	}

	void setArgumentAsAggregateOfAggregateOfEntityInstance(unsigned int i, aggregate_of_aggregate_of_instance::ptr v) {
		IfcUtil::ArgumentType arg_type = helper_fn_attribute_type($self, i);
		if (arg_type == IfcUtil::Argument_AGGREGATE_OF_AGGREGATE_OF_ENTITY_INSTANCE) {
			IfcWrite::IfcWriteArgument* arg = new IfcWrite::IfcWriteArgument();
			arg->set(v);
			self->data().setArgument(i, arg);
		} else {
			throw IfcParse::IfcException("Attribute not set");
		}
	}
}

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
		IfcParse::IfcFile* f = new IfcParse::IfcFile(fn);
		return f;
	}

    IfcParse::IfcFile* read(const std::string& data) {
		char* copiedData = new char[data.length()];
		memcpy(copiedData, data.c_str(), data.length());
		IfcParse::IfcFile* f = new IfcParse::IfcFile((void *)copiedData, data.length());
		return f;
	}

	const char* version() {
		return IFCOPENSHELL_VERSION;
	}

	IfcUtil::IfcBaseClass* new_IfcBaseClass(const std::string& schema_identifier, const std::string& name) {
		const IfcParse::schema_definition* schema = IfcParse::schema_by_name(schema_identifier);
		const IfcParse::declaration* decl = schema->declaration_by_name(name);
		IfcEntityInstanceData* data = new IfcEntityInstanceData(decl);

		for (size_t i = 0; i < data->getArgumentCount(); ++i) {
			data->setArgument(i, new IfcWrite::IfcWriteArgument());
		}

		if (decl->as_entity()) {			
			const std::vector<bool>& derived = decl->as_entity()->derived();
			std::vector<bool>::const_iterator it = derived.begin();

			size_t index = 0;
			for (; it != derived.end(); ++it, ++index) {
				if (*it) {
					IfcWrite::IfcWriteArgument* arg = new IfcWrite::IfcWriteArgument();
					arg->set(IfcWrite::IfcWriteArgument::Derived());
					data->setArgument(index, arg);
				}
			}
		}
		
		return schema->instantiate(data);
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
	PyObject* convert_cpp_attribute_to_python(IfcUtil::ArgumentType type, Argument& arg) {
		if (!arg.isNull() && type != IfcUtil::Argument_DERIVED) {
		try {
		switch(type) {
			case IfcUtil::Argument_INT: {
				int v = arg;
				return pythonize(v);
			break; }
			case IfcUtil::Argument_BOOL: {
				bool v = arg;
				return pythonize(v);
			break; }
			case IfcUtil::Argument_LOGICAL: {
				boost::logic::tribool v = arg;
				return pythonize(v);
			break; }
			case IfcUtil::Argument_DOUBLE: {
				double v = arg;
				return pythonize(v);
			break; }
			case IfcUtil::Argument_ENUMERATION:
			case IfcUtil::Argument_STRING: {
				std::string v = arg;
				return pythonize(v);
			break; }
			case IfcUtil::Argument_BINARY: {
				boost::dynamic_bitset<> v = arg;
				return pythonize(v);
			break; }
			case IfcUtil::Argument_AGGREGATE_OF_INT: {
				std::vector<int> v = arg;
				return pythonize_vector(v);
			break; }
			case IfcUtil::Argument_AGGREGATE_OF_DOUBLE: {
				std::vector<double> v = arg;
				return pythonize_vector(v);
			break; }
			case IfcUtil::Argument_AGGREGATE_OF_STRING: {
				std::vector<std::string> v = arg;
				return pythonize_vector(v);
			break; }
			case IfcUtil::Argument_ENTITY_INSTANCE: {
				IfcUtil::IfcBaseClass* v = arg;
				return get_info_cpp(v);
			break; }
			case IfcUtil::Argument_AGGREGATE_OF_ENTITY_INSTANCE: {
				aggregate_of_instance::ptr v = arg;
				auto r = PyTuple_New(v->size());
				for (unsigned i = 0; i < v->size(); ++i) {
					PyTuple_SetItem(r, i, get_info_cpp((*v)[i]));
				}				
				return r;
			break; }
			case IfcUtil::Argument_AGGREGATE_OF_BINARY: {
				std::vector< boost::dynamic_bitset<> > v = arg;
				return pythonize_vector(v);
			break; }
			case IfcUtil::Argument_AGGREGATE_OF_AGGREGATE_OF_INT: {
				std::vector< std::vector<int> > v = arg;
				return pythonize_vector2(v);
			break; }
			case IfcUtil::Argument_AGGREGATE_OF_AGGREGATE_OF_DOUBLE: {
				std::vector< std::vector<double> > v = arg;
				return pythonize_vector2(v);
			break; }
			case IfcUtil::Argument_AGGREGATE_OF_AGGREGATE_OF_ENTITY_INSTANCE: {
				aggregate_of_aggregate_of_instance::ptr vs = arg;
				auto rs = PyTuple_New(vs->size());
				for (auto it = vs->begin(); it != vs->end(); ++it) {
					aggregate_of_instance::ptr v_i = arg;
					auto r = PyTuple_New(v_i->size());
					for (unsigned i = 0; i < v_i->size(); ++i) {
						PyTuple_SetItem(r, i, get_info_cpp((*v_i)[i]));
					}
					PyTuple_SetItem(rs, std::distance(vs->begin(), it), r);
				}				
				return rs;
			break; }
			case IfcUtil::Argument_EMPTY_AGGREGATE: {
				return PyTuple_New(0);
			break; }
		}
		} catch(...) {}
		}
		Py_INCREF(Py_None);
		return Py_None;
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
				auto value_cpp = v->data().getArgument(std::distance(attrs.begin(), it));
				auto value_py = convert_cpp_attribute_to_python(attr_type, *value_cpp);
				PyDict_SetItem(d, name_py, value_py);
				Py_DECREF(name_py);
				Py_DECREF(value_py);
			}

			const std::string& id_cpp = "id";
			auto id_py = pythonize(id_cpp);
			auto id_v_py = pythonize(v->data().id());
			PyDict_SetItem(d, id_py, id_v_py);
			Py_DECREF(id_py);
			Py_DECREF(id_v_py);
		} else {
			const std::string& name_cpp = "wrappedValue";
			auto name_py = pythonize(name_cpp);
			auto value_cpp = v->data().getArgument(0);
			auto value_py = convert_cpp_attribute_to_python(value_cpp->type(), *value_cpp);
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

