#ifndef CONVERSIONSETTINGS_H
#define CONVERSIONSETTINGS_H

#include <array>
#include <limits>
#include <string>

#include "ifc_geom_api.h"

namespace ifcopenshell {
	namespace geometry {

		class IFC_GEOM_API ConversionSettings {
		public:
			// Tolerances and settings for various geometrical operations:
			enum GeomValue {
				// Specifies the deflection of the mesher
				// Default: 0.001m / 1mm
				GV_DEFLECTION_TOLERANCE,
				// Specifies the minimal area of a face to be included in an IfcConnectedFaceset
				// Read-only
				GV_MINIMAL_FACE_AREA,
				// Specifies the threshold distance under which cartesian points are deemed equal
				// Read-only
				GV_POINT_EQUALITY_TOLERANCE,
				// Specifies maximum number of faces for a shell to be reoriented.
				// Default: -1
				GV_MAX_FACES_TO_ORIENT,
				// The length unit used the creation of TopoDS_Shapes, primarily affects the
				// interpretation of IfcCartesianPoints and IfcVector magnitudes
				// DefaultL 1.0
				GV_LENGTH_UNIT,
				// The plane angle unit used for the creation of TopoDS_Shapes, primarily affects
				// the interpretation of IfcParamaterValues of IfcTrimmedCurves
				// Default: -1.0 (= not set, fist try degrees, then radians)
				GV_PLANEANGLE_UNIT,
				// The precision used in boolean operations, setting this value too low results
				// in artefacts and potentially modelling failures
				// Default: 0.00001 (obtained from IfcGeometricRepresentationContext if available)
				GV_PRECISION,
				// Whether to process shapes of type Face or higher (1) Wire or lower (-1) or all (0)
				GV_DIMENSIONALITY,
				GV_LAYERSET_FIRST,
				GV_DISABLE_BOOLEAN_RESULT,
				GV_NO_WIRE_INTERSECTION_CHECK,
				GV_PRECISION_FACTOR,
				GV_NO_WIRE_INTERSECTION_TOLERANCE,
				GV_DEBUG_BOOLEAN,
				GV_BOOLEAN_ATTEMPT_2D,
				NUM_SETTINGS
			};

			void setValue(GeomValue var, double value);

			double getValue(GeomValue var) const;

		private:
			std::array<double, NUM_SETTINGS> values_ = {
				/* deflection_tolerance = */ 0.001,
				// @todo make sure these 'read-only' variables work.
				/* minimal_face_area = */ std::numeric_limits<double>::quiet_NaN(),
				/* max_faces_to_orient = */ -1.0,
				/* ifc_length_unit = */ 1.0,
				/* ifc_planeangle_unit = */ -1.0,
				/* modelling_precision = */ 0.00001,
				/* dimensionality = */ 1.,
				/* layerset_first = */ -1.,
				/* disable_boolean_result = */ -1.
				/* no_wire_intersection_check = */ -1.,
				/* precision_factor = */ 10.,
				/* no_wire_intersection_tolerance = */ -1.,
				/* boolean_debug_setting = */ -1.,
				/* boolean_attempt_2d = */ 1.
			};
		};
	}
}

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
