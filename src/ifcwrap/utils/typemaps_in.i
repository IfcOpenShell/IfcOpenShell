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

%typemap(in) IfcEntityList::ptr {
	if (PySequence_Check($input)) {
		$1 = IfcEntityList::ptr(new IfcEntityList());
		for(Py_ssize_t i = 0; i < PySequence_Size($input); ++i) {
			PyObject* element = PySequence_GetItem($input, i);
			IfcUtil::IfcBaseClass* inst = cast_pyobject<IfcUtil::IfcBaseClass*>(element);
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

%typemap(in) IfcEntityListList::ptr {
	if (PySequence_Check($input)) {
		$1 = IfcEntityListList::ptr(new IfcEntityListList());
		for(Py_ssize_t i = 0; i < PySequence_Size($input); ++i) {
			PyObject* element = PySequence_GetItem($input, i);
			if (PySequence_Check(element)) {
				std::vector<IfcUtil::IfcBaseClass*> vector;
				vector.reserve(PySequence_Size(element));
				for(Py_ssize_t j = 0; j < PySequence_Size(element); ++j) {
					PyObject* element_element = PySequence_GetItem(element, j);
					IfcUtil::IfcBaseClass* inst = cast_pyobject<IfcUtil::IfcBaseClass*>(element_element);
					if (inst) {
						vector.push_back(cast_pyobject<IfcUtil::IfcBaseClass*>(element_element));
					} else {
						SWIG_exception(SWIG_TypeError, "Attribute of type AGGREGATE OF AGGREGATE OF ENTITY INSTANCE needs a python sequence of sequence of entity instances");
					} 
				}
				$1->push(vector);
			} else {
				SWIG_exception(SWIG_TypeError, "Attribute of type AGGREGATE OF AGGREGATE OF ENTITY INSTANCE needs a python sequence of sequence of entity instances");
				break;
			}			
		}
	} else {
		SWIG_exception(SWIG_TypeError, "Attribute of type AGGREGATE OF AGGREGATE OF ENTITY INSTANCE needs a python sequence of sequence of entity instances");
	}
}