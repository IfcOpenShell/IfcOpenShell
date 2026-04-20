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

#ifndef INSTANCEDGEOMETRY_H
#define INSTANCEDGEOMETRY_H

#include <cstdint>
#include <string>
#include <vector>

// Per-vertex layout for instanced meshes, stored in local coordinates,
// quantized against each mesh's local AABB.  12 bytes per vertex:
//   offset 0   pos     3 x uint16   normalized -> [0,1]; dequant to
//                                   mix(mesh.aabb_min, mesh.aabb_max, t)
//   offset 6   normal  2 x int8     normalized -> [-1,1]; octahedral-decoded
//   offset 8   color   4 x uint8    normalized -> [0,1]
//
// int8 normals give ~1.4° worst-case angular error — invisible for BIM
// geometry which is overwhelmingly axis-aligned (walls, floors, slabs).
//
// Quantization basis is per mesh, stored in the MeshGpu SSBO bound at
// binding=2.  The vertex shader looks up its basis via the instance's mesh_id.
static constexpr int INSTANCED_VERTEX_STRIDE_BYTES = 12;

// Streamer-side intermediate format: 7 floats per vertex (pos3 + normal3 +
// color-as-float).  GeometryStreamer writes this into MeshChunk.vertices;
// ViewportWindow::uploadMeshChunk quantizes it down to STRIDE_BYTES on the
// way to the VBO.  Not the GPU layout — purely a transfer convention.
static constexpr int INSTANCED_VERTEX_STRIDE_FLOATS = 7;

static constexpr int INSTANCED_VERTEX_POS_OFFSET    = 0;
static constexpr int INSTANCED_VERTEX_NORMAL_OFFSET = 6;
static constexpr int INSTANCED_VERTEX_COLOR_OFFSET  = 8;

// Per-mesh quantization basis, uploaded to a std430 SSBO.  Two vec4s so
// std430 layout is trivial (no alignment surprises).  w components unused.
struct alignas(16) MeshGpu {
    float aabb_min[4];  // xyz = local AABB min; w = 0
    float aabb_max[4];  // xyz = local AABB max; w = 0
};
static_assert(sizeof(MeshGpu) == 32, "MeshGpu must be 32 bytes");

// Per-mesh metadata on the CPU side.  Meshes own a slice of the model's
// VBO (shared across LODs) and one or more slices of the EBO, one per LOD.
//
// LOD0 is the original, full-resolution tessellation — the fields
// `ebo_byte_offset` / `index_count` describe it.
//
// LOD1 is an optional decimated copy of the same triangles referencing the
// same vertex buffer.  Built at sidecar time via meshoptimizer for meshes
// whose triangle count crosses a threshold.  `lod1_index_count == 0`
// means no LOD1 was built; the renderer must use LOD0 at every distance.
struct MeshInfo {
    uint32_t vbo_byte_offset = 0;    // where this mesh's vertices start
    uint32_t vertex_count    = 0;
    uint32_t ebo_byte_offset = 0;    // LOD0 indices
    uint32_t index_count     = 0;    // LOD0 index count
    float    local_aabb_min[3]{};
    float    local_aabb_max[3]{};
    uint32_t first_instance  = 0;    // index into per-model instances array
    uint32_t instance_count  = 0;
    uint32_t lod1_ebo_byte_offset = 0;
    uint32_t lod1_index_count     = 0;   // 0 = no LOD1 available
};
static_assert(sizeof(MeshInfo) == 56, "MeshInfo must be 56 bytes");

// Per-instance record uploaded to an SSBO and read by the vertex shader.
// Layout deliberately matches std430 expectations:
//   mat4 transform (64 B column-major)
//   uint object_id
//   uint color_override_rgba8   -- 0 = use baked vertex color, else override
//   uint mesh_id                -- index into per-model MeshGpu[]
//   uint _pad1                  -- align to 16 for std430
struct alignas(16) InstanceGpu {
    float    transform[16];
    uint32_t object_id            = 0;
    uint32_t color_override_rgba8 = 0;
    uint32_t mesh_id              = 0;   // index into per-model MeshGpu[]
    uint32_t _pad1                = 0;
};
static_assert(sizeof(InstanceGpu) == 80, "InstanceGpu must be 80 bytes");

// CPU-side per-instance data.  The GPU record above is derived from this;
// we also retain the world AABB for BVH construction and the mesh_id.
struct InstanceCpu {
    uint32_t mesh_id              = 0;  // index into meshes array
    uint32_t object_id            = 0;
    uint32_t color_override_rgba8 = 0;
    uint32_t model_id             = 0;
    float    transform[16]{};
    float    world_aabb_min[3]{};
    float    world_aabb_max[3]{};
};

// Chunks emitted by the streamer to the viewport (main thread).

// Emitted the first time a representation id is seen.  Carries the mesh
// geometry in local coords.  `local_mesh_id` is the streamer-assigned id
// within this model.
struct MeshChunk {
    uint32_t model_id      = 0;
    uint32_t local_mesh_id = 0;
    std::vector<float>    vertices;  // 7 floats * N_verts (pos3+norm3+color1_packed)
    std::vector<uint32_t> indices;
    float    local_aabb_min[3]{};
    float    local_aabb_max[3]{};
};

// Emitted for every placement (every triangulation element from the
// iterator).  For the first instance of a mesh, the MeshChunk is emitted
// just before this.
struct InstanceChunk {
    uint32_t model_id             = 0;
    uint32_t local_mesh_id        = 0;
    uint32_t object_id            = 0;
    uint32_t color_override_rgba8 = 0;
    float    transform[16]{};
    float    world_aabb_min[3]{};
    float    world_aabb_max[3]{};
};

#endif // INSTANCEDGEOMETRY_H
