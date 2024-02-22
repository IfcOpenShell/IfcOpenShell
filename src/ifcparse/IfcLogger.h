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
#include "IfcBaseClass.h"

#include <boost/optional.hpp>
#include <boost/scope_exit.hpp>
#include <exception>
#include <map>
#include <sstream>
#include <string>

class IFC_PARSE_API Logger {
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
    // template argument of Logger or controlled using preprocessor directives?
    static std::ostream* log1_;
    static std::ostream* log2_;

    static std::wostream* wlog1_;
    static std::wostream* wlog2_;

    static std::stringstream log_stream_;

    static Severity verbosity_;
    static Format format_;
    static boost::optional<const IfcUtil::IfcBaseClass*> current_product_;
    static Severity max_severity_;

    static boost::optional<long long> first_timepoint_;
    static std::map<std::string, double> performance_statistics_;
    static std::map<std::string, double> performance_signal_start_;

    static bool print_perf_stats_on_element_;

  public:
    static void SetProduct(boost::optional<const IfcUtil::IfcBaseClass*> product);

    /// Determines to what stream respectively progress and errors are logged
    static void SetOutput(std::wostream* stream1, std::wostream* stream2);

    /// Determines to what stream respectively progress and errors are logged
    static void SetOutput(std::ostream* stream1, std::ostream* stream2);

    /// Determines the types of log messages to get logged
    static void Verbosity(Severity severity);
    static Severity Verbosity();
    static Severity MaxSeverity();

    /// Determines output format: plain text or sequence of JSON objects
    static void OutputFormat(Format format);
    static Format OutputFormat();

    /// Log a message to the output stream
    static void Message(Severity type, const std::string& message, const IfcUtil::IfcBaseInterface* instance = 0);
    static void Message(Severity type, const std::exception& exception, const IfcUtil::IfcBaseInterface* instance = 0);

    static void Notice(const std::string& message, const IfcUtil::IfcBaseInterface* instance = 0) { Message(LOG_NOTICE, message, instance); }
    static void Warning(const std::string& message, const IfcUtil::IfcBaseInterface* instance = 0) { Message(LOG_WARNING, message, instance); }
    static void Error(const std::string& message, const IfcUtil::IfcBaseInterface* instance = 0) { Message(LOG_ERROR, message, instance); }

    static void Notice(const std::exception& exception, const IfcUtil::IfcBaseInterface* instance = 0) { Message(LOG_NOTICE, exception, instance); }
    static void Warning(const std::exception& exception, const IfcUtil::IfcBaseInterface* instance = 0) { Message(LOG_WARNING, exception, instance); }
    static void Error(const std::exception& exception, const IfcUtil::IfcBaseInterface* instance = 0) { Message(LOG_ERROR, exception, instance); }

    static void Status(const std::string& message, bool new_line = true);

    static void ProgressBar(int progress);
    static std::string GetLog();
    static void PrintPerformanceStats();
    static void PrintPerformanceStatsOnElement(bool b) { print_perf_stats_on_element_ = b; }
};

#define PERF(x)                                                      \
                                                                     \
    Logger::Message(Logger::LOG_PERF, x);                            \
                                                                     \
    BOOST_SCOPE_EXIT(void) {                                         \
        Logger::Message(Logger::LOG_PERF, "done " + std::string(x)); \
    }                                                                \
    BOOST_SCOPE_EXIT_END

#endif
