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

%include "std_vector.i"
%include "std_string.i"
%include "exception.i"

%ignore Ifc::IfcUntypedEntity::is;
%ignore Ifc::IfcUntypedEntity::type;
%ignore Ifc::IfcUntypedEntity::getArgument;
%ignore Ifc::IfcUntypedEntity::IfcUntypedEntity(IfcAbstractEntity);

%ignore IfcParse::IfcFile::Init;
%ignore IfcParse::IfcFile::EntityById;
%ignore IfcParse::IfcFile::EntityByGuid;
%ignore IfcParse::IfcFile::AddEntity;
%ignore operator<<;

%rename("by_type") EntitiesByType;
%rename("get_argument_count") getArgumentCount;
%rename("get_argument_type") getArgumentType;
%rename("get_argument_name") getArgumentName;
%rename("get_argument_index") getArgumentIndex;
%rename("_set_argument") setArgument;
%rename("__repr__") toString;
%rename("Entity") IfcUntypedEntity;

%typemap(typecheck,precedence=SWIG_TYPECHECK_INTEGER) IfcEntities {
   $1 = (PySequence_Check($input) && !PyUnicode_Check($input) && !PyString_Check($input)) ? 1 : 0;
}

%typemap(in) IfcEntities {
	if (PySequence_Check($input)) {
		$1 = SHARED_PTR<IfcEntityList>(new IfcEntityList());
		for(Py_ssize_t i = 0; i < PySequence_Size($input); ++i) {
			PyObject* obj = PySequence_GetItem($input, i);
			if (obj) {
				void *arg = 0;
				int res = SWIG_ConvertPtr(obj, &arg, SWIGTYPE_p_Ifc__IfcUntypedEntity, 0);
				if (!SWIG_IsOK(res)) {
					SWIG_exception_fail(SWIG_ArgError(res), "in method '" "Entity__set_argument" "', argument " "3"" of type '" "Ifc::IfcUntypedEntity *""'"); 
				} else {
					$1->push(reinterpret_cast<Ifc::IfcUntypedEntity*>(arg));
				}
			}
		}
	} else {
		SWIG_exception(SWIG_RuntimeError,"Unknown argument type");
	}
}

%typemap(out) IfcEntities {
	const unsigned size = $1 ? $1->Size() : 0;
	$result = PyList_New(size);
	for (unsigned i = 0; i < size; ++i) {
		PyObject *o = SWIG_NewPointerObj(SWIG_as_voidptr((*$1)[i]), SWIGTYPE_p_Ifc__IfcUntypedEntity, 0);
		PyList_SetItem($result,i,o);
	}
}

%typemap(out) std::pair<IfcUtil::ArgumentType,ArgumentPtr> {
	const Argument& arg = *($1.second);
	const ArgumentType type = $1.first;
	if (arg.isNull()) {
		Py_INCREF(Py_None);
		$result = Py_None;
	} else {
	switch(type) {
		case Argument_INT:
			$result = PyInt_FromLong((int)arg);
		break;
		case Argument_BOOL:
			$result = PyBool_FromLong((bool)arg);
		break; 
		case Argument_DOUBLE:
			$result = PyFloat_FromDouble(arg);
		break;
		case Argument_ENUMERATION:
		case Argument_STRING: {
			const std::string s = arg;
			$result = PyString_FromString(s.c_str());
		break; }
		case Argument_VECTOR_INT: {
			const std::vector<int> v = arg;
			const unsigned size = v.size();
			$result = PyList_New(size);
			for (unsigned int i = 0; i < size; ++i) {
				PyList_SetItem($result,i,PyInt_FromLong(v[i]));
			}
		break; }
		case Argument_VECTOR_DOUBLE: {
			const std::vector<double> v = arg;
			const unsigned size = v.size();
			$result = PyList_New(size);
			for (unsigned int i = 0; i < size; ++i) {
				PyList_SetItem($result,i,PyFloat_FromDouble(v[i]));
			}
		break; }
		case Argument_VECTOR_STRING: {
			const std::vector<std::string> v = arg;
			const unsigned size = v.size();
			$result = PyList_New(size);
			for (unsigned int i = 0; i < size; ++i) {
				PyList_SetItem($result,i,PyString_FromString(v[i].c_str()));
			}
		break; }
		case Argument_ENTITY: {
			IfcUtil::IfcSchemaEntity e = arg;
			$result = SWIG_NewPointerObj(SWIG_as_voidptr(e), SWIGTYPE_p_Ifc__IfcUntypedEntity, 0);
		break; }
		case Argument_ENTITY_LIST: {
			IfcEntities es = arg;
			const unsigned size = es->Size();
			$result = PyList_New(size);
			for (unsigned i = 0; i < size; ++i) {
				PyObject *o = SWIG_NewPointerObj(SWIG_as_voidptr((*es)[i]), SWIGTYPE_p_Ifc__IfcUntypedEntity, 0);
				PyList_SetItem($result,i,o);
			}
		break; }
		case Argument_UNKNOWN:
		default:
			SWIG_exception(SWIG_RuntimeError,"Unknown argument type");
		break;
	}
	}
}

%exception {
	try {
		$action
	} catch(::IfcParse::IfcException& e) {
		SWIG_exception(SWIG_RuntimeError,e.what());
	}
}

%module IfcImport %{
	#include "../ifcparse/IfcException.h"
	#include "Interface.h"	
	using namespace Ifc;
	using namespace IfcParse;
%}

%include "Interface.h"

%extend IfcParse::IfcFile {
	Ifc::IfcUntypedEntity* by_id(unsigned id) {
		return (IfcUntypedEntity*) $self->EntityById(id);
	}
	Ifc::IfcUntypedEntity* by_guid(const std::string& guid) {
		return (IfcUntypedEntity*) $self->EntityByGuid(guid);
	}
	void add(Ifc::IfcUntypedEntity* e) {
		$self->AddEntity(e);
	}
	void write(const std::string& fn) {
		std::ofstream f(fn.c_str());
		f << (*$self);
	}
}

%extend Ifc::IfcUntypedEntity {
	%pythoncode %{
	set_argument = lambda self,x,y: self._set_argument(x) if y is None else self._set_argument(x,y)
	%}
}

namespace std {
   %template(Ints) vector<int>;
   %template(Doubles) vector<double>;
   %template(Strings) vector<string>;
};
