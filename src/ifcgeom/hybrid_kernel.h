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

#ifndef HYBRID_KERNEL_H
#define HYBRID_KERNEL_H

#include "AbstractKernel.h"

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

namespace {
	inline bool is_valid_for_kernel(const ifcopenshell::geometry::kernels::AbstractKernel* k, const IfcGeom::ConversionResult& shp) {
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
		return false;
	}
}

namespace ifcopenshell {
	namespace geometry {
		namespace kernels {

			class HybridKernel : public ifcopenshell::geometry::kernels::AbstractKernel {
				std::vector<std::unique_ptr<AbstractKernel>> kernels_;
				ifcopenshell::geometry::abstract_mapping* mapping_;
				IfcParse::IfcFile* file_;
			public:
				HybridKernel(const std::string& name, IfcParse::IfcFile* file, Settings& settings, std::vector<std::unique_ptr<AbstractKernel>>&& kernels)
					: AbstractKernel(name, settings)
					, kernels_(std::move(kernels))
					, mapping_(ifcopenshell::geometry::impl::mapping_implementations().construct(file, settings))
					, file_(file)
				{
				}
				virtual bool supports_boolean_operations() const
				{
					for (auto& k : kernels_) {
						if (k->supports_boolean_operations()) {
							return true;
						}
					}
					return false;
				}
				virtual bool convert(const taxonomy::ptr item, IfcGeom::ConversionResults& rs)
				{
					auto ops = mapping_->find_openings(item->instance->as<IfcUtil::IfcBaseEntity>());
					bool has_openings = ops && ops->size();
					for (auto& k : kernels_) {
#ifdef IFOPSH_WITH_CGAL
						if (has_openings && !k->supports_boolean_operations()) {
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
						} catch (...) {}
						if (success) {
							return true;
						}
					}
					return false;
				}
				virtual bool apply_layerset(IfcGeom::ConversionResults& items, const ifcopenshell::geometry::layerset_information& layers)
				{
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
				virtual bool apply_folded_layerset(IfcGeom::ConversionResults& items, const ifcopenshell::geometry::layerset_information& layers, const std::map<IfcUtil::IfcBaseEntity*, ifcopenshell::geometry::layerset_information>& folds)
				{
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
							if (!is_valid_for_kernel(k.get(), s)) {
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
				virtual AbstractKernel* clone() const
				{
					std::vector<std::unique_ptr<AbstractKernel>> ks;
					for (auto& k : kernels_) {
						ks.emplace_back(k->clone());
					}
					// @todo ugly
					return new HybridKernel(geometry_library(), file_, const_cast<Settings&>(settings()), std::move(ks));
				}
			};

			inline std::unique_ptr<AbstractKernel> construct(IfcParse::IfcFile* file, const std::string& geometry_library, Settings& conv_settings) {
				std::string geometry_library_lower = boost::to_lower_copy(geometry_library);

#ifdef IFOPSH_WITH_OPENCASCADE
				if (geometry_library_lower == "opencascade") {
					return std::make_unique<IfcGeom::OpenCascadeKernel>(conv_settings);
				}
#endif

#ifdef IFOPSH_WITH_CGAL
				if (geometry_library_lower == "cgal") {
					return std::make_unique<CgalKernel>(conv_settings);
				}

				if (geometry_library_lower == "cgal-simple") {
					return std::make_unique<SimpleCgalKernel>(conv_settings);
				}
#endif

				if (geometry_library_lower.rfind("hybrid-", 0) == 0) {
					geometry_library_lower = geometry_library_lower.substr(strlen("hybrid"));
					std::vector<std::unique_ptr<AbstractKernel>> kernels;
					while (!geometry_library_lower.empty()) {
						if (geometry_library_lower.find("-", 0) == 0) {
							geometry_library_lower = geometry_library_lower.substr(strlen("-"));
						} else {
							throw IfcParse::IfcException("Invalid hybrid kernel " + geometry_library);
						}
						auto n = kernels.size();
#ifdef IFOPSH_WITH_OPENCASCADE
						if (geometry_library_lower.find("opencascade", 0) == 0) {
							kernels.emplace_back(new IfcGeom::OpenCascadeKernel(conv_settings));
							geometry_library_lower = geometry_library_lower.substr(strlen("opencascade"));
						}
#endif

#ifdef IFOPSH_WITH_CGAL
						if (geometry_library_lower.find("cgal-simple", 0) == 0) {
							kernels.emplace_back(new SimpleCgalKernel(conv_settings));
							geometry_library_lower = geometry_library_lower.substr(strlen("cgal-simple"));
						}

						if (geometry_library_lower.find("cgal", 0) == 0) {
							kernels.emplace_back(new CgalKernel(conv_settings));
							geometry_library_lower = geometry_library_lower.substr(strlen("cgal"));
						}
#endif
						if (kernels.size() != n + 1) {
							throw IfcParse::IfcException("Invalid hybrid kernel " + geometry_library);
						}
					}

					for (auto it = kernels.begin(); it != kernels.end(); ++it) {
						(**it).propagate_exceptions = it == kernels.begin();
						(**it).partial_success_is_success = it == kernels.end() - 1;
					}

					if (!kernels.empty()) {
						return std::make_unique<HybridKernel>(geometry_library, file, conv_settings, std::move(kernels));
					}
				}

				throw IfcParse::IfcException("No geometry kernel registered for " + geometry_library);
			}

		}
	}
}

#endif