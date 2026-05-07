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

%{
	#include <array>
%}
%template(DoubleArray3) std::array<double, 3>;

%ignore IfcGeom::NumberNativeDouble;
%ignore ifcopenshell::geometry::Converter;

// Not relevant for python: new_IfcBaseClass() calls instantiate()
%ignore schema_definition::instantiate;

// Irrelevant abstract base that only has anonymous concrete implementations
%ignore instance_factory;

// Not relevant for python usage
%ignore express::Base::data;
%ignore *::references_to_resolve;

// SVG serializer internal
%ignore geometry_data;
%ignore vertical_section;
%ignore horizontal_plan;
%ignore storey_sorter;
%ignore layerset_information;

// taxonomy
// - tuples
%ignore curves;
%ignore surfaces;
%ignore upgrades;

%ignore loop_to_face_upgrade_impl;
%ignore curve_to_edge_upgrade_impl;
%ignore curve_to_loop_upgrade_impl;
%ignore edge_to_loop_upgrade_impl;
%ignore curve_to_face_upgrade_impl;
%ignore loop_to_function_item_upgrade_impl;

%ignore IfcGeom::geometry_exception;
%ignore IfcGeom::too_many_faces_exception;
%ignore ifcopenshell::geometry::taxonomy::topology_error;

// settings, can this done more generally?
// GeometrySerializer.h
%ignore UseElementNames;
%ignore UseElementGuids;
%ignore UseElementStepIds;
%ignore UseElementTypes;
%ignore UseYUp;
%ignore WriteGltfEcef;
%ignore FloatingPointDigits;
%ignore BaseUri;
%ignore WktUseSection;
%ignore SeparateZUpNode;
// ConversionSettings.h
%ignore MesherLinearDeflection;
%ignore MesherAngularDeflection;
%ignore ReorientShells;
%ignore LengthUnit;
%ignore PlaneUnit;
%ignore Precision;
%ignore LayersetFirst;
%ignore DisableBooleanResult;
%ignore NoWireIntersectionCheck;
%ignore NoWireIntersectionTolerance;
%ignore PrecisionFactor;
%ignore DebugBooleanOperations;
%ignore BooleanAttempt2d;
%ignore WeldVertices;
%ignore UseWorldCoords;
%ignore UnifyShapes;
%ignore UseMaterialNames;
%ignore ConvertBackUnits;
%ignore ContextIds;
%ignore ContextTypes;
%ignore ContextIdentifiers;
%ignore OutputDimensionality;
%ignore IteratorOutput;
%ignore DisableOpeningSubtractions;
%ignore ApplyDefaultMaterials;
%ignore DontEmitNormals;
%ignore GenerateUvs;
%ignore ApplyLayerSets;
%ignore UseElementHierarchy;
%ignore ValidateQuantities;
%ignore EdgeArrows;
%ignore SiteLocalPlacement;
%ignore BuildingLocalPlacement;
%ignore NoParallelMapping;
%ignore PermissiveShapeReuse;
%ignore ForceSpaceTransparency;
%ignore CircleSegments;
%ignore CgalSmoothAngleDegrees;
%ignore KeepBoundingBoxes;
%ignore SurfaceColour;
%ignore ComputeCurvature;
%ignore FunctionStepType;
%ignore FunctionStepParam;
%ignore ModelOffset;
%ignore ModelRotation;
%ignore TriangulationType;
%ignore CgalEmitOriginalEdges;
%ignore OcctNoCleanTriangulation;
%ignore CacheShapes;
%ignore MakeVolume;
%ignore DeferProcessingFirstElement;
%ignore MaxOffset;
%ignore MaxOffsetDeviation;
%ignore ApplyOffset;

// Triangulated representation helper struct
%ignore EdgeKey;

// General python-specific rename rules for comparison operators.
// Mostly to silence warnings, but might be of use some time.
%rename("__eq__") operator ==;
%rename("__lt__") operator <;

%exception {
	try {
		$action
	} catch(const ifcopenshell::attribute_out_of_range_exception& e) {
		SWIG_exception(SWIG_IndexError, e.what());
	} catch(const ifcopenshell::exception& e) {
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
	#include "../ifcgeom/tree.h"
	#include "../ifcgeom/Serialization/Serialization.h"
	#include "../ifcgeom/taxonomy.h"
	#include "../ifcgeom/function_item_evaluator.h"

	#include "../ifcparse/express.h"
	#include "../ifcparse/file.h"
	#include "../ifcparse/schema.h"
	#include "../ifcparse/utils.h"

	#include "../ifcgeom/ConversionSettings.h"
	#include "../ifcgeom/ConversionResult.h"

	#include "../svgfill/src/svgfill.h"

	// @todo abstract into plug-in interface
	#include "../serializers/RocksDbSerializer.h"
%}

// Create docstrings for generated python code.
%feature("autodoc", "1");

%include "utils/type_conversion.i"

%include "utils/typemaps_in.i"

%include "utils/typemaps_out.i"

%module ifcopenshell_wrapper %{
	#include "../ifcgeom/Converter.h"
	#include "../ifcgeom/tree.h"
	#include "../ifcgeom/Serialization/Serialization.h"
	#include "../ifcgeom/taxonomy.h"
	#include "../ifcgeom/function_item_evaluator.h"
	#include "../ifcgeom/Iterator.h"
	#include "../ifcgeom/ConversionResult.h"
	#include "../ifcgeom/hybrid_kernel.h"

	#include "../ifcparse/express.h"
	#include "../ifcparse/file.h"
	#include "../ifcparse/schema.h"
	#include "../ifcparse/utils.h"
	
	#include "../ifcgeom/ConversionSettings.h"
	#include "../ifcgeom/ConversionResult.h"

	#include "../svgfill/src/svgfill.h"

	// @todo abstract into plug-in interface
	#include "../serializers/RocksDbSerializer.h"
%}

%{
#include <string>
#include <vector>
namespace ifcopenshell {
namespace plugin {
void set_search_paths(const std::vector<std::string>& paths);
std::vector<std::string> search_paths();
void clear_search_paths();
}
}
%}

%inline %{
void set_plugin_search_paths(const std::vector<std::string>& paths) {
	ifcopenshell::plugin::set_search_paths(paths);
}

std::vector<std::string> get_plugin_search_paths() {
	return ifcopenshell::plugin::search_paths();
}

void clear_plugin_search_paths() {
	ifcopenshell::plugin::clear_search_paths();
}
%}

%include "IfcGeomWrapper.i"
%include "IfcParseWrapper.i"
