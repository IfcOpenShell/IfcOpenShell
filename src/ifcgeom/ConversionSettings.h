#ifndef CONVERSIONSETTINGS_H
#define CONVERSIONSETTINGS_H

#include <array>
#include <limits>
#include <string>
#include <iostream>
#include <string>
#include <map>
#include <tuple>
#include <type_traits>

#include <boost/program_options.hpp>
#include <boost/optional.hpp>
#include <boost/variant.hpp>
#include <boost/algorithm/string.hpp>
#include <boost/optional/optional_io.hpp>

#include "ifc_geom_api.h"

#ifndef SWIG
namespace po = boost::program_options;

namespace std {
	istream& operator>>(istream& in, set<int>& ints);
	istream& operator>>(istream& in, set<string>& ints);
}
#endif

namespace ifcopenshell {
	namespace geometry {
		inline namespace settings {

#ifndef SWIG
			template <typename T, typename U = int>
			struct HasDefault : std::false_type { };

			template <typename T>
			struct HasDefault<T, decltype((void)T::defaultvalue, 0)> : std::true_type { };
#endif

			template <typename Derived, typename T>
			struct SettingBase {
				typedef T base_type;

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
					if constexpr (std::is_same_v<T, bool>) {
						// @todo bool_switch doesn't work with optional unfortunately...
						value.emplace();
						desc.add_options()(Derived::name, apply_default(po::bool_switch(&*value)), Derived::description);
					} else {
						desc.add_options()(Derived::name, apply_default(po::value(&value)), Derived::description);
					}
				}

				T get() const {
					if (value) {
						return value.get();
					}
					if constexpr (HasDefault<Derived>()) {
						return Derived::defaultvalue;
					}
					throw std::runtime_error("Setting not set");
				}

				bool has() const {
					// @todo this is not reliable, better use vmap[...].defaulted()
					return !!value;
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
				static constexpr const char* const description = "Specifies whether to orient the faces of IfcConnectedFaceSets. "
					"This is a potentially time consuming operation, but guarantees a "
					"consistent orientation of surface normals, even if the faces are not "
					"properly oriented in the IFC file.";
				static constexpr bool defaultvalue = false;
			};

			struct LengthUnit : public SettingBase<LengthUnit, double> {
				static constexpr const char* const name = "length-unit";
				static constexpr const char* const description = "";
				static constexpr double defaultvalue = 1.0;
			};

			struct PlaneUnit : public SettingBase<PlaneUnit, double> {
				static constexpr const char* const name = "angle-unit";
				static constexpr const char* const description = "";
				static constexpr double defaultvalue = 1.0;
			};

			struct Precision : public SettingBase<Precision, double> {
				static constexpr const char* const name = "precision";
				static constexpr const char* const description = "";
				static constexpr double defaultvalue = 0.00001;
			};

			struct LayersetFirst : public SettingBase<LayersetFirst, bool> {
				static constexpr const char* const name = "layerset-first";
				static constexpr const char* const description = "Assigns the first layer material of the layerset "
					"to the complete product.";
				static constexpr bool defaultvalue = false;
			};

			struct DisableBooleanResult : public SettingBase<DisableBooleanResult, bool> {
				static constexpr const char* const name = "disable-boolean-result";
				static constexpr const char* const description = "Specifies whether to disable the boolean operation within representations "
			"such as clippings by means of IfcBooleanResult and subtypes";
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
				static constexpr const char* const description = "Option to increase linear tolerance for more permissive edge curves and fewer artifacts after "
					"boolean operations at the expense of geometric detail "
					"due to vertex collapsing and wire intersection fuzziness.";
				static constexpr double defaultvalue = 1.0;
			};

			struct DebugBooleanOperations : public SettingBase<DebugBooleanOperations, double> {
				static constexpr const char* const name = "debug-boolean";
				static constexpr const char* const description = "";
				static constexpr bool defaultvalue = false;
			};

			struct BooleanAttempt2d : public SettingBase<BooleanAttempt2d, double> {
				static constexpr const char* const name = "boolean-attempt-2d";
				static constexpr const char* const description = "Do not attempt to process boolean subtractions in 2D.";
				static constexpr bool defaultvalue = true;
			};

			// These are the old IteratorSettings

			struct WeldVertices : public SettingBase<WeldVertices, bool> {
				static constexpr const char* const name = "weld-vertices";
				static constexpr const char* const description = "Specifies whether vertices are welded, meaning that the coordinates "
					"vector will only contain unique xyz-triplets. This results in a "
					"manifold mesh which is useful for modelling applications, but might "
					"result in unwanted shading artefacts in rendering applications.";
				static constexpr bool defaultvalue = true;
			};

			struct UseWorldCoords : public SettingBase<UseWorldCoords, bool> {
				static constexpr const char* const name = "use-world-coords";
				static constexpr const char* const description = "Specifies whether to apply the local placements of building elements "
					"directly to the coordinates of the representation mesh rather than "
					"to represent the local placement in the 4x3 matrix, which will in that "
					"case be the identity matrix.";
				static constexpr bool defaultvalue = false;
			};

			struct UseMaterialNames : public SettingBase<UseMaterialNames, bool> {
				static constexpr const char* const name = "use-material-names";
				static constexpr const char* const description = "Use material names instead of unique IDs for naming materials upon serialization. "
					"Applicable for OBJ and DAE output.";
				static constexpr bool defaultvalue = false;
			};

			struct ConvertBackUnits : public SettingBase<ConvertBackUnits, bool> {
				static constexpr const char* const name = "convert-back-units";
				static constexpr const char* const description = "Specifies whether to convert back geometrical output back to the "
					"unit of measure in which it is defined in the IFC file. Default is "
					"to use meters.";
				static constexpr bool defaultvalue = false;
			};

			struct ContextIds : public SettingBase<ContextIds, std::set<int>> {
				static constexpr const char* const name = "context-ids";
				static constexpr const char* const description = "";
			};

			struct ContextTypes : public SettingBase<ContextIds, std::set<std::string>> {
				static constexpr const char* const name = "context-types";
				static constexpr const char* const description = "";
			};

			struct ContextIdentifiers : public SettingBase<ContextIds, std::set<std::string>> {
				static constexpr const char* const name = "context-identifiers";
				static constexpr const char* const description = "";
			};

			enum OutputDimensionalityTypes {
				CURVES,
				SURFACES_AND_SOLIDS,
				CURVES_SURFACES_AND_SOLIDS
			};

			std::istream& operator>>(std::istream& in, OutputDimensionalityTypes& ioo);

			struct OutputDimensionality : public SettingBase<OutputDimensionality, OutputDimensionalityTypes> {
				static constexpr const char* const name = "dimensionality";
				static constexpr const char* const description = "Specifies whether to include curves and/or surfaces and solids in the output result. Defaults to only surfaces and solids.";
				static constexpr OutputDimensionalityTypes defaultvalue = SURFACES_AND_SOLIDS;
			};

			enum IteratorOutputOptions {
				TRIANGULATED,
				NATIVE,
				SERIALIZED
			};

			std::istream& operator>>(std::istream& in, IteratorOutputOptions& ioo);

			struct IteratorOutput : public SettingBase<IteratorOutput, IteratorOutputOptions> {
				static constexpr const char* const name = "iterator-output";
				static constexpr const char* const description = "";
				static constexpr IteratorOutputOptions defaultvalue = TRIANGULATED;
			};

			struct DisableOpeningSubtractions : public SettingBase<DisableOpeningSubtractions, bool> {
				static constexpr const char* const name = "disable-opening-subtractions";
				static constexpr const char* const description = "Specifies whether to disable the boolean subtraction of "
					"IfcOpeningElement Representations from their RelatingElements.";
				static constexpr bool defaultvalue = false;
			};

			struct ApplyDefaultMaterials : public SettingBase<ApplyDefaultMaterials, bool> {
				static constexpr const char* const name = "apply-default-materials";
				static constexpr const char* const description = "";
				static constexpr bool defaultvalue = true;
			};

			struct DontEmitNormals : public SettingBase<DontEmitNormals, bool> {
				static constexpr const char* const name = "no-normals";
				static constexpr const char* const description = "Disables computation of normals.Saves time and file size and is useful "
					"in instances where you're going to recompute normals for the exported "
					"model in other modelling application in any case.";
				static constexpr bool defaultvalue = false;
			};

			struct GenerateUvs : public SettingBase<GenerateUvs, bool> {
				static constexpr const char* const name = "generate-uvs";
				static constexpr const char* const description = "Generates UVs (texture coordinates) by using simple box projection. Requires normals. "
					"Not guaranteed to work properly if used with --weld-vertices.";
				static constexpr bool defaultvalue = false;
			};

			struct ApplyLayerSets : public SettingBase<ApplyLayerSets, bool> {
				static constexpr const char* const name = "enable-layerset-slicing";
				static constexpr const char* const description = "Specifies whether to enable the slicing of products according "
					"to their associated IfcMaterialLayerSet.";
				static constexpr bool defaultvalue = false;
			};

			struct UseElementHierarchy : public SettingBase<UseElementHierarchy, bool> {
				static constexpr const char* const name = "element-hierarchy";
				static constexpr const char* const description = "Assign the elements using their e.g IfcBuildingStorey parent."
					"Applicable to DAE output.";
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
				static constexpr const char* const description = "Place elements locally in the IfcSite coordinate system, instead of placing "
					"them in the IFC global coords. Applicable for OBJ, DAE, and STP output.";
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

			struct ForceSpaceTransparency : public SettingBase<ForceSpaceTransparency, double> {
				static constexpr const char* const name = "force-space-transparency";
				static constexpr const char* const description = "Overrides transparency of spaces in geometry output.";
			};

			struct CircleSegments : public SettingBase<CircleSegments, int> {
				static constexpr const char* const name = "circle-segments";
				static constexpr const char* const description = "Number of segments to approximate full circles in CGAL kernel.";
				static constexpr int defaultvalue = 16;
			};

			struct KeepBoundingBoxes : public SettingBase<KeepBoundingBoxes, bool> {
				static constexpr const char* const name = "keep-bounding-boxes";
				static constexpr const char* const description =
					"Default is to removes IfcBoundingBox from model prior to converting geometry."
					"Setting this option disables that behaviour";
				static constexpr bool defaultvalue = false;
			};

			enum PiecewiseStepMethod  {
				MAXSTEPSIZE,
				MINSTEPS };

			std::istream& operator>>(std::istream& in, PiecewiseStepMethod& ioo);

         struct PiecewiseStepType : public SettingBase<PiecewiseStepType, PiecewiseStepMethod> {
               static constexpr const char* const name = "piecewise-step-type";
               static constexpr const char* const description = "Indicates the method used for defining step size when evaluating piecewise curves. Provides interpretation of piecewise-step-param";
               static constexpr PiecewiseStepMethod defaultvalue = MAXSTEPSIZE;
         };

			struct PiecewiseStepParam : public SettingBase<PiecewiseStepParam, double> {
               static constexpr const char* const name = "piecewise-step-param";
               static constexpr const char* const description = "Indicates the parameter value for defining step size when evaluating piecewise curves.";
               static constexpr double defaultvalue = 0.5; // ceiling of this value is used when PiecewiseStepMethod is MinSteps
         };
		}

		template <typename settings_t>
		class IFC_GEOM_API SettingsContainer {
		public:
         typedef boost::variant<bool, int, double, std::string, std::set<int>, std::set<std::string>, IteratorOutputOptions, PiecewiseStepMethod, OutputDimensionalityTypes> value_variant_t;
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
			void set_option_(const std::string& name, const value_variant_t& val) {
				if (std::tuple_element_t<Index, settings_t>::name == name) {
					if constexpr (std::is_enum_v<typename std::tuple_element_t<Index, settings_t>::base_type>) {
						if (val.which() == 1) {
							auto val_as_enum = (typename std::tuple_element_t<Index, settings_t>::base_type) boost::get<int>(val);
							std::get<Index>(settings).value = val_as_enum;
							return;
						}
					}
					std::get<Index>(settings).value = boost::get<typename std::tuple_element_t<Index, settings_t>::base_type>(val);
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

			std::vector<std::string> setting_names() const {
				std::vector<std::string> r;
				get_setting_names_<0>(r);
				return r;
			}
		};

		class IFC_GEOM_API Settings : public SettingsContainer<
                                          std::tuple<MesherLinearDeflection, MesherAngularDeflection, ReorientShells, LengthUnit, PlaneUnit, Precision, OutputDimensionality, LayersetFirst, DisableBooleanResult, NoWireIntersectionCheck, NoWireIntersectionTolerance, PrecisionFactor, DebugBooleanOperations, BooleanAttempt2d, WeldVertices, UseWorldCoords, UseMaterialNames, ConvertBackUnits, ContextIds, ContextTypes, ContextIdentifiers, IteratorOutput, DisableOpeningSubtractions, ApplyDefaultMaterials, DontEmitNormals, GenerateUvs, ApplyLayerSets, UseElementHierarchy, ValidateQuantities, EdgeArrows, BuildingLocalPlacement, SiteLocalPlacement, ForceSpaceTransparency, CircleSegments, KeepBoundingBoxes, PiecewiseStepType, PiecewiseStepParam, NoParallelMapping>
		>
		{};
}
}

// namespace ifcopenshell {
// 	namespace geometry {
// 
// 		class IFC_GEOM_API ConversionSettings {
// 		public:
// 			// Tolerances and settings for various geometrical operations:
// 			enum GeomValue {
// 				// 
// 				// Default: 0.001m / 1mm
// 				GV_DEFLECTION_TOLERANCE,
// 
// 				// The length unit used the creation of TopoDS_Shapes, primarily affects the
// 				// interpretation of IfcCartesianPoints and IfcVector magnitudes
// 				// DefaultL 1.0
// 				GV_LENGTH_UNIT,
// 				// The plane angle unit used for the creation of TopoDS_Shapes, primarily affects
// 				// the interpretation of IfcParamaterValues of IfcTrimmedCurves
// 				// Default: -1.0 (= not set, fist try degrees, then radians)
// 				GV_PLANEANGLE_UNIT,
// 				// The precision used in boolean operations, setting this value too low results
// 				// in artefacts and potentially modelling failures
// 				// Default: 0.00001 (obtained from IfcGeometricRepresentationContext if available)
// 				GV_PRECISION,
// 				// Whether to process shapes of type Face or higher (1) Wire or lower (-1) or all (0)
// 				GV_DIMENSIONALITY,
// 				GV_LAYERSET_FIRST,
// 				GV_DISABLE_BOOLEAN_RESULT,
// 				GV_NO_WIRE_INTERSECTION_CHECK,
// 				GV_PRECISION_FACTOR,
// 				GV_NO_WIRE_INTERSECTION_TOLERANCE,
// 				GV_DEBUG_BOOLEAN,
// 				GV_BOOLEAN_ATTEMPT_2D,
// 				NUM_SETTINGS
// 			};
// 
// 			void setValue(GeomValue var, double value);
// 
// 			double getValue(GeomValue var) const;
// 
// 		private:
// 			std::array<double, NUM_SETTINGS> values_ = {
// 				/* deflection_tolerance = */ 0.001,
// 				// @todo make sure these 'read-only' variables work.
// 				/* minimal_face_area = */ std::numeric_limits<double>::quiet_NaN(),
// 				/* max_faces_to_orient = */ -1.0,
// 				/* ifc_length_unit = */ 1.0,
// 				/* ifc_planeangle_unit = */ -1.0,
// 				/* modelling_precision = */ 0.00001,
// 				/* dimensionality = */ 1.,
// 				/* layerset_first = */ -1.,
// 				/* disable_boolean_result = */ -1.
// 				/* no_wire_intersection_check = */ -1.,
// 				/* precision_factor = */ 10.,
// 				/* no_wire_intersection_tolerance = */ -1.,
// 				/* boolean_debug_setting = */ -1.,
// 				/* boolean_attempt_2d = */ 1.
// 			};
// 		};
// 	}
// }

// @todo find a place
namespace IfcGeom {
	class IFC_GEOM_API geometry_exception : public std::exception {
	protected:
		std::string message;
	public:
		geometry_exception(const std::string& m)
			: message(m) {}
		virtual ~geometry_exception() throw () {}
		virtual const char* what() const throw() {
			return message.c_str();
		}
	};

	class IFC_GEOM_API too_many_faces_exception : public geometry_exception {
	public:
		too_many_faces_exception()
			: geometry_exception("Too many faces for operation") {}
	};
}
#endif
