#ifndef ABSTRACT_KERNEL_H
#define ABSTRACT_KERNEL_H

#include "../ifcparse/macros.h"
#include "../ifcparse/IfcLogger.h"
#include "../ifcgeom/ifc_geom_api.h"
#include "../ifcgeom/IfcGeomRepresentation.h"
#include "../ifcgeom/taxonomy.h"
#include "../ifcgeom/ConversionSettings.h"

static const double ALMOST_ZERO = 1.e-9;

template <typename T>
inline static bool ALMOST_THE_SAME(const T& a, const T& b, double tolerance = ALMOST_ZERO) {
	return fabs(a - b) < tolerance;
}

namespace ifcopenshell { namespace geometry { namespace kernels {

	class IFC_GEOM_API AbstractKernel {
	protected:
		std::string geometry_library;
		ConversionSettings conv_settings_;

	public:
		AbstractKernel(const std::string& geometry_library, const ConversionSettings& settings)
			: geometry_library(geometry_library)
			, conv_settings_(settings) {}

		bool convert(const taxonomy::ptr, IfcGeom::ConversionResults&);
		const ConversionSettings& settings() const;

		virtual bool convert_impl(const taxonomy::matrix4::ptr, IfcGeom::ConversionResults&) { throw std::runtime_error("Not implemented"); }
		virtual bool convert_impl(const taxonomy::point3::ptr, IfcGeom::ConversionResults&) { throw std::runtime_error("Not implemented"); }
		virtual bool convert_impl(const taxonomy::direction3::ptr, IfcGeom::ConversionResults&) { throw std::runtime_error("Not implemented"); }
		virtual bool convert_impl(const taxonomy::line::ptr, IfcGeom::ConversionResults&) { throw std::runtime_error("Not implemented"); }
		virtual bool convert_impl(const taxonomy::circle::ptr, IfcGeom::ConversionResults&) { throw std::runtime_error("Not implemented"); }
		virtual bool convert_impl(const taxonomy::ellipse::ptr, IfcGeom::ConversionResults&) { throw std::runtime_error("Not implemented"); }
		virtual bool convert_impl(const taxonomy::bspline_curve::ptr, IfcGeom::ConversionResults&) { throw std::runtime_error("Not implemented"); }
		virtual bool convert_impl(const taxonomy::edge::ptr, IfcGeom::ConversionResults&) { throw std::runtime_error("Not implemented"); }
		virtual bool convert_impl(const taxonomy::loop::ptr, IfcGeom::ConversionResults&) { throw std::runtime_error("Not implemented"); }
		virtual bool convert_impl(const taxonomy::shell::ptr, IfcGeom::ConversionResults&) { throw std::runtime_error("Not implemented"); }
		virtual bool convert_impl(const taxonomy::face::ptr, IfcGeom::ConversionResults&) { throw std::runtime_error("Not implemented"); }
		virtual bool convert_impl(const taxonomy::extrusion::ptr, IfcGeom::ConversionResults&) { throw std::runtime_error("Not implemented"); }
		virtual bool convert_impl(const taxonomy::node::ptr, IfcGeom::ConversionResults&) { throw std::runtime_error("Not implemented"); }
		virtual bool convert_impl(const taxonomy::colour::ptr, IfcGeom::ConversionResults&) { throw std::runtime_error("Not implemented"); }
		virtual bool convert_impl(const taxonomy::boolean_result::ptr, IfcGeom::ConversionResults&) { throw std::runtime_error("Not implemented"); }
		virtual bool convert_impl(const taxonomy::plane::ptr, IfcGeom::ConversionResults&) { throw std::runtime_error("Not implemented"); }
		virtual bool convert_impl(const taxonomy::offset_curve::ptr, IfcGeom::ConversionResults&) { throw std::runtime_error("Not implemented"); }
		virtual bool convert_impl(const taxonomy::revolve::ptr, IfcGeom::ConversionResults&) { throw std::runtime_error("Not implemented"); }
		virtual bool convert_impl(const taxonomy::bspline_surface::ptr, IfcGeom::ConversionResults&) { throw std::runtime_error("Not implemented"); }
		virtual bool convert_impl(const taxonomy::cylinder::ptr, IfcGeom::ConversionResults&) { throw std::runtime_error("Not implemented"); }
		virtual bool convert_impl(const taxonomy::solid::ptr, IfcGeom::ConversionResults&) { throw std::runtime_error("Not implemented"); }
		virtual bool convert_impl(const taxonomy::surface_curve_sweep::ptr, IfcGeom::ConversionResults&) { throw std::runtime_error("Not implemented"); }
		virtual bool convert_impl(const taxonomy::loft::ptr, IfcGeom::ConversionResults&) { throw std::runtime_error("Not implemented"); }
		virtual bool convert_impl(const taxonomy::collection::ptr, IfcGeom::ConversionResults&);

		/*
		virtual void set_offset(const std::array<double, 3> &p_offset);
		virtual void set_rotation(const std::array<double, 4> &p_rotation);
		*/

		virtual bool apply_layerset(IfcGeom::ConversionResults&, const ifcopenshell::geometry::layerset_information&) { throw std::runtime_error("Not implemented"); }
		virtual bool apply_folded_layerset(IfcGeom::ConversionResults&, const ifcopenshell::geometry::layerset_information&, const std::map<IfcUtil::IfcBaseEntity*, ifcopenshell::geometry::layerset_information>&) { throw std::runtime_error("Not implemented"); }
		virtual bool convert_openings(const IfcUtil::IfcBaseEntity* entity, const std::vector<std::pair<taxonomy::ptr, ifcopenshell::geometry::taxonomy::matrix4>>& openings,
			const IfcGeom::ConversionResults& entity_shapes, const ifcopenshell::geometry::taxonomy::matrix4& entity_trsf, IfcGeom::ConversionResults& cut_shapes) = 0;

	};

	AbstractKernel* construct(const std::string& geometry_library, const ConversionSettings& conv_settings);

}
}
}


namespace {
	/* A compile-time for loop over the taxonomy kinds */
	template <size_t N>
	struct dispatch_conversion {
		static bool dispatch(ifcopenshell::geometry::kernels::AbstractKernel* kernel, const ifcopenshell::geometry::taxonomy::ptr item, IfcGeom::ConversionResults& results) {
			if (N == item->kind()) {
				auto concrete_item = taxonomy::template cast<ifcopenshell::geometry::taxonomy::type_by_kind::type<N>>(item);
				return kernel->convert_impl(concrete_item, results);
			} else {
				return dispatch_conversion<N + 1>::dispatch(kernel, item, results);
			}
		}
	};

	template <>
	struct dispatch_conversion<ifcopenshell::geometry::taxonomy::type_by_kind::max> {
		static bool dispatch(ifcopenshell::geometry::kernels::AbstractKernel*, const ifcopenshell::geometry::taxonomy::ptr item, IfcGeom::ConversionResults&) {
			Logger::Error("No conversion for " + std::to_string(item->kind()));
			return false;
		}
	};

	/* A compile-time for loop over the curve kinds */
	template <typename T, size_t N = 0>
	struct dispatch_curve_creation {
		static bool dispatch(const ifcopenshell::geometry::taxonomy::ptr item, T& visitor) {
			// @todo it should be possible to eliminate this dynamic_cast when there is a static equivalent to kind()
			auto v = taxonomy::template dcast<ifcopenshell::geometry::taxonomy::curves::type<N>>(item);
			if (v) {
				visitor(v);
				return true;
			} else {
				return dispatch_curve_creation<T, N + 1>::dispatch(item, visitor);
			}
		}
	};

	template <typename T>
	struct dispatch_curve_creation<T, ifcopenshell::geometry::taxonomy::curves::max> {
		static bool dispatch(const ifcopenshell::geometry::taxonomy::ptr item, T&) {
			Logger::Error("No conversion for " + std::to_string(item->kind()));
			return false;
		}
	};
}

#endif