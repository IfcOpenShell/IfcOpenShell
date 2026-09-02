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
#include "../ifcgeom/kernels/opencascade/boolean_utils.h"
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
	// Whether an attempt's own (temporary, in-memory) logger carries a signal that its
	// result should be distrusted, e.g. has_coincident_edges() (see boolean_utils.cpp).
	inline bool logger_flags_suspicious_result(const Logger& logger) {
#ifdef IFOPSH_WITH_OPENCASCADE
		if (IfcGeom::util::has_coincident_faces_warning(logger)) {
			return true;
		}
#endif
		return false;
	}

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
				// Each kernels_[i] is bound to its own dedicated, in-memory attempt_loggers_[i]
				// so a chain attempt's log messages can be inspected then discarded or
				// folded into logger_, without disturbing the other kernels' persisted state.
				std::vector<std::unique_ptr<Logger>> attempt_loggers_;
				ifcopenshell::geometry::abstract_mapping* mapping_;
				IfcParse::IfcFile* file_;

				void bind_attempt_loggers() {
					attempt_loggers_.clear();
					attempt_loggers_.reserve(kernels_.size());
					for (auto& k : kernels_) {
						attempt_loggers_.emplace_back(std::make_unique<Logger>());
						auto& al = *attempt_loggers_.back();
						al.OutputFormat(Logger::FMT_INMEMORY);
						// Capture at least at NOTICE, regardless of logger_'s (e.g. CLI-configured)
						// verbosity, so detection doesn't depend on the user's chosen verbosity;
						// Append() re-applies logger_'s real verbosity when replaying.
						al.Verbosity((std::min)(Logger::LOG_NOTICE, logger_.Verbosity()));
						k.reset(k->clone(al));
					}
				}
			public:
				HybridKernel(const std::string& name, IfcParse::IfcFile* file, Settings& settings, std::vector<std::unique_ptr<AbstractKernel>>&& kernels, Logger& logger = Logger::Root())
					: AbstractKernel(name, settings, logger)
					, kernels_(std::move(kernels))
					, mapping_(ifcopenshell::geometry::impl::mapping_implementations().construct(file, settings, logger))
					, file_(file)
				{
					bind_attempt_loggers();
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

					IfcGeom::ConversionResults best;
					bool have_best = false;
					size_t best_index = 0;

					for (size_t i = 0; i < kernels_.size(); ++i) {
						auto& k = kernels_[i];
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
						auto& attempt_logger = *attempt_loggers_[i];
						attempt_logger.ClearLog();

						IfcGeom::ConversionResults candidate;
						bool success = false;
						try {
							success = k->convert(item, candidate);
						} catch (...) {}
						if (!success) {
							continue;
						}
						if (!logger_flags_suspicious_result(attempt_logger)) {
							logger_.Append(attempt_logger);
							rs.insert(rs.end(), candidate.begin(), candidate.end());
							return true;
						}
						// A kernel further down the chain gets a chance to clear this up;
						// keep the first suspicious success (and its log) in case none do.
						if (!have_best) {
							best = std::move(candidate);
							best_index = i;
							have_best = true;
						}
					}

					if (have_best) {
						logger_.Warning("SYS", 36, "Hybrid kernel chain has no non-suspicious result, using the first suspicious one", item->instance);
						logger_.Append(*attempt_loggers_[best_index]);
						rs.insert(rs.end(), best.begin(), best.end());
						return true;
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
					// @todo entity_shapes already commits to one kernel's native shape type,
					// so is_valid_for_kernel() below usually leaves only one candidate.
					IfcGeom::ConversionResults best;
					bool have_best = false;
					size_t best_index = 0;

					for (size_t i = 0; i < kernels_.size(); ++i) {
						auto& k = kernels_[i];
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

						auto& attempt_logger = *attempt_loggers_[i];
						attempt_logger.ClearLog();

						IfcGeom::ConversionResults candidate;
						bool success = false;
						try {
							success = k->convert_openings(entity, openings, entity_shapes, entity_trsf, candidate);
						} catch (...) {}
						if (!success) {
							continue;
						}
						if (!logger_flags_suspicious_result(attempt_logger)) {
							logger_.Append(attempt_logger);
							cut_shapes.insert(cut_shapes.end(), candidate.begin(), candidate.end());
							return true;
						}
						if (!have_best) {
							best = std::move(candidate);
							best_index = i;
							have_best = true;
						}
					}

					if (have_best) {
						logger_.Warning("SYS", 36, "Hybrid kernel chain has no non-suspicious opening cut, using the first suspicious one", entity);
						logger_.Append(*attempt_loggers_[best_index]);
						cut_shapes.insert(cut_shapes.end(), best.begin(), best.end());
						return true;
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

			inline std::unique_ptr<AbstractKernel> construct(IfcParse::IfcFile* file, const std::string& geometry_library, Settings& conv_settings, Logger& logger = Logger::Root()) {
				std::string geometry_library_lower = boost::to_lower_copy(geometry_library);

#ifdef IFOPSH_WITH_OPENCASCADE
				if (geometry_library_lower == "opencascade") {
					return std::make_unique<IfcGeom::OpenCascadeKernel>(conv_settings, logger);
				}
#endif

#ifdef IFOPSH_WITH_CGAL
				if (geometry_library_lower == "cgal") {
					return std::make_unique<CgalKernel>(conv_settings, logger);
				}

				if (geometry_library_lower == "cgal-simple") {
					return std::make_unique<SimpleCgalKernel>(conv_settings, logger);
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
							kernels.emplace_back(new IfcGeom::OpenCascadeKernel(conv_settings, logger));
							geometry_library_lower = geometry_library_lower.substr(strlen("opencascade"));
						}
#endif

#ifdef IFOPSH_WITH_CGAL
						if (geometry_library_lower.find("cgal-simple", 0) == 0) {
							kernels.emplace_back(new SimpleCgalKernel(conv_settings, logger));
							geometry_library_lower = geometry_library_lower.substr(strlen("cgal-simple"));
						}

						if (geometry_library_lower.find("cgal", 0) == 0) {
							kernels.emplace_back(new CgalKernel(conv_settings, logger));
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
						return std::make_unique<HybridKernel>(geometry_library, file, conv_settings, std::move(kernels), logger);
					}
				}

				throw IfcParse::IfcException("No geometry kernel registered for " + geometry_library);
			}

		}
	}
}

#endif
