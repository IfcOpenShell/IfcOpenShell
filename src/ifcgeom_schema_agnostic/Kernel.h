#ifndef ITERATOR_KERNEL_H
#define ITERATOR_KERNEL_H

#include "../ifcparse/IfcFile.h"
#include "../ifcgeom_schema_agnostic/IfcGeomIteratorSettings.h"
#include "../ifcgeom_schema_agnostic/IfcRepresentationShapeItem.h"

#include <boost/preprocessor/stringize.hpp>
#include <boost/preprocessor/seq/size.hpp>
#include <boost/preprocessor/seq/pop_back.hpp>
#include <boost/preprocessor/comparison/greater.hpp> 
#include <boost/preprocessor/selection/min.hpp>


// @tfk A macro cannot define an include (I think), so here we can't
// loop over the sequence of schema identifiers, but rather we have
// unroll the loop with at least the amount of schemas we'd like support
// for and then overflow into an existing empty include file.

#define INCLUDE_SCHEMA(n) \
	BOOST_PP_IIF(BOOST_PP_GREATER(BOOST_PP_SEQ_SIZE(SCHEMA_SEQ), n), BOOST_PP_STRINGIZE(../ifcparse/BOOST_PP_CAT(Ifc,BOOST_PP_SEQ_ELEM(BOOST_PP_MIN(n, BOOST_PP_SEQ_SIZE(BOOST_PP_SEQ_POP_BACK(SCHEMA_SEQ))),SCHEMA_SEQ)).h), "empty.h")

#include INCLUDE_SCHEMA(0)
#include INCLUDE_SCHEMA(1)
#include INCLUDE_SCHEMA(2)
#include INCLUDE_SCHEMA(3)
#include INCLUDE_SCHEMA(4)
#include INCLUDE_SCHEMA(5)
#include INCLUDE_SCHEMA(6)
#include INCLUDE_SCHEMA(7)
#include INCLUDE_SCHEMA(8)
#include INCLUDE_SCHEMA(9)

#include <boost/function.hpp>

#include <TopExp_Explorer.hxx>
#include <gp_Ax2.hxx>
#include <gp_Ax3.hxx>
#include <gp_Trsf2d.hxx>
#include <gp_GTrsf2d.hxx>
#include <gp_Trsf.hxx>
#include <gp_GTrsf.hxx>

static const double ALMOST_ZERO = 1.e-9;

template <typename T>
inline static bool ALMOST_THE_SAME(const T& a, const T& b, double tolerance = ALMOST_ZERO) {
	return fabs(a - b) < tolerance;
}

namespace IfcGeom {

	class BRepElement;

	class Kernel {
	private:
		Kernel* implementation_;

	protected:
		Kernel() {};

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
			GV_BOOLEAN_ATTEMPT_2D
		};

		IFC_PARSE_API Kernel(IfcParse::IfcFile* file_);
		
		virtual ~Kernel() {}

		virtual void setValue(GeomValue var, double value) {
			implementation_->setValue(var, value);
		}

		virtual double getValue(GeomValue var) const {
			return implementation_->getValue(var);
		}

		virtual BRepElement* convert(
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

		IFC_PARSE_API static int count(const TopoDS_Shape&, TopAbs_ShapeEnum, bool unique = false);
		IFC_PARSE_API static int surface_genus(const TopoDS_Shape&);

		IFC_PARSE_API static bool is_manifold(const TopoDS_Shape& a);
		IFC_PARSE_API static IfcUtil::IfcBaseEntity* get_decomposing_entity(IfcUtil::IfcBaseEntity*, bool include_openings = true);
		IFC_PARSE_API static std::map<std::string, IfcUtil::IfcBaseEntity*> get_layers(IfcUtil::IfcBaseEntity*);

		// For axis placements detect equality early in order for the
		// relatively computionaly expensive gp_Trsf calculation to be skipped
		IFC_PARSE_API static bool axis_equal(const gp_Ax3& a, const gp_Ax3& b, double tolerance) {
			if (!a.Location().IsEqual(b.Location(), tolerance)) return false;
			// Note that the tolerance below is angular, above is linear. Since architectural
			// objects are about 1m'ish in scale, it should be somewhat equivalent. Besides,
			// this is mostly a filter for NULL or default values in the placements.
			if (!a.Direction().IsEqual(b.Direction(), tolerance)) return false;
			if (!a.XDirection().IsEqual(b.XDirection(), tolerance)) return false;
			if (!a.YDirection().IsEqual(b.YDirection(), tolerance)) return false;
			return true;
		}

		IFC_PARSE_API static bool axis_equal(const gp_Ax2d& a, const gp_Ax2d& b, double tolerance) {
			if (!a.Location().IsEqual(b.Location(), tolerance)) return false;
			if (!a.Direction().IsEqual(b.Direction(), tolerance)) return false;
			return true;
		}

		IFC_PARSE_API static bool is_identity(const gp_Trsf2d& t, double tolerance);
		IFC_PARSE_API static bool is_identity(const gp_GTrsf2d& t, double tolerance);
		IFC_PARSE_API static bool is_identity(const gp_Trsf& t, double tolerance);
		IFC_PARSE_API static bool is_identity(const gp_GTrsf& t, double tolerance);

		IFC_PARSE_API static gp_Trsf combine_offset_and_rotation(const gp_Vec &offset, const gp_Quaternion& rotation);
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

	namespace util {
		bool is_nested_compound_of_solid(const TopoDS_Shape& s, int depth = 0);
	}

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