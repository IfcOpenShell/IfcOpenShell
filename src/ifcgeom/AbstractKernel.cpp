#include "../ifcgeom/IfcGeomElement.h"
#include "../ifcgeom/ConversionSettings.h"
#include "../ifcgeom/abstract_mapping.h"
#include "../ifcgeom/function_item_evaluator.h"

#include "AbstractKernel.h"

using namespace ifcopenshell::geometry;

const char* ifcopenshell::not_implemented_error::what() const noexcept {
	return "Not implemented.";
}

const char* ifcopenshell::not_supported_error::what() const noexcept {
	return "Not supported.";
}

bool ifcopenshell::geometry::kernels::AbstractKernel::convert(const taxonomy::ptr item, IfcGeom::ConversionResults& results) {
	if (settings_.get<settings::CacheShapes>().get()) {
		auto it = cache_.find(item);
		if (it != cache_.end()) {
			results = it->second;
			logger_.Notice("SYS", 25, "Cache hit #" + std::to_string(item->instance->as<IfcUtil::IfcBaseEntity>()->id()) +
				" -> #" + std::to_string(it->first->instance->as<IfcUtil::IfcBaseEntity>()->id()));
			return true;
		}
	}

	auto with_exception_handling = [&](auto fn) {
		try {
			return fn();
		} catch (std::exception& e) {
			logger_.Error("GEO", 27, e, item->instance);
			return false;
		} catch (...) {
			// @todo we can't log OCCT exceptions here, can we do some reraising to solve this?
			return false;
		}
	};
	auto without_exception_handling = [](auto fn) {
		return fn();
	};
	// Kernel-agnostic approximation of a swept solid as a tessellated shell
	// (Eigen only, see taxonomy::sweep_along_curve::as_shell). This lets kernels
	// without a native sweep (cgal) consume it, and lets any kernel be forced onto
	// the approximation for verification via the ApproximateSweptSolids setting.
	auto try_sweep_approximation = [&]() -> boost::optional<bool> {
		auto swp = taxonomy::dcast<taxonomy::sweep_along_curve>(item);
		if (!swp) {
			return boost::none;
		}
		auto shell = swp->as_shell(
			settings_.get<settings::CircleSegments>().get(),
			settings_.get<settings::MesherLinearDeflection>().get());
		if (!shell) {
			return boost::none;
		}
		return dispatch_conversion<0>::dispatch(this, shell->kind(), shell, results);
	};

	// Kernel-agnostic faceted lofting (Eigen only, see taxonomy::loft::as_shell).
	// The polyhedral loft logic no longer lives only in the opencascade kernel, so
	// a kernel without a native loft (cgal) can consume the tessellated shell
	// instead of dropping the item.
	auto try_loft_approximation = [&]() -> boost::optional<bool> {
		auto lft = taxonomy::dcast<taxonomy::loft>(item);
		if (!lft) {
			return boost::none;
		}
		auto shell = lft->as_shell();
		if (!shell) {
			return boost::none;
		}
		return dispatch_conversion<0>::dispatch(this, shell->kind(), shell, results);
	};

	auto process_with_upgrade = [&]() {
		// Forced approximation mode: applies to every kernel (including opencascade).
		if (settings_.get<settings::ApproximateSweptSolids>().get()) {
			if (auto res = try_sweep_approximation()) {
				return *res;
			}
		}
		try {
			return dispatch_conversion<0>::dispatch(this, item->kind(), item, results);
		} catch (const not_implemented_error&) {
			// The kernel has no native conversion for this item. If it is a swept
			// solid or a loft, fall back to the tessellated-shell approximation
			// before giving up.
			if (auto res = try_sweep_approximation()) {
				return *res;
			}
			if (auto res = try_loft_approximation()) {
				return *res;
			}
			return dispatch_with_upgrade<0>::dispatch(this, item, results);
		}
	};

	bool res;
	if (propagate_exceptions) {
		res = without_exception_handling(process_with_upgrade);
	} else {
		res = with_exception_handling(process_with_upgrade);
	}

	if (settings_.get<settings::CacheShapes>().get() && res) {
		cache_.insert({ item, results });
	}

	return res;
}

const Settings& ifcopenshell::geometry::kernels::AbstractKernel::settings() const
{
	return settings_;
}

bool ifcopenshell::geometry::kernels::AbstractKernel::convert_impl(const taxonomy::collection::ptr collection, IfcGeom::ConversionResults& r) {
	auto s = r.size();
	for (auto& c : collection->children) {
		if (!convert(c, r) && !partial_success_is_success) {
			return false;
		}
	}
	for (auto i = s; i < r.size(); ++i) {
		if (collection->matrix) {
			r[i].prepend(collection->matrix);
		}
		if (!r[i].hasStyle() && collection->surface_style) {
			r[i].setStyle(collection->surface_style);
		}
	}
	return r.size() > s;
}

bool ifcopenshell::geometry::kernels::AbstractKernel::convert_impl(const taxonomy::function_item::ptr item, IfcGeom::ConversionResults& cs) {
   function_item_evaluator evaluator(settings(),item);
   auto expl = evaluator.evaluate();
	expl->instance = item->instance;
	return convert(expl, cs);
}

bool ifcopenshell::geometry::kernels::AbstractKernel::convert_impl(const taxonomy::functor_item::ptr item, IfcGeom::ConversionResults& cs) {
    function_item_evaluator evaluator(settings(), item);
    auto expl = evaluator.evaluate();
    expl->instance = item->instance;
    return convert(expl, cs);
}

bool ifcopenshell::geometry::kernels::AbstractKernel::convert_impl(const taxonomy::piecewise_function::ptr item, IfcGeom::ConversionResults& cs) {
    function_item_evaluator evaluator(settings(), item);
    auto expl = evaluator.evaluate();
    expl->instance = item->instance;
    return convert(expl, cs);
}

bool ifcopenshell::geometry::kernels::AbstractKernel::convert_impl(const taxonomy::gradient_function::ptr item, IfcGeom::ConversionResults& cs) {
    function_item_evaluator evaluator(settings(), item);
    auto expl = evaluator.evaluate();
    expl->instance = item->instance;
    return convert(expl, cs);
}

bool ifcopenshell::geometry::kernels::AbstractKernel::convert_impl(const taxonomy::cant_function::ptr item, IfcGeom::ConversionResults& cs) {
    function_item_evaluator evaluator(settings(), item);
    auto expl = evaluator.evaluate();
    expl->instance = item->instance;
    return convert(expl, cs);
}

bool ifcopenshell::geometry::kernels::AbstractKernel::convert_impl(const taxonomy::offset_function::ptr item, IfcGeom::ConversionResults& cs) {
    function_item_evaluator evaluator(settings(), item);
    auto expl = evaluator.evaluate();
    expl->instance = item->instance;
    return convert(expl, cs);
}
