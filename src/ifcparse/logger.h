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

#include <cstddef>
#include <cstdint>
#include <exception>
#include <map>
#include <mutex>
#include <optional>
#include <sstream>
#include <string>
#include <vector>

namespace ifcopenshell {

class IFC_PARSE_API log_message {
  public:
    char code[7];
    int severity;
    std::string timestamp, message, instance, product;

    log_message(
        int severity,
        const std::string& code,
        const std::string& timestamp,
        const std::string& message,
        const express::base& instance = express::base(),
        const express::base& current_product = express::base());
};

class IFC_PARSE_API logger {
  public:
    typedef enum {
        LOG_PERF,
        LOG_DEBUG,
        LOG_NOTICE,
        LOG_WARNING,
        LOG_ERROR
    } severity;

    typedef enum {
        FMT_PLAIN,
        FMT_JSON,
        FMT_INMEMORY
    } format;

  private:
    std::vector<log_message> log_messages_;

    std::ostream* log1_ = nullptr;
    std::ostream* log2_ = nullptr;

    std::wostream* wlog1_ = nullptr;
    std::wostream* wlog2_ = nullptr;

    std::stringstream log_stream_;
    express::base current_product_;

    severity verbosity_ = LOG_NOTICE;
    format format_ = FMT_PLAIN;
    severity max_severity_ = LOG_NOTICE;

    std::optional<long long> first_timepoint_;
    std::map<std::string, double> performance_statistics_;
    std::map<std::string, double> performance_signal_start_;

    bool print_perf_stats_on_element_ = false;
    std::mutex mutex_;

    const express::base& current_product() const;
    void current_product(const express::base& product);
    void message(severity type, const std::string& code, const std::string& message, const express::base& instance);

  public:
    logger() = default;
    logger(const logger&) = delete;
    logger& operator=(const logger&) = delete;

    static logger& root();

    void set_product(std::optional<express::base> product);
    void set_product(const express::base& product) { set_product(std::optional<express::base>(product)); }

    void set_output(std::wostream* stream1, std::wostream* stream2);
    void set_output(std::ostream* stream1, std::ostream* stream2);

    void verbosity(severity severity);
    severity verbosity() const;
    severity max_severity() const;

    void output_format(format format);
    format output_format() const;

    void message(severity type, const std::string& message, const express::base& instance = express::base());
    void message(severity type, const std::exception& exception, const express::base& instance = express::base());
    void message(severity type, const char (&code_prefix)[4], uint16_t code_number, const std::string& message, const express::base& instance = express::base());
    void message(severity type, const char (&code_prefix)[4], uint16_t code_number, const std::exception& exception, const express::base& instance = express::base());

    void notice(const std::string& message, const express::base& instance = express::base()) { this->message(LOG_NOTICE, message, instance); }
    void warning(const std::string& message, const express::base& instance = express::base()) { this->message(LOG_WARNING, message, instance); }
    void error(const std::string& message, const express::base& instance = express::base()) { this->message(LOG_ERROR, message, instance); }

    void notice(const std::exception& exception, const express::base& instance = express::base()) { message(LOG_NOTICE, exception, instance); }
    void warning(const std::exception& exception, const express::base& instance = express::base()) { message(LOG_WARNING, exception, instance); }
    void error(const std::exception& exception, const express::base& instance = express::base()) { message(LOG_ERROR, exception, instance); }

    void notice(const char (&code_prefix)[4], uint16_t code_number, const std::string& message, const express::base& instance = express::base()) { this->message(LOG_NOTICE, code_prefix, code_number, message, instance); }
    void warning(const char (&code_prefix)[4], uint16_t code_number, const std::string& message, const express::base& instance = express::base()) { this->message(LOG_WARNING, code_prefix, code_number, message, instance); }
    void error(const char (&code_prefix)[4], uint16_t code_number, const std::string& message, const express::base& instance = express::base()) { this->message(LOG_ERROR, code_prefix, code_number, message, instance); }

    void notice(const char (&code_prefix)[4], uint16_t code_number, const std::exception& exception, const express::base& instance = express::base()) { message(LOG_NOTICE, code_prefix, code_number, exception, instance); }
    void warning(const char (&code_prefix)[4], uint16_t code_number, const std::exception& exception, const express::base& instance = express::base()) { message(LOG_WARNING, code_prefix, code_number, exception, instance); }
    void error(const char (&code_prefix)[4], uint16_t code_number, const std::exception& exception, const express::base& instance = express::base()) { message(LOG_ERROR, code_prefix, code_number, exception, instance); }

    void status(const std::string& message, bool new_line = true);

    void progress_bar(int progress);
    std::string get_log();
    std::size_t count(const std::string& code);
    void clear();
    void append(logger& other);
    void print_performance_stats();
    void print_performance_stats_on_element(bool enabled) { print_perf_stats_on_element_ = enabled; }
    bool print_performance_stats_on_element() const { return print_perf_stats_on_element_; }

    const std::vector<log_message>& log_messages() const { return log_messages_; }
};

// SWIG couldn't represent `logger::root()` default value using Python,
// so when translating signature it represents it just as `fn(*args)`, losing information about args.
// Using `logger* = nullptr` instead of `logger& = logger::root()` helps,
// since `nullptr` is convertable Python's `None`.
// `logger_or_root` is just covering the boilerplate for this pattern.
inline logger& logger_or_root(logger* logger) { return logger ? *logger : logger::root(); }

namespace detail {
class performance_scope {
    std::string label_;

  public:
    explicit performance_scope(const std::string& label) : label_(label) {
        logger::root().message(logger::LOG_PERF, label_);
    }

    ~performance_scope() {
        logger::root().message(logger::LOG_PERF, "done " + label_);
    }

    performance_scope(const performance_scope&) = delete;
    performance_scope& operator=(const performance_scope&) = delete;
};
} // namespace detail

} // namespace ifcopenshell

#define IFCOPENSHELL_PERF_NAME_IMPL(line) ifcopenshell_performance_scope_##line
#define IFCOPENSHELL_PERF_NAME(line) IFCOPENSHELL_PERF_NAME_IMPL(line)
#define PERF(x) ::ifcopenshell::detail::performance_scope IFCOPENSHELL_PERF_NAME(__LINE__)(x)

#endif
