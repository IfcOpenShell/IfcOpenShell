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

#ifndef IFCVIEWER_FRAMESTATS_H
#define IFCVIEWER_FRAMESTATS_H

#include <cstdint>

// Per-frame statistics emitted from render() so the embedder can
// surface them (bonsai's status bar, the web-side dev console, the
// benchmark accumulator). Pure POD so it travels through ViewportHost
// without dragging Qt along. ViewportWindow::FrameStats re-exports
// this so existing bonsai callers still see the familiar
// ViewportWindow::FrameStats type.
struct FrameStats {
    float    fps;
    float    frame_time_ms;
    std::uint32_t total_objects;
    std::uint32_t visible_objects;
    std::uint32_t total_triangles;
    std::uint32_t visible_triangles;
    std::uint32_t unique_meshes;
    std::uint32_t gl_draw_calls;        // wgpu draw-call count; name kept for bonsai parity
    std::uint32_t indirect_sub_draws;   // sub-draws packed into the chunk-indirect lists
    // Chunk geometry pool occupancy (see BufferPool). wgpu exposes no
    // adapter-wide VRAM query, so this is the viewer's own allocation,
    // not the device total.
    std::uint64_t vram_used_bytes;
    std::uint64_t vram_capacity_bytes;
    // Whole-device VRAM from the driver (NVML / sysfs, see GpuMemory.h).
    // Desktop only; zero on web or when no backend could answer, so
    // consumers must treat 0 as "unknown" rather than as empty.
    std::uint64_t device_vram_used_bytes;
    std::uint64_t device_vram_total_bytes;
};

#endif  // IFCVIEWER_FRAMESTATS_H
