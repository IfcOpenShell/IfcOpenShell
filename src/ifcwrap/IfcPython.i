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

%include "Interface.h"

%module IfcImport %{
	#include "Interface.h"
	using namespace IfcGeom;
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

namespace std {
	%template(IntVector) vector<int>;
	%template(FloatVector) vector<float>;
};