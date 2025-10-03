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
			Logger::Notice("Cache hit #" + std::to_string(item->instance->as<IfcUtil::IfcBaseEntity>()->id()) +
				" -> #" + std::to_string(it->first->instance->as<IfcUtil::IfcBaseEntity>()->id()));
			return true;
		}
	}

	auto with_exception_handling = [&](auto fn) {
		try {
			return fn();
		} catch (std::exception& e) {
			Logger::Error(e, item->instance);
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
