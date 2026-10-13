#include "../ifcgeom/element.h"
#include "../ifcgeom/conversion_settings.h"
#include "../ifcgeom/abstract_mapping.h"
#include "../ifcgeom/function_item_evaluator.h"

#include "abstract_kernel.h"

using namespace ifcopenshell::geom;

const char* ifcopenshell::not_implemented_error::what() const noexcept {
	return "Not implemented.";
}

const char* ifcopenshell::not_supported_error::what() const noexcept {
	return "Not supported.";
}

bool ifcopenshell::geom::kernels::abstract_kernel::convert(const taxonomy::ptr item, std::vector<ifcopenshell::geom::conversion_result>& results) {
	if (settings_.get<settings::CacheShapes>().get()) {
		auto it = cache_.find(item);
		if (it != cache_.end()) {
			results = it->second;
			logger_.notice("SYS", 25, "Cache hit #" + std::to_string(item->instance.id()) +
				" -> #" + std::to_string(it->first->instance.id()));
			return true;
		}
	}

	auto with_exception_handling = [&](auto fn) {
		try {
			return fn();
		} catch (std::exception& e) {
			logger_.error("GEO", 27, e, item->instance);
			return false;
		} catch (...) {
			// @todo we can't log OCCT exceptions here, can we do some reraising to solve this?
			return false;
		}
	};
	auto without_exception_handling = [](auto fn) {
		return fn();
	};
	// Tessellated-shell approximation of a swept solid, so kernels without a native sweep (cgal) can consume it.
	auto try_sweep_approximation = [&]() -> std::optional<bool> {
		auto swp = taxonomy::dcast<taxonomy::sweep_along_curve>(item);
		if (!swp) {
			return std::nullopt;
		}
		auto shell = swp->as_shell(
			settings_.get<settings::CircleSegments>().get(),
			settings_.get<settings::MesherLinearDeflection>().get());
		if (!shell) {
			return std::nullopt;
		}
		return dispatch_conversion<0>::dispatch(this, shell->kind(), shell, results);
	};

	// Tessellated-shell approximation of a loft, so kernels without a native loft (cgal) can consume it.
	auto try_loft_approximation = [&]() -> std::optional<bool> {
		auto lft = taxonomy::dcast<taxonomy::loft>(item);
		if (!lft) {
			return std::nullopt;
		}
		auto shell = lft->as_shell();
		if (!shell) {
			return std::nullopt;
		}
		shell->matrix = lft->matrix;
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
			// No native conversion: approximate a swept solid or loft as a tessellated shell before giving up.
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

const ifcopenshell::geom::settings& ifcopenshell::geom::kernels::abstract_kernel::settings() const
{
	return settings_;
}

bool ifcopenshell::geom::kernels::abstract_kernel::convert_impl(const taxonomy::collection::ptr collection, std::vector<ifcopenshell::geom::conversion_result>& r) {
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

bool ifcopenshell::geom::kernels::abstract_kernel::convert_impl(const taxonomy::function_item::ptr item, std::vector<ifcopenshell::geom::conversion_result>& cs) {
   function_item_evaluator evaluator(settings(),item);
   auto expl = evaluator.evaluate();
	expl->instance = item->instance;
	return convert(expl, cs);
}

bool ifcopenshell::geom::kernels::abstract_kernel::convert_impl(const taxonomy::functor_item::ptr item, std::vector<ifcopenshell::geom::conversion_result>& cs) {
    function_item_evaluator evaluator(settings(), item);
    auto expl = evaluator.evaluate();
    expl->instance = item->instance;
    return convert(expl, cs);
}

bool ifcopenshell::geom::kernels::abstract_kernel::convert_impl(const taxonomy::piecewise_function::ptr item, std::vector<ifcopenshell::geom::conversion_result>& cs) {
    function_item_evaluator evaluator(settings(), item);
    auto expl = evaluator.evaluate();
    expl->instance = item->instance;
    return convert(expl, cs);
}

bool ifcopenshell::geom::kernels::abstract_kernel::convert_impl(const taxonomy::gradient_function::ptr item, std::vector<ifcopenshell::geom::conversion_result>& cs) {
    function_item_evaluator evaluator(settings(), item);
    auto expl = evaluator.evaluate();
    expl->instance = item->instance;
    return convert(expl, cs);
}

bool ifcopenshell::geom::kernels::abstract_kernel::convert_impl(const taxonomy::cant_function::ptr item, std::vector<ifcopenshell::geom::conversion_result>& cs) {
    function_item_evaluator evaluator(settings(), item);
    auto expl = evaluator.evaluate();
    expl->instance = item->instance;
    return convert(expl, cs);
}

bool ifcopenshell::geom::kernels::abstract_kernel::convert_impl(const taxonomy::offset_function::ptr item, std::vector<ifcopenshell::geom::conversion_result>& cs) {
    function_item_evaluator evaluator(settings(), item);
    auto expl = evaluator.evaluate();
    expl->instance = item->instance;
    return convert(expl, cs);
}
