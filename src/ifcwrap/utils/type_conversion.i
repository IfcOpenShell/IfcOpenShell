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

// Conversion functions and checks to convert Python objects into STL vectors
%{
	template <typename T> void* get_python_type();
	template <> void* get_python_type<double>() { return &PyFloat_Type; }
	#if PY_VERSION_HEX >= 0x03000000
	template <> void* get_python_type<int>() { return &PyLong_Type; }
	template <> void* get_python_type<std::string>() { return &PyUnicode_Type; }
	#else
	template <> void* get_python_type<int>() { return &PyInt_Type; }
	template <> void* get_python_type<std::string>() { return &PyString_Type; }
	#endif

	bool check_aggregate_of_type(PyObject* aggregate, void* type_obj) {
		if (!PySequence_Check(aggregate)) return false;
		for(Py_ssize_t i = 0; i < PySequence_Size(aggregate); ++i) {
			PyObject* element = PySequence_GetItem(aggregate, i);
			// This is equivalent to the PyFloat_CheckExact macro. This means
			// that direct instances of int, float, str, etc. need to be used.
			if (element->ob_type != type_obj) return false;
		}
		return true;		
	}

	bool check_aggregate_of_aggregate_of_type(PyObject* aggregate, void* type_obj) {
		if (!PySequence_Check(aggregate)) return false;
		for(Py_ssize_t i = 0; i < PySequence_Size(aggregate); ++i) {
			PyObject* element = PySequence_GetItem(aggregate, i);
			if (!check_aggregate_of_type(element, type_obj)) {
				return false;
			}
		}
		return true;
	}

	template <typename T>
	T cast_pyobject(PyObject* element);

	template <>
	int cast_pyobject(PyObject* element) {
		return static_cast<int>(PyInt_AsLong(element));
	}

	template <>
	double cast_pyobject(PyObject* element) {
		return PyFloat_AsDouble(element);
	}

	template <>
	std::string cast_pyobject(PyObject* element) {
		char* str_data = SWIG_Python_str_AsChar(element);
		std::string str = str_data;
		SWIG_Python_str_DelForPy3(str_data);
		return str;
	}

	template <>
	IfcUtil::IfcBaseClass* cast_pyobject(PyObject* element) {
		void *arg = 0;
		int res = SWIG_ConvertPtr(element, &arg, SWIGTYPE_p_IfcUtil__IfcBaseClass, 0);
		return static_cast<IfcUtil::IfcBaseClass*>(SWIG_IsOK(res) ? arg : 0);
	}

	template <typename T>
	std::vector<T> python_sequence_as_vector(PyObject* aggregate) {
		std::vector<T> result_vector;
		result_vector.reserve(PySequence_Size(aggregate));
		for(Py_ssize_t i = 0; i < PySequence_Size(aggregate); ++i) {
			PyObject* element = PySequence_GetItem(aggregate, i);
			T t = cast_pyobject<T>(element);
			result_vector.push_back(t);
		}
		return result_vector;
	}

	template <typename T>
	std::vector< std::vector<T> > python_sequence_as_vector_of_vector(PyObject* aggregate) {
		std::vector< std::vector<T> > result_vector;
		result_vector.reserve(PySequence_Size(aggregate));
		for(Py_ssize_t i = 0; i < PySequence_Size(aggregate); ++i) {
			PyObject* element = PySequence_GetItem(aggregate, i);
			std::vector<T> t = python_sequence_as_vector<T>(element);
			result_vector.push_back(t);
		}
		return result_vector;
	}
%}

// Conversion functions to convert STL vectors into Python objects
%{
	PyObject* pythonize(const int& t)                   { return PyInt_FromLong(t);                                                                  }
	PyObject* pythonize(const unsigned int& t)          { return PyInt_FromLong(t);                                                                  }
	PyObject* pythonize(const bool& t)                  { return PyBool_FromLong(t);                                                                 }
	PyObject* pythonize(const double& t)                { return PyFloat_FromDouble(t);                                                              }
	PyObject* pythonize(const std::string& t)           { return PyUnicode_FromString(t.c_str());                                                    }
	PyObject* pythonize(const IfcUtil::IfcBaseClass* t) { return SWIG_NewPointerObj(SWIG_as_voidptr(t), SWIGTYPE_p_IfcUtil__IfcBaseClass, 0); }
	// NB: This cannot be temporary as a Python object is constructed from a pointer to the address of this object
	PyObject* pythonize(const IfcGeom::Material& t)     { return SWIG_NewPointerObj(SWIG_as_voidptr(&t), SWIGTYPE_p_IfcGeom__Material, 0);           }
	
	PyObject* pythonize(const boost::dynamic_bitset<>& t) { 
		std::string bitstring;
		boost::to_string(t, bitstring);
		return pythonize(bitstring);
	}

	PyObject* pythonize(const IfcEntityList::ptr& t) { 
		unsigned int i = 0;
		PyObject* pyobj = PyTuple_New(t->size());
		for (IfcEntityList::it it = t->begin(); it != t->end(); ++it, ++i) {
			PyTuple_SetItem(pyobj, i, pythonize(*it));
		}
		return pyobj;
	}

	template <typename T>
	PyObject* pythonize_vector(const std::vector<T>& v) {
		const size_t size = v.size();
		PyObject* pyobj = PyTuple_New(size);
		for (size_t i = 0; i < size; ++i) {
			PyTuple_SetItem(pyobj, i, pythonize(v[i]));
		}
		return pyobj;
	}

	template <typename T>
	PyObject* pythonize_vector2(const std::vector< std::vector<T> >& v) {
		const size_t size = v.size();
		PyObject* pyobj = PyTuple_New(size);
		for (size_t i = 0; i < size; ++i) {
			PyTuple_SetItem(pyobj, i, pythonize_vector(v[i]));
		}
		return pyobj;
	}

	PyObject* pythonize(const IfcEntityListList::ptr& t) {
		unsigned int i = 0;
		PyObject* pyobj = PyTuple_New(t->size());
		for (IfcEntityListList::outer_it it = t->begin(); it != t->end(); ++it, ++i) {
			PyTuple_SetItem(pyobj, i, pythonize_vector(*it));
		}
		return pyobj;
	}
%}
