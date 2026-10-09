// This file was generated with the assistance of an AI coding tool.
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

#include "StreamedRecords.h"

#include "../ifcgeom/element.h"
#include "../ifcgeom/taxonomy.h"

#include <algorithm>
#include <cstring>
#include <limits>
#include <unordered_map>

struct MaterialInfo {
    float r = 0.75f, g = 0.75f, b = 0.78f, a = 1.0f;
};

static MaterialInfo materialFromStyle(const ifcopenshell::geom::taxonomy::style::ptr& style) {
    MaterialInfo material;
    if (!style) return material;
    const auto& color = style->get_color();
    if (color) {
        material.r = static_cast<float>(color.r());
        material.g = static_cast<float>(color.g());
        material.b = static_cast<float>(color.b());
    }
    if (!std::isnan(style->transparency)) {
        material.a = 1.0f - static_cast<float>(style->transparency);
    }
    return material;
}

static inline uint32_t packRGBA8(const MaterialInfo& material) {
    auto to_byte = [](float channel_value) -> uint32_t {
        float clamped_value = std::clamp(channel_value, 0.0f, 1.0f);
        return static_cast<uint32_t>(clamped_value * 255.0f + 0.5f);
    };
    uint32_t r = to_byte(material.r);
    uint32_t g = to_byte(material.g);
    uint32_t b = to_byte(material.b);
    uint32_t a = to_byte(material.a);
    // Little-endian byte layout [r,g,b,a] for GL_UNSIGNED_BYTE * 4 normalized.
    return r | (g << 8) | (b << 16) | (a << 24);
}

// Build a streamed mesh record (local coords, 28-byte interleaved vertices) from a
// TriangulationElement. Per-vertex color is baked from material_ids so that
// triangulations with per-face materials still render correctly.
// Vertex rebasing: when `offset` is non-zero, every vertex position is
// subtracted by it so the emitted mesh-local coordinates stay near the
// origin (and float32 precision survives upload to the GPU).  Caller
// compensates by post-multiplying each instance's PlacementTransformation
// by T(+offset), which is mathematically the identity overall but moves
// the magnitude off the float-precision-sensitive vertex column.
StreamedMesh buildStreamedMesh(uint32_t session_model_id,
                               uint32_t local_mesh_id,
                               const ifcopenshell::geom::triangulation_element* elem,
                               const Eigen::Vector3d& offset) {
    StreamedMesh mesh;
    mesh.session_model_id = session_model_id;
    mesh.local_mesh_id = local_mesh_id;

    const auto& geom = elem->geometry();
    const auto& verts = geom.verts();
    const auto& faces = geom.faces();
    const auto& normals = geom.normals();
    const auto& materials = geom.materials();
    const auto& material_ids = geom.material_ids();

    if (verts.empty() || faces.empty()) return mesh;

    const size_t num_verts_src = verts.size() / 3;
    const size_t num_tris = faces.size() / 3;
    const bool have_per_tri_material = (material_ids.size() == num_tris);

    // Dedupe (original vertex index, material id) so vertices shared across
    // triangles of the same material stay shared; vertices spanning multiple
    // materials are split (per-face color demands it).
    auto make_key = [](uint32_t orig_idx, int mat_id) -> uint64_t {
        return (static_cast<uint64_t>(orig_idx) << 32) | static_cast<uint32_t>(mat_id);
    };

    std::unordered_map<uint64_t, uint32_t> remap;
    remap.reserve(num_verts_src);

    mesh.vertices.reserve(num_verts_src * INSTANCED_VERTEX_STRIDE_FLOATS);
    mesh.indices.reserve(faces.size());

    // Track local AABB as we emit vertices.
    float local_aabb_min[3] = { std::numeric_limits<float>::max(),
                                std::numeric_limits<float>::max(),
                                std::numeric_limits<float>::max() };
    float local_aabb_max[3] = { -std::numeric_limits<float>::max(),
                                -std::numeric_limits<float>::max(),
                                -std::numeric_limits<float>::max() };

    auto emit_vertex = [&](uint32_t orig_idx, int mat_id) -> uint32_t {
        const uint64_t key = make_key(orig_idx, mat_id);
        auto it = remap.find(key);
        if (it != remap.end()) return it->second;

        const uint32_t new_idx = static_cast<uint32_t>(
            mesh.vertices.size() / INSTANCED_VERTEX_STRIDE_FLOATS);

        // Subtract in double, narrow to float — preserves precision when
        // verts are far from origin and offset cancels the magnitude.
        float px = static_cast<float>(verts[orig_idx * 3 + 0] - offset.x());
        float py = static_cast<float>(verts[orig_idx * 3 + 1] - offset.y());
        float pz = static_cast<float>(verts[orig_idx * 3 + 2] - offset.z());
        mesh.vertices.push_back(px);
        mesh.vertices.push_back(py);
        mesh.vertices.push_back(pz);
        if (px < local_aabb_min[0]) local_aabb_min[0] = px;
        if (px > local_aabb_max[0]) local_aabb_max[0] = px;
        if (py < local_aabb_min[1]) local_aabb_min[1] = py;
        if (py > local_aabb_max[1]) local_aabb_max[1] = py;
        if (pz < local_aabb_min[2]) local_aabb_min[2] = pz;
        if (pz > local_aabb_max[2]) local_aabb_max[2] = pz;

        if (orig_idx * 3 + 2 < normals.size()) {
            mesh.vertices.push_back(static_cast<float>(normals[orig_idx * 3 + 0]));
            mesh.vertices.push_back(static_cast<float>(normals[orig_idx * 3 + 1]));
            mesh.vertices.push_back(static_cast<float>(normals[orig_idx * 3 + 2]));
        } else {
            mesh.vertices.push_back(0.0f);
            mesh.vertices.push_back(1.0f);
            mesh.vertices.push_back(0.0f);
        }

        MaterialInfo m;
        if (mat_id >= 0 && mat_id < static_cast<int>(materials.size())) {
            m = materialFromStyle(materials[mat_id]);
        }
        uint32_t packed = packRGBA8(m);
        float packed_as_float;
        std::memcpy(&packed_as_float, &packed, sizeof(float));
        mesh.vertices.push_back(packed_as_float);

        remap.emplace(key, new_idx);
        return new_idx;
    };

    for (size_t t = 0; t < num_tris; ++t) {
        const int mat_id = have_per_tri_material ? material_ids[t] : -1;
        mesh.indices.push_back(emit_vertex(static_cast<uint32_t>(faces[t * 3 + 0]), mat_id));
        mesh.indices.push_back(emit_vertex(static_cast<uint32_t>(faces[t * 3 + 1]), mat_id));
        mesh.indices.push_back(emit_vertex(static_cast<uint32_t>(faces[t * 3 + 2]), mat_id));
    }

    if (mesh.vertices.empty()) {
        for (int a = 0; a < 3; ++a) local_aabb_min[a] = local_aabb_max[a] = 0.0f;
    }
    for (int a = 0; a < 3; ++a) {
        mesh.local_aabb_min[a] = local_aabb_min[a];
        mesh.local_aabb_max[a] = local_aabb_max[a];
    }
    return mesh;
}

// Compute the world-space AABB by transforming the 8 corners of the local
// AABB through the column-major 4x4 transform.
static void worldAabbFromLocal(const float local_min[3],
                               const float local_max[3],
                               const float M[16],
                               float out_min[3], float out_max[3]) {
    out_min[0] = out_min[1] = out_min[2] =  std::numeric_limits<float>::max();
    out_max[0] = out_max[1] = out_max[2] = -std::numeric_limits<float>::max();
    for (int c = 0; c < 8; ++c) {
        float x = (c & 1) ? local_max[0] : local_min[0];
        float y = (c & 2) ? local_max[1] : local_min[1];
        float z = (c & 4) ? local_max[2] : local_min[2];
        // Column-major: world = M * [x,y,z,1].
        float wx = M[0]*x + M[4]*y + M[8]*z  + M[12];
        float wy = M[1]*x + M[5]*y + M[9]*z  + M[13];
        float wz = M[2]*x + M[6]*y + M[10]*z + M[14];
        if (wx < out_min[0]) out_min[0] = wx; if (wx > out_max[0]) out_max[0] = wx;
        if (wy < out_min[1]) out_min[1] = wy; if (wy > out_max[1]) out_max[1] = wy;
        if (wz < out_min[2]) out_min[2] = wz; if (wz > out_max[2]) out_max[2] = wz;
    }
}

StreamedInstance makeStreamedInstance(uint32_t session_model_id,
                                      uint32_t local_mesh_id,
                                      uint32_t object_id,
                                      const ifcopenshell::geom::triangulation_element& elem,
                                      const MeshAabb& mesh_aabb) {
    // Vertex rebasing cont.: post-multiply the per-instance
    // PlacementTransformation by T(+offset) so world position is
    // preserved.  Keep the emitted placement in double so later
    // CoordinateOperation / false-origin composition can cancel
    // large translations before the final GPU float upload.
    Eigen::Matrix4d mat_d = elem.transformation().data()->ccomponents();
    if (mesh_aabb.has_offset) {
        const Eigen::Vector3d mesh_rebase_offset(
            mesh_aabb.offset[0], mesh_aabb.offset[1], mesh_aabb.offset[2]);
        mat_d.block<3, 1>(0, 3) += mat_d.block<3, 3>(0, 0) * mesh_rebase_offset;
    }

    StreamedInstance inst;
    inst.session_model_id = session_model_id;
    inst.local_mesh_id = local_mesh_id;
    inst.object_id = object_id;
    inst.color_override_rgba8 = 0;
    for (int i = 0; i < 16; ++i) {
        inst.transform[i] = mat_d.data()[i];
    }

    float mat_f[16];
    for (int i = 0; i < 16; ++i) {
        mat_f[i] = static_cast<float>(inst.transform[i]);
    }
    worldAabbFromLocal(mesh_aabb.lmin, mesh_aabb.lmax, mat_f,
                       inst.world_aabb_min, inst.world_aabb_max);
    return inst;
}
