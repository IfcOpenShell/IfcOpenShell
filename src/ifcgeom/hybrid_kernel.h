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
#include "kernel_registry.h"

namespace ifcopenshell {
	namespace geometry {
		namespace kernels {

			class HybridKernel : public ifcopenshell::geometry::kernels::AbstractKernel {
				std::vector<std::unique_ptr<AbstractKernel>> kernels_;
				ifcopenshell::geometry::abstract_mapping* mapping_;
				ifcopenshell::file* file_;
			public:
				HybridKernel(const std::string& name, ifcopenshell::file* file, Settings& settings, std::vector<std::unique_ptr<AbstractKernel>>&& kernels, Logger& logger = Logger::Root())
					: AbstractKernel(name, settings, logger)
					, kernels_(std::move(kernels))
					, mapping_(ifcopenshell::geometry::impl::mapping_implementations().construct(file, settings, logger))
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
					auto ops = mapping_->find_openings(item->instance);
					bool has_openings = ops.size();
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
						if (has_openings && k->geometry_library() == "passthrough") {
							continue;
						}
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
				virtual bool apply_folded_layerset(IfcGeom::ConversionResults& items, const ifcopenshell::geometry::layerset_information& layers, const std::map<express::Base, ifcopenshell::geometry::layerset_information>& folds)
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
                virtual bool convert_openings(const express::Base& entity, const std::vector<std::pair<taxonomy::ptr, ifcopenshell::geometry::taxonomy::matrix4>>& openings,
					const IfcGeom::ConversionResults& entity_shapes, const ifcopenshell::geometry::taxonomy::matrix4& entity_trsf, IfcGeom::ConversionResults& cut_shapes)
				{
					for (auto& k : kernels_) {
						bool is_valid = true;
						for (auto& s : entity_shapes) {
							if (!k->accepts(*s.Shape())) {
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
				virtual AbstractKernel* clone(Logger& logger) const
				{
					std::vector<std::unique_ptr<AbstractKernel>> ks;
					for (auto& k : kernels_) {
						ks.emplace_back(k->clone(logger));
					}
					// @todo ugly
					return new HybridKernel(geometry_library(), file_, const_cast<Settings&>(settings()), std::move(ks), logger);
				}
			};
		}
	}
}

#endif
