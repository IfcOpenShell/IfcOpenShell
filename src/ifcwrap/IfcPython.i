/********************************************************************************
 *																		      *
 * This file is part of IfcOpenShell.										   *
 *																		      *
 * IfcOpenShell is free software: you can redistribute it and/or modify		 *
 * it under the terms of the Lesser GNU General Public License as published by  *
 * the Free Software Foundation, either version 3.0 of the License, or		  *
 * (at your option) any later version.										  *
 *																		      *
 * IfcOpenShell is distributed in the hope that it will be useful,		      *
 * but WITHOUT ANY WARRANTY; without even the implied warranty of		       *
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the				 *
 * Lesser GNU General Public License for more details.						  *
 *																		      *
 * You should have received a copy of the Lesser GNU General Public License     *
 * along with this program. If not, see <http://www.gnu.org/licenses/>.		 *
 *																		      *
 ********************************************************************************/

%include "std_vector.i"
%include "std_string.i"
%include "exception.i"

// This is only used for RGB colours, hence the size of 3
%typemap(out) const double* {
	$result = PyTuple_New(3);
	for (int i = 0; i < 3; ++i) {
		PyTuple_SetItem($result, i, PyFloat_FromDouble($1[i]));
	}
}

// Using RTTI return a more specialized type of Element
%typemap(out) IfcGeom::Element<float>* {
	IfcGeom::SerializedElement<float>* serialized_elem = dynamic_cast<IfcGeom::SerializedElement<float>*>($1);
	IfcGeom::TriangulationElement<float>* triangulation_elem = dynamic_cast<IfcGeom::TriangulationElement<float>*>($1);
	if (triangulation_elem) {
		$result = SWIG_NewPointerObj(SWIG_as_voidptr(triangulation_elem), SWIGTYPE_p_IfcGeom__TriangulationElementT_float_t, 0);
	} else if (serialized_elem) {
		$result = SWIG_NewPointerObj(SWIG_as_voidptr(serialized_elem), SWIGTYPE_p_IfcGeom__SerializedElementT_float_t, 0);
	}
}

// Using RTTI return a more specialized type of Element
%typemap(out) IfcGeom::Element<double>* {
	IfcGeom::SerializedElement<double>* serialized_elem = dynamic_cast<IfcGeom::SerializedElement<double>*>($1);
	IfcGeom::TriangulationElement<double>* triangulation_elem = dynamic_cast<IfcGeom::TriangulationElement<double>*>($1);
	if (triangulation_elem) {
		$result = SWIG_NewPointerObj(SWIG_as_voidptr(triangulation_elem), SWIGTYPE_p_IfcGeom__TriangulationElementT_double_t, 0);
	} else if (serialized_elem) {
		$result = SWIG_NewPointerObj(SWIG_as_voidptr(serialized_elem), SWIGTYPE_p_IfcGeom__SerializedElementT_double_t, 0);
	}
}

// SWIG does not support bool references in a meaningful way, so the
// IfcGeom::IteratorSettings functions degrade to return a read only value
%typemap(out) double& {
	$result = SWIG_From_double(*$1);
}
%typemap(out) bool& {
	$result = PyBool_FromLong(static_cast<long>(*$1));
}

%exception {
	try {
		$action
	} catch(std::runtime_error& e) {
		SWIG_exception(SWIG_RuntimeError, e.what());
	} catch(...) {
		SWIG_exception(SWIG_RuntimeError, "An unknown error occurred");
	}
}

%include "../ifcgeom/IfcGeomIteratorSettings.h"
%include "../ifcgeom/IfcGeomMaterial.h"
%include "../ifcgeom/IfcGeomRepresentation.h"
%include "../ifcgeom/IfcGeomElement.h"
%include "../ifcgeom/IfcGeomIterator.h"

// This does not seem to work:
%ignore IfcGeom::Iterator<float>::Iterator(const IfcGeom::IteratorSettings&, IfcParse::IfcFile*);
%ignore IfcGeom::Iterator<float>::Iterator(const IfcGeom::IteratorSettings&, void*, int);
%ignore IfcGeom::Iterator<float>::Iterator(const IfcGeom::IteratorSettings&, std::istream&, int);
%ignore IfcGeom::Iterator<double>::Iterator(const IfcGeom::IteratorSettings&, IfcParse::IfcFile*);
%ignore IfcGeom::Iterator<double>::Iterator(const IfcGeom::IteratorSettings&, void*, int);
%ignore IfcGeom::Iterator<double>::Iterator(const IfcGeom::IteratorSettings&, std::istream&, int);

%extend IfcGeom::IteratorSettings {
	%pythoncode %{
		attrs = ("convert_back_units", "deflection_tolerance", "disable_opening_subtractions", "disable_triangulation", "faster_booleans", "force_ccw_face_orientation", "sew_shells", "use_brep_data", "use_world_coords", "weld_vertices")
		def __repr__(self):
			return "IteratorSettings(%s)"%(",".join(tuple("%s=%r"%(a, getattr(self, a)()) for a in self.attrs)))
	%}
}

%module ifcopenshell %{
	#include "../ifcgeom/IfcGeomIteratorSettings.h"
	#include "../ifcgeom/IfcGeomMaterial.h"
	#include "../ifcgeom/IfcGeomRepresentation.h"
	#include "../ifcgeom/IfcGeomElement.h"
	#include "../ifcgeom/IfcGeomIterator.h"

	using namespace IfcGeom;
%}

%extend IfcGeom::Iterator<float> {
	static int mantissa_size() {
		return std::numeric_limits<float>::digits;
	}
};

%extend IfcGeom::Iterator<double> {
	static int mantissa_size() {
		return std::numeric_limits<double>::digits;
	}
};

%extend IfcGeom::Representation::Triangulation {
    %pythoncode %{
		if _newclass:
			# Hide the getters with read-only property implementations
			id = property(id)
			verts = property(verts)
			faces = property(faces)
			edges = property(edges)
			normals = property(normals)
			material_ids = property(material_ids)
			materials = property(materials)
    %}
};

%extend IfcGeom::Representation::Serialization {
	%pythoncode %{
		if _newclass:
			# Hide the getters with read-only property implementations
			id = property(id)
			brep_data = property(brep_data)
    %}
};

%extend IfcGeom::Element {
	%pythoncode %{
		if _newclass:
			# Hide the getters with read-only property implementations
			id = property(id)
			parent_id = property(parent_id)
			name = property(name)
			type = property(type)
			guid = property(guid)
			transformation = property(transformation)
    %}
};

%extend IfcGeom::TriangulationElement {
	%pythoncode %{
		if _newclass:
			# Hide the getters with read-only property implementations
			geometry = property(geometry)
    %}
};

%extend IfcGeom::SerializedElement {
	%pythoncode %{
		if _newclass:
			# Hide the getters with read-only property implementations
			geometry = property(geometry)
    %}
};

%extend IfcGeom::Material {
	%pythoncode %{
		if _newclass:
			# Hide the getters with read-only property implementations
			has_diffuse = property(hasDiffuse)
			has_specular = property(hasSpecular)
			has_transparency = property(hasTransparency)
			has_specularity = property(hasSpecularity)
			diffuse = property(diffuse)
			specular = property(specular)
			transparency = property(transparency)
			specularity = property(specularity)
			name = property(name)
    %}
};

%extend IfcGeom::Transformation {
	%pythoncode %{
		if _newclass:
			# Hide the getters with read-only property implementations
			matrix = property(matrix)
    %}
};

%extend IfcGeom::Matrix {
	%pythoncode %{
		if _newclass:
			# Hide the getters with read-only property implementations
			data = property(data)
    %}
};

namespace std {
	%template(IntVector) vector<int>;
	%template(FloatVector) vector<float>;
	%template(DoubleVector) vector<double>;
	%template(MaterialVector) vector<IfcGeom::Material>;
};

namespace IfcGeom {
	%template(IteratorSinglePrecision) Iterator<float>;
	%template(IteratorDoublePrecision) Iterator<double>;

	%template(ElementSinglePrecision) Element<float>;
	%template(ElementDoublePrecision) Element<double>;

	%template(TriangulationElementSinglePrecision) TriangulationElement<float>;
	%template(TriangulationElementDoublePrecision) TriangulationElement<double>;

	%template(SerializedElementSinglePrecision) SerializedElement<float>;
	%template(SerializedElementDoublePrecision) SerializedElement<double>;

	%template(TransformationSinglePrecision) Transformation<float>;
	%template(TransformationDoublePrecision) Transformation<double>;

	%template(MatrixSinglePrecision) Matrix<float>;
	%template(MatrixDoublePrecision) Matrix<double>;

	namespace Representation {
		%template(TriangulationSinglePrecision) Triangulation<float>;
		%template(TriangulationDoublePrecision) Triangulation<double>;
	};
};

// Hide templating precision to the user by choosing based on Python's 
// internal float type. This is probably always going to be a double.
%pythoncode %{
	import sys
	for ty in (IteratorSinglePrecision, IteratorDoublePrecision):
		if ty.mantissa_size() == sys.float_info.mant_dig: Iterator = ty
%}