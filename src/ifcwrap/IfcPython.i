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

namespace std {
	%template(int_vector) vector<int>;
	%template(float_vector) vector<float>;
	%template(double_vector) vector<double>;
	%template(string_vector) vector<std::string>;
	%template(material_vector) vector<IfcGeom::Material>;
};

%include "IfcGeomWrapper.i"
%include "IfcParseWrapper.i"
