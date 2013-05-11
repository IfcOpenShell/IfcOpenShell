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

%typemap(out) const double* {
	// This is only used for RGB colours, hence the size of 3
	$result = PyTuple_New(3);
	for (int i = 0; i < 3; ++i) {
		PyTuple_SetItem($result, i, PyFloat_FromDouble($1[i]));
	}
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

%include "Interface.h"

%module IfcImport %{
	#include "Interface.h"
	using namespace IfcGeomObjects;
%}

%extend IfcGeomObjects::IfcRepresentationTriangulation {
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
		def __repr__(self): return "RepresentationTriangulation #%d"%self.id
    %}
};

%extend IfcGeomObjects::IfcRepresentationBrepData {
	%pythoncode %{
		if _newclass:
			# Hide the getters with read-only property implementations
			id = property(id)
			brep_data = property(brep_data)
		def __repr__(self): return "RepresentationBrepData #%d"%self.id
    %}
};

%extend IfcGeomObjects::IfcObject {
	%pythoncode %{
		if _newclass:
			# Hide the getters with read-only property implementations
			id = property(id)
			parent_id = property(parent_id)
			name = property(name)
			type = property(type)
			guid = property(guid)
			matrix = property(matrix)
		def __repr__(self): return "Object #%d"%self.id
    %}
};

%extend IfcGeomObjects::IfcGeomObject {
	%pythoncode %{
		if _newclass:
			# Hide the getters with read-only property implementations
			mesh = property(mesh)
		def __repr__(self): return "GeomObject #%d"%self.id
    %}
};

%extend IfcGeomObjects::IfcGeomBrepDataObject {
	%pythoncode %{
		if _newclass:
			# Hide the getters with read-only property implementations
			mesh = property(mesh)
		def __repr__(self): return "GeomBrepDataObject #%d"%self.id
    %}
};

%extend IfcGeomObjects::Material {
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
		def __repr__(self): return "Material"
    %}
};

namespace std {
	%template(IntVector) vector<int>;
	%template(FloatVector) vector<float>;
	%template(MaterialVector) vector<IfcGeomObjects::Material>;
};