#ifndef ITERATOR_KERNEL_H
#define ITERATOR_KERNEL_H

#include "../../ifcparse/IfcFile.h"
#include "../../ifcgeom/schema_agnostic/IfcGeomIteratorSettings.h"
#include "../../ifcgeom/schema_agnostic/ConversionResult.h"

#include <boost/function.hpp>

namespace IfcGeom {

	template <typename P, typename PP>
	class NativeElement;

	class Kernel {
	private:
		Kernel* implementation_;

	public:
		// Tolerances and settings for various geometrical operations:
		enum GeomValue {
			// Specifies the deflection of the mesher
			// Default: 0.001m / 1mm
			GV_DEFLECTION_TOLERANCE,
			// Specifies the tolerance of the wire builder, most notably for trimmed curves
			// Default: 0.0001m / 0.1mm
			GV_WIRE_CREATION_TOLERANCE,
			// Specifies the minimal area of a face to be included in an IfcConnectedFaceset
			// Read-only
			GV_MINIMAL_FACE_AREA,
			// Specifies the threshold distance under which cartesian points are deemed equal
			// Default: 0.00001m / 0.01mm
			GV_POINT_EQUALITY_TOLERANCE,
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

		Kernel(const std::string& geometry_library, IfcParse::IfcFile* file_ = 0);
		
		virtual ~Kernel() {}

		virtual void setValue(GeomValue var, double value) {
			implementation_->setValue(var, value);
		}

		virtual double getValue(GeomValue var) const {
			return implementation_->getValue(var);
		}

		virtual NativeElement<double, double>* convert(
			const IteratorSettings& settings, IfcUtil::IfcBaseClass* representation,
			IfcUtil::IfcBaseClass* product)
		{
			return implementation_->convert(settings, representation, product);
		}

		virtual ConversionResults convert(IfcUtil::IfcBaseClass* item) {
			return implementation_->convert(item);
		}

		virtual bool convert_placement(IfcUtil::IfcBaseClass* item, ConversionResultPlacement*& trsf) {
			return implementation_->convert_placement(item, trsf);
		}

		static int count(const ConversionResultShape*, int, bool unique=false);
		static int surface_genus(const ConversionResultShape*);

		static bool is_manifold(const ConversionResultShape*);
		static IfcUtil::IfcBaseEntity* get_decomposing_entity(IfcUtil::IfcBaseEntity*);
		static std::map<std::string, IfcUtil::IfcBaseEntity*> get_layers(IfcUtil::IfcBaseEntity*);
		static IfcEntityList::ptr find_openings(IfcUtil::IfcBaseEntity* product);
	};

	namespace impl {
		typedef boost::function1<Kernel*, IfcParse::IfcFile*> kernel_fn;

		class KernelFactoryImplementation : public std::map<std::pair<std::string, std::string>, kernel_fn> {
		public:
			KernelFactoryImplementation();
			void bind(const std::string& schema_name, const std::string& geometry_library, kernel_fn);
			Kernel* construct(const std::string& schema_name, const std::string& geometry_library, IfcParse::IfcFile*);
		};

		KernelFactoryImplementation& kernel_implementations();
	}
}

#endif