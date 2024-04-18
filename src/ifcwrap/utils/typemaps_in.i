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

%define CREATE_VECTOR_TYPEMAP_IN(template_type, express_name, python_name)

	%typemap(in) std::vector<template_type> {
		if (!check_aggregate_of_type($input, get_python_type<template_type>())) {
			SWIG_exception(SWIG_TypeError, "Attribute of type AGGREGATE OF " #express_name " needs a python sequence of " #python_name "s");
		}
		$1 = python_sequence_as_vector<template_type>($input);
	}
	%typemap(typecheck,precedence=SWIG_TYPECHECK_INTEGER) std::vector<template_type> {
		$1 = check_aggregate_of_type($input, get_python_type<template_type>()) ? 1 : 0;
	}

	%typemap(typecheck,precedence=SWIG_TYPECHECK_INTEGER) const std::vector<template_type>& {
		$1 = check_aggregate_of_type($input, get_python_type<template_type>()) ? 1 : 0;
	}
	%typemap(arginit) const std::vector<template_type>& {
		$1 = new std::vector<template_type>();
	}
	%typemap(in) const std::vector<template_type>& {
		if (!check_aggregate_of_type($input, get_python_type<template_type>())) {
			SWIG_exception(SWIG_TypeError, "Attribute of type AGGREGATE OF " #express_name " needs a python sequence of " #python_name "s");
		}
		*$1 = python_sequence_as_vector<template_type>($input);
	}
	%typemap(freearg) const std::vector<template_type>& {
		delete $1;
	}

	%typemap(in) std::vector< std::vector<template_type> > {
		if (!check_aggregate_of_aggregate_of_type($input, get_python_type<template_type>())) {
			SWIG_exception(SWIG_TypeError, "Attribute of type AGGREGATE OF AGGREGATE OF " #express_name " needs a python sequence of sequence of " #python_name "s");
		}
		$1 = python_sequence_as_vector_of_vector<template_type>($input);
	}

	%typemap(arginit) const std::vector< std::vector<template_type> >& {
		$1 = new std::vector< std::vector<template_type> >();
	}
	%typemap(in) const std::vector< std::vector<template_type> >& {
		if (!check_aggregate_of_aggregate_of_type($input, get_python_type<template_type>())) {
			SWIG_exception(SWIG_TypeError, "Attribute of type AGGREGATE OF AGGREGATE OF " #express_name " needs a python sequence of sequence of " #python_name "s");
		}
		*$1 = python_sequence_as_vector_of_vector<template_type>($input);
	}
	%typemap(freearg) const std::vector< std::vector<template_type> >& {
		delete $1;
	}

%enddef

CREATE_VECTOR_TYPEMAP_IN(int, INTEGER, int)
CREATE_VECTOR_TYPEMAP_IN(double, REAL, float)
CREATE_VECTOR_TYPEMAP_IN(std::string, STRING, str)

// @todo use macros.

%typemap(in) const std::vector<const IfcParse::declaration*>& {
	if (PySequence_Check($input)) {
		$1 = new std::vector<const IfcParse::declaration*>;
		for(Py_ssize_t i = 0; i < PySequence_Size($input); ++i) {
			PyObject* element = PySequence_GetItem($input, i);
			void *arg = 0;
			int res = SWIG_ConvertPtr(element, &arg, SWIGTYPE_p_IfcParse__declaration, 0);
			Py_DECREF(element);
			auto decl = static_cast<const IfcParse::declaration*>(SWIG_IsOK(res) ? arg : 0);
			if (decl) {
				$1->push_back(decl);
			} else {
				SWIG_exception(SWIG_TypeError, "Expected a schema declaration");
			}
		}
	} else {
		SWIG_exception(SWIG_TypeError, "Expected an sequence type");
	}
}

%typemap(in) const std::vector<const IfcParse::entity*>& {
	if (PySequence_Check($input)) {
		$1 = new std::vector<const IfcParse::entity*>;
		for(Py_ssize_t i = 0; i < PySequence_Size($input); ++i) {
			PyObject* element = PySequence_GetItem($input, i);
			void *arg = 0;
			int res = SWIG_ConvertPtr(element, &arg, SWIGTYPE_p_IfcParse__entity, 0);
			Py_DECREF(element);
			auto decl = static_cast<const IfcParse::entity*>(SWIG_IsOK(res) ? arg : 0);
			if (decl) {
				$1->push_back(decl);
			} else {
				SWIG_exception(SWIG_TypeError, "Expected a schema entity");
			}
		}
	} else {
		SWIG_exception(SWIG_TypeError, "Expected an sequence type");
	}
}

%typemap(in) const std::vector<const IfcParse::attribute*>& {
	if (PySequence_Check($input)) {
		$1 = new std::vector<const IfcParse::attribute*>;
		for(Py_ssize_t i = 0; i < PySequence_Size($input); ++i) {
			PyObject* element = PySequence_GetItem($input, i);
			void *arg = 0;
			int res = SWIG_ConvertPtr(element, &arg, SWIGTYPE_p_IfcParse__attribute, 0);
			Py_DECREF(element);
			auto decl = static_cast<const IfcParse::attribute*>(SWIG_IsOK(res) ? arg : 0);
			if (decl) {
				$1->push_back(decl);
			} else {
				SWIG_exception(SWIG_TypeError, "Expected a schema attribute");
			}
		}
	} else {
		SWIG_exception(SWIG_TypeError, "Expected an sequence type");
	}
}

%typemap(in) const std::vector<const IfcParse::inverse_attribute*>& {
	if (PySequence_Check($input)) {
		$1 = new std::vector<const IfcParse::inverse_attribute*>;
		for(Py_ssize_t i = 0; i < PySequence_Size($input); ++i) {
			PyObject* element = PySequence_GetItem($input, i);
			void *arg = 0;
			int res = SWIG_ConvertPtr(element, &arg, SWIGTYPE_p_IfcParse__inverse_attribute, 0);
			Py_DECREF(element);
			auto decl = static_cast<const IfcParse::inverse_attribute*>(SWIG_IsOK(res) ? arg : 0);
			if (decl) {
				$1->push_back(decl);
			} else {
				SWIG_exception(SWIG_TypeError, "Expected a schema inverse attribute");
			}
		}
	} else {
		SWIG_exception(SWIG_TypeError, "Expected an sequence type");
	}
}

%typemap(in) const std::vector<bool>& {
	if (PySequence_Check($input)) {
		$1 = new std::vector<bool>;
		for(Py_ssize_t i = 0; i < PySequence_Size($input); ++i) {
			PyObject* element = PySequence_GetItem($input, i);
			$1->push_back(PyObject_IsTrue(element));
			Py_DECREF(element);
		}
	} else {
		SWIG_exception(SWIG_TypeError, "Expected an sequence type");
	}
}

%typemap(in) aggregate_of_instance::ptr {
	if (PySequence_Check($input)) {
		$1 = aggregate_of_instance::ptr(new aggregate_of_instance());
		for(Py_ssize_t i = 0; i < PySequence_Size($input); ++i) {
			PyObject* element = PySequence_GetItem($input, i);
			IfcUtil::IfcBaseClass* inst = cast_pyobject<IfcUtil::IfcBaseClass*>(element);
			Py_DECREF(element);
			if (inst) {
				$1->push(inst);
			} else {
				SWIG_exception(SWIG_TypeError, "Attribute of type AGGREGATE OF ENTITY INSTANCE needs a python sequence of entity instances");
			}
		}
	} else {
		SWIG_exception(SWIG_TypeError, "Attribute of type AGGREGATE OF ENTITY INSTANCE needs a python sequence of entity instances");
	}
}

%typemap(in) aggregate_of_aggregate_of_instance::ptr {
	if (PySequence_Check($input)) {
		$1 = aggregate_of_aggregate_of_instance::ptr(new aggregate_of_aggregate_of_instance());
		for(Py_ssize_t i = 0; i < PySequence_Size($input); ++i) {
			PyObject* element = PySequence_GetItem($input, i);
			bool b = false;
			if (PySequence_Check(element)) {
				b = true;
				std::vector<IfcUtil::IfcBaseClass*> vector;
				vector.reserve(PySequence_Size(element));
				for(Py_ssize_t j = 0; j < PySequence_Size(element); ++j) {
					PyObject* element_element = PySequence_GetItem(element, j);
					IfcUtil::IfcBaseClass* inst = cast_pyobject<IfcUtil::IfcBaseClass*>(element_element);
					Py_DECREF(element_element);
					if (inst) {
						vector.push_back(inst);
					} else {
						SWIG_exception(SWIG_TypeError, "Attribute of type AGGREGATE OF AGGREGATE OF ENTITY INSTANCE needs a python sequence of sequence of entity instances");
					}
				}
				$1->push(vector);
			}
			Py_DECREF(element);
			if (!b) {
				SWIG_exception(SWIG_TypeError, "Attribute of type AGGREGATE OF AGGREGATE OF ENTITY INSTANCE needs a python sequence of sequence of entity instances");
				break;
			}
		}
	} else {
		SWIG_exception(SWIG_TypeError, "Attribute of type AGGREGATE OF AGGREGATE OF ENTITY INSTANCE needs a python sequence of sequence of entity instances");
	}
}

%typemap(in) const gp_Pnt& {
	if (!check_aggregate_of_type($input, get_python_type<double>())) {
		SWIG_exception(SWIG_TypeError, "<Point> type needs a python sequence of 3 floats");
	}
	std::vector<double> ds = python_sequence_as_vector<double>($input);
	if (ds.size() != 3) {
		SWIG_exception(SWIG_TypeError, "<Point> type needs a python sequence of 3 floats");
	}
	$1 = new gp_Pnt(ds[0], ds[1], ds[2]);
}

%typemap(in) const gp_Dir& {
	if (!check_aggregate_of_type($input, get_python_type<double>())) {
		SWIG_exception(SWIG_TypeError, "<Direction> type needs a python sequence of 3 floats");
	}
	std::vector<double> ds = python_sequence_as_vector<double>($input);
	if (ds.size() != 3) {
		SWIG_exception(SWIG_TypeError, "<Direction> type needs a python sequence of 3 floats");
	}
	$1 = new gp_Dir(ds[0], ds[1], ds[2]);
}

%typemap(in) const Bnd_Box& {
	if (!check_aggregate_of_aggregate_of_type($input, get_python_type<double>())) {
		SWIG_exception(SWIG_TypeError, "<AABB> type needs a python sequence of 2 x 3 floats");
	}
	std::vector< std::vector<double> > ds = python_sequence_as_vector_of_vector<double>($input);
	if (ds.size() != 2) {
		SWIG_exception(SWIG_TypeError, "<AABB> type needs a python sequence of 2 x 3 floats");
	}
	if (ds[0].size() != 3 || ds[1].size() != 3) {
		SWIG_exception(SWIG_TypeError, "<AABB> type needs a python sequence of 2 x 3 floats");
	}
	$1 = new Bnd_Box();
	$1->Add(gp_Pnt(ds[0][0], ds[0][1], ds[0][2]));
	$1->Add(gp_Pnt(ds[1][0], ds[1][1], ds[1][2]));
}

%typemap(typecheck, precedence=SWIG_TYPECHECK_INTEGER) const gp_Pnt& {
   $1 = check_aggregate_of_type($input, get_python_type<double>());
}

%typemap(typecheck, precedence=SWIG_TYPECHECK_INTEGER) const gp_Dir& {
   $1 = check_aggregate_of_type($input, get_python_type<double>());
}

%typemap(typecheck, precedence=SWIG_TYPECHECK_INTEGER) const Bnd_Box& {
   $1 = check_aggregate_of_aggregate_of_type($input, get_python_type<double>());
}

%typemap(in) boost::logic::tribool {
	if (PyBool_Check($input)) {
		$1 = $input == Py_True;
	} else if (PyUnicode_Check($input)) {
		// we already checked the value of the string in the typecheck typemap
		$1 = boost::logic::indeterminate;
	} else {
		SWIG_exception(SWIG_TypeError, "Logical needs boolean or \"UNKOWN\"");
	}
}

%typemap(typecheck, precedence=SWIG_TYPECHECK_INTEGER) boost::logic::tribool {
    $1 = PyBool_Check($input);
	if (!$1 && PyUnicode_Check($input)) {
		PyObject * ascii = PyUnicode_AsEncodedString(result, "UTF-8", "strict");
		if (ascii) {
			$1 = strcmp(PyBytes_AS_STRING(ascii), "UNKNOWN") == 0;
			Py_DECREF(ascii);
		}	
	}
}

%define CREATE_OPTIONAL_TYPEMAP_IN(template_type, express_name, python_name)

	%typemap(in) const boost::optional<template_type>& {
		if ($input == Py_None) {
			(*$1) = boost::none;
		} else if ($input->ob_type != get_python_type<template_type>()) {
			SWIG_exception(SWIG_TypeError, "Optional " #express_name " needs a " #python_name " or None");
		} else {
			(*$1) = cast_pyobject<template_type>($input);
		}
	}

	%typemap(typecheck,precedence=SWIG_TYPECHECK_INTEGER) const boost::optional<template_type>& {
		$1 = ($input == Py_None || $input->ob_type == get_python_type<template_type>()) ? 1 : 0;
	}

	%typemap(arginit) const boost::optional<template_type>& {
		$1 = new boost::optional<template_type>();
	}

	%typemap(freearg) const boost::optional<template_type>& {
		delete $1;
	}

%enddef

CREATE_OPTIONAL_TYPEMAP_IN(int, integer, int)
CREATE_OPTIONAL_TYPEMAP_IN(double, real, float)
CREATE_OPTIONAL_TYPEMAP_IN(std::string, string, str)

%{
	bool check_aggregate_of_swig_type(PyObject* aggregate, swig_type_info* type_obj) {
		if (!PySequence_Check(aggregate)) return false;
		for(Py_ssize_t i = 0; i < PySequence_Size(aggregate); ++i) {
			PyObject* element = PySequence_GetItem(aggregate, i);
			
			bool b = true;
			void* argp1 = nullptr;
			auto res1 = SWIG_ConvertPtr(element, &argp1, type_obj, 0);
			if (!SWIG_IsOK(res1)) {
				b = false;
			}
			
			Py_DECREF(element);
			if (!b) {
				return false;
			}
		}
		return true;		
	}

	template <typename T>
	std::vector<T> python_sequence_as_swig_object_vector(PyObject* aggregate, swig_type_info* type_obj) {
		std::vector<T> result_vector;
		result_vector.reserve(PySequence_Size(aggregate));
		for(Py_ssize_t i = 0; i < PySequence_Size(aggregate); ++i) {
			PyObject* element = PySequence_GetItem(aggregate, i);
			void* argp1 = nullptr;
			auto res1 = SWIG_ConvertPtr(element, &argp1, type_obj, 0);
			if (SWIG_IsOK(res1)) {
				auto arg1 = reinterpret_cast<IfcGeom::OpaqueCoordinate<4>*>(argp1);
				result_vector.push_back(*arg1);
			}
		}
		return result_vector;
	}
%}

%typemap(typecheck,precedence=SWIG_TYPECHECK_INTEGER) const std::vector<IfcGeom::OpaqueCoordinate<4>>& {
	$1 = check_aggregate_of_swig_type($input, SWIGTYPE_p_IfcGeom__OpaqueCoordinateT_4_t) ? 1 : 0;
}
%typemap(arginit) const std::vector<IfcGeom::OpaqueCoordinate<4>>& {
	$1 = new std::vector<IfcGeom::OpaqueCoordinate<4>>();
}
%typemap(in) const std::vector<IfcGeom::OpaqueCoordinate<4>>& {
	if (!check_aggregate_of_swig_type($input, SWIGTYPE_p_IfcGeom__OpaqueCoordinateT_4_t)) {
		SWIG_exception(SWIG_TypeError, "");
	}
	*$1 = python_sequence_as_swig_object_vector<IfcGeom::OpaqueCoordinate<4>>($input, SWIGTYPE_p_IfcGeom__OpaqueCoordinateT_4_t);
}
%typemap(freearg) const std::vector<IfcGeom::OpaqueCoordinate<4>>& {
	delete $1;
}



%define CREATE_SET_TYPEMAP_IN(template_type)

	%typemap(in) std::set<template_type> {
		if (!check_aggregate_of_type($input, get_python_type<template_type>())) {
			SWIG_exception(SWIG_TypeError, "Invalid");
		}
		$1 = python_sequence_as_set<template_type>($input);
	}
	%typemap(typecheck,precedence=SWIG_TYPECHECK_INTEGER) std::set<template_type> {
		$1 = check_aggregate_of_type($input, get_python_type<template_type>()) ? 1 : 0;
	}

	%typemap(typecheck,precedence=SWIG_TYPECHECK_INTEGER) const std::set<template_type>& {
		$1 = check_aggregate_of_type($input, get_python_type<template_type>()) ? 1 : 0;
	}
	%typemap(arginit) const std::set<template_type>& {
		$1 = new std::set<template_type>();
	}
	%typemap(in) const std::set<template_type>& {
		if (!check_aggregate_of_type($input, get_python_type<template_type>())) {
			SWIG_exception(SWIG_TypeError, "Invalid");
		}
		*$1 = python_sequence_as_set<template_type>($input);
	}
	%typemap(freearg) const std::set<template_type>& {
		delete $1;
	}
%enddef

CREATE_SET_TYPEMAP_IN(int)
CREATE_SET_TYPEMAP_IN(std::string)
