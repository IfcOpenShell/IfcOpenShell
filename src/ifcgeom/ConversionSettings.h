#ifndef CONVERSIONSETTINGS_H
#define CONVERSIONSETTINGS_H

#include <array>

namespace ifcopenshell { namespace geometry {

	class NativeElement;

	class ConversionSettings {
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
			GV_DIMENSIONALITY
		};

		void setValue(GeomValue var, double value);

		double getValue(GeomValue var) const;

	private:
		std::array<double, 8> values_ = {
			/* deflection_tolerance = */ 0.001,
			/* wire_creation_tolerance = */ 0.0001,
			/* point_equality_tolerance = */ 0.00001,
			/* max_faces_to_sew = */ -1.0,
			/* ifc_length_unit = */ 1.0,
			/* ifc_planeangle_unit = */ -1.0,
			/* modelling_precision = */ 0.00001,
			/* dimensionality = */ 1.,
		};
	};

} }

#endif