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

%begin %{
#if defined(_DEBUG) && defined(SWIG_PYTHON_INTERPRETER_NO_DEBUG)
/* https://github.com/swig/swig/issues/325 */
# include <basetsd.h>
# include <assert.h>
# include <ctype.h>
# include <errno.h>
# include <io.h>
# include <math.h>
# include <sal.h>
# include <stdarg.h>
# include <stddef.h>
# include <stdio.h>
# include <stdlib.h>
# include <string.h>
# include <sys/stat.h>
# include <time.h>
# include <wchar.h>
#endif

#ifdef _MSC_VER
# pragma warning(push)
# pragma warning(disable : 4127 4244 4702 4510 4512 4610)
# if _MSC_VER > 1800
#  pragma warning(disable : 4456 4459)
# endif
#endif
// TODO add '# pragma warning(pop)' to the very end of the file
%}

%include "stdint.i"
%include "std_array.i"
%include "std_vector.i"
%include "std_string.i"
%include "exception.i"
%include "std_shared_ptr.i"

%ignore IfcGeom::NumberNativeDouble;
%ignore ifcopenshell::geometry::Converter;

// General python-specific rename rules for comparison operators.
// Mostly to silence warnings, but might be of use some time.
%rename("__eq__") operator ==;
%rename("__lt__") operator <;

%exception {
	try {
		$action
	} catch(const IfcParse::IfcAttributeOutOfRangeException& e) {
		SWIG_exception(SWIG_IndexError, e.what());
	} catch(const IfcParse::IfcException& e) {
		SWIG_exception(SWIG_RuntimeError, e.what());
	} catch(const std::runtime_error& e) {
		SWIG_exception(SWIG_RuntimeError, e.what());
	} catch(...) {
		SWIG_exception(SWIG_RuntimeError, "An unknown error occurred");
	}
}

%include "../serializers/serializers_api.h"

// Include headers for the typemaps to function. This set of includes,
// can probably be reduced, but for now it's identical to the includes
// of the module definition below.
%{
	#include "../ifcgeom/Iterator.h"
	#include "../ifcgeom/taxonomy.h"
#ifdef IFOPSH_WITH_OPENCASCADE
	#include "../ifcgeom/Serialization/Serialization.h"
	#include "../ifcgeom/kernels/opencascade/IfcGeomTree.h"

	#include <BRepTools_ShapeSet.hxx>
#endif

	#include "../serializers/SvgSerializer.h"
	#include "../serializers/WavefrontObjSerializer.h"
	#include "../serializers/HdfSerializer.h"
	
#ifdef HAS_SCHEMA_2x3
	#include "../ifcparse/Ifc2x3.h"
#endif
#ifdef HAS_SCHEMA_4
	#include "../ifcparse/Ifc4.h"
#endif
#ifdef HAS_SCHEMA_4x1
	#include "../ifcparse/Ifc4x1.h"
#endif
#ifdef HAS_SCHEMA_4x2
	#include "../ifcparse/Ifc4x2.h"
#endif
#ifdef HAS_SCHEMA_4x3_rc1
	#include "../ifcparse/Ifc4x3_rc1.h"
#endif
#ifdef HAS_SCHEMA_4x3_rc2
	#include "../ifcparse/Ifc4x3_rc2.h"
#endif
#ifdef HAS_SCHEMA_4x3_rc3
#include "../ifcparse/Ifc4x3_rc3.h"
#endif
#ifdef HAS_SCHEMA_4x3_rc4
#include "../ifcparse/Ifc4x3_rc4.h"
#endif
#ifdef HAS_SCHEMA_4x3
#include "../ifcparse/Ifc4x3.h"
#endif
#ifdef HAS_SCHEMA_4x3_tc1
#include "../ifcparse/Ifc4x3_tc1.h"
#endif
#ifdef HAS_SCHEMA_4x3_add1
#include "../ifcparse/Ifc4x3_add1.h"
#endif
#ifdef HAS_SCHEMA_4x3_add2
#include "../ifcparse/Ifc4x3_add2.h"
#endif

	#include "../ifcparse/IfcBaseClass.h"
	#include "../ifcparse/IfcFile.h"
	#include "../ifcparse/IfcSchema.h"
	#include "../ifcparse/utils.h"

	#include "../ifcgeom/ConversionSettings.h"
	#include "../ifcgeom/ConversionResult.h"

	#include "../svgfill/src/svgfill.h"

#ifdef IFOPSH_WITH_CGAL
	#include "../ifcgeom/kernels/cgal/CgalConversionResult.h"
#endif
%}

// Create docstrings for generated python code.
%feature("autodoc", "1");

%include "utils/type_conversion.i"

%include "utils/typemaps_in.i"

%include "utils/typemaps_out.i"

%module ifcopenshell_wrapper %{
	#include "../ifcgeom/Converter.h"
	#include "../ifcgeom/taxonomy.h"
#ifdef IFOPSH_WITH_OPENCASCADE
	#include "../ifcgeom/Serialization/Serialization.h"
	#include "../ifcgeom/kernels/opencascade/IfcGeomTree.h"

	#include <BRepTools_ShapeSet.hxx>
#endif
	#include "../ifcgeom/Iterator.h"
	#include "../ifcgeom/ConversionResult.h"

	#include "../serializers/SvgSerializer.h"
	#include "../serializers/WavefrontObjSerializer.h"
	#include "../serializers/HdfSerializer.h"
	#include "../serializers/XmlSerializer.h"
	#include "../serializers/GltfSerializer.h"
	
#ifdef HAS_SCHEMA_2x3
	#include "../ifcparse/Ifc2x3.h"
#endif
#ifdef HAS_SCHEMA_4
	#include "../ifcparse/Ifc4.h"
#endif
#ifdef HAS_SCHEMA_4x1
	#include "../ifcparse/Ifc4x1.h"
#endif
#ifdef HAS_SCHEMA_4x2
	#include "../ifcparse/Ifc4x2.h"
#endif
#ifdef HAS_SCHEMA_4x3_rc1
	#include "../ifcparse/Ifc4x3_rc1.h"
#endif
#ifdef HAS_SCHEMA_4x3_rc2
	#include "../ifcparse/Ifc4x3_rc2.h"
#endif
#ifdef HAS_SCHEMA_4x3_rc3
	#include "../ifcparse/Ifc4x3_rc3.h"
#endif
#ifdef HAS_SCHEMA_4x3_rc4
	#include "../ifcparse/Ifc4x3_rc4.h"
#endif
#ifdef HAS_SCHEMA_4x3
	#include "../ifcparse/Ifc4x3.h"
#endif
#ifdef HAS_SCHEMA_4x3_tc1
	#include "../ifcparse/Ifc4x3_tc1.h"
#endif
#ifdef HAS_SCHEMA_4x3_add1
	#include "../ifcparse/Ifc4x3_add1.h"
#endif
#ifdef HAS_SCHEMA_4x3_add2
	#include "../ifcparse/Ifc4x3_add2.h"
#endif

	#include "../ifcparse/IfcBaseClass.h"
	#include "../ifcparse/IfcFile.h"
	#include "../ifcparse/IfcSchema.h"
	#include "../ifcparse/utils.h"
	
	#include "../ifcgeom/ConversionSettings.h"
	#include "../ifcgeom/ConversionResult.h"

	#include "../svgfill/src/svgfill.h"
%}

%include "IfcGeomWrapper.i"
%include "IfcParseWrapper.i"
%include "std_vector.i"
	
namespace std {
  %template(float_array_3) array<double, 3>;
  %template(FloatVector) vector<float>;
  %template(IntVector) std::vector<int>;
  %template(DoubleVector) std::vector<double>;
  %template(StringVector) std::vector<std::string>;
  %template(FloatVectorVector) std::vector<std::vector<float>>;
  %template(DoubleVectorVector) std::vector<std::vector<double>>;
}
