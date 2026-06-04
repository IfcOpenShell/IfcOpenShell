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

#ifndef IFCVIEWER_LOG_H
#define IFCVIEWER_LOG_H

// Tiny portable logging shim. Replaces Qt's qInfo()/qWarning()/qDebug()
// stream syntax with a no-Qt equivalent so IfcViewerCore can run under
// Emscripten + so ViewportCore (post-extraction) doesn't link Qt for
// the sake of a few diagnostic prints.
//
// Surface mimics QDebug enough for mass `qInfo()`→`Log::info()` /
// `qWarning()`→`Log::warn()` replacement to compile unchanged:
//
//   - operator<< overloads for the common primitives + char strings
//   - .noquote() / .nospace() as compat no-ops (Qt formatting controls
//     that don't have meaningful equivalents here — Qt added a quoted
//     wrapper around QStrings + a space separator between args; we just
//     never do those)
//   - a temp-destructor newline so call-site syntax stays terse
//
// QString streaming sites have to convert at the boundary (".toUtf8()
// .constData()") because Log.h lives in IfcViewerCore and can't pull in
// Qt. Once the QString → std::string sweep lands the manual conversions
// go away.
//
// Both info() and warn() write to stderr; the only difference is the
// prefix tag. Add a colourised stream sink later if we ever want
// terminal-friendly output.

#include <cstdio>
#include <string>
#include <string_view>

namespace Log {

class Stream {
public:
    Stream() = default;
    ~Stream() { std::fputc('\n', stderr); std::fflush(stderr); }

    // Move-only — copies would double the trailing newline.
    Stream(const Stream&)            = delete;
    Stream& operator=(const Stream&) = delete;
    Stream(Stream&&)                 = default;

    // Qt-style formatting toggles. Both are no-ops here; declared so
    // existing qInfo().noquote().nospace() chains keep parsing.
    Stream& noquote() { return *this; }
    Stream& nospace() { return *this; }
    Stream& quote()   { return *this; }
    Stream& space()   { return *this; }

    Stream& operator<<(const char* s) {
        if (s) std::fputs(s, stderr);
        return *this;
    }
    Stream& operator<<(const std::string& s) {
        std::fwrite(s.data(), 1, s.size(), stderr);
        return *this;
    }
    Stream& operator<<(std::string_view s) {
        std::fwrite(s.data(), 1, s.size(), stderr);
        return *this;
    }
    Stream& operator<<(char c)            { std::fputc(c, stderr); return *this; }
    Stream& operator<<(bool b)            { std::fputs(b ? "true" : "false", stderr); return *this; }
    Stream& operator<<(int x)             { std::fprintf(stderr, "%d", x); return *this; }
    Stream& operator<<(unsigned int x)    { std::fprintf(stderr, "%u", x); return *this; }
    Stream& operator<<(long x)            { std::fprintf(stderr, "%ld", x); return *this; }
    Stream& operator<<(unsigned long x)   { std::fprintf(stderr, "%lu", x); return *this; }
    Stream& operator<<(long long x)       { std::fprintf(stderr, "%lld", x); return *this; }
    Stream& operator<<(unsigned long long x) { std::fprintf(stderr, "%llu", x); return *this; }
    Stream& operator<<(float x)           { std::fprintf(stderr, "%g", double(x)); return *this; }
    Stream& operator<<(double x)          { std::fprintf(stderr, "%g", x); return *this; }
    Stream& operator<<(const void* p)     { std::fprintf(stderr, "%p", p); return *this; }
};

inline Stream info() {
    std::fputs("[info] ", stderr);
    return Stream{};
}
inline Stream warn() {
    std::fputs("[warn] ", stderr);
    return Stream{};
}

} // namespace Log

#endif  // IFCVIEWER_LOG_H
