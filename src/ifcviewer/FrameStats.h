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
    // Chunk geometry pool occupancy (see BufferPool): bytes held by
    // resident chunks, the pool's current capacity, and the budget the
    // pool may grow to (GpuBudget; 0 when still unbounded).
    std::uint64_t vram_used_bytes;
    std::uint64_t vram_capacity_bytes;
    std::uint64_t vram_budget_bytes;
    // The camera's working set: chunks the streaming driver wants resident
    // (in frustum and large enough on screen) and how many of those are
    // not — i.e. geometry the user should be seeing but is not yet, or
    // cannot be because it does not fit the cache. Transiently non-zero
    // after any camera move; persistently non-zero means the scene does
    // not fit in VRAM.
    std::uint32_t chunks_wanted;
    std::uint32_t chunks_wanted_missing;
    std::uint64_t wanted_missing_bytes;   // raw vertex + index bytes of the missing chunks
    // Whole-device VRAM from the driver (NVML / sysfs, see GpuMemory.h).
    // Desktop only; zero on web or when no backend could answer, so
    // consumers must treat 0 as "unknown" rather than as empty.
    std::uint64_t device_vram_used_bytes;
    std::uint64_t device_vram_total_bytes;
};

#endif  // IFCVIEWER_FRAMESTATS_H
