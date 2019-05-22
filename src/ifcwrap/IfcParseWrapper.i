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
	IfcEntityList::ptr get_inverse(IfcUtil::IfcBaseClass* e) {
		return $self->getInverse(e->data().id(), 0, -1);
	}

	void write(const std::string& fn) {
		std::ofstream f(fn.c_str());
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
		if _newclass:
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

	std::string is_a() const {
		return self->declaration().name();
	}

	std::pair<IfcUtil::ArgumentType,Argument*> get_argument(unsigned i) {
		return std::pair<IfcUtil::ArgumentType,Argument*>($self->data().getArgument(i)->type(), $self->data().getArgument(i));
	}

	std::pair<IfcUtil::ArgumentType,Argument*> get_argument(const std::string& a) {
		unsigned i = $self->declaration().as_entity()->attribute_index(a);
		return std::pair<IfcUtil::ArgumentType,Argument*>($self->data().getArgument(i)->type(), $self->data().getArgument(i));
	}

	bool __eq__(IfcUtil::IfcBaseClass* other) const {
		if ($self == other) {
			return true;
		}
		if (!$self->declaration().as_entity() || !other->declaration().as_entity()) {
			/// @todo
			return false;
		} else {
			IfcUtil::IfcBaseEntity* self_ = (IfcUtil::IfcBaseEntity*) self;
			IfcUtil::IfcBaseEntity* other_ = (IfcUtil::IfcBaseEntity*) other;
			return self_->data().id() == other_->data().id() && self_->data().file == other_->data().file;
		} 
	}

	std::string __repr__() const {
		return $self->data().toString();
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

	IfcEntityList::ptr get_inverse(const std::string& a) {
		const std::vector<const IfcParse::inverse_attribute*> attrs = $self->declaration().as_entity()->all_inverse_attributes();
		std::vector<const IfcParse::inverse_attribute*>::const_iterator it = attrs.begin();
		for (; it != attrs.end(); ++it) {
			if ((*it)->name() == a) {
				return self->data().getInverse(
					(*it)->entity_reference(),
					(*it)->entity_reference()->attribute_index((*it)->attribute_reference()));
			}
		}
		throw IfcParse::IfcException(a + " not found on " + $self->declaration().name());
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

	void setArgumentAsAggregateOfEntityInstance(unsigned int i, IfcEntityList::ptr v) {
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

	void setArgumentAsAggregateOfAggregateOfEntityInstance(unsigned int i, IfcEntityListList::ptr v) {
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
		if _newclass:
			# Hide the getters with read-only property implementations
			file_description = property(file_description)
			file_name = property(file_name)
			file_schema = property(file_schema)
	%}
};

%extend IfcParse::FileDescription {
	%pythoncode %{
		if _newclass:
			# Hide the getters with read-write property implementations
			__swig_getmethods__["description"] = description
			__swig_setmethods__["description"] = description
			description = property(description, description)
			__swig_getmethods__["implementation_level"] = implementation_level
			__swig_setmethods__["implementation_level"] = implementation_level
			implementation_level = property(implementation_level, implementation_level)
	%}
};

%extend IfcParse::FileName {
	%pythoncode %{
		if _newclass:
			# Hide the getters with read-write property implementations
			__swig_getmethods__["name"] = name
			__swig_setmethods__["name"] = name
			name = property(name, name)
			__swig_getmethods__["time_stamp"] = time_stamp
			__swig_setmethods__["time_stamp"] = time_stamp
			time_stamp = property(time_stamp, time_stamp)
			__swig_getmethods__["author"] = author
			__swig_setmethods__["author"] = author
			author = property(author, author)
			__swig_getmethods__["organization"] = organization
			__swig_setmethods__["organization"] = organization
			organization = property(organization, organization)
			__swig_getmethods__["preprocessor_version"] = preprocessor_version
			__swig_setmethods__["preprocessor_version"] = preprocessor_version
			preprocessor_version = property(preprocessor_version, preprocessor_version)
			__swig_getmethods__["originating_system"] = originating_system
			__swig_setmethods__["originating_system"] = originating_system
			originating_system = property(originating_system, originating_system)
			__swig_getmethods__["authorization"] = authorization
			__swig_setmethods__["authorization"] = authorization
			authorization = property(authorization, authorization)
	%}
};

%extend IfcParse::FileSchema {
	%pythoncode %{
		if _newclass:
			# Hide the getters with read-write property implementations
			__swig_getmethods__["schema_identifiers"] = schema_identifiers
			__swig_setmethods__["schema_identifiers"] = schema_identifiers
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
%}

