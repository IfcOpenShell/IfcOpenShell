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

#define invalid_argument(i, arg_name) { throw IfcParse::IfcException(IfcSchema::Type::GetAttributeName(self->entity->type(), (unsigned char)i) + " is not a valid type for '" + arg_name + "'"); }

%ignore IfcParse::IfcFile::Init;
%ignore IfcParse::IfcFile::entityByGuid;
%ignore IfcParse::IfcFile::register_inverse;
%ignore IfcParse::IfcFile::unregister_inverse;
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

%rename("by_id") entityById;
%rename("by_type") entitiesByType;
%rename("__len__") getArgumentCount;
%rename("get_argument_type") getArgumentType;
%rename("get_argument_name") getArgumentName;
%rename("get_argument_index") getArgumentIndex;
%rename("get_argument_optionality") getArgumentOptionality;
%rename("get_attribute_names") getAttributeNames;
%rename("get_inverse_attribute_names") getInverseAttributeNames;
%rename("entity_instance") IfcBaseClass;
%rename("file") IfcFile;
%rename("add") addEntity;
%rename("remove") removeEntity;

%extend IfcParse::IfcFile {
	IfcUtil::IfcBaseClass* by_guid(const std::string& guid) {
		return $self->entityByGuid(guid);
	}
	IfcEntityList::ptr get_inverse(IfcUtil::IfcBaseClass* e) {
		return $self->getInverse(e->entity->id(), IfcSchema::Type::UNDEFINED, -1);
	}

	void write(const std::string& fn) {
		std::ofstream f(fn.c_str());
		f << (*$self);
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
		std::transform($self->types_begin(), $self->types_end(), std::back_inserter(ts), IfcSchema::Type::ToString);
		return ts;
	}

	std::vector<std::string> types_with_super() const {
		const size_t n = std::distance($self->types_incl_super_begin(), $self->types_incl_super_end());
		std::vector<std::string> ts;
		ts.reserve(n);
		std::transform($self->types_incl_super_begin(), $self->types_incl_super_end(), std::back_inserter(ts), IfcSchema::Type::ToString);
		return ts;
	}

	%pythoncode %{
		if _newclass:
			# Hide the getters with read-only property implementations
			header = property(header)
	%}
}

%extend IfcUtil::IfcBaseClass {

	int get_attribute_category(const std::string& name) const {
		if (IfcSchema::Type::IsSimple($self->type())) {
			return name == "wrappedValue";
		}
		IfcUtil::IfcBaseEntity* self_ = (IfcUtil::IfcBaseEntity*) self; 
		const std::vector<std::string> names = self_->getAttributeNames();
		if (std::find(names.begin(), names.end(), name) != names.end()) {
			return 1;
		} else {
			const std::vector<std::string> names = self_->getInverseAttributeNames();
			if (std::find(names.begin(), names.end(), name) != names.end()) {
				return 2;
			} else {
				return 0;
			}
		}
	}

	// id() is defined on IfcBaseEntity and not on IfcBaseClass, in order
	// to expose it to the Python wrapper it is simply duplicated here.
	// Same applies to the two methods reimplemented below.
	int id() const {
		return $self->entity->id();
	}

	std::vector<std::string> getAttributeNames() const {
		if (IfcSchema::Type::IsSimple($self->type())) {
			return std::vector<std::string>(1, "wrappedValue");
		}
		IfcUtil::IfcBaseEntity* self_ = (IfcUtil::IfcBaseEntity*) self; 
		return self_->getAttributeNames();
	}

	std::vector<std::string> getInverseAttributeNames() const {
		if (IfcSchema::Type::IsSimple($self->type())) {
			return std::vector<std::string>(0);
		}
		IfcUtil::IfcBaseEntity* self_ = (IfcUtil::IfcBaseEntity*) self; 
		return self_->getInverseAttributeNames();
	}
	
	bool is_a(const std::string& s) {
		return self->is(IfcSchema::Type::FromString(boost::to_upper_copy(s)));
	}

	std::string is_a() const {
		return IfcSchema::Type::ToString(self->entity->type());
	}

	std::pair<IfcUtil::ArgumentType,Argument*> get_argument(unsigned i) {
		return std::pair<IfcUtil::ArgumentType,Argument*>($self->getArgumentType(i), $self->getArgument(i));
	}

	std::pair<IfcUtil::ArgumentType,Argument*> get_argument(const std::string& a) {
		unsigned i = IfcSchema::Type::GetAttributeIndex($self->type(), a);
		return std::pair<IfcUtil::ArgumentType,Argument*>($self->getArgumentType(i), $self->getArgument(i));
	}

	bool __eq__(IfcUtil::IfcBaseClass* other) const {
		if ($self == other) {
			return true;
		}
		if (IfcSchema::Type::IsSimple($self->type()) || IfcSchema::Type::IsSimple(other->type())) {
			/// @todo
			return false;
		} else {
			IfcUtil::IfcBaseEntity* self_ = (IfcUtil::IfcBaseEntity*) self;
			IfcUtil::IfcBaseEntity* other_ = (IfcUtil::IfcBaseEntity*) other;
			return self_->id() == other_->id() && self_->entity->file == other_->entity->file;
		} 
	}

	std::string __repr__() const {
		return $self->entity->toString();
	}

	// Just something to have a somewhat sensible value to hash
	size_t file_pointer() const {
		return reinterpret_cast<size_t>($self->entity->file);
	}

	unsigned get_argument_index(const std::string& a) const {
		return IfcSchema::Type::GetAttributeIndex(self->entity->type(), a);
	}

	IfcEntityList::ptr get_inverse(const std::string& a) {
		std::pair<IfcSchema::Type::Enum, unsigned> inv = IfcSchema::Type::GetInverseAttribute(self->entity->type(), a);
		return self->entity->getInverse(inv.first, inv.second);
	}

	void setArgumentAsNull(unsigned int i) {
		bool is_optional = IfcSchema::Type::GetAttributeOptional(self->entity->type(), (unsigned char)i);
		if (is_optional) {
			self->entity->setArgument(i, new IfcWrite::IfcWriteArgument());
		} else invalid_argument(i,"NULL");
	}

	void setArgumentAsInt(unsigned int i, int v) {
		IfcUtil::ArgumentType arg_type = IfcSchema::Type::GetAttributeType(self->entity->type(), (unsigned char)i);
		if (arg_type == IfcUtil::Argument_INT) {
			IfcWrite::IfcWriteArgument* arg = new IfcWrite::IfcWriteArgument();
			arg->set(v);
			self->entity->setArgument(i, arg);	
		} else if ( (arg_type == IfcUtil::Argument_BOOL) && ( (v == 0) || (v == 1) ) ) {
			IfcWrite::IfcWriteArgument* arg = new IfcWrite::IfcWriteArgument();
			arg->set(v == 1);
			self->entity->setArgument(i, arg);	
		} else invalid_argument(i,"INTEGER");
	}

	void setArgumentAsBool(unsigned int i, bool v) {
		IfcUtil::ArgumentType arg_type = IfcSchema::Type::GetAttributeType(self->entity->type(), (unsigned char)i);
		if (arg_type == IfcUtil::Argument_BOOL) {
			IfcWrite::IfcWriteArgument* arg = new IfcWrite::IfcWriteArgument();
			arg->set(v);
			self->entity->setArgument(i, arg);	
		} else invalid_argument(i,"BOOLEAN");
	}

	void setArgumentAsDouble(unsigned int i, double v) {
		IfcUtil::ArgumentType arg_type = IfcSchema::Type::GetAttributeType(self->entity->type(), (unsigned char)i);
		if (arg_type == IfcUtil::Argument_DOUBLE) {
			IfcWrite::IfcWriteArgument* arg = new IfcWrite::IfcWriteArgument();
			arg->set(v);
			self->entity->setArgument(i, arg);	
		} else invalid_argument(i,"REAL");
	}

	void setArgumentAsString(unsigned int i, const std::string& a) {
		IfcUtil::ArgumentType arg_type = IfcSchema::Type::GetAttributeType(self->entity->type(), (unsigned char)i);
		if (arg_type == IfcUtil::Argument_STRING) {
			IfcWrite::IfcWriteArgument* arg = new IfcWrite::IfcWriteArgument();
			arg->set(a);
			self->entity->setArgument(i, arg);	
		} else if (arg_type == IfcUtil::Argument_ENUMERATION) {
			std::pair<const char*, int> enum_data = IfcSchema::Type::GetEnumerationIndex(IfcSchema::Type::GetAttributeEntity(self->entity->type(), (unsigned char)i), a);
			IfcWrite::IfcWriteArgument* arg = new IfcWrite::IfcWriteArgument();
			arg->set(IfcWrite::IfcWriteArgument::EnumerationReference(enum_data.second, enum_data.first));
			self->entity->setArgument(i, arg);
		} else if (arg_type == IfcUtil::Argument_BINARY) {
			if (IfcUtil::valid_binary_string(a)) {
				boost::dynamic_bitset<> bits(a);
				IfcWrite::IfcWriteArgument* arg = new IfcWrite::IfcWriteArgument();
				arg->set(bits);
				self->entity->setArgument(i, arg);
			} else {
				throw IfcParse::IfcException("String not a valid binary representation");
			}
		} else invalid_argument(i,"STRING");
	}

	void setArgumentAsAggregateOfInt(unsigned int i, const std::vector<int>& v) {
		IfcUtil::ArgumentType arg_type = IfcSchema::Type::GetAttributeType(self->entity->type(), (unsigned char)i);
		if (arg_type == IfcUtil::Argument_AGGREGATE_OF_INT) {
			IfcWrite::IfcWriteArgument* arg = new IfcWrite::IfcWriteArgument();
			arg->set(v);
			self->entity->setArgument(i, arg);
		} else invalid_argument(i,"AGGREGATE OF INT");
	}

	void setArgumentAsAggregateOfDouble(unsigned int i, const std::vector<double>& v) {
		IfcUtil::ArgumentType arg_type = IfcSchema::Type::GetAttributeType(self->entity->type(), (unsigned char)i);
		if (arg_type == IfcUtil::Argument_AGGREGATE_OF_DOUBLE) {
			IfcWrite::IfcWriteArgument* arg = new IfcWrite::IfcWriteArgument();
			arg->set(v);
			self->entity->setArgument(i, arg);
		} else invalid_argument(i,"AGGREGATE OF DOUBLE");
	}

	void setArgumentAsAggregateOfString(unsigned int i, const std::vector<std::string>& v) {
		IfcUtil::ArgumentType arg_type = IfcSchema::Type::GetAttributeType(self->entity->type(), (unsigned char)i);
		if (arg_type == IfcUtil::Argument_AGGREGATE_OF_STRING) {
			IfcWrite::IfcWriteArgument* arg = new IfcWrite::IfcWriteArgument();
			arg->set(v);
			self->entity->setArgument(i, arg);
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
			self->entity->setArgument(i, arg);
		} else invalid_argument(i,"AGGREGATE OF STRING");
	}

	void setArgumentAsEntityInstance(unsigned int i, IfcUtil::IfcBaseClass* v) {
		IfcUtil::ArgumentType arg_type = IfcSchema::Type::GetAttributeType(self->entity->type(), (unsigned char)i);
		if (arg_type == IfcUtil::Argument_ENTITY_INSTANCE) {
			IfcWrite::IfcWriteArgument* arg = new IfcWrite::IfcWriteArgument();
			arg->set(v);
			self->entity->setArgument(i, arg);
		} else invalid_argument(i,"ENTITY INSTANCE");
	}

	void setArgumentAsAggregateOfEntityInstance(unsigned int i, IfcEntityList::ptr v) {
		IfcUtil::ArgumentType arg_type = IfcSchema::Type::GetAttributeType(self->entity->type(), (unsigned char)i);
		if (arg_type == IfcUtil::Argument_AGGREGATE_OF_ENTITY_INSTANCE) {
			IfcWrite::IfcWriteArgument* arg = new IfcWrite::IfcWriteArgument();
			arg->set(v);
			self->entity->setArgument(i, arg);
		} else invalid_argument(i,"AGGREGATE OF ENTITY INSTANCE");
	}

	void setArgumentAsAggregateOfAggregateOfInt(unsigned int i, const std::vector< std::vector<int> >& v) {
		IfcUtil::ArgumentType arg_type = IfcSchema::Type::GetAttributeType(self->entity->type(), (unsigned char)i);
		if (arg_type == IfcUtil::Argument_AGGREGATE_OF_AGGREGATE_OF_INT) {
			IfcWrite::IfcWriteArgument* arg = new IfcWrite::IfcWriteArgument();
			arg->set(v);
			self->entity->setArgument(i, arg);
		} else invalid_argument(i,"AGGREGATE OF AGGREGATE OF INT");
	}

	void setArgumentAsAggregateOfAggregateOfDouble(unsigned int i, const std::vector< std::vector<double> >& v) {
		IfcUtil::ArgumentType arg_type = IfcSchema::Type::GetAttributeType(self->entity->type(), (unsigned char)i);
		if (arg_type == IfcUtil::Argument_AGGREGATE_OF_AGGREGATE_OF_DOUBLE) {
			IfcWrite::IfcWriteArgument* arg = new IfcWrite::IfcWriteArgument();
			arg->set(v);
			self->entity->setArgument(i, arg);
		} else invalid_argument(i,"AGGREGATE OF AGGREGATE OF DOUBLE");
	}

	void setArgumentAsAggregateOfAggregateOfEntityInstance(unsigned int i, IfcEntityListList::ptr v) {
		IfcUtil::ArgumentType arg_type = IfcSchema::Type::GetAttributeType(self->entity->type(), (unsigned char)i);
		if (arg_type == IfcUtil::Argument_AGGREGATE_OF_AGGREGATE_OF_ENTITY_INSTANCE) {
			IfcWrite::IfcWriteArgument* arg = new IfcWrite::IfcWriteArgument();
			arg->set(v);
			self->entity->setArgument(i, arg);
		} else invalid_argument(i,"AGGREGATE OF AGGREGATE OF ENTITY INSTANCE");
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

// The IfcFile* returned by open() is to be freed by SWIG/Python
%newobject open;
%newobject read;

%inline %{
	IfcParse::IfcFile* open(const std::string& fn) {
		IfcParse::IfcFile* f = new IfcParse::IfcFile();
		f->Init(fn);
		return f;
	}
    IfcParse::IfcFile* read(const std::string& data) {
		char* copiedData = new char[data.length()];
		memcpy(copiedData, data.c_str(), data.length());
		IfcParse::IfcFile* f = new IfcParse::IfcFile();
		f->Init((void *)copiedData, data.length());
		return f;
	}
	const char* schema_identifier() {
		return IfcSchema::Identifier;
	}

	const char* version() {
		return IFCOPENSHELL_VERSION;
	}

	std::string get_supertype(std::string n) {
		boost::to_upper(n);
		IfcSchema::Type::Enum t = IfcSchema::Type::FromString(n);
		if (IfcSchema::Type::Parent(t)) {
			return IfcSchema::Type::ToString(*IfcSchema::Type::Parent(t));
		} else {
			return "";
		}
	}

	IfcUtil::IfcBaseClass* new_IfcBaseClass(const std::string& s) {
		IfcSchema::Type::Enum ty = IfcSchema::Type::FromString(boost::to_upper_copy(s));
		IfcEntityInstanceData* data = new IfcEntityInstanceData(ty);
		data->setArgument(IfcSchema::Type::GetAttributeCount(ty) - 1, new IfcWrite::IfcWriteArgument());
		IfcSchema::Type::PopulateDerivedFields(data);
		return IfcSchema::SchemaEntity(data);
	}
%}

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

