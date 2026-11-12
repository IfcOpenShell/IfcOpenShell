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


#ifndef GPUMEMORY_H
#define GPUMEMORY_H

#include <cstdint>

// How much video memory the card has, and how much of it is in use.
//
// WebGPU deliberately exposes neither -- `maxBufferSize` reports 1 TB on this
// stack and is useless as a proxy -- so this goes outside the graphics API.
// That is legitimate on desktop, where the viewer is a native app, and it is
// the number every other part of the residency story needs: a gauge to show
// the user, a budget to keep the pool under, and a pre-flight check that can
// refuse a model before it wedges the session.
//
// Matching the right GPU matters. On a laptop with switchable graphics the
// obvious sysfs entry is often the *integrated* chip rather than the one wgpu
// selected -- measured here: /sys/class/drm/card1 reports a 512 MB AMD iGPU
// while wgpu is running on a 4 GB GeForce. So the query takes the vendor and
// device ids from WGPUAdapterInfo and matches on them.
namespace ifcviewer {

struct GpuMemoryInfo {
    std::uint64_t total_bytes = 0;
    std::uint64_t used_bytes  = 0;
    // False when no backend could answer -- an unknown driver, a platform
    // without a query, or a device the probe could not match. Callers must
    // treat that as "unknown" and not as "zero": refusing to load because an
    // unavailable query returned 0 would be worse than not asking.
    bool          valid       = false;

    std::uint64_t free_bytes() const {
        return total_bytes > used_bytes ? total_bytes - used_bytes : 0;
    }
};

// Query the GPU wgpu selected. `vendor_id` / `device_id` come from
// wgpuAdapterGetInfo. Cheap enough to call once a second; not per frame.
GpuMemoryInfo queryGpuMemory(std::uint32_t vendor_id, std::uint32_t device_id);

}  // namespace ifcviewer

#endif
