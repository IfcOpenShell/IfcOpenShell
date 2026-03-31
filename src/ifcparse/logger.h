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

#ifndef IFCLOGGER_H
#define IFCLOGGER_H

#include "ifc_parse_api.h"
#include "express.h"

#include <boost/optional.hpp>
#include <boost/scope_exit.hpp>
#include <exception>
#include <map>
#include <sstream>
#include <string>

class IFC_PARSE_API logger {
  public:
    typedef enum {
        LOG_PERF,
        LOG_DEBUG,
        LOG_NOTICE,
        LOG_WARNING,
        LOG_ERROR
    } Severity;
    typedef enum {
        FMT_PLAIN,
        FMT_JSON
    } Format;

  private:
    // To both stream variants need to exist at runtime or should this be a
    // template argument of logger or controlled using preprocessor directives?
    static std::ostream* log1_;
    static std::ostream* log2_;

    static std::wostream* wlog1_;
    static std::wostream* wlog2_;

    static std::stringstream log_stream_;

    static Severity verbosity_;
    static Format format_;
    static Severity max_severity_;

    static std::optional<long long> first_timepoint_;
    static std::map<std::string, double> performance_statistics_;
    static std::map<std::string, double> performance_signal_start_;

    static bool print_perf_stats_on_element_;

  public:
    static void set_product(std::optional<const express::Base> product);

    /// Determines to what stream respectively progress and errors are logged
    static void set_output(std::wostream* progress_stream, std::wostream* error_stream);

    /// Determines to what stream respectively progress and errors are logged
    static void set_output(std::ostream* progress_stream, std::ostream* error_stream);

    /// Determines the types of log messages to get logged
    static void verbosity(Severity severity);
    static Severity verbosity();
    static Severity max_severity();

    /// Determines output format: plain text or sequence of JSON objects
    static void output_format(Format format);
    static Format output_format();

    /// Log a message to the output stream
    static void message(Severity severity, const std::string& text, const express::Base& instance = express::Base());
    static void message(Severity severity, const std::exception& exception, const express::Base& instance = express::Base());

    static void notice(const std::string& text, const express::Base& instance = express::Base()) { logger::message(LOG_NOTICE, text, instance); }
    static void warning(const std::string& text, const express::Base& instance = express::Base()) { logger::message(LOG_WARNING, text, instance); }
    static void error(const std::string& text, const express::Base& instance = express::Base()) { logger::message(LOG_ERROR, text, instance); }

    static void notice(const std::exception& exception, const express::Base& instance = express::Base()) { message(LOG_NOTICE, exception, instance); }
    static void warning(const std::exception& exception, const express::Base& instance = express::Base()) { message(LOG_WARNING, exception, instance); }
    static void error(const std::exception& exception, const express::Base& instance = express::Base()) { message(LOG_ERROR, exception, instance); }

    static void status(const std::string& message, bool append_newline = true);

    static void progress_bar(int progress_percent);
    static std::string get_log();
    static void print_performance_stats();
    static void print_performance_stats_on_element(bool enabled) { print_perf_stats_on_element_ = enabled; }
};

#define PERF(x)                                                      \
                                                                     \
    logger::message(logger::LOG_PERF, x);                            \
                                                                     \
    BOOST_SCOPE_EXIT(void) {                                         \
        logger::message(logger::LOG_PERF, "done " + std::string(x)); \
    }                                                                \
    BOOST_SCOPE_EXIT_END

#endif
