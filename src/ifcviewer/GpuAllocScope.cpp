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

#include "GpuAllocScope.h"

#include <cassert>

namespace {

// Shared between the two pop callbacks; freed by whichever fires last.
struct PendingPop {
    GpuAllocScope::Callback on_result;
    int   remaining = 2;
    bool  error     = false;
    // Desktop: points at a flag on end()'s stack frame so the spin-wait
    // can observe completion without touching this (freed) object.
    bool* done      = nullptr;
};

void onPopped(WGPUPopErrorScopeStatus, WGPUErrorType type, WGPUStringView,
              void* userdata1, void* /*userdata2*/) {
    auto* pending = static_cast<PendingPop*>(userdata1);
    if (type != WGPUErrorType_NoError) pending->error = true;
    if (--pending->remaining > 0) return;
    const bool ok   = !pending->error;
    bool*      done = pending->done;
    GpuAllocScope::Callback on_result = std::move(pending->on_result);
    delete pending;
    on_result(ok);
    if (done) *done = true;
}

}  // namespace

GpuAllocScope::GpuAllocScope(WGPUInstance instance, WGPUDevice device)
    : instance_(instance), device_(device) {
    // Validation outer, OutOfMemory inner: each pop sees the errors of
    // its own filter, and an OOM reported under either classification
    // reaches one of the two.
    wgpuDevicePushErrorScope(device_, WGPUErrorFilter_Validation);
    wgpuDevicePushErrorScope(device_, WGPUErrorFilter_OutOfMemory);
}

GpuAllocScope::~GpuAllocScope() {
    assert(ended_ && "GpuAllocScope::end() must be called exactly once");
}

void GpuAllocScope::end(Callback on_result) {
    assert(!ended_);
    ended_ = true;

    bool  done    = false;
    auto* pending = new PendingPop{std::move(on_result)};

    WGPUPopErrorScopeCallbackInfo cb = {};
#if defined(__EMSCRIPTEN__)
    // Dawn-web resolves pops from the JS event loop; the caller proceeds
    // provisionally and hears back in on_result.
    cb.mode = WGPUCallbackMode_AllowSpontaneous;
#else
    // wgpu-native fires these from wgpuInstanceProcessEvents, which we
    // spin below so on_result has run by the time end() returns.
    cb.mode       = WGPUCallbackMode_AllowProcessEvents;
    pending->done = &done;
#endif
    cb.callback  = onPopped;
    cb.userdata1 = pending;
    wgpuDevicePopErrorScope(device_, cb);   // OutOfMemory (inner)
    wgpuDevicePopErrorScope(device_, cb);   // Validation (outer)

#if !defined(__EMSCRIPTEN__)
    while (!done) wgpuInstanceProcessEvents(instance_);
#else
    (void)done;
#endif
}
