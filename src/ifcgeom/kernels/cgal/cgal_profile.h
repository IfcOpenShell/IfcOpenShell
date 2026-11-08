// Generated with the assistance of an AI coding tool.
// SPDX-License-Identifier: LGPL-3.0-or-later
#pragma once

#ifdef IFOPSH_CGAL_ENABLE_PROFILING

#include "../../../ifcparse/logger.h"

#include <chrono>

namespace ifcopenshell::geom {
// Direct elapsed times avoid the logger's shared label-based start/stop state
// when several products are converted concurrently. Nested scopes are inclusive.
class cgal_profile_scope {
    ifcopenshell::logger& logger_;
    std::string label_;
    express::base instance_;
    std::chrono::steady_clock::time_point started_;
    bool enabled_;

  public:
    cgal_profile_scope(ifcopenshell::logger& logger, std::string label, express::base instance = {})
        : logger_(logger), label_(std::move(label)), instance_(instance), started_(std::chrono::steady_clock::now()), enabled_(logger.verbosity() <= ifcopenshell::logger::LOG_DEBUG) {}
    ~cgal_profile_scope() {
        if (enabled_) {
            double seconds = std::chrono::duration<double>(std::chrono::steady_clock::now() - started_).count();
            logger_.message(ifcopenshell::logger::LOG_DEBUG, "CGP", 1, "CGAL " + label_ + ": " + std::to_string(seconds), instance_);
        }
    }
    cgal_profile_scope(const cgal_profile_scope&) = delete;
    cgal_profile_scope& operator=(const cgal_profile_scope&) = delete;
};
} // namespace ifcopenshell::geom

#define IFOPSH_CGAL_PROFILE_SCOPE(name, ...) \
    ::ifcopenshell::geom::cgal_profile_scope name(__VA_ARGS__)

#else

#define IFOPSH_CGAL_PROFILE_SCOPE(name, ...) ((void)0)

#endif // IFOPSH_CGAL_ENABLE_PROFILING
