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
#include <cstdint>
#include <exception>
#include <map>
#include <mutex>
#include <sstream>
#include <string>
#include <vector>

class IFC_PARSE_API log_message {
  public:
    char code[7];
    int severity;
    std::string timestamp, message, instance, product;

    log_message(
        int severity,
        const char (&code_prefix)[4],
        uint16_t code_number,
        const std::string& timestamp,
        const std::string& message,
        const IfcUtil::IfcBaseInterface* inst = 0,
        const IfcUtil::IfcBaseClass* current_product = 0);
};

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
        FMT_JSON,
        FMT_INMEMORY
    } Format;

  private:
    std::vector<log_message> log_messages_;

    // To both stream variants need to exist at runtime or should this be a
    // template argument of Logger or controlled using preprocessor directives?
    std::ostream* log1_ = nullptr;
    std::ostream* log2_ = nullptr;

    std::wostream* wlog1_ = nullptr;
    std::wostream* wlog2_ = nullptr;

    std::stringstream log_stream_;
    const IfcUtil::IfcBaseClass* current_product_ = nullptr;

    Severity verbosity_ = LOG_NOTICE;
    Format format_ = FMT_PLAIN;
    Severity max_severity_ = LOG_NOTICE;

    boost::optional<long long> first_timepoint_;
    std::map<std::string, double> performance_statistics_;
    std::map<std::string, double> performance_signal_start_;

    bool print_perf_stats_on_element_ = false;
    std::mutex mutex_;

    const IfcUtil::IfcBaseClass* current_product() const;
    void current_product(const IfcUtil::IfcBaseClass* product);

  public:
    Logger() = default;
    Logger(const Logger&) = delete;
    Logger& operator=(const Logger&) = delete;

    static Logger& Root();

    void SetProduct(boost::optional<const IfcUtil::IfcBaseClass*> product);

    /// Determines to what stream respectively progress and errors are logged
    void SetOutput(std::wostream* stream1, std::wostream* stream2);

    /// Determines to what stream respectively progress and errors are logged
    void SetOutput(std::ostream* stream1, std::ostream* stream2);

    /// Determines the types of log messages to get logged
    void Verbosity(Severity severity);
    Severity Verbosity() const;
    Severity MaxSeverity() const;

    /// Determines output format: plain text or sequence of JSON objects
    void OutputFormat(Format format);
    Format OutputFormat() const;

    /// Log a message to the output stream
    void Message(Severity type, const char (&code_prefix)[4], uint16_t code_number, const std::string& message, const IfcUtil::IfcBaseInterface* instance = 0);
    void Message(Severity type, const char (&code_prefix)[4], uint16_t code_number, const std::exception& exception, const IfcUtil::IfcBaseInterface* instance = 0);

    void Notice(const char (&code_prefix)[4], uint16_t code_number, const std::string& message, const IfcUtil::IfcBaseInterface* instance = 0) { Message(LOG_NOTICE, code_prefix, code_number, message, instance); }
    void Warning(const char (&code_prefix)[4], uint16_t code_number, const std::string& message, const IfcUtil::IfcBaseInterface* instance = 0) { Message(LOG_WARNING, code_prefix, code_number, message, instance); }
    void Error(const char (&code_prefix)[4], uint16_t code_number, const std::string& message, const IfcUtil::IfcBaseInterface* instance = 0) { Message(LOG_ERROR, code_prefix, code_number, message, instance); }

    void Notice(const char (&code_prefix)[4], uint16_t code_number, const std::exception& exception, const IfcUtil::IfcBaseInterface* instance = 0) { Message(LOG_NOTICE, code_prefix, code_number, exception, instance); }
    void Warning(const char (&code_prefix)[4], uint16_t code_number, const std::exception& exception, const IfcUtil::IfcBaseInterface* instance = 0) { Message(LOG_WARNING, code_prefix, code_number, exception, instance); }
    void Error(const char (&code_prefix)[4], uint16_t code_number, const std::exception& exception, const IfcUtil::IfcBaseInterface* instance = 0) { Message(LOG_ERROR, code_prefix, code_number, exception, instance); }

    void Status(const std::string& message, bool new_line = true);

    void ProgressBar(int progress);
    std::string GetLog();
    void ClearLog();
    void Append(Logger& logger);
    void PrintPerformanceStats();
    void PrintPerformanceStatsOnElement(bool b) { print_perf_stats_on_element_ = b; }
    bool PrintPerformanceStatsOnElement() const { return print_perf_stats_on_element_; }

    const std::vector<log_message>& log_messages() const { return log_messages_; }
};

// SWIG couldn't represent `Logger::Root()` default value using Python,
// so when translating signature it represents it just as `fn(*args)`, losing information about args.
// Using `Logger * = nullptr` instead of `&Logger = Logger::Root` helps,
// since `nullptr` is convertable Python's `None`.
// `logger_or_root` is just covering the boilerplate for this pattern.
inline Logger& logger_or_root(Logger* logger) { return logger ? *logger : Logger::Root(); }

#define PERF(x)                                                      \
                                                                     \
    Logger::Root().Message(Logger::LOG_PERF, "SYS", 1, x);            \
                                                                     \
    BOOST_SCOPE_EXIT(void) {                                         \
        Logger::Root().Message(Logger::LOG_PERF, "SYS", 2, "done " + std::string(x)); \
    }                                                                \
    BOOST_SCOPE_EXIT_END

#endif
