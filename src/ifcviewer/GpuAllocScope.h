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

#ifndef IFCVIEWER_GPUALLOCSCOPE_H
#define IFCVIEWER_GPUALLOCSCOPE_H

#include <webgpu/webgpu.h>

#include <functional>

// Brackets one or more wgpu resource creations so an out-of-memory is
// observed instead of silently producing an invalid resource.
//
// WebGPU never returns null from createBuffer / createTexture: a failed
// allocation yields an *error* resource, and the failure is only reported
// through an error scope. Left unobserved it surfaces later as a validation
// error on the first use -- and on wgpu-native an invalid attachment in
// wgpuQueueSubmit is a Rust panic across the FFI boundary, i.e. an abort
// with no recovery path. So every allocation the renderer cannot do
// without goes through one of these.
//
// Two filters are pushed, not one: wgpu-native classifies "Not enough
// memory left" as a Validation error, Dawn as OutOfMemory.
//
// Desktop and web differ only in *when* the answer arrives. On wgpu-native
// the scope pops synchronously (the instance is spun until the callback
// fires) and `end` invokes the callback before returning. On Dawn-web the
// pop is a promise and spinning would deadlock the JS event loop, so the
// callback fires later from the event loop; callers use the resource
// provisionally and correct course in the callback if it turns out bad.
class GpuAllocScope {
public:
    using Callback = std::function<void(bool ok)>;

    GpuAllocScope(WGPUInstance instance, WGPUDevice device);
    ~GpuAllocScope();

    GpuAllocScope(const GpuAllocScope&)            = delete;
    GpuAllocScope& operator=(const GpuAllocScope&) = delete;

    // Pop the scopes and deliver the verdict: `ok` is true when no error
    // fired between construction and here. Must be called exactly once.
    void end(Callback on_result);

private:
    WGPUInstance instance_ = nullptr;
    WGPUDevice   device_   = nullptr;
    bool         ended_    = false;
};

#endif  // IFCVIEWER_GPUALLOCSCOPE_H
