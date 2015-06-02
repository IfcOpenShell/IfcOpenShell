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

%include "std_vector.i"
%include "std_string.i"
%include "exception.i"

%exception {
	try {
		$action
	} catch(IfcParse::IfcException& e) {
		SWIG_exception(SWIG_RuntimeError, e.what());
	} catch(std::runtime_error& e) {
		SWIG_exception(SWIG_RuntimeError, e.what());
	} catch(...) {
		SWIG_exception(SWIG_RuntimeError, "An unknown error occurred");
	}
}

%module ifcopenshell_wrapper %{
	#include "../ifcgeom/IfcGeom.h"
	#include "../ifcgeom/IfcGeomIterator.h"

	#include "../ifcparse/IfcFile.h"
	#include "../ifcparse/IfcLateBoundEntity.h"
%}

// The following typemaps are an alternative for the read-only std::vector
// implementations provided by SWIG, as passing STL objects across dynamic
// library boundaries can be problematic.
%typemap(out) std::pair<const float*, unsigned> {
	$result = PyTuple_New($1.second);
	for (unsigned i = 0; i < $1.second; ++i) {
		PyTuple_SetItem($result, i, PyFloat_FromDouble($1.first[i]));
	}
}
%typemap(out) std::pair<const double*, unsigned> {
	$result = PyTuple_New($1.second);
	for (unsigned i = 0; i < $1.second; ++i) {
		PyTuple_SetItem($result, i, PyFloat_FromDouble($1.first[i]));
	}
}
%typemap(out) std::pair<const int*, unsigned> {
	$result = PyTuple_New($1.second);
	for (unsigned i = 0; i < $1.second; ++i) {
		PyTuple_SetItem($result, i, PyLong_FromLong($1.first[i]));
	}
}
%typemap(out) std::pair<const std::string*, unsigned> {
	$result = PyTuple_New($1.second);
	for (unsigned i = 0; i < $1.second; ++i) {
		PyTuple_SetItem($result, i, PyUnicode_FromString($1.first[i]->c_str()));
	}
}
%typemap(out) std::pair<const IfcGeom::Material*, unsigned> {
	$result = PyTuple_New($1.second);
	for (unsigned i = 0; i < $1.second; ++i) {
		PyTuple_SetItem($result, i, SWIG_NewPointerObj(SWIG_as_voidptr(&$1.first[i]), SWIGTYPE_p_IfcGeom__Material, 0));
	}
}
%typemap(out) std::vector<unsigned> {
	$result = PyTuple_New($1.size());
	unsigned i = 0;
	for (std::vector<unsigned>::const_iterator it = $1.begin(); it != $1.end(); ++it) {
		PyTuple_SetItem($result, i++, PyLong_FromLong(*it));
	}
}

%include "IfcGeomWrapper.i"
%include "IfcParseWrapper.i"
