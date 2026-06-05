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

#include <algorithm>
#include <cmath>
#include <cstdio>
#include <cstring>
#include <limits>
#include <vector>

#include "CameraMath.h"
#include "InstanceCompose.h"
#include "Log.h"

namespace {
// Orbit camera around target_. World +Z up (BIM convention). Yaw is
// rotation about Z (positive = anticlockwise looking down +Z); pitch
// is elevation above the XY plane. Matches the GL viewport's
// updateCamera convention so framing aligns between backends.
Eigen::Vector3f orbitEye(const float target[3], float dist,
                         float yaw_deg, float pitch_deg) {
    constexpr float kDeg2Rad = float(M_PI) / 180.0f;
    const float yaw = yaw_deg   * kDeg2Rad;
    const float pit = pitch_deg * kDeg2Rad;
    const float cp = std::cos(pit), sp = std::sin(pit);
    const float cy = std::cos(yaw), sy = std::sin(yaw);
    return Eigen::Vector3f(target[0] + dist * cp * cy,
                           target[1] + dist * cp * sy,
                           target[2] + dist * sp);
}
} // namespace

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

// ---- Camera math ----------------------------------------------------------

void ViewportCore::buildViewProj(Eigen::Matrix4f& view_out,
                                 Eigen::Matrix4f& proj_out) const {
    const Eigen::Vector3f target(camera_target_[0], camera_target_[1], camera_target_[2]);
    const Eigen::Vector3f eye = orbitEye(camera_target_, camera_distance_,
                                         camera_yaw_deg_, camera_pitch_deg_);
    // Within 1° of straight-up/down, switch up from world +Z to world +Y
    // so lookAt's side vector doesn't degenerate (forward × up → 0).
    const Eigen::Vector3f up = (std::abs(camera_pitch_deg_) >= 89.0f)
                       ? Eigen::Vector3f(0.0f, 1.0f, 0.0f)
                       : Eigen::Vector3f(0.0f, 0.0f, 1.0f);
    view_out = lookAtRH(eye, target, up);

    const float aspect = (configured_h_ > 0)
                            ? float(configured_w_) / float(configured_h_)
                            : 1.0f;
    Eigen::Matrix4f p;
    if (projection_ortho_) {
        constexpr float kDeg2Rad = float(M_PI) / 180.0f;
        const float half_h = camera_distance_
            * std::tan(camera_fov_y_deg_ * 0.5f * kDeg2Rad);
        const float half_w = half_h * aspect;
        const float depth  = camera_distance_ * 10.0f;
        p = orthoGL(-half_w, half_w, -half_h, half_h, -depth, depth);
    } else {
        p = perspectiveYFovGL(camera_fov_y_deg_, aspect, camera_near_, camera_far_);
    }
    Eigen::Matrix4f z_remap = Eigen::Matrix4f::Identity();
    z_remap(2, 2) = 0.5f;
    z_remap(2, 3) = 0.5f;
    proj_out = z_remap * p;
}

bool ViewportCore::computeSceneAabb(float mn[3], float mx[3]) const {
    bool any = false;
    for (int i = 0; i < 3; ++i) {
        mn[i] =  std::numeric_limits<float>::infinity();
        mx[i] = -std::numeric_limits<float>::infinity();
    }
    for (const auto& [mid, m] : models_gpu_) {
        if (m.hidden) continue;
        for (const auto& inst : m.instances) {
            for (int i = 0; i < 3; ++i) {
                mn[i] = std::min(mn[i], inst.world_aabb_min[i]);
                mx[i] = std::max(mx[i], inst.world_aabb_max[i]);
            }
            any = true;
        }
    }
    return any;
}

float ViewportCore::chunkScreenAreaPx(const ModelGpuData::Chunk& c,
                                      const Eigen::Matrix4f& vp_mat) const {
    if (configured_w_ <= 0 || configured_h_ <= 0)   return 0.0f;
    if (c.aabb_min[0] > c.aabb_max[0])              return 0.0f;
    const float full_area = float(configured_w_) * float(configured_h_);

    // Eye-inside-AABB → full viewport (matches GL contribution-cull
    // short-circuit). Any corner behind near plane → also full
    // viewport; 8 corners can't measure true on-screen extent once
    // any are behind, so over-prioritise rather than under-prioritise.
    const Eigen::Vector3f eye = orbitEye(camera_target_, camera_distance_,
                                         camera_yaw_deg_, camera_pitch_deg_);
    if (eye.x() >= c.aabb_min[0] && eye.x() <= c.aabb_max[0] &&
        eye.y() >= c.aabb_min[1] && eye.y() <= c.aabb_max[1] &&
        eye.z() >= c.aabb_min[2] && eye.z() <= c.aabb_max[2]) {
        return full_area;
    }

    float xmin = std::numeric_limits<float>::infinity();
    float ymin = std::numeric_limits<float>::infinity();
    float xmax = -std::numeric_limits<float>::infinity();
    float ymax = -std::numeric_limits<float>::infinity();
    int corners_in_front = 0;
    int corners_behind   = 0;
    for (int i = 0; i < 8; ++i) {
        const Eigen::Vector4f corner_world(
            (i & 1) ? c.aabb_max[0] : c.aabb_min[0],
            (i & 2) ? c.aabb_max[1] : c.aabb_min[1],
            (i & 4) ? c.aabb_max[2] : c.aabb_min[2],
            1.0f);
        const Eigen::Vector4f clip = vp_mat * corner_world;
        if (clip.w() <= 1e-3f) { ++corners_behind; continue; }
        ++corners_in_front;
        const float ndc_x = clip.x() / clip.w();
        const float ndc_y = clip.y() / clip.w();
        const float px_x  = (ndc_x * 0.5f + 0.5f) * float(configured_w_);
        const float px_y  = (ndc_y * 0.5f + 0.5f) * float(configured_h_);
        xmin = std::min(xmin, px_x);
        ymin = std::min(ymin, px_y);
        xmax = std::max(xmax, px_x);
        ymax = std::max(ymax, px_y);
    }
    if (corners_in_front == 0) return 0.0f;
    if (corners_behind > 0)    return full_area;

    xmin = std::max(xmin, 0.0f);
    ymin = std::max(ymin, 0.0f);
    xmax = std::min(xmax, float(configured_w_));
    ymax = std::min(ymax, float(configured_h_));
    if (xmax <= xmin || ymax <= ymin) return 0.0f;
    return (xmax - xmin) * (ymax - ymin);
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

// ---- Camera mutators ------------------------------------------------------

void ViewportCore::frameAabb(const float mn[3], const float mx[3],
                             float padding) {
    constexpr float kDeg2Rad = float(M_PI) / 180.0f;
    const float cx = 0.5f * (mn[0] + mx[0]);
    const float cy = 0.5f * (mn[1] + mx[1]);
    const float cz = 0.5f * (mn[2] + mx[2]);
    camera_target_[0] = cx;
    camera_target_[1] = cy;
    camera_target_[2] = cz;

    const float dx = mx[0] - mn[0];
    const float dy = mx[1] - mn[1];
    const float dz = mx[2] - mn[2];
    const float radius = 0.5f * std::sqrt(dx*dx + dy*dy + dz*dz);

    if (radius > 1e-4f) {
        const float fovy_rad = camera_fov_y_deg_ * kDeg2Rad;
        const float tan_half = std::tan(fovy_rad * 0.5f);
        if (tan_half > 1e-6f) {
            const int   h          = std::max(configured_h_, 1);
            const float aspect     = float(std::max(configured_w_, 1)) / float(h);
            const float min_aspect = aspect < 1.0f ? aspect : 1.0f;
            camera_distance_ = std::max(0.1f, (radius / (tan_half * min_aspect)) * padding);
        }
    }
    host_->requestFrame();
}

void ViewportCore::viewAll() {
    float mn[3], mx[3];
    if (!computeSceneAabb(mn, mx)) return;

    // Same math as GL's frameAabb(mn, mx, 1.10): target at centroid,
    // distance pulls the bounding sphere just inside the tighter of
    // horizontal/vertical FOV. 1.10 padding matches GL viewAll.
    frameAabb(mn, mx, 1.10f);

    const float cx = 0.5f * (mn[0] + mx[0]);
    const float cy = 0.5f * (mn[1] + mx[1]);
    const float cz = 0.5f * (mn[2] + mx[2]);
    const float dx = mx[0] - mn[0];
    const float dy = mx[1] - mn[1];
    const float dz = mx[2] - mn[2];
    const float radius = 0.5f * std::sqrt(dx*dx + dy*dy + dz*dz);
    std::fprintf(stderr,
        "[info] [wgpu] viewAll target=(%g, %g, %g) distance=%g (scene radius=%g)\n",
        cx, cy, cz, camera_distance_, radius);
}

void ViewportCore::setCamera(float tx, float ty, float tz,
                             float dist, float yaw_deg, float pitch_deg) {
    camera_target_[0]   = tx;
    camera_target_[1]   = ty;
    camera_target_[2]   = tz;
    camera_distance_    = std::max(0.01f, dist);
    camera_yaw_deg_     = yaw_deg;
    // Mirrors GL clamp — keep pitch just shy of the pole so orbit math
    // doesn't degenerate. The standard-view top/bottom hotkeys go through
    // setStandardView, which bypasses the clamp on purpose.
    camera_pitch_deg_   = std::clamp(pitch_deg, -89.9f, 89.9f);
    host_->requestFrame();
}

void ViewportCore::setStandardView(float yaw_deg, float pitch_deg) {
    // Bypass the orbit-pitch clamp so top/bottom land exactly at ±90°.
    // buildViewProj picks the up vector based on |pitch| so lookAt
    // stays well-conditioned at the poles.
    camera_yaw_deg_   = yaw_deg;
    camera_pitch_deg_ = pitch_deg;
    host_->requestFrame();
}

void ViewportCore::toggleProjection() {
    projection_ortho_ = !projection_ortho_;
    std::fprintf(stderr, "[info] [wgpu] projection: %s\n",
                 projection_ortho_ ? "ortho" : "perspective");
    host_->requestFrame();
}

std::string ViewportCore::cameraString() const {
    char buf[128];
    std::snprintf(buf, sizeof(buf), "%.4f,%.4f,%.4f,%.4f,%.2f,%.2f",
                  camera_target_[0], camera_target_[1], camera_target_[2],
                  camera_distance_, camera_yaw_deg_, camera_pitch_deg_);
    return std::string(buf);
}

ViewportCore::CameraState ViewportCore::cameraState() const {
    CameraState s;
    s.target  = Eigen::Vector3f(camera_target_[0], camera_target_[1], camera_target_[2]);
    s.distance = camera_distance_;
    s.yaw      = camera_yaw_deg_;
    s.pitch    = camera_pitch_deg_;
    return s;
}

bool ViewportCore::computeObjectAabb(uint32_t object_id,
                                     float mn[3], float mx[3]) const {
    bool any = false;
    for (int i = 0; i < 3; ++i) {
        mn[i] =  std::numeric_limits<float>::infinity();
        mx[i] = -std::numeric_limits<float>::infinity();
    }
    for (const auto& [mid, m] : models_gpu_) {
        for (const auto& inst : m.instances) {
            if (inst.object_id != object_id) continue;
            for (int i = 0; i < 3; ++i) {
                mn[i] = std::min(mn[i], inst.world_aabb_min[i]);
                mx[i] = std::max(mx[i], inst.world_aabb_max[i]);
            }
            any = true;
        }
    }
    return any;
}

bool ViewportCore::computeObjectAabb(uint32_t object_id,
                                     Eigen::Vector3f& mn,
                                     Eigen::Vector3f& mx) const {
    float fmin[3], fmax[3];
    if (!computeObjectAabb(object_id, fmin, fmax)) return false;
    mn = Eigen::Vector3f(fmin[0], fmin[1], fmin[2]);
    mx = Eigen::Vector3f(fmax[0], fmax[1], fmax[2]);
    return true;
}

// |det| of the 3×3 linear part of a column-major double[16] placement
// matrix. Picks up uniform scale + mirror so a 2× clone of a 1m³ mesh
// reports 8m³. Used by the volume readout below.
namespace {
double det3OfPlacement(const double M[16]) {
    const double m00 = M[0],  m10 = M[1],  m20 = M[2];
    const double m01 = M[4],  m11 = M[5],  m21 = M[6];
    const double m02 = M[8],  m12 = M[9],  m22 = M[10];
    return m00 * (m11 * m22 - m12 * m21)
         - m01 * (m10 * m22 - m12 * m20)
         + m02 * (m10 * m21 - m11 * m20);
}
} // namespace

double ViewportCore::volumeOfObjects(
        const std::vector<uint32_t>& object_ids) const {
    if (object_ids.empty()) return 0.0;
    double total = 0.0;
    for (uint32_t oid : object_ids) {
        for (const auto& [mid, m] : models_gpu_) {
            auto it = m.object_id_to_instance.find(oid);
            if (it == m.object_id_to_instance.end()) continue;
            const InstanceCpu& inst = m.instances[it->second];
            if (inst.mesh_id >= m.mesh_local_volumes.size()) break;
            const double v_local = m.mesh_local_volumes[inst.mesh_id];
            const double det = std::abs(det3OfPlacement(inst.placement_transformation));
            total += v_local * det;
            break;  // object_id is globally unique → at most one hit
        }
    }
    return total;
}

std::vector<std::pair<uint32_t, double>>
ViewportCore::volumesPerObject(
        const std::vector<uint32_t>& object_ids) const {
    std::vector<std::pair<uint32_t, double>> out;
    if (object_ids.empty()) return out;
    out.reserve(object_ids.size());
    for (uint32_t oid : object_ids) {
        for (const auto& [mid, m] : models_gpu_) {
            auto it = m.object_id_to_instance.find(oid);
            if (it == m.object_id_to_instance.end()) continue;
            const InstanceCpu& inst = m.instances[it->second];
            if (inst.mesh_id >= m.mesh_local_volumes.size()) break;
            const double v_local = m.mesh_local_volumes[inst.mesh_id];
            const double det = std::abs(det3OfPlacement(inst.placement_transformation));
            out.emplace_back(oid, v_local * det);
            break;
        }
    }
    return out;
}

// ===========================================================================
// Pipeline construction (#84-k)
// ===========================================================================

namespace {
// WGPUStringView builder for null-terminated C strings. Used heavily by
// label fields and shader source descriptors. Tiny but worth a name.
WGPUStringView svFromCStr(const char* s) {
    WGPUStringView v{};
    v.data   = s;
    v.length = std::strlen(s);
    return v;
}

static const char* MAIN_WGSL = R"(
struct InstanceRecord {
    transform: mat4x4<f32>,
    object_id: u32,
    color_override: u32,
    mesh_id: u32,
    _pad1: u32,
};

struct MeshQuant {
    aabb_min: vec4<f32>,
    aabb_max: vec4<f32>,
};

struct FrameUniforms {
    view_proj:    mat4x4<f32>,
    light_dir:    vec4<f32>,
    fill_dir:     vec4<f32>,
    sky_color:    vec4<f32>,
    ground_color: vec4<f32>,
    clip_count:   i32,
    // Three scalar i32 pads instead of vec3<i32>: vec3 has 16-byte
    // alignment so it would also pad the SUBSEQUENT clip_planes start
    // up to offset 160. Three i32s pad to 144 with no further nudge,
    // matching the tightly-packed C++ FrameUniforms (240 B).
    _pad_clip_0:  i32,
    _pad_clip_1:  i32,
    _pad_clip_2:  i32,
    clip_planes:  array<vec4<f32>, 6>,
    // X-ray mode cap. fs_main clamps `out.a = min(in.color.a, xray_alpha_cap)`.
    // Default 1.0 (no effect — the min returns in.color.a). Alt+X drops it
    // toward ~0.3 to translucent-everything. The cull classifier also
    // routes every instance into the transparent pass when this is < 1
    // so the blend stage actually fires (an opaque-pass fragment with
    // capped alpha would still overwrite the back buffer).
    xray_alpha_cap: f32,
    _pad_xray_0:  f32,
    _pad_xray_1:  f32,
    _pad_xray_2:  f32,
};

// Returns true if `world` lies on the positive (clipped-away) side of any
// active section plane. Each plane is (n.xyz, d) and clips where
// dot(n, world) + d > 0. Both the main and pick fragments discard with
// this predicate so cuts are visible AND consistent with selection.
fn is_section_clipped(world: vec3<f32>) -> bool {
    let n = u_frame.clip_count;
    if (n == 0) { return false; }
    for (var i = 0; i < n; i = i + 1) {
        let p = u_frame.clip_planes[i];
        if (dot(p.xyz, world) + p.w > 0.0) { return true; }
    }
    return false;
}

struct VisibleDraw {
    mesh_id:        u32,
    instance_idx:   u32,
    ebo_first_u32:  u32,
    base_vertex:    u32,
};

struct PerModel {
    draw_count:           u32,
    total_vertex_count:   u32,
    _pad0:                u32,
    _pad1:                u32,
};

@group(0) @binding(0) var<uniform> u_frame: FrameUniforms;
// Selection flags indexed by object_id. bit 0 = in selection, bit 1 = active.
// Sized to next_object_id_ on the CPU side; out-of-range reads can't happen
// because we cap the index by arrayLength before fetching.
@group(0) @binding(1) var<storage, read> sel_flags: array<u32>;

@group(1) @binding(0) var<storage, read> vertices:      array<u32>;
@group(1) @binding(1) var<storage, read> meshes:        array<MeshQuant>;
@group(1) @binding(2) var<storage, read> instances:     array<InstanceRecord>;
@group(1) @binding(3) var<storage, read> indices:       array<u32>;
@group(1) @binding(4) var<storage, read> visible_draws: array<VisibleDraw>;
@group(1) @binding(5) var<storage, read> prefix_sums:   array<u32>;
@group(1) @binding(6) var<uniform>       u_model:       PerModel;

struct VsOut {
    @builtin(position) clip_pos: vec4<f32>,
    @location(0) normal:    vec3<f32>,
    @location(1) color:     vec4<f32>,
    @location(2) world_pos: vec3<f32>,
    @location(3) @interpolate(flat) object_id: u32,
};

// Sign-extend an i8 packed into the byte_idx'th byte of `packed`.
fn extractI8(packed: u32, byte_idx: u32) -> i32 {
    let raw = i32((packed >> (byte_idx * 8u)) & 0xFFu);
    return select(raw, raw - 256, raw >= 128);
}

// Meyer et al. octahedral normal decode. Input in [-1,1]^2.
fn octDecode(e: vec2<f32>) -> vec3<f32> {
    var n = vec3<f32>(e.x, e.y, 1.0 - abs(e.x) - abs(e.y));
    if (n.z < 0.0) {
        let tx = select(-1.0, 1.0, n.x >= 0.0);
        let ty = select(-1.0, 1.0, n.y >= 0.0);
        n = vec3<f32>((1.0 - abs(n.y)) * tx, (1.0 - abs(n.x)) * ty, n.z);
    }
    return normalize(n);
}

// Binary search for the largest i in [0, draw_count) with prefix_sums[i] <= vid.
// prefix_sums is monotonic non-decreasing and contains draw_count+1 entries
// (prefix_sums[draw_count] == total_vertex_count).
fn find_draw(vid: u32) -> u32 {
    var lo: u32 = 0u;
    var hi: u32 = u_model.draw_count;
    while (lo + 1u < hi) {
        let mid = (lo + hi) >> 1u;
        if (prefix_sums[mid] <= vid) {
            lo = mid;
        } else {
            hi = mid;
        }
    }
    return lo;
}

@vertex
fn vs_main(@builtin(vertex_index) vid: u32) -> VsOut {
    // Saturate past the end (shouldn't happen given draw() count, but safe).
    if (vid >= u_model.total_vertex_count) {
        var degen: VsOut;
        degen.clip_pos = vec4<f32>(0.0, 0.0, 0.0, 0.0);
        return degen;
    }

    let draw_idx = find_draw(vid);
    let local_v  = vid - prefix_sums[draw_idx];
    let item     = visible_draws[draw_idx];

    // Fetch the mesh-local index then the global vertex index.
    let mesh_local_index = indices[item.ebo_first_u32 + local_v];
    let v_global         = item.base_vertex + mesh_local_index;

    let inst = instances[item.instance_idx];
    let mq   = meshes[item.mesh_id];

    let w0 = vertices[v_global * 3u + 0u];
    let w1 = vertices[v_global * 3u + 1u];
    let w2 = vertices[v_global * 3u + 2u];

    let px = f32(w0 & 0xFFFFu)         / 65535.0;
    let py = f32((w0 >> 16u) & 0xFFFFu) / 65535.0;
    let pz = f32(w1 & 0xFFFFu)         / 65535.0;
    let pos_local = mix(mq.aabb_min.xyz, mq.aabb_max.xyz, vec3<f32>(px, py, pz));

    let nx = f32(extractI8(w1, 2u)) / 127.0;
    let ny = f32(extractI8(w1, 3u)) / 127.0;
    let n_local = octDecode(vec2<f32>(nx, ny));

    let r = f32(w2 & 0xFFu)          / 255.0;
    let g = f32((w2 >>  8u) & 0xFFu) / 255.0;
    let b = f32((w2 >> 16u) & 0xFFu) / 255.0;
    let a = f32((w2 >> 24u) & 0xFFu) / 255.0;

    let world4 = inst.transform * vec4<f32>(pos_local, 1.0);
    let rot = mat3x3<f32>(inst.transform[0].xyz,
                          inst.transform[1].xyz,
                          inst.transform[2].xyz);
    let n_world = normalize(rot * n_local);
    let det = determinant(rot);
    let n_final = select(n_world, -n_world, det < 0.0);

    var color = vec4<f32>(r, g, b, a);
    if (inst.color_override != 0u) {
        let cr = f32(inst.color_override         & 0xFFu) / 255.0;
        let cg = f32((inst.color_override >>  8u) & 0xFFu) / 255.0;
        let cb = f32((inst.color_override >> 16u) & 0xFFu) / 255.0;
        let ca = f32((inst.color_override >> 24u) & 0xFFu) / 255.0;
        if (ca > 0.0) { color = vec4<f32>(cr, cg, cb, ca); }
    }

    var out: VsOut;
    out.clip_pos  = u_frame.view_proj * world4;
    out.normal    = n_final;
    out.color     = color;
    out.world_pos = world4.xyz;
    out.object_id = inst.object_id;
    return out;
}

// sRGB decode — used to undo wgpu's automatic linear→sRGB write encoding
// on swap-chain BGRA8Unorm so the final bytes match what the GL backend
// writes directly. The GL pipeline outputs to a non-sRGB FB and treats
// every colour input as already-linear, so its bytes are exactly its
// shader outputs. wgpu on the same swap chain auto-encodes, which makes
// everything appear ~3× brighter unless we pre-decode once.
fn srgbToLinear(s: vec3<f32>) -> vec3<f32> {
    let lo = s / 12.92;
    let hi = pow((s + 0.055) / 1.055, vec3<f32>(2.4));
    return select(hi, lo, s <= vec3<f32>(0.04045));
}

@fragment
fn fs_main(in: VsOut) -> @location(0) vec4<f32> {
    if (is_section_clipped(in.world_pos)) { discard; }

    var n = normalize(in.normal);

    // World +Z is up (BIM convention). Hemisphere ambient: faces pointing
    // up read sky, faces pointing down read ground, lerp by n.z.
    let hemi_t  = 0.5 + 0.5 * n.z;
    let ambient = mix(u_frame.ground_color.xyz, u_frame.sky_color.xyz, hemi_t);

    let key  = max(dot(n, u_frame.light_dir.xyz), 0.0);
    let fill = max(dot(n, u_frame.fill_dir.xyz),  0.0) * 0.35;

    var color = in.color.xyz * (ambient + (key + fill) * 0.7);

    // Cavity shading: where adjacent fragments have a sharp normal change
    // (concave creases, edges where two faces meet), darken slightly so
    // shape boundaries read on flat-colour models. Matches the GL shader.
    let cavity = clamp(length(fwidth(n)) * 1.5, 0.0, 0.35);
    color = color * (1.0 - cavity);

    // Selection tint. bit 0 = in selection (cool blue mix), bit 1 = active
    // (slightly stronger blue mix). Matches the GL main shader.
    if (in.object_id < arrayLength(&sel_flags)) {
        let flags = sel_flags[in.object_id];
        if ((flags & 1u) != 0u) { color = mix(color, vec3<f32>(0.2, 0.6, 1.0), 0.45); }
        if ((flags & 2u) != 0u) { color = mix(color, vec3<f32>(0.4, 0.8, 1.0), 0.40); }
    }

    // Cancel the swap chain's implicit linear→sRGB encoding so the final
    // bytes match the GL backend (see srgbToLinear above). Alpha is
    // clamped to `xray_alpha_cap` (default 1.0 = no effect; X-ray sets
    // it to ~0.3) so a global translucency override lands without
    // touching any per-instance state.
    let alpha_out = min(in.color.a, u_frame.xray_alpha_cap);
    return vec4<f32>(srgbToLinear(color), alpha_out);
}

// --------------------------- Pick pipeline ---------------------------------
// Same vertex pulling as vs_main, but VsOutPick carries only the object_id
// (flat-interpolated). Fragment writes the object_id to an R32UInt target.
// Background (no draw) reads 0 because the pick attachment is cleared to 0.

struct VsOutPick {
    @builtin(position) clip_pos: vec4<f32>,
    @location(0) @interpolate(flat) object_id: u32,
    @location(1) world_pos: vec3<f32>,
    @location(2) normal:    vec3<f32>,
};

// Section tool needs the actual per-fragment normal (the AABB face was
// too coarse for diagonal geometry). Two color attachments — R32UInt
// object_id at @location(0), RGBA16F packed normal at @location(1).
// We multiply-by-0.5+0.5 so unsigned half-floats keep the sign without
// extra channel allocation.
struct FsOutPick {
    @location(0) object_id: u32,
    @location(1) normal:    vec4<f32>,
};

@vertex
fn vs_pick(@builtin(vertex_index) vid: u32) -> VsOutPick {
    var out: VsOutPick;
    if (vid >= u_model.total_vertex_count) {
        out.clip_pos  = vec4<f32>(0.0, 0.0, 0.0, 0.0);
        out.object_id = 0u;
        out.world_pos = vec3<f32>(0.0, 0.0, 0.0);
        out.normal    = vec3<f32>(0.0, 0.0, 1.0);
        return out;
    }

    let draw_idx = find_draw(vid);
    let local_v  = vid - prefix_sums[draw_idx];
    let item     = visible_draws[draw_idx];
    let mesh_local_index = indices[item.ebo_first_u32 + local_v];
    let v_global = item.base_vertex + mesh_local_index;
    let inst = instances[item.instance_idx];
    let mq   = meshes[item.mesh_id];

    let w0 = vertices[v_global * 3u + 0u];
    let w1 = vertices[v_global * 3u + 1u];
    let pos_norm = vec3<f32>(
        f32(w0 & 0xFFFFu)          / 65535.0,
        f32((w0 >> 16u) & 0xFFFFu) / 65535.0,
        f32(w1 & 0xFFFFu)          / 65535.0,
    );
    let pos_local = mix(mq.aabb_min.xyz, mq.aabb_max.xyz, pos_norm);
    let world4    = inst.transform * vec4<f32>(pos_local, 1.0);

    // Decode the same octahedral normal as vs_main — pick needs it so
    // the section tool can drop perpendicular cuts.
    let nx = f32(extractI8(w1, 2u)) / 127.0;
    let ny = f32(extractI8(w1, 3u)) / 127.0;
    let n_local = octDecode(vec2<f32>(nx, ny));
    let rot = mat3x3<f32>(inst.transform[0].xyz,
                          inst.transform[1].xyz,
                          inst.transform[2].xyz);
    let n_world = normalize(rot * n_local);
    let det = determinant(rot);
    let n_final = select(n_world, -n_world, det < 0.0);

    out.clip_pos  = u_frame.view_proj * world4;
    out.object_id = inst.object_id;
    out.world_pos = world4.xyz;
    out.normal    = n_final;
    return out;
}

@fragment
fn fs_pick(in: VsOutPick) -> FsOutPick {
    if (is_section_clipped(in.world_pos)) { discard; }
    var out: FsOutPick;
    out.object_id = in.object_id;
    // Pack signed normal into RGBA16F (unsigned-ish half range) as ×0.5+0.5.
    out.normal = vec4<f32>(normalize(in.normal) * 0.5 + vec3<f32>(0.5), 1.0);
    return out;
}
)";
} // namespace

bool ViewportCore::buildPipelines() {
    // ---- Bind group layouts ----------------------------------------------
    WGPUBindGroupLayoutEntry frame_entries[2] = {};
    frame_entries[0].binding = 0;
    frame_entries[0].visibility = WGPUShaderStage_Vertex | WGPUShaderStage_Fragment;
    frame_entries[0].buffer.type = WGPUBufferBindingType_Uniform;
    frame_entries[0].buffer.minBindingSize = sizeof(FrameUniforms);
    frame_entries[1].binding = 1;
    frame_entries[1].visibility = WGPUShaderStage_Fragment;
    frame_entries[1].buffer.type = WGPUBufferBindingType_ReadOnlyStorage;

    WGPUBindGroupLayoutDescriptor frame_bgl_desc = {};
    frame_bgl_desc.entryCount = 2;
    frame_bgl_desc.entries    = frame_entries;
    frame_bgl_desc.label      = svFromCStr("ifcviewer-wgpu.frame_bgl");
    frame_bgl_ = wgpuDeviceCreateBindGroupLayout(device_, &frame_bgl_desc);

    // 6 read-only storage buffers (vertices, meshes, instances, indices,
    // visible_draws, prefix_sums) + 1 uniform (per-model count). All read
    // in the vertex shader. WebGPU's mandatory min is 8 storage / 12 uniform
    // per stage, so we're comfortably under the cap.
    WGPUBindGroupLayoutEntry model_entries[7] = {};
    for (int i = 0; i < 6; ++i) {
        model_entries[i].binding     = uint32_t(i);
        model_entries[i].visibility  = WGPUShaderStage_Vertex;
        model_entries[i].buffer.type = WGPUBufferBindingType_ReadOnlyStorage;
    }
    model_entries[6].binding             = 6;
    model_entries[6].visibility          = WGPUShaderStage_Vertex;
    model_entries[6].buffer.type         = WGPUBufferBindingType_Uniform;
    model_entries[6].buffer.minBindingSize = 16;
    WGPUBindGroupLayoutDescriptor model_bgl_desc = {};
    model_bgl_desc.entryCount = 7;
    model_bgl_desc.entries    = model_entries;
    model_bgl_desc.label      = svFromCStr("ifcviewer-wgpu.model_bgl");
    model_bgl_ = wgpuDeviceCreateBindGroupLayout(device_, &model_bgl_desc);

    // ---- Pipeline layout -------------------------------------------------
    WGPUBindGroupLayout bgls[2] = { frame_bgl_, model_bgl_ };
    WGPUPipelineLayoutDescriptor pl_desc = {};
    pl_desc.bindGroupLayoutCount = 2;
    pl_desc.bindGroupLayouts     = bgls;
    pl_desc.label                = svFromCStr("ifcviewer-wgpu.pipeline_layout");
    pipeline_layout_ = wgpuDeviceCreatePipelineLayout(device_, &pl_desc);

    // ---- Shader module ---------------------------------------------------
    WGPUShaderSourceWGSL wgsl_src = {};
    wgsl_src.chain.sType = WGPUSType_ShaderSourceWGSL;
    wgsl_src.code        = svFromCStr(MAIN_WGSL);

    WGPUShaderModuleDescriptor sm_desc = {};
    sm_desc.nextInChain = &wgsl_src.chain;
    sm_desc.label       = svFromCStr("ifcviewer-wgpu.main_wgsl");
    main_shader_module_ = wgpuDeviceCreateShaderModule(device_, &sm_desc);

    // ---- Render pipeline -------------------------------------------------
    WGPUColorTargetState color_target = {};
    color_target.format    = surface_format_;
    color_target.writeMask = WGPUColorWriteMask_All;

    WGPUFragmentState frag = {};
    frag.module      = main_shader_module_;
    frag.entryPoint  = svFromCStr("fs_main");
    frag.targetCount = 1;
    frag.targets     = &color_target;

    WGPUDepthStencilState depth = {};
    depth.format              = WGPUTextureFormat_Depth32Float;
    depth.depthWriteEnabled   = WGPUOptionalBool_True;
    depth.depthCompare        = WGPUCompareFunction_Less;
    depth.stencilFront.compare = WGPUCompareFunction_Always;
    depth.stencilBack.compare  = WGPUCompareFunction_Always;

    WGPURenderPipelineDescriptor rp_desc = {};
    rp_desc.layout            = pipeline_layout_;
    rp_desc.label             = svFromCStr("ifcviewer-wgpu.main_pipeline");
    rp_desc.vertex.module     = main_shader_module_;
    rp_desc.vertex.entryPoint = svFromCStr("vs_main");
    rp_desc.vertex.bufferCount = 0;       // vertex pulling: no IA bindings
    rp_desc.fragment          = &frag;
    rp_desc.depthStencil      = &depth;
    rp_desc.primitive.topology = WGPUPrimitiveTopology_TriangleList;
    rp_desc.primitive.cullMode = WGPUCullMode_Back;
    rp_desc.primitive.frontFace = WGPUFrontFace_CCW;
    rp_desc.multisample.count = kViewportSampleCount;
    rp_desc.multisample.mask  = 0xFFFFFFFFu;

    main_pipeline_ = wgpuDeviceCreateRenderPipeline(device_, &rp_desc);
    if (!main_pipeline_) {
        Log::warn() << "wgpu main render pipeline creation failed";
        return false;
    }

    // ---- Transparent variant of the main pipeline ----------------------
    // Same shader, same layout, same vertex pulling, same depth test —
    // differs only in:
    //   * depth.depthWriteEnabled = False (we still depth-test against
    //     the opaque pass's z-buffer, but the transparent fragment's z
    //     doesn't write, so further-back geometry behind the glass still
    //     paints over)
    //   * color_target.blend = SrcAlpha / OneMinusSrcAlpha (standard
    //     porter-duff "over" — premultiplied wouldn't help because our
    //     vertex colours come in straight-alpha from the IFC iterator)
    // No sort, no OIT — overlapping transparent surfaces of the same
    // kind will produce order-dependent artefacts but for typical IFC
    // glazing (panes that don't overlap much in screen space) the
    // result is "good enough".
    WGPUBlendState main_blend = {};
    main_blend.color.srcFactor = WGPUBlendFactor_SrcAlpha;
    main_blend.color.dstFactor = WGPUBlendFactor_OneMinusSrcAlpha;
    main_blend.color.operation = WGPUBlendOperation_Add;
    main_blend.alpha.srcFactor = WGPUBlendFactor_One;
    main_blend.alpha.dstFactor = WGPUBlendFactor_OneMinusSrcAlpha;
    main_blend.alpha.operation = WGPUBlendOperation_Add;

    WGPUColorTargetState color_target_transparent = color_target;
    color_target_transparent.blend = &main_blend;

    WGPUFragmentState frag_transparent = frag;
    frag_transparent.targets = &color_target_transparent;

    // depthWriteEnabled stays True so the edge-detect pass (which samples
    // depth_view_ to find silhouette discontinuities) can see window
    // panes — leaving it False made transparent surfaces invisible to
    // the edge detector, so windows ended up as edge-less "framed holes"
    // and the edges of opaque geometry behind the glass painted through
    // at full intensity. Trade-off: overlapping transparent surfaces
    // become depth-test-occluded by the closer one, increasing order
    // sensitivity. For BIM glass (panes that don't overlap in screen
    // space) this is invisible; for scenes where it matters, the right
    // fix is OIT or sort-by-distance, not turning depth write off.
    WGPUDepthStencilState depth_transparent = depth;

    WGPURenderPipelineDescriptor rp_desc_t = rp_desc;
    rp_desc_t.label        = svFromCStr("ifcviewer-wgpu.main_pipeline_transparent");
    rp_desc_t.fragment     = &frag_transparent;
    rp_desc_t.depthStencil = &depth_transparent;

    main_pipeline_transparent_ =
        wgpuDeviceCreateRenderPipeline(device_, &rp_desc_t);
    if (!main_pipeline_transparent_) {
        Log::warn() << "wgpu main transparent render pipeline creation failed";
        return false;
    }

    // ---- Per-frame uniform buffer ---------------------------------------
    WGPUBufferDescriptor fb_desc = {};
    fb_desc.size  = sizeof(FrameUniforms);
    fb_desc.usage = WGPUBufferUsage_Uniform | WGPUBufferUsage_CopyDst;
    fb_desc.label = svFromCStr("ifcviewer-wgpu.frame_uniform");
    frame_uniform_buffer_ = wgpuDeviceCreateBuffer(device_, &fb_desc);

    // frame_bind_group_ is built lazily once we have a selection_flags_
    // buffer to bind alongside the uniform — ensureSelectionFlagsBuffer
    // handles both the first creation and any subsequent resize.

    return true;
}

void ViewportCore::ensureSelectionFlagsBuffer() {
    // Round up to at least 64 entries (256 B — minimum useful storage) and
    // grow geometrically when next_object_id_ outruns the current capacity.
    const uint32_t needed = std::max<uint32_t>(next_object_id_, 64);
    if (selection_flags_buffer_ && selection_flags_capacity_ >= needed) {
        if (!frame_bind_group_) {
            // First-time bind group creation after the buffer exists.
            // (Should always be true here.)
        } else {
            return;
        }
    }

    // (Re)allocate. Geometric grow so we don't recreate every frame as a
    // big scene streams in.
    uint32_t new_cap = selection_flags_capacity_;
    if (new_cap < 64) new_cap = 64;
    while (new_cap < needed) new_cap *= 2;

    if (!selection_flags_buffer_ || selection_flags_capacity_ < new_cap) {
        if (selection_flags_buffer_) {
            wgpuBufferRelease(selection_flags_buffer_);
            selection_flags_buffer_ = nullptr;
        }
        WGPUBufferDescriptor sb = {};
        sb.size  = uint64_t(new_cap) * sizeof(uint32_t);
        sb.usage = WGPUBufferUsage_Storage | WGPUBufferUsage_CopyDst;
        sb.label = svFromCStr("ifcviewer-wgpu.selection_flags");
        selection_flags_buffer_   = wgpuDeviceCreateBuffer(device_, &sb);
        selection_flags_capacity_ = new_cap;
        // Initialise to zero so any unused range reads as "not selected".
        // wgpuQueueWriteBuffer with a small zero block is enough; the rest
        // is created as zero-initialised by wgpu per the spec.
    }

    // Rebuild the frame bind group against the (possibly new) buffer.
    if (frame_bind_group_) {
        wgpuBindGroupRelease(frame_bind_group_);
        frame_bind_group_ = nullptr;
    }
    WGPUBindGroupEntry fbg_entries[2] = {};
    fbg_entries[0].binding = 0;
    fbg_entries[0].buffer  = frame_uniform_buffer_;
    fbg_entries[0].size    = sizeof(FrameUniforms);
    fbg_entries[1].binding = 1;
    fbg_entries[1].buffer  = selection_flags_buffer_;
    fbg_entries[1].size    = WGPU_WHOLE_SIZE;
    WGPUBindGroupDescriptor fbg_desc = {};
    fbg_desc.layout     = frame_bgl_;
    fbg_desc.entryCount = 2;
    fbg_desc.entries    = fbg_entries;
    fbg_desc.label      = svFromCStr("ifcviewer-wgpu.frame_bind_group");
    frame_bind_group_ = wgpuDeviceCreateBindGroup(device_, &fbg_desc);

    // Force a re-upload of the flags into the (possibly new) buffer.
    selection_flags_scratch_.assign(selection_flags_capacity_, 0);
    selection_.fillFlagsArray(selection_flags_scratch_, selection_flags_capacity_);
    wgpuQueueWriteBuffer(queue_, selection_flags_buffer_, 0,
                         selection_flags_scratch_.data(),
                         selection_flags_scratch_.size() * sizeof(uint32_t));
    selection_.markClean();
}

void ViewportCore::uploadSelectionFlagsIfDirty() {
    if (!selection_.dirty() || !selection_flags_buffer_) return;
    selection_flags_scratch_.assign(selection_flags_capacity_, 0);
    selection_.fillFlagsArray(selection_flags_scratch_, selection_flags_capacity_);
    wgpuQueueWriteBuffer(queue_, selection_flags_buffer_, 0,
                         selection_flags_scratch_.data(),
                         selection_flags_scratch_.size() * sizeof(uint32_t));
    selection_.markClean();
}
