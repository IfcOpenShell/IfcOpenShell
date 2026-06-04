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

// Platform-agnostic render core. Owns the wgpu lifecycle state +
// (eventually) scene state + per-frame render path. Talks to its
// embedder through ViewportHost (window/canvas surface, scheduling,
// notifications) — has no Qt or browser dependencies of its own.
//
// First migration target (#84-a): wgpu instance/adapter/device/queue/
// surface ownership. The next subsystems (pipelines, models, render
// path) move incrementally across subsequent commits — each leaving
// the desktop build green. ViewportWindow currently holds reference
// members pointing back at ViewportCore's storage so its body doesn't
// have to acquire a `core_.` prefix on every wgpu touch. Those
// references shrink as render methods themselves move over.

#include <webgpu/webgpu.h>

#include "ViewportHost.h"

class ViewportCore {
public:
    explicit ViewportCore(ViewportHost* host);
    ~ViewportCore();

    ViewportCore(const ViewportCore&)            = delete;
    ViewportCore& operator=(const ViewportCore&) = delete;

    ViewportHost* host() const { return host_; }

    // Friend access for ViewportWindow's reference proxies. As each
    // render method moves into ViewportCore it stops needing these
    // (it touches the fields directly); once everything has migrated
    // the friend declaration goes away.
    friend class ViewportWindow;

private:
    ViewportHost* host_;

    // ---- wgpu lifecycle state ------------------------------------------------
    //
    // Plain pointers (wgpu C handles); zero-init means "not yet
    // initialised". Owned by ViewportCore now; reference members in
    // ViewportWindow alias these so the existing call sites don't
    // need to change to use a `core_.` prefix.
    WGPUInstance      instance_           = nullptr;
    WGPUAdapter       adapter_            = nullptr;
    WGPUDevice        device_             = nullptr;
    WGPUQueue         queue_              = nullptr;
    WGPUSurface       surface_            = nullptr;
    WGPUTextureFormat surface_format_     = WGPUTextureFormat_Undefined;
    bool              surface_configured_ = false;
};

#endif  // VIEWPORTCORE_H
