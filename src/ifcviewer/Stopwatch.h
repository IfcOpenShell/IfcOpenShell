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

#ifndef IFCVIEWER_STOPWATCH_H
#define IFCVIEWER_STOPWATCH_H

// Qt-free QElapsedTimer replacement: a thin wrapper over
// std::chrono::steady_clock that exposes the handful of methods our code
// actually uses (start, restart, elapsed-as-ms, nsecsElapsed, isValid).
// Same call-site API as QElapsedTimer so the existing diagnostics keep
// reading the same way after the type swap.

#include <chrono>
#include <cstdint>

class Stopwatch {
public:
    using Clock     = std::chrono::steady_clock;
    using TimePoint = Clock::time_point;

    Stopwatch() = default;

    bool isValid() const { return started_; }
    void start()         { t0_ = Clock::now(); started_ = true; }
    void restart()       { start(); }
    void invalidate()    { started_ = false; }

    // Elapsed milliseconds since start(); matches QElapsedTimer::elapsed().
    int64_t elapsed() const {
        if (!started_) return 0;
        return std::chrono::duration_cast<std::chrono::milliseconds>(
            Clock::now() - t0_).count();
    }
    // Nanoseconds since start; matches QElapsedTimer::nsecsElapsed().
    int64_t nsecsElapsed() const {
        if (!started_) return 0;
        return std::chrono::duration_cast<std::chrono::nanoseconds>(
            Clock::now() - t0_).count();
    }

private:
    TimePoint t0_{};
    bool      started_ = false;
};

#endif  // IFCVIEWER_STOPWATCH_H
