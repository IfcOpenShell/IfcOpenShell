#ifndef CONVERSIONSETTINGS_H
#define CONVERSIONSETTINGS_H

#include <array>
#include <limits>
#include <string>
#include <iostream>
#include <map>
#include <tuple>
#include <type_traits>
#include <optional>
#include <variant>
#include <vector>

#include <boost/program_options.hpp>
#include <boost/optional.hpp>
#include <boost/algorithm/string.hpp>

#include "ifc_geom_api.h"

#ifndef SWIG
namespace po = boost::program_options;

namespace std {
	IFC_GEOM_API istream& operator>>(istream& in, set<int>& ints);
	IFC_GEOM_API istream& operator>>(istream& in, set<string>& ints);
	IFC_GEOM_API istream& operator>>(istream& in, vector<double>& vs);
}
#endif

namespace ifcopenshell {
	namespace geom {
		namespace settings_detail {

#ifndef SWIG
			template <typename T, typename U = int>
			struct HasDefault : std::false_type { };

			template <typename T>
			struct HasDefault<T, decltype((void)T::defaultvalue, 0)> : std::true_type { };
#endif

			template <typename Derived, typename T, bool Internal=false>
			struct SettingBase {
				typedef T base_type;

				// boost program options does not seem to handle optional<vector> types, so in case
				// of vector settings we need to strip away the optional and detect argument presence
				// with !vector::empty()
				// tfk: we no longer do this because negative values can not be passed like this as boost confuses them with options
				// std::conditional_t<std::is_same_v<T, std::vector<double>>, T, std::optional<T>> value;
                // tfk: note that we use boost::optional to avoid a lack of deserialization support with std::optional and boost program options
				boost::optional<T> value;

				SettingBase() {}

				void defineOption(po::options_description& desc) {
					auto apply_default = [](auto x) {
						if constexpr (HasDefault<Derived>()) {
							return x->default_value(Derived::defaultvalue);
						} else {
							return x;
						}
					};
					if constexpr (Internal) {
						// do nothing, this is an internal setting and not supposed to be set from the command line
					} else if constexpr (std::is_same_v<T, bool>) {
						// @todo bool_switch doesn't work with optional unfortunately...
						value.emplace();
						desc.add_options()(Derived::name, apply_default(po::bool_switch(&*value)), Derived::description);
					} else if constexpr (std::is_same_v<T, std::vector<double>>) {
						// these options have to be supplied manually in IfcConvert.cpp
						// desc.add_options()(Derived::name, apply_default(po::value(&value)->multitoken()), Derived::description);
					} else {
						desc.add_options()(Derived::name, apply_default(po::value(&value)), Derived::description);
					}
				}

				T get() const {
					if constexpr (false && std::is_same_v<T, std::vector<double>>) {
						return value;
					} else {
						if (value) {
							return value.value();
						}
						if constexpr (HasDefault<Derived>()) {
							return Derived::defaultvalue;
						} else {
						    throw std::runtime_error("Setting not set");
						}
					}
				}

				bool has() const {
					if constexpr (false && std::is_same_v<T, std::vector<double>>) {
						return !value.empty();
					} else {
						// @todo this is not reliable, better use vmap[...].defaulted()
						return !!value;
					}
				}
			};

			// These are the old geometry settings values from the kernel

			struct MesherLinearDeflection : public SettingBase<MesherLinearDeflection, double> {
				static constexpr const char* const name = "mesher-linear-deflection";
				static constexpr const char* const description = "Specifies the linear deflection of the mesher. Controls the detail of curved surfaces in triangulated output formats.";
				static constexpr double defaultvalue = 0.001;
			};

			struct MesherAngularDeflection : public SettingBase<MesherAngularDeflection, double> {
				static constexpr const char* const name = "mesher-angular-deflection";
				static constexpr const char* const description = "Sets the angular tolerance of the mesher in radians 0.5 by default if not specified.";
				static constexpr double defaultvalue = 0.5;
			};

			struct ReorientShells : public SettingBase<ReorientShells, bool> {
				static constexpr const char* const name = "reorient-shells";
				static constexpr const char* const description = "Specifies whether to orient the faces of IfcConnectedFaceSets. This is a potentially time consuming operation, but guarantees a consistent orientation of surface normals, even if the faces are not properly oriented in the IFC file.";
				static constexpr bool defaultvalue = false;
			};

			struct LengthUnit : public SettingBase<LengthUnit, double, true> {
				static constexpr const char* const name = "length-unit";
				static constexpr const char* const description = "";
				static constexpr double defaultvalue = 1.0;
			};

			struct PlaneUnit : public SettingBase<PlaneUnit, double, true> {
				static constexpr const char* const name = "angle-unit";
				static constexpr const char* const description = "";
				static constexpr double defaultvalue = 1.0;
			};

			struct Precision : public SettingBase<Precision, double, true> {
				static constexpr const char* const name = "precision";
				static constexpr const char* const description = "";
				static constexpr double defaultvalue = 0.00001;
			};

			struct LayersetFirst : public SettingBase<LayersetFirst, bool> {
				static constexpr const char* const name = "layerset-first";
				static constexpr const char* const description = "Assigns the first layer material of the layerset to the complete product.";
				static constexpr bool defaultvalue = false;
			};

			struct DisableBooleanResult : public SettingBase<DisableBooleanResult, bool> {
				static constexpr const char* const name = "disable-boolean-result";
				static constexpr const char* const description = "Specifies whether to disable the boolean operation within representations such as clippings by means of IfcBooleanResult and subtypes";
				static constexpr bool defaultvalue = false;
			};

			struct NoWireIntersectionCheck : public SettingBase<NoWireIntersectionCheck, bool> {
				static constexpr const char* const name = "no-wire-intersection-check";
				static constexpr const char* const description = "Skip wire intersection check.";
				static constexpr bool defaultvalue = false;
			};

			struct NoWireIntersectionTolerance : public SettingBase<NoWireIntersectionTolerance, double> {
				static constexpr const char* const name = "no-wire-intersection-tolerance";
				static constexpr const char* const description = "Set wire intersection tolerance to 0.";
				static constexpr bool defaultvalue = false;
			};

			struct PrecisionFactor : public SettingBase<PrecisionFactor, double> {
				static constexpr const char* const name = "precision-factor";
				static constexpr const char* const description = "Option to increase linear tolerance for more permissive edge curves and fewer artifacts after boolean operations at the expense of geometric detail due to vertex collapsing and wire intersection fuzziness.";
				static constexpr double defaultvalue = 1.0;
			};

			struct DebugBooleanOperations : public SettingBase<DebugBooleanOperations, bool> {
				static constexpr const char* const name = "debug";
				static constexpr const char* const description = "write boolean operands to file in current directory for debugging purposes";
				static constexpr bool defaultvalue = false;
			};

			struct BooleanAttempt2d : public SettingBase<BooleanAttempt2d, bool> {
				static constexpr const char* const name = "boolean-attempt-2d";
				static constexpr const char* const description = "Do not attempt to process boolean subtractions in 2D.";
				static constexpr bool defaultvalue = true;
			};

			// These are the old IteratorSettings

			struct WeldVertices : public SettingBase<WeldVertices, bool> {
				static constexpr const char* const name = "weld-vertices";
				static constexpr const char* const description = "Specifies whether vertices are welded, meaning that the coordinates vector will only contain unique xyz-triplets. This results in a manifold mesh which is useful for modelling applications, but might result in unwanted shading artefacts in rendering applications.";
				static constexpr bool defaultvalue = true;
			};

			struct UseWorldCoords : public SettingBase<UseWorldCoords, bool> {
				static constexpr const char* const name = "use-world-coords";
				static constexpr const char* const description = "Specifies whether to apply the local placements of building elements directly to the coordinates of the representation mesh rather than to represent the local placement in the 4x3 matrix, which will in that case be the identity matrix.";
				static constexpr bool defaultvalue = false;
			};

			struct UnifyShapes : public SettingBase<UnifyShapes, bool> {
				static constexpr const char* const name = "unify-shapes";
				static constexpr const char* const description = "Unify adjacent co-planar and co-linear subshapes (topological entities sharing the same geometric domain) before triangulation or further processing";
				static constexpr bool defaultvalue = false;
			};

			struct UseMaterialNames : public SettingBase<UseMaterialNames, bool> {
				static constexpr const char* const name = "use-material-names";
				static constexpr const char* const description = "Use material names instead of unique IDs for naming materials upon serialization. Applicable for OBJ and DAE output.";
				static constexpr bool defaultvalue = false;
			};

			struct ConvertBackUnits : public SettingBase<ConvertBackUnits, bool> {
				static constexpr const char* const name = "convert-back-units";
				static constexpr const char* const description = "Specifies whether to convert back geometrical output back to the unit of measure in which it is defined in the IFC file. Default is to use meters.";
				static constexpr bool defaultvalue = false;
			};

			struct ContextIds : public SettingBase<ContextIds, std::set<int>> {
				static constexpr const char* const name = "context-ids";
				static constexpr const char* const description = "List of comma separated context ids to process - e.g. '15,29' (no quotes needed).";
			};

			struct ContextTypes : public SettingBase<ContextTypes, std::set<std::string>> {
				static constexpr const char* const name = "context-types";
				static constexpr const char* const description = "Currently option has no effect.";
			};

			struct ContextIdentifiers : public SettingBase<ContextIdentifiers, std::set<std::string>> {
				static constexpr const char* const name = "context-identifiers";
				static constexpr const char* const description = "Currently option has no effect.";
			};

			struct ContextPriorities : public SettingBase<ContextPriorities, std::vector<std::string>> {
                static constexpr const char* const name = "context-priorities";
                static constexpr const char* const description = "Selects a representation for product based on the following ordered context queries";
            };

			enum OutputDimensionalityTypes {
				CURVES,
				SURFACES_AND_SOLIDS,
				CURVES_SURFACES_AND_SOLIDS
			};

			IFC_GEOM_API std::istream& operator>>(std::istream& in, OutputDimensionalityTypes& ioo);

			struct OutputDimensionality : public SettingBase<OutputDimensionality, OutputDimensionalityTypes> {
				static constexpr const char* const name = "dimensionality";
				static constexpr const char* const description = "Specifies whether to include curves and/or surfaces and solids in the output result. Defaults to only surfaces and solids (SURFACES_AND_SOLIDS). Other possible values are CURVES, CURVES_SURFACES_AND_SOLIDS.";
				static constexpr OutputDimensionalityTypes defaultvalue = SURFACES_AND_SOLIDS;
			};

			enum IteratorOutputOptions {
				TRIANGULATED,
				NATIVE,
				SERIALIZED
			};

			IFC_GEOM_API std::istream& operator>>(std::istream& in, IteratorOutputOptions& ioo);

			struct IteratorOutput : public SettingBase<IteratorOutput, IteratorOutputOptions> {
				static constexpr const char* const name = "iterator-output";
				static constexpr const char* const description = "";
				static constexpr IteratorOutputOptions defaultvalue = TRIANGULATED;
			};

			struct DisableOpeningSubtractions : public SettingBase<DisableOpeningSubtractions, bool> {
				static constexpr const char* const name = "disable-opening-subtractions";
				static constexpr const char* const description = "Specifies whether to disable the boolean subtraction of IfcOpeningElement Representations from their RelatingElements.";
				static constexpr bool defaultvalue = false;
			};

			struct MaxVoidsPerElement : public SettingBase<MaxVoidsPerElement, int> {
                static constexpr const char* const name = "max-voids-per-element";
                static constexpr const char* const description = "Specifies the maximum number of voids that will be processed per element. 0 means unlimited. No voids will be processed for elements with more voids.";
                static constexpr int defaultvalue = 0;
            };

			struct ApplyDefaultMaterials : public SettingBase<ApplyDefaultMaterials, bool> {
				static constexpr const char* const name = "apply-default-materials";
				static constexpr const char* const description = "";
				static constexpr bool defaultvalue = true;
			};

			struct DontEmitNormals : public SettingBase<DontEmitNormals, bool> {
				static constexpr const char* const name = "no-normals";
				static constexpr const char* const description = "Disables computation of normals.Saves time and file size and is useful in instances where you're going to recompute normals for the exported model in other modelling application in any case.";
				static constexpr bool defaultvalue = false;
			};

			struct GenerateUvs : public SettingBase<GenerateUvs, bool> {
				static constexpr const char* const name = "generate-uvs";
				static constexpr const char* const description = "Generates UVs (texture coordinates) by using simple box projection. Requires normals. Not guaranteed to work properly if used with --weld-vertices.";
				static constexpr bool defaultvalue = false;
			};

			struct ApplyLayerSets : public SettingBase<ApplyLayerSets, bool> {
				static constexpr const char* const name = "enable-layerset-slicing";
				static constexpr const char* const description = "Specifies whether to enable the slicing of products according to their associated IfcMaterialLayerSet.";
				static constexpr bool defaultvalue = false;
			};

			struct UseElementHierarchy : public SettingBase<UseElementHierarchy, bool> {
				static constexpr const char* const name = "element-hierarchy";
				static constexpr const char* const description = "Assign the elements using their e.g IfcBuildingStorey parent.Applicable to DAE output.";
				static constexpr bool defaultvalue = false;
			};

			struct ValidateQuantities : public SettingBase<ValidateQuantities, bool> {
				static constexpr const char* const name = "validate";
				static constexpr const char* const description = "Checks whether geometrical output conforms to the included explicit quantities.";
				static constexpr bool defaultvalue = false;
			};

			struct EdgeArrows : public SettingBase<EdgeArrows, bool> {
				static constexpr const char* const name = "edge-arrows";
				static constexpr const char* const description = "Adds arrow heads to edge segments to signify edge direction";
				static constexpr bool defaultvalue = false;
			};

			struct SiteLocalPlacement : public SettingBase<SiteLocalPlacement, bool> {
				static constexpr const char* const name = "site-local-placement";
				static constexpr const char* const description = "Place elements locally in the IfcSite coordinate system, instead of placing them in the IFC global coords. Applicable for OBJ, DAE, and STP output.";
				static constexpr bool defaultvalue = false;
			};

			struct BuildingLocalPlacement : public SettingBase<BuildingLocalPlacement, bool> {
				static constexpr const char* const name = "building-local-placement";
				static constexpr const char* const description = "Similar to --site-local-placement, but placing elements in locally in the parent IfcBuilding coord system";
				static constexpr bool defaultvalue = false;
			};

			struct NoParallelMapping : public SettingBase<NoParallelMapping, bool> {
				static constexpr const char* const name = "no-parallel-mapping";
				static constexpr const char* const description = "Perform mapping upfront (single-threaded) as opposed to in parallel. May decrease performance, but also decrease output size (in the future)";
				static constexpr bool defaultvalue = false;
			};

			struct PermissiveShapeReuse : public SettingBase<PermissiveShapeReuse, bool> {
				static constexpr const char* const name = "permissive-shape-reuse";
				static constexpr const char* const description = "Traverse geometry-level transformations and apply to product-level placement in order to increase reuse of geometries";
				static constexpr bool defaultvalue = false;
			};

			struct ForceSpaceTransparency : public SettingBase<ForceSpaceTransparency, double> {
				static constexpr const char* const name = "force-space-transparency";
				static constexpr const char* const description = "Overrides transparency of spaces in geometry output.";
			};

			struct CircleSegments : public SettingBase<CircleSegments, int> {
				static constexpr const char* const name = "circle-segments";
				static constexpr const char* const description = "Number of segments to approximate full circles in the CGAL kernel. When 0 (the default) the segment count is derived from mesher-linear-deflection and mesher-angular-deflection instead, whichever is stricter, so curves stay within tolerance regardless of radius.";
				static constexpr int defaultvalue = 0;
			};

			struct CgalSmoothAngleDegrees : public SettingBase<CgalSmoothAngleDegrees, double> {
				static constexpr const char* const name = "cgal-smooth-angle-degrees";
				static constexpr const char* const description = "Angle in degrees under which adjacent facets will have averaged vertex normals in CGAL output. NB irrespective of original IFC geometry types. Defaults to -1 to disable smoothing.";
				static constexpr double defaultvalue = -1.;
			};

			struct SvgRidgeAngleMinDegrees : public SettingBase<SvgRidgeAngleMinDegrees, double> {
				static constexpr const char* const name = "svg-ridge-angle-min-degrees";
				static constexpr const char* const description = "SVG edge classification (issue #3668): minimum convex dihedral deviation from flat, in degrees, for a projection edge to be classified as 'sharp' rather than 'flush'.";
				static constexpr double defaultvalue = 45.;
			};

			struct SvgValleyAngleMinDegrees : public SettingBase<SvgValleyAngleMinDegrees, double> {
				static constexpr const char* const name = "svg-valley-angle-min-degrees";
				static constexpr const char* const description = "SVG edge classification (issue #3668): minimum concave dihedral deviation from flat, in degrees, for a projection edge to be classified as 'crease' rather than 'flush'.";
				static constexpr double defaultvalue = 12.;
			};

			struct SvgEmitFlushEdges : public SettingBase<SvgEmitFlushEdges, bool> {
				static constexpr const char* const name = "svg-emit-flush-edges";
				static constexpr const char* const description = "SVG edge classification (issue #3668): whether to emit 'flush' projection edges (dihedral deviation below both ridge/valley thresholds). Defaults to false, i.e. flush edges are omitted from the output.";
				static constexpr bool defaultvalue = false;
			};

			struct SvgUseEdgeClassification : public SettingBase<SvgUseEdgeClassification, bool> {
				static constexpr const char* const name = "svg-use-edge-classification";
				static constexpr const char* const description = "SVG edge classification (issue #3668): enable the 5-class boundary/outline/sharp/crease/flush scheme. When false (the default), falls back to the original unclassified linework.";
				static constexpr bool defaultvalue = false;
			};

			struct SvgRenderCreaseEdges : public SettingBase<SvgRenderCreaseEdges, bool> {
				static constexpr const char* const name = "svg-render-crease-edges";
				static constexpr const char* const description = "SVG edge classification (issue #3668): whether to emit 'crease' (concave) projection edges. Only relevant when svg-use-edge-classification is enabled.";
				static constexpr bool defaultvalue = true;
			};

			struct SvgRenderSharpEdges : public SettingBase<SvgRenderSharpEdges, bool> {
				static constexpr const char* const name = "svg-render-sharp-edges";
				static constexpr const char* const description = "SVG edge classification (issue #3668): whether to emit 'sharp' (convex) projection edges. Only relevant when svg-use-edge-classification is enabled.";
				static constexpr bool defaultvalue = true;
			};

			struct KeepBoundingBoxes : public SettingBase<KeepBoundingBoxes, bool> {
				static constexpr const char* const name = "keep-bounding-boxes";
				static constexpr const char* const description = "Default is to removes IfcBoundingBox from model prior to converting geometry.Setting this option disables that behaviour";
				static constexpr bool defaultvalue = false;
			};

			struct SurfaceColour : public SettingBase<SurfaceColour, bool> {
                static constexpr const char* const name = "surface-colour";
                static constexpr const char* const description =
                    "Prioritizes the surface color instead of using diffuse.";
                static constexpr bool defaultvalue = false;
            };

            struct ComputeCurvature : public SettingBase<ComputeCurvature, bool> {
                static constexpr const char* const name = "compute-curvature";
                static constexpr const char* const description = "Specifies whether function_item_evaluator.evaluate() computes curvature.";
                static constexpr bool defaultvalue = false;
            };

			enum FunctionStepMethod  {
				MAXSTEPSIZE,
				MINSTEPS };

			IFC_GEOM_API std::istream& operator>>(std::istream& in, FunctionStepMethod& ioo);

         struct FunctionStepType : public SettingBase<FunctionStepType, FunctionStepMethod> {
               static constexpr const char* const name = "function-step-type";
               static constexpr const char* const description = "Indicates the method used for defining step size when evaluating function-based curves. Provides interpretation of function-step-param";
               static constexpr FunctionStepMethod defaultvalue = MAXSTEPSIZE;
         };

			struct FunctionStepParam : public SettingBase<FunctionStepParam, double> {
               static constexpr const char* const name = "function-step-param";
               static constexpr const char* const description = "Indicates the parameter value for defining step size when evaluating function-based curves.";
               static constexpr double defaultvalue = 0.5; // ceiling of this value is used when FunctionStepMethod is MinSteps
         };

			struct ModelOffset : public SettingBase<ModelOffset, std::vector<double>> {
				static constexpr const char* const name = "model-offset";
				static constexpr const char* const description = "Applies an arbitrary offset of form x,y,z to all placements.";
			};

			struct ModelRotation : public SettingBase<ModelRotation, std::vector<double>> {
				static constexpr const char* const name = "model-rotation";
				static constexpr const char* const description = "Applies an arbitrary quaternion rotation of form x,y,z,w to all placements.";
			};

			enum TriangulationMethod {
				TRIANGLE_MESH,
				POLYHEDRON_WITHOUT_HOLES,
				POLYHEDRON_WITH_HOLES
			};

			IFC_GEOM_API std::istream& operator>>(std::istream& in, TriangulationMethod& ioo);

			struct TriangulationType : public SettingBase<TriangulationType, TriangulationMethod> {
				static constexpr const char* const name = "triangulation-type";
				static constexpr const char* const description = "Type of planar facet to be emitted";
				static constexpr TriangulationMethod defaultvalue = TRIANGLE_MESH;
			};

			struct CgalEmitOriginalEdges : public SettingBase<CgalEmitOriginalEdges, bool> {
				static constexpr const char* const name = "cgal-original-edges";
				static constexpr const char* const description = "Try to emit original edge face boundary edges instead of recomputed ones based on face normal. Falls back to triangulated data in case of boolean operands and faces with holes.";
				static constexpr bool defaultvalue = false;
			};

			struct OcctNoCleanTriangulation : public SettingBase<OcctNoCleanTriangulation, bool, true> {
				static constexpr const char* const name = "no-clean-triangulation";
				static constexpr const char* const description = "Don't clean triangulations, might cause memory leaks";
				static constexpr bool defaultvalue = false;
			};

			struct CacheShapes : public SettingBase<CacheShapes, bool> {
				static constexpr const char* const name = "cache-shapes";
				static constexpr const char* const description = "Experimental as not all topology hash functions fully implemented";
				static constexpr bool defaultvalue = false;
			};

			struct MakeVolume : public SettingBase<MakeVolume, bool> {
                static constexpr const char* const name = "make-volume";
                static constexpr const char* const description = "Try to isolate and fix a valid volume from non-manifold elements prior to opening subtraction";
                static constexpr bool defaultvalue = false;
            };

			struct DeferProcessingFirstElement : public SettingBase<DeferProcessingFirstElement, bool, true> {
				static constexpr const char* const name = "defer-processing-first-element";
				static constexpr const char* const description = "Don't process first element in Iterator::initialize call()";
				static constexpr bool defaultvalue = false;
			};

			struct MaxOffset : public SettingBase<MaxOffset, double> {
				static constexpr const char* const name = "max-offset";
				static constexpr const char* const description = "Maximum translation offset to be observed after which median offset in model gets removed and logged. Requires --no-parallel-mapping.";
			};

			struct MaxOffsetDeviation : public SettingBase<MaxOffsetDeviation, double> {
				static constexpr const char* const name = "max-offset-deviation";
				static constexpr const char* const description = "To retain field of view, completely remove elements outside of the median offset. Requires --no-parallel-mapping.";
			};

			struct ApplyOffset : public SettingBase<ApplyOffset, std::vector<double>> {
				static constexpr const char* const name = "apply-offset";
				static constexpr const char* const description = "Slight variation of --model-offset where large offsets are applied by negating existing large offsets to retain maximum precision. Requires --no-parallel-mapping.";
			};
		}

		namespace impl {
			template <typename T>
			struct readable_name {
				static constexpr const char* name = "Unknown Type";
			};

			template <>
			struct readable_name<bool> {
				static constexpr const char* name = "bool";
			};

			template <>
			struct readable_name<int> {
				static constexpr const char* name = "int";
			};

			template <>
			struct readable_name<double> {
				static constexpr const char* name = "double";
			};

			template <>
			struct readable_name<std::string> {
				static constexpr const char* name = "std::string";
			};

			template <>
			struct readable_name<std::set<int>> {
				static constexpr const char* name = "std::set<int>";
			};

			template <>
			struct readable_name<std::set<std::string>> {
				static constexpr const char* name = "std::set<std::string>";
			};

			template <>
			struct readable_name<std::vector<double>> {
				static constexpr const char* name = "std::vector<double>";
			};

			template <>
			struct readable_name<std::vector<std::string>> {
				static constexpr const char* name = "std::vector<std::string>";
			};

			template <>
			struct readable_name<settings_detail::IteratorOutputOptions> {
				static constexpr const char* name = "IteratorOutputOptions";
			};

			template <>
			struct readable_name<settings_detail::FunctionStepMethod> {
				static constexpr const char* name = "FunctionStepMethod";
			};

			template <>
			struct readable_name<settings_detail::OutputDimensionalityTypes> {
				static constexpr const char* name = "OutputDimensionalityTypes";
			};

			template <>
			struct readable_name<settings_detail::TriangulationMethod> {
				static constexpr const char* name = "TriangulationMethod";
			};
		}

		template <typename settings_t>
		class settings_container {
		public:
			typedef std::variant<bool, int, double, std::string, std::set<int>, std::set<std::string>,
				std::vector<double>, std::vector<std::string>, settings_detail::IteratorOutputOptions, settings_detail::FunctionStepMethod,
				settings_detail::OutputDimensionalityTypes, settings_detail::TriangulationMethod> value_variant_t;
		private:
			settings_t settings;

			template <std::size_t Index>
			void define_options_(po::options_description& desc) {
				std::get<Index>(settings).defineOption(desc);
				if constexpr (Index + 1 < std::tuple_size_v<settings_t>) {
					define_options_<Index + 1>(desc);
				}
			}

			template <std::size_t Index>
			value_variant_t get_option_(const std::string& name) const {
				if (std::tuple_element_t<Index, settings_t>::name == name) {
					return std::get<Index>(settings).get();
				}
				if constexpr (Index + 1 < std::tuple_size_v<settings_t>) {
					return get_option_<Index + 1>(name);
				} else {
					throw std::runtime_error("Setting not available");
				}
			}

			template <std::size_t Index>
			std::string get_type_(const std::string& name) const {
				if (std::tuple_element_t<Index, settings_t>::name == name) {
					return impl::readable_name<typename std::tuple_element_t<Index, settings_t>::base_type>::name;
				}
				if constexpr (Index + 1 < std::tuple_size_v<settings_t>) {
					return get_type_<Index + 1>(name);
				} else {
					throw std::runtime_error("Setting not available");
				}
			}

			template <std::size_t Index>
			void set_option_(const std::string& name, const value_variant_t& val) {
				if (std::tuple_element_t<Index, settings_t>::name == name) {
					if constexpr (std::is_enum_v<typename std::tuple_element_t<Index, settings_t>::base_type>) {
						if (auto* val_ptr = std::get_if<int>(&val)) {
							auto val_as_enum = (typename std::tuple_element_t<Index, settings_t>::base_type) *val_ptr;
							std::get<Index>(settings).value = val_as_enum;
							return;
						}
					}
					try {
                        std::get<Index>(settings).value = std::get<typename std::tuple_element_t<Index, settings_t>::base_type>(val);
					} catch (const std::bad_variant_access&) {
						std::string ty = impl::readable_name<typename std::tuple_element_t<Index, settings_t>::base_type>::name;
						throw std::runtime_error("Expected a value of type <" + ty + "> for setting '" + name + "'");
					}
				} else if constexpr (Index + 1 < std::tuple_size_v<settings_t>) {
					set_option_<Index + 1>(name, val);
				} else {
					throw std::runtime_error("Setting not available");
				}
			}

			template <std::size_t Index>
			void get_setting_names_(std::vector<std::string>& vec) const {
				vec.push_back(std::tuple_element_t<Index, settings_t>::name);
				if constexpr (Index + 1 < std::tuple_size_v<settings_t>) {
					return get_setting_names_<Index + 1>(vec);
				}
			}
		public:
			typedef settings_t settings_tuple;

			void define_options(po::options_description& desc) {
				define_options_<0>(desc);
			}

			template <typename T>
			const T& get() const {
				return std::get<T>(settings);
			}

			template <typename T>
			T& get() {
				return std::get<T>(settings);
			}

			template <typename T>
			void set(T& v) {
				std::get<T>(settings) = v;
			}

			value_variant_t get(const std::string& name) const {
				return get_option_<0>(name);
			}

			void set(const std::string& name, value_variant_t val) {
				set_option_<0>(name, val);
			}

			std::string get_type(const std::string& name) {
				return get_type_<0>(name);
			}

			std::vector<std::string> setting_names() const {
				std::vector<std::string> r;
				get_setting_names_<0>(r);
				return r;
			}
		};

		namespace settings_detail {

	struct UseElementNames : public settings_detail::SettingBase<UseElementNames, bool> {
		static constexpr const char* const name = "use-element-names";
		static constexpr const char* const description = "Use entity instance IfcRoot.Name instead of unique IDs for naming elements upon serialization. Applicable for OBJ, DAE, STP, and SVG output.";
		static constexpr bool defaultvalue = false;
	};

	struct UseElementGuids : public settings_detail::SettingBase<UseElementGuids, bool> {
		static constexpr const char* const name = "use-element-guids";
		static constexpr const char* const description = "Use entity instance IfcRoot.GlobalId instead of unique IDs for naming elements upon serialization. Applicable for OBJ, DAE, STP, and SVG output.";
		static constexpr bool defaultvalue = false;
	};

	struct UseElementStepIds : public settings_detail::SettingBase<UseElementStepIds, bool> {
		static constexpr const char* const name = "use-element-step-ids";
		static constexpr const char* const description = "Use the numeric step identifier (entity instance name) for naming elements upon serialization. Applicable for OBJ, DAE, STP, and SVG output.";
		static constexpr bool defaultvalue = false;
	};

	struct UseElementTypes : public settings_detail::SettingBase<UseElementTypes, bool> {
		static constexpr const char* const name = "use-element-types";
		static constexpr const char* const description = "Use element types instead of unique IDs for naming elements upon serialization. Applicable to DAE output.";
		static constexpr bool defaultvalue = false;
	};

	struct UseYUp : public settings_detail::SettingBase<UseYUp, bool> {
		static constexpr const char* const name = "y-up";
		static constexpr const char* const description = "Change the 'up' axis to positive Y, default is Z UP. Applicable to OBJ output.";
		static constexpr bool defaultvalue = false;
	};

	struct WriteGltfEcef : public settings_detail::SettingBase<WriteGltfEcef, bool> {
		static constexpr const char* const name = "ecef";
		static constexpr const char* const description = "Write glTF in Earth-Centered Earth-Fixed coordinates. Requires PROJ.";
		static constexpr bool defaultvalue = false;
	};

	struct FloatingPointDigits : public settings_detail::SettingBase<FloatingPointDigits, int> {
		static constexpr const char* const name = "digits";
		static constexpr const char* const description = "Sets the precision to be used to format floating-point values, 15 by default. Use a negative value to use the system's default precision (should be 6 typically). Applicable for OBJ and DAE output. For DAE output, value >= 15 means that up to 16 decimals are used,  and any other value means that 6 or 7 decimals are used.";
		static constexpr int defaultvalue = 15;
	};

	struct BaseUri : public settings_detail::SettingBase<BaseUri, std::string> {
		static constexpr const char* const name = "base-uri";
		static constexpr const char* const description = "Base URI for products to be used in RDF-based serializations.";
	};

	struct WktUseSection : public settings_detail::SettingBase<WktUseSection, bool> {
		static constexpr const char* const name = "wkt-use-section";
		static constexpr const char* const description = "Use a geometrical section rather than full polyhedral output and footprint in TTL WKT";
		static constexpr bool defaultvalue = false;
	};

	struct SeparateZUpNode : public settings_detail::SettingBase<SeparateZUpNode, bool> {
        static constexpr const char* const name = "separate-z-up-node";
        static constexpr const char* const description = "Introduce a separate Z-Up node into the GlTF hierarchy instead of multiplying the transform into the root node matrices";
        static constexpr bool defaultvalue = false;
    };

	struct SvgBounds : public settings_detail::SettingBase<SvgBounds, std::string> {
		static constexpr const char* const name = "bounds";
		static constexpr const char* const description = "Specifies the bounding rectangle, for example 512x512, to which the output will be scaled. Only used when converting to SVG.";
	};

	struct SvgScale : public settings_detail::SettingBase<SvgScale, std::string> {
		static constexpr const char* const name = "scale";
		static constexpr const char* const description = "Interprets SVG bounds in mm, centers layout and draw elements to scale. Only used when converting to SVG. Example 1:100.";
	};

	struct SvgCenter : public settings_detail::SettingBase<SvgCenter, std::string> {
		static constexpr const char* const name = "center";
		static constexpr const char* const description = "When using --scale, specifies the location in the range [0 1]x[0 1] around which to center the drawings. Example 0.5x0.5.";
	};

	struct SvgSectionRef : public settings_detail::SettingBase<SvgSectionRef, std::string> {
		static constexpr const char* const name = "section-ref";
		static constexpr const char* const description = "Element at which cross sections should be created.";
	};

	struct SvgElevationRef : public settings_detail::SettingBase<SvgElevationRef, std::string> {
		static constexpr const char* const name = "elevation-ref";
		static constexpr const char* const description = "Element at which drawings should be created.";
	};

	struct SvgElevationRefGuid : public settings_detail::SettingBase<SvgElevationRefGuid, std::string> {
		static constexpr const char* const name = "elevation-ref-guid";
		static constexpr const char* const description = "Element guids at which drawings should be created.";
	};

	struct SvgAutoSection : public settings_detail::SettingBase<SvgAutoSection, bool> {
		static constexpr const char* const name = "auto-section";
		static constexpr const char* const description = "Creates SVG cross section drawings automatically based on model extents.";
		static constexpr bool defaultvalue = false;
	};

	struct SvgAutoElevation : public settings_detail::SettingBase<SvgAutoElevation, bool> {
		static constexpr const char* const name = "auto-elevation";
		static constexpr const char* const description = "Creates SVG elevation drawings automatically based on model extents.";
		static constexpr bool defaultvalue = false;
	};

	struct SvgDrawStoreyHeights : public settings_detail::SettingBase<SvgDrawStoreyHeights, std::string> {
		static constexpr const char* const name = "draw-storey-heights";
		static constexpr const char* const description = "Draws a horizontal line at the height of building storeys in vertical drawings. Accepted values are none, full, and left.";
	};

	struct SvgProfileThreshold : public settings_detail::SettingBase<SvgProfileThreshold, int> {
		static constexpr const char* const name = "profile-threshold";
		static constexpr const char* const description = "Limits the number of projected wire profiles for non-wall and non-slab elements in SVG output. A negative value disables the limit.";
		static constexpr int defaultvalue = -1;
	};

	struct SvgStoreyHeightLineLength : public settings_detail::SettingBase<SvgStoreyHeightLineLength, double> {
		static constexpr const char* const name = "storey-height-line-length";
		static constexpr const char* const description = "Length of the line when --draw-storey-heights=left.";
	};

	struct SvgUseNamespace : public settings_detail::SettingBase<SvgUseNamespace, bool> {
		static constexpr const char* const name = "svg-xmlns";
		static constexpr const char* const description = "Stores name and guid in a separate namespace as opposed to data-name, data-guid.";
		static constexpr bool defaultvalue = false;
	};

	struct SvgUseHlrPoly : public settings_detail::SettingBase<SvgUseHlrPoly, bool> {
		static constexpr const char* const name = "svg-poly";
		static constexpr const char* const description = "Uses the polygonal algorithm for hidden line rendering.";
		static constexpr bool defaultvalue = false;
	};

	struct SvgUsePrefiltering : public settings_detail::SettingBase<SvgUsePrefiltering, bool> {
		static constexpr const char* const name = "svg-prefilter";
		static constexpr const char* const description = "Prefilter faces and shapes before feeding to the hidden-line algorithm.";
		static constexpr bool defaultvalue = false;
	};

	struct SvgUnifyInputs : public settings_detail::SettingBase<SvgUnifyInputs, bool> {
		static constexpr const char* const name = "svg-unify-inputs";
		static constexpr const char* const description = "Unify input shapes before SVG projection.";
		static constexpr bool defaultvalue = false;
	};

	struct SvgSegmentProjection : public settings_detail::SettingBase<SvgSegmentProjection, bool> {
		static constexpr const char* const name = "svg-segment-projection";
		static constexpr const char* const description = "Segment result of projection with respect to original products.";
		static constexpr bool defaultvalue = false;
	};

	struct SvgSubtractBefore : public settings_detail::SettingBase<SvgSubtractBefore, std::string> {
		static constexpr const char* const name = "svg-subtract-before";
		static constexpr const char* const description = "Controls which shapes are cut before SVG hidden-line projection. Accepted values are auto, slabs-and-walls, and always.";
	};

	struct SvgPolygonal : public settings_detail::SettingBase<SvgPolygonal, bool> {
		static constexpr const char* const name = "svg-write-poly";
		static constexpr const char* const description = "Approximate every curve as polygonal in SVG output.";
		static constexpr bool defaultvalue = false;
	};

	struct SvgAlwaysProject : public settings_detail::SettingBase<SvgAlwaysProject, bool> {
		static constexpr const char* const name = "svg-project";
		static constexpr const char* const description = "Always enable hidden line rendering instead of only on elevations.";
		static constexpr bool defaultvalue = false;
	};

	struct SvgWithoutStoreys : public settings_detail::SettingBase<SvgWithoutStoreys, bool> {
		static constexpr const char* const name = "svg-without-storeys";
		static constexpr const char* const description = "Do not emit drawings for building storeys.";
		static constexpr bool defaultvalue = false;
	};

	struct SvgNoCss : public settings_detail::SettingBase<SvgNoCss, bool> {
		static constexpr const char* const name = "svg-no-css";
		static constexpr const char* const description = "Do not emit CSS style declarations.";
		static constexpr bool defaultvalue = false;
	};

	struct SvgMirrorY : public settings_detail::SettingBase<SvgMirrorY, bool> {
		static constexpr const char* const name = "svg-mirror-y";
		static constexpr const char* const description = "Mirror SVG output along the Y axis.";
		static constexpr bool defaultvalue = false;
	};

	struct SvgMirrorX : public settings_detail::SettingBase<SvgMirrorX, bool> {
		static constexpr const char* const name = "svg-mirror-x";
		static constexpr const char* const description = "Mirror SVG output along the X axis.";
		static constexpr bool defaultvalue = false;
	};

	struct SvgDoorArcs : public settings_detail::SettingBase<SvgDoorArcs, bool> {
		static constexpr const char* const name = "door-arcs";
		static constexpr const char* const description = "Draw door opening arcs for IfcDoor elements.";
		static constexpr bool defaultvalue = false;
	};

	struct SvgSectionHeight : public settings_detail::SettingBase<SvgSectionHeight, double> {
		static constexpr const char* const name = "section-height";
		static constexpr const char* const description = "Specifies the cut section height for SVG 2D geometry.";
	};

	struct SvgSectionHeightFromStoreys : public settings_detail::SettingBase<SvgSectionHeightFromStoreys, bool> {
		static constexpr const char* const name = "section-height-from-storeys";
		static constexpr const char* const description = "Derives section height from storey elevation. Use --section-height to override the default offset of 1.2.";
		static constexpr bool defaultvalue = false;
	};

	struct SvgPrintSpaceNames : public settings_detail::SettingBase<SvgPrintSpaceNames, bool> {
		static constexpr const char* const name = "print-space-names";
		static constexpr const char* const description = "Prints IfcSpace LongName and Name in the geometry output. Applicable for SVG output.";
		static constexpr bool defaultvalue = false;
	};

	struct SvgPrintSpaceAreas : public settings_detail::SettingBase<SvgPrintSpaceAreas, bool> {
		static constexpr const char* const name = "print-space-areas";
		static constexpr const char* const description = "Prints calculated IfcSpace areas in square meters. Applicable for SVG output.";
		static constexpr bool defaultvalue = false;
	};

	struct SvgSpaceNameTransform : public settings_detail::SettingBase<SvgSpaceNameTransform, std::string> {
		static constexpr const char* const name = "space-name-transform";
		static constexpr const char* const description = "Additional transform to the space labels in SVG.";
	};
}

using geometry_setting_types = std::tuple<
			settings_detail::MesherLinearDeflection,
			settings_detail::MesherAngularDeflection,
			settings_detail::ReorientShells,
			settings_detail::LengthUnit,
			settings_detail::PlaneUnit,
			settings_detail::Precision,
			settings_detail::OutputDimensionality,
			settings_detail::LayersetFirst,
			settings_detail::DisableBooleanResult,
			settings_detail::NoWireIntersectionCheck,
			settings_detail::NoWireIntersectionTolerance,
			settings_detail::PrecisionFactor,
			settings_detail::DebugBooleanOperations,
			settings_detail::BooleanAttempt2d,
			settings_detail::SurfaceColour,
			settings_detail::WeldVertices,
			settings_detail::UseWorldCoords,
			settings_detail::UnifyShapes,
			settings_detail::UseMaterialNames,
			settings_detail::ConvertBackUnits,
			settings_detail::ContextIds,
			settings_detail::ContextTypes,
			settings_detail::ContextIdentifiers,
			settings_detail::ContextPriorities,
			settings_detail::IteratorOutput,
			settings_detail::DisableOpeningSubtractions,
			settings_detail::MaxVoidsPerElement,
			settings_detail::ApplyDefaultMaterials,
			settings_detail::DontEmitNormals,
			settings_detail::GenerateUvs,
			settings_detail::ApplyLayerSets,
			settings_detail::UseElementHierarchy,
			settings_detail::ValidateQuantities,
			settings_detail::EdgeArrows,
			settings_detail::BuildingLocalPlacement,
			settings_detail::SiteLocalPlacement,
			settings_detail::ForceSpaceTransparency,
			settings_detail::CircleSegments,
			settings_detail::CgalSmoothAngleDegrees,
			settings_detail::SvgRidgeAngleMinDegrees,
			settings_detail::SvgValleyAngleMinDegrees,
			settings_detail::SvgEmitFlushEdges,
			settings_detail::SvgUseEdgeClassification,
			settings_detail::SvgRenderCreaseEdges,
			settings_detail::SvgRenderSharpEdges,
			settings_detail::KeepBoundingBoxes,
			settings_detail::ComputeCurvature,
			settings_detail::FunctionStepType,
			settings_detail::FunctionStepParam,
			settings_detail::NoParallelMapping,
			settings_detail::PermissiveShapeReuse,
			settings_detail::ModelOffset,
			settings_detail::ModelRotation,
			settings_detail::TriangulationType,
			settings_detail::CgalEmitOriginalEdges,
			settings_detail::OcctNoCleanTriangulation,
			settings_detail::CacheShapes,
			settings_detail::DeferProcessingFirstElement,
			settings_detail::MaxOffset,
			settings_detail::MaxOffsetDeviation,
			settings_detail::ApplyOffset,
			settings_detail::MakeVolume,
			settings_detail::UseElementNames,
			settings_detail::UseElementGuids,
			settings_detail::UseElementStepIds,
			settings_detail::UseElementTypes,
			settings_detail::UseYUp,
			settings_detail::WriteGltfEcef,
			settings_detail::FloatingPointDigits,
			settings_detail::BaseUri,
			settings_detail::WktUseSection,
			settings_detail::SeparateZUpNode,
			settings_detail::SvgBounds,
			settings_detail::SvgScale,
			settings_detail::SvgCenter,
			settings_detail::SvgSectionRef,
			settings_detail::SvgElevationRef,
			settings_detail::SvgElevationRefGuid,
			settings_detail::SvgAutoSection,
			settings_detail::SvgAutoElevation,
			settings_detail::SvgDrawStoreyHeights,
			settings_detail::SvgProfileThreshold,
			settings_detail::SvgStoreyHeightLineLength,
			settings_detail::SvgUseNamespace,
			settings_detail::SvgUseHlrPoly,
			settings_detail::SvgUsePrefiltering,
			settings_detail::SvgUnifyInputs,
			settings_detail::SvgSegmentProjection,
			settings_detail::SvgSubtractBefore,
			settings_detail::SvgPolygonal,
			settings_detail::SvgAlwaysProject,
			settings_detail::SvgWithoutStoreys,
			settings_detail::SvgNoCss,
			settings_detail::SvgMirrorY,
			settings_detail::SvgMirrorX,
			settings_detail::SvgDoorArcs,
			settings_detail::SvgSectionHeight,
			settings_detail::SvgSectionHeightFromStoreys,
			settings_detail::SvgPrintSpaceNames,
			settings_detail::SvgPrintSpaceAreas,
			settings_detail::SvgSpaceNameTransform>;

		class settings : public settings_container<geometry_setting_types> {
		public:
			using MesherLinearDeflection = settings_detail::MesherLinearDeflection;
			using MesherAngularDeflection = settings_detail::MesherAngularDeflection;
			using ReorientShells = settings_detail::ReorientShells;
			using LengthUnit = settings_detail::LengthUnit;
			using PlaneUnit = settings_detail::PlaneUnit;
			using Precision = settings_detail::Precision;
			using OutputDimensionality = settings_detail::OutputDimensionality;
			using LayersetFirst = settings_detail::LayersetFirst;
			using DisableBooleanResult = settings_detail::DisableBooleanResult;
			using NoWireIntersectionCheck = settings_detail::NoWireIntersectionCheck;
			using NoWireIntersectionTolerance = settings_detail::NoWireIntersectionTolerance;
			using PrecisionFactor = settings_detail::PrecisionFactor;
			using DebugBooleanOperations = settings_detail::DebugBooleanOperations;
			using BooleanAttempt2d = settings_detail::BooleanAttempt2d;
			using SurfaceColour = settings_detail::SurfaceColour;
			using WeldVertices = settings_detail::WeldVertices;
			using UseWorldCoords = settings_detail::UseWorldCoords;
			using UnifyShapes = settings_detail::UnifyShapes;
			using UseMaterialNames = settings_detail::UseMaterialNames;
			using ConvertBackUnits = settings_detail::ConvertBackUnits;
			using ContextIds = settings_detail::ContextIds;
			using ContextTypes = settings_detail::ContextTypes;
			using ContextIdentifiers = settings_detail::ContextIdentifiers;
			using ContextPriorities = settings_detail::ContextPriorities;
			using IteratorOutput = settings_detail::IteratorOutput;
			using DisableOpeningSubtractions = settings_detail::DisableOpeningSubtractions;
			using MaxVoidsPerElement = settings_detail::MaxVoidsPerElement;
			using ApplyDefaultMaterials = settings_detail::ApplyDefaultMaterials;
			using DontEmitNormals = settings_detail::DontEmitNormals;
			using GenerateUvs = settings_detail::GenerateUvs;
			using ApplyLayerSets = settings_detail::ApplyLayerSets;
			using UseElementHierarchy = settings_detail::UseElementHierarchy;
			using ValidateQuantities = settings_detail::ValidateQuantities;
			using EdgeArrows = settings_detail::EdgeArrows;
			using BuildingLocalPlacement = settings_detail::BuildingLocalPlacement;
			using SiteLocalPlacement = settings_detail::SiteLocalPlacement;
			using ForceSpaceTransparency = settings_detail::ForceSpaceTransparency;
			using CircleSegments = settings_detail::CircleSegments;
			using CgalSmoothAngleDegrees = settings_detail::CgalSmoothAngleDegrees;
			using SvgRidgeAngleMinDegrees = settings_detail::SvgRidgeAngleMinDegrees;
			using SvgValleyAngleMinDegrees = settings_detail::SvgValleyAngleMinDegrees;
			using SvgEmitFlushEdges = settings_detail::SvgEmitFlushEdges;
			using SvgUseEdgeClassification = settings_detail::SvgUseEdgeClassification;
			using SvgRenderCreaseEdges = settings_detail::SvgRenderCreaseEdges;
			using SvgRenderSharpEdges = settings_detail::SvgRenderSharpEdges;
			using KeepBoundingBoxes = settings_detail::KeepBoundingBoxes;
			using ComputeCurvature = settings_detail::ComputeCurvature;
			using FunctionStepType = settings_detail::FunctionStepType;
			using FunctionStepParam = settings_detail::FunctionStepParam;
			using NoParallelMapping = settings_detail::NoParallelMapping;
			using PermissiveShapeReuse = settings_detail::PermissiveShapeReuse;
			using ModelOffset = settings_detail::ModelOffset;
			using ModelRotation = settings_detail::ModelRotation;
			using TriangulationType = settings_detail::TriangulationType;
			using CgalEmitOriginalEdges = settings_detail::CgalEmitOriginalEdges;
			using OcctNoCleanTriangulation = settings_detail::OcctNoCleanTriangulation;
			using CacheShapes = settings_detail::CacheShapes;
			using DeferProcessingFirstElement = settings_detail::DeferProcessingFirstElement;
			using MaxOffset = settings_detail::MaxOffset;
			using MaxOffsetDeviation = settings_detail::MaxOffsetDeviation;
			using ApplyOffset = settings_detail::ApplyOffset;
			using MakeVolume = settings_detail::MakeVolume;

			using UseElementNames = settings_detail::UseElementNames;
			using UseElementGuids = settings_detail::UseElementGuids;
			using UseElementStepIds = settings_detail::UseElementStepIds;
			using UseElementTypes = settings_detail::UseElementTypes;
			using UseYUp = settings_detail::UseYUp;
			using WriteGltfEcef = settings_detail::WriteGltfEcef;
			using FloatingPointDigits = settings_detail::FloatingPointDigits;
			using BaseUri = settings_detail::BaseUri;
			using WktUseSection = settings_detail::WktUseSection;
			using SeparateZUpNode = settings_detail::SeparateZUpNode;
			using SvgBounds = settings_detail::SvgBounds;
			using SvgScale = settings_detail::SvgScale;
			using SvgCenter = settings_detail::SvgCenter;
			using SvgSectionRef = settings_detail::SvgSectionRef;
			using SvgElevationRef = settings_detail::SvgElevationRef;
			using SvgElevationRefGuid = settings_detail::SvgElevationRefGuid;
			using SvgAutoSection = settings_detail::SvgAutoSection;
			using SvgAutoElevation = settings_detail::SvgAutoElevation;
			using SvgDrawStoreyHeights = settings_detail::SvgDrawStoreyHeights;
			using SvgProfileThreshold = settings_detail::SvgProfileThreshold;
			using SvgStoreyHeightLineLength = settings_detail::SvgStoreyHeightLineLength;
			using SvgUseNamespace = settings_detail::SvgUseNamespace;
			using SvgUseHlrPoly = settings_detail::SvgUseHlrPoly;
			using SvgUsePrefiltering = settings_detail::SvgUsePrefiltering;
			using SvgUnifyInputs = settings_detail::SvgUnifyInputs;
			using SvgSegmentProjection = settings_detail::SvgSegmentProjection;
			using SvgSubtractBefore = settings_detail::SvgSubtractBefore;
			using SvgPolygonal = settings_detail::SvgPolygonal;
			using SvgAlwaysProject = settings_detail::SvgAlwaysProject;
			using SvgWithoutStoreys = settings_detail::SvgWithoutStoreys;
			using SvgNoCss = settings_detail::SvgNoCss;
			using SvgMirrorY = settings_detail::SvgMirrorY;
			using SvgMirrorX = settings_detail::SvgMirrorX;
			using SvgDoorArcs = settings_detail::SvgDoorArcs;
			using SvgSectionHeight = settings_detail::SvgSectionHeight;
			using SvgSectionHeightFromStoreys = settings_detail::SvgSectionHeightFromStoreys;
			using SvgPrintSpaceNames = settings_detail::SvgPrintSpaceNames;
			using SvgPrintSpaceAreas = settings_detail::SvgPrintSpaceAreas;
			using SvgSpaceNameTransform = settings_detail::SvgSpaceNameTransform;

			using OutputDimensionalityTypes = settings_detail::OutputDimensionalityTypes;
			using IteratorOutputOptions = settings_detail::IteratorOutputOptions;
			using FunctionStepMethod = settings_detail::FunctionStepMethod;
			using TriangulationMethod = settings_detail::TriangulationMethod;

			static constexpr auto CURVES = settings_detail::CURVES;
			static constexpr auto SURFACES_AND_SOLIDS = settings_detail::SURFACES_AND_SOLIDS;
			static constexpr auto CURVES_SURFACES_AND_SOLIDS = settings_detail::CURVES_SURFACES_AND_SOLIDS;
			static constexpr auto TRIANGULATED = settings_detail::TRIANGULATED;
			static constexpr auto NATIVE = settings_detail::NATIVE;
			static constexpr auto SERIALIZED = settings_detail::SERIALIZED;
			static constexpr auto MAXSTEPSIZE = settings_detail::MAXSTEPSIZE;
			static constexpr auto MINSTEPS = settings_detail::MINSTEPS;
			static constexpr auto TRIANGLE_MESH = settings_detail::TRIANGLE_MESH;
			static constexpr auto POLYHEDRON_WITHOUT_HOLES = settings_detail::POLYHEDRON_WITHOUT_HOLES;
			static constexpr auto POLYHEDRON_WITH_HOLES = settings_detail::POLYHEDRON_WITH_HOLES;
		};
}
}

// @todo find a place
namespace ifcopenshell::geom {

#if defined(_MSC_VER)
#pragma warning(push)
#pragma warning(disable: 4275)
#endif

	class IFC_GEOM_API geometry_exception : public std::runtime_error {
	protected:
		std::string message;
	public:
		geometry_exception(const std::string& m)
			: std::runtime_error(m)
		{}
		~geometry_exception() override;
	};

	class IFC_GEOM_API too_many_faces_exception : public geometry_exception {
	public:
		too_many_faces_exception()
			: geometry_exception("Too many faces for operation") {}
		~too_many_faces_exception() override;
	};
}

#if defined(_MSC_VER)
#pragma warning(pop)
#endif

#endif
