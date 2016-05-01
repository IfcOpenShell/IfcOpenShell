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

// Two class declarations to silence SWIG warning about base classes being
// undefined, the constructors are private so that SWIG does not wrap them
class IfcAbstractEntity {
private:
	IfcAbstractEntity();
};
namespace IfcUtil {
	class IfcBaseEntity {
	private:
		IfcBaseEntity();
	};
}

%ignore IfcParse::IfcLateBoundEntity::is;
%ignore IfcParse::IfcLateBoundEntity::type;
%ignore IfcParse::IfcLateBoundEntity::getArgument;
%ignore IfcParse::IfcLateBoundEntity::IfcLateBoundEntity(IfcAbstractEntity*);

%ignore IfcParse::IfcFile::Init;
%ignore IfcParse::IfcFile::entityById;
%ignore IfcParse::IfcFile::entityByGuid;
%ignore IfcParse::IfcFile::addEntity;
%ignore IfcParse::IfcFile::removeEntity;
%ignore IfcParse::IfcFile::traverse(IfcUtil::IfcBaseClass*, int);
%ignore IfcParse::IfcFile::traverse(IfcUtil::IfcBaseClass*);
%ignore operator<<;

%ignore IfcParse::FileDescription::FileDescription;
%ignore IfcParse::FileName::FileName;
%ignore IfcParse::FileSchema::FileSchema;
%ignore IfcParse::IfcFile::tokens;

%ignore IfcParse::IfcSpfHeader::IfcSpfHeader(IfcSpfLexer*);
%ignore IfcParse::IfcSpfHeader::lexer;
%ignore IfcParse::IfcSpfHeader::stream;
%ignore IfcParse::HeaderEntity::is;

%rename("by_type") entitiesByType;
%rename("__len__") getArgumentCount;
%rename("get_argument_type") getArgumentType;
%rename("get_argument_name") getArgumentName;
%rename("get_argument_index") getArgumentIndex;
%rename("get_argument_optionality") getArgumentOptionality;
%rename("get_attribute_names") getAttributeNames;
%rename("get_inverse_attribute_names") getInverseAttributeNames;
%rename("__repr__") toString;
%rename("entity_instance") IfcLateBoundEntity;
%rename("file") IfcFile;

%extend IfcParse::IfcFile {
	IfcParse::IfcLateBoundEntity* by_id(unsigned id) {
		return (IfcParse::IfcLateBoundEntity*) $self->entityById(id);
	}
	IfcParse::IfcLateBoundEntity* by_guid(const std::string& guid) {
		return (IfcParse::IfcLateBoundEntity*) $self->entityByGuid(guid);
	}
	IfcParse::IfcLateBoundEntity* add(IfcParse::IfcLateBoundEntity* e) {
		return (IfcParse::IfcLateBoundEntity*) $self->addEntity(e);
	}
	void remove(IfcParse::IfcLateBoundEntity* e) {
		$self->removeEntity(e);
	}
	IfcEntityList::ptr traverse(IfcParse::IfcLateBoundEntity* e, int max_level=-1) {
		return $self->traverse(e, max_level);
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
	%pythoncode %{
		if _newclass:
			# Hide the getters with read-only property implementations
			header = property(header)
	%}
}

%extend IfcParse::IfcLateBoundEntity {
	int get_attribute_category(const std::string& name) const {
		const std::vector<std::string> names = $self->getAttributeNames();
		if (std::find(names.begin(), names.end(), name) != names.end()) {
			return 1;
		} else {
			const std::vector<std::string> names = $self->getInverseAttributeNames();
			if (std::find(names.begin(), names.end(), name) != names.end()) {
				return 2;
			} else {
				return 0;
			}
		}
	}

	std::pair<IfcUtil::ArgumentType,Argument*> get_argument(unsigned i) {
		return std::pair<IfcUtil::ArgumentType,Argument*>($self->getArgumentType(i), $self->getArgument(i));
	}

	std::pair<IfcUtil::ArgumentType,Argument*> get_argument(const std::string& a) {
		unsigned i = IfcSchema::Type::GetAttributeIndex($self->type(), a);
		return std::pair<IfcUtil::ArgumentType,Argument*>($self->getArgumentType(i), $self->getArgument(i));
	}

	bool __eq__(IfcParse::IfcLateBoundEntity* other) const {
		if ($self == other) {
			return true;
		}
		return $self->id() == other->id() && $self->entity->file == other->entity->file;
	}

	// Just something to have a somewhat sensible value to hash
	size_t file_pointer() const {
		return reinterpret_cast<size_t>($self->entity->file);
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

%include "../ifcparse/IfcSpfHeader.h"
%include "../ifcparse/IfcFile.h"
%include "../ifcparse/IfcLateBoundEntity.h"

// The IfcFile* returned by open() is to be freed by SWIG/Python
%newobject open;

%inline %{
	IfcParse::IfcFile* open(const std::string& s) {
		IfcParse::IfcFile* f = new IfcParse::IfcFile(true);
		f->Init(s);
		return f;
	}

	const char* const schema_identifier() {
		return IfcSchema::Identifier;
	}

	const char* const version() {
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
%}