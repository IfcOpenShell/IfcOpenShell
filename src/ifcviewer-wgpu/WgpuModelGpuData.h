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

#ifndef WGPUMODELGPUDATA_H
#define WGPUMODELGPUDATA_H

#include <webgpu/webgpu.h>

#include <cstddef>
#include <cstdint>
#include <vector>

#include "InstancedGeometry.h"

// Per-model wgpu state. Mirrors the GL backend's ModelGpuData but with
// wgpu handles. Stage 2 only allocates and uploads the four core buffers;
// bind groups, pipelines, BVH and cull scratch land in later stages.
//
// All vertex/index/mesh/instance bytes are uploaded once at load time via
// wgpuQueueWriteBuffer. The vertex storage buffer is read by the vertex
// shader (vertex pulling), not used as a classic vertex buffer — there is
// no input-assembler vertex layout to match.
struct WgpuModelGpuData {
    // Raw VBO bytes at the INSTANCED_VERTEX_STRIDE_BYTES layout (12 B/vertex).
    // Bound as a read-only storage buffer in the vertex shader.
    WGPUBuffer vertex_storage = nullptr;
    // Mesh-local u32 indices. base_vertex applied at draw time so a single
    // index buffer per model is shared across meshes.
    WGPUBuffer index_buffer = nullptr;
    // MeshGpu[] — per-mesh quantization basis (aabb_min/max as vec4 pair).
    // Derived from MeshInfo on upload.
    WGPUBuffer mesh_storage = nullptr;
    // InstanceGpu[] — per-instance transform + ids. Derived from InstanceCpu
    // on upload. Stage 2 stores the cached `transform`; later stages will
    // recompose from placement_transformation when stage matrices change.
    WGPUBuffer instance_storage = nullptr;

    // Bind group binding the three storage buffers above (group=1 in the
    // main pipeline). Built in applyCachedModel after the buffers exist.
    WGPUBindGroup bind_group = nullptr;

    // Size mirrors for stats / range checks.
    size_t   vertex_bytes   = 0;
    uint32_t index_count    = 0;
    uint32_t mesh_count     = 0;
    uint32_t instance_count = 0;

    // CPU side, kept for cull / picking / federation recompose.
    std::vector<MeshInfo>    meshes;
    std::vector<InstanceCpu> instances;

    bool hidden = false;
};

// Release every wgpu handle in `m` and clear its size mirrors. Safe to call
// repeatedly; idempotent on already-released entries.
void releaseWgpuModelGpuData(WgpuModelGpuData& m);

#endif // WGPUMODELGPUDATA_H
