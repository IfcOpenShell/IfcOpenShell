#ifndef ABSTRACT_KERNEL_H
#define ABSTRACT_KERNEL_H

#include "../../ifcparse/macros.h"
#include "../../ifcgeom/schema_agnostic/ifc_geom_api.h"
#include "../../ifcgeom/schema_agnostic/IfcGeomRepresentation.h"
#include "../../ifcgeom/taxonomy.h"

static const double ALMOST_ZERO = 1.e-9;

template <typename T>
inline static bool ALMOST_THE_SAME(const T& a, const T& b, double tolerance = ALMOST_ZERO) {
	return fabs(a - b) < tolerance;
}

namespace ifcopenshell { namespace geometry { namespace kernels {

	class IFC_GEOM_API AbstractKernel {
	protected:
		// For stopping PlacementRelTo recursion in convert(const IfcSchema::IfcObjectPlacement* l, gp_Trsf& trsf)
		const IfcParse::declaration* placement_rel_to;

		double deflection_tolerance;
		double wire_creation_tolerance;
		double point_equality_tolerance;
		double max_faces_to_sew;
		double ifc_length_unit;
		double ifc_planeangle_unit;
		double modelling_precision;
		double dimensionality;

		std::string geometry_library;

	public:
		AbstractKernel(const std::string& geometry_library)
			: geometry_library(geometry_library)
			, deflection_tolerance(0.001)
			, wire_creation_tolerance(0.0001)
			, point_equality_tolerance(0.00001)
			, max_faces_to_sew(-1.0)
			, ifc_length_unit(1.0)
			, ifc_planeangle_unit(-1.0)
			, modelling_precision(0.00001)
			, dimensionality(1.)
			, placement_rel_to(0) {}

		bool convert(const taxonomy::item*, ifcopenshell::geometry::ConversionResults&);

		virtual bool convert_impl(const taxonomy::matrix4*, ifcopenshell::geometry::ConversionResults&) { throw std::runtime_error("Not implemented"); }
		virtual bool convert_impl(const taxonomy::point3*, ifcopenshell::geometry::ConversionResults&) { throw std::runtime_error("Not implemented"); }
		virtual bool convert_impl(const taxonomy::direction3*, ifcopenshell::geometry::ConversionResults&) { throw std::runtime_error("Not implemented"); }
		virtual bool convert_impl(const taxonomy::line*, ifcopenshell::geometry::ConversionResults&) { throw std::runtime_error("Not implemented"); }
		virtual bool convert_impl(const taxonomy::circle*, ifcopenshell::geometry::ConversionResults&) { throw std::runtime_error("Not implemented"); }
		virtual bool convert_impl(const taxonomy::ellipse*, ifcopenshell::geometry::ConversionResults&) { throw std::runtime_error("Not implemented"); }
		virtual bool convert_impl(const taxonomy::bspline_curve*, ifcopenshell::geometry::ConversionResults&) { throw std::runtime_error("Not implemented"); }
		virtual bool convert_impl(const taxonomy::edge*, ifcopenshell::geometry::ConversionResults&) { throw std::runtime_error("Not implemented"); }
		virtual bool convert_impl(const taxonomy::loop*, ifcopenshell::geometry::ConversionResults&) { throw std::runtime_error("Not implemented"); }
		virtual bool convert_impl(const taxonomy::shell*, ifcopenshell::geometry::ConversionResults&) { throw std::runtime_error("Not implemented"); }
		virtual bool convert_impl(const taxonomy::face*, ifcopenshell::geometry::ConversionResults&) { throw std::runtime_error("Not implemented"); }
		virtual bool convert_impl(const taxonomy::extrusion*, ifcopenshell::geometry::ConversionResults&) { throw std::runtime_error("Not implemented"); }
		virtual bool convert_impl(const taxonomy::node*, ifcopenshell::geometry::ConversionResults&) { throw std::runtime_error("Not implemented"); }
		virtual bool convert_impl(const taxonomy::colour*, ifcopenshell::geometry::ConversionResults&) { throw std::runtime_error("Not implemented"); }
		virtual bool convert_impl(const taxonomy::collection*, ifcopenshell::geometry::ConversionResults&);
	};

	AbstractKernel* construct(const std::string& geometry_library, IfcParse::IfcFile*);

}
}
}

#endif