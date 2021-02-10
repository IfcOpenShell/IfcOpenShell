#ifndef ITERATOR_KERNEL_H
#define ITERATOR_KERNEL_H

#include "../ifcparse/IfcFile.h"
#include "../ifcgeom/IfcGeomIteratorSettings.h"
#include "../ifcgeom/IfcRepresentationShapeItem.h"

#include "../ifcparse/Ifc2x3.h"
#include "../ifcparse/Ifc4.h"
#include "../ifcparse/Ifc4x1.h"
#include "../ifcparse/Ifc4x2.h"
#include "../ifcparse/Ifc4x3_rc1.h"

#include <boost/function.hpp>

#include <TopExp_Explorer.hxx>

namespace IfcGeom {

	template <typename P, typename PP>
	class BRepElement;

	class Kernel {
	private:
		Kernel* implementation_;

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
		};

		Kernel(IfcParse::IfcFile* file_ = 0);
		
		virtual ~Kernel() {}

		virtual void setValue(GeomValue var, double value) {
			implementation_->setValue(var, value);
		}

		virtual double getValue(GeomValue var) const {
			return implementation_->getValue(var);
		}

		virtual BRepElement<double, double>* convert(
			const IteratorSettings& settings, IfcUtil::IfcBaseClass* representation,
			IfcUtil::IfcBaseClass* product)
		{
			return implementation_->convert(settings, representation, product);
		}

		virtual IfcRepresentationShapeItems convert(IfcUtil::IfcBaseClass* item) {
			return implementation_->convert(item);
		}

		virtual bool convert_placement(IfcUtil::IfcBaseClass* item, gp_Trsf& trsf) {
			return implementation_->convert_placement(item, trsf);
		}

		static int count(const TopoDS_Shape&, TopAbs_ShapeEnum, bool unique=false);
		static int surface_genus(const TopoDS_Shape&);

		static bool is_manifold(const TopoDS_Shape& a);
		static IfcUtil::IfcBaseEntity* get_decomposing_entity(IfcUtil::IfcBaseEntity*, bool include_openings=true);
		static std::map<std::string, IfcUtil::IfcBaseEntity*> get_layers(IfcUtil::IfcBaseEntity*);
	};

	namespace impl {
		typedef boost::function1<Kernel*, IfcParse::IfcFile*> kernel_fn;

		class KernelFactoryImplementation : public std::map<std::string, kernel_fn> {
		public:
			KernelFactoryImplementation();
			void bind(const std::string& schema_name, kernel_fn);
			Kernel* construct(const std::string& schema_name, IfcParse::IfcFile*);
		};

		KernelFactoryImplementation& kernel_implementations();
	}
}

#endif