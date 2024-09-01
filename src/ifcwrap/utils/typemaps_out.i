%typemap(out) aggregate_of_instance::ptr {
	const unsigned size = $1 ? $1->size() : 0;
	$result = PyTuple_New(size);
	for (unsigned i = 0; i < size; ++i) {
		PyTuple_SetItem($result, i, pythonize((*$1)[i]));
	}
}

%typemap(out) IfcUtil::ArgumentType {
	$result = SWIG_Python_str_FromChar(IfcUtil::ArgumentTypeToString($1));
}

%typemap(out) IfcParse::declaration* {
	$result = SWIG_NewPointerObj(SWIG_as_voidptr($1), declaration_type_to_swig($1), 0);
}

%typemap(out) IfcParse::parameter_type* {
	if ($1->as_named_type()) {
		$result = SWIG_NewPointerObj(SWIG_as_voidptr($1->as_named_type()), SWIGTYPE_p_IfcParse__named_type, 0);
	} else if ($1->as_simple_type()) {
		$result = SWIG_NewPointerObj(SWIG_as_voidptr($1->as_simple_type()), SWIGTYPE_p_IfcParse__simple_type, 0);
	} else if ($1->as_aggregation_type()) {
		$result = SWIG_NewPointerObj(SWIG_as_voidptr($1->as_aggregation_type()), SWIGTYPE_p_IfcParse__aggregation_type, 0);
	} else {
		$result = SWIG_Py_Void();
	}
}

%typemap(out) IfcParse::simple_type::data_type {
	static const char* const data_type_strings[] = {"binary", "boolean", "integer", "logical", "number", "real", "string"};
	$result = SWIG_Python_str_FromChar(data_type_strings[(int)$1]);
}

%typemap(out) AttributeValue {
	// The SWIG %exception directive does not take care
	// of our typemap. So the attribute conversion block
	// is wrapped in a try-catch block manually.
	try {
		$result = $1.array_->apply_visitor([](auto& v){
			using U = std::decay_t<decltype(v)>;
            if constexpr (is_std_vector_vector_v<U>) {
                return pythonize_vector2(v);
            } else if constexpr (is_std_vector_v<U>) {
				return pythonize_vector(v);
            } else if constexpr (std::is_same_v<U, EnumerationReference>) {
                return pythonize(std::string(v.value()));
			} else if constexpr (std::is_same_v<U, Derived>) {
				if (feature_use_attribute_value_derived) {
					return SWIG_NewPointerObj(new attribute_value_derived, SWIGTYPE_p_attribute_value_derived, SWIG_POINTER_OWN);
				} else {
					Py_INCREF(Py_None);
					return static_cast<PyObject*>(Py_None); 
				}
            } else if constexpr (std::is_same_v<U, empty_aggregate_t> || std::is_same_v<U, empty_aggregate_of_aggregate_t> || std::is_same_v<U, Blank>) {
                Py_INCREF(Py_None);
				return static_cast<PyObject*>(Py_None); 
            } else if constexpr (std::is_same_v<U, empty_aggregate_t> || std::is_same_v<U, empty_aggregate_of_aggregate_t> || std::is_same_v<U, Derived> || std::is_same_v<U, Blank>) {
                Py_INCREF(Py_None);
				return static_cast<PyObject*>(Py_None); 
            } else {
				return pythonize(v);
			}
		}, $1.index_);
	} catch(IfcParse::IfcException& e) {
		SWIG_exception(SWIG_RuntimeError, e.what());
	} catch(...) {
		SWIG_exception(SWIG_RuntimeError, "An unknown error occurred");
	}
}

%define CREATE_VECTOR_TYPEMAP_OUT(template_type)
	%typemap(out) std::vector<template_type> {
		$result = pythonize_vector<template_type>($1);
	}
	%typemap(out) const std::vector<template_type>& {
		$result = pythonize_vector<template_type>(*$1);
	}
%enddef

CREATE_VECTOR_TYPEMAP_OUT(bool)
CREATE_VECTOR_TYPEMAP_OUT(int)
CREATE_VECTOR_TYPEMAP_OUT(unsigned int)
CREATE_VECTOR_TYPEMAP_OUT(double)
CREATE_VECTOR_TYPEMAP_OUT(std::string)
// CREATE_VECTOR_TYPEMAP_OUT(IfcGeom::Material)
CREATE_VECTOR_TYPEMAP_OUT(IfcParse::attribute const *)
CREATE_VECTOR_TYPEMAP_OUT(IfcParse::inverse_attribute const *)
CREATE_VECTOR_TYPEMAP_OUT(IfcParse::entity const *)
CREATE_VECTOR_TYPEMAP_OUT(IfcParse::declaration const *)
CREATE_VECTOR_TYPEMAP_OUT(IfcGeom::ConversionResultShape *)

%typemap(out) ifcopenshell::geometry::Settings::value_variant_t {
	pythonizing_visitor vis;
	$result = $1.apply_visitor(vis);
}

%typemap(out) ifcopenshell::geometry::SerializerSettings::value_variant_t {
	pythonizing_visitor vis;
	$result = $1.apply_visitor(vis);
}

%typemap(out) std::pair<const char*, size_t> {
    $result = PyBytes_FromStringAndSize($1.first, $1.second);
}

%define vector_of_item(item_name)

%typemap(out) const std::vector<item_name::ptr>& {
	$result = PyTuple_New((*$1).size());
	for (int i = 0; i < (*$1).size(); ++i) {
		PyTuple_SetItem($result, i, item_to_pyobject((*$1).at(i)));
	}
};

%typemap(out) const item_name::ptr& {
	$result = item_to_pyobject(*$1);
};

%enddef

vector_of_item(ifcopenshell::geometry::taxonomy::item)
vector_of_item(ifcopenshell::geometry::taxonomy::boolean_result)
vector_of_item(ifcopenshell::geometry::taxonomy::bspline_curve)
vector_of_item(ifcopenshell::geometry::taxonomy::bspline_surface)
vector_of_item(ifcopenshell::geometry::taxonomy::circle)
vector_of_item(ifcopenshell::geometry::taxonomy::collection)
vector_of_item(ifcopenshell::geometry::taxonomy::colour)
vector_of_item(ifcopenshell::geometry::taxonomy::cylinder)
vector_of_item(ifcopenshell::geometry::taxonomy::direction3)
vector_of_item(ifcopenshell::geometry::taxonomy::edge)
vector_of_item(ifcopenshell::geometry::taxonomy::ellipse)
vector_of_item(ifcopenshell::geometry::taxonomy::extrusion)
vector_of_item(ifcopenshell::geometry::taxonomy::face)
vector_of_item(ifcopenshell::geometry::taxonomy::line)
vector_of_item(ifcopenshell::geometry::taxonomy::loft)
vector_of_item(ifcopenshell::geometry::taxonomy::loop)
vector_of_item(ifcopenshell::geometry::taxonomy::matrix4)
vector_of_item(ifcopenshell::geometry::taxonomy::node)
vector_of_item(ifcopenshell::geometry::taxonomy::offset_curve)
vector_of_item(ifcopenshell::geometry::taxonomy::piecewise_function)
vector_of_item(ifcopenshell::geometry::taxonomy::plane)
vector_of_item(ifcopenshell::geometry::taxonomy::point3)
vector_of_item(ifcopenshell::geometry::taxonomy::revolve)
vector_of_item(ifcopenshell::geometry::taxonomy::shell)
vector_of_item(ifcopenshell::geometry::taxonomy::solid)
vector_of_item(ifcopenshell::geometry::taxonomy::sphere)
vector_of_item(ifcopenshell::geometry::taxonomy::torus)
vector_of_item(ifcopenshell::geometry::taxonomy::style)
vector_of_item(ifcopenshell::geometry::taxonomy::sweep_along_curve)
vector_of_item(ifcopenshell::geometry::taxonomy::geom_item)
