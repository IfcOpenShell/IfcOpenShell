/********************************************************************************
 *                                                                              *
 * This file is part of IfcOpenShell.                                           *
 *                                                                              *
 * IfcOpenShell is free software: you can redistribute it and/or modify         *
 * it under the terms of the Lesser GNU General Public License as published by  *
 * the Free Software Foundation, either version 3.0 of the License, or          *
 * (at your option) any later version.                                          *
 *                                                                              *
 * IfcOpenShell is distributed in the hope that it will be useful,              *
 * but WITHOUT ANY WARRANTY; without even the implied warranty of               *
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the                 *
 * Lesser GNU General Public License for more details.                          *
 *                                                                              *
 * You should have received a copy of the Lesser GNU General Public License     *
 * along with this program. If not, see <http://www.gnu.org/licenses/>.         *
 *                                                                              *
 ********************************************************************************/

#ifndef ABSTRACT_KERNEL_H
#define ABSTRACT_KERNEL_H

#include "../ifcparse/macros.h"
#include "../ifcparse/logger.h"
#include "../ifcgeom/ifc_geom_api.h"
#include "../ifcgeom/representation.h"
#include "../ifcgeom/taxonomy.h"
#include "../ifcgeom/conversion_settings.h"
#include "../ifcgeom/abstract_mapping.h"

#include <string_view>

static const double ALMOST_ZERO = 1.e-9;

template <typename T>
inline static bool ALMOST_THE_SAME(const T& a, const T& b, double tolerance = ALMOST_ZERO) {
	return fabs(a - b) < tolerance;
}

namespace ifcopenshell {

#if defined(_MSC_VER)
#pragma warning(push)
#pragma warning(disable: 4275)
#endif

	class IFC_GEOM_API not_implemented_error : public std::exception {
	public:
		const char* what() const noexcept override;
	};

	class IFC_GEOM_API not_supported_error : public std::exception {
	public:
		const char* what() const noexcept override;
	};

#if defined(_MSC_VER)
#pragma warning(pop)
#endif

	namespace geom { namespace kernels {

	class IFC_GEOM_API abstract_kernel {
	private:
		std::unordered_map<taxonomy::item::ptr, std::vector<ifcopenshell::geom::conversion_result>, ifcopenshell::geom::taxonomy::hash_functor, ifcopenshell::geom::taxonomy::equal_functor> cache_;
	protected:
		std::string geometry_library_;
		ifcopenshell::geom::settings settings_;
		ifcopenshell::logger& logger_;
	public:
		bool propagate_exceptions = false;
		bool partial_success_is_success = true;

		abstract_kernel(const std::string& geometry_library, const ifcopenshell::geom::settings& settings, ifcopenshell::logger& logger = ifcopenshell::logger::root())
			: geometry_library_(geometry_library)
			, settings_(settings)
			, logger_(logger) {}

		virtual ~abstract_kernel() = default;

		virtual bool convert(const taxonomy::ptr, std::vector<ifcopenshell::geom::conversion_result>&);
		const ifcopenshell::geom::settings& settings() const;
		const std::string& geometry_library() const {
			return geometry_library_;
		}
		virtual std::string_view backend_id() const {
			return geometry_library_;
		}
		virtual bool accepts(const ifcopenshell::geom::conversion_result_shape& shape) const {
			return shape.backend_id() == backend_id();
		}
		ifcopenshell::logger& logger() const { return logger_; }

		virtual bool supports_boolean_operations() const = 0;

		virtual bool convert_impl(const taxonomy::matrix4::ptr, std::vector<ifcopenshell::geom::conversion_result>&) { throw not_implemented_error(); }
		virtual bool convert_impl(const taxonomy::point3::ptr, std::vector<ifcopenshell::geom::conversion_result>&) { throw not_implemented_error(); }
		virtual bool convert_impl(const taxonomy::direction3::ptr, std::vector<ifcopenshell::geom::conversion_result>&) { throw not_implemented_error(); }
		virtual bool convert_impl(const taxonomy::line::ptr, std::vector<ifcopenshell::geom::conversion_result>&) { throw not_implemented_error(); }
		virtual bool convert_impl(const taxonomy::circle::ptr, std::vector<ifcopenshell::geom::conversion_result>&) { throw not_implemented_error(); }
		virtual bool convert_impl(const taxonomy::ellipse::ptr, std::vector<ifcopenshell::geom::conversion_result>&) { throw not_implemented_error(); }
		virtual bool convert_impl(const taxonomy::bspline_curve::ptr, std::vector<ifcopenshell::geom::conversion_result>&) { throw not_implemented_error(); }
		virtual bool convert_impl(const taxonomy::edge::ptr, std::vector<ifcopenshell::geom::conversion_result>&) { throw not_implemented_error(); }
		virtual bool convert_impl(const taxonomy::loop::ptr, std::vector<ifcopenshell::geom::conversion_result>&) { throw not_implemented_error(); }
		virtual bool convert_impl(const taxonomy::shell::ptr, std::vector<ifcopenshell::geom::conversion_result>&) { throw not_implemented_error(); }
		virtual bool convert_impl(const taxonomy::face::ptr, std::vector<ifcopenshell::geom::conversion_result>&) { throw not_implemented_error(); }
		virtual bool convert_impl(const taxonomy::extrusion::ptr, std::vector<ifcopenshell::geom::conversion_result>&) { throw not_implemented_error(); }
		virtual bool convert_impl(const taxonomy::node::ptr, std::vector<ifcopenshell::geom::conversion_result>&) { throw not_implemented_error(); }
		virtual bool convert_impl(const taxonomy::colour::ptr, std::vector<ifcopenshell::geom::conversion_result>&) { throw not_implemented_error(); }
		virtual bool convert_impl(const taxonomy::boolean_result::ptr, std::vector<ifcopenshell::geom::conversion_result>&) { throw not_implemented_error(); }
		virtual bool convert_impl(const taxonomy::plane::ptr, std::vector<ifcopenshell::geom::conversion_result>&) { throw not_implemented_error(); }
		virtual bool convert_impl(const taxonomy::offset_curve::ptr, std::vector<ifcopenshell::geom::conversion_result>&) { throw not_implemented_error(); }
		virtual bool convert_impl(const taxonomy::revolve::ptr, std::vector<ifcopenshell::geom::conversion_result>&) { throw not_implemented_error(); }
		virtual bool convert_impl(const taxonomy::bspline_surface::ptr, std::vector<ifcopenshell::geom::conversion_result>&) { throw not_implemented_error(); }
		virtual bool convert_impl(const taxonomy::cylinder::ptr, std::vector<ifcopenshell::geom::conversion_result>&) { throw not_implemented_error(); }
		virtual bool convert_impl(const taxonomy::sphere::ptr, std::vector<ifcopenshell::geom::conversion_result>&) { throw not_implemented_error(); }
		virtual bool convert_impl(const taxonomy::torus::ptr, std::vector<ifcopenshell::geom::conversion_result>&) { throw not_implemented_error(); }
		virtual bool convert_impl(const taxonomy::solid::ptr, std::vector<ifcopenshell::geom::conversion_result>&) { throw not_implemented_error(); }
		virtual bool convert_impl(const taxonomy::sweep_along_curve::ptr, std::vector<ifcopenshell::geom::conversion_result>&) { throw not_implemented_error(); }
		virtual bool convert_impl(const taxonomy::loft::ptr, std::vector<ifcopenshell::geom::conversion_result>&) { throw not_implemented_error(); }
		virtual bool convert_impl(const taxonomy::collection::ptr, std::vector<ifcopenshell::geom::conversion_result>&);
		virtual bool convert_impl(const taxonomy::function_item::ptr item, std::vector<ifcopenshell::geom::conversion_result>& cs);
      virtual bool convert_impl(const taxonomy::functor_item::ptr item, std::vector<ifcopenshell::geom::conversion_result>& cs);
      virtual bool convert_impl(const taxonomy::piecewise_function::ptr item, std::vector<ifcopenshell::geom::conversion_result>& cs);
      virtual bool convert_impl(const taxonomy::gradient_function::ptr item, std::vector<ifcopenshell::geom::conversion_result>& cs);
      virtual bool convert_impl(const taxonomy::cant_function::ptr item, std::vector<ifcopenshell::geom::conversion_result>& cs);
      virtual bool convert_impl(const taxonomy::offset_function::ptr item, std::vector<ifcopenshell::geom::conversion_result>& cs);

		/*
		virtual void set_offset(const std::array<double, 3> &p_offset);
		virtual void set_rotation(const std::array<double, 4> &p_rotation);
		*/

		virtual bool apply_layerset(std::vector<ifcopenshell::geom::conversion_result>&, const ifcopenshell::geom::layerset_information&) { throw not_implemented_error(); }
		virtual bool apply_folded_layerset(std::vector<ifcopenshell::geom::conversion_result>&, const ifcopenshell::geom::layerset_information&, const std::map<express::base, ifcopenshell::geom::layerset_information>&) { throw not_implemented_error(); }
		virtual bool convert_openings(const express::base& entity, const std::vector<std::pair<taxonomy::ptr, ifcopenshell::geom::taxonomy::matrix4>>& openings,
			const std::vector<ifcopenshell::geom::conversion_result>& entity_shapes, const ifcopenshell::geom::taxonomy::matrix4& entity_trsf, std::vector<ifcopenshell::geom::conversion_result>& cut_shapes) = 0;
		virtual bool unify_shapes(const std::vector<ifcopenshell::geom::conversion_result>&, std::vector<ifcopenshell::geom::conversion_result>&) { throw not_implemented_error(); }

		virtual abstract_kernel* clone(ifcopenshell::logger& logger) const = 0;
	};
}
}
}


namespace {
	/* A compile-time for loop over the taxonomy kinds */
	template <size_t N>
	struct dispatch_conversion {
		static bool dispatch(ifcopenshell::geom::kernels::abstract_kernel* kernel, ifcopenshell::geom::taxonomy::kinds item_kind, const ifcopenshell::geom::taxonomy::ptr& item, std::vector<ifcopenshell::geom::conversion_result>& results) {
			if (N == item_kind) {
				auto concrete_item = std::static_pointer_cast<ifcopenshell::geom::taxonomy::type_by_kind::type<N>>(item);
				return kernel->convert_impl(concrete_item, results);
			} else {
				return dispatch_conversion<N + 1>::dispatch(kernel, item_kind, item, results);
			}
		}
	};

	template <>
	struct dispatch_conversion<ifcopenshell::geom::taxonomy::type_by_kind::max> {
        static bool dispatch(ifcopenshell::geom::kernels::abstract_kernel* kernel, ifcopenshell::geom::taxonomy::kinds, const ifcopenshell::geom::taxonomy::ptr& item, std::vector<ifcopenshell::geom::conversion_result>&) {
            if (kernel->partial_success_is_success) {
				std::string created_from;
				if (item->instance) {
					created_from = " (created from " + item->instance.declaration().name() + ")";
				}
				kernel->logger().error("UNS", 1, "No support for " + ifcopenshell::geom::taxonomy::kind_to_string(item->kind()) + created_from + " in kernel " + kernel->geometry_library());
			}
			return false;
		}
	};

	template <size_t N>
	struct dispatch_with_upgrade {
		static bool dispatch(ifcopenshell::geom::kernels::abstract_kernel* kernel, const ifcopenshell::geom::taxonomy::ptr& item, std::vector<ifcopenshell::geom::conversion_result>& results) {
			auto concrete_item = ifcopenshell::geom::taxonomy::template dcast<ifcopenshell::geom::taxonomy::upgrades::type<N>>(item);
			if (concrete_item) {
				return kernel->convert_impl(concrete_item, results);
			} else {
				return dispatch_with_upgrade<N + 1>::dispatch(kernel, item, results);
			}
		}
	};

	template <>
	struct dispatch_with_upgrade<ifcopenshell::geom::taxonomy::upgrades::max> {
		static bool dispatch(ifcopenshell::geom::kernels::abstract_kernel* kernel, const ifcopenshell::geom::taxonomy::ptr& item, std::vector<ifcopenshell::geom::conversion_result>&) {
            if (kernel->partial_success_is_success) {
				std::string created_from;
				if (item->instance) {
					created_from = " (created from " + item->instance.declaration().name() + ")";
				}
				kernel->logger().error("UNS", 2, "No support (after considering item upgrade) for " + ifcopenshell::geom::taxonomy::kind_to_string(item->kind()) + created_from + " in kernel " + kernel->geometry_library());
			}
			return false;
		}
	};

	template <class T, class Tuple>
	struct tuple_type_index;

	template <class T, class... Types>
	struct tuple_type_index<T, std::tuple<T, Types...>> {
		static const std::size_t value = 0;
	};

	template <class T, class U, class... Types>
	struct tuple_type_index<T, std::tuple<U, Types...>> {
		static const std::size_t value = 1 + tuple_type_index<T, std::tuple<Types...>>::value;
	};

	/* A compile-time for loop over the curve kinds */
	template <typename T, size_t N = 0>
	struct dispatch_curve_creation {
		static bool dispatch(const ifcopenshell::geom::taxonomy::ptr& item, T& visitor) {
			constexpr auto KindIndex = tuple_type_index<std::tuple_element_t<N, ifcopenshell::geom::taxonomy::impl::curves_tuple>, ifcopenshell::geom::taxonomy::impl::kinds_tuple>::value;
			if (item->kind() == KindIndex) {
				auto concrete_item = std::static_pointer_cast<ifcopenshell::geom::taxonomy::curves::type<N>>(item);
				visitor(concrete_item);
				return true;
			} else {
				return dispatch_curve_creation<T, N + 1>::dispatch(item, visitor);
			}
		}
	};

	template <typename T>
	struct dispatch_curve_creation<T, ifcopenshell::geom::taxonomy::curves::max> {
		static bool dispatch(const ifcopenshell::geom::taxonomy::ptr& item, T&) {
			ifcopenshell::logger::root().error("GEO", 28, "No conversion for " + std::to_string(item->kind()));
			return false;
		}
	};

	/* A compile-time for loop over the curve kinds */
	template <typename T, size_t N = 0>
	struct dispatch_surface_creation {
		static bool dispatch(const ifcopenshell::geom::taxonomy::ptr& item, T& visitor) {
			auto v = ifcopenshell::geom::taxonomy::template dcast<ifcopenshell::geom::taxonomy::surfaces::type<N>>(item);
			if (v && item->kind() == v->kind()) {
				visitor(v);
				return true;
			} else {
				return dispatch_surface_creation<T, N + 1>::dispatch(item, visitor);
			}
		}
	};

	template <typename T>
	struct dispatch_surface_creation<T, ifcopenshell::geom::taxonomy::surfaces::max> {
		static bool dispatch(const ifcopenshell::geom::taxonomy::ptr& item, T&) {
			ifcopenshell::logger::root().error("GEO", 29, "No conversion for " + std::to_string(item->kind()));
			return false;
		}
	};
}

#endif
