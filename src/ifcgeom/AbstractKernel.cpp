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
	auto process_with_upgrade = [&]() {
		try {
			return dispatch_conversion<0>::dispatch(this, item->kind(), item, results);
		} catch (const not_implemented_error&) {
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

namespace {
	// Homogeneous taxonomy::point3 collections (e.g. IfcCartesianPointList3D)
	// are reduced to a single result, see #134/#1409/#5218.
	bool is_reducible_point_collection(const ifcopenshell::geometry::taxonomy::collection::ptr& collection) {
		if (collection->children.empty()) {
			return false;
		}
		for (auto& c : collection->children) {
			if (c->kind() != ifcopenshell::geometry::taxonomy::POINT3) {
				return false;
			}
		}
		return true;
	}
}

bool ifcopenshell::geometry::kernels::AbstractKernel::convert_impl(const taxonomy::collection::ptr collection, IfcGeom::ConversionResults& r) {
	if (collection->instance && is_reducible_point_collection(collection)) {
		// Reduce via the generic wrap_in_compound()/concat_many() API rather
		// than a per-kernel convert_impl(collection) override. concat_many()
		// combines everything in a single bulk call so kernels can implement
		// it in O(n): a loop calling concat() pairwise would either
		// re-classify an ever-growing accumulator (quadratic) or produce an
		// O(n)-deep nested shape (quadratic to traverse later).
		// Kept alive until concat_many() below: shapes[] holds raw pointers
		// into these ConversionResults' shared_ptr<ConversionResultShape>.
		IfcGeom::ConversionResults child_results;
		for (auto& c : collection->children) {
			if (!convert(c, child_results) && !partial_success_is_success) {
				return false;
			}
		}

		if (child_results.empty()) {
			return false;
		}

		std::vector<IfcGeom::ConversionResultShape*> shapes;
		shapes.reserve(child_results.size());
		for (auto& t : child_results) {
			shapes.push_back(t.Shape().get());
		}

		auto* first = shapes.front();
		std::vector<IfcGeom::ConversionResultShape*> rest(shapes.begin() + 1, shapes.end());
		auto* accum = first->concat_many(rest);

		r.emplace_back(IfcGeom::ConversionResult(collection->instance->as<IfcUtil::IfcBaseEntity>()->id(), accum, collection->surface_style));
		if (collection->matrix) {
			r.back().prepend(collection->matrix);
		}
		return true;
	}

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
