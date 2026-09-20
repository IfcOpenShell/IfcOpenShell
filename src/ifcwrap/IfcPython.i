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
%include "std_unique_ptr.i"

%{
	#include <array>
%}
%template(DoubleArray3) std::array<double, 3>;

%ignore ifcopenshell::geom::converter;

// Not relevant for python: new_IfcBaseClass() calls instantiate()
%ignore schema_definition::instantiate;

// Irrelevant abstract base that only has anonymous concrete implementations
%ignore instance_factory;

%ignore ifcopenshell::schema_registry;
%ignore ifcopenshell::schema_registry_instance;
%ignore ifcopenshell::schema_plugin_registration_symbol;
%ignore ifcopenshell::schema_plugin_metadata;
%ignore ifcopenshell::schema_plugin_directory;
%ignore ifcopenshell::load_schema_plugins;
%ignore ifcopenshell::detail::performance_scope;

// Not relevant for python usage
%ignore express::base::data;
%ignore express::base::data_weak;
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

%ignore ifcopenshell::geom::geometry_exception;
%ignore ifcopenshell::geom::too_many_faces_exception;
%ignore ifcopenshell::geom::taxonomy::topology_error;

// settings, can this done more generally?
// geometry_serializer.h
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
%ignore SvgBounds;
%ignore SvgScale;
%ignore SvgCenter;
%ignore SvgSectionRef;
%ignore SvgElevationRef;
%ignore SvgElevationRefGuid;
%ignore SvgAutoSection;
%ignore SvgAutoElevation;
%ignore SvgDrawStoreyHeights;
%ignore SvgProfileThreshold;
%ignore SvgStoreyHeightLineLength;
%ignore SvgUseNamespace;
%ignore SvgUseHlrPoly;
%ignore SvgUsePrefiltering;
%ignore SvgUnifyInputs;
%ignore SvgSegmentProjection;
%ignore SvgSubtractBefore;
%ignore SvgPolygonal;
%ignore SvgAlwaysProject;
%ignore SvgWithoutStoreys;
%ignore SvgNoCss;
%ignore SvgMirrorY;
%ignore SvgMirrorX;
%ignore SvgDoorArcs;
%ignore SvgSectionHeight;
%ignore SvgSectionHeightFromStoreys;
%ignore SvgPrintSpaceNames;
%ignore SvgPrintSpaceAreas;
%ignore SvgSpaceNameTransform;
// conversion_settings.h
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
%ignore ContextPriorities;
%ignore OutputDimensionality;
%ignore MaxVoidsPerElement;
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
%ignore SvgRidgeAngleMinDegrees;
%ignore SvgValleyAngleMinDegrees;
%ignore SvgEmitFlushEdges;
%ignore SvgUseEdgeClassification;
%ignore SvgRenderCreaseEdges;
%ignore SvgRenderSharpEdges;

%ignore filetype;
%ignore guess_file_type;

// Triangulated representation helper struct
%ignore edge_key;

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
	#include "../ifcgeom/iterator.h"
	#include "../ifcgeom/tree.h"
	#include "../ifcgeom/serialization/serialization.h"
	#include "../ifcgeom/taxonomy.h"
	#include "../ifcgeom/function_item_evaluator.h"

	#include "../ifcparse/express.h"
	#include "../ifcparse/file.h"
	#include "../ifcparse/schema.h"
	#include "../ifcparse/utils.h"

	#include "../ifcgeom/conversion_settings.h"
	#include "../ifcgeom/conversion_result.h"

	#include "../svgfill/src/svgfill.h"

	// @todo abstract into plug-in interface
	#include "../serializers/rocks_db_serializer.h"

	using ifcopenshell::attribute_value;
	using ifcopenshell::blank;
	using ifcopenshell::derived;
	using ifcopenshell::empty_aggregate;
	using ifcopenshell::empty_aggregate_of_aggregate;
	using ifcopenshell::enumeration_reference;
%}

// Create docstrings for generated python code.
%feature("autodoc", "1");

%include "utils/type_conversion.i"

%include "utils/typemaps_in.i"

%include "utils/typemaps_out.i"

%module ifcopenshell_wrapper %{
	#include "../ifcgeom/converter.h"
	#include "../ifcgeom/tree.h"
	#include "../ifcgeom/serialization/serialization.h"
	#include "../ifcgeom/taxonomy.h"
	#include "../ifcgeom/function_item_evaluator.h"
	#include "../ifcgeom/iterator.h"
	#include "../ifcgeom/conversion_result.h"
	#include "../ifcgeom/hybrid_kernel.h"
	#include "../ifcgeom/geometry_serializer.h"
	#include "../ifcgeom/kernel_plugin.h"

	#include "../ifcparse/express.h"
	#include "../ifcparse/file.h"
	#include "../ifcparse/schema.h"
	#include "../ifcparse/utils.h"

	#include "../ifcgeom/conversion_settings.h"
	#include "../ifcgeom/conversion_result.h"

	#include "../svgfill/src/svgfill.h"

	// @todo abstract into plug-in interface
	#include "../serializers/rocks_db_serializer.h"
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

bool has_geometry_library(const std::string& geometry_library) {
	auto& registry = ifcopenshell::geom::kernels::kernel_registry_instance();
	try {
		return registry.has(geometry_library) ||
			ifcopenshell::geom::kernels::load_kernel_plugin(registry, geometry_library);
	} catch (const std::exception&) {
		return false;
	}
}
%}

%include "IfcGeomWrapper.i"
%include "IfcParseWrapper.i"
