%typemap(out) ifcopenshell::argument_type {
	$result = PyUnicode_FromString(ifcopenshell::argument_type_to_string($1));
}

%typemap(out) ifcopenshell::declaration* {
	$result = SWIG_NewPointerObj(SWIG_as_voidptr($1), declaration_type_to_swig($1), 0);
}

%typemap(out) const ifcopenshell::declaration& {
	$result = SWIG_NewPointerObj(SWIG_as_voidptr($1), declaration_type_to_swig($1), 0);
}

%typemap(out) ifcopenshell::parameter_type* {
	if ($1->as_named_type()) {
		$result = SWIG_NewPointerObj(SWIG_as_voidptr($1->as_named_type()), SWIGTYPE_p_ifcopenshell__named_type, 0);
	} else if ($1->as_simple_type()) {
		$result = SWIG_NewPointerObj(SWIG_as_voidptr($1->as_simple_type()), SWIGTYPE_p_ifcopenshell__simple_type, 0);
	} else if ($1->as_aggregation_type()) {
		$result = SWIG_NewPointerObj(SWIG_as_voidptr($1->as_aggregation_type()), SWIGTYPE_p_ifcopenshell__aggregation_type, 0);
	} else {
		$result = SWIG_Py_Void();
	}
}

%typemap(out) ifcopenshell::simple_type::data_type {
	static const char* const data_type_strings[] = {"binary", "boolean", "integer", "logical", "number", "real", "string"};
	$result = PyUnicode_FromString(data_type_strings[(int)$1]);
}

%typemap(out) attribute_value {
	// The SWIG %exception directive does not take care
	// of our typemap. So the attribute conversion block
	// is wrapped in a try-catch block manually.
	try {
		$result = $1.apply_visitor([](const auto& v){
			using u = std::decay_t<decltype(v)>;
            if constexpr (is_std_vector_v<u>) {
				return pythonize_vector(v);
            } else if constexpr (std::is_same_v<u, ifcopenshell::enumeration_reference>) {
                return pythonize(std::string(v.value()));
			} else if constexpr (std::is_same_v<u, ifcopenshell::derived>) {
				if (feature_use_attribute_value_derived) {
					return SWIG_NewPointerObj(new attribute_value_derived, SWIGTYPE_p_attribute_value_derived, SWIG_POINTER_OWN);
				} else {
					Py_INCREF(Py_None);
					return static_cast<PyObject*>(Py_None);
				}
            } else if constexpr (std::is_same_v<u, ifcopenshell::empty_aggregate> || std::is_same_v<u, ifcopenshell::empty_aggregate_of_aggregate> || std::is_same_v<u, ifcopenshell::blank>) {
                Py_INCREF(Py_None);
				return static_cast<PyObject*>(Py_None);
            } else {
				return pythonize(v);
			}
		});
	} catch(ifcopenshell::exception& e) {
		SWIG_exception(SWIG_RuntimeError, e.what());
	} catch(...) {
		SWIG_exception(SWIG_RuntimeError, "An unknown error occurred");
	}
}

%define CREATE_VECTOR_TYPEMAP_OUT(template_type)
	%typemap(out) std::vector<template_type> {
		$result = pythonize_vector<std::vector<template_type>>($1);
	}
	%typemap(out) const std::vector<template_type>& {
		$result = pythonize_vector<std::vector<template_type>>(*$1);
	}
	%typemap(out) std::vector<std::vector<template_type>> {
		$result = pythonize_vector<std::vector<std::vector<template_type>>>($1);
	}
	%typemap(out) const std::vector<std::vector<template_type>>& {
		$result = pythonize_vector<std::vector<std::vector<template_type>>>(*$1);
	}
	%typemap(out) std::vector<std::vector<std::vector<template_type>>> {
		$result = pythonize_vector<std::vector<std::vector<std::vector<template_type>>>>($1);
	}
	%typemap(out) const std::vector<std::vector<std::vector<template_type>>>& {
		$result = pythonize_vector<std::vector<std::vector<std::vector<template_type>>>>(*$1);
	}
%enddef

CREATE_VECTOR_TYPEMAP_OUT(express::base)
CREATE_VECTOR_TYPEMAP_OUT(bool)
CREATE_VECTOR_TYPEMAP_OUT(int)
CREATE_VECTOR_TYPEMAP_OUT(unsigned int)
CREATE_VECTOR_TYPEMAP_OUT(double)
CREATE_VECTOR_TYPEMAP_OUT(std::string)
// CREATE_VECTOR_TYPEMAP_OUT(ifcopenshell::geom::Material)
CREATE_VECTOR_TYPEMAP_OUT(ifcopenshell::attribute const *)
CREATE_VECTOR_TYPEMAP_OUT(ifcopenshell::inverse_attribute const *)
CREATE_VECTOR_TYPEMAP_OUT(ifcopenshell::entity const *)
CREATE_VECTOR_TYPEMAP_OUT(ifcopenshell::declaration const *)
CREATE_VECTOR_TYPEMAP_OUT(ifcopenshell::geom::conversion_result_shape *)
CREATE_VECTOR_TYPEMAP_OUT(ifcopenshell::log_message)

%typemap(out) ifcopenshell::geom::settings::value_variant_t {
	pythonizing_visitor vis;
	$result = std::visit(vis, $1);
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

%typemap(out) std::vector<item_name::ptr> {
	const auto& v = (std::vector<item_name::ptr>) $1;
	$result = PyTuple_New(v.size());
	for (int i = 0; i < v.size(); ++i) {
		PyTuple_SetItem($result, i, item_to_pyobject(v[i]));
	}
};

%typemap(out) const item_name::ptr& {
	$result = item_to_pyobject(*$1);
};

%enddef

vector_of_item(ifcopenshell::geom::taxonomy::item)
vector_of_item(ifcopenshell::geom::taxonomy::boolean_result)
vector_of_item(ifcopenshell::geom::taxonomy::bspline_curve)
vector_of_item(ifcopenshell::geom::taxonomy::bspline_surface)
vector_of_item(ifcopenshell::geom::taxonomy::circle)
vector_of_item(ifcopenshell::geom::taxonomy::collection)
vector_of_item(ifcopenshell::geom::taxonomy::colour)
vector_of_item(ifcopenshell::geom::taxonomy::cylinder)
vector_of_item(ifcopenshell::geom::taxonomy::direction3)
vector_of_item(ifcopenshell::geom::taxonomy::edge)
vector_of_item(ifcopenshell::geom::taxonomy::ellipse)
vector_of_item(ifcopenshell::geom::taxonomy::extrusion)
vector_of_item(ifcopenshell::geom::taxonomy::face)
vector_of_item(ifcopenshell::geom::taxonomy::line)
vector_of_item(ifcopenshell::geom::taxonomy::loft)
vector_of_item(ifcopenshell::geom::taxonomy::loop)
vector_of_item(ifcopenshell::geom::taxonomy::matrix4)
vector_of_item(ifcopenshell::geom::taxonomy::node)
vector_of_item(ifcopenshell::geom::taxonomy::offset_curve)
vector_of_item(ifcopenshell::geom::taxonomy::piecewise_function)
vector_of_item(ifcopenshell::geom::taxonomy::plane)
vector_of_item(ifcopenshell::geom::taxonomy::point3)
vector_of_item(ifcopenshell::geom::taxonomy::revolve)
vector_of_item(ifcopenshell::geom::taxonomy::shell)
vector_of_item(ifcopenshell::geom::taxonomy::solid)
vector_of_item(ifcopenshell::geom::taxonomy::sphere)
vector_of_item(ifcopenshell::geom::taxonomy::torus)
vector_of_item(ifcopenshell::geom::taxonomy::style)
vector_of_item(ifcopenshell::geom::taxonomy::sweep_along_curve)
vector_of_item(ifcopenshell::geom::taxonomy::geom_item)
