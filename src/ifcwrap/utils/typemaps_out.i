%typemap(out) IfcEntityList::ptr {
	const unsigned size = $1 ? $1->size() : 0;
	$result = PyTuple_New(size);
	for (unsigned i = 0; i < size; ++i) {
		PyTuple_SetItem($result, i, pythonize((*$1)[i]));
	}
}

%typemap(out) IfcUtil::ArgumentType {
	$result = SWIG_Python_str_FromChar(IfcUtil::ArgumentTypeToString($1));
}

%typemap(out) std::pair<IfcUtil::ArgumentType, Argument*> {
	// The SWIG %exception directive does not take care
	// of our typemap. So the attribute conversion block
	// is wrapped in a try-catch block manually.
	try {
	const Argument& arg = *($1.second);
	const IfcUtil::ArgumentType type = $1.first;
	if (arg.isNull() || type == IfcUtil::Argument_DERIVED) {
		Py_INCREF(Py_None);
		$result = Py_None;
	} else {
	switch(type) {
		case IfcUtil::Argument_INT: {
			int v = arg;
			$result = pythonize(v);
		break; }
		case IfcUtil::Argument_BOOL: {
			bool v = arg;
			$result = pythonize(v);
		break; }
		case IfcUtil::Argument_DOUBLE: {
			double v = arg;
			$result = pythonize(v);
		break; }
		case IfcUtil::Argument_ENUMERATION:
		case IfcUtil::Argument_STRING: {
			std::string v = arg;
			$result = pythonize(v);
		break; }
		case IfcUtil::Argument_BINARY: {
			boost::dynamic_bitset<> v = arg;
			$result = pythonize(v);
		break; }
		case IfcUtil::Argument_AGGREGATE_OF_INT: {
			std::vector<int> v = arg;
			$result = pythonize_vector(v);
		break; }
		case IfcUtil::Argument_AGGREGATE_OF_DOUBLE: {
			std::vector<double> v = arg;
			$result = pythonize_vector(v);
		break; }
		case IfcUtil::Argument_AGGREGATE_OF_STRING: {
			std::vector<std::string> v = arg;
			$result = pythonize_vector(v);
		break; }
		case IfcUtil::Argument_ENTITY_INSTANCE: {
			IfcUtil::IfcBaseClass* v = arg;
			$result = pythonize(v);
		break; }
		case IfcUtil::Argument_AGGREGATE_OF_ENTITY_INSTANCE: {
			IfcEntityList::ptr v = arg;
			$result = pythonize(v);
		break; }
		case IfcUtil::Argument_AGGREGATE_OF_BINARY: {
			std::vector< boost::dynamic_bitset<> > v = arg;
			$result = pythonize_vector(v);
		break; }
		case IfcUtil::Argument_AGGREGATE_OF_AGGREGATE_OF_INT: {
			std::vector< std::vector<int> > v = arg;
			$result = pythonize_vector2(v);
		break; }
		case IfcUtil::Argument_AGGREGATE_OF_AGGREGATE_OF_DOUBLE: {
			std::vector< std::vector<double> > v = arg;
			$result = pythonize_vector2(v);
		break; }
		case IfcUtil::Argument_AGGREGATE_OF_AGGREGATE_OF_ENTITY_INSTANCE: {
			IfcEntityListList::ptr v = arg;
			$result = pythonize(v);
		break; }
		case IfcUtil::Argument_UNKNOWN:
		default:
			SWIG_exception(SWIG_RuntimeError,"Unknown attribute type");
		break;
	}
	}
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

CREATE_VECTOR_TYPEMAP_OUT(int)
CREATE_VECTOR_TYPEMAP_OUT(unsigned int)
CREATE_VECTOR_TYPEMAP_OUT(double)
CREATE_VECTOR_TYPEMAP_OUT(std::string)
CREATE_VECTOR_TYPEMAP_OUT(IfcGeom::Material)
