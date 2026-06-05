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

#include "ViewportCore.h"

#include <cstring>
#include <limits>
#include <vector>

#include "InstanceCompose.h"

ViewportCore::ViewportCore(ViewportHost* host) : host_(host) {}
ViewportCore::~ViewportCore() = default;

// Tear down a model's per-chunk GPU resources, free its pool slices,
// and reset all the bookkeeping vectors so the slot can be reused.
// Static because callers from outside this TU still live in
// ViewportWindow.cpp; ModelGpuData.h's declaration keeps the
// inter-TU contract.
void releaseWgpuModelGpuData(ModelGpuData& m, BufferPool& pool) {
    for (auto& c : m.chunks) {
        if (c.bind_group)           { wgpuBindGroupRelease(c.bind_group);          c.bind_group = nullptr; }
        if (c.vertex_slice.valid()) {
            pool.free(c.vertex_slice);
            c.vertex_slice = {};
        }
        if (c.index_slice.valid()) {
            pool.free(c.index_slice);
            c.index_slice = {};
        }
        if (c.visible_draws_buffer) { wgpuBufferRelease(c.visible_draws_buffer);   c.visible_draws_buffer = nullptr; }
        if (c.prefix_sums_buffer)   { wgpuBufferRelease(c.prefix_sums_buffer);     c.prefix_sums_buffer = nullptr; }
        if (c.per_chunk_uniform)    { wgpuBufferRelease(c.per_chunk_uniform);      c.per_chunk_uniform = nullptr; }
    }
    m.chunks.clear();
    m.mesh_chunk_idx.clear();
    m.mesh_chunk_local_base_vertex.clear();
    m.mesh_chunk_local_ebo_first_u32.clear();
    m.mesh_chunk_local_lod1_first_u32.clear();
    m.instance_chunk_idx.clear();
    m.instance_base_vertex.clear();
    m.instance_ebo_first_u32.clear();
    m.instance_lod1_first_u32.clear();
    if (m.mesh_storage)         { wgpuBufferRelease(m.mesh_storage);          m.mesh_storage = nullptr; }
    if (m.instance_storage)     { wgpuBufferRelease(m.instance_storage);      m.instance_storage = nullptr; }
    m.vertex_bytes   = 0;
    m.index_count    = 0;
    m.mesh_count     = 0;
    m.instance_count = 0;
    m.meshes.clear();
    m.instances.clear();
}

// ---- Scene mutators -------------------------------------------------------

void ViewportCore::removeModel(uint32_t model_id) {
    auto it = models_gpu_.find(model_id);
    if (it == models_gpu_.end()) return;
    releaseWgpuModelGpuData(it->second, pool_);
    models_gpu_.erase(it);
    host_->requestFrame();
}

void ViewportCore::resetScene() {
    for (auto& [mid, m] : models_gpu_) releaseWgpuModelGpuData(m, pool_);
    models_gpu_.clear();
    host_->requestFrame();
}

void ViewportCore::hideModel(uint32_t model_id) {
    auto it = models_gpu_.find(model_id);
    if (it == models_gpu_.end() || it->second.hidden) return;
    it->second.hidden = true;
    host_->requestFrame();
}

void ViewportCore::showModel(uint32_t model_id) {
    auto it = models_gpu_.find(model_id);
    if (it == models_gpu_.end() || !it->second.hidden) return;
    it->second.hidden = false;
    host_->requestFrame();
}

void ViewportCore::setFederatedFalseOrigin(const Eigen::Matrix4d& matrix_meters) {
    if (federated_false_origin_meters_ == matrix_meters) return;
    federated_false_origin_meters_ = matrix_meters;
    for (auto& kv : models_gpu_) recomposeAndUploadModel(kv.first);
}

void ViewportCore::setModelCoordinateOperation(uint32_t model_id,
                                               const Eigen::Matrix4d& matrix_meters) {
    auto it = models_gpu_.find(model_id);
    if (it == models_gpu_.end()) return;
    if (it->second.coordinate_operation_meters == matrix_meters) return;
    it->second.coordinate_operation_meters = matrix_meters;
    recomposeAndUploadModel(model_id);
}

void ViewportCore::setModelTransformation(uint32_t model_id,
                                          const Eigen::Matrix4d& matrix_meters) {
    auto it = models_gpu_.find(model_id);
    if (it == models_gpu_.end()) return;
    if (it->second.model_transformation_meters == matrix_meters) return;
    it->second.model_transformation_meters = matrix_meters;
    recomposeAndUploadModel(model_id);
}

void ViewportCore::recomposeAndUploadModel(uint32_t model_id) {
    if (!wgpu_initialized_) return;
    auto it = models_gpu_.find(model_id);
    if (it == models_gpu_.end()) return;
    ModelGpuData& m = it->second;
    if (m.instances.empty() || m.instance_storage == nullptr) return;

    std::vector<InstanceGpu> gpu(m.instances.size());
    for (size_t i = 0; i < m.instances.size(); ++i) {
        InstanceCpu& inst = m.instances[i];
        composeInstanceFromPlacement(inst, m);

        InstanceGpu& dst = gpu[i];
        std::memcpy(dst.transform, inst.transform, sizeof(dst.transform));
        dst.object_id            = inst.object_id;
        dst.color_override_rgba8 = inst.color_override_rgba8;
        dst.mesh_id              = inst.mesh_id;
        dst._pad1                = 0;
    }
    wgpuQueueWriteBuffer(queue_, m.instance_storage, 0,
                         gpu.data(), gpu.size() * sizeof(InstanceGpu));

    // Per-chunk world AABBs are derived from instance world AABBs; they
    // drive chunk-level frustum cull and the streaming priority, so they
    // must follow the recompose. Reset to ±inf and re-fold every chunk's
    // instances. Streaming chunks that haven't yet been assigned
    // instance_ids (extremely rare path) just stay at ±inf and naturally
    // fall out of frustum tests until the next load completes.
    for (auto& c : m.chunks) {
        c.aabb_min[0] = c.aabb_min[1] = c.aabb_min[2] =
             std::numeric_limits<float>::infinity();
        c.aabb_max[0] = c.aabb_max[1] = c.aabb_max[2] =
            -std::numeric_limits<float>::infinity();
        for (uint32_t inst_idx : c.instance_ids) {
            if (inst_idx >= m.instances.size()) continue;
            const InstanceCpu& inst = m.instances[inst_idx];
            for (int a = 0; a < 3; ++a) {
                c.aabb_min[a] = std::min(c.aabb_min[a], inst.world_aabb_min[a]);
                c.aabb_max[a] = std::max(c.aabb_max[a], inst.world_aabb_max[a]);
            }
        }
    }

    host_->requestFrame();
}

bool ViewportCore::findInstance(uint32_t object_id,
                                InstanceCompose::InstanceLookup& out) const {
    return InstanceCompose::findInstanceInModels(object_id, models_gpu_, out);
}

bool ViewportCore::firstGeometryPointWorldM(uint32_t model_id,
                                            Eigen::Vector3d& out) const {
    auto it = models_gpu_.find(model_id);
    if (it == models_gpu_.end()) return false;
    const ModelGpuData& m = it->second;
    if (m.instances.empty()) return false;

    const InstanceCpu& inst0 = m.instances[0];
    if (inst0.mesh_id >= m.meshes.size()) return false;
    const MeshInfo& mesh0 = m.meshes[inst0.mesh_id];

    // Mesh-local AABB centre — a point that's actually on the geometry.
    // Using AABB centre (vs. literal vertex 0) gives a centroid-like
    // anchor rather than a corner, which is more representative of where
    // the mesh "is" for the false-origin guess.
    const Eigen::Vector3d local_center_m(
        0.5 * (double(mesh0.local_aabb_min[0]) + double(mesh0.local_aabb_max[0])),
        0.5 * (double(mesh0.local_aabb_min[1]) + double(mesh0.local_aabb_max[1])),
        0.5 * (double(mesh0.local_aabb_min[2]) + double(mesh0.local_aabb_max[2])));

    // placement_transformation is double[16] column-major in metres,
    // pre-CoordinateOperation / FederatedFalseOrigin / ModelTransformation
    // (same convention as InstanceLookup above).
    using Mat4dCol = Eigen::Matrix<double, 4, 4, Eigen::ColMajor>;
    const Eigen::Matrix4d P =
        Eigen::Map<const Mat4dCol>(inst0.placement_transformation);
    out = (P * local_center_m.homogeneous()).head<3>();
    return true;
}

void ViewportCore::composeInstanceFromPlacement(InstanceCpu& inst,
                                                const ModelGpuData& m) const {
    if (inst.mesh_id < m.meshes.size()) {
        const MeshInfo& mi = m.meshes[inst.mesh_id];
        InstanceCompose::composeInstance(
            inst.placement_transformation,
            federated_false_origin_meters_,
            m.model_transformation_meters,
            m.coordinate_operation_meters,
            mi.local_aabb_min, mi.local_aabb_max,
            inst.transform,
            inst.world_aabb_min, inst.world_aabb_max);
    } else {
        // Unknown mesh id: still compose the transform (downstream may
        // use it for picking / readback even without geometry), but
        // emit a degenerate world AABB so cull doesn't pick this up.
        const float zero[3] = {0.0f, 0.0f, 0.0f};
        InstanceCompose::composeInstance(
            inst.placement_transformation,
            federated_false_origin_meters_,
            m.model_transformation_meters,
            m.coordinate_operation_meters,
            zero, zero,
            inst.transform,
            inst.world_aabb_min, inst.world_aabb_max);
        for (int a = 0; a < 3; ++a) {
            inst.world_aabb_min[a] = 0.0f;
            inst.world_aabb_max[a] = 0.0f;
        }
    }
}
