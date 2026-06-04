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

#ifndef VIEWPORTCORE_H
#define VIEWPORTCORE_H

// Platform-agnostic render core. Owns the wgpu state + scene state +
// per-frame render path. Talks to its embedder through ViewportHost
// (window/canvas surface, scheduling, notifications) — has no Qt or
// browser dependencies of its own.
//
// Empty for now: this header / TU is the placeholder for the
// incremental Path-A refactor (#77-#86). Each subsequent commit moves
// one subsystem out of ViewportWindow.cpp into here and updates the
// public surface accordingly. Until that work lands, ViewportWindow
// retains its render body; this class is just the target for the
// move.

#include "ViewportHost.h"

class ViewportCore {
public:
    explicit ViewportCore(ViewportHost* host);
    ~ViewportCore();

    ViewportCore(const ViewportCore&)            = delete;
    ViewportCore& operator=(const ViewportCore&) = delete;

    ViewportHost* host() const { return host_; }

private:
    ViewportHost* host_;
};

#endif  // VIEWPORTCORE_H
