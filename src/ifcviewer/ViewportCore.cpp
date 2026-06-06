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

// ===========================================================================
// Streaming driver (#84-o): driveStreamingLoads
// ===========================================================================

#include <filesystem>
#include <set>

namespace {
// Extract the file's base name (no extension, no parent dirs) for log
// readability — replaces the previous QFileInfo(...).completeBaseName().
std::string pathStem(const std::string& path) {
    if (path.empty()) return {};
    return std::filesystem::path(path).stem().string();
}
} // namespace

void ViewportCore::driveStreamingLoads() {
    // Bump LRU clock once per call. Resident-and-visible chunks get
    // stamped with this value below; the evictor uses it to find the
    // least-recently-visible non-visible resident chunk.
    ++streaming_frame_idx_;

    // Refresh per-chunk frame state. (a) LRU stamp on frustum-visible
    // residents (HiZ flicker can't un-stamp them; cull-with-HiZ would
    // thrash the LRU). (b) EMA-smoothed visibility_history: how often
    // the chunk has *actually* contributed pixels (post-HiZ) over the
    // last ~30 frames.
    constexpr float HISTORY_ALPHA = 1.0f / 30.0f;
    for (auto& [mid, m] : models_gpu_) {
        if (m.hidden) continue;
        for (auto& c : m.chunks) {
            if (c.is_resident && c.frustum_visible_count > 0) {
                c.last_visible_frame_idx = streaming_frame_idx_;
            }
            const float current = (c.total_visible_draws > 0) ? 1.0f : 0.0f;
            c.visibility_history =
                c.visibility_history * (1.0f - HISTORY_ALPHA)
              + current * HISTORY_ALPHA;
        }
    }

    // Build the camera's view-projection for the diagnostic dump below.
    Eigen::Matrix4f v_mat, p_mat;
    buildViewProj(v_mat, p_mat);
    const Eigen::Matrix4f vp_mat = p_mat * v_mat;

    // chunk.current_priority was accumulated during cullModelCpuCompute
    // (one add per frustum-passing instance). No standalone walk needed
    // here; the candidate/resident priority lambdas just read it.
    auto chunk_screen_area_px = [&](const ModelGpuData::Chunk& c) -> float {
        return c.current_priority;
    };

    // Resident chunks: contribution × visibility_history (floored), so
    // chunks that don't actually render lose priority over time and
    // become evictable. Candidates: pure contribution — best-case
    // estimate. Newly-loaded chunks get a GRACE_FRAMES grace period at
    // full max-history factor to stop equal-priority swap loops.
    constexpr float    HISTORY_FLOOR = 0.05f;
    constexpr std::uint64_t GRACE_FRAMES  = 30;
    auto resident_priority = [&](const ModelGpuData::Chunk& c) -> float {
        const std::uint64_t age = streaming_frame_idx_ - c.loaded_frame_idx;
        const float vis = (age < GRACE_FRAMES)
            ? 1.0f
            : std::max(c.visibility_history, HISTORY_FLOOR);
        return chunk_screen_area_px(c) * vis;
    };
    auto candidate_priority = [&](const ModelGpuData::Chunk& c) -> float {
        return chunk_screen_area_px(c);
    };

    // Per-frame load budget. 4 chunks/frame × 60fps ingests 240/sec —
    // a 100-model scene fully resides in ~1s.
    constexpr int MAX_STREAMING_LOADS_PER_FRAME = 4;
    int loads = 0;
    bool more_pending = false;

    // Reset per-frame counters used by WGPU_STREAM_DEBUG output.
    streaming_candidates_this_frame_    = 0;
    streaming_evictions_lru_this_frame_ = 0;
    streaming_evictions_pri_this_frame_ = 0;
    streaming_drained_this_frame_       = 0;
    streaming_blocked_oom_this_frame_   = 0;

    auto pool_can_fit = [&](std::uint64_t bytes) -> bool {
        if (pool_.largest_free_run_bytes() >= bytes) return true;
        if (pool_.can_grow() && pool_.next_growth_size_bytes() >= bytes) return true;
        return false;
    };

    // Phase-1 evictor: drop the LRU non-visible resident chunk. Skips
    // chunks stamped on streaming_frame_idx_ to avoid yanking what cull
    // just marked visible.
    auto evict_one_lru = [&]() -> bool {
        ModelGpuData* victim_m = nullptr;
        std::size_t   victim_ci = 0;
        std::uint64_t victim_lru = std::numeric_limits<std::uint64_t>::max();
        for (auto& [mid, m] : models_gpu_) {
            for (std::size_t ci = 0; ci < m.chunks.size(); ++ci) {
                auto& c = m.chunks[ci];
                if (!c.is_resident) continue;
                if (c.last_visible_frame_idx == streaming_frame_idx_) continue;
                if (c.last_visible_frame_idx < victim_lru) {
                    victim_lru = c.last_visible_frame_idx;
                    victim_m   = &m;
                    victim_ci  = ci;
                }
            }
        }
        if (!victim_m) return false;
        unloadChunk(*victim_m, victim_ci);
        ++streaming_evictions_lru_this_frame_;
        return true;
    };

    // Phase-2 evictor: when every resident is visible-this-frame but a
    // higher-priority candidate needs room, drop the lowest-priority
    // resident provided the candidate's contribution is meaningfully
    // bigger (2× area hysteresis stops oscillation).
    constexpr float EVICT_PRIORITY_RATIO = 2.0f;
    // WGPU_STREAM_EVICT_LOG=1 — log every priority-eviction with the
    // (candidate, victim) pair and detect direct A→B→A 2-cycles.
    static const bool evict_log =
        std::getenv("WGPU_STREAM_EVICT_LOG") != nullptr;
    auto evict_lowest_priority_than = [&](std::uint32_t cand_mid,
                                          std::uint32_t cand_ci,
                                          float    cand_priority) -> bool {
        const float threshold = cand_priority / EVICT_PRIORITY_RATIO;
        ModelGpuData* victim_m  = nullptr;
        std::size_t   victim_ci = 0;
        float         victim_priority = threshold;
        for (auto& [mid, m] : models_gpu_) {
            for (std::size_t ci = 0; ci < m.chunks.size(); ++ci) {
                auto& c = m.chunks[ci];
                if (!c.is_resident) continue;
                const float p = resident_priority(c);
                if (p < victim_priority) {
                    victim_priority = p;
                    victim_m        = &m;
                    victim_ci       = ci;
                }
            }
        }
        if (!victim_m) return false;

        auto& victim = victim_m->chunks[victim_ci];

        if (evict_log) {
            const std::string cand_stem = pathStem(
                models_gpu_.at(cand_mid).streaming_file_path);
            const std::string vic_stem  = pathStem(victim_m->streaming_file_path);
            // 2-cycle detection: this victim was previously evicted by
            // THIS exact candidate — the smoking gun for a swap loop.
            const bool is_2_cycle =
                   victim.last_evicted_by_model_id == cand_mid
                && victim.last_evicted_by_chunk_idx == cand_ci
                && victim.load_count > 1;
            Log::info()
                << (is_2_cycle ? "[evict 2-cycle] " : "[evict] ")
                << "kicked chunk " << victim_ci
                << " of " << vic_stem
                << " (eff=" << int(victim_priority)
                << ", load_count=" << victim.load_count
                << ") for chunk " << cand_ci
                << " of " << cand_stem
                << " (pri=" << int(cand_priority)
                << ", threshold=" << int(threshold) << ")";
        }

        victim.last_evicted_by_model_id  = cand_mid;
        victim.last_evicted_by_chunk_idx = cand_ci;
        victim.last_evicted_by_priority  = cand_priority;
        victim.last_evicted_frame_idx    = streaming_frame_idx_;

        unloadChunk(*victim_m, victim_ci);
        ++streaming_evictions_pri_this_frame_;
        return true;
    };

    constexpr std::uint64_t BLOCKED_COOLDOWN_FRAMES = 180;

    // ---- Drain worker results -------------------------------------------
    {
        auto results = streaming_thread_.drainResults();
        for (auto& res : results) {
            auto it = models_gpu_.find(res.model_id);
            if (it == models_gpu_.end()) continue;  // model unloaded
            auto& m = it->second;
            if (res.chunk_idx >= m.chunks.size()) continue;
            auto& c = m.chunks[res.chunk_idx];
            c.is_loading = false;
            if (!res.success) {
                Log::warn() << "[wgpu stream] worker read failed for model "
                            << res.model_id << " chunk " << res.chunk_idx;
                continue;
            }
            if (!applyStreamedChunk(m, res.chunk_idx, res.vbytes, res.idx)) {
                c.blocked_cooldown_until_frame_idx =
                    streaming_frame_idx_ + BLOCKED_COOLDOWN_FRAMES;
                if (evict_log) {
                    Log::info()
                        << "[blocked-apply] chunk " << res.chunk_idx
                        << " of " << pathStem(m.streaming_file_path)
                        << " — pool OOM at apply, fetched bytes discarded"
                        << " — cooldown " << BLOCKED_COOLDOWN_FRAMES << "f";
                }
                continue;
            }
            ++loads;
            ++streaming_drained_this_frame_;
            ++c.load_count;
            c.last_visible_frame_idx = streaming_frame_idx_;
            // Thrash watch — fire once per power-of-≈3 threshold.
            const std::uint32_t lc = c.load_count;
            if (lc == 3 || lc == 10 || lc == 30 || lc == 100
             || (lc > 100 && (lc % 100) == 0)) {
                Log::info()
                    << "[stream thrash] chunk " << res.chunk_idx
                    << " of " << pathStem(m.streaming_file_path)
                    << " loaded " << lc << "x -- pool saturated?";
            }
        }
    }

    // ---- Enqueue new requests -------------------------------------------
    struct Candidate {
        ModelGpuData* m;
        std::size_t   ci;
        std::uint32_t mid;
        float         priority;
    };
    std::vector<Candidate> candidates;
    candidates.reserve(64);
    for (auto& [mid, m] : models_gpu_) {
        if (m.streaming_file_path.empty() || m.hidden) continue;
        for (std::size_t ci = 0; ci < m.chunks.size(); ++ci) {
            auto& c = m.chunks[ci];
            if (c.is_resident)                       continue;
            if (c.is_loading)                        continue;
            if (c.frustum_visible_count == 0)        continue;
            if (c.blocked_cooldown_until_frame_idx > streaming_frame_idx_) continue;
            candidates.push_back({&m, ci, mid, candidate_priority(c)});
        }
    }
    streaming_candidates_this_frame_ = int(candidates.size());
    std::sort(candidates.begin(), candidates.end(),
              [](const Candidate& a, const Candidate& b) {
                  return a.priority > b.priority;
              });

    int enqueued = 0;
    for (const Candidate& cand : candidates) {
        if (enqueued >= MAX_STREAMING_LOADS_PER_FRAME) {
            more_pending = true;
            break;
        }
        auto& c = cand.m->chunks[cand.ci];

        const std::uint64_t need = c.vertex_byte_size
                                 + c.index_count * sizeof(std::uint32_t);
        while (!pool_can_fit(c.vertex_byte_size)
               || (c.index_count > 0
                   && !pool_can_fit(c.index_count * sizeof(std::uint32_t)))
               || pool_.total_free_bytes() < need) {
            if (evict_one_lru())                                                continue;
            if (evict_lowest_priority_than(cand.mid, std::uint32_t(cand.ci),
                                           cand.priority))                      continue;
            break;
        }
        if (!pool_can_fit(c.vertex_byte_size)
            || (c.index_count > 0
                && !pool_can_fit(c.index_count * sizeof(std::uint32_t)))) {
            ++streaming_blocked_oom_this_frame_;
            c.blocked_cooldown_until_frame_idx =
                streaming_frame_idx_ + BLOCKED_COOLDOWN_FRAMES;
            if (evict_log) {
                const std::uint64_t v_bytes = c.vertex_byte_size;
                const std::uint64_t i_bytes = c.index_count * sizeof(std::uint32_t);
                const double mb = 1.0 / (1024.0 * 1024.0);
                Log::info()
                    << "[blocked] chunk " << cand.ci
                    << " of " << pathStem(cand.m->streaming_file_path)
                    << " (pri=" << int(cand.priority)
                    << ") -- needs v=" << double(v_bytes) * mb
                    << " MB + i=" << double(i_bytes) * mb
                    << " MB; pool largest_free="
                    << double(pool_.largest_free_run_bytes()) * mb
                    << " MB total_free="
                    << double(pool_.total_free_bytes()) * mb
                    << " MB can_grow=" << (pool_.can_grow() ? "Y" : "N")
                    << " -- cooldown " << BLOCKED_COOLDOWN_FRAMES << "f";
            }
            more_pending = true;
            continue;
        }

        // Sync fallback when a screenshot is pending: the deferred-
        // capture wait would let the window manager re-layout the
        // window while we wait, capturing at the wrong size. With sync
        // loads the chunk appears in the same frame we enqueue.
        if (!pending_screenshot_path_.empty()) {
            if (loadChunkBytesAndUploadGpu(*cand.m, cand.ci)) {
                ++enqueued;
                c.last_visible_frame_idx = streaming_frame_idx_;
            }
            continue;
        }

        if (streaming_thread_.enqueue(makeChunkRequest(*cand.m, cand.ci, cand.mid))) {
            c.is_loading = true;
            ++enqueued;
        }
    }
    loads += enqueued;
    if (loads > 0 || streaming_thread_.inFlightApprox() > 0) host_->requestFrame();

    streaming_loads_this_frame_ = loads;
    streaming_more_pending_     = more_pending;

    // Click-and-track diagnostic. When the user picked an object, we
    // noted which chunk holds it. If that chunk has just transitioned
    // resident→evicted, dump the priority + pool state at the moment
    // of loss.
    if (tracked_chunk_idx_ != SIZE_MAX) {
        auto it = models_gpu_.find(tracked_chunk_mid_);
        if (it != models_gpu_.end()
            && tracked_chunk_idx_ < it->second.chunks.size()) {
            const auto& m = it->second;
            const auto& c = m.chunks[tracked_chunk_idx_];
            if (tracked_was_resident_ && !c.is_resident) {
                const double mb = 1.0 / (1024.0 * 1024.0);
                const float my_area  = chunkScreenAreaPx(c, vp_mat);
                const std::uint64_t my_bytes = c.vertex_byte_size
                                             + c.index_count * sizeof(std::uint32_t);
                Log::info()
                    << "[track] chunk " << tracked_chunk_idx_
                    << " (object " << tracked_object_id_
                    << ", model " << tracked_chunk_mid_
                    << ") EVICTED this frame";
                Log::info()
                    << "  area=" << int(my_area) << "px2"
                    << " frustum_vis=" << c.frustum_visible_count
                    << " hist=" << c.visibility_history
                    << " load_count=" << c.load_count
                    << " size=" << double(my_bytes) * mb << "MB";
                Log::info()
                    << "  chunk aabb "
                    << (c.aabb_max[0] - c.aabb_min[0]) << "x"
                    << (c.aabb_max[1] - c.aabb_min[1]) << "x"
                    << (c.aabb_max[2] - c.aabb_min[2]) << "m"
                    << " centre=("
                    << 0.5f * (c.aabb_min[0] + c.aabb_max[0]) << ","
                    << 0.5f * (c.aabb_min[1] + c.aabb_max[1]) << ","
                    << 0.5f * (c.aabb_min[2] + c.aabb_max[2]) << ")";
                Log::info()
                    << "  pool used="
                    << int(double(pool_.total_used_bytes()) * mb)
                    << "/"
                    << int(double(pool_.total_capacity_bytes()) * mb)
                    << "MB largest_free="
                    << double(pool_.largest_free_run_bytes()) * mb << "MB";
                Log::info()
                    << "  this-frame: cands=" << streaming_candidates_this_frame_
                    << " enq=" << enqueued
                    << " ev_lru=" << streaming_evictions_lru_this_frame_
                    << " ev_pri=" << streaming_evictions_pri_this_frame_
                    << " blocked=" << streaming_blocked_oom_this_frame_;

                struct Stat { std::uint32_t mid; std::size_t ci; float area; };
                std::vector<Stat> all;
                all.reserve(64);
                for (const auto& [mid2, m2] : models_gpu_) {
                    for (std::size_t ci2 = 0; ci2 < m2.chunks.size(); ++ci2) {
                        const auto& cc = m2.chunks[ci2];
                        if (cc.is_resident)                continue;
                        if (cc.frustum_visible_count == 0) continue;
                        all.push_back({mid2, ci2, chunkScreenAreaPx(cc, vp_mat)});
                    }
                }
                std::sort(all.begin(), all.end(),
                          [](const Stat& a, const Stat& b){ return a.area > b.area; });
                const std::size_t n = std::min<std::size_t>(5, all.size());
                for (std::size_t i = 0; i < n; ++i) {
                    Log::info()
                        << "  top cand #" << i << ": model " << all[i].mid
                        << " chunk " << all[i].ci
                        << " area=" << int(all[i].area) << "px2";
                }
            }
            tracked_was_resident_ = c.is_resident;
        }
    }

    if (streaming_debug_) {
        std::size_t resident = 0;
        std::uint32_t max_load_count = 0;
        std::size_t   cycled = 0;
        for (const auto& [mid, m] : models_gpu_) {
            for (const auto& c : m.chunks) {
                if (c.is_resident) ++resident;
                if (c.load_count > max_load_count) max_load_count = c.load_count;
                if (c.load_count > 1) ++cycled;
            }
        }
        Log::info()
            << "[stream-debug] f" << streaming_frame_idx_
            << " cands=" << streaming_candidates_this_frame_
            << " enq=" << enqueued
            << " drained=" << streaming_drained_this_frame_
            << " ev_lru=" << streaming_evictions_lru_this_frame_
            << " ev_pri=" << streaming_evictions_pri_this_frame_
            << " blocked=" << streaming_blocked_oom_this_frame_
            << " resident=" << resident
            << " cycled=" << cycled
            << " max_load=" << max_load_count;
    }
}

// ===========================================================================
// Cull (#84-p): cullModelCpuCompute + cullModelCpuUpload
// ===========================================================================

std::uint32_t ViewportCore::cullModelCpuCompute(
        ModelGpuData& m,
        const float planes[6][4],
        const float eye[3],
        const float forward[3],
        const float right[3],
        const float up[3],
        float focal_px,
        float min_radius_px,
        float lod1_threshold_px,
        const HizOccludedFn& hiz_occluded) const {
    std::uint32_t hiz_rejects = 0;

    if (m.instances.empty() || m.meshes.empty() || m.chunks.empty()) {
        return 0;
    }

    const bool contrib_enabled = (min_radius_px      > 0.0f);
    const bool lod_enabled     = (lod1_threshold_px  > 0.0f);
    const bool hiz_active      = static_cast<bool>(hiz_occluded);

    // Reset per-chunk scratch + counters at the start of each cull.
    for (auto& c : m.chunks) {
        c.visible_draws_scratch.clear();
        c.visible_draws_scratch_transparent.clear();
        c.transparent_per_draw_vertex_counts.clear();
        c.prefix_sums_scratch.clear();
        c.prefix_sums_scratch.push_back(0);
        c.total_visible_vertices  = 0;
        c.total_visible_draws     = 0;
        c.opaque_visible_vertices = 0;
        c.opaque_visible_draws    = 0;
        c.frustum_visible_count   = 0;
        c.current_priority        = 0.0f;
    }

    // Per-chunk running vertex count for incremental prefix sums.
    std::vector<std::uint32_t> running_vertex_count(m.chunks.size(), 0);

    auto process_instance = [&](std::uint32_t i) {
        const auto& inst = m.instances[i];
        if (inst.mesh_id >= m.meshes.size()) return;
        if (visibility_.isHidden(inst.object_id)) return;
        // Per-instance frustum still needed: a partially-covered subtree
        // descended this far means *some* leaves are visible, but not
        // necessarily this one.
        if (!aabbInFrustum(inst.world_aabb_min, inst.world_aabb_max, planes)) return;

        const std::uint32_t chunk_idx = m.instance_chunk_idx[i];
        ModelGpuData::Chunk& c = m.chunks[chunk_idx];

        // Bump the chunk's frustum-only counter before contribution / HiZ
        // so the streaming loader sees a stable signal across frames.
        ++c.frustum_visible_count;

        const MeshInfo& mesh = m.meshes[inst.mesh_id];

        // Two screen-space metrics: sphere-radius projection (cheap,
        // conservative — used for contribution + LOD pick) and AABB-
        // rectangle projection (tight — used for streaming priority).
        float projected_px = std::numeric_limits<float>::infinity();
        {
            const float cx = 0.5f * (inst.world_aabb_min[0] + inst.world_aabb_max[0]);
            const float cy = 0.5f * (inst.world_aabb_min[1] + inst.world_aabb_max[1]);
            const float cz = 0.5f * (inst.world_aabb_min[2] + inst.world_aabb_max[2]);
            const float ex = inst.world_aabb_max[0] - inst.world_aabb_min[0];
            const float ey = inst.world_aabb_max[1] - inst.world_aabb_min[1];
            const float ez = inst.world_aabb_max[2] - inst.world_aabb_min[2];
            const float radius_world = 0.5f * std::sqrt(ex*ex + ey*ey + ez*ez);
            const float view_z = forward[0] * (cx - eye[0])
                               + forward[1] * (cy - eye[1])
                               + forward[2] * (cz - eye[2]);
            if (view_z > 1e-3f) {
                projected_px = radius_world * focal_px / view_z;

                const float hex = 0.5f * ex;
                const float hey = 0.5f * ey;
                const float hez = 0.5f * ez;
                const float view_he_x = std::fabs(right[0]) * hex
                                      + std::fabs(right[1]) * hey
                                      + std::fabs(right[2]) * hez;
                const float view_he_y = std::fabs(up[0])    * hex
                                      + std::fabs(up[1])    * hey
                                      + std::fabs(up[2])    * hez;
                const float inv_z = focal_px / view_z;
                const float box_area_px2 = 4.0f
                                         * view_he_x * inv_z
                                         * view_he_y * inv_z;
                c.current_priority += box_area_px2;
            }
        }

        // Contribution cull before HiZ: HiZ is by far the most expensive
        // per-instance test, so letting cheap contribution drops happen
        // first cuts the HiZ-tested population by ~5× on real scenes.
        if (contrib_enabled && projected_px < min_radius_px) return;

        if (hiz_active
            && hiz_occluded(inst.world_aabb_min, inst.world_aabb_max)) {
            ++hiz_rejects;
            return;
        }

        const bool use_lod1 = lod_enabled
                            && mesh.lod1_index_count > 0
                            && projected_px < lod1_threshold_px;

        // Emit one VisibleDraw entry into the chunk that owns this
        // instance's vertex range.
        ModelGpuData::VisibleDrawGpu d;
        d.mesh_id       = inst.mesh_id;
        d.instance_idx  = i;
        d.ebo_first_u32 = use_lod1 ? m.instance_lod1_first_u32[i]
                                   : m.instance_ebo_first_u32[i];
        d.base_vertex   = m.instance_base_vertex[i];

        const std::uint32_t entry_vert_count = use_lod1 ? mesh.lod1_index_count
                                                        : mesh.index_count;

        // Opaque-vs-transparent classifier. Routes the draw into the
        // chunk's opaque half or its transparent half. X-ray cap forces
        // every instance into the transparent pass so the blend stage
        // fires; otherwise a non-zero color_override_rgba8's alpha byte
        // (or the mesh's baked has-alpha flag) decides.
        const bool xray_active     = (xray_alpha_cap_ < 1.0f);
        const bool override_active = (inst.color_override_rgba8 != 0u);
        const bool is_transparent  = xray_active
            ? true
            : (override_active
               ? (((inst.color_override_rgba8 >> 24) & 0xFFu) < 255u)
               : (inst.mesh_id < m.mesh_has_alpha.size()
                  && m.mesh_has_alpha[inst.mesh_id] != 0));

        if (is_transparent) {
            c.visible_draws_scratch_transparent.push_back(d);
            c.transparent_per_draw_vertex_counts.push_back(entry_vert_count);
        } else {
            c.visible_draws_scratch.push_back(d);
            running_vertex_count[chunk_idx] += entry_vert_count;
            c.prefix_sums_scratch.push_back(running_vertex_count[chunk_idx]);
        }
        if (use_lod1) {
            ++lod1_dbg_count_;
            lod1_dbg_tris_saved_ += (mesh.index_count > mesh.lod1_index_count
                                     ? (mesh.index_count - mesh.lod1_index_count) / 3
                                     : 0);
        } else if (mesh.lod1_index_count > 0) {
            ++lod0_dbg_eligible_count_;
        } else {
            ++lod0_dbg_no_lod1_count_;
        }
    };

    // Chunk-driven walk: frustum-test each chunk's AABB once, skip
    // every instance inside when the chunk is off-screen. With spatial
    // chunk planning this rejects most instances without ever touching
    // them individually — a strict superset of the previous BVH walk's
    // win, with zero traversal overhead.
    for (auto& c : m.chunks) {
        if (c.instance_ids.empty()) continue;
        if (!aabbInFrustum(c.aabb_min, c.aabb_max, planes)) continue;
        for (std::uint32_t i : c.instance_ids) process_instance(i);
    }

    for (std::size_t ci = 0; ci < m.chunks.size(); ++ci) {
        auto& c = m.chunks[ci];

        // Snapshot opaque-half before appending transparents.
        c.opaque_visible_draws    = std::uint32_t(c.visible_draws_scratch.size());
        c.opaque_visible_vertices = running_vertex_count[ci];

        // Concatenate transparent entries onto the opaque half and
        // continue the prefix-sum sequence. The fragment-pipeline split
        // lives in render(): opaque-pass draws [0, opaque_visible_vertices),
        // transparent-pass draws [opaque_visible_vertices, total_visible_vertices).
        for (std::size_t k = 0; k < c.visible_draws_scratch_transparent.size(); ++k) {
            c.visible_draws_scratch.push_back(
                c.visible_draws_scratch_transparent[k]);
            running_vertex_count[ci] += c.transparent_per_draw_vertex_counts[k];
            c.prefix_sums_scratch.push_back(running_vertex_count[ci]);
        }
        c.total_visible_draws    = std::uint32_t(c.visible_draws_scratch.size());
        c.total_visible_vertices = running_vertex_count[ci];
    }
    return hiz_rejects;
}

void ViewportCore::cullModelCpuUpload(ModelGpuData& m) {
    for (auto& c : m.chunks) {
        if (!c.visible_draws_buffer || !c.prefix_sums_buffer || !c.per_chunk_uniform) continue;

        if (c.total_visible_draws == 0) {
            // Render() will skip this chunk; still zero the uniform so
            // any accidental dispatch sees 0 work.
            const std::uint32_t um[4] = { 0, 0, 0, 0 };
            wgpuQueueWriteBuffer(queue_, c.per_chunk_uniform, 0, um, sizeof(um));
            continue;
        }

        wgpuQueueWriteBuffer(queue_, c.visible_draws_buffer, 0,
                             c.visible_draws_scratch.data(),
                             c.visible_draws_scratch.size()
                                 * sizeof(ModelGpuData::VisibleDrawGpu));
        wgpuQueueWriteBuffer(queue_, c.prefix_sums_buffer, 0,
                             c.prefix_sums_scratch.data(),
                             c.prefix_sums_scratch.size() * sizeof(std::uint32_t));

        // per_chunk_uniform layout (vec4<u32> u_model in the shader):
        //   [0] total_visible_draws       (opaque + transparent)
        //   [1] total_visible_vertices    (sum across the partition)
        //   [2] opaque_visible_vertices   (firstVertex for transparent pass)
        //   [3] opaque_visible_draws      (reserved for a future GPU-side filter)
        const std::uint32_t um[4] = {
            c.total_visible_draws,
            c.total_visible_vertices,
            c.opaque_visible_vertices,
            c.opaque_visible_draws,
        };
        wgpuQueueWriteBuffer(queue_, c.per_chunk_uniform, 0, um, sizeof(um));
    }
}

// ===========================================================================
// Sidecar / direct load (#84-q): applyCachedModel + uploadMeshChunk +
// uploadInstanceChunk + finalizeModel
// ===========================================================================

#include "ChunkPlanner.h"
#include "VertexQuantization.h"

namespace {

// Allocate a wgpu buffer of `size_bytes` with the given usage, and upload
// `data` into it via the queue. Returns nullptr when size_bytes == 0
// (wgpu rejects zero-sized buffer creation). `label` is informational;
// it shows up in validation messages when something goes wrong.
WGPUBuffer createBufferWithData(WGPUDevice device, WGPUQueue queue,
                                const void* data, std::size_t size_bytes,
                                WGPUBufferUsage usage,
                                const char* label) {
    if (size_bytes == 0) return nullptr;

    WGPUBufferDescriptor desc = {};
    desc.size  = std::uint64_t(size_bytes);
    desc.usage = usage | WGPUBufferUsage_CopyDst;
    if (label) {
        desc.label.data   = label;
        desc.label.length = std::strlen(label);
    }
    WGPUBuffer buf = wgpuDeviceCreateBuffer(device, &desc);
    if (buf && data) {
        wgpuQueueWriteBuffer(queue, buf, 0, data, size_bytes);
    }
    return buf;
}

// Look up (or create) the direct-load staging entry for a given model.
// Holds a unique_ptr so address stability is preserved as the map grows.
SidecarData& getOrCreateDirectStaging(
        std::unordered_map<std::uint32_t, std::unique_ptr<SidecarData>>& staging,
        std::uint32_t model_id) {
    auto it = staging.find(model_id);
    if (it == staging.end()) {
        auto [it_new, _] = staging.emplace(
            model_id, std::make_unique<SidecarData>());
        return *it_new->second;
    }
    return *it->second;
}

} // namespace

void ViewportCore::applyCachedModel(std::uint32_t model_id,
                                    StreamingSidecar metadata) {
    if (!device_ || !queue_) {
        Log::warn() << "applyCachedModel without an initialised device";
        return;
    }

    // Replace any existing state for this id.
    auto it = models_gpu_.find(model_id);
    if (it != models_gpu_.end()) {
        releaseWgpuModelGpuData(it->second, pool_);
        models_gpu_.erase(it);
    }

    ModelGpuData m;
    m.vertex_bytes   = metadata.vertex_total_bytes;
    m.index_count    = std::uint32_t(metadata.index_total_count);
    m.mesh_count     = std::uint32_t(metadata.meta.meshes.size());
    m.instance_count = std::uint32_t(metadata.meta.instances.size());
    m.streaming_file_path             = metadata.file_path;
    m.streaming_vertex_section_offset = metadata.vertex_section_offset;
    m.streaming_index_section_offset  = metadata.index_section_offset;

    // ---- Spatial chunk plan ----------------------------------------------
    // Sort meshes by 3D Morton code over centroids, then greedy-pack into
    // chunks <= WGPU_CHUNK_VERTEX_BYTES_LIMIT. Each chunk's AABB ends up
    // tight rather than spanning the whole model, so the distance-based
    // streaming evictor can meaningfully distinguish chunks.
    const std::size_t n_meshes = metadata.meta.meshes.size();
    m.mesh_chunk_idx.assign(n_meshes, 0);
    m.mesh_chunk_local_base_vertex.assign(n_meshes, 0);
    m.mesh_chunk_local_ebo_first_u32.assign(n_meshes, 0);
    m.mesh_chunk_local_lod1_first_u32.assign(n_meshes, 0);

    std::vector<float>    mesh_cx(n_meshes, 0.0f),
                          mesh_cy(n_meshes, 0.0f),
                          mesh_cz(n_meshes, 0.0f);
    std::vector<std::uint32_t> mesh_inst_count(n_meshes, 0);
    for (const auto& inst : metadata.meta.instances) {
        if (inst.mesh_id >= n_meshes) continue;
        mesh_cx[inst.mesh_id] += 0.5f * (inst.world_aabb_min[0] + inst.world_aabb_max[0]);
        mesh_cy[inst.mesh_id] += 0.5f * (inst.world_aabb_min[1] + inst.world_aabb_max[1]);
        mesh_cz[inst.mesh_id] += 0.5f * (inst.world_aabb_min[2] + inst.world_aabb_max[2]);
        ++mesh_inst_count[inst.mesh_id];
    }
    for (std::size_t i = 0; i < n_meshes; ++i) {
        if (mesh_inst_count[i] > 0) {
            const float inv = 1.0f / float(mesh_inst_count[i]);
            mesh_cx[i] *= inv; mesh_cy[i] *= inv; mesh_cz[i] *= inv;
        }
    }

    std::vector<std::vector<std::uint32_t>> chunk_mesh_ids;
    std::vector<std::uint32_t>              instance_to_chunk;
    instance_to_chunk.assign(metadata.meta.instances.size(), 0);
    {
        std::vector<std::uint32_t> sorted_mesh_ids = ChunkPlanner::sortMeshIdsByMorton(
            n_meshes, mesh_cx, mesh_cy, mesh_cz, mesh_inst_count);
        std::vector<std::uint32_t> mesh_vertex_count;
        mesh_vertex_count.reserve(n_meshes);
        for (std::size_t i = 0; i < n_meshes; ++i) {
            mesh_vertex_count.push_back(metadata.meta.meshes[i].vertex_count);
        }
        chunk_mesh_ids = ChunkPlanner::greedyPackChunks(
            sorted_mesh_ids, mesh_vertex_count,
            INSTANCED_VERTEX_STRIDE_BYTES,
            WGPU_CHUNK_VERTEX_BYTES_LIMIT);
        std::vector<std::uint32_t> mesh_to_chunk(n_meshes, 0);
        for (std::size_t ci = 0; ci < chunk_mesh_ids.size(); ++ci) {
            for (std::uint32_t mi : chunk_mesh_ids[ci]) mesh_to_chunk[mi] = std::uint32_t(ci);
        }
        for (std::size_t i = 0; i < metadata.meta.instances.size(); ++i) {
            const std::uint32_t mi = metadata.meta.instances[i].mesh_id;
            if (mi < n_meshes) instance_to_chunk[i] = mesh_to_chunk[mi];
        }
    }

    std::vector<std::uint32_t> chunk_instance_count(chunk_mesh_ids.size(), 0);
    for (std::size_t i = 0; i < instance_to_chunk.size(); ++i) {
        const std::uint32_t ci = instance_to_chunk[i];
        if (ci < chunk_instance_count.size()) ++chunk_instance_count[ci];
    }

    // ---- Allocate per-chunk state. NO pool slices yet (chunks are
    // non-resident); the per-frame loader brings them in as cull marks
    // them visible.
    m.chunks.resize(chunk_mesh_ids.size());
    struct MeshLocal {
        std::uint32_t base_vertex;
        std::uint32_t ebo_first;
        std::uint32_t lod1_first;
    };
    std::vector<std::unordered_map<std::uint32_t, MeshLocal>>
        chunk_mesh_offsets(chunk_mesh_ids.size());
    for (std::size_t ci = 0; ci < chunk_mesh_ids.size(); ++ci) {
        ModelGpuData::Chunk& c = m.chunks[ci];
        c.mesh_ids    = std::move(chunk_mesh_ids[ci]);
        c.is_resident = false;

        std::uint32_t chunk_local_v = 0;
        std::uint32_t chunk_local_i = 0;
        for (std::uint32_t mi : c.mesh_ids) {
            const MeshInfo& mesh = metadata.meta.meshes[mi];
            m.mesh_chunk_idx[mi]                 = std::uint32_t(ci);
            m.mesh_chunk_local_base_vertex[mi]   = chunk_local_v;
            m.mesh_chunk_local_ebo_first_u32[mi] = chunk_local_i;
            chunk_mesh_offsets[ci][mi] = MeshLocal{chunk_local_v, chunk_local_i, 0};
            chunk_local_v += mesh.vertex_count;
            chunk_local_i += mesh.index_count;
        }
        std::uint32_t chunk_local_lod1 = 0;
        for (std::uint32_t mi : c.mesh_ids) {
            const MeshInfo& mesh = metadata.meta.meshes[mi];
            if (mesh.lod1_index_count == 0) continue;
            m.mesh_chunk_local_lod1_first_u32[mi] = chunk_local_i + chunk_local_lod1;
            chunk_mesh_offsets[ci][mi].lod1_first = chunk_local_i + chunk_local_lod1;
            chunk_local_lod1 += mesh.lod1_index_count;
        }
        c.vertex_count     = chunk_local_v;
        c.vertex_byte_size = std::uint64_t(chunk_local_v) * INSTANCED_VERTEX_STRIDE_BYTES;
        c.index_count      = chunk_local_i + chunk_local_lod1;
        c.lod1_index_count = chunk_local_lod1;

        // Small per-chunk buffers, allocated upfront so cull can write into
        // them. visible_draws_buffer cap = chunk's instance count.
        const std::size_t chunk_inst = std::max<std::size_t>(chunk_instance_count[ci], 1);
        const std::size_t draws_bytes = chunk_inst * sizeof(ModelGpuData::VisibleDrawGpu);
        const std::size_t ps_bytes    = (chunk_inst + 1) * sizeof(std::uint32_t);

        WGPUBufferDescriptor vd_desc = {};
        vd_desc.size  = std::max<std::uint64_t>(draws_bytes, 16);
        vd_desc.usage = WGPUBufferUsage_Storage | WGPUBufferUsage_CopyDst;
        vd_desc.label = svFromCStr("model.chunk.visible_draws");
        c.visible_draws_buffer   = wgpuDeviceCreateBuffer(device_, &vd_desc);
        c.visible_draws_capacity = chunk_inst;
        m.vram_bytes_ssbo += vd_desc.size;

        WGPUBufferDescriptor ps_desc = {};
        ps_desc.size  = std::max<std::uint64_t>(ps_bytes, 16);
        ps_desc.usage = WGPUBufferUsage_Storage | WGPUBufferUsage_CopyDst;
        ps_desc.label = svFromCStr("model.chunk.prefix_sums");
        c.prefix_sums_buffer   = wgpuDeviceCreateBuffer(device_, &ps_desc);
        c.prefix_sums_capacity = chunk_inst + 1;
        m.vram_bytes_ssbo += ps_desc.size;

        WGPUBufferDescriptor mu_desc = {};
        mu_desc.size  = 16;
        mu_desc.usage = WGPUBufferUsage_Uniform | WGPUBufferUsage_CopyDst;
        mu_desc.label = svFromCStr("model.chunk.uniform");
        c.per_chunk_uniform = wgpuDeviceCreateBuffer(device_, &mu_desc);
        m.vram_bytes_ssbo += 16;

        c.visible_draws_scratch.reserve(chunk_inst);
        c.prefix_sums_scratch.reserve(chunk_inst + 1);
    }

    // Index section is NOT loaded upfront. Each chunk's index slice is
    // range-read alongside its vertex bytes in loadChunkBytesAndUploadGpu.

    // MeshGpu storage (per-mesh quant basis).
    std::vector<MeshGpu> mesh_gpu;
    mesh_gpu.reserve(metadata.meta.meshes.size());
    for (const auto& mi : metadata.meta.meshes) {
        MeshGpu mg = {};
        mg.aabb_min[0] = mi.local_aabb_min[0];
        mg.aabb_min[1] = mi.local_aabb_min[1];
        mg.aabb_min[2] = mi.local_aabb_min[2];
        mg.aabb_max[0] = mi.local_aabb_max[0];
        mg.aabb_max[1] = mi.local_aabb_max[1];
        mg.aabb_max[2] = mi.local_aabb_max[2];
        mesh_gpu.push_back(mg);
    }
    const std::size_t mesh_storage_bytes = mesh_gpu.size() * sizeof(MeshGpu);
    m.mesh_storage = createBufferWithData(
        device_, queue_,
        mesh_gpu.data(), mesh_storage_bytes,
        WGPUBufferUsage_Storage,
        "model.mesh_storage");
    m.vram_bytes_ssbo += mesh_storage_bytes;

    // InstanceGpu storage. Rebase object_ids globally.
    const std::uint32_t object_id_base = next_object_id_;
    std::uint32_t max_local_id = 0;
    std::vector<InstanceGpu> inst_gpu;
    inst_gpu.reserve(metadata.meta.instances.size());
    for (auto& ic : metadata.meta.instances) {
        if (ic.object_id > max_local_id) max_local_id = ic.object_id;
        ic.object_id = object_id_base + ic.object_id;
        InstanceGpu ig = {};
        std::memcpy(ig.transform, ic.transform, sizeof(ig.transform));
        ig.object_id            = ic.object_id;
        ig.color_override_rgba8 = ic.color_override_rgba8;
        ig.mesh_id              = ic.mesh_id;
        inst_gpu.push_back(ig);
    }
    next_object_id_ = object_id_base + max_local_id + 1;
    const std::size_t inst_storage_bytes = inst_gpu.size() * sizeof(InstanceGpu);
    m.instance_storage = createBufferWithData(
        device_, queue_,
        inst_gpu.data(), inst_storage_bytes,
        WGPUBufferUsage_Storage,
        "model.instance_storage");
    m.vram_bytes_ssbo += inst_storage_bytes;

    // Hand off CPU mirrors.
    m.meshes    = std::move(metadata.meta.meshes);
    m.instances = std::move(metadata.meta.instances);

    // Streaming defers per-mesh vertex data until the owning chunk is
    // loaded. Both volumes + Area-tool CPU shadow fill in per-chunk
    // inside applyStreamedChunk as the bytes arrive.
    m.mesh_local_volumes.assign(m.meshes.size(), 0.0);
    m.mesh_triangles_cache.assign(m.meshes.size(), ModelGpuData::MeshTriangles{});
    m.mesh_has_alpha.assign(m.meshes.size(), std::uint8_t(0));

    // object_id → instance index lookup. Volume tool reads it on every
    // selection mutation; per-pick latency stays O(K) instead of O(K*N).
    m.object_id_to_instance.clear();
    m.object_id_to_instance.reserve(m.instances.size());
    for (std::uint32_t i = 0; i < std::uint32_t(m.instances.size()); ++i) {
        m.object_id_to_instance.emplace(m.instances[i].object_id, i);
    }

    // Per-chunk world AABBs + instance-id lists from instance_to_chunk.
    for (std::size_t ci = 0; ci < m.chunks.size(); ++ci) {
        m.chunks[ci].instance_ids.reserve(m.instances.size() / m.chunks.size() + 4);
    }
    for (std::uint32_t inst_idx = 0; inst_idx < std::uint32_t(m.instances.size()); ++inst_idx) {
        const auto& inst = m.instances[inst_idx];
        const std::uint32_t ci = instance_to_chunk[inst_idx];
        if (ci >= m.chunks.size()) continue;
        auto& c = m.chunks[ci];
        for (int a = 0; a < 3; ++a) {
            c.aabb_min[a] = std::min(c.aabb_min[a], inst.world_aabb_min[a]);
            c.aabb_max[a] = std::max(c.aabb_max[a], inst.world_aabb_max[a]);
        }
        c.instance_ids.push_back(inst_idx);
    }

    // Populate per-instance arrays from the per-chunk per-mesh offsets
    // computed during chunk construction.
    {
        const std::size_t n_inst = m.instances.size();
        m.instance_chunk_idx.assign(n_inst, 0);
        m.instance_base_vertex.assign(n_inst, 0);
        m.instance_ebo_first_u32.assign(n_inst, 0);
        m.instance_lod1_first_u32.assign(n_inst, 0);
        for (std::size_t i = 0; i < n_inst; ++i) {
            const std::uint32_t ci = instance_to_chunk[i];
            const std::uint32_t mi = m.instances[i].mesh_id;
            if (ci >= chunk_mesh_offsets.size()) continue;
            auto it_off = chunk_mesh_offsets[ci].find(mi);
            if (it_off == chunk_mesh_offsets[ci].end()) continue;
            m.instance_chunk_idx[i]      = ci;
            m.instance_base_vertex[i]    = it_off->second.base_vertex;
            m.instance_ebo_first_u32[i]  = it_off->second.ebo_first;
            m.instance_lod1_first_u32[i] = it_off->second.lod1_first;
        }
    }

    auto [inserted, _] = models_gpu_.emplace(model_id, std::move(m));
    ModelGpuData& mref = inserted->second;

    Log::info()
        << "[wgpu stream] applyCachedModel mid=" << model_id
        << " verts=" << mref.vertex_bytes << "B (deferred)"
        << " idx="   << mref.index_count
        << " meshes=" << mref.mesh_count
        << " instances=" << mref.instance_count
        << " chunks=" << mref.chunks.size();

    if (!initial_view_applied_) {
        viewAll();
        initial_view_applied_ = true;
    }
    ensureSelectionFlagsBuffer();
    host_->requestFrame();
}

void ViewportCore::uploadMeshChunk(const MeshChunk& chunk) {
    if (chunk.vertices.empty() || chunk.indices.empty()) return;
    SidecarData& s = getOrCreateDirectStaging(pending_direct_loads_, chunk.model_id);

    // Streamer format: 7 floats / vertex (pos3 + normal3 + color-as-float).
    // Same quantisation as SidecarBuilder::onMeshReady so direct-load and
    // sidecar-load produce byte-identical GPU buffers.
    const std::size_t n_verts = chunk.vertices.size() / INSTANCED_VERTEX_STRIDE_FLOATS;

    float bmin[3] = {  std::numeric_limits<float>::infinity(),
                       std::numeric_limits<float>::infinity(),
                       std::numeric_limits<float>::infinity() };
    float bmax[3] = { -std::numeric_limits<float>::infinity(),
                      -std::numeric_limits<float>::infinity(),
                      -std::numeric_limits<float>::infinity() };
    for (std::size_t i = 0; i < n_verts; ++i) {
        const float* v = chunk.vertices.data() + i * INSTANCED_VERTEX_STRIDE_FLOATS;
        for (int a = 0; a < 3; ++a) {
            if (v[a] < bmin[a]) bmin[a] = v[a];
            if (v[a] > bmax[a]) bmax[a] = v[a];
        }
    }
    float extent_recip[3];
    for (int a = 0; a < 3; ++a) {
        const float ext = bmax[a] - bmin[a];
        extent_recip[a] = ext > 0.0f ? 1.0f / ext : 0.0f;
    }

    const std::size_t vb_offset = s.vertices.size();
    s.vertices.resize(vb_offset + n_verts * INSTANCED_VERTEX_STRIDE_BYTES);
    for (std::size_t i = 0; i < n_verts; ++i) {
        quantizeVertex(chunk.vertices.data() + i * INSTANCED_VERTEX_STRIDE_FLOATS,
                       bmin, extent_recip,
                       s.vertices.data() + vb_offset
                           + i * INSTANCED_VERTEX_STRIDE_BYTES);
    }

    const std::size_t ib_offset = s.indices.size();
    s.indices.insert(s.indices.end(),
                     chunk.indices.begin(), chunk.indices.end());

    MeshInfo info{};
    info.vbo_byte_offset = std::uint32_t(vb_offset);
    info.vertex_count    = std::uint32_t(n_verts);
    info.ebo_byte_offset = std::uint32_t(ib_offset * sizeof(std::uint32_t));
    info.index_count     = std::uint32_t(chunk.indices.size());
    for (int a = 0; a < 3; ++a) {
        info.local_aabb_min[a] = bmin[a];
        info.local_aabb_max[a] = bmax[a];
    }
    info.first_instance       = 0;
    info.instance_count       = 0;
    info.lod1_ebo_byte_offset = 0;
    info.lod1_index_count     = 0;

    if (s.meshes.size() <= chunk.local_mesh_id) {
        s.meshes.resize(chunk.local_mesh_id + 1);
    }
    s.meshes[chunk.local_mesh_id] = info;
}

void ViewportCore::uploadInstanceChunk(const InstanceChunk& chunk) {
    SidecarData& s = getOrCreateDirectStaging(pending_direct_loads_, chunk.model_id);

    InstanceCpu inst{};
    inst.mesh_id              = chunk.local_mesh_id;
    inst.object_id            = chunk.object_id;
    inst.color_override_rgba8 = chunk.color_override_rgba8;
    inst.model_id             = chunk.model_id;
    std::memcpy(inst.placement_transformation, chunk.transform,
                sizeof(inst.placement_transformation));
    for (int i = 0; i < 16; ++i) {
        inst.transform[i] = float(chunk.transform[i]);
    }
    std::memcpy(inst.world_aabb_min, chunk.world_aabb_min, sizeof(inst.world_aabb_min));
    std::memcpy(inst.world_aabb_max, chunk.world_aabb_max, sizeof(inst.world_aabb_max));

    s.instances.push_back(inst);
}

void ViewportCore::finalizeModel(std::uint32_t model_id) {
    auto it = pending_direct_loads_.find(model_id);
    if (it == pending_direct_loads_.end()) {
        Log::warn()
            << "[wgpu direct] finalizeModel(" << model_id
            << ") with no staged data; skipping";
        return;
    }
    std::unique_ptr<SidecarData> staging_ptr = std::move(it->second);
    pending_direct_loads_.erase(it);
    SidecarData& s = *staging_ptr;

    if (!device_ || !queue_) {
        Log::warn() << "[wgpu direct] finalizeModel without an initialised device";
        return;
    }
    if (s.meshes.empty() || s.instances.empty()) {
        Log::info() << "[wgpu direct] finalizeModel(" << model_id
                    << "): empty staging (meshes=" << s.meshes.size()
                    << " instances=" << s.instances.size() << ")";
        return;
    }

    // Build a StreamingSidecar around the staging so applyCachedModel can
    // run its chunk planner over the same shape it expects from on-disk
    // metadata. file_path is left empty — the streaming worker keys off
    // that to skip these chunks (they're already resident after the
    // applyStreamedChunk loop below).
    StreamingSidecar metadata;
    metadata.meta = std::move(s);
    metadata.vertex_section_offset = 0;
    metadata.vertex_total_bytes    = metadata.meta.vertices.size();
    metadata.index_section_offset  = 0;
    metadata.index_total_count     = metadata.meta.indices.size();
    metadata.file_path.clear();

    std::vector<std::uint8_t>  raw_vertices = std::move(metadata.meta.vertices);
    std::vector<std::uint32_t> raw_indices  = std::move(metadata.meta.indices);

    applyCachedModel(model_id, std::move(metadata));

    auto model_it = models_gpu_.find(model_id);
    if (model_it == models_gpu_.end()) {
        Log::warn()
            << "[wgpu direct] finalizeModel(" << model_id
            << "): applyCachedModel produced no model entry";
        return;
    }
    ModelGpuData& m = model_it->second;

    // Gather each chunk's vertex + index bytes from the staged buffers.
    std::size_t chunks_uploaded = 0;
    for (std::size_t ci = 0; ci < m.chunks.size(); ++ci) {
        auto& c = m.chunks[ci];
        if (c.mesh_ids.empty()) continue;

        std::vector<std::uint8_t>  vbytes(c.vertex_byte_size);
        std::vector<std::uint32_t> idx;
        idx.reserve(c.index_count);

        for (std::uint32_t mi : c.mesh_ids) {
            const MeshInfo& mesh = m.meshes[mi];
            const std::size_t vsz = std::size_t(mesh.vertex_count) * INSTANCED_VERTEX_STRIDE_BYTES;
            if (vsz > 0) {
                const std::size_t dst_off = std::size_t(m.mesh_chunk_local_base_vertex[mi])
                                          * INSTANCED_VERTEX_STRIDE_BYTES;
                std::memcpy(vbytes.data() + dst_off,
                            raw_vertices.data() + mesh.vbo_byte_offset, vsz);
            }
            if (mesh.index_count > 0) {
                const std::uint32_t* src = raw_indices.data()
                                         + (mesh.ebo_byte_offset / sizeof(std::uint32_t));
                idx.insert(idx.end(), src, src + mesh.index_count);
            }
        }

        if (!applyStreamedChunk(m, ci, vbytes, idx)) {
            Log::warn()
                << "[wgpu direct] finalizeModel(" << model_id
                << "): applyStreamedChunk failed on chunk " << ci
                << " (pool OOM?)";
            continue;
        }
        ++chunks_uploaded;
    }

    Log::info()
        << "[wgpu direct] finalizeModel mid=" << model_id
        << " meshes=" << m.meshes.size()
        << " instances=" << m.instances.size()
        << " chunks=" << chunks_uploaded << "/" << m.chunks.size()
        << " verts=" << raw_vertices.size() << "B"
        << " idx=" << raw_indices.size();
}

// ===========================================================================
// HiZ + framebuffer attachments (#84-r)
// ===========================================================================

namespace {

// Tunable per-frame log budget for WGPU_HIZ_TRACE diagnostic mode.
// Also referenced by VW's render() bench-warm gate.

const char* HIZ_WGSL = R"(
struct HizUniforms {
    src_w: u32,
    src_h: u32,
    dst_w: u32,
    dst_h: u32,
};

@group(0) @binding(0) var src_depth: texture_depth_multisampled_2d;
@group(0) @binding(1) var<uniform> u_hiz: HizUniforms;

struct VsOut {
    @builtin(position) clip_pos: vec4<f32>,
};

@vertex
fn vs_main(@builtin(vertex_index) vid: u32) -> VsOut {
    // Fullscreen triangle from a 3-vertex draw, no IA bindings.
    let x = f32((vid << 1u) & 2u) * 2.0 - 1.0;
    let y = f32(vid & 2u) * 2.0 - 1.0;
    var out: VsOut;
    out.clip_pos = vec4<f32>(x, -y, 0.0, 1.0);
    return out;
}

@fragment
fn fs_main(in: VsOut) -> @builtin(frag_depth) f32 {
    let dst_x = u32(in.clip_pos.x);
    let dst_y = u32(in.clip_pos.y);
    let sx0 = (dst_x * u_hiz.src_w) / u_hiz.dst_w;
    let sx1 = ((dst_x + 1u) * u_hiz.src_w) / u_hiz.dst_w;
    let sy0 = (dst_y * u_hiz.src_h) / u_hiz.dst_h;
    let sy1 = ((dst_y + 1u) * u_hiz.src_h) / u_hiz.dst_h;

    var max_d: f32 = 0.0;
    for (var y: u32 = sy0; y < sy1; y = y + 1u) {
        for (var x: u32 = sx0; x < sx1; x = x + 1u) {
            let d = textureLoad(src_depth, vec2<i32>(i32(x), i32(y)), 0);
            max_d = max(max_d, d);
        }
    }
    return max_d;
}
)";

} // namespace

bool ViewportCore::buildHizPipeline() {
    WGPUBindGroupLayoutEntry entries[2] = {};
    entries[0].binding = 0;
    entries[0].visibility = WGPUShaderStage_Fragment;
    entries[0].texture.sampleType = WGPUTextureSampleType_Depth;
    entries[0].texture.viewDimension = WGPUTextureViewDimension_2D;
    entries[0].texture.multisampled = 1;
    entries[1].binding = 1;
    entries[1].visibility = WGPUShaderStage_Fragment;
    entries[1].buffer.type = WGPUBufferBindingType_Uniform;
    entries[1].buffer.minBindingSize = 16;  // 4 u32s

    WGPUBindGroupLayoutDescriptor bgl_desc = {};
    bgl_desc.entryCount = 2;
    bgl_desc.entries    = entries;
    bgl_desc.label      = svFromCStr("ifcviewer-wgpu.hiz_bgl");
    hiz_bgl_ = wgpuDeviceCreateBindGroupLayout(device_, &bgl_desc);

    WGPUPipelineLayoutDescriptor pl_desc = {};
    pl_desc.bindGroupLayoutCount = 1;
    pl_desc.bindGroupLayouts     = &hiz_bgl_;
    pl_desc.label                = svFromCStr("ifcviewer-wgpu.hiz_pipeline_layout");
    hiz_pipeline_layout_ = wgpuDeviceCreatePipelineLayout(device_, &pl_desc);

    WGPUShaderSourceWGSL wgsl_src = {};
    wgsl_src.chain.sType = WGPUSType_ShaderSourceWGSL;
    wgsl_src.code        = svFromCStr(HIZ_WGSL);
    WGPUShaderModuleDescriptor sm_desc = {};
    sm_desc.nextInChain = &wgsl_src.chain;
    sm_desc.label       = svFromCStr("ifcviewer-wgpu.hiz_wgsl");
    hiz_shader_module_  = wgpuDeviceCreateShaderModule(device_, &sm_desc);

    // Depth-only output, no colour target. Single-sample.
    WGPUDepthStencilState depth = {};
    depth.format               = WGPUTextureFormat_Depth32Float;
    depth.depthWriteEnabled    = WGPUOptionalBool_True;
    depth.depthCompare         = WGPUCompareFunction_Always;
    depth.stencilFront.compare = WGPUCompareFunction_Always;
    depth.stencilBack.compare  = WGPUCompareFunction_Always;

    WGPURenderPipelineDescriptor rp_desc = {};
    rp_desc.layout              = hiz_pipeline_layout_;
    rp_desc.label               = svFromCStr("ifcviewer-wgpu.hiz_pipeline");
    rp_desc.vertex.module       = hiz_shader_module_;
    rp_desc.vertex.entryPoint   = svFromCStr("vs_main");
    rp_desc.vertex.bufferCount  = 0;

    WGPUFragmentState frag = {};
    frag.module      = hiz_shader_module_;
    frag.entryPoint  = svFromCStr("fs_main");
    frag.targetCount = 0;
    rp_desc.fragment = &frag;

    rp_desc.depthStencil       = &depth;
    rp_desc.primitive.topology = WGPUPrimitiveTopology_TriangleList;
    rp_desc.primitive.cullMode = WGPUCullMode_None;
    rp_desc.multisample.count  = 1;
    rp_desc.multisample.mask   = 0xFFFFFFFFu;

    hiz_pipeline_ = wgpuDeviceCreateRenderPipeline(device_, &rp_desc);
    if (!hiz_pipeline_) {
        Log::warn() << "wgpu hiz pipeline creation failed";
        return false;
    }

    WGPUBufferDescriptor ub_desc = {};
    ub_desc.size  = 16;
    ub_desc.usage = WGPUBufferUsage_Uniform | WGPUBufferUsage_CopyDst;
    ub_desc.label = svFromCStr("ifcviewer-wgpu.hiz_uniform");
    hiz_uniform_buffer_ = wgpuDeviceCreateBuffer(device_, &ub_desc);

    return true;
}

void ViewportCore::ensureHizTextures(int viewport_w, int viewport_h) {
    if (viewport_w <= 0 || viewport_h <= 0) return;

    const std::uint32_t dst_w = HIZ_BASE_W;
    const std::uint32_t dst_h = std::max<std::uint32_t>(
        1, (std::uint32_t(viewport_h) * dst_w + std::uint32_t(viewport_w) / 2)
            / std::uint32_t(viewport_w));

    if (dst_w == hiz_resolve_w_ && dst_h == hiz_resolve_h_ && hiz_resolve_view_) return;

    if (hiz_resolve_view_)    { wgpuTextureViewRelease(hiz_resolve_view_); hiz_resolve_view_ = nullptr; }
    if (hiz_resolve_texture_) { wgpuTextureRelease(hiz_resolve_texture_);  hiz_resolve_texture_ = nullptr; }
    for (int s = 0; s < HIZ_SLOTS; ++s) {
        if (hiz_staging_buffers_[s]) {
            if (hiz_slot_state_[s] == HizSlotState::Mapped) {
                wgpuBufferUnmap(hiz_staging_buffers_[s]);
            }
            wgpuBufferRelease(hiz_staging_buffers_[s]);
            hiz_staging_buffers_[s] = nullptr;
        }
        hiz_slot_state_[s] = HizSlotState::Idle;
    }
    hiz_write_idx_ = 0;
    hiz_valid_     = false;
    if (hiz_bind_group_)      { wgpuBindGroupRelease(hiz_bind_group_);     hiz_bind_group_ = nullptr; }

    WGPUTextureDescriptor desc = {};
    desc.usage         = WGPUTextureUsage_RenderAttachment | WGPUTextureUsage_CopySrc;
    desc.dimension     = WGPUTextureDimension_2D;
    desc.size.width    = dst_w;
    desc.size.height   = dst_h;
    desc.size.depthOrArrayLayers = 1;
    desc.format        = WGPUTextureFormat_Depth32Float;
    desc.mipLevelCount = 1;
    desc.sampleCount   = 1;
    desc.label         = svFromCStr("ifcviewer-wgpu.hiz_resolve");
    hiz_resolve_texture_ = wgpuDeviceCreateTexture(device_, &desc);

    WGPUTextureViewDescriptor vdesc = {};
    vdesc.format          = WGPUTextureFormat_Depth32Float;
    vdesc.dimension       = WGPUTextureViewDimension_2D;
    vdesc.mipLevelCount   = 1;
    vdesc.arrayLayerCount = 1;
    vdesc.aspect          = WGPUTextureAspect_DepthOnly;
    hiz_resolve_view_ = wgpuTextureCreateView(hiz_resolve_texture_, &vdesc);

    // Two staging slots ping-pong so GPU fill of slot N overlaps CPU
    // read of slot N-1. Rows padded to the WGPU spec's textureToBuffer
    // bytesPerRow alignment (256 B).
    constexpr std::uint64_t kWgpuBytesPerRowAlign = 256;
    hiz_padded_bpr_ = std::uint32_t(
        (dst_w * sizeof(float) + kWgpuBytesPerRowAlign - 1)
        / kWgpuBytesPerRowAlign * kWgpuBytesPerRowAlign);
    for (int s = 0; s < HIZ_SLOTS; ++s) {
        WGPUBufferDescriptor bdesc = {};
        bdesc.size  = std::uint64_t(hiz_padded_bpr_) * std::uint64_t(dst_h);
        bdesc.usage = WGPUBufferUsage_CopyDst | WGPUBufferUsage_MapRead;
        bdesc.label = svFromCStr(s == 0 ? "ifcviewer-wgpu.hiz_staging[0]"
                                        : "ifcviewer-wgpu.hiz_staging[1]");
        hiz_staging_buffers_[s] = wgpuDeviceCreateBuffer(device_, &bdesc);
    }

    hiz_resolve_w_ = dst_w;
    hiz_resolve_h_ = dst_h;
    hiz_valid_     = false;
}

void ViewportCore::releaseHizResources() {
    if (hiz_bind_group_)      { wgpuBindGroupRelease(hiz_bind_group_);     hiz_bind_group_ = nullptr; }
    if (hiz_uniform_buffer_)  { wgpuBufferRelease(hiz_uniform_buffer_);    hiz_uniform_buffer_ = nullptr; }
    if (hiz_resolve_view_)    { wgpuTextureViewRelease(hiz_resolve_view_); hiz_resolve_view_ = nullptr; }
    if (hiz_resolve_texture_) { wgpuTextureRelease(hiz_resolve_texture_);  hiz_resolve_texture_ = nullptr; }
    for (int s = 0; s < HIZ_SLOTS; ++s) {
        if (hiz_staging_buffers_[s]) {
            if (hiz_slot_state_[s] == HizSlotState::Mapped) {
                wgpuBufferUnmap(hiz_staging_buffers_[s]);
            }
            wgpuBufferRelease(hiz_staging_buffers_[s]);
            hiz_staging_buffers_[s] = nullptr;
        }
        hiz_slot_state_[s] = HizSlotState::Idle;
    }
    hiz_write_idx_ = 0;
    if (hiz_pipeline_)        { wgpuRenderPipelineRelease(hiz_pipeline_);  hiz_pipeline_ = nullptr; }
    if (hiz_shader_module_)   { wgpuShaderModuleRelease(hiz_shader_module_); hiz_shader_module_ = nullptr; }
    if (hiz_pipeline_layout_) { wgpuPipelineLayoutRelease(hiz_pipeline_layout_); hiz_pipeline_layout_ = nullptr; }
    if (hiz_bgl_)             { wgpuBindGroupLayoutRelease(hiz_bgl_);      hiz_bgl_ = nullptr; }
    hiz_resolve_w_ = hiz_resolve_h_ = hiz_padded_bpr_ = 0;
    hiz_valid_ = false;
    hiz_pyramid_.clear();
    hiz_mip_offset_.clear();
    hiz_mip_w_.clear();
    hiz_mip_h_.clear();
}

int ViewportCore::encodeHizResolve(WGPUCommandEncoder enc) {
    if (!hiz_enabled_ || !hiz_pipeline_ || !hiz_resolve_view_ || !depth_view_) return -1;

    // Pick an idle ping-pong slot. If both slots are in flight, skip
    // this frame's resolve — the cull keeps using whatever pyramid we
    // already have (slightly more stale, never blocks).
    int slot = -1;
    for (int s = 0; s < HIZ_SLOTS; ++s) {
        const int idx = (hiz_write_idx_ + s) % HIZ_SLOTS;
        if (hiz_slot_state_[idx] == HizSlotState::Idle) { slot = idx; break; }
    }
    if (slot < 0) return -1;
    hiz_write_idx_ = (slot + 1) % HIZ_SLOTS;

    // Rebuild the bind group when the depth view itself was replaced
    // (driven by surface resize); the resize path nulls hiz_bind_group_.
    if (!hiz_bind_group_) {
        WGPUBindGroupEntry entries[2] = {};
        entries[0].binding     = 0;
        entries[0].textureView = depth_view_;
        entries[1].binding     = 1;
        entries[1].buffer      = hiz_uniform_buffer_;
        entries[1].size        = 16;
        WGPUBindGroupDescriptor bg = {};
        bg.layout     = hiz_bgl_;
        bg.entryCount = 2;
        bg.entries    = entries;
        bg.label      = svFromCStr("ifcviewer-wgpu.hiz_bind_group");
        hiz_bind_group_ = wgpuDeviceCreateBindGroup(device_, &bg);
    }

    const std::uint32_t uniforms[4] = {
        std::uint32_t(depth_w_), std::uint32_t(depth_h_),
        hiz_resolve_w_, hiz_resolve_h_,
    };
    wgpuQueueWriteBuffer(queue_, hiz_uniform_buffer_, 0, uniforms, sizeof(uniforms));

    WGPURenderPassDepthStencilAttachment depth_att = {};
    depth_att.view              = hiz_resolve_view_;
    depth_att.depthLoadOp       = WGPULoadOp_Clear;
    depth_att.depthStoreOp      = WGPUStoreOp_Store;
    depth_att.depthClearValue   = 0.0f;
    depth_att.stencilLoadOp     = WGPULoadOp_Undefined;
    depth_att.stencilStoreOp    = WGPUStoreOp_Undefined;
    depth_att.depthReadOnly     = false;
    depth_att.stencilReadOnly   = true;

    WGPURenderPassDescriptor pass_desc = {};
    pass_desc.colorAttachmentCount   = 0;
    pass_desc.depthStencilAttachment = &depth_att;
    pass_desc.label                  = svFromCStr("ifcviewer-wgpu.hiz_resolve_pass");

    WGPURenderPassEncoder pass = wgpuCommandEncoderBeginRenderPass(enc, &pass_desc);
    wgpuRenderPassEncoderSetPipeline(pass, hiz_pipeline_);
    wgpuRenderPassEncoderSetBindGroup(pass, 0, hiz_bind_group_, 0, nullptr);
    wgpuRenderPassEncoderDraw(pass, 3, 1, 0, 0);
    wgpuRenderPassEncoderEnd(pass);
    wgpuRenderPassEncoderRelease(pass);

    WGPUTexelCopyTextureInfo src = {};
    src.texture = hiz_resolve_texture_;
    src.aspect  = WGPUTextureAspect_DepthOnly;

    WGPUTexelCopyBufferInfo dst = {};
    dst.buffer              = hiz_staging_buffers_[slot];
    dst.layout.bytesPerRow  = hiz_padded_bpr_;
    dst.layout.rowsPerImage = hiz_resolve_h_;

    WGPUExtent3D extent = {};
    extent.width  = hiz_resolve_w_;
    extent.height = hiz_resolve_h_;
    extent.depthOrArrayLayers = 1;

    wgpuCommandEncoderCopyTextureToBuffer(enc, &src, &dst, &extent);
    return slot;
}

void ViewportCore::startHizMap(int slot, const Eigen::Matrix4f& vp_used) {
    if (slot < 0 || slot >= HIZ_SLOTS) return;
    if (!hiz_staging_buffers_[slot] || hiz_resolve_w_ == 0) return;

    hiz_slot_vp_[slot]    = vp_used;
    hiz_slot_state_[slot] = HizSlotState::Mapping;

    struct MapCtx { ViewportCore* self; int slot; };
    auto* ctx = new MapCtx{ this, slot };

    WGPUBufferMapCallbackInfo mcb = {};
    mcb.mode = WGPUCallbackMode_AllowProcessEvents;
    mcb.callback = [](WGPUMapAsyncStatus status, WGPUStringView /*msg*/,
                      void* ud1, void* /*ud2*/) {
        auto* c = static_cast<MapCtx*>(ud1);
        if (status == WGPUMapAsyncStatus_Success) {
            c->self->hiz_slot_state_[c->slot] = HizSlotState::Mapped;
        } else {
            c->self->hiz_slot_state_[c->slot] = HizSlotState::Idle;
        }
        delete c;
    };
    mcb.userdata1 = ctx;

    const std::size_t map_size = std::size_t(hiz_padded_bpr_) * std::size_t(hiz_resolve_h_);
    wgpuBufferMapAsync(hiz_staging_buffers_[slot], WGPUMapMode_Read,
                       0, map_size, mcb);
}

void ViewportCore::drainHizReadbacks() {
    if (!hiz_enabled_ || hiz_resolve_w_ == 0) return;
    // Non-blocking: wgpuInstanceProcessEvents returns immediately after
    // firing any ready callbacks.
    wgpuInstanceProcessEvents(instance_);

    for (int slot = 0; slot < HIZ_SLOTS; ++slot) {
        if (hiz_slot_state_[slot] != HizSlotState::Mapped) continue;

        const std::size_t map_size =
            std::size_t(hiz_padded_bpr_) * std::size_t(hiz_resolve_h_);
        const std::uint8_t* mapped = static_cast<const std::uint8_t*>(
            wgpuBufferGetConstMappedRange(hiz_staging_buffers_[slot], 0, map_size));

        const std::uint32_t W0 = hiz_resolve_w_;
        const std::uint32_t H0 = hiz_resolve_h_;

        // (Re)build mip pyramid metadata if dimensions changed. Ceil-
        // halving so edge rows of mip 0 always have a child texel.
        if (hiz_mip_offset_.empty()
            || hiz_mip_w_.empty() || hiz_mip_w_[0] != W0
            || hiz_mip_h_.empty() || hiz_mip_h_[0] != H0) {
            hiz_mip_offset_.clear();
            hiz_mip_w_.clear();
            hiz_mip_h_.clear();
            std::uint32_t total = 0;
            std::uint32_t w = W0, h = H0;
            while (true) {
                hiz_mip_offset_.push_back(total);
                hiz_mip_w_.push_back(w);
                hiz_mip_h_.push_back(h);
                total += w * h;
                if (w == 1 && h == 1) break;
                w = std::max(1u, (w + 1u) / 2u);
                h = std::max(1u, (h + 1u) / 2u);
            }
            hiz_pyramid_.assign(total, 0.0f);
        }

        // Mip 0: strip per-row padding.
        for (std::uint32_t y = 0; y < H0; ++y) {
            std::memcpy(&hiz_pyramid_[y * W0],
                        mapped + std::size_t(y) * hiz_padded_bpr_,
                        W0 * sizeof(float));
        }
        wgpuBufferUnmap(hiz_staging_buffers_[slot]);
        hiz_slot_state_[slot] = HizSlotState::Idle;

        // Higher mips: max-reduce 2x2 children.
        for (std::size_t L = 1; L < hiz_mip_offset_.size(); ++L) {
            const std::uint32_t prev_w = hiz_mip_w_[L - 1];
            const std::uint32_t prev_h = hiz_mip_h_[L - 1];
            const std::uint32_t this_w = hiz_mip_w_[L];
            const std::uint32_t this_h = hiz_mip_h_[L];
            const float* src = &hiz_pyramid_[hiz_mip_offset_[L - 1]];
            float*       dst = &hiz_pyramid_[hiz_mip_offset_[L]];
            for (std::uint32_t y = 0; y < this_h; ++y) {
                for (std::uint32_t x = 0; x < this_w; ++x) {
                    const std::uint32_t x0 = std::min(prev_w - 1, x * 2u);
                    const std::uint32_t y0 = std::min(prev_h - 1, y * 2u);
                    const std::uint32_t x1 = std::min(prev_w - 1, x0 + 1u);
                    const std::uint32_t y1 = std::min(prev_h - 1, y0 + 1u);
                    const float a = src[y0 * prev_w + x0];
                    const float b = src[y0 * prev_w + x1];
                    const float c = src[y1 * prev_w + x0];
                    const float d = src[y1 * prev_w + x1];
                    dst[y * this_w + x] = std::max(std::max(a, b), std::max(c, d));
                }
            }
        }

        hiz_vp_    = hiz_slot_vp_[slot];
        hiz_valid_ = true;
    }
}

bool ViewportCore::aabbOccludedByHiz(const float mn[3], const float mx[3]) const {
    if (!hiz_valid_ || hiz_mip_offset_.empty()) return false;

    // Project the 8 corners of the AABB. Track min/max NDC x,y, min
    // projected z (nearest point to the camera), and whether any
    // corner has clip.w <= 0 (straddles near plane).
    const float* m = hiz_vp_.data();
    auto applyVp = [m](float x, float y, float z, float out[4]) {
        out[0] = m[0]*x + m[4]*y + m[8] *z + m[12];
        out[1] = m[1]*x + m[5]*y + m[9] *z + m[13];
        out[2] = m[2]*x + m[6]*y + m[10]*z + m[14];
        out[3] = m[3]*x + m[7]*y + m[11]*z + m[15];
    };

    float nx_lo =  std::numeric_limits<float>::infinity();
    float ny_lo =  std::numeric_limits<float>::infinity();
    float nx_hi = -std::numeric_limits<float>::infinity();
    float ny_hi = -std::numeric_limits<float>::infinity();
    float min_z =  std::numeric_limits<float>::infinity();
    for (int i = 0; i < 8; ++i) {
        const float x = (i & 1) ? mx[0] : mn[0];
        const float y = (i & 2) ? mx[1] : mn[1];
        const float z = (i & 4) ? mx[2] : mn[2];
        float c[4]; applyVp(x, y, z, c);
        if (c[3] <= 1e-4f) return false;
        const float inv_w = 1.0f / c[3];
        const float ndc_x = c[0] * inv_w;
        const float ndc_y = c[1] * inv_w;
        const float ndc_z = c[2] * inv_w;
        nx_lo = std::min(nx_lo, ndc_x);
        ny_lo = std::min(ny_lo, ndc_y);
        nx_hi = std::max(nx_hi, ndc_x);
        ny_hi = std::max(ny_hi, ndc_y);
        min_z = std::min(min_z, ndc_z);
    }

    if (nx_hi < -1.0f || nx_lo > 1.0f || ny_hi < -1.0f || ny_lo > 1.0f) return false;
    if (min_z < 0.0f) return false;

    // NDC y is +up; HiZ-texture y is +down (framebuffer-space frag
    // coords). v = 0.5 * (1 - ny) gives the mapping.
    const std::uint32_t W0 = hiz_mip_w_[0];
    const std::uint32_t H0 = hiz_mip_h_[0];
    const float u_lo =  0.5f * (nx_lo + 1.0f);
    const float u_hi =  0.5f * (nx_hi + 1.0f);
    const float v_lo =  0.5f * (1.0f - ny_hi);
    const float v_hi =  0.5f * (1.0f - ny_lo);
    int x0 = std::max(0, int(std::floor(u_lo * float(W0))));
    int x1 = std::min(int(W0) - 1, int(std::ceil (u_hi * float(W0))));
    int y0 = std::max(0, int(std::floor(v_lo * float(H0))));
    int y1 = std::min(int(H0) - 1, int(std::ceil (v_hi * float(H0))));
    if (x1 < x0 || y1 < y0) return false;

    // Pick the smallest mip level where the AABB covers <= 2 texels
    // per axis. Stops at the coarsest level so 1x1 always works.
    const int side = std::max(x1 - x0 + 1, y1 - y0 + 1);
    int level = 0;
    while (level + 1 < int(hiz_mip_offset_.size()) && (1 << level) < side) ++level;

    const std::uint32_t lw = hiz_mip_w_[level];
    const std::uint32_t lh = hiz_mip_h_[level];
    const int lx0 = std::clamp(int(x0) >> level, 0, int(lw) - 1);
    const int ly0 = std::clamp(int(y0) >> level, 0, int(lh) - 1);
    const int lx1 = std::clamp(int(x1) >> level, 0, int(lw) - 1);
    const int ly1 = std::clamp(int(y1) >> level, 0, int(lh) - 1);
    if (lx0 > lx1 || ly0 > ly1) return false;

    const float* level_data = &hiz_pyramid_[hiz_mip_offset_[level]];
    float max_d = 0.0f;
    for (int y = ly0; y <= ly1; ++y) {
        for (int x = lx0; x <= lx1; ++x) {
            max_d = std::max(max_d, level_data[y * int(lw) + x]);
        }
    }

    // AABB occluded iff its nearest projected z is BEHIND the pyramid's
    // coverage (greater in WebGPU's [0,1] z, where 0 is near).
    const bool rejected = (min_z > max_d);

    // WGPU_HIZ_TRACE diagnostic. Atomic budget shared across the
    // parallel cull workers — fetch_sub returns the previous value.
    if (rejected && hiz_trace_budget_.load(std::memory_order_relaxed) > 0) {
        int prev = hiz_trace_budget_.fetch_sub(1, std::memory_order_relaxed);
        if (prev > 0) {
            Log::info()
                << "[hiz reject] aabb_min=(" << mn[0] << "," << mn[1] << "," << mn[2] << ")"
                << " aabb_max=(" << mx[0] << "," << mx[1] << "," << mx[2] << ")"
                << " ndc_x=[" << nx_lo << "," << nx_hi << "]"
                << " ndc_y=[" << ny_lo << "," << ny_hi << "]"
                << " min_z=" << min_z << " max_d=" << max_d
                << " gap=" << (min_z - max_d)
                << " level=" << level
                << " sample=(" << lx0 << "," << ly0 << ")-(" << lx1 << "," << ly1 << ")"
                << " mip=" << lw << "x" << lh;
        }
    }
    return rejected;
}

void ViewportCore::ensureDepthTexture(int w, int h) {
    if (w == depth_w_ && h == depth_h_ && depth_view_) return;
    releaseDepthTexture();

    WGPUTextureDescriptor desc = {};
    // TextureBinding is needed so the HiZ resolve pass can sample this
    // as a texture_depth_multisampled_2d in its fragment shader.
    desc.usage         = WGPUTextureUsage_RenderAttachment | WGPUTextureUsage_TextureBinding;
    desc.dimension     = WGPUTextureDimension_2D;
    desc.size.width    = std::uint32_t(w);
    desc.size.height   = std::uint32_t(h);
    desc.size.depthOrArrayLayers = 1;
    desc.format        = WGPUTextureFormat_Depth32Float;
    desc.mipLevelCount = 1;
    desc.sampleCount   = kViewportSampleCount;  // matches MSAA color target
    desc.label         = svFromCStr("ifcviewer-wgpu.depth");
    depth_texture_ = wgpuDeviceCreateTexture(device_, &desc);

    WGPUTextureViewDescriptor vdesc = {};
    vdesc.format          = WGPUTextureFormat_Depth32Float;
    vdesc.dimension       = WGPUTextureViewDimension_2D;
    vdesc.mipLevelCount   = 1;
    vdesc.arrayLayerCount = 1;
    vdesc.aspect          = WGPUTextureAspect_DepthOnly;
    depth_view_ = wgpuTextureCreateView(depth_texture_, &vdesc);

    depth_w_ = w;
    depth_h_ = h;
}

void ViewportCore::releaseDepthTexture() {
    if (depth_view_)    { wgpuTextureViewRelease(depth_view_); depth_view_ = nullptr; }
    if (depth_texture_) { wgpuTextureRelease(depth_texture_);  depth_texture_ = nullptr; }
    depth_w_ = depth_h_ = 0;
}

void ViewportCore::ensureMsaaColorTexture(int w, int h) {
    if (w == msaa_w_ && h == msaa_h_ && msaa_color_view_) return;
    releaseMsaaColorTexture();

    WGPUTextureDescriptor desc = {};
    desc.usage         = WGPUTextureUsage_RenderAttachment;
    desc.dimension     = WGPUTextureDimension_2D;
    desc.size.width    = std::uint32_t(w);
    desc.size.height   = std::uint32_t(h);
    desc.size.depthOrArrayLayers = 1;
    desc.format        = surface_format_;
    desc.mipLevelCount = 1;
    desc.sampleCount   = kViewportSampleCount;
    desc.label         = svFromCStr("ifcviewer-wgpu.msaa_color");
    msaa_color_texture_ = wgpuDeviceCreateTexture(device_, &desc);

    msaa_color_view_ = wgpuTextureCreateView(msaa_color_texture_, nullptr);
    msaa_w_ = w;
    msaa_h_ = h;
}

void ViewportCore::releaseMsaaColorTexture() {
    if (msaa_color_view_)    { wgpuTextureViewRelease(msaa_color_view_); msaa_color_view_ = nullptr; }
    if (msaa_color_texture_) { wgpuTextureRelease(msaa_color_texture_);  msaa_color_texture_ = nullptr; }
    msaa_w_ = msaa_h_ = 0;
}
