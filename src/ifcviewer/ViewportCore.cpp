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

// wgpu-native extensions (log callback, MULTI_DRAW_INDIRECT). The web
// build (emdawnwebgpu / Dawn) doesn't ship this header — validation
// errors there go to the browser console, so the log-callback path
// simply compiles out under __EMSCRIPTEN__.
#if !defined(__EMSCRIPTEN__)
#  include <webgpu/wgpu.h>
#endif

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

void ViewportCore::updateFrameUniforms() {
    Eigen::Matrix4f view, proj;
    buildViewProj(view, proj);

    const Eigen::Matrix4f view_proj = proj * view;

    FrameUniforms u = {};
    std::memcpy(u.view_proj, view_proj.data(), 16 * sizeof(float));

    // Values match the GL viewport's main fragment shader so a side-by-side
    // diff of the two backends only shows what the wgpu pipeline has yet to
    // implement (edge silhouette pass, MSAA polish, etc.) — not lighting
    // model differences. Key + fill are ~unit-length, ~120° apart.
    Eigen::Vector3f L( 0.3f,  0.5f, 0.8f); L.normalize();
    Eigen::Vector3f F(-0.3f, -0.5f, 0.8f); F.normalize();
    u.light_dir[0] = L.x(); u.light_dir[1] = L.y(); u.light_dir[2] = L.z(); u.light_dir[3] = 0;
    u.fill_dir [0] = F.x(); u.fill_dir [1] = F.y(); u.fill_dir [2] = F.z(); u.fill_dir [3] = 0;
    u.sky_color   [0] = 0.55f; u.sky_color   [1] = 0.60f; u.sky_color   [2] = 0.70f;
    u.ground_color[0] = 0.35f; u.ground_color[1] = 0.32f; u.ground_color[2] = 0.28f;

    // Pack active section planes. `is_section_clipped` (WGSL) reads
    // u.clip_count and u.clip_planes[0..clip_count) and discards
    // fragments on the positive side.
    const int n = std::min<int>(int(section_planes_.size()), kMaxSectionPlanes);
    u.clip_count = n;
    for (int i = 0; i < n; ++i) {
        const SectionPlane& p = section_planes_[i];
        u.clip_planes[i][0] = p.n.x();
        u.clip_planes[i][1] = p.n.y();
        u.clip_planes[i][2] = p.n.z();
        u.clip_planes[i][3] = p.d;
    }
    u.xray_alpha_cap = xray_alpha_cap_;
    u._pad_xray[0] = u._pad_xray[1] = u._pad_xray[2] = 0.0f;

    wgpuQueueWriteBuffer(queue_, frame_uniform_buffer_, 0, &u, sizeof(u));
}

// ===========================================================================
// Lifecycle (#84-l): initWgpu + probeAndCreatePool + shutdown
// ===========================================================================

namespace {
// String-view → std::string for log output. WGPU_STRLEN is the
// sentinel meaning "nul-terminated", in which case strlen() gives the
// length.
std::string svToStr(WGPUStringView s) {
    if (!s.data) return {};
    const std::size_t len = (s.length == WGPU_STRLEN)
                                ? std::strlen(s.data)
                                : s.length;
    return std::string(s.data, len);
}

#if !defined(__EMSCRIPTEN__)
// wgpu-native callback: route every log line to Log::warn / Log::info
// so backend init problems surface in the console instead of being
// swallowed by the native runtime. Not available on emdawnwebgpu —
// see the include guard above.
void onWgpuLog(WGPULogLevel level, WGPUStringView message, void* /*userdata*/) {
    const std::string m = svToStr(message);
    switch (level) {
        case WGPULogLevel_Error: Log::warn() << "[wgpu err] "   << m; break;
        case WGPULogLevel_Warn:  Log::warn() << "[wgpu warn] "  << m; break;
        case WGPULogLevel_Info:  Log::info() << "[wgpu info] "  << m; break;
        case WGPULogLevel_Debug: Log::info() << "[wgpu dbg] "   << m; break;
        case WGPULogLevel_Trace: Log::info() << "[wgpu trace] " << m; break;
        default: break;
    }
}
#endif

// Per-device uncaptured-error callback. Validation failures land here
// when no error scope is open. Surfacing them into Log::warn makes
// otherwise-silent driver complaints attributable.
void onUncapturedError(WGPUDevice const* /*device*/,
                       WGPUErrorType type, WGPUStringView message,
                       void* /*ud1*/, void* /*ud2*/) {
    Log::warn() << "[wgpu device error " << int(type) << "] " << svToStr(message);
}
} // namespace

bool ViewportCore::probeAndCreatePool() {
    // Discover the largest single buffer the runtime will grant. Each
    // attempt sits inside OOM + Validation error scopes so a failed
    // allocation doesn't surface as a noisy uncaptured-error warning.
    WGPULimits device_limits = {};
    wgpuDeviceGetLimits(device_, &device_limits);

    constexpr uint64_t MIN_POOL_CAPACITY = 64ull * 1024 * 1024;
    constexpr uint64_t MAX_PROBE_START   = 4ull * 1024 * 1024 * 1024;
    uint64_t try_size = std::min<uint64_t>(device_limits.maxBufferSize,
                                           MAX_PROBE_START);
    if (try_size < MIN_POOL_CAPACITY) try_size = MIN_POOL_CAPACITY;

    const WGPUBufferUsage pool_usage = WGPUBufferUsage_Storage
                                     | WGPUBufferUsage_CopyDst;

    while (try_size >= MIN_POOL_CAPACITY) {
        wgpuDevicePushErrorScope(device_, WGPUErrorFilter_Validation);
        wgpuDevicePushErrorScope(device_, WGPUErrorFilter_OutOfMemory);

        WGPUBufferDescriptor desc = {};
        desc.usage             = pool_usage;
        desc.size              = try_size;
        desc.label.data        = "ifcviewer-wgpu.pool_probe";
        desc.label.length      = std::strlen("ifcviewer-wgpu.pool_probe");
        WGPUBuffer probe_buf   = wgpuDeviceCreateBuffer(device_, &desc);

        struct PopResult { bool done = false; bool error = false; };
        auto pop = [&](PopResult& pr) {
            WGPUPopErrorScopeCallbackInfo pcb = {};
            pcb.mode = WGPUCallbackMode_AllowProcessEvents;
            pcb.callback = [](WGPUPopErrorScopeStatus, WGPUErrorType type,
                              WGPUStringView, void* ud1, void* /*ud2*/) {
                auto* p = static_cast<PopResult*>(ud1);
                p->done = true;
                p->error = (type != WGPUErrorType_NoError);
            };
            pcb.userdata1 = &pr;
            wgpuDevicePopErrorScope(device_, pcb);
            while (!pr.done) wgpuInstanceProcessEvents(instance_);
        };
        PopResult oom_pop, validation_pop;
        pop(oom_pop);
        pop(validation_pop);

        if (probe_buf) wgpuBufferRelease(probe_buf);
        if (probe_buf && !oom_pop.error && !validation_pop.error) {
            pool_.configure(instance_, device_, pool_usage, try_size,
                            "ifcviewer-wgpu.pool");
            Log::info() << "wgpu: pool per-sub-buffer capacity = "
                        << (try_size / (1024 * 1024)) << " MB"
                        << " (device maxBufferSize = "
                        << (device_limits.maxBufferSize / (1024 * 1024))
                        << " MB); pool will grow on demand";
            return true;
        }
        try_size /= 2;
    }

    Log::warn() << "wgpu: pool probe found no allocatable size >= "
                << (MIN_POOL_CAPACITY / (1024 * 1024)) << " MB";
    return false;
}

bool ViewportCore::initWgpu(bool web_limits) {
#if !defined(__EMSCRIPTEN__)
    wgpuSetLogCallback(onWgpuLog, nullptr);
    wgpuSetLogLevel(WGPULogLevel_Warn);
#endif

    instance_ = wgpuCreateInstance(nullptr);
    if (!instance_) {
        Log::warn() << "wgpuCreateInstance returned null";
        return false;
    }

    // Surface comes from the host (X11/HWND/CAMetalLayer on desktop;
    // Emscripten canvas selector on web).
    surface_ = host_->createSurface(instance_);
    if (!surface_) {
        Log::warn() << "host createSurface returned null";
        return false;
    }

    // ---- Async request adapter -------------------------------------------
    struct AdapterReq { WGPUAdapter adapter = nullptr; bool done = false; bool ok = false; };
    AdapterReq areq;

    WGPURequestAdapterOptions adapter_opts = {};
    adapter_opts.compatibleSurface = surface_;
    adapter_opts.powerPreference   = WGPUPowerPreference_HighPerformance;

    WGPURequestAdapterCallbackInfo acb = {};
    acb.mode      = WGPUCallbackMode_AllowProcessEvents;
    acb.callback  = [](WGPURequestAdapterStatus status, WGPUAdapter adapter,
                       WGPUStringView message, void* ud1, void* /*ud2*/) {
        auto* r = static_cast<AdapterReq*>(ud1);
        r->done = true;
        if (status == WGPURequestAdapterStatus_Success) {
            r->adapter = adapter;
            r->ok = true;
        } else {
            Log::warn() << "RequestAdapter failed: " << svToStr(message);
        }
    };
    acb.userdata1 = &areq;

    wgpuInstanceRequestAdapter(instance_, &adapter_opts, acb);
    while (!areq.done) wgpuInstanceProcessEvents(instance_);
    if (!areq.ok) return false;
    adapter_ = areq.adapter;

    // ---- Async request device --------------------------------------------
    struct DeviceReq { WGPUDevice device = nullptr; bool done = false; bool ok = false; };
    DeviceReq dreq;

    WGPULimits adapter_limits = {};
    wgpuAdapterGetLimits(adapter_, &adapter_limits);

    WGPULimits web_floor_limits = adapter_limits;
    web_floor_limits.maxStorageBufferBindingSize = 128ull * 1024 * 1024;
    web_floor_limits.maxBufferSize               = 256ull * 1024 * 1024;

    WGPUDeviceDescriptor dev_desc = {};
    dev_desc.requiredLimits = web_limits ? &web_floor_limits : &adapter_limits;
    if (web_limits) {
        Log::info() << "wgpu --web-limits: requesting browser-floor limits "
                       "(maxStorageBufferBindingSize=128MB, maxBufferSize=256MB)";
    }
    dev_desc.uncapturedErrorCallbackInfo.callback = onUncapturedError;

    WGPURequestDeviceCallbackInfo dcb = {};
    dcb.mode     = WGPUCallbackMode_AllowProcessEvents;
    dcb.callback = [](WGPURequestDeviceStatus status, WGPUDevice device,
                      WGPUStringView message, void* ud1, void* /*ud2*/) {
        auto* r = static_cast<DeviceReq*>(ud1);
        r->done = true;
        if (status == WGPURequestDeviceStatus_Success) {
            r->device = device;
            r->ok = true;
        } else {
            Log::warn() << "RequestDevice failed: " << svToStr(message);
        }
    };
    dcb.userdata1 = &dreq;

    wgpuAdapterRequestDevice(adapter_, &dev_desc, dcb);
    while (!dreq.done) wgpuInstanceProcessEvents(instance_);
    if (!dreq.ok) return false;
    device_ = dreq.device;
    queue_  = wgpuDeviceGetQueue(device_);

    if (!probeAndCreatePool()) {
        Log::warn() << "wgpu: streaming pool probe failed; cannot start";
        return false;
    }
    streaming_thread_.start();

    WGPUSurfaceCapabilities caps = {};
    if (wgpuSurfaceGetCapabilities(surface_, adapter_, &caps) != WGPUStatus_Success
        || caps.formatCount == 0) {
        Log::warn() << "wgpuSurfaceGetCapabilities returned no formats";
        return false;
    }
    surface_format_ = caps.formats[0];
    wgpuSurfaceCapabilitiesFreeMembers(caps);

    Log::info() << "wgpu init OK; surface format = " << int(surface_format_);
    return true;
}

void ViewportCore::shutdown() {
    // Stop streaming first so no late results land in the pool after
    // we've torn down model state. Worker drains its queue then joins.
    streaming_thread_.stop();

    for (auto& [mid, m] : models_gpu_) releaseWgpuModelGpuData(m, pool_);
    models_gpu_.clear();

    if (frame_bind_group_)        { wgpuBindGroupRelease(frame_bind_group_);          frame_bind_group_ = nullptr; }
    if (frame_uniform_buffer_)    { wgpuBufferRelease(frame_uniform_buffer_);         frame_uniform_buffer_ = nullptr; }
    if (selection_flags_buffer_)  { wgpuBufferRelease(selection_flags_buffer_);       selection_flags_buffer_ = nullptr; }
    selection_flags_capacity_ = 0;
    if (main_pipeline_)              { wgpuRenderPipelineRelease(main_pipeline_);             main_pipeline_ = nullptr; }
    if (main_pipeline_transparent_)  { wgpuRenderPipelineRelease(main_pipeline_transparent_); main_pipeline_transparent_ = nullptr; }
    if (main_shader_module_)   { wgpuShaderModuleRelease(main_shader_module_);    main_shader_module_ = nullptr; }
    if (pipeline_layout_)      { wgpuPipelineLayoutRelease(pipeline_layout_);     pipeline_layout_ = nullptr; }
    if (model_bgl_)            { wgpuBindGroupLayoutRelease(model_bgl_);          model_bgl_ = nullptr; }
    if (frame_bgl_)            { wgpuBindGroupLayoutRelease(frame_bgl_);          frame_bgl_ = nullptr; }

    // Destroy the streaming pool while device_ is still alive — it owns
    // the underlying WGPUBuffer.
    pool_.destroy();

    if (queue_)    { wgpuQueueRelease(queue_);       queue_    = nullptr; }
    if (device_)   { wgpuDeviceRelease(device_);     device_   = nullptr; }
    if (adapter_)  { wgpuAdapterRelease(adapter_);   adapter_  = nullptr; }
    if (surface_)  { wgpuSurfaceRelease(surface_);   surface_  = nullptr; }
    if (instance_) { wgpuInstanceRelease(instance_); instance_ = nullptr; }
    wgpu_initialized_   = false;
    surface_configured_ = false;
}

// ===========================================================================
// Chunk residency (#84-n): buildChunkBindGroup + applyStreamedChunk +
// loadChunkBytesAndUploadGpu + unloadChunk + makeChunkRequest +
// computeMeshLocalVolumeQuantised
// ===========================================================================

#include "StreamingLoader.h"

namespace {

// Pure function of the mesh's local AABB + index list. Computes the
// signed-tetrahedra-volume sum (divergence theorem), takes its absolute
// value, divides by 6 — gives the mesh-local volume in m³. Side effect:
// if `out_tris` is non-null, populates it with dequantised positions +
// index copy so the Area / Volume tool can later refine to a single
// triangle. Stays as a free helper because applyStreamedChunk is the
// only call site.
double computeMeshLocalVolumeQuantised(
        const MeshInfo& mesh,
        const std::uint8_t* vbase, const std::uint32_t* ibase,
        std::uint32_t n_indices,
        ModelGpuData::MeshTriangles* out_tris) {
    if (n_indices < 3 || vbase == nullptr || ibase == nullptr) return 0.0;
    const float ax = mesh.local_aabb_min[0];
    const float ay = mesh.local_aabb_min[1];
    const float az = mesh.local_aabb_min[2];
    const float ex = mesh.local_aabb_max[0] - ax;
    const float ey = mesh.local_aabb_max[1] - ay;
    const float ez = mesh.local_aabb_max[2] - az;
    const float inv_q = 1.0f / 65535.0f;

    std::vector<float> positions;
    positions.resize(std::size_t(mesh.vertex_count) * 3);
    for (std::uint32_t v = 0; v < mesh.vertex_count; ++v) {
        const std::uint8_t* p = vbase
            + std::size_t(v) * INSTANCED_VERTEX_STRIDE_BYTES;
        std::uint16_t qx, qy, qz;
        std::memcpy(&qx, p + 0, 2);
        std::memcpy(&qy, p + 2, 2);
        std::memcpy(&qz, p + 4, 2);
        positions[3 * v + 0] = ax + float(qx) * inv_q * ex;
        positions[3 * v + 1] = ay + float(qy) * inv_q * ey;
        positions[3 * v + 2] = az + float(qz) * inv_q * ez;
    }

    double sum = 0.0;
    for (std::uint32_t i = 0; i + 2 < n_indices; i += 3) {
        const std::uint32_t i0 = ibase[i + 0];
        const std::uint32_t i1 = ibase[i + 1];
        const std::uint32_t i2 = ibase[i + 2];
        if (i0 >= mesh.vertex_count || i1 >= mesh.vertex_count
         || i2 >= mesh.vertex_count) continue;
        const float* p0 = &positions[3 * i0];
        const float* p1 = &positions[3 * i1];
        const float* p2 = &positions[3 * i2];
        const double cx = double(p1[1]) * p2[2] - double(p1[2]) * p2[1];
        const double cy = double(p1[2]) * p2[0] - double(p1[0]) * p2[2];
        const double cz = double(p1[0]) * p2[1] - double(p1[1]) * p2[0];
        sum += double(p0[0]) * cx + double(p0[1]) * cy + double(p0[2]) * cz;
    }

    if (out_tris) {
        out_tris->positions = std::move(positions);
        out_tris->indices.assign(ibase, ibase + n_indices);
    }
    return std::abs(sum) / 6.0;
}

} // namespace

void ViewportCore::buildChunkBindGroup(ModelGpuData& m, std::size_t chunk_idx) {
    if (chunk_idx >= m.chunks.size()) return;
    auto& c = m.chunks[chunk_idx];
    if (c.bind_group) {
        wgpuBindGroupRelease(c.bind_group);
        c.bind_group = nullptr;
    }
    if (!c.vertex_slice.valid() || !c.index_slice.valid()
        || !c.visible_draws_buffer || !c.prefix_sums_buffer || !c.per_chunk_uniform
        || !m.mesh_storage || !m.instance_storage) {
        return;
    }

    WGPUBindGroupEntry entries[7] = {};
    // vertices and indices live in the shared pool. Each slice carries
    // the specific sub-buffer it landed in (the pool may span several
    // when scenes exceed wgpu's single-buffer cap). The other entries
    // are still per-chunk small buffers (visible_draws/prefix_sums/uniform)
    // or per-model (mesh/instance).
    entries[0].binding = 0;
    entries[0].buffer  = c.vertex_slice.buffer;
    entries[0].offset  = c.vertex_slice.offset;
    entries[0].size    = c.vertex_slice.size;
    entries[1].binding = 1;
    entries[1].buffer  = m.mesh_storage;
    entries[1].size    = WGPU_WHOLE_SIZE;
    entries[2].binding = 2;
    entries[2].buffer  = m.instance_storage;
    entries[2].size    = WGPU_WHOLE_SIZE;
    entries[3].binding = 3;
    entries[3].buffer  = c.index_slice.buffer;
    entries[3].offset  = c.index_slice.offset;
    entries[3].size    = c.index_slice.size;
    entries[4].binding = 4;
    entries[4].buffer  = c.visible_draws_buffer;
    entries[4].size    = WGPU_WHOLE_SIZE;
    entries[5].binding = 5;
    entries[5].buffer  = c.prefix_sums_buffer;
    entries[5].size    = WGPU_WHOLE_SIZE;
    entries[6].binding = 6;
    entries[6].buffer  = c.per_chunk_uniform;
    entries[6].size    = 16;

    WGPUBindGroupDescriptor desc = {};
    desc.layout     = model_bgl_;
    desc.entryCount = 7;
    desc.entries    = entries;
    desc.label      = svFromCStr("ifcviewer-wgpu.chunk_bind_group");
    c.bind_group = wgpuDeviceCreateBindGroup(device_, &desc);
}

bool ViewportCore::applyStreamedChunk(
        ModelGpuData& m, std::size_t chunk_idx,
        const std::vector<std::uint8_t>& vbytes,
        const std::vector<std::uint32_t>& idx) {
    auto& c = m.chunks[chunk_idx];

    c.vertex_slice = pool_.alloc(vbytes.size(), 256);
    if (!c.vertex_slice.valid()) return false;
    wgpuQueueWriteBuffer(queue_, c.vertex_slice.buffer,
                         c.vertex_slice.offset,
                         vbytes.data(), vbytes.size());
    m.vram_bytes_vbo += vbytes.size();

    if (!idx.empty()) {
        const std::size_t ibytes = idx.size() * sizeof(std::uint32_t);
        c.index_slice = pool_.alloc(ibytes, 256);
        if (!c.index_slice.valid()) {
            pool_.free(c.vertex_slice);
            m.vram_bytes_vbo -= c.vertex_slice.size;
            c.vertex_slice = {};
            return false;
        }
        wgpuQueueWriteBuffer(queue_, c.index_slice.buffer,
                             c.index_slice.offset,
                             idx.data(), ibytes);
        m.vram_bytes_ebo += ibytes;
    }

    buildChunkBindGroup(m, chunk_idx);
    c.is_resident      = true;
    c.is_loading       = false;
    c.loaded_frame_idx = streaming_frame_idx_;

    // Per-mesh alpha probe. Scan every vertex of every mesh in this chunk
    // for any alpha byte < 255 — fires the mesh_has_alpha flag the cull
    // classifier reads to route instances of this mesh to the transparent
    // pass. Done here (vs. once at sidecar bake time) because for the
    // streaming path the bytes only arrive now; the same code services
    // both the worker-result drain and the sync first-frame fallback.
    if (m.mesh_has_alpha.size() == m.meshes.size()) {
        for (std::uint32_t mi : c.mesh_ids) {
            if (mi >= m.meshes.size()) continue;
            const MeshInfo& mesh = m.meshes[mi];
            if (mesh.vertex_count == 0) continue;
            const std::size_t v_off =
                std::size_t(m.mesh_chunk_local_base_vertex[mi])
                * INSTANCED_VERTEX_STRIDE_BYTES;
            const std::size_t v_end = v_off
                + std::size_t(mesh.vertex_count) * INSTANCED_VERTEX_STRIDE_BYTES;
            if (v_end > vbytes.size()) continue;
            bool any_alpha = false;
            // Alpha byte sits in the high byte of the vertex's 3rd u32
            // (shader: `w2 >> 24`), i.e. offset 11 within the 12-byte
            // vertex record. See InstancedGeometry.h's vertex layout.
            for (std::uint32_t v = 0; v < mesh.vertex_count && !any_alpha; ++v) {
                const std::size_t a_off = v_off
                    + std::size_t(v) * INSTANCED_VERTEX_STRIDE_BYTES + 11;
                if (vbytes[a_off] < 255u) any_alpha = true;
            }
            m.mesh_has_alpha[mi] = any_alpha
                ? std::uint8_t(1) : std::uint8_t(0);
        }
    }

    // Mesh-local volumes for the meshes in this chunk. applyCachedModel
    // left them zero because the bytes weren't in memory yet; the first
    // chunk to deliver each mesh fills it in.
    bool filled_volume = false;
    if (!m.mesh_local_volumes.empty() && !idx.empty()) {
        for (std::uint32_t mi : c.mesh_ids) {
            if (mi >= m.meshes.size() || mi >= m.mesh_local_volumes.size()) continue;
            if (m.mesh_local_volumes[mi] != 0.0) continue;
            const MeshInfo& mesh = m.meshes[mi];
            if (mesh.vertex_count == 0 || mesh.index_count < 3) continue;
            const std::size_t v_off =
                std::size_t(m.mesh_chunk_local_base_vertex[mi])
                * INSTANCED_VERTEX_STRIDE_BYTES;
            const std::size_t i_off = m.mesh_chunk_local_ebo_first_u32[mi];
            const std::size_t v_end = v_off
                + std::size_t(mesh.vertex_count) * INSTANCED_VERTEX_STRIDE_BYTES;
            if (v_end > vbytes.size()) continue;
            if (i_off + mesh.index_count > idx.size()) continue;
            ModelGpuData::MeshTriangles* tris =
                (mi < m.mesh_triangles_cache.size())
                    ? &m.mesh_triangles_cache[mi]
                    : nullptr;
            m.mesh_local_volumes[mi] = computeMeshLocalVolumeQuantised(
                mesh, vbytes.data() + v_off, idx.data() + i_off, mesh.index_count,
                tris);
            filled_volume = true;
        }
    }
    // Fire the tool-refresh callback once per apply if anything new filled
    // in. ViewportWindow wires this to its Volume-tool HUD; non-Qt hosts
    // leave the callback null (no-op).
    if (filled_volume && on_volume_dirty_) on_volume_dirty_();
    return true;
}

StreamingThread::Request ViewportCore::makeChunkRequest(
        const ModelGpuData& m, std::size_t chunk_idx,
        std::uint32_t model_id) {
    const auto& c = m.chunks[chunk_idx];
    StreamingThread::Request req;
    req.model_id              = model_id;
    req.chunk_idx             = chunk_idx;
    req.file_path             = m.streaming_file_path;
    req.vertex_section_offset = m.streaming_vertex_section_offset;
    req.index_section_offset  = m.streaming_index_section_offset;
    req.v_ranges.reserve(c.mesh_ids.size());
    req.i_ranges.reserve(c.mesh_ids.size());
    for (std::uint32_t mi : c.mesh_ids) {
        const MeshInfo& mesh = m.meshes[mi];
        const std::uint64_t v_bytes =
            std::uint64_t(mesh.vertex_count) * INSTANCED_VERTEX_STRIDE_BYTES;
        if (v_bytes > 0) {
            req.v_ranges.emplace_back(std::uint64_t(mesh.vbo_byte_offset), v_bytes);
        }
        if (mesh.index_count > 0) {
            req.i_ranges.emplace_back(
                std::uint64_t(mesh.ebo_byte_offset / sizeof(std::uint32_t)),
                std::uint64_t(mesh.index_count));
        }
    }
    // LOD1 indices second pass — matches the chunk-local packing order
    // (all LOD0 first, then LOD1) so the worker's concatenated index
    // result lands at the offsets recorded in
    // m.mesh_chunk_local_lod1_first_u32.
    for (std::uint32_t mi : c.mesh_ids) {
        const MeshInfo& mesh = m.meshes[mi];
        if (mesh.lod1_index_count == 0) continue;
        req.i_ranges.emplace_back(
            std::uint64_t(mesh.lod1_ebo_byte_offset / sizeof(std::uint32_t)),
            std::uint64_t(mesh.lod1_index_count));
    }
    return req;
}

bool ViewportCore::loadChunkBytesAndUploadGpu(ModelGpuData& m,
                                              std::size_t chunk_idx) {
    if (chunk_idx >= m.chunks.size()) return false;
    auto& c = m.chunks[chunk_idx];
    if (c.is_resident) return true;
    if (m.streaming_file_path.empty()) return false;

    // Synchronous fallback: build the request, do the disk read inline,
    // apply. Used only when the async path can't be — i.e. by the
    // screenshot test on first frame.
    StreamingThread::Request req = makeChunkRequest(m, chunk_idx, /*model_id*/ 0);

    std::vector<std::uint8_t>  vbytes;
    std::vector<std::uint32_t> idx;
    if (!req.v_ranges.empty()) {
        if (!readSidecarVertexRanges(req.file_path,
                                     req.vertex_section_offset,
                                     req.v_ranges, vbytes)) {
            Log::warn() << "[wgpu stream] failed to read vertex chunk "
                        << chunk_idx
                        << " (" << req.v_ranges.size() << " ranges, total "
                        << c.vertex_byte_size << " B)";
            return false;
        }
    }
    if (!req.i_ranges.empty()) {
        if (!readSidecarIndexRanges(req.file_path,
                                    req.index_section_offset,
                                    req.i_ranges, idx)) {
            Log::warn() << "[wgpu stream] failed to read index chunk "
                        << chunk_idx
                        << " (" << req.i_ranges.size() << " ranges, total "
                        << c.index_count << " indices)";
            return false;
        }
    }
    return applyStreamedChunk(m, chunk_idx, vbytes, idx);
}

void ViewportCore::unloadChunk(ModelGpuData& m, std::size_t chunk_idx) {
    if (chunk_idx >= m.chunks.size()) return;
    auto& c = m.chunks[chunk_idx];
    if (!c.is_resident) return;

    if (c.bind_group) {
        wgpuBindGroupRelease(c.bind_group);
        c.bind_group = nullptr;
    }
    if (c.vertex_slice.valid()) {
        m.vram_bytes_vbo -= c.vertex_slice.size;
        pool_.free(c.vertex_slice);
        c.vertex_slice = {};
    }
    if (c.index_slice.valid()) {
        m.vram_bytes_ebo -= c.index_slice.size;
        pool_.free(c.index_slice);
        c.index_slice = {};
    }
    // Clear per-frame visibility so the chunk doesn't get re-rendered or
    // re-evicted on the same frame; cull will set it again next time
    // the chunk falls in the frustum.
    c.total_visible_draws    = 0;
    c.total_visible_vertices = 0;
    c.is_resident = false;
}
