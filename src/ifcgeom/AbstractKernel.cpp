#include "AbstractKernel.h"

#include "../ifcgeom/IfcGeomElement.h"
#include "../ifcgeom/ConversionSettings.h"
#include "../ifcgeom/abstract_mapping.h"

#ifdef IFOPSH_WITH_OPENCASCADE
#include "../ifcgeom/kernels/opencascade/OpenCascadeKernel.h"
#undef Handle
#endif

#ifdef IFOPSH_WITH_CGAL
#include "../ifcgeom/kernels/cgal/CgalKernel.h"
#undef CGAL_KERNEL_H
#undef CGALCONVERSIONRESULT_H
#define IFOPSH_SIMPLE_KERNEL
#include "../ifcgeom/kernels/cgal/CgalKernel.h"
#undef CgalKernel
#endif

using namespace ifcopenshell::geometry;

bool ifcopenshell::geometry::kernels::AbstractKernel::convert(const taxonomy::ptr item, IfcGeom::ConversionResults& results) {
	// std::stringstream ss;
	// item->print(ss);
	// auto sss = ss.str();
	// std::wcout << sss.c_str() << std::endl;

	try {
		return dispatch_conversion<0>::dispatch(this, item->kind(), item, results);
	} catch (std::exception& e) {
		Logger::Error(e, item->instance);
		return false;
	} catch (...) {
		// @todo we can't log OCCT exceptions here, can we do some reraising to solve this?
		return false;
	}
}

const Settings& ifcopenshell::geometry::kernels::AbstractKernel::settings() const
{
	return settings_;
}


bool is_valid_for_kernel(const ifcopenshell::geometry::kernels::AbstractKernel* k, const IfcGeom::ConversionResult& shp) {
#ifdef IFOPSH_WITH_OPENCASCADE
	if (k->geometry_library() == "opencascade") {
		return dynamic_cast<ifcopenshell::geometry::OpenCascadeShape*>(shp.Shape().get()) != nullptr;
	}
#endif
#ifdef IFOPSH_WITH_CGAL
	if (k->geometry_library() == "cgal-simple") {
		return dynamic_cast<ifcopenshell::geometry::SimpleCgalShape*>(shp.Shape().get()) != nullptr;
	}
	if (k->geometry_library() == "cgal") {
		return dynamic_cast<ifcopenshell::geometry::CgalShape*>(shp.Shape().get()) != nullptr;
	}
#endif
}

class HybridKernel : public ifcopenshell::geometry::kernels::AbstractKernel {
	std::vector<AbstractKernel*> kernels_;
	ifcopenshell::geometry::abstract_mapping* mapping_;
public:
	HybridKernel(const std::string& name, IfcParse::IfcFile* file, Settings& settings, std::vector<AbstractKernel*> kernels)
		: AbstractKernel(name, settings)
		, kernels_(kernels)
		, mapping_(ifcopenshell::geometry::impl::mapping_implementations().construct(file, settings))
	{}
	virtual bool convert(const taxonomy::ptr item, IfcGeom::ConversionResults& rs) {
		auto ops = mapping_->find_openings(item->instance->as<IfcUtil::IfcBaseEntity>());
		bool has_openings = ops && ops->size();
		for (auto& k : kernels_) {
#ifdef IFOPSH_WITH_CGAL
			if (has_openings && dynamic_cast<ifcopenshell::geometry::kernels::SimpleCgalKernel*>(k)) {
				// @todo this would fail later on in the find_openings() call, because we have a
				// SimpleCgalShape which cannot be used on a kernel that supports booleans.
				// @todo 1 implement the translation between various conversion result shapes
				// @todo 2 fold the boolean result openings into the taxonomy item. This should be possible
				//         now that we have shared_ptr<item> and caching in place. So the inability
				//         to instance wouldn't matter as much.
				continue;
			}
#endif
			bool success = false;
			try {
				success = k->convert(item, rs);
			} catch(...) {}
			if (success) {
				return true;
			}
		}
		return false;
	}
	virtual bool apply_layerset(IfcGeom::ConversionResults& items, const ifcopenshell::geometry::layerset_information& layers) {
		for (auto& k : kernels_) {
			bool success = false;
			try {
				success = k->apply_layerset(items, layers);
			} catch (...) {}
			if (success) {
				return true;
			}
		}
		return false;
	}
	virtual bool apply_folded_layerset(IfcGeom::ConversionResults& items, const ifcopenshell::geometry::layerset_information& layers, const std::map<IfcUtil::IfcBaseEntity*, ifcopenshell::geometry::layerset_information>& folds) {
		for (auto& k : kernels_) {
			bool success = false;
			try {
				success = k->apply_folded_layerset(items, layers, folds);
			} catch (...) {}
			if (success) {
				return true;
			}
		}
		return false;
	}
	virtual bool convert_openings(const IfcUtil::IfcBaseEntity* entity, const std::vector<std::pair<taxonomy::ptr, ifcopenshell::geometry::taxonomy::matrix4>>& openings,
		const IfcGeom::ConversionResults& entity_shapes, const ifcopenshell::geometry::taxonomy::matrix4& entity_trsf, IfcGeom::ConversionResults& cut_shapes)
	{
		for (auto& k : kernels_) {
			bool is_valid = true;
			for (auto& s : entity_shapes) {
				if (!is_valid_for_kernel(k, s)) {
					is_valid = false;
					break;
				}
			}
			if (!is_valid) {
				continue;
			}
			bool success = false;
			try {
				success = k->convert_openings(entity, openings, entity_shapes, entity_trsf, cut_shapes);
			} catch (...) {}
			if (success) {
				return true;
			}
		}
		return false;
	}
};

ifcopenshell::geometry::kernels::AbstractKernel* ifcopenshell::geometry::kernels::construct(IfcParse::IfcFile* file, const std::string& geometry_library, Settings& conv_settings) {
	std::string geometry_library_lower = boost::to_lower_copy(geometry_library);

#ifdef IFOPSH_WITH_OPENCASCADE
	if (geometry_library_lower == "opencascade") {
		return new IfcGeom::OpenCascadeKernel(conv_settings);
	}
#endif

#ifdef IFOPSH_WITH_CGAL
	if (geometry_library_lower == "cgal") {
		return new CgalKernel(conv_settings);
	}

	if (geometry_library_lower == "cgal-simple") {
		return new SimpleCgalKernel(conv_settings);
	}
#endif

	if (geometry_library_lower.rfind("hybrid-", 0) == 0) {
		geometry_library_lower = geometry_library_lower.substr(strlen("hybrid"));
		std::vector<AbstractKernel*> kernels;
		while (!geometry_library_lower.empty()) {
			if (geometry_library_lower.find("-", 0) == 0) {
				geometry_library_lower = geometry_library_lower.substr(strlen("-"));
			} else {
				throw IfcParse::IfcException("Invalid hybrid kernel " + geometry_library);
			}
			auto n = kernels.size();
#ifdef IFOPSH_WITH_OPENCASCADE
			if (geometry_library_lower.find("opencascade", 0) == 0) {
				kernels.push_back(new IfcGeom::OpenCascadeKernel(conv_settings));
				geometry_library_lower = geometry_library_lower.substr(strlen("opencascade"));
			}
#endif

#ifdef IFOPSH_WITH_CGAL
			if (geometry_library_lower.find("cgal-simple", 0) == 0) {
				kernels.push_back(new SimpleCgalKernel(conv_settings));
				geometry_library_lower = geometry_library_lower.substr(strlen("cgal-simple"));
			}

			if (geometry_library_lower.find("cgal", 0) == 0) {
				kernels.push_back(new CgalKernel(conv_settings));
				geometry_library_lower = geometry_library_lower.substr(strlen("cgal"));
			}
#endif
			if (kernels.size() != n + 1) {
				throw IfcParse::IfcException("Invalid hybrid kernel " + geometry_library);
			}
		}

		if (!kernels.empty()) {
			return new HybridKernel(geometry_library, file, conv_settings, kernels);
		}
	}
	
	throw IfcParse::IfcException("No geometry kernel registered for " + geometry_library);
}

bool ifcopenshell::geometry::kernels::AbstractKernel::convert_impl(const taxonomy::collection::ptr collection, IfcGeom::ConversionResults& r) {
	auto s = r.size();
	for (auto& c : collection->children) {
		convert(c, r);
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

bool ifcopenshell::geometry::kernels::AbstractKernel::convert_impl(const taxonomy::piecewise_function::ptr item, IfcGeom::ConversionResults& cs) {
	auto expl = item->evaluate();
	expl->instance = item->instance;
	return convert(expl, cs);
}
