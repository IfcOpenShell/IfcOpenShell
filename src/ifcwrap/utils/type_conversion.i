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
			bool b = element->ob_type == type_obj;
			Py_DECREF(element);
			if (!b) {
				return false;
			}
		}
		return true;		
	}

	bool check_aggregate_of_aggregate_of_type(PyObject* aggregate, void* type_obj) {
		if (!PySequence_Check(aggregate)) return false;
		for(Py_ssize_t i = 0; i < PySequence_Size(aggregate); ++i) {
			PyObject* element = PySequence_GetItem(aggregate, i);
			bool b = check_aggregate_of_type(element, type_obj);
			Py_DECREF(element);
			if (!b) {
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
	#if SWIG_VERSION >= 0x040200
	    PyObject *pbytes = NULL;
	    const char* str_data = SWIG_PyUnicode_AsUTF8AndSize(element, NULL, &pbytes);
		std::string str = str_data;
		Py_XDECREF(pbytes);
	#else
		char* str_data = SWIG_Python_str_AsChar(element);
		std::string str = str_data;
		SWIG_Python_str_DelForPy3(str_data);
	#endif
		return str;
	}

	template <>
	IfcUtil::IfcBaseClass* cast_pyobject(PyObject* element) {
		void *arg = 0;
		int res = SWIG_ConvertPtr(element, &arg, SWIGTYPE_p_IfcUtil__IfcBaseClass, 0);
		return static_cast<IfcUtil::IfcBaseClass*>(SWIG_IsOK(res) ? arg : 0);
	}

	template<typename T>
	void add_to_container(std::vector<T>& container, const T& element) {
		container.push_back(element);
	}

	template<typename T>
	void add_to_container(std::set<T>& container, const T& element) {
		container.insert(element);
	}

	template <typename T, template<typename...> typename U>
	U<T> python_sequence_as_cpp_container(PyObject* aggregate) {
		U<T> result_vector;
		if constexpr (std::is_same_v<U<T>, std::vector<T>>) {
			result_vector.reserve(PySequence_Size(aggregate));
		}
		for(Py_ssize_t i = 0; i < PySequence_Size(aggregate); ++i) {
			PyObject* element = PySequence_GetItem(aggregate, i);
			T t = cast_pyobject<T>(element);
			add_to_container(result_vector, t);
		}
		return result_vector;
	}

	template <typename T>
	std::vector<T> python_sequence_as_vector(PyObject* aggregate) {
		return python_sequence_as_cpp_container<T, std::vector>(aggregate);
	}

	template <typename T>
	std::set<T> python_sequence_as_set(PyObject* aggregate) {
		return python_sequence_as_cpp_container<T, std::set>(aggregate);
	}

	template <typename T>
	std::vector< std::vector<T> > python_sequence_as_vector_of_vector(PyObject* aggregate) {
		std::vector< std::vector<T> > result_vector;
		result_vector.reserve(PySequence_Size(aggregate));
		for(Py_ssize_t i = 0; i < PySequence_Size(aggregate); ++i) {
			PyObject* element = PySequence_GetItem(aggregate, i);
			std::vector<T> t = python_sequence_as_vector<T>(element);
			result_vector.push_back(t);
			Py_DECREF(element);
		}
		return result_vector;
	}
%}

// Conversion functions to convert STL vectors into Python objects
%{
	swig_type_info* declaration_type_to_swig(const IfcParse::declaration* t) {
		if (t->as_entity()) {
			return SWIGTYPE_p_IfcParse__entity;
		} else if (t->as_type_declaration()) {
			return SWIGTYPE_p_IfcParse__type_declaration;
		} else if (t->as_select_type()) {
			return SWIGTYPE_p_IfcParse__select_type;
		} else if (t->as_enumeration_type()) {
			return SWIGTYPE_p_IfcParse__enumeration_type;
		} else {
			throw std::runtime_error("Unexpected declaration type");
		}
	}

	PyObject* pythonize(const int& t)                   { return PyInt_FromLong(t);                                                                  }
	PyObject* pythonize(const unsigned int& t)          { return PyInt_FromLong(t);                                                                  }
	PyObject* pythonize(const bool& t)                  { return PyBool_FromLong(t);                                                                 }
	PyObject* pythonize(const boost::logic::tribool& t) { return boost::logic::indeterminate(t) ? PyUnicode_FromString("UNKNOWN") : PyBool_FromLong((bool)t) ;}
	PyObject* pythonize(const double& t)                { return PyFloat_FromDouble(t);                                                              }
	PyObject* pythonize(const std::string& t)           { return PyUnicode_FromString(t.c_str());                                                    }
	PyObject* pythonize(const IfcUtil::IfcBaseClass* t) { return SWIG_NewPointerObj(SWIG_as_voidptr(t), SWIGTYPE_p_IfcUtil__IfcBaseClass, 0);        }
	PyObject* pythonize(const IfcParse::attribute* t)   { return SWIG_NewPointerObj(SWIG_as_voidptr(t), SWIGTYPE_p_IfcParse__attribute, 0);          }
	PyObject* pythonize(const IfcParse::inverse_attribute* t) { return SWIG_NewPointerObj(SWIG_as_voidptr(t), SWIGTYPE_p_IfcParse__inverse_attribute, 0); }
	PyObject* pythonize(const IfcParse::entity* t)      { return SWIG_NewPointerObj(SWIG_as_voidptr(t), SWIGTYPE_p_IfcParse__entity, 0);             }
	PyObject* pythonize(const IfcParse::declaration* t) { return SWIG_NewPointerObj(SWIG_as_voidptr(t), declaration_type_to_swig(t), 0);             }
	// @nb ownership
	PyObject* pythonize(const IfcGeom::ConversionResultShape* t) { return SWIG_NewPointerObj(SWIG_as_voidptr(t), SWIGTYPE_p_IfcGeom__ConversionResultShape, SWIG_POINTER_OWN); }
	// PyObject* pythonize(const IfcGeom::ConversionResultShape* t) { return SWIG_NewPointerObj(SWIG_as_voidptr(t), SWIGTYPE_p_IfcGeom__ConversionResultShape, 0); }
	// NB: This cannot be temporary as a Python object is constructed from a pointer to the address of this object
	// PyObject* pythonize(const IfcGeom::Material& t)     { return SWIG_NewPointerObj(SWIG_as_voidptr(&t), SWIGTYPE_p_IfcGeom__Material, 0);           }
	
	PyObject* pythonize(const boost::dynamic_bitset<>& t) { 
		std::string bitstring;
		boost::to_string(t, bitstring);
		return pythonize(bitstring);
	}

	PyObject* pythonize(const aggregate_of_instance::ptr& t) { 
		unsigned int i = 0;
		PyObject* pyobj = PyTuple_New(t->size());
		for (aggregate_of_instance::it it = t->begin(); it != t->end(); ++it, ++i) {
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

	PyObject* pythonize(const aggregate_of_aggregate_of_instance::ptr& t) {
		unsigned int i = 0;
		PyObject* pyobj = PyTuple_New(t->size());
		for (aggregate_of_aggregate_of_instance::outer_it it = t->begin(); it != t->end(); ++it, ++i) {
			PyTuple_SetItem(pyobj, i, pythonize_vector(*it));
		}
		return pyobj;
	}

	struct pythonizing_visitor {
		typedef PyObject* result_type;

		template <typename T>
		PyObject* operator()(const T& t) {
			if constexpr (std::is_same_v<std::remove_cv_t<std::remove_reference_t<T>>, std::set<int>>) {
				std::vector<int> vs(t.begin(), t.end());
				return pythonize_vector(vs);
			} else if constexpr (std::is_same_v<std::remove_cv_t<std::remove_reference_t<T>>, std::set<std::string>>) {
                std::vector<std::string> vs(t.begin(), t.end());
                return pythonize_vector(vs);
            } else {
				return pythonize(t);
			}
		}
	};

%}

%{

PyObject* item_to_pyobject(const ifcopenshell::geometry::taxonomy::item::ptr& i) {
	using namespace ifcopenshell::geometry::taxonomy;
	if (i == nullptr) {
		Py_INCREF(Py_None);
		return Py_None;
	}
	auto kind = i->kind();
	// @todo this is not automatically generated :(
	// we can probably use the dispatch mechanism for this we already have in the kernel
	if (kind == BOOLEAN_RESULT) { return SWIG_NewPointerObj(SWIG_as_voidptr(new std::shared_ptr<boolean_result>(std::static_pointer_cast<boolean_result>(i))), SWIGTYPE_p_std__shared_ptrT_ifcopenshell__geometry__taxonomy__boolean_result_t, 0 | SWIG_POINTER_OWN); }
	else if (kind == BSPLINE_CURVE) { return SWIG_NewPointerObj(SWIG_as_voidptr(new std::shared_ptr<bspline_curve>(std::static_pointer_cast<bspline_curve>(i))), SWIGTYPE_p_std__shared_ptrT_ifcopenshell__geometry__taxonomy__bspline_curve_t, 0 | SWIG_POINTER_OWN); }
	else if (kind == BSPLINE_SURFACE) { return SWIG_NewPointerObj(SWIG_as_voidptr(new std::shared_ptr<bspline_surface>(std::static_pointer_cast<bspline_surface>(i))), SWIGTYPE_p_std__shared_ptrT_ifcopenshell__geometry__taxonomy__bspline_surface_t, 0 | SWIG_POINTER_OWN); }
	else if (kind == CIRCLE) { return SWIG_NewPointerObj(SWIG_as_voidptr(new std::shared_ptr<circle>(std::static_pointer_cast<circle>(i))), SWIGTYPE_p_std__shared_ptrT_ifcopenshell__geometry__taxonomy__circle_t, 0 | SWIG_POINTER_OWN); }
	else if (kind == COLLECTION) { return SWIG_NewPointerObj(SWIG_as_voidptr(new std::shared_ptr<collection>(std::static_pointer_cast<collection>(i))), SWIGTYPE_p_std__shared_ptrT_ifcopenshell__geometry__taxonomy__collection_t, 0 | SWIG_POINTER_OWN); }
	else if (kind == COLOUR) { return SWIG_NewPointerObj(SWIG_as_voidptr(new std::shared_ptr<colour>(std::static_pointer_cast<colour>(i))), SWIGTYPE_p_std__shared_ptrT_ifcopenshell__geometry__taxonomy__colour_t, 0 | SWIG_POINTER_OWN); }
	else if (kind == CYLINDER) { return SWIG_NewPointerObj(SWIG_as_voidptr(new std::shared_ptr<cylinder>(std::static_pointer_cast<cylinder>(i))), SWIGTYPE_p_std__shared_ptrT_ifcopenshell__geometry__taxonomy__cylinder_t, 0 | SWIG_POINTER_OWN); }
	else if (kind == DIRECTION3) { return SWIG_NewPointerObj(SWIG_as_voidptr(new std::shared_ptr<direction3>(std::static_pointer_cast<direction3>(i))), SWIGTYPE_p_std__shared_ptrT_ifcopenshell__geometry__taxonomy__direction3_t, 0 | SWIG_POINTER_OWN); }
	else if (kind == EDGE) { return SWIG_NewPointerObj(SWIG_as_voidptr(new std::shared_ptr<edge>(std::static_pointer_cast<edge>(i))), SWIGTYPE_p_std__shared_ptrT_ifcopenshell__geometry__taxonomy__edge_t, 0 | SWIG_POINTER_OWN); }
	else if (kind == ELLIPSE) { return SWIG_NewPointerObj(SWIG_as_voidptr(new std::shared_ptr<ellipse>(std::static_pointer_cast<ellipse>(i))), SWIGTYPE_p_std__shared_ptrT_ifcopenshell__geometry__taxonomy__ellipse_t, 0 | SWIG_POINTER_OWN); }
	else if (kind == EXTRUSION) { return SWIG_NewPointerObj(SWIG_as_voidptr(new std::shared_ptr<extrusion>(std::static_pointer_cast<extrusion>(i))), SWIGTYPE_p_std__shared_ptrT_ifcopenshell__geometry__taxonomy__extrusion_t, 0 | SWIG_POINTER_OWN); }
	else if (kind == FACE) { return SWIG_NewPointerObj(SWIG_as_voidptr(new std::shared_ptr<face>(std::static_pointer_cast<face>(i))), SWIGTYPE_p_std__shared_ptrT_ifcopenshell__geometry__taxonomy__face_t, 0 | SWIG_POINTER_OWN); }
	else if (kind == LINE) { return SWIG_NewPointerObj(SWIG_as_voidptr(new std::shared_ptr<line>(std::static_pointer_cast<line>(i))), SWIGTYPE_p_std__shared_ptrT_ifcopenshell__geometry__taxonomy__line_t, 0 | SWIG_POINTER_OWN); }
	else if (kind == LOFT) { return SWIG_NewPointerObj(SWIG_as_voidptr(new std::shared_ptr<loft>(std::static_pointer_cast<loft>(i))), SWIGTYPE_p_std__shared_ptrT_ifcopenshell__geometry__taxonomy__loft_t, 0 | SWIG_POINTER_OWN); }
	else if (kind == LOOP) { return SWIG_NewPointerObj(SWIG_as_voidptr(new std::shared_ptr<loop>(std::static_pointer_cast<loop>(i))), SWIGTYPE_p_std__shared_ptrT_ifcopenshell__geometry__taxonomy__loop_t, 0 | SWIG_POINTER_OWN); }
	else if (kind == MATRIX4) { return SWIG_NewPointerObj(SWIG_as_voidptr(new std::shared_ptr<matrix4>(std::static_pointer_cast<matrix4>(i))), SWIGTYPE_p_std__shared_ptrT_ifcopenshell__geometry__taxonomy__matrix4_t, 0 | SWIG_POINTER_OWN); }
	else if (kind == NODE) { return SWIG_NewPointerObj(SWIG_as_voidptr(new std::shared_ptr<node>(std::static_pointer_cast<node>(i))), SWIGTYPE_p_std__shared_ptrT_ifcopenshell__geometry__taxonomy__node_t, 0 | SWIG_POINTER_OWN); }
	else if (kind == OFFSET_CURVE) { return SWIG_NewPointerObj(SWIG_as_voidptr(new std::shared_ptr<offset_curve>(std::static_pointer_cast<offset_curve>(i))), SWIGTYPE_p_std__shared_ptrT_ifcopenshell__geometry__taxonomy__offset_curve_t, 0 | SWIG_POINTER_OWN); }
	else if (kind == PIECEWISE_FUNCTION) { return SWIG_NewPointerObj(SWIG_as_voidptr(new std::shared_ptr<piecewise_function>(std::static_pointer_cast<piecewise_function>(i))), SWIGTYPE_p_std__shared_ptrT_ifcopenshell__geometry__taxonomy__piecewise_function_t, 0 | SWIG_POINTER_OWN); }
	else if (kind == PLANE) { return SWIG_NewPointerObj(SWIG_as_voidptr(new std::shared_ptr<plane>(std::static_pointer_cast<plane>(i))), SWIGTYPE_p_std__shared_ptrT_ifcopenshell__geometry__taxonomy__plane_t, 0 | SWIG_POINTER_OWN); }
	else if (kind == POINT3) { return SWIG_NewPointerObj(SWIG_as_voidptr(new std::shared_ptr<point3>(std::static_pointer_cast<point3>(i))), SWIGTYPE_p_std__shared_ptrT_ifcopenshell__geometry__taxonomy__point3_t, 0 | SWIG_POINTER_OWN); }
	else if (kind == REVOLVE) { return SWIG_NewPointerObj(SWIG_as_voidptr(new std::shared_ptr<revolve>(std::static_pointer_cast<revolve>(i))), SWIGTYPE_p_std__shared_ptrT_ifcopenshell__geometry__taxonomy__revolve_t, 0 | SWIG_POINTER_OWN); }
	else if (kind == SHELL) { return SWIG_NewPointerObj(SWIG_as_voidptr(new std::shared_ptr<shell>(std::static_pointer_cast<shell>(i))), SWIGTYPE_p_std__shared_ptrT_ifcopenshell__geometry__taxonomy__shell_t, 0 | SWIG_POINTER_OWN); }
	else if (kind == SOLID) { return SWIG_NewPointerObj(SWIG_as_voidptr(new std::shared_ptr<solid>(std::static_pointer_cast<solid>(i))), SWIGTYPE_p_std__shared_ptrT_ifcopenshell__geometry__taxonomy__solid_t, 0 | SWIG_POINTER_OWN); }
	else if (kind == SPHERE) { return SWIG_NewPointerObj(SWIG_as_voidptr(new std::shared_ptr<sphere>(std::static_pointer_cast<sphere>(i))), SWIGTYPE_p_std__shared_ptrT_ifcopenshell__geometry__taxonomy__sphere_t, 0 | SWIG_POINTER_OWN); }
	else if (kind == TORUS) { return SWIG_NewPointerObj(SWIG_as_voidptr(new std::shared_ptr<torus>(std::static_pointer_cast<torus>(i))), SWIGTYPE_p_std__shared_ptrT_ifcopenshell__geometry__taxonomy__torus_t, 0 | SWIG_POINTER_OWN); }
	else if (kind == STYLE) { return SWIG_NewPointerObj(SWIG_as_voidptr(new std::shared_ptr<style>(std::static_pointer_cast<style>(i))), SWIGTYPE_p_std__shared_ptrT_ifcopenshell__geometry__taxonomy__style_t, 0 | SWIG_POINTER_OWN); }
	else if (kind == SWEEP_ALONG_CURVE) { return SWIG_NewPointerObj(SWIG_as_voidptr(new std::shared_ptr<sweep_along_curve>(std::static_pointer_cast<sweep_along_curve>(i))), SWIGTYPE_p_std__shared_ptrT_ifcopenshell__geometry__taxonomy__sweep_along_curve_t, 0 | SWIG_POINTER_OWN); }
	else {
		Py_INCREF(Py_None);
		return Py_None;
	}
}

%}
