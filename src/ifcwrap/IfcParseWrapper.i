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
%rename("_set_argument") setArgument;
%rename("__repr__") toString;
%rename("entity_instance") IfcLateBoundEntity;
%rename("file") IfcFile;

%typemap(typecheck,precedence=SWIG_TYPECHECK_INTEGER) IfcEntityList::ptr {
   $1 = (PySequence_Check($input) && !PyUnicode_Check($input) && !PyString_Check($input)) ? 1 : 0;
}

%typemap(in) IfcEntityList::ptr {
	if (PySequence_Check($input)) {
		$1 = IfcEntityList::ptr(new IfcEntityList());
		for(Py_ssize_t i = 0; i < PySequence_Size($input); ++i) {
			PyObject* obj = PySequence_GetItem($input, i);
			if (obj) {
				void *arg = 0;
				int res = SWIG_ConvertPtr(obj, &arg, SWIGTYPE_p_IfcParse__IfcLateBoundEntity, 0);
				if (!SWIG_IsOK(res)) {
					SWIG_exception_fail(SWIG_ArgError(res), "Sequence element not of type IfcParse::IfcLateBoundEntity*"); 
				} else {
					$1->push(reinterpret_cast<IfcParse::IfcLateBoundEntity*>(arg));
				}
			}
		}
	} else {
		SWIG_exception(SWIG_RuntimeError,"Unknown argument type");
	}
}

%typemap(out) IfcEntityList::ptr {
	const unsigned size = $1 ? $1->size() : 0;
	$result = PyList_New(size);
	for (unsigned i = 0; i < size; ++i) {
		PyObject *o = SWIG_NewPointerObj(SWIG_as_voidptr((*$1)[i]), SWIGTYPE_p_IfcParse__IfcLateBoundEntity, 0);
		PyList_SetItem($result,i,o);
	}
}

%typemap(out) IfcUtil::ArgumentType {
	$result = SWIG_Python_str_FromChar(IfcUtil::ArgumentTypeToString($1));
}

%typemap(out) std::pair<IfcUtil::ArgumentType, Argument*> {
	// The SWIG %exception directive does not take care
	// of our typemap. So the argument conversion block
	// is wrapped in a try-catch block manually.
	try {
	const Argument& arg = *($1.second);
	const IfcUtil::ArgumentType type = $1.first;
	if (arg.isNull() || type == IfcUtil::Argument_DERIVED) {
		Py_INCREF(Py_None);
		$result = Py_None;
	} else {
	switch(type) {
		case IfcUtil::Argument_INT:
			$result = PyInt_FromLong((int)arg);
		break;
		case IfcUtil::Argument_BOOL:
			$result = PyBool_FromLong((bool)arg);
		break; 
		case IfcUtil::Argument_DOUBLE:
			$result = PyFloat_FromDouble(arg);
		break;
		case IfcUtil::Argument_ENUMERATION:
		case IfcUtil::Argument_STRING: {
			const std::string s = arg;
			$result = PyString_FromString(s.c_str());
		break; }
		case IfcUtil::Argument_VECTOR_INT: {
			const std::vector<int> v = arg;
			const unsigned size = v.size();
			$result = PyList_New(size);
			for (unsigned int i = 0; i < size; ++i) {
				PyList_SetItem($result,i,PyInt_FromLong(v[i]));
			}
		break; }
		case IfcUtil::Argument_VECTOR_DOUBLE: {
			const std::vector<double> v = arg;
			const unsigned size = v.size();
			$result = PyList_New(size);
			for (unsigned int i = 0; i < size; ++i) {
				PyList_SetItem($result,i,PyFloat_FromDouble(v[i]));
			}
		break; }
		case IfcUtil::Argument_VECTOR_STRING: {
			const std::vector<std::string> v = arg;
			const unsigned size = v.size();
			$result = PyList_New(size);
			for (unsigned int i = 0; i < size; ++i) {
				PyList_SetItem($result,i,PyString_FromString(v[i].c_str()));
			}
		break; }
		case IfcUtil::Argument_ENTITY: {
			IfcUtil::IfcBaseClass* e = arg;
			$result = SWIG_NewPointerObj(SWIG_as_voidptr(e), SWIGTYPE_p_IfcParse__IfcLateBoundEntity, 0);
		break; }
		case IfcUtil::Argument_ENTITY_LIST: {
			IfcEntityList::ptr es = arg;
			const unsigned size = es->size();
			$result = PyList_New(size);
			for (unsigned i = 0; i < size; ++i) {
				PyObject *o = SWIG_NewPointerObj(SWIG_as_voidptr((*es)[i]), SWIGTYPE_p_IfcParse__IfcLateBoundEntity, 0);
				PyList_SetItem($result,i,o);
			}
		break; }
		case IfcUtil::Argument_UNKNOWN:
		default:
			SWIG_exception(SWIG_RuntimeError,"Unknown argument type");
		break;
	}
	}
	} catch(IfcParse::IfcException& e) {
		SWIG_exception(SWIG_RuntimeError, e.what());
	} catch(...) {
		SWIG_exception(SWIG_RuntimeError, "An unknown error occurred");
	}
}

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
	std::vector<int> entity_names() const {
		std::vector<int> keys;
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
	%pythoncode %{
	set_argument = lambda self,x,y: self._set_argument(x) if y is None else self._set_argument(x,y)
	%}
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
%}