#ifndef ITERATOR_KERNEL_H
#define ITERATOR_KERNEL_H

namespace IfcGeom {
	class Kernel {
	public:
		// Tolerances and settings for various geometrical operations:
		enum GeomValue {
			// Specifies the deflection of the mesher
			// Default: 0.001m / 1mm
			GV_DEFLECTION_TOLERANCE,
			// Specifies the tolerance of the wire builder, most notably for trimmed curves
			// Defailt: 0.0001m / 0.1mm
			GV_WIRE_CREATION_TOLERANCE,
			// Specifies the minimal area of a face to be included in an IfcConnectedFaceset
			// Read-only
			GV_MINIMAL_FACE_AREA,
			// Specifies the treshold distance under which cartesian points are deemed equal
			// Default: 0.00001m / 0.01mm
			GV_POINT_EQUALITY_TOLERANCE,
			// Specifies maximum number of faces for a shell to be sewed. Sewing shells
			// that consist of many faces is really detrimental for the performance.
			// Default: 1000
			GV_MAX_FACES_TO_SEW,
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
		
		virtual ~Kernel() {}
	};
}

#endif