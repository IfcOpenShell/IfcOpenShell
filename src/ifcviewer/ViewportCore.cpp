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


#include <algorithm>
#include <cmath>
#include <cstdio>
#include <cstring>
#include <limits>
#include <vector>

namespace {
// Orbit camera around target_. World +Z up (BIM convention). Yaw is
// rotation about Z (positive = anticlockwise looking down +Z); pitch
// is elevation above the XY plane. Matches the GL viewport's
// updateCamera convention so framing aligns between backends.
Eigen::Vector3f orbitEye(const float target[3], float dist,
                         float yaw_deg, float pitch_deg) {
    constexpr float kDeg2Rad = kPiF / 180.0f;
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

void ViewportCore::removeModel(uint32_t session_model_id) {
    auto it = models_gpu_.find(session_model_id);
    if (it == models_gpu_.end()) return;
    releaseWgpuModelGpuData(it->second, pool_);
    models_gpu_.erase(it);
    host_->requestFrame();
}

void ViewportCore::resetScene() {
    for (auto& [session_model_id, m] : models_gpu_) releaseWgpuModelGpuData(m, pool_);
    models_gpu_.clear();
    // A fresh scene should auto-frame its first model. Without this the flag
    // stays set from the previous scene (on web, the embedded sample sets it at
    // startup), so the next load — e.g. a ?model= federation after clear_scene_c
    // — would never get framed.
    initial_view_applied_ = false;
    host_->requestFrame();
}

void ViewportCore::hideModel(uint32_t session_model_id) {
    auto it = models_gpu_.find(session_model_id);
    if (it == models_gpu_.end() || it->second.hidden) return;
    it->second.hidden = true;
    host_->requestFrame();
}

void ViewportCore::showModel(uint32_t session_model_id) {
    auto it = models_gpu_.find(session_model_id);
    if (it == models_gpu_.end() || !it->second.hidden) return;
    it->second.hidden = false;
    host_->requestFrame();
}

void ViewportCore::setFederatedFalseOrigin(const Eigen::Matrix4d& matrix_meters) {
    if (federated_false_origin_meters_ == matrix_meters) return;
    federated_false_origin_meters_ = matrix_meters;
    for (auto& kv : models_gpu_) recomposeAndUploadModel(kv.first);
}

void ViewportCore::setModelCoordinateOperation(uint32_t session_model_id,
                                               const Eigen::Matrix4d& matrix_meters) {
    auto it = models_gpu_.find(session_model_id);
    if (it == models_gpu_.end()) return;
    if (it->second.coordinate_operation_meters == matrix_meters) return;
    it->second.coordinate_operation_meters = matrix_meters;
    recomposeAndUploadModel(session_model_id);
}

void ViewportCore::setModelTransformation(uint32_t session_model_id,
                                          const Eigen::Matrix4d& matrix_meters) {
    auto it = models_gpu_.find(session_model_id);
    if (it == models_gpu_.end()) return;
    if (it->second.model_transformation_meters == matrix_meters) return;
    it->second.model_transformation_meters = matrix_meters;
    recomposeAndUploadModel(session_model_id);
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
        constexpr float kDeg2Rad = kPiF / 180.0f;
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
    return InstanceCompose::sceneWorldAabb(models_gpu_, mn, mx);
}

bool ViewportCore::computeModelsAabb(const std::vector<uint32_t>& session_model_ids,
                                     float mn[3], float mx[3]) const {
    return InstanceCompose::modelsWorldAabb(models_gpu_, session_model_ids, mn, mx);
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

void ViewportCore::uploadInstanceRecords(ModelGpuData& m) {
    if (!wgpu_initialized_ || m.instances.empty() || m.instance_storage == nullptr) return;

    std::vector<InstanceGpu> gpu(m.instances.size());
    for (size_t i = 0; i < m.instances.size(); ++i) {
        const InstanceInfo& inst = m.instances[i];
        InstanceGpu& dst = gpu[i];
        std::memcpy(dst.transform, inst.transform, sizeof(dst.transform));
        dst.object_id            = inst.object_id;
        dst.color_override_rgba8 = inst.color_override_rgba8;
        dst.mesh_id              = inst.mesh_id;
        dst._pad1                = 0;
    }
    wgpuQueueWriteBuffer(queue_, m.instance_storage, 0,
                         gpu.data(), gpu.size() * sizeof(InstanceGpu));
}

void ViewportCore::recomposeAndUploadModel(uint32_t session_model_id) {
    if (!wgpu_initialized_) return;
    auto it = models_gpu_.find(session_model_id);
    if (it == models_gpu_.end()) return;
    ModelGpuData& m = it->second;
    if (m.instances.empty() || m.instance_storage == nullptr) return;

    for (auto& inst : m.instances) composeInstanceFromPlacement(inst, m);
    uploadInstanceRecords(m);

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
            const InstanceInfo& inst = m.instances[inst_idx];
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

uint32_t ViewportCore::modelObjectIdBase(uint32_t session_model_id) const {
    auto it = models_gpu_.find(session_model_id);
    return it == models_gpu_.end() ? 0u : it->second.object_id_base;
}

bool ViewportCore::firstGeometryPointWorldM(uint32_t session_model_id,
                                            Eigen::Vector3d& out) const {
    auto it = models_gpu_.find(session_model_id);
    if (it == models_gpu_.end()) return false;
    const ModelGpuData& m = it->second;
    if (m.instances.empty()) return false;

    const InstanceInfo& inst0 = m.instances[0];
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

bool ViewportCore::modelGeoref(uint32_t session_model_id, ModelGeoref& out) const {
    auto it = models_gpu_.find(session_model_id);
    if (it == models_gpu_.end()) return false;
    const ModelGpuData& m = it->second;
    out.units                       = m.units;
    out.coordinate_operation_meters = m.coordinate_operation_meters;
    out.has_coordinate_operation    = m.has_coordinate_operation;
    return true;
}

void ViewportCore::composeInstanceFromPlacement(InstanceInfo& inst,
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
    constexpr float kDeg2Rad = kPiF / 180.0f;
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

bool ViewportCore::viewModels(const std::vector<uint32_t>& session_model_ids) {
    float mn[3], mx[3];
    if (!computeModelsAabb(session_model_ids, mn, mx)) return false;
    frameAabb(mn, mx, 1.10f);   // same padding as viewAll
    Log::info().noquote().nospace()
        << "[wgpu] viewModels framed " << session_model_ids.size() << " model(s)";
    return true;
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

void ViewportCore::setStandardView(StandardView view) {
    switch (view) {
    case StandardView::Front:  setStandardView(0.0f,   0.0f);   break;
    case StandardView::Back:   setStandardView(180.0f, 0.0f);   break;
    case StandardView::Right:  setStandardView(90.0f,  0.0f);   break;
    case StandardView::Left:   setStandardView(270.0f, 0.0f);   break;
    case StandardView::Top:    setStandardView(camera_yaw_deg_,  90.0f); break;
    case StandardView::Bottom: setStandardView(camera_yaw_deg_, -90.0f); break;
    }
}

void ViewportCore::setNavPreset(const char* name) {
    using B = MouseBtn; using M = NavMod;
    if (name && std::strcmp(name, "rhino") == 0)
        nav_bindings_ = { B::Right,  M::Plain,  B::Right,  M::Shift, B::Left,  M::Plain };
    else if (name && std::strcmp(name, "revit") == 0)
        nav_bindings_ = { B::Middle, M::Shift, B::Middle, M::Plain,  B::Left,  M::Plain };
    else if (name && std::strcmp(name, "web") == 0)
        nav_bindings_ = { B::Left,   M::Plain,  B::Middle, M::Plain,  B::Right, M::Plain };
    else  // blender (default)
        nav_bindings_ = { B::Middle, M::Plain,  B::Middle, M::Shift, B::Left,  M::Plain };
}

void ViewportCore::setBackfaceCulling(bool enabled) {
    if (backface_culling_ == enabled) return;
    backface_culling_ = enabled;
    host_->requestFrame();
}

void ViewportCore::setBackgroundColor(float r, float g, float b, float a) {
    Eigen::Vector4f next{r, g, b, a};
    if (background_color_ == next) return;
    background_color_ = next;
    host_->requestFrame();
}

bool ViewportCore::frameSelection() {
    if (selection_.count() == 0) return false;
    float lo[3] = {  std::numeric_limits<float>::infinity(),
                     std::numeric_limits<float>::infinity(),
                     std::numeric_limits<float>::infinity() };
    float hi[3] = { -std::numeric_limits<float>::infinity(),
                    -std::numeric_limits<float>::infinity(),
                    -std::numeric_limits<float>::infinity() };
    bool any = false;
    for (uint32_t id : selection_.selectionIds()) {
        float mn[3], mx[3];
        if (!computeObjectAabb(id, mn, mx)) continue;
        for (int i = 0; i < 3; ++i) {
            lo[i] = std::min(lo[i], mn[i]);
            hi[i] = std::max(hi[i], mx[i]);
        }
        any = true;
    }
    if (!any) return false;
    frameAabb(lo, hi, 1.30f);
    return true;
}

void ViewportCore::orbitBy(float dx_px, float dy_px) {
    // 0.4 deg/px matches the GL viewport. pitch is clamped just shy of
    // the pole so orbitEye() stays well-conditioned.
    camera_yaw_deg_   -= dx_px * 0.4f;
    camera_pitch_deg_ += dy_px * 0.4f;
    camera_pitch_deg_ = std::clamp(camera_pitch_deg_, -89.9f, 89.9f);
    host_->requestFrame();
}

void ViewportCore::panBy(float dx_px, float dy_px, int viewport_height_px) {
    constexpr float kDeg2Rad = kPiF / 180.0f;

    // Pan in the camera's screen-space plane. Within 1° of straight
    // up/down the world-Z up-reference degenerates (cross with forward
    // is the zero vector → NaN), so switch to world-Y up — matches the
    // up-vector switch in buildViewProj so top/bottom views still pan.
    const Eigen::Vector3f target(camera_target_[0], camera_target_[1], camera_target_[2]);
    const Eigen::Vector3f eye = orbitEye(camera_target_, camera_distance_,
                                         camera_yaw_deg_, camera_pitch_deg_);
    const Eigen::Vector3f fwd = (target - eye).normalized();
    const Eigen::Vector3f world_up = (std::abs(camera_pitch_deg_) >= 89.0f)
                                     ? Eigen::Vector3f(0.0f, 1.0f, 0.0f)
                                     : Eigen::Vector3f(0.0f, 0.0f, 1.0f);
    const Eigen::Vector3f right = fwd.cross(world_up).normalized();
    const Eigen::Vector3f up    = right.cross(fwd).normalized();

    const float half_h_world = camera_distance_
        * std::tan(camera_fov_y_deg_ * 0.5f * kDeg2Rad);
    const float pan_per_pixel = (viewport_height_px > 0)
        ? (2.0f * half_h_world / float(viewport_height_px))
        : 0.0f;

    const Eigen::Vector3f shift = -right * (dx_px * pan_per_pixel)
                                +  up    * (dy_px * pan_per_pixel);
    camera_target_[0] += shift.x();
    camera_target_[1] += shift.y();
    camera_target_[2] += shift.z();
    host_->requestFrame();
}

void ViewportCore::dollyBy(float notches) {
    // Each notch zooms ~10% in/out; sign matches "wheel up = in".
    const float factor = std::pow(0.9f, notches);
    camera_distance_   = std::max(0.01f, camera_distance_ * factor);
    host_->requestFrame();
}

void ViewportCore::setPivotIndicatorVisible(bool visible, int hide_after_ms) {
    pivot_indicator_visible_ = visible;
    pivot_indicator_hide_ms_ = hide_after_ms;
    if (visible && hide_after_ms > 0) pivot_indicator_timer_.start();
    else                              pivot_indicator_timer_.invalidate();
    host_->requestFrame();
}

bool ViewportCore::pivotIndicatorVisible() const {
    if (!pivot_indicator_visible_) return false;
    // No armed afterglow means a drag is holding it up.
    if (!pivot_indicator_timer_.isValid()) return true;
    return pivot_indicator_timer_.elapsed() < pivot_indicator_hide_ms_;
}

void ViewportCore::flyMove(bool fwd, bool back, bool right, bool left,
                           bool up, bool down, bool boost, float dt_seconds) {
    if (dt_seconds <= 0.0f) return;
    if (dt_seconds > 0.1f) dt_seconds = 0.1f;  // stall clamp
    // Forward = orbit eye -> target, kept as the view direction in fly mode too
    // so entering fly right after orbiting doesn't snap to a new heading.
    const Eigen::Vector3f target(camera_target_[0], camera_target_[1], camera_target_[2]);
    const Eigen::Vector3f eye = orbitEye(camera_target_, camera_distance_,
                                         camera_yaw_deg_, camera_pitch_deg_);
    Eigen::Vector3f forward = target - eye;
    if (forward.norm() < 1e-6f) return;
    forward.normalize();
    // Looking straight up/down degenerates cross(forward, worldZ); fall back to
    // worldY so `right` doesn't go NaN.
    const Eigen::Vector3f world_up(0.0f, 0.0f, 1.0f);
    const Eigen::Vector3f right_basis =
        (std::abs(camera_pitch_deg_) >= 89.0f) ? Eigen::Vector3f(0.0f, 1.0f, 0.0f) : world_up;
    Eigen::Vector3f right_vec = forward.cross(right_basis);
    right_vec.normalize();
    Eigen::Vector3f move(0.0f, 0.0f, 0.0f);
    if (fwd)   move += forward;
    if (back)  move -= forward;
    if (right) move += right_vec;
    if (left)  move -= right_vec;
    if (up)    move += world_up;
    if (down)  move -= world_up;
    if (move.isZero()) return;
    move.normalize();
    const float speed = fly_move_speed_ * (boost ? 5.0f : 1.0f);  // absolute m/s
    const Eigen::Vector3f delta = move * (speed * dt_seconds);
    camera_target_[0] += delta.x();
    camera_target_[1] += delta.y();
    camera_target_[2] += delta.z();
    host_->requestFrame();
}

void ViewportCore::flyLook(float dx_px, float dy_px) {
    // Turn in place: pin the eye, rotate yaw/pitch, then re-derive the orbit
    // target so orbitEye(target, dist, new_yaw, new_pitch) == the pinned eye.
    const Eigen::Vector3f pinned_eye = orbitEye(camera_target_, camera_distance_,
                                                camera_yaw_deg_, camera_pitch_deg_);
    camera_yaw_deg_   -= dx_px * 0.2f;
    camera_pitch_deg_ += dy_px * 0.2f;
    camera_pitch_deg_ = std::clamp(camera_pitch_deg_, -89.9f, 89.9f);
    constexpr float kDeg2Rad = 0.01745329251994329577f;
    const float yaw = camera_yaw_deg_ * kDeg2Rad;
    const float pit = camera_pitch_deg_ * kDeg2Rad;
    const float cp = std::cos(pit), sp = std::sin(pit);
    const float cy = std::cos(yaw), sy = std::sin(yaw);
    camera_target_[0] = pinned_eye.x() - camera_distance_ * cp * cy;
    camera_target_[1] = pinned_eye.y() - camera_distance_ * cp * sy;
    camera_target_[2] = pinned_eye.z() - camera_distance_ * sp;
    host_->requestFrame();
}

void ViewportCore::flyAdjustSpeed(float notches) {
    const float factor = std::pow(1.25f, notches);  // up = faster
    fly_move_speed_ = std::clamp(fly_move_speed_ * factor, 0.05f, 1000.0f);
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

Eigen::Vector3f ViewportCore::cameraEye() const {
    return orbitEye(camera_target_, camera_distance_, camera_yaw_deg_, camera_pitch_deg_);
}

bool ViewportCore::computeObjectAabb(uint32_t object_id,
                                     float mn[3], float mx[3]) const {
    bool any = false;
    for (int i = 0; i < 3; ++i) {
        mn[i] =  std::numeric_limits<float>::infinity();
        mx[i] = -std::numeric_limits<float>::infinity();
    }
    for (const auto& [session_model_id, m] : models_gpu_) {
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
        for (const auto& [session_model_id, m] : models_gpu_) {
            auto it = m.object_id_to_instance.find(oid);
            if (it == m.object_id_to_instance.end()) continue;
            const InstanceInfo& inst = m.instances[it->second];
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
        for (const auto& [session_model_id, m] : models_gpu_) {
            auto it = m.object_id_to_instance.find(oid);
            if (it == m.object_id_to_instance.end()) continue;
            const InstanceInfo& inst = m.instances[it->second];
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

// X-ray marquee select: one bit per object_id, set by fs_boxpick. That pass
// runs with depth testing off and the scissor clamped to the marquee rect, so
// every object with a fragment anywhere inside the box sets its bit whether it
// is occluded or not — which is the whole point of selecting through in x-ray.
// Only the box-pick pipeline writes it; the layout entry is FRAGMENT-visible
// only, because WebGPU forbids a read_write storage buffer in the vertex stage.
@group(0) @binding(2) var<storage, read_write> hit_flags: array<atomic<u32>>;

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
        let session_model_id = (lo + hi) >> 1u;
        if (prefix_sums[session_model_id] <= vid) {
            lo = session_model_id;
        } else {
            hi = session_model_id;
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

// Selection silhouette mask. Same vertex pulling as vs_main, but the only
// output is coverage: 1 where a selected object is drawn, nothing anywhere
// else. The pass shares the main depth buffer read-only, so the mask is the
// selection AS VISIBLE — an occluded object contributes nothing and gets no
// halo. encodeSelectionOutlinePass dilates this into the outline.
@fragment
fn fs_mask(in: VsOut) -> @location(0) f32 {
    if (is_section_clipped(in.world_pos)) { discard; }
    if (in.object_id >= arrayLength(&sel_flags)) { discard; }
    if ((sel_flags[in.object_id] & 1u) == 0u) { discard; }
    return 1.0;
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
    @location(2) world_pos: vec4<f32>,
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
    // Exact surface world position (F32) so surface pick lands on the true face,
    // not a ray-AABB approximation.
    out.world_pos = vec4<f32>(in.world_pos, 1.0);
    return out;
}

// X-ray marquee. No colour outputs and no depth write — the only result is the
// bit this sets, so every layer under the cursor is recorded rather than just
// the front-most fragment the depth test would leave standing.
@fragment
fn fs_boxpick(in: VsOutPick) {
    if (is_section_clipped(in.world_pos)) { discard; }
    let word = in.object_id >> 5u;
    if (word >= arrayLength(&hit_flags)) { return; }
    atomicOr(&hit_flags[word], 1u << (in.object_id & 31u));
}
)";
} // namespace

bool ViewportCore::buildPipelines() {
    // ---- Bind group layouts ----------------------------------------------
    WGPUBindGroupLayoutEntry frame_entries[3] = {};
    frame_entries[0].binding = 0;
    frame_entries[0].visibility = WGPUShaderStage_Vertex | WGPUShaderStage_Fragment;
    frame_entries[0].buffer.type = WGPUBufferBindingType_Uniform;
    frame_entries[0].buffer.minBindingSize = sizeof(FrameUniforms);
    frame_entries[1].binding = 1;
    frame_entries[1].visibility = WGPUShaderStage_Fragment;
    frame_entries[1].buffer.type = WGPUBufferBindingType_ReadOnlyStorage;
    // X-ray marquee hit bits. Fragment-only: a read_write storage buffer is
    // illegal in the vertex stage, and every pipeline shares this layout.
    frame_entries[2].binding = 2;
    frame_entries[2].visibility = WGPUShaderStage_Fragment;
    frame_entries[2].buffer.type = WGPUBufferBindingType_Storage;

    WGPUBindGroupLayoutDescriptor frame_bgl_desc = {};
    frame_bgl_desc.entryCount = 3;
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
    color_target.format    = surface_view_format_;  // sRGB view (see configureSurface)
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

    // ---- Backface-culling-off variant of the opaque pipeline -----------
    // The "Backface Culling" setting picks between this and main_pipeline_ at
    // draw time (opaque pass). Identical but cullMode None, so single-sided
    // IFC meshes show their back faces.
    WGPURenderPipelineDescriptor rp_desc_nc = rp_desc;
    rp_desc_nc.label = svFromCStr("ifcviewer-wgpu.main_pipeline_no_cull");
    rp_desc_nc.primitive.cullMode = WGPUCullMode_None;
    main_pipeline_no_cull_ = wgpuDeviceCreateRenderPipeline(device_, &rp_desc_nc);
    if (!main_pipeline_no_cull_) {
        Log::warn() << "wgpu main no-cull render pipeline creation failed";
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

    // Section-plane gizmo (shared desktop + web). Optional — a failure just
    // means no gizmo, not a dead viewport.
    section_gizmo_.init(device_, queue_, surface_view_format_, kViewportSampleCount);

    // Corner axis gizmo + orbit pivot indicator (shared desktop + web).
    // Also optional: a failure costs the indicator, not the viewport.
    axis_indicator_.init(device_, queue_, surface_view_format_, kViewportSampleCount);
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

        // The x-ray marquee's hit bits ride the same capacity — one BIT per
        // object where the flags take a word, so a thirty-second of the size.
        // CopySrc because the box pick reads it back through a staging buffer.
        if (hit_flags_buffer_) {
            wgpuBufferRelease(hit_flags_buffer_);
            hit_flags_buffer_ = nullptr;
        }
        hit_flags_words_ = (new_cap + 31u) / 32u;
        WGPUBufferDescriptor hb = {};
        hb.size  = uint64_t(hit_flags_words_) * sizeof(uint32_t);
        hb.usage = WGPUBufferUsage_Storage | WGPUBufferUsage_CopyDst
                 | WGPUBufferUsage_CopySrc;
        hb.label = svFromCStr("ifcviewer-wgpu.xray_hit_flags");
        hit_flags_buffer_ = wgpuDeviceCreateBuffer(device_, &hb);
    }

    // Rebuild the frame bind group against the (possibly new) buffer.
    if (frame_bind_group_) {
        wgpuBindGroupRelease(frame_bind_group_);
        frame_bind_group_ = nullptr;
    }
    WGPUBindGroupEntry fbg_entries[3] = {};
    fbg_entries[0].binding = 0;
    fbg_entries[0].buffer  = frame_uniform_buffer_;
    fbg_entries[0].size    = sizeof(FrameUniforms);
    fbg_entries[1].binding = 1;
    fbg_entries[1].buffer  = selection_flags_buffer_;
    fbg_entries[1].size    = WGPU_WHOLE_SIZE;
    fbg_entries[2].binding = 2;
    fbg_entries[2].buffer  = hit_flags_buffer_;
    fbg_entries[2].size    = WGPU_WHOLE_SIZE;
    WGPUBindGroupDescriptor fbg_desc = {};
    fbg_desc.layout     = frame_bgl_;
    fbg_desc.entryCount = 3;
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
// Lifecycle (#84-l): initWgpu + createPool + shutdown
// ===========================================================================

#if defined(__EMSCRIPTEN__)
#  include <emscripten/emscripten.h>
#endif

namespace {

// Drain pending async callbacks. On wgpu-native this means literally
// calling wgpuInstanceProcessEvents, which fires queued completions.
// On emdawnwebgpu/Dawn-web, queued completions are JS promise resolves
// — wgpuInstanceProcessEvents is a no-op there, so a busy-loop
// `while (!done) processEvents()` would spin forever blocking the
// browser main thread. With ASYNCIFY enabled (see CMakeLists), calling
// emscripten_sleep(0) unwinds the wasm stack, lets JS process resolved
// promises (firing our WGPU callbacks via AllowProcessEvents mode),
// then resumes the C++ caller. Net effect: the same "spin until done"
// shape works on both backends.
// Async-callback mode for WGPU futures. wgpu-native fires
// AllowProcessEvents callbacks deterministically from
// wgpuInstanceProcessEvents — that's what we want on desktop. Dawn-web
// queues those same callbacks indefinitely (waits for a specific
// instance state we don't drive); AllowSpontaneous on web lets the JS
// event loop fire the callback as soon as the underlying promise
// resolves.
constexpr WGPUCallbackMode kAsyncCbMode =
#if defined(__EMSCRIPTEN__)
    WGPUCallbackMode_AllowSpontaneous;
#else
    WGPUCallbackMode_AllowProcessEvents;
#endif

inline void waitTickInstance(WGPUInstance instance) {
#if defined(__EMSCRIPTEN__)
    // Asyncify is OFF on web (see ifcviewer-web/CMakeLists.txt). The
    // init path no longer uses this helper — it's callback-driven via
    // initWgpuAsyncWeb. The remaining callers are MapAsync sync-wait
    // loops (pick readback): those will spin forever here until they
    // are ported to a callback-driven shape. Until then, hitting a
    // pick on web hangs the page. ProcessEvents is a no-op on
    // Dawn-web but harmless to call.
    wgpuInstanceProcessEvents(instance);
#else
    wgpuInstanceProcessEvents(instance);
#endif
}


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

// The fragment shader pre-decodes sRGB→linear to cancel the surface's
// automatic linear→sRGB write encoding (so the final bytes match the GL
// backend). That only works when the render target is an sRGB format. On
// desktop the surface's preferred format already is (e.g. BGRA8UnormSrgb);
// the browser canvas only offers the plain Unorm format, so we render to an
// sRGB *view* of it instead (configured via viewFormats). Maps a Unorm
// surface format to its sRGB sibling; returns the input unchanged when it is
// already sRGB (or has no sibling), so the desktop path is untouched.
WGPUTextureFormat srgbViewFormat(WGPUTextureFormat f) {
    switch (f) {
        case WGPUTextureFormat_BGRA8Unorm: return WGPUTextureFormat_BGRA8UnormSrgb;
        case WGPUTextureFormat_RGBA8Unorm: return WGPUTextureFormat_RGBA8UnormSrgb;
        default:                           return f;
    }
}
} // namespace

bool ViewportCore::createPool() {
    // Size the streaming pool to *demand*: configure a modest initial
    // sub-buffer and let BufferPool::addSubBuffer grow it lazily (and
    // halve-retry down to its 64 MB floor on constrained devices) as the
    // working set needs more.
    //
    // We deliberately do NOT grab the largest momentarily-allocatable
    // buffer up front. Drivers can advertise an effectively unbounded
    // maxBufferSize (1 TB observed on this Linux/wgpu-native stack), so a
    // "probe for the biggest single buffer" walk lands on multiple GB.
    // Allocating that for a 1 MB model starves the depth/MSAA/HiZ/pick
    // attachments and the selection-flags buffer, OOMing the device on
    // the next tiny allocation. A single chunk is capped at
    // WGPU_CHUNK_VERTEX_BYTES_LIMIT (16 MB), so the initial sub-buffer
    // only has to clear that floor; everything beyond is added on demand.
    WGPULimits device_limits = {};
    wgpuDeviceGetLimits(device_, &device_limits);

    constexpr uint64_t MIN_POOL_CAPACITY = 64ull * 1024 * 1024;
#if defined(__EMSCRIPTEN__)
    // Web stays at the 64 MB floor: Chrome's WebGPU process contends
    // badly on large first allocations (and any other WebGPU tab on the
    // same origin makes it worse), so a small first sub-buffer keeps
    // first-frame cheap. See the web-init gotchas note.
    constexpr uint64_t INITIAL_SUB_BUFFER = 64ull * 1024 * 1024;
#else
    // Desktop has no such contention constraint; a larger initial
    // sub-buffer means fewer sub-buffers (and per-chunk bind groups) for
    // big models. 256 MB holds ~16 max-size chunks; if the device can't
    // grant it, addSubBuffer halve-retries down to the 64 MB floor.
    constexpr uint64_t INITIAL_SUB_BUFFER = 256ull * 1024 * 1024;
#endif
    const WGPUBufferUsage pool_usage = WGPUBufferUsage_Storage
                                     | WGPUBufferUsage_CopyDst;
    const uint64_t per_sub = std::min<uint64_t>(
        device_limits.maxBufferSize,
        std::max<uint64_t>(MIN_POOL_CAPACITY, INITIAL_SUB_BUFFER));
    pool_.configure(instance_, device_, pool_usage, per_sub,
                    "ifcviewer-wgpu.pool");
#if defined(__EMSCRIPTEN__)
    // Cap total pool capacity below the wasm heap ceiling. On web a growth that
    // would push the heap past MAXIMUM_MEMORY is a bad_alloc → uncatchable
    // abort, so the pool must stop growing (and evict) before then. Leave
    // headroom for metadata (instances/maps), transient decompression buffers,
    // and wgpu overhead. Big federations then keep a bounded, highest-priority
    // resident set instead of aborting.
    pool_.setMaxTotalCapacity(3072ull * 1024 * 1024);  // 3 GB (heap ceiling 4 GB)
#endif
    Log::info() << "wgpu: pool per-sub-buffer capacity = "
                << (per_sub / (1024 * 1024)) << " MB (grows lazily on "
                << "demand; device maxBufferSize = "
                << (device_limits.maxBufferSize / (1024 * 1024)) << " MB)";
    return true;
}

bool ViewportCore::initWgpu(bool web_limits) {
#if !defined(__EMSCRIPTEN__)
    wgpuSetLogCallback(onWgpuLog, nullptr);
    wgpuSetLogLevel(WGPULogLevel_Warn);
#endif

    Log::info() << "[initWgpu] 1/7 wgpuCreateInstance";
    instance_ = wgpuCreateInstance(nullptr);
    if (!instance_) {
        Log::warn() << "wgpuCreateInstance returned null";
        return false;
    }

    Log::info() << "[initWgpu] 2/7 host_->createSurface";
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
    acb.mode = kAsyncCbMode;
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

    Log::info() << "[initWgpu] 3/7 wgpuInstanceRequestAdapter";
    wgpuInstanceRequestAdapter(instance_, &adapter_opts, acb);
    while (!areq.done) waitTickInstance(instance_);
    if (!areq.ok) return false;
    adapter_ = areq.adapter;
    Log::info() << "[initWgpu] 3/7 adapter ready";

    // ---- Async request device --------------------------------------------
    struct DeviceReq { WGPUDevice device = nullptr; bool done = false; bool ok = false; };
    DeviceReq dreq;

    WGPULimits adapter_limits = {};
    wgpuAdapterGetLimits(adapter_, &adapter_limits);

    WGPULimits web_floor_limits = adapter_limits;
    web_floor_limits.maxStorageBufferBindingSize = 128ull * 1024 * 1024;
    web_floor_limits.maxBufferSize               = 256ull * 1024 * 1024;

    WGPUDeviceDescriptor dev_desc = {};
#if defined(__EMSCRIPTEN__)
    // Dawn-web's RequestDevice hangs (no promise resolution) when we
    // pass a fully-populated WGPULimits as requiredLimits — every
    // non-zero field is treated as a hard requirement, and the
    // browser's adapter-reported limits include values it won't grant
    // back to a device. nullptr means "no specific requirements; give
    // me default limits", which the spec guarantees succeeds and is
    // exactly what we need: the pool sizes itself to demand in
    // createPool and grows lazily, so we don't lose anything by
    // deferring to defaults here.
    (void)web_floor_limits;
    (void)web_limits;
    dev_desc.requiredLimits = nullptr;
#else
    dev_desc.requiredLimits = web_limits ? &web_floor_limits : &adapter_limits;
    if (web_limits) {
        Log::info() << "wgpu --web-limits: requesting browser-floor limits "
                       "(maxStorageBufferBindingSize=128MB, maxBufferSize=256MB)";
    }
#endif
#if !defined(__EMSCRIPTEN__)
    // Setting only the callback (leaving uncapturedErrorCallbackInfo.mode
    // = 0 default) makes Dawn-web's RequestDevice silently never resolve
    // the device promise. Leave the whole struct zeroed on web; the
    // browser already surfaces uncaptured errors to the JS console.
    dev_desc.uncapturedErrorCallbackInfo.callback = onUncapturedError;
#endif

    WGPURequestDeviceCallbackInfo dcb = {};
    dcb.mode = kAsyncCbMode;
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

    Log::info() << "[initWgpu] 4/7a wgpuAdapterRequestDevice CALL";
#if defined(__EMSCRIPTEN__)
    // Pass nullptr descriptor so Dawn-web takes the all-defaults path.
    // Setting any descriptor field that Dawn-web can't grant silently
    // makes the device promise never resolve, so we avoid the whole
    // struct. Note: web init normally goes through initWgpuAsyncWeb,
    // not this sync path; this branch is dead code on the current
    // web build but kept for any future caller.
    wgpuAdapterRequestDevice(adapter_, nullptr, dcb);
#else
    wgpuAdapterRequestDevice(adapter_, &dev_desc, dcb);
#endif
    Log::info() << "[initWgpu] 4/7b RequestDevice returned, entering spin";
    int tick = 0;
    while (!dreq.done) {
        waitTickInstance(instance_);
        if (++tick % 100 == 0) {
            Log::info() << "[initWgpu] 4/7c spin tick=" << tick;
        }
        if (tick > 2000) {
            Log::warn() << "[initWgpu] 4/7 giving up after 2000 ticks";
            return false;
        }
    }
    if (!dreq.ok) return false;
    device_ = dreq.device;
    queue_  = wgpuDeviceGetQueue(device_);
    Log::info() << "[initWgpu] 4/7d device + queue ready";

    Log::info() << "[initWgpu] 5/7 createPool";
    if (!createPool()) {
        Log::warn() << "wgpu: streaming pool probe failed; cannot start";
        return false;
    }
    Log::info() << "[initWgpu] 5/7 pool created";
#if !defined(__EMSCRIPTEN__)
    // Background streaming worker. On desktop std::thread spawns a real
    // OS thread; under Emscripten that requires -pthread + SharedArrayBuffer
    // (which itself needs COOP/COEP headers from the hosting page).
    // Until the web build wires those up we run streaming inline from
    // the render thread (see the `use_sync = true` branch in
    // driveStreamingLoads on Emscripten).
    streaming_thread_.start();
#endif

    Log::info() << "[initWgpu] 6/7 wgpuSurfaceGetCapabilities";
    WGPUSurfaceCapabilities caps = {};
    if (wgpuSurfaceGetCapabilities(surface_, adapter_, &caps) != WGPUStatus_Success
        || caps.formatCount == 0) {
        Log::warn() << "wgpuSurfaceGetCapabilities returned no formats";
        return false;
    }
    surface_format_      = caps.formats[0];
    surface_view_format_ = srgbViewFormat(surface_format_);
    wgpuSurfaceCapabilitiesFreeMembers(caps);

    Log::info() << "wgpu init OK; surface format = " << int(surface_format_)
                << " view format = " << int(surface_view_format_);
    return true;
}

#if defined(__EMSCRIPTEN__)
namespace {
// State carrier for the nested callback chain. Heap-allocated so it
// survives across the JS event loop ticks that resolve each promise;
// freed at the leaf callback (success or any error path).
struct WebInitCtx {
    ViewportCore* core;
    std::function<void(bool)> on_complete;
};
} // namespace

void ViewportCore::initWgpuAsyncWeb(std::function<void(bool)> on_complete) {
    // Pass a defaulted descriptor (not nullptr). On Dawn-web,
    // wgpuCreateInstance(nullptr) returns a usable instance but the
    // subsequent RequestDevice promise silently never resolves.
    WGPUInstanceDescriptor inst_desc = {};
    instance_ = wgpuCreateInstance(&inst_desc);
    if (!instance_) {
        Log::warn() << "[web init] wgpuCreateInstance returned null";
        on_complete(false);
        return;
    }

    auto* ctx = new WebInitCtx{this, std::move(on_complete)};

    // No compatibleSurface — setting THAT makes the device promise silently
    // never resolve on Dawn-web, which is what this comment used to warn about
    // for every field.
    //
    // powerPreference is safe, and it matters: without it the browser picks its
    // default adapter, and on a hybrid laptop that is the INTEGRATED GPU. Seen
    // on a Windows machine with an RTX 500 sitting at 0% while Intel Graphics
    // did the work — no warning anywhere, because this is hardware rendering,
    // just on the wrong hardware. Verified in Chrome that all three settings
    // resolve a device, and that the choice is honoured: default and
    // high-performance give the discrete card, low-power gives the iGPU.
    WGPURequestAdapterOptions adapter_opts = {};
    adapter_opts.powerPreference = WGPUPowerPreference_HighPerformance;

    WGPURequestAdapterCallbackInfo acb = {};
    acb.mode = WGPUCallbackMode_AllowSpontaneous;
    acb.callback = [](WGPURequestAdapterStatus status, WGPUAdapter adapter,
                      WGPUStringView msg, void* ud1, void* /*ud2*/) {
        auto* c = static_cast<WebInitCtx*>(ud1);
        if (status != WGPURequestAdapterStatus_Success || !adapter) {
            Log::warn() << "[web init] RequestAdapter failed: " << svToStr(msg);
            c->on_complete(false);
            delete c;
            return;
        }
        c->core->adapter_ = adapter;

        WGPURequestDeviceCallbackInfo dcb = {};
        dcb.mode = WGPUCallbackMode_AllowSpontaneous;
        dcb.callback = [](WGPURequestDeviceStatus dstatus, WGPUDevice device,
                          WGPUStringView dmsg, void* ud1b, void* /*ud2*/) {
            auto* c = static_cast<WebInitCtx*>(ud1b);
            if (dstatus != WGPURequestDeviceStatus_Success || !device) {
                Log::warn() << "[web init] RequestDevice failed: " << svToStr(dmsg);
                c->on_complete(false);
                delete c;
                return;
            }
            c->core->device_ = device;
            c->core->queue_  = wgpuDeviceGetQueue(device);

            // Surface creation is deferred to here (post-device-ready).
            // Creating it inside the adapter callback (before
            // wgpuAdapterRequestDevice) makes the device promise
            // silently never resolve on Dawn-web.
            c->core->surface_ = c->core->host_->createSurface(c->core->instance_);
            if (!c->core->surface_) {
                Log::warn() << "[web init] host createSurface returned null";
                c->on_complete(false);
                delete c;
                return;
            }

            if (!c->core->createPool()) {
                Log::warn() << "[web init] pool create failed";
                c->on_complete(false);
                delete c;
                return;
            }

            WGPUSurfaceCapabilities caps = {};
            if (wgpuSurfaceGetCapabilities(c->core->surface_, c->core->adapter_, &caps)
                    != WGPUStatus_Success
                || caps.formatCount == 0) {
                Log::warn() << "[web init] surface has no formats";
                c->on_complete(false);
                delete c;
                return;
            }
            c->core->surface_format_      = caps.formats[0];
            c->core->surface_view_format_ = srgbViewFormat(c->core->surface_format_);
            wgpuSurfaceCapabilitiesFreeMembers(caps);

            Log::info() << "[web init] wgpu device + surface ready (format="
                        << int(c->core->surface_format_) << " view format="
                        << int(c->core->surface_view_format_) << ")";
            // Device + queue are live: the buffer-upload paths guarded on this
            // (uploadInstanceRecords, recomposeAndUploadModel) are now safe. The
            // desktop host latches the same flag after its own initWgpu returns.
            c->core->wgpu_initialized_ = true;
            c->on_complete(true);
            delete c;
        };
        dcb.userdata1 = c;
        // Pass a zero-init local descriptor (not nullptr). Dawn-web's
        // RequestDevice silently never resolves the promise when passed
        // nullptr.
        WGPUDeviceDescriptor dd = {};
        // Device-lost handler. If another GPU client (e.g. the desktop app
        // launched alongside this tab) exhausts GPU memory, the browser can
        // reclaim our device. Without this we'd keep driving render() on a
        // dead device — wgpuSurfaceGetCurrentTexture returns Lost forever and
        // the reconfigure+requestFrame retry becomes a tight loop that hangs
        // the tab. Latch a flag so render() bails and the loop goes idle.
        // Skip the intentional Destroyed reason (fired by our own shutdown).
        dd.deviceLostCallbackInfo.mode     = WGPUCallbackMode_AllowSpontaneous;
        dd.deviceLostCallbackInfo.callback =
            [](const WGPUDevice* /*dev*/, WGPUDeviceLostReason reason,
               WGPUStringView msg, void* ud1, void* /*ud2*/) {
                if (reason == WGPUDeviceLostReason_Destroyed) return;
                auto* core = static_cast<ViewportCore*>(ud1);
                core->device_lost_ = true;
                Log::warn() << "[wgpu] device lost (GPU memory reclaimed?): "
                            << svToStr(msg) << " — reload the page";
            };
        dd.deviceLostCallbackInfo.userdata1 = c->core;
        wgpuAdapterRequestDevice(adapter, &dd, dcb);
    };
    acb.userdata1 = ctx;
    wgpuInstanceRequestAdapter(instance_, &adapter_opts, acb);
}
#endif  // __EMSCRIPTEN__

void ViewportCore::shutdown() {
    // Stop streaming first so no late results land in the pool after
    // we've torn down model state. Worker drains its queue then joins.
    streaming_thread_.stop();

    for (auto& [session_model_id, m] : models_gpu_) releaseWgpuModelGpuData(m, pool_);
    models_gpu_.clear();

    if (frame_bind_group_)        { wgpuBindGroupRelease(frame_bind_group_);          frame_bind_group_ = nullptr; }
    if (frame_uniform_buffer_)    { wgpuBufferRelease(frame_uniform_buffer_);         frame_uniform_buffer_ = nullptr; }
    if (selection_flags_buffer_)  { wgpuBufferRelease(selection_flags_buffer_);       selection_flags_buffer_ = nullptr; }
    selection_flags_capacity_ = 0;
    if (hit_flags_buffer_)        { wgpuBufferRelease(hit_flags_buffer_);             hit_flags_buffer_ = nullptr; }
    hit_flags_words_ = 0;
    if (main_pipeline_)              { wgpuRenderPipelineRelease(main_pipeline_);             main_pipeline_ = nullptr; }
    if (main_pipeline_no_cull_)      { wgpuRenderPipelineRelease(main_pipeline_no_cull_);     main_pipeline_no_cull_ = nullptr; }
    if (main_pipeline_transparent_)  { wgpuRenderPipelineRelease(main_pipeline_transparent_); main_pipeline_transparent_ = nullptr; }
    section_gizmo_.destroy();
    axis_indicator_.destroy();
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
#include "SidecarCompress.h"

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
        std::uint32_t session_model_id) {
    const auto& c = m.chunks[chunk_idx];
    StreamingThread::Request req;
    req.session_model_id                = session_model_id;
    req.chunk_idx               = chunk_idx;
    req.file_path               = m.streaming_file_path;
    // v16: one compressed vertex frame + one compressed index frame per chunk.
    req.geometry_section_offset = m.geometry_section_offset;
    req.v_comp_off  = c.v_comp_off;
    req.v_comp_size = c.v_comp_size;
    req.v_raw_size  = c.vertex_byte_size;
    req.i_comp_off  = c.i_comp_off;
    req.i_comp_size = c.i_comp_size;
    req.i_raw_size  = c.index_count * sizeof(std::uint32_t);
    return req;
}

bool ViewportCore::loadChunkBytesAndUploadGpu(ModelGpuData& m,
                                              std::size_t chunk_idx) {
    if (chunk_idx >= m.chunks.size()) return false;
    auto& c = m.chunks[chunk_idx];
    if (c.is_resident) return true;
    if (m.streaming_file_path.empty()) return false;

    // Synchronous fallback: read + decompress the chunk inline, apply. Used
    // only when the async path can't be — i.e. by the screenshot test on the
    // first frame.
    std::vector<std::uint8_t>  vbytes;
    std::vector<std::uint32_t> idx;
    if (!readChunkGeometryCompressed(
            m.streaming_file_path, m.geometry_section_offset,
            c.v_comp_off, c.v_comp_size, c.vertex_byte_size,
            c.i_comp_off, c.i_comp_size, c.index_count * sizeof(std::uint32_t),
            vbytes, idx)) {
        Log::warn() << "[wgpu stream] failed to read/decompress chunk " << chunk_idx;
        return false;
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
    for (auto& [session_model_id, m] : models_gpu_) {
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
        for (auto& [session_model_id, m] : models_gpu_) {
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
        for (auto& [session_model_id, m] : models_gpu_) {
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
                   victim.last_evicted_by_session_model_id == cand_mid
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

        victim.last_evicted_by_session_model_id  = cand_mid;
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
            auto it = models_gpu_.find(res.session_model_id);
            if (it == models_gpu_.end()) continue;  // model unloaded
            auto& m = it->second;
            if (res.chunk_idx >= m.chunks.size()) continue;
            auto& c = m.chunks[res.chunk_idx];
            c.is_loading = false;
            if (!res.success) {
                Log::warn() << "[wgpu stream] worker read failed for model "
                            << res.session_model_id << " chunk " << res.chunk_idx;
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
        std::uint32_t session_model_id;
        float         priority;
    };
    std::vector<Candidate> candidates;
    candidates.reserve(64);
    for (auto& [session_model_id, m] : models_gpu_) {
        if (m.streaming_file_path.empty() || m.hidden) continue;
        for (std::size_t ci = 0; ci < m.chunks.size(); ++ci) {
            auto& c = m.chunks[ci];
            if (c.is_resident)                       continue;
            if (c.is_loading)                        continue;
            // Contribution cull: only fetch chunks big enough on screen to
            // actually draw at the current view — not everything in the
            // frustum. Zoomed out over a big federation this skips the fine
            // chunks that project to sub-pixel, so the network only pulls
            // what's resolvable now; the rest stream in as you approach.
            if (c.contribution_visible_count == 0)   continue;
            if (c.blocked_cooldown_until_frame_idx > streaming_frame_idx_) continue;
            candidates.push_back({&m, ci, session_model_id, candidate_priority(c)});
        }
    }
    streaming_candidates_this_frame_ = int(candidates.size());
    std::sort(candidates.begin(), candidates.end(),
              [](const Candidate& a, const Candidate& b) {
                  return a.priority > b.priority;
              });

    int enqueued = 0;
    web_pending_.clear();
    web_pending_head_ = 0;
    // Everything from `from` onwards that streams over the network, in priority
    // order, for the completions to drain. Called from BOTH exits of the loop:
    // the per-frame budget is reached first when nothing is in flight yet, so
    // queueing only on the in-flight cap left the queue empty exactly when it
    // was needed most.
    auto queue_web_tail = [&](std::size_t from) {
        for (std::size_t k = from; k < candidates.size(); ++k) {
            const Candidate& rest = candidates[k];
            if (rest.m->streaming_from_web) {
                web_pending_.push_back({rest.session_model_id, rest.ci});
            }
        }
    };
    for (std::size_t cand_idx = 0; cand_idx < candidates.size(); ++cand_idx) {
        const Candidate& cand = candidates[cand_idx];
        if (enqueued >= MAX_STREAMING_LOADS_PER_FRAME) {
            more_pending = true;
            queue_web_tail(cand_idx);
            break;
        }
        auto& c = cand.m->chunks[cand.ci];

        const std::uint64_t need = c.vertex_byte_size
                                 + c.index_count * sizeof(std::uint32_t);

#if defined(__EMSCRIPTEN__)
        // Web async loads only allocate pool space when they COMPLETE, and pool
        // growth is itself async (provisional sub-buffers validated off the JS
        // event loop). Gate issuance on what the pool can hold so we never fetch
        // bytes we can't place (which would re-fetch → network thrash; a 531 MB
        // model re-fetched 4×).
        if (cand.m->streaming_from_web
            && pool_.total_free_bytes() < streaming_web_inflight_bytes_ + need) {
            // Not enough VALIDATED pool space for this chunk plus what's already
            // in flight. If the pool can still grow, grow FIRST (async on web: a
            // provisional sub-buffer validates a frame or two later) — cheaper
            // than evict/refetch thrash while the model still fits by growing.
            if (pool_.can_grow()) {
                pool_.requestGrowth();
                c.blocked_cooldown_until_frame_idx =
                    streaming_frame_idx_ + kGrowBackoffFrames;
                more_pending = true;
                continue;
            }
            // At the hard capacity budget (setMaxTotalCapacity): growth can't
            // help — growing further would abort the wasm heap. Evict lower-
            // priority / LRU resident chunks so this priority-sorted candidate
            // fits. This is the only path that keeps a big federation navigable
            // once it exceeds the memory budget (highest-contribution chunks win).
            while (pool_.total_free_bytes() < streaming_web_inflight_bytes_ + need) {
                if (evict_one_lru()) continue;
                if (evict_lowest_priority_than(cand.session_model_id, std::uint32_t(cand.ci),
                                               cand.priority)) continue;
                break;
            }
            if (pool_.total_free_bytes() < streaming_web_inflight_bytes_ + need) {
                c.blocked_cooldown_until_frame_idx =
                    streaming_frame_idx_ + kBlockedCooldownFrames;
                more_pending = true;
                continue;  // couldn't free enough — hold off this frame
            }
            // Freed enough — fall through to the web load below.
        }
#endif
        while (!pool_can_fit(c.vertex_byte_size)
               || (c.index_count > 0
                   && !pool_can_fit(c.index_count * sizeof(std::uint32_t)))
               || pool_.total_free_bytes() < need) {
            if (evict_one_lru())                                                continue;
            if (evict_lowest_priority_than(cand.session_model_id, std::uint32_t(cand.ci),
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

        // Sync fallback. Two ways to land here:
        // - A screenshot capture is pending — the deferred-capture
        //   wait would let the window manager re-layout while we wait,
        //   capturing at the wrong size. Sync loads make the chunk
        //   appear in the same frame we enqueue.
        // - Emscripten — the worker thread isn't started (no pthreads
        //   wired yet, #88), so streaming_thread_.enqueue would just
        //   queue requests with nothing to drain them. Chunks would
        //   never go resident.
#if defined(__EMSCRIPTEN__)
        // Web-sourced models (picked File or remote URL) read chunk bytes
        // asynchronously (Blob.slice / HTTP Range) — the whole file is never
        // in the heap. The chunk goes resident in the JS completion callback;
        // hold is_loading until then so it isn't re-issued every frame. The
        // embedded MEMFS sample falls through to the synchronous fopen path.
        if (cand.m->streaming_from_web) {
            // Cap concurrent chunk downloads. The browser multiplexes every
            // in-flight Range request over one HTTP/2 connection, so without a
            // cap all visible chunks download at once, split the bandwidth N
            // ways, and finish together — nothing paints until ~the whole model
            // has arrived (measured: 9 in flight → first paint after 113 of
            // 118 MB). A small cap lets the highest-priority chunks (candidates
            // are priority-sorted) finish first and paint, then the next —
            // progressive, no special first-chunk handling.
            if (streaming_web_inflight_count_ >= kMaxWebInflightChunks) {
                more_pending = true;
                // Hand the rest to the pump, in priority order, so completing
                // loads can start them without waiting for a render. This used
                // to just break, which made the fetch rate a function of the
                // frame rate: at 60fps that is fine, but the loop is on-demand
                // and quiesces, and any frame-rate drop — a heavy cull, an
                // occluded window, a background tab — throttled DOWNLOADING in
                // proportion. Measured at ~2 renders/s: 0.83 MB/s with the
                // network idle 99.6% of the time and 0.1s of decode.
                queue_web_tail(cand_idx);
                break;
            }
            c.is_loading = true;
            c.last_visible_frame_idx = streaming_frame_idx_;
            ++streaming_web_inflight_count_;
            beginWebChunkLoad(cand.session_model_id, cand.ci);
            ++enqueued;
            continue;
        }
        const bool use_sync = true;
#else
        const bool use_sync = !pending_screenshot_path_.empty();
#endif
        if (use_sync) {
            if (loadChunkBytesAndUploadGpu(*cand.m, cand.ci)) {
                ++enqueued;
                c.last_visible_frame_idx = streaming_frame_idx_;
            }
            continue;
        }

        if (streaming_thread_.enqueue(makeChunkRequest(*cand.m, cand.ci, cand.session_model_id))) {
            c.is_loading = true;
            ++enqueued;
        }
    }
    loads += enqueued;
    // Whatever the frame could not start, start now if the cap allows — and
    // leave the rest queued for the completions to drain.
    pumpWebChunkLoads();

    // Keep the render loop alive while streaming settles. The main draw + cull
    // run *before* this point in render(), so a chunk that becomes resident
    // here is only drawn on a later frame — and on web a sync load finishes
    // instantly (inFlightApprox stays 0), so a single requestFrame after a
    // load isn't enough to flush that cull→display latency. Arm a short settle
    // burst whenever there's streaming activity (a load this frame, work still
    // queued, or a visible chunk not yet resident) and bleed it down over the
    // next few frames so an on-demand render loop doesn't stall before the
    // geometry actually appears. Bounded, so the loop still quiesces at idle.
    // A chunk still waiting on pool GROWTH keeps the loop alive too. Growth is
    // asynchronous on web (a provisional sub-buffer validates a frame or two
    // later), so the driver parks its candidates in a grow-backoff cooldown
    // while it waits — and that cooldown is counted in FRAMES, which only
    // advance while the loop is alive. Left out of this test, the loop quiesced
    // after the settle burst (4 frames) but before the backoff expired (8), the
    // frame index froze, and the cooldown could then never expire: streaming
    // stalled part-loaded until the user happened to move the camera. Deadlock.
    //
    // Cooldowns that no growth can resolve are still ignored, so the loop keeps
    // quiescing at idle in the cases this test was written for: a sub-pixel
    // chunk (contribution_visible_count == 0) is never fetched at all, and a
    // chunk blocked at the pool's hard capacity — where growth cannot help and
    // eviction has already failed — genuinely has nothing to wait for.
    const bool growth_may_land = pool_.growth_pending() || pool_.can_grow();
    bool visible_pending = false;
    for (const auto& [session_model_id, m] : models_gpu_) {
        if (m.streaming_file_path.empty() || m.hidden) continue;
        for (const auto& c : m.chunks) {
            if (c.is_resident) continue;
            if (c.is_loading) { visible_pending = true; break; }
            if (c.contribution_visible_count == 0) continue;  // sub-pixel: never fetched
            const bool cooling = c.blocked_cooldown_until_frame_idx > streaming_frame_idx_;
            if (!cooling || growth_may_land) {
                visible_pending = true;
                break;
            }
        }
        if (visible_pending) break;
    }
    if (loads > 0 || more_pending || visible_pending
        || streaming_thread_.inFlightApprox() > 0) {
        streaming_settle_frames_ = kStreamingSettleFrames;
    }
    if (streaming_settle_frames_ > 0) {
        --streaming_settle_frames_;
        host_->requestFrame();
    }

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

                struct Stat { std::uint32_t session_model_id; std::size_t ci; float area; };
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
                        << "  top cand #" << i << ": model " << all[i].session_model_id
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
        for (const auto& [session_model_id, m] : models_gpu_) {
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
        c.contribution_visible_count = 0;
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

        // Passed frustum + contribution (pre-HiZ). Streaming uses this to
        // decide what's worth fetching for the current view.
        ++c.contribution_visible_count;

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

// Same contents? A plain == would need operator== on the POD payloads; these
// are trivially copyable GPU structs, so the bytes are the whole story.
template <typename T>
static bool sameBytes(const std::vector<T>& a, const std::vector<T>& b) {
    return a.size() == b.size()
        && (a.empty() || std::memcmp(a.data(), b.data(), a.size() * sizeof(T)) == 0);
}

void ViewportCore::cullModelCpuUpload(ModelGpuData& m) {
    for (auto& c : m.chunks) {
        if (!c.visible_draws_buffer || !c.prefix_sums_buffer || !c.per_chunk_uniform) continue;

        if (c.total_visible_draws == 0) {
            // Render() will skip this chunk; still zero the uniform so any
            // accidental dispatch sees 0 work — but only once. A chunk that is
            // off screen stays off screen for many frames, and re-sending four
            // zero bytes to say so was most of the per-frame write count.
            const std::uint32_t um[4] = { 0, 0, 0, 0 };
            if (std::memcmp(c.uniform_uploaded, um, sizeof(um)) != 0) {
                ++cull_writes_this_frame_;
                wgpuQueueWriteBuffer(queue_, c.per_chunk_uniform, 0, um, sizeof(um));
                std::memcpy(c.uniform_uploaded, um, sizeof(um));
            }
            continue;
        }

        // Only what actually changed. A static camera recomputes the same
        // visible set every frame, so without this the identical bytes go over
        // the wire 60 times a second — which is exactly the load phase, where
        // nothing is moving and everything is waiting on frames.
        if (!sameBytes(c.visible_draws_uploaded, c.visible_draws_scratch)) {
            const std::size_t bytes = c.visible_draws_scratch.size()
                                    * sizeof(ModelGpuData::VisibleDrawGpu);
            cull_write_bytes_this_frame_ += bytes;
            ++cull_writes_this_frame_;
            wgpuQueueWriteBuffer(queue_, c.visible_draws_buffer, 0,
                                 c.visible_draws_scratch.data(), bytes);
            c.visible_draws_uploaded = c.visible_draws_scratch;
        }
        if (!sameBytes(c.prefix_sums_uploaded, c.prefix_sums_scratch)) {
            const std::size_t bytes = c.prefix_sums_scratch.size() * sizeof(std::uint32_t);
            cull_write_bytes_this_frame_ += bytes;
            ++cull_writes_this_frame_;
            wgpuQueueWriteBuffer(queue_, c.prefix_sums_buffer, 0,
                                 c.prefix_sums_scratch.data(), bytes);
            c.prefix_sums_uploaded = c.prefix_sums_scratch;
        }

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
        if (std::memcmp(c.uniform_uploaded, um, sizeof(um)) != 0) {
            ++cull_writes_this_frame_;
            wgpuQueueWriteBuffer(queue_, c.per_chunk_uniform, 0, um, sizeof(um));
            std::memcpy(c.uniform_uploaded, um, sizeof(um));
        }
    }
}

// ===========================================================================
// Sidecar / direct load (#84-q): applyCachedModel + uploadStreamedMesh +
// uploadStreamedInstance + finalizeModel
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
        std::uint32_t session_model_id) {
    auto it = staging.find(session_model_id);
    if (it == staging.end()) {
        auto [it_new, _] = staging.emplace(
            session_model_id, std::make_unique<SidecarData>());
        return *it_new->second;
    }
    return *it->second;
}

} // namespace

void ViewportCore::applyCachedModel(std::uint32_t session_model_id,
                                    StreamingSidecar metadata) {
    if (!device_ || !queue_) {
        Log::warn() << "applyCachedModel without an initialised device";
        return;
    }

    // Replace any existing state for this id.
    auto it = models_gpu_.find(session_model_id);
    if (it != models_gpu_.end()) {
        releaseWgpuModelGpuData(it->second, pool_);
        models_gpu_.erase(it);
    }

    ModelGpuData model_gpu_data;
    model_gpu_data.vertex_bytes   = 0;  // accumulated from chunks below (v16 has no section)
    model_gpu_data.index_count    = 0;
    model_gpu_data.mesh_count     = std::uint32_t(metadata.meta.meshes.size());
    model_gpu_data.instance_count = std::uint32_t(metadata.meta.instances.size());
    model_gpu_data.streaming_file_path      = metadata.file_path;
    model_gpu_data.geometry_section_offset  = metadata.geometry_section_offset;

    // Seed the CoordinateOperation from the sidecar (v11+) so a model lands in
    // global coordinates without anyone having to push it. Before this, the
    // matrix stayed identity unless a host called setModelCoordinateOperation —
    // which only BonsaiViewer does (modules/viewport/View.cpp), so the web
    // viewer rendered every model in raw local coordinates and federated models
    // with differing map conversions came out misaligned.
    //
    // Instances are composed further down against model_gpu_data, so this has
    // to be set before that, not after.
    //
    // Desktop is unaffected: ViewportView::applyCoordinateOperation pushes the
    // same matrix derived from the same computeModelGeoref, and
    // setModelCoordinateOperation early-returns when the value is unchanged.
    model_gpu_data.has_coordinate_operation = metadata.meta.has_coordinate_operation != 0;
    if (model_gpu_data.has_coordinate_operation) {
        // Sidecar stores column-major, matching Eigen's default storage order.
        model_gpu_data.coordinate_operation_meters =
            Eigen::Map<const Eigen::Matrix4d>(metadata.meta.coordinate_operation_meters);
    }
    model_gpu_data.units.project_length_to_meters = metadata.meta.project_length_to_meters;
    model_gpu_data.units.map_unit_to_meters       = metadata.meta.map_unit_to_meters;

    // ---- Spatial chunk plan ----------------------------------------------
    // A sidecar carries a baked chunk TOC (v14): each chunk is a contiguous
    // run of meshes, laid out contiguously in the file (see SidecarLayout), so
    // we build chunks straight from it — one contiguous byte range per chunk.
    // The plan is NOT re-derived here because the float Morton quantisation
    // isn't bit-identical across toolchains (x86 baker vs wasm loader), which
    // would scatter the chunks. In-memory direct loads (finalizeModel) carry
    // no TOC, so they fall back to deriving the same Morton + greedy plan.
    const std::size_t n_meshes = metadata.meta.meshes.size();
    model_gpu_data.mesh_chunk_idx.assign(n_meshes, 0);
    model_gpu_data.mesh_chunk_local_base_vertex.assign(n_meshes, 0);
    model_gpu_data.mesh_chunk_local_ebo_first_u32.assign(n_meshes, 0);
    model_gpu_data.mesh_chunk_local_lod1_first_u32.assign(n_meshes, 0);

    std::vector<std::vector<std::uint32_t>> chunk_mesh_ids;
    std::vector<std::uint32_t>              instance_to_chunk;
    instance_to_chunk.assign(metadata.meta.instances.size(), 0);

    if (!metadata.meta.chunks.empty()) {
        // Baked TOC: chunk ci is meshes [first_mesh, first_mesh + mesh_count).
        chunk_mesh_ids.reserve(metadata.meta.chunks.size());
        for (const auto& sidecar_chunk : metadata.meta.chunks) {
            std::vector<std::uint32_t> mesh_ids;
            mesh_ids.reserve(sidecar_chunk.mesh_count);
            for (std::uint32_t k = 0; k < sidecar_chunk.mesh_count; ++k) {
                const std::uint32_t mesh_index = sidecar_chunk.first_mesh + k;
                if (mesh_index < n_meshes) mesh_ids.push_back(mesh_index);
            }
            chunk_mesh_ids.push_back(std::move(mesh_ids));
        }
    } else {
        // No TOC (direct load): derive the plan from mesh centroids.
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
        std::vector<std::uint32_t> sorted_mesh_ids = ChunkPlanner::sortMeshIdsByMorton(
            n_meshes, mesh_cx, mesh_cy, mesh_cz, mesh_inst_count);
        std::vector<std::uint32_t> mesh_vertex_count;
        mesh_vertex_count.reserve(n_meshes);
        for (std::size_t i = 0; i < n_meshes; ++i)
            mesh_vertex_count.push_back(metadata.meta.meshes[i].vertex_count);
        chunk_mesh_ids = ChunkPlanner::greedyPackChunks(
            sorted_mesh_ids, mesh_vertex_count,
            INSTANCED_VERTEX_STRIDE_BYTES,
            WGPU_CHUNK_VERTEX_BYTES_LIMIT);
    }

    {
        std::vector<std::uint32_t> mesh_to_chunk(n_meshes, 0);
        for (std::size_t chunk_index = 0; chunk_index < chunk_mesh_ids.size(); ++chunk_index) {
            for (std::uint32_t mesh_index : chunk_mesh_ids[chunk_index]) {
                mesh_to_chunk[mesh_index] = std::uint32_t(chunk_index);
            }
        }
        for (std::size_t i = 0; i < metadata.meta.instances.size(); ++i) {
            const std::uint32_t mesh_index = metadata.meta.instances[i].mesh_id;
            if (mesh_index < n_meshes) instance_to_chunk[i] = mesh_to_chunk[mesh_index];
        }
    }

    std::vector<std::uint32_t> chunk_instance_count(chunk_mesh_ids.size(), 0);
    for (std::size_t i = 0; i < instance_to_chunk.size(); ++i) {
        const std::uint32_t chunk_index = instance_to_chunk[i];
        if (chunk_index < chunk_instance_count.size()) ++chunk_instance_count[chunk_index];
    }

    // ---- Allocate per-chunk state. NO pool slices yet (chunks are
    // non-resident); the per-frame loader brings them in as cull marks
    // them visible.
    model_gpu_data.chunks.resize(chunk_mesh_ids.size());
    struct MeshLocal {
        std::uint32_t base_vertex;
        std::uint32_t ebo_first;
        std::uint32_t lod1_first;
    };
    std::vector<std::unordered_map<std::uint32_t, MeshLocal>>
        chunk_mesh_offsets(chunk_mesh_ids.size());
    for (std::size_t chunk_index = 0; chunk_index < chunk_mesh_ids.size(); ++chunk_index) {
        ModelGpuData::Chunk& chunk = model_gpu_data.chunks[chunk_index];
        chunk.mesh_ids    = std::move(chunk_mesh_ids[chunk_index]);
        chunk.is_resident = false;

        std::uint32_t chunk_local_vertex_count = 0;
        std::uint32_t chunk_local_index_count = 0;
        for (std::uint32_t mesh_index : chunk.mesh_ids) {
            const MeshInfo& mesh = metadata.meta.meshes[mesh_index];
            model_gpu_data.mesh_chunk_idx[mesh_index] = std::uint32_t(chunk_index);
            model_gpu_data.mesh_chunk_local_base_vertex[mesh_index] = chunk_local_vertex_count;
            model_gpu_data.mesh_chunk_local_ebo_first_u32[mesh_index] = chunk_local_index_count;
            chunk_mesh_offsets[chunk_index][mesh_index] =
                MeshLocal{chunk_local_vertex_count, chunk_local_index_count, 0};
            chunk_local_vertex_count += mesh.vertex_count;
            chunk_local_index_count += mesh.index_count;
        }
        std::uint32_t chunk_local_lod1 = 0;
        for (std::uint32_t mesh_index : chunk.mesh_ids) {
            const MeshInfo& mesh = metadata.meta.meshes[mesh_index];
            if (mesh.lod1_index_count == 0) continue;
            model_gpu_data.mesh_chunk_local_lod1_first_u32[mesh_index] =
                chunk_local_index_count + chunk_local_lod1;
            chunk_mesh_offsets[chunk_index][mesh_index].lod1_first =
                chunk_local_index_count + chunk_local_lod1;
            chunk_local_lod1 += mesh.lod1_index_count;
        }
        chunk.vertex_count     = chunk_local_vertex_count;
        chunk.vertex_byte_size = std::uint64_t(chunk_local_vertex_count) * INSTANCED_VERTEX_STRIDE_BYTES;
        chunk.index_count      = chunk_local_index_count + chunk_local_lod1;
        chunk.lod1_index_count = chunk_local_lod1;
        // v16: compressed-blob locators from the baked TOC (streaming path).
        if (chunk_index < metadata.meta.chunks.size()) {
            const SidecarChunk& sidecar_chunk = metadata.meta.chunks[chunk_index];
            chunk.v_comp_off = sidecar_chunk.v_comp_off;
            chunk.v_comp_size = sidecar_chunk.v_comp_size;
            chunk.i_comp_off = sidecar_chunk.i_comp_off;
            chunk.i_comp_size = sidecar_chunk.i_comp_size;
        }
        model_gpu_data.vertex_bytes += chunk.vertex_byte_size;
        model_gpu_data.index_count  += std::uint32_t(chunk.index_count);

        // Small per-chunk buffers, allocated upfront so cull can write into
        // them. visible_draws_buffer cap = chunk's instance count.
        const std::size_t chunk_inst = std::max<std::size_t>(chunk_instance_count[chunk_index], 1);
        const std::size_t draws_bytes = chunk_inst * sizeof(ModelGpuData::VisibleDrawGpu);
        const std::size_t ps_bytes    = (chunk_inst + 1) * sizeof(std::uint32_t);

        WGPUBufferDescriptor vd_desc = {};
        vd_desc.size  = std::max<std::uint64_t>(draws_bytes, 16);
        vd_desc.usage = WGPUBufferUsage_Storage | WGPUBufferUsage_CopyDst;
        vd_desc.label = svFromCStr("model.chunk.visible_draws");
        chunk.visible_draws_buffer   = wgpuDeviceCreateBuffer(device_, &vd_desc);
        chunk.visible_draws_capacity = chunk_inst;
        model_gpu_data.vram_bytes_ssbo += vd_desc.size;

        WGPUBufferDescriptor ps_desc = {};
        ps_desc.size  = std::max<std::uint64_t>(ps_bytes, 16);
        ps_desc.usage = WGPUBufferUsage_Storage | WGPUBufferUsage_CopyDst;
        ps_desc.label = svFromCStr("model.chunk.prefix_sums");
        chunk.prefix_sums_buffer   = wgpuDeviceCreateBuffer(device_, &ps_desc);
        chunk.prefix_sums_capacity = chunk_inst + 1;
        model_gpu_data.vram_bytes_ssbo += ps_desc.size;

        WGPUBufferDescriptor mu_desc = {};
        mu_desc.size  = 16;
        mu_desc.usage = WGPUBufferUsage_Uniform | WGPUBufferUsage_CopyDst;
        mu_desc.label = svFromCStr("model.chunk.uniform");
        chunk.per_chunk_uniform = wgpuDeviceCreateBuffer(device_, &mu_desc);
        model_gpu_data.vram_bytes_ssbo += 16;

        chunk.visible_draws_scratch.reserve(chunk_inst);
        chunk.prefix_sums_scratch.reserve(chunk_inst + 1);
    }

    // Index section is NOT loaded upfront. Each chunk's index slice is
    // range-read alongside its vertex bytes in loadChunkBytesAndUploadGpu.

    // MeshGpu storage (per-mesh quant basis).
    std::vector<MeshGpu> mesh_gpu;
    mesh_gpu.reserve(metadata.meta.meshes.size());
    for (const auto& mesh_info : metadata.meta.meshes) {
        MeshGpu mesh_gpu_record = {};
        mesh_gpu_record.aabb_min[0] = mesh_info.local_aabb_min[0];
        mesh_gpu_record.aabb_min[1] = mesh_info.local_aabb_min[1];
        mesh_gpu_record.aabb_min[2] = mesh_info.local_aabb_min[2];
        mesh_gpu_record.aabb_max[0] = mesh_info.local_aabb_max[0];
        mesh_gpu_record.aabb_max[1] = mesh_info.local_aabb_max[1];
        mesh_gpu_record.aabb_max[2] = mesh_info.local_aabb_max[2];
        mesh_gpu.push_back(mesh_gpu_record);
    }
    const std::size_t mesh_storage_bytes = mesh_gpu.size() * sizeof(MeshGpu);
    model_gpu_data.mesh_storage = createBufferWithData(
        device_, queue_,
        mesh_gpu.data(), mesh_storage_bytes,
        WGPUBufferUsage_Storage,
        "model.mesh_storage");
    model_gpu_data.vram_bytes_ssbo += mesh_storage_bytes;

    // InstanceGpu storage. Rebase object_ids globally.
    const std::uint32_t object_id_base = next_object_id_;
    std::uint32_t max_local_id = 0;
    std::vector<InstanceGpu> inst_gpu;
    inst_gpu.reserve(metadata.meta.instances.size());
    for (auto& instance_cpu : metadata.meta.instances) {
        if (instance_cpu.object_id > max_local_id) max_local_id = instance_cpu.object_id;
        instance_cpu.object_id = object_id_base + instance_cpu.object_id;
        InstanceGpu instance_gpu = {};
        std::memcpy(instance_gpu.transform, instance_cpu.transform, sizeof(instance_gpu.transform));
        instance_gpu.object_id            = instance_cpu.object_id;
        instance_gpu.color_override_rgba8 = instance_cpu.color_override_rgba8;
        instance_gpu.mesh_id              = instance_cpu.mesh_id;
        inst_gpu.push_back(instance_gpu);
    }
    next_object_id_ = object_id_base + max_local_id + 1;
    model_gpu_data.object_id_base = object_id_base;  // element metadata records rebase to match
    const std::size_t inst_storage_bytes = inst_gpu.size() * sizeof(InstanceGpu);
    model_gpu_data.instance_storage = createBufferWithData(
        device_, queue_,
        inst_gpu.data(), inst_storage_bytes,
        WGPUBufferUsage_Storage,
        "model.instance_storage");
    model_gpu_data.vram_bytes_ssbo += inst_storage_bytes;

    // Hand off CPU mirrors.
    model_gpu_data.meshes    = std::move(metadata.meta.meshes);
    model_gpu_data.instances = std::move(metadata.meta.instances);

    // Where the element metadata block lives. The web path fetches that block
    // lazily (loadElementMetadataWeb), so it must arrive here already knowing
    // WHERE to fetch from: a model that is in the scene but whose locator is
    // still unknown is indistinguishable from one that has no element block at
    // all, and loadElementMetadataWeb would latch it as permanently empty.
    model_gpu_data.element_metadata_comp_offset = metadata.element_metadata_comp_offset;
    model_gpu_data.element_metadata_comp_size   = metadata.element_metadata_comp_size;
    model_gpu_data.element_metadata_raw_size    = metadata.element_metadata_raw_size;

    // Element metadata, when the caller already read it. readSidecarMetadata
    // parses the block up front, so a path-based load arrives with it in hand;
    // the web byte-range path deliberately skips it (first paint must not wait
    // on it) and fetches later via loadElementMetadataWeb, arriving here empty.
    // Either way the rebase is the same and happens here — this function is the
    // sole authority on object_id_base.
    if (!metadata.meta.elements.empty()) {
        model_gpu_data.elements     = std::move(metadata.meta.elements);
        model_gpu_data.string_table = std::move(metadata.meta.string_table);
        for (auto& e : model_gpu_data.elements) e.object_id += object_id_base;
        model_gpu_data.element_metadata_loaded = true;
    }

    // Streaming defers per-mesh vertex data until the owning chunk is
    // loaded. Both volumes + Area-tool CPU shadow fill in per-chunk
    // inside applyStreamedChunk as the bytes arrive.
    model_gpu_data.mesh_local_volumes.assign(model_gpu_data.meshes.size(), 0.0);
    model_gpu_data.mesh_triangles_cache.assign(model_gpu_data.meshes.size(), ModelGpuData::MeshTriangles{});
    model_gpu_data.mesh_has_alpha.assign(model_gpu_data.meshes.size(), std::uint8_t(0));

    // object_id → instance index lookup. Volume tool reads it on every
    // selection mutation; per-pick latency stays O(K) instead of O(K*N).
    model_gpu_data.object_id_to_instance.clear();
    model_gpu_data.object_id_to_instance.reserve(model_gpu_data.instances.size());
    for (std::uint32_t i = 0; i < std::uint32_t(model_gpu_data.instances.size()); ++i) {
        model_gpu_data.object_id_to_instance.emplace(model_gpu_data.instances[i].object_id, i);
    }

    // Per-chunk world AABBs + instance-id lists from instance_to_chunk.
    for (std::size_t chunk_index = 0; chunk_index < model_gpu_data.chunks.size(); ++chunk_index) {
        model_gpu_data.chunks[chunk_index].instance_ids.reserve(
            model_gpu_data.instances.size() / model_gpu_data.chunks.size() + 4);
    }
    for (std::uint32_t inst_idx = 0; inst_idx < std::uint32_t(model_gpu_data.instances.size()); ++inst_idx) {
        const auto& inst = model_gpu_data.instances[inst_idx];
        const std::uint32_t chunk_index = instance_to_chunk[inst_idx];
        if (chunk_index >= model_gpu_data.chunks.size()) continue;
        auto& chunk = model_gpu_data.chunks[chunk_index];
        for (int a = 0; a < 3; ++a) {
            chunk.aabb_min[a] = std::min(chunk.aabb_min[a], inst.world_aabb_min[a]);
            chunk.aabb_max[a] = std::max(chunk.aabb_max[a], inst.world_aabb_max[a]);
        }
        chunk.instance_ids.push_back(inst_idx);
    }

    // Populate per-instance arrays from the per-chunk per-mesh offsets
    // computed during chunk construction.
    {
        const std::size_t n_inst = model_gpu_data.instances.size();
        model_gpu_data.instance_chunk_idx.assign(n_inst, 0);
        model_gpu_data.instance_base_vertex.assign(n_inst, 0);
        model_gpu_data.instance_ebo_first_u32.assign(n_inst, 0);
        model_gpu_data.instance_lod1_first_u32.assign(n_inst, 0);
        for (std::size_t i = 0; i < n_inst; ++i) {
            const std::uint32_t chunk_index = instance_to_chunk[i];
            const std::uint32_t mesh_index = model_gpu_data.instances[i].mesh_id;
            if (chunk_index >= chunk_mesh_offsets.size()) continue;
            auto it_off = chunk_mesh_offsets[chunk_index].find(mesh_index);
            if (it_off == chunk_mesh_offsets[chunk_index].end()) continue;
            model_gpu_data.instance_chunk_idx[i]      = chunk_index;
            model_gpu_data.instance_base_vertex[i]    = it_off->second.base_vertex;
            model_gpu_data.instance_ebo_first_u32[i]  = it_off->second.ebo_first;
            model_gpu_data.instance_lod1_first_u32[i] = it_off->second.lod1_first;
        }
    }

    auto [inserted, _] = models_gpu_.emplace(session_model_id, std::move(model_gpu_data));
    ModelGpuData& inserted_model = inserted->second;

    Log::info()
        << "[wgpu stream] applyCachedModel session_model_id=" << session_model_id
        << " verts=" << inserted_model.vertex_bytes << "B (deferred)"
        << " idx="   << inserted_model.index_count
        << " meshes=" << inserted_model.mesh_count
        << " instances=" << inserted_model.instance_count
        << " chunks=" << inserted_model.chunks.size();

    // The instance transforms above came straight from the sidecar, where they
    // were baked with identity federation matrices. Recompose whenever any of
    // them is now non-identity, or the model renders in the wrong place:
    //
    //   - its own CoordinateOperation, seeded above — a georeferenced model
    //     would otherwise draw at its local coordinates;
    //   - a federated false origin already in force, which is the normal case
    //     for the SECOND and later models of a federation.
    //
    // Desktop never hit this because BonsaiViewer pushes
    // setModelCoordinateOperation + setModelTransformation after every load and
    // each of those recomposes. Nothing does that on web.
    if (inserted_model.has_coordinate_operation ||
        !federated_false_origin_meters_.isIdentity()) {
        recomposeAndUploadModel(session_model_id);
    }

    if (!initial_view_applied_) {
        viewAll();
        initial_view_applied_ = true;
    }
    ensureSelectionFlagsBuffer();
    host_->requestFrame();
}

void ViewportCore::uploadStreamedMesh(const StreamedMesh& mesh) {
    if (mesh.vertices.empty() || mesh.indices.empty()) return;
    SidecarData& staging = getOrCreateDirectStaging(pending_direct_loads_, mesh.session_model_id);

    // Streamer format: 7 floats / vertex (pos3 + normal3 + color-as-float).
    // Same quantisation as SidecarBuilder::onMeshReady so direct-load and
    // sidecar-load produce byte-identical GPU buffers.
    const std::size_t n_verts = mesh.vertices.size() / INSTANCED_VERTEX_STRIDE_FLOATS;

    float bmin[3] = {  std::numeric_limits<float>::infinity(),
                       std::numeric_limits<float>::infinity(),
                       std::numeric_limits<float>::infinity() };
    float bmax[3] = { -std::numeric_limits<float>::infinity(),
                      -std::numeric_limits<float>::infinity(),
                      -std::numeric_limits<float>::infinity() };
    for (std::size_t i = 0; i < n_verts; ++i) {
        const float* vertex = mesh.vertices.data() + i * INSTANCED_VERTEX_STRIDE_FLOATS;
        for (int a = 0; a < 3; ++a) {
            if (vertex[a] < bmin[a]) bmin[a] = vertex[a];
            if (vertex[a] > bmax[a]) bmax[a] = vertex[a];
        }
    }
    float extent_recip[3];
    for (int a = 0; a < 3; ++a) {
        const float ext = bmax[a] - bmin[a];
        extent_recip[a] = ext > 0.0f ? 1.0f / ext : 0.0f;
    }

    const std::size_t vb_offset = staging.vertices.size();
    staging.vertices.resize(vb_offset + n_verts * INSTANCED_VERTEX_STRIDE_BYTES);
    for (std::size_t i = 0; i < n_verts; ++i) {
        quantizeVertex(mesh.vertices.data() + i * INSTANCED_VERTEX_STRIDE_FLOATS,
                       bmin, extent_recip,
                       staging.vertices.data() + vb_offset
                           + i * INSTANCED_VERTEX_STRIDE_BYTES);
    }

    const std::size_t ib_offset = staging.indices.size();
    staging.indices.insert(staging.indices.end(),
                     mesh.indices.begin(), mesh.indices.end());

    MeshInfo info{};
    info.vbo_byte_offset = std::uint32_t(vb_offset);
    info.vertex_count    = std::uint32_t(n_verts);
    info.ebo_byte_offset = std::uint32_t(ib_offset * sizeof(std::uint32_t));
    info.index_count     = std::uint32_t(mesh.indices.size());
    for (int a = 0; a < 3; ++a) {
        info.local_aabb_min[a] = bmin[a];
        info.local_aabb_max[a] = bmax[a];
    }
    info.first_instance       = 0;
    info.instance_count       = 0;
    info.lod1_ebo_byte_offset = 0;
    info.lod1_index_count     = 0;

    if (staging.meshes.size() <= mesh.local_mesh_id) {
        staging.meshes.resize(mesh.local_mesh_id + 1);
    }
    staging.meshes[mesh.local_mesh_id] = info;
}

void ViewportCore::uploadStreamedInstance(const StreamedInstance& instance_record) {
    SidecarData& staging = getOrCreateDirectStaging(pending_direct_loads_, instance_record.session_model_id);

    InstanceInfo instance{};
    instance.mesh_id              = instance_record.local_mesh_id;
    instance.object_id            = instance_record.object_id;
    instance.color_override_rgba8 = instance_record.color_override_rgba8;
    instance.session_model_id             = instance_record.session_model_id;
    std::memcpy(instance.placement_transformation, instance_record.transform,
                sizeof(instance.placement_transformation));
    for (int i = 0; i < 16; ++i) {
        instance.transform[i] = float(instance_record.transform[i]);
    }
    std::memcpy(instance.world_aabb_min, instance_record.world_aabb_min, sizeof(instance.world_aabb_min));
    std::memcpy(instance.world_aabb_max, instance_record.world_aabb_max, sizeof(instance.world_aabb_max));

    staging.instances.push_back(instance);
}

std::uint32_t ViewportCore::loadSidecarFromPath(const std::string& path) {
    if (!device_ || !queue_) {
        Log::warn() << "loadSidecarFromPath: wgpu not initialised";
        return 0;
    }
    auto meta_opt = readSidecarMetadata(path);
    if (!meta_opt) {
        Log::warn() << "loadSidecarFromPath: could not read sidecar metadata from " << path;
        return 0;
    }
    const std::uint32_t session_model_id = next_session_model_id_++;
    applyCachedModel(session_model_id, std::move(*meta_opt));
    return session_model_id;
}

#if defined(__EMSCRIPTEN__)
// ===========================================================================
// Web byte-range streaming (#88): Blob.slice source + async chunk loads
// ===========================================================================
//
// The desktop streaming path fopen()s the sidecar and fread()s chunk byte
// ranges synchronously from a worker thread. On web there is no worker (no
// pthreads yet) and Blob.slice() is inherently async, so chunk bytes are
// pulled through the JS event loop: webReadRangesAsync issues one Blob.slice
// per coalesced read plan, scatters the bytes into the destination, then
// invokes a continuation once the whole range set has landed. The picked
// File stays in JS (Module.__ifcvFile) — only chunk-sized slices ever enter
// the wasm heap, so a 500 MB sidecar never does.

namespace {

// Byte-source registry (multi-file federation). Module.__ifcvSources[id] is
// { file: File|null, url: string|null, size: number } — a picked File or a
// remote URL, registered + sized by shell.html before the load. Several models
// can stream from different sources at once (the web analog of the desktop
// per-model streaming_file_path). Size of source `sid`, or 0 if unknown.
EM_JS(double, ifcvSourceSize, (int sid), {
    var s = Module["__ifcvSources"] && Module["__ifcvSources"][sid];
    return s ? (s.size || 0) : 0;
});

// Read [offset, offset+size) of source `sid` into dst (which must hold `size`
// bytes), then call back _ifcv_on_range_done(reqId, ok). Async. File:
// Blob.slice. URL: an HTTP Range request — if a server ignores Range and
// returns the whole body (200), slice out the requested window so it still
// works (just without the bandwidth saving).
EM_JS(void, ifcvReadRangeInto, (int sid, int reqId, double offset, double size, void* dst), {
    var deliver = function(ok, buf) {
        if (ok && buf) {
            HEAPU8.set(new Uint8Array(buf), dst);
            Module["__ifcvBytesLoaded"] = (Module["__ifcvBytesLoaded"] || 0) + buf.byteLength;
        }
        Module["_ifcv_on_range_done"](reqId, ok ? 1 : 0);
    };
    var s = Module["__ifcvSources"] && Module["__ifcvSources"][sid];
    if (s && s.file) {
        s.file.slice(offset, offset + size).arrayBuffer()
            .then(function(buf) { deliver(1, buf); })
            .catch(function(e) { deliver(0, null); });
        return;
    }
    if (s && s.url) {
        var end = offset + size - 1;
        fetch(s.url, { headers: { "Range": "bytes=" + offset + "-" + end } })
            .then(function(resp) {
                if (resp.status !== 206 && resp.status !== 200) { deliver(0, null); return; }
                var full = resp.status === 200;
                return resp.arrayBuffer().then(function(buf) {
                    if (full && buf.byteLength > size) buf = buf.slice(offset, offset + size);
                    deliver(1, buf);
                });
            })
            .catch(function(e) { deliver(0, null); });
        return;
    }
    Module["_ifcv_on_range_done"](reqId, 0);
});

// One in-flight multi-range read: a sequence of coalesced plans, each read
// into `scratch` then scattered into `out`. `done(ok, out)` fires once every
// plan has landed, or on the first failure.
struct WebRangeRead {
    int                          source_id = 0;  // Module.__ifcvSources index
    std::vector<SidecarReadPlan> plans;
    std::size_t                  plan_idx = 0;
    std::vector<std::uint8_t>    scratch;
    std::vector<std::uint8_t>    out;
    std::function<void(bool, std::vector<std::uint8_t>&&)> done;
};

std::unordered_map<int, WebRangeRead> g_web_reads;
int g_web_read_next = 1;

// Issue the current plan's Blob.slice, or finish (success) if all plans done.
void webIssueCurrentPlan(int id) {
    auto it = g_web_reads.find(id);
    if (it == g_web_reads.end()) return;
    WebRangeRead& r = it->second;
    if (r.plan_idx >= r.plans.size()) {
        auto done = std::move(r.done);
        std::vector<std::uint8_t> out = std::move(r.out);
        g_web_reads.erase(it);
        if (done) done(true, std::move(out));
        return;
    }
    const SidecarReadPlan& plan = r.plans[r.plan_idx];
    r.scratch.assign(std::size_t(plan.read_size), 0);
    ifcvReadRangeInto(r.source_id, id, double(plan.file_offset), double(plan.read_size),
                      r.scratch.data());
}

// Read `ranges` (section-relative (offset,size)) into a destination laid out
// in input order, then call done(true, bytes). On any failure: done(false,{}).
// `section_offset` makes the offsets absolute (pass 0 if already absolute).
void webReadRangesAsync(
        int source_id,
        std::uint64_t section_offset,
        const std::vector<std::pair<std::uint64_t, std::uint64_t>>& ranges,
        std::function<void(bool, std::vector<std::uint8_t>&&)> done) {
    std::uint64_t total = 0;
    for (const auto& rg : ranges) total += rg.second;

    WebRangeRead r;
    r.source_id = source_id;
    r.out.assign(std::size_t(total), 0);
    // Coalesce within 1 MB: each Blob.slice is an async round trip, so a
    // generous gap trades a few wasted bytes for far fewer JS hops.
    r.plans = planSidecarReadRanges(section_offset, ranges, std::uint64_t(1) << 20);
    r.done  = std::move(done);

    if (r.plans.empty()) {  // nothing to read — complete synchronously
        if (r.done) r.done(true, std::move(r.out));
        return;
    }
    const int id = g_web_read_next++;
    g_web_reads.emplace(id, std::move(r));
    webIssueCurrentPlan(id);
}

}  // namespace

// JS completion callback for one Blob.slice plan. Scatters the landed bytes
// and advances to the next plan, or fails the whole read. Exported as
// _ifcv_on_range_done (see ifcviewer-web/CMakeLists.txt).
extern "C" EMSCRIPTEN_KEEPALIVE void ifcv_on_range_done(int reqId, int ok) {
    auto it = g_web_reads.find(reqId);
    if (it == g_web_reads.end()) return;
    WebRangeRead& r = it->second;
    if (!ok) {
        auto done = std::move(r.done);
        g_web_reads.erase(it);
        if (done) done(false, {});
        return;
    }
    const SidecarReadPlan& plan = r.plans[r.plan_idx];
    for (const auto& s : plan.slices) {
        std::memcpy(r.out.data() + s.dst_offset,
                    r.scratch.data() + s.src_offset, std::size_t(s.bytes));
    }
    ++r.plan_idx;
    webIssueCurrentPlan(reqId);
}

#endif  // __EMSCRIPTEN__

// Deliberately outside the web-streaming block above, unlike its neighbours:
// driveStreamingLoads calls this unconditionally and ViewportCore.h declares it
// unconditionally, so desktop needs a definition to link against. The body
// guards itself instead, compiling to a no-op off the web — there is nothing to
// pump when chunk loads are not asynchronous.

// Start queued chunk loads until the in-flight cap is reached. Called at the
// end of driveStreamingLoads and, more importantly, from every load's
// completion — so the fetch pipeline refills itself instead of waiting for the
// next render.
//
// The queue is a snapshot of the last frame's priorities and may be stale by
// the time a completion drains it: the camera can have moved, the chunk can
// have gone resident by another route, the pool can have filled. So every entry
// is re-checked against live state here, exactly as driveStreamingLoads checks
// its own candidates. A stale-but-close priority order beats waiting a frame
// for a fresh one.
void ViewportCore::pumpWebChunkLoads() {
#if defined(__EMSCRIPTEN__)
    while (streaming_web_inflight_count_ < kMaxWebInflightChunks
           && web_pending_head_ < web_pending_.size()) {
        const PendingWebChunk next = web_pending_[web_pending_head_++];
        auto it = models_gpu_.find(next.session_model_id);
        if (it == models_gpu_.end()) continue;
        ModelGpuData& m = it->second;
        if (m.hidden || next.ci >= m.chunks.size()) continue;
        auto& c = m.chunks[next.ci];
        if (c.is_resident || c.is_loading)     continue;
        if (c.contribution_visible_count == 0) continue;   // no longer worth drawing
        if (c.blocked_cooldown_until_frame_idx > streaming_frame_idx_) continue;

        // Room, or the prospect of room. Eviction is deliberately NOT attempted
        // here — it is stamped against the frame index and interleaved with the
        // cull, so it stays where it can reason about what is visible. If the
        // pool is full the rest of the queue is dropped and the next frame,
        // which can evict, decides afresh.
        const std::uint64_t need = c.vertex_byte_size
                                 + c.index_count * sizeof(std::uint32_t);
        if (pool_.largest_free_run_bytes() < need && !pool_.can_grow()) {
            web_pending_head_ = web_pending_.size();
            break;
        }

        c.is_loading = true;
        c.last_visible_frame_idx = streaming_frame_idx_;
        ++streaming_web_inflight_count_;
        beginWebChunkLoad(next.session_model_id, next.ci);
    }
#endif
}

#if defined(__EMSCRIPTEN__)   // resume the web-streaming block

void ViewportCore::beginWebChunkLoad(std::uint32_t session_model_id, std::size_t chunk_idx) {
    auto it = models_gpu_.find(session_model_id);
    if (it == models_gpu_.end()) return;
    ModelGpuData& m = it->second;
    if (chunk_idx >= m.chunks.size()) return;

    const ModelGpuData::Chunk& c = m.chunks[chunk_idx];
    const int sid = m.web_source_id;  // which registered byte-source to read from
    const std::uint64_t geom        = m.geometry_section_offset;
    const std::uint64_t v_comp_off  = c.v_comp_off,  v_comp_size = c.v_comp_size;
    const std::uint64_t i_comp_off  = c.i_comp_off,  i_comp_size = c.i_comp_size;
    const std::uint64_t v_raw       = c.vertex_byte_size;
    const std::uint64_t i_raw       = std::uint64_t(c.index_count) * sizeof(std::uint32_t);

    // Reserve the RAW (decompressed) footprint while in flight so
    // driveStreamingLoads doesn't over-commit the pool.
    const std::uint64_t need = v_raw + i_raw;
    streaming_web_inflight_bytes_ += need;

    // Fetch the chunk's two zstd frames CONCURRENTLY (vertex + index) and join
    // when both land, then decompress and apply. Re-look-up the model at apply
    // time: a resetScene() could have landed mid-flight.
    struct ChunkJoin {
        std::vector<std::uint8_t> vz, iz;  // compressed frames
        bool v_done = false, i_done = false, v_ok = false, i_ok = false;
    };
    auto join = std::make_shared<ChunkJoin>();
    std::function<void()> finish =
        [this, session_model_id, chunk_idx, need, v_raw, i_raw, join]() {
        if (!join->v_done || !join->i_done) return;  // wait for the other frame
        streaming_web_inflight_bytes_ -= std::min(streaming_web_inflight_bytes_, need);
        if (streaming_web_inflight_count_ > 0) --streaming_web_inflight_count_;
        host_->requestFrame();

        auto mit = models_gpu_.find(session_model_id);
        if (mit == models_gpu_.end()) return;
        ModelGpuData& mm = mit->second;
        if (chunk_idx >= mm.chunks.size()) return;
        auto& cc = mm.chunks[chunk_idx];
        cc.is_loading = false;

        // emscripten_get_now, not Stopwatch: this is web-only code and the
        // Stopwatch header is included further down the file than here.
        const double apply_t0 = emscripten_get_now();
        std::vector<std::uint8_t>  vbytes(static_cast<std::size_t>(v_raw));
        std::vector<std::uint32_t> idx(static_cast<std::size_t>(i_raw / sizeof(std::uint32_t)));
        const bool ok = join->v_ok && join->i_ok
            && SidecarCompress::decompress(join->vz.data(), join->vz.size(),
                                           vbytes.data(), vbytes.size())
            && SidecarCompress::decompress(join->iz.data(), join->iz.size(),
                                           reinterpret_cast<std::uint8_t*>(idx.data()),
                                           std::size_t(i_raw));
        chunk_apply_ms_total_ += emscripten_get_now() - apply_t0;
        chunk_apply_raw_bytes_ += v_raw + i_raw;
        ++chunk_apply_count_;
        if (!ok || !applyStreamedChunk(mm, chunk_idx, vbytes, idx)) {
            cc.blocked_cooldown_until_frame_idx = streaming_frame_idx_
                + (pool_.can_grow() ? kGrowBackoffFrames : kBlockedCooldownFrames);
            pumpWebChunkLoads();   // this one is parked; get on with the rest
            return;
        }
        host_->requestFrame();
        // Refill the pipeline now rather than on the next render. After the
        // apply, so the pool reservation this chunk just released is real
        // before the next one reserves against it.
        pumpWebChunkLoads();
    };

    webReadRangesAsync(sid, geom, {{v_comp_off, v_comp_size}},
        [join, finish](bool ok, std::vector<std::uint8_t>&& vz) {
            join->v_ok = ok; join->vz = std::move(vz); join->v_done = true; finish();
        });
    webReadRangesAsync(sid, geom, {{i_comp_off, i_comp_size}},
        [join, finish](bool ok, std::vector<std::uint8_t>&& iz) {
            join->i_ok = ok; join->iz = std::move(iz); join->i_done = true; finish();
        });
}

// Source-agnostic metadata bootstrap. The active byte-source (local File or
// remote URL) is already set on the JS side, so this reads via ifcvFileSize +
// webReadRangesAsync without caring which it is: head (16 B) → num_vertex_bytes;
// the 4-byte index count after the vertex section; then the metadata tail
// (index-section end .. EOF). The bulk vertex/index sections are never read
// here — they stream per chunk through beginWebChunkLoad. `source_label` is a
// log/identity tag stored as file_path (chunk reads go through the JS source,
// not this path).
void ViewportCore::loadSidecarMetadataWeb(int source_id, std::string source_label,
                                          std::function<void(std::uint32_t)> on_loaded) {
    if (!device_ || !queue_) {
        Log::warn() << "loadSidecarMetadataWeb: wgpu not initialised";
        return;
    }
    const double fsize = ifcvSourceSize(source_id);
    if (fsize <= 0.0) {
        Log::warn() << "loadSidecarMetadataWeb: source " << source_id << " has zero size";
        return;
    }

    // Mint the session model id HERE, synchronously, rather than at the end of
    // the read chain below. Session ids are what orders the scene's models —
    // modelIdsInLoadOrder sorts by them, and every per-model slot a host sees
    // (modelProgress's index, ElementRef::model_index) is a rank in that order.
    // Minting on completion made that rank the order the models' network reads
    // happened to finish in, so with several federated models in flight the
    // slots came out shuffled against the order the host added them and a pick
    // was attributed to the wrong file. Requesting order is the order the host
    // asked for, which is the order it can reason about. A load that fails
    // partway simply abandons its id — the ranks compact over whatever models
    // made it into the scene, exactly as before.
    const std::uint32_t session_model_id = next_session_model_id_++;

    // Head (v16): [header 12][geom_bytes 8]. The two compressed metadata blocks
    // follow the compressed geometry at SIDECAR_HEAD_BYTES + geom_bytes.
    webReadRangesAsync(source_id, 0, {{0, SIDECAR_HEAD_BYTES}},
        [this, fsize, source_id, source_label, session_model_id,
         on_loaded = std::move(on_loaded)]
        (bool ok, std::vector<std::uint8_t>&& head) mutable {
            std::uint64_t geom_bytes = 0;
            if (!ok || !parseSidecarHead(head.data(), head.size(), geom_bytes)) {
                Log::warn() << "loadSidecarMetadataWeb: bad sidecar head (wrong version?)";
                return;
            }
            const std::uint64_t meta_off = std::uint64_t(SIDECAR_HEAD_BYTES) + geom_bytes;
            if (double(meta_off + 16) > fsize) {
                Log::warn() << "loadSidecarMetadataWeb: metadata past EOF";
                return;
            }
            // Geometry metadata block on disk: [comp u64][raw u64][zstd frame].
            webReadRangesAsync(source_id, 0, {{meta_off, 16}},
                [this, fsize, meta_off, source_id, source_label, session_model_id,
                 on_loaded = std::move(on_loaded)]
                (bool ok2, std::vector<std::uint8_t>&& h) {
                    if (!ok2 || h.size() < 16) {
                        Log::warn() << "loadSidecarMetadataWeb: short geometry metadata header";
                        return;
                    }
                    std::uint64_t geometry_metadata_comp = 0, geometry_metadata_raw = 0;
                    std::memcpy(&geometry_metadata_comp, h.data(), 8);
                    std::memcpy(&geometry_metadata_raw, h.data() + 8, 8);
                    const std::uint64_t geometry_metadata_off = meta_off + 16;
                    if (double(geometry_metadata_off + geometry_metadata_comp + 16) > fsize) {
                        Log::warn() << "loadSidecarMetadataWeb: geometry metadata past EOF";
                        return;
                    }
                    webReadRangesAsync(source_id, 0,
                        {{geometry_metadata_off, geometry_metadata_comp}},
                        [this, geometry_metadata_off, geometry_metadata_comp,
                         geometry_metadata_raw, source_id, source_label,
                         session_model_id, on_loaded = std::move(on_loaded)]
                        (bool ok3, std::vector<std::uint8_t>&& cz) {
                            if (!ok3) {
                                Log::warn() << "loadSidecarMetadataWeb: geometry metadata read failed";
                                return;
                            }
                            std::vector<std::uint8_t> geometry_metadata(
                                static_cast<std::size_t>(geometry_metadata_raw));
                            if (!SidecarCompress::decompress(cz.data(), cz.size(),
                                                             geometry_metadata.data(),
                                                             geometry_metadata.size())) {
                                Log::warn() << "loadSidecarMetadataWeb: geometry metadata decompress failed";
                                return;
                            }
                            StreamingSidecar sc;
                            sc.file_path               = source_label;
                            sc.geometry_section_offset = SIDECAR_HEAD_BYTES;
                            if (!parseSidecarGeometryMetadata(geometry_metadata.data(),
                                                              geometry_metadata.size(), sc.meta)) {
                                Log::warn() << "loadSidecarMetadataWeb: bad geometry metadata";
                                return;
                            }
                            // Read the element metadata block's 16-byte header to
                            // learn where that block lives, and only THEN put the
                            // model in the scene. Doing it the other way round
                            // leaves a window in which the model is loaded but its
                            // locator is still zero — and a loadElementMetadataWeb
                            // landing in that window (a host page calling
                            // getObjects() as soon as the model appears) cannot
                            // tell "locator not read yet" from "this sidecar has no
                            // element block", so it latches the model as
                            // permanently empty. It costs one extra 16-byte
                            // round-trip before first paint.
                            const std::uint64_t element_metadata_hdr_off =
                                geometry_metadata_off + geometry_metadata_comp;
                            webReadRangesAsync(source_id, 0, {{element_metadata_hdr_off, 16}},
                                [this, sc = std::move(sc), element_metadata_hdr_off,
                                 source_id, source_label, session_model_id,
                                 on_loaded = std::move(on_loaded)]
                                (bool ok4, std::vector<std::uint8_t>&& dh) mutable {
                                    if (ok4 && dh.size() >= 16) {
                                        std::uint64_t dc = 0, dr = 0;
                                        std::memcpy(&dc, dh.data(), 8);
                                        std::memcpy(&dr, dh.data() + 8, 8);
                                        sc.element_metadata_comp_offset = element_metadata_hdr_off + 16;
                                        sc.element_metadata_comp_size   = dc;
                                        sc.element_metadata_raw_size    = dr;
                                    } else {
                                        Log::warn() << "loadSidecarMetadataWeb: element metadata"
                                                       " header read failed — no properties for "
                                                    << source_label;
                                    }

                                    const std::size_t n_meshes    = sc.meta.meshes.size();
                                    const std::size_t n_instances = sc.meta.instances.size();
                                    applyCachedModel(session_model_id, std::move(sc));
                                    // Mark web-streamed + set the source IMMEDIATELY — the
                                    // model now has non-resident chunks and the RAF loop's
                                    // driveStreamingLoads can run before we return here. If
                                    // streaming_from_web weren't set yet it would take the
                                    // sync fopen path and fail ("failed to read/decompress
                                    // chunk 0").
                                    if (auto m0 = models_gpu_.find(session_model_id); m0 != models_gpu_.end()) {
                                        m0->second.streaming_from_web = true;
                                        m0->second.web_source_id      = source_id;
                                    }
                                    // NOTE: no viewAll() here — applyCachedModel
                                    // already frames the FIRST model (gated by
                                    // initial_view_applied_), matching desktop.
                                    // Reframing per model would jump the camera
                                    // as each federated model streams in.
                                    host_->requestFrame();
                                    Log::info() << "ifcviewer-web: loaded sidecar (" << source_label
                                                << ", id " << session_model_id << ", " << n_meshes << " meshes, "
                                                << n_instances << " instances)";
                                    // Last: the model is fully in the scene, so a
                                    // handler is free to push federation matrices
                                    // or reframe without racing the setup above.
                                    if (on_loaded) on_loaded(session_model_id);
                                });
                        });
                });
        });
}

void ViewportCore::loadElementMetadataWeb(std::uint32_t session_model_id,
                                          std::function<void(bool)> done) {
    // On-demand fetch of the v15 element metadata block (elements + string table)
    // for a web-streamed model — the property data a UI needs (selected-
    // object name, search) but rendering doesn't. Fetches at most once. Reads
    // from the model's own registered byte-source, so it works per-model even
    // with several federated files loaded.
    auto it = models_gpu_.find(session_model_id);
    if (it == models_gpu_.end()) { if (done) done(false); return; }
    ModelGpuData& m = it->second;
    if (m.element_metadata_loaded || m.element_metadata_comp_size == 0) {
        m.element_metadata_loaded = true;
        if (done) done(true);
        return;
    }
    const std::uint64_t raw_size = m.element_metadata_raw_size;
    webReadRangesAsync(m.web_source_id, 0,
        {{m.element_metadata_comp_offset, m.element_metadata_comp_size}},
        [this, session_model_id, raw_size, done](bool ok, std::vector<std::uint8_t>&& cz) {
            auto mit = models_gpu_.find(session_model_id);
            if (mit == models_gpu_.end()) { if (done) done(false); return; }
            std::vector<std::uint8_t> buf(static_cast<std::size_t>(raw_size));
            SidecarData tmp;
            if (!ok ||
                !SidecarCompress::decompress(cz.data(), cz.size(), buf.data(), buf.size()) ||
                !parseSidecarElementMetadata(buf.data(), buf.size(), tmp)) {
                Log::warn() << "loadElementMetadataWeb: read/decompress/parse failed";
                if (done) done(false);
                return;
            }
            mit->second.elements             = std::move(tmp.elements);
            mit->second.string_table         = std::move(tmp.string_table);
            // Rebase element object_ids to the model's global id space so they
            // match the (already-rebased) instance ids used by pick/selection.
            const std::uint32_t base = mit->second.object_id_base;
            for (auto& e : mit->second.elements) e.object_id += base;
            mit->second.element_metadata_loaded = true;
            Log::info() << "ifcviewer-web: loaded element metadata ("
                        << mit->second.elements.size() << " elements)";
            if (done) done(true);
        });
}

void ViewportCore::loadAllElementMetadataWeb(std::function<void(bool)> done) {
    const std::vector<std::uint32_t> ids = modelIdsInLoadOrder();
    if (ids.empty()) { if (done) done(true); return; }
    // Fan out one lazy fetch per model and join on a shared counter. The
    // fetches complete through the JS event loop, so `pending` is only ever
    // touched from the main thread — no synchronisation needed.
    struct Join { std::size_t pending; bool ok; std::function<void(bool)> done; };
    auto join = std::make_shared<Join>(Join{ ids.size(), true, std::move(done) });
    for (std::uint32_t session_model_id : ids) {
        loadElementMetadataWeb(session_model_id, [join](bool ok) {
            join->ok = join->ok && ok;
            if (--join->pending == 0 && join->done) join->done(join->ok);
        });
    }
}

void ViewportCore::logSelectedObjectGuidWeb(std::uint32_t object_id) {
    InstanceCompose::InstanceLookup lk;
    if (!findInstance(object_id, lk)) return;  // empty pick / unknown id
    const std::uint32_t session_model_id = lk.session_model_id;
    loadElementMetadataWeb(session_model_id, [this, object_id](bool ok) {
        ElementRef e;
        if (!ok || !elementForObject(object_id, e)) {
            Log::warn() << "pick: no element metadata for object " << object_id;
            return;
        }
        Log::info() << "pick: object " << object_id << " GUID " << e.guid;
        // Surface the selection to JS so host pages can react (e.g. show the
        // GUID + model). Fires
        // Module.__ifcvOnSelect(object_id, guid, modelIndex, sourceId).
        // modelIndex is the load-order slot; sourceId is the byte-source the
        // host added the model from, which is the one that cannot shift.
        EM_ASM({
            if (Module.__ifcvOnSelect)
                Module.__ifcvOnSelect($0, UTF8ToString($1), $2, $3);
        }, object_id, e.guid.c_str(), e.model_index, e.source_id);
    });
}
#endif  // __EMSCRIPTEN__

void ViewportCore::streamingProgress(int& resident_chunks, int& total_chunks) const {
    resident_chunks = 0;
    total_chunks    = 0;
    for (const auto& [session_model_id, m] : models_gpu_) {
        for (const auto& c : m.chunks) {
            ++total_chunks;
            if (c.is_resident) ++resident_chunks;
        }
    }
}

int ViewportCore::streamingModelCount() const {
    return int(models_gpu_.size());
}

std::vector<std::uint32_t> ViewportCore::modelIdsInLoadOrder() const {
    std::vector<std::uint32_t> ids;
    ids.reserve(models_gpu_.size());
    for (const auto& [session_model_id, m] : models_gpu_) ids.push_back(session_model_id);
    std::sort(ids.begin(), ids.end());
    return ids;
}

int ViewportCore::modelLoadIndex(std::uint32_t session_model_id) const {
    const std::vector<std::uint32_t> ids = modelIdsInLoadOrder();
    const auto it = std::find(ids.begin(), ids.end(), session_model_id);
    return (it == ids.end()) ? -1 : int(it - ids.begin());
}

void ViewportCore::streamingModelProgress(int idx, int& resident_chunks,
                                          int& total_chunks) const {
    resident_chunks = 0;
    total_chunks    = 0;
    if (idx < 0 || idx >= int(models_gpu_.size())) return;
    auto it = models_gpu_.find(modelIdsInLoadOrder()[std::size_t(idx)]);
    if (it == models_gpu_.end()) return;
    for (const auto& c : it->second.chunks) {
        ++total_chunks;
        if (c.is_resident) ++resident_chunks;
    }
}

namespace {

// Resolve one element record against its model's string table. Offsets that run
// past the table (or carry zero length) yield an empty string rather than a
// fabricated one — the sidecar writes no string for an unnamed element.
ViewportCore::ElementRef makeElementRef(const ModelGpuData& m, int model_index,
                                        const ElementTableRecord& e) {
    auto str = [&m](std::uint32_t offset, std::uint32_t length) {
        return (length > 0 && std::size_t(offset) + length <= m.string_table.size())
                   ? m.string_table.substr(offset, length)
                   : std::string();
    };
    ViewportCore::ElementRef ref;
    ref.object_id   = e.object_id;
    ref.model_index = model_index;
    ref.source_id   = m.web_source_id;
    ref.guid        = str(e.guid_offset, e.guid_length);
    ref.name        = str(e.name_offset, e.name_length);
    ref.type        = str(e.type_offset, e.type_length);
    return ref;
}

}  // namespace

std::vector<ViewportCore::ElementRef> ViewportCore::elements() const {
    std::vector<ElementRef> out;
    const std::vector<std::uint32_t> ids = modelIdsInLoadOrder();
    for (std::size_t model_index = 0; model_index < ids.size(); ++model_index) {
        auto it = models_gpu_.find(ids[model_index]);
        if (it == models_gpu_.end()) continue;
        const ModelGpuData& m = it->second;
        out.reserve(out.size() + m.elements.size());
        for (const ElementTableRecord& e : m.elements)
            out.push_back(makeElementRef(m, int(model_index), e));
    }
    return out;
}

bool ViewportCore::elementForObject(std::uint32_t object_id, ElementRef& out) const {
    InstanceCompose::InstanceLookup lk;
    if (!findInstance(object_id, lk)) return false;
    auto it = models_gpu_.find(lk.session_model_id);
    if (it == models_gpu_.end()) return false;
    const ModelGpuData& m = it->second;
    for (const ElementTableRecord& e : m.elements) {
        if (e.object_id != object_id) continue;
        out = makeElementRef(m, modelLoadIndex(lk.session_model_id), e);
        return true;
    }
    return false;
}

void ViewportCore::streamingByteProgress(std::uint64_t& total_bytes,
                                         std::uint64_t& needed_bytes,
                                         std::uint64_t& loaded_bytes) const {
    // total  = all geometry across every model (the whole federation).
    // needed = chunks the CURRENT view wants (passed contribution culling).
    // loaded = the needed chunks that are resident.
    // So loaded/needed = how done this view is; needed/total = how much of the
    // whole model this view even requires.
    total_bytes = needed_bytes = loaded_bytes = 0;
    for (const auto& [session_model_id, m] : models_gpu_) {
        if (m.hidden) continue;
        for (const auto& c : m.chunks) {
            // Report COMPRESSED bytes — what actually crosses the network. Fall
            // back to raw for direct (in-memory) loads that have no blobs.
            const std::uint64_t bytes = (c.v_comp_size + c.i_comp_size > 0)
                ? c.v_comp_size + c.i_comp_size
                : c.vertex_byte_size + c.index_count * sizeof(std::uint32_t);
            total_bytes += bytes;
            if (c.contribution_visible_count > 0) {
                needed_bytes += bytes;
                if (c.is_resident) loaded_bytes += bytes;
            }
        }
    }
}

void ViewportCore::finalizeModel(std::uint32_t session_model_id) {
    auto it = pending_direct_loads_.find(session_model_id);
    if (it == pending_direct_loads_.end()) {
        Log::warn()
            << "[wgpu direct] finalizeModel(" << session_model_id
            << ") with no staged data; skipping";
        return;
    }
    std::unique_ptr<SidecarData> staging_ptr = std::move(it->second);
    pending_direct_loads_.erase(it);
    SidecarData& sidecar_data = *staging_ptr;

    if (!device_ || !queue_) {
        Log::warn() << "[wgpu direct] finalizeModel without an initialised device";
        return;
    }
    if (sidecar_data.meshes.empty() || sidecar_data.instances.empty()) {
        Log::info() << "[wgpu direct] finalizeModel(" << session_model_id
                    << "): empty staging (meshes=" << sidecar_data.meshes.size()
                    << " instances=" << sidecar_data.instances.size() << ")";
        return;
    }

    // Build a StreamingSidecar around the staging so applyCachedModel can
    // run its chunk planner over the same shape it expects from on-disk
    // metadata. file_path is left empty — the streaming worker keys off
    // that to skip these chunks (they're already resident after the
    // applyStreamedChunk loop below).
    StreamingSidecar metadata;
    metadata.meta = std::move(sidecar_data);
    // Direct load: geometry is already in memory (uploaded below), streamed
    // from nothing — leave file_path empty so the streaming worker skips it.
    metadata.geometry_section_offset = 0;
    metadata.file_path.clear();

    std::vector<std::uint8_t>  raw_vertices = std::move(metadata.meta.vertices);
    std::vector<std::uint32_t> raw_indices  = std::move(metadata.meta.indices);

    applyCachedModel(session_model_id, std::move(metadata));

    auto model_it = models_gpu_.find(session_model_id);
    if (model_it == models_gpu_.end()) {
        Log::warn()
            << "[wgpu direct] finalizeModel(" << session_model_id
            << "): applyCachedModel produced no model entry";
        return;
    }
    ModelGpuData& model_gpu_data = model_it->second;

    // Gather each chunk's vertex + index bytes from the staged buffers.
    std::size_t chunks_uploaded = 0;
    for (std::size_t chunk_index = 0; chunk_index < model_gpu_data.chunks.size(); ++chunk_index) {
        auto& chunk = model_gpu_data.chunks[chunk_index];
        if (chunk.mesh_ids.empty()) continue;

        std::vector<std::uint8_t>  vbytes(chunk.vertex_byte_size);
        std::vector<std::uint32_t> indices;
        indices.reserve(chunk.index_count);

        for (std::uint32_t mesh_index : chunk.mesh_ids) {
            const MeshInfo& mesh = model_gpu_data.meshes[mesh_index];
            const std::size_t vertex_byte_count =
                std::size_t(mesh.vertex_count) * INSTANCED_VERTEX_STRIDE_BYTES;
            if (vertex_byte_count > 0) {
                const std::size_t destination_vertex_offset =
                    std::size_t(model_gpu_data.mesh_chunk_local_base_vertex[mesh_index])
                                          * INSTANCED_VERTEX_STRIDE_BYTES;
                std::memcpy(vbytes.data() + destination_vertex_offset,
                            raw_vertices.data() + mesh.vbo_byte_offset, vertex_byte_count);
            }
            if (mesh.index_count > 0) {
                const std::uint32_t* src = raw_indices.data()
                                         + (mesh.ebo_byte_offset / sizeof(std::uint32_t));
                indices.insert(indices.end(), src, src + mesh.index_count);
            }
        }

        if (!applyStreamedChunk(model_gpu_data, chunk_index, vbytes, indices)) {
            Log::warn()
                << "[wgpu direct] finalizeModel(" << session_model_id
                << "): applyStreamedChunk failed on chunk " << chunk_index
                << " (pool OOM?)";
            continue;
        }
        ++chunks_uploaded;
    }

    Log::info()
        << "[wgpu direct] finalizeModel session_model_id=" << session_model_id
        << " meshes=" << model_gpu_data.meshes.size()
        << " instances=" << model_gpu_data.instances.size()
        << " chunks=" << chunks_uploaded << "/" << model_gpu_data.chunks.size()
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
    mcb.mode = kAsyncCbMode;
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
    desc.format        = surface_view_format_;  // matches the surface sRGB view + main pipeline target
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

// ===========================================================================
// Edge silhouette post-process (#84-s): buildEdgePipeline + encodeEdgePass +
// releaseEdgeResources
// ===========================================================================

namespace {

const char* EDGE_WGSL = R"(
@group(0) @binding(0) var src_depth: texture_depth_multisampled_2d;

const NEAR: f32 = 0.1;
const FAR:  f32 = 10000.0;
const EDGE_SCALE:     f32 = 6.0;
const EDGE_THRESHOLD: f32 = 0.004;

// Depth texture stores [0,1] z (we pre-multiply a z-remap onto Qt's GL-style
// projection in the main pipeline). Convert back to GL-NDC then reverse-
// project to view-space distance.
fn linearise(z: f32) -> f32 {
    let ndc = z * 2.0 - 1.0;
    return (2.0 * NEAR * FAR) / (FAR + NEAR - ndc * (FAR - NEAR));
}

@vertex
fn vs_main(@builtin(vertex_index) vid: u32) -> @builtin(position) vec4<f32> {
    let x = f32((vid << 1u) & 2u) * 2.0 - 1.0;
    let y = f32(vid & 2u) * 2.0 - 1.0;
    return vec4<f32>(x, y, 0.0, 1.0);
}

@fragment
fn fs_main(@builtin(position) frag: vec4<f32>) -> @location(0) vec4<f32> {
    let p   = vec2<i32>(i32(frag.x), i32(frag.y));
    let dim = vec2<i32>(textureDimensions(src_depth));

    let dc_raw = textureLoad(src_depth, p, 0);
    // Background pixels: nothing was drawn here. Skip so we don't draw
    // edges on the void / sky.
    if (dc_raw >= 0.99999) { discard; }

    let c = linearise(dc_raw);
    let n = linearise(textureLoad(src_depth, vec2<i32>(p.x,                     max(p.y - 1, 0)),     0));
    let s = linearise(textureLoad(src_depth, vec2<i32>(p.x,                     min(p.y + 1, dim.y - 1)), 0));
    let e = linearise(textureLoad(src_depth, vec2<i32>(min(p.x + 1, dim.x - 1), p.y),                 0));
    let w = linearise(textureLoad(src_depth, vec2<i32>(max(p.x - 1, 0),         p.y),                 0));

    let lap   = abs(4.0 * c - n - s - e - w);
    let t     = EDGE_THRESHOLD * c;
    let edge  = clamp((lap - t) * EDGE_SCALE, 0.0, 0.6);

    // Multiplicative blend (Dst, Zero): output rgb = (1 - edge), so the
    // existing surface colour is multiplied by (1 - edge) per channel.
    return vec4<f32>(vec3<f32>(1.0 - edge), 1.0);
}
)";

} // namespace

bool ViewportCore::buildEdgePipeline() {
    WGPUBindGroupLayoutEntry entries[1] = {};
    entries[0].binding = 0;
    entries[0].visibility = WGPUShaderStage_Fragment;
    entries[0].texture.sampleType    = WGPUTextureSampleType_Depth;
    entries[0].texture.viewDimension = WGPUTextureViewDimension_2D;
    entries[0].texture.multisampled  = 1;

    WGPUBindGroupLayoutDescriptor bgl_desc = {};
    bgl_desc.entryCount = 1;
    bgl_desc.entries    = entries;
    bgl_desc.label      = svFromCStr("ifcviewer-wgpu.edge_bgl");
    edge_bgl_ = wgpuDeviceCreateBindGroupLayout(device_, &bgl_desc);

    WGPUPipelineLayoutDescriptor pl_desc = {};
    pl_desc.bindGroupLayoutCount = 1;
    pl_desc.bindGroupLayouts     = &edge_bgl_;
    pl_desc.label                = svFromCStr("ifcviewer-wgpu.edge_pipeline_layout");
    edge_pipeline_layout_ = wgpuDeviceCreatePipelineLayout(device_, &pl_desc);

    WGPUShaderSourceWGSL wgsl_src = {};
    wgsl_src.chain.sType = WGPUSType_ShaderSourceWGSL;
    wgsl_src.code        = svFromCStr(EDGE_WGSL);
    WGPUShaderModuleDescriptor sm_desc = {};
    sm_desc.nextInChain = &wgsl_src.chain;
    sm_desc.label       = svFromCStr("ifcviewer-wgpu.edge_wgsl");
    edge_shader_module_ = wgpuDeviceCreateShaderModule(device_, &sm_desc);

    // Multiplicative blend (Dst, Zero): out.rgb = src.rgb * dst.rgb.
    // Fragment outputs (1 - edge, 1 - edge, 1 - edge) so the existing
    // surface colour is scaled per-channel — strictly darkens, never
    // brightens. Matches GL's renderEdgePass (GL_DST_COLOR, GL_ZERO).
    WGPUBlendState blend = {};
    blend.color.srcFactor = WGPUBlendFactor_Dst;
    blend.color.dstFactor = WGPUBlendFactor_Zero;
    blend.color.operation = WGPUBlendOperation_Add;
    blend.alpha.srcFactor = WGPUBlendFactor_Zero;
    blend.alpha.dstFactor = WGPUBlendFactor_One;
    blend.alpha.operation = WGPUBlendOperation_Add;

    WGPUColorTargetState target = {};
    target.format    = surface_view_format_;  // sRGB view, matches the main pass target
    target.blend     = &blend;
    target.writeMask = WGPUColorWriteMask_All;

    WGPUFragmentState frag = {};
    frag.module      = edge_shader_module_;
    frag.entryPoint  = svFromCStr("fs_main");
    frag.targetCount = 1;
    frag.targets     = &target;

    WGPURenderPipelineDescriptor rp_desc = {};
    rp_desc.layout              = edge_pipeline_layout_;
    rp_desc.label               = svFromCStr("ifcviewer-wgpu.edge_pipeline");
    rp_desc.vertex.module       = edge_shader_module_;
    rp_desc.vertex.entryPoint   = svFromCStr("vs_main");
    rp_desc.vertex.bufferCount  = 0;
    rp_desc.fragment            = &frag;
    rp_desc.depthStencil        = nullptr;            // no depth attachment
    rp_desc.primitive.topology  = WGPUPrimitiveTopology_TriangleList;
    rp_desc.primitive.cullMode  = WGPUCullMode_None;
    rp_desc.multisample.count   = 1;
    rp_desc.multisample.mask    = 0xFFFFFFFFu;

    edge_pipeline_ = wgpuDeviceCreateRenderPipeline(device_, &rp_desc);
    if (!edge_pipeline_) {
        Log::warn() << "wgpu edge pipeline creation failed";
        return false;
    }
    return true;
}

void ViewportCore::encodeEdgePass(WGPUCommandEncoder enc,
                                  WGPUTextureView surface_view) {
    if (!edges_enabled_ || !edge_pipeline_ || !depth_view_ || !surface_view) return;

    // Rebuild lazily when the underlying depth view was replaced (on
    // resize we proactively null this alongside the HiZ bind group).
    if (!edge_bind_group_) {
        WGPUBindGroupEntry entry = {};
        entry.binding     = 0;
        entry.textureView = depth_view_;
        WGPUBindGroupDescriptor bg = {};
        bg.layout     = edge_bgl_;
        bg.entryCount = 1;
        bg.entries    = &entry;
        bg.label      = svFromCStr("ifcviewer-wgpu.edge_bind_group");
        edge_bind_group_ = wgpuDeviceCreateBindGroup(device_, &bg);
    }

    WGPURenderPassColorAttachment color = {};
    color.view       = surface_view;
    color.loadOp     = WGPULoadOp_Load;
    color.storeOp    = WGPUStoreOp_Store;
    color.depthSlice = WGPU_DEPTH_SLICE_UNDEFINED;

    WGPURenderPassDescriptor pass_desc = {};
    pass_desc.colorAttachmentCount   = 1;
    pass_desc.colorAttachments       = &color;
    pass_desc.depthStencilAttachment = nullptr;
    pass_desc.label                  = svFromCStr("ifcviewer-wgpu.edge_pass");

    WGPURenderPassEncoder pass = wgpuCommandEncoderBeginRenderPass(enc, &pass_desc);
    wgpuRenderPassEncoderSetPipeline(pass, edge_pipeline_);
    wgpuRenderPassEncoderSetBindGroup(pass, 0, edge_bind_group_, 0, nullptr);
    wgpuRenderPassEncoderDraw(pass, 3, 1, 0, 0);
    wgpuRenderPassEncoderEnd(pass);
    wgpuRenderPassEncoderRelease(pass);
}

void ViewportCore::releaseEdgeResources() {
    if (edge_bind_group_)      { wgpuBindGroupRelease(edge_bind_group_);      edge_bind_group_ = nullptr; }
    if (edge_pipeline_)        { wgpuRenderPipelineRelease(edge_pipeline_);   edge_pipeline_ = nullptr; }
    if (edge_shader_module_)   { wgpuShaderModuleRelease(edge_shader_module_);edge_shader_module_ = nullptr; }
    if (edge_pipeline_layout_) { wgpuPipelineLayoutRelease(edge_pipeline_layout_); edge_pipeline_layout_ = nullptr; }
    if (edge_bgl_)             { wgpuBindGroupLayoutRelease(edge_bgl_);       edge_bgl_ = nullptr; }
}

// ===========================================================================
// Selection silhouette outline: buildSelectionOutlinePipelines +
// ensureSelectionOutlineTextures + encodeSelectionMaskPass +
// encodeSelectionOutlinePass
//
// A halo drawn just OUTSIDE the selected objects, so the cue does not depend
// on the object's own colour the way the fs_main selection tint does — a blue
// element in a blue-tinted selection is otherwise indistinguishable.
//
// Three steps: a geometry pass writes a coverage mask (fs_mask), then two
// fullscreen passes dilate it. The dilation is separable — a horizontal max
// into an RGBA8 scratch, then a vertical max composited onto the surface —
// because the naive 2D disc is O(r^2) taps per pixel and a 3-physical-pixel
// radius on a HiDPI canvas is already 100+ loads over the whole screen.
// Separable makes it O(r), and the square structuring element it implies is
// invisible at this radius.
// ===========================================================================

namespace {

// Scratch format for the horizontal pass. r = max over the inner radius,
// g = max over the outer radius, b = this pixel's own coverage passed
// through so the vertical pass needs only this one texture bound.
constexpr WGPUTextureFormat kSelScratchFormat = WGPUTextureFormat_RGBA8Unorm;

const char* SEL_OUTLINE_WGSL = R"(
struct OutlineUniforms {
    inner_color:  vec4<f32>,   // rgb + alpha of the ring hugging the silhouette
    outer_color:  vec4<f32>,   // rgb + alpha of the band beyond it
    inner_radius: f32,         // physical pixels
    outer_radius: f32,         // physical pixels, >= inner_radius
    _pad0:        f32,
    _pad1:        f32,
};

@group(0) @binding(0) var src: texture_2d<f32>;
@group(0) @binding(1) var<uniform> u: OutlineUniforms;

// Undo the swap chain's implicit linear->sRGB write encoding, exactly as
// the main shader does, so the halo's bytes are the colour we asked for.
fn srgbToLinear(s: vec3<f32>) -> vec3<f32> {
    let lo = s / 12.92;
    let hi = pow((s + 0.055) / 1.055, vec3<f32>(2.4));
    return select(hi, lo, s <= vec3<f32>(0.04045));
}

@vertex
fn vs_main(@builtin(vertex_index) vid: u32) -> @builtin(position) vec4<f32> {
    let x = f32((vid << 1u) & 2u) * 2.0 - 1.0;
    let y = f32(vid & 2u) * 2.0 - 1.0;
    return vec4<f32>(x, y, 0.0, 1.0);
}

// Horizontal half of the dilation. Reads the resolved coverage mask.
@fragment
fn fs_dilate_h(@builtin(position) frag: vec4<f32>) -> @location(0) vec4<f32> {
    let p     = vec2<i32>(i32(frag.x), i32(frag.y));
    let max_x = i32(textureDimensions(src).x) - 1;
    let ri    = i32(u.inner_radius);
    let ro    = i32(u.outer_radius);

    let here = textureLoad(src, p, 0).r;
    var inner = 0.0;
    var outer = 0.0;
    for (var dx = -ro; dx <= ro; dx = dx + 1) {
        let m = textureLoad(src, vec2<i32>(clamp(p.x + dx, 0, max_x), p.y), 0).r;
        outer = max(outer, m);
        if (dx >= -ri && dx <= ri) { inner = max(inner, m); }
    }
    return vec4<f32>(inner, outer, here, 1.0);
}

// Vertical half, plus the composite. Reads the scratch written above.
@fragment
fn fs_outline(@builtin(position) frag: vec4<f32>) -> @location(0) vec4<f32> {
    let p     = vec2<i32>(i32(frag.x), i32(frag.y));
    let max_y = i32(textureDimensions(src).y) - 1;
    let ri    = i32(u.inner_radius);
    let ro    = i32(u.outer_radius);

    // Coverage at this pixel. Inside the silhouette there is nothing to
    // draw: the halo sits strictly outside, so a selected element's own
    // colour is never painted over.
    let here = textureLoad(src, p, 0).b;
    if (here >= 0.999) { discard; }

    var inner = 0.0;
    var outer = 0.0;
    for (var dy = -ro; dy <= ro; dy = dy + 1) {
        let s = textureLoad(src, vec2<i32>(p.x, clamp(p.y + dy, 0, max_y)), 0);
        outer = max(outer, s.g);
        if (dy >= -ri && dy <= ri) { inner = max(inner, s.r); }
    }

    // Two concentric rings, written as differences so they never overlap:
    // `in_ring` is the dilation minus the shape, `out_ring` is the wider
    // dilation minus the narrower one.
    let in_ring  = clamp(inner - here,  0.0, 1.0);
    let out_ring = clamp(outer - inner, 0.0, 1.0);

    let a_in  = in_ring  * u.inner_color.a;
    let a_out = out_ring * u.outer_color.a * (1.0 - in_ring);
    let a     = a_in + a_out;
    if (a <= 0.004) { discard; }

    // Straight (unpremultiplied) alpha out — the SrcAlpha blend factor
    // does the premultiply, which is what the surface's premultiplied
    // alpha mode expects to find in the buffer.
    let rgb = (srgbToLinear(u.inner_color.rgb) * a_in
             + srgbToLinear(u.outer_color.rgb) * a_out) / a;
    return vec4<f32>(rgb, a);
}
)";

} // namespace

bool ViewportCore::buildSelectionOutlinePipelines() {
    // ---- Mask pass. Reuses the main shader module + pipeline layout, so it
    // vertex-pulls identically and sees the same sel_flags binding. Depth is
    // the main pass's, bound read-only: LessEqual against already-written
    // scene depth keeps only the fragments that actually survived.
    {
        WGPUColorTargetState target = {};
        target.format    = WGPUTextureFormat_R8Unorm;
        target.writeMask = WGPUColorWriteMask_All;

        WGPUFragmentState frag = {};
        frag.module      = main_shader_module_;
        frag.entryPoint  = svFromCStr("fs_mask");
        frag.targetCount = 1;
        frag.targets     = &target;

        WGPUDepthStencilState depth = {};
        depth.format               = WGPUTextureFormat_Depth32Float;
        depth.depthWriteEnabled    = WGPUOptionalBool_False;
        depth.depthCompare         = WGPUCompareFunction_LessEqual;
        depth.stencilFront.compare = WGPUCompareFunction_Always;
        depth.stencilBack.compare  = WGPUCompareFunction_Always;

        WGPURenderPipelineDescriptor rp_desc = {};
        rp_desc.layout             = pipeline_layout_;
        rp_desc.label              = svFromCStr("ifcviewer-wgpu.sel_mask_pipeline");
        rp_desc.vertex.module      = main_shader_module_;
        rp_desc.vertex.entryPoint  = svFromCStr("vs_main");
        rp_desc.vertex.bufferCount = 0;
        rp_desc.fragment           = &frag;
        rp_desc.depthStencil       = &depth;
        rp_desc.primitive.topology = WGPUPrimitiveTopology_TriangleList;
        // No cull: an open shell (a wall face, a plate) would otherwise
        // punch holes in its own silhouette when seen from behind.
        rp_desc.primitive.cullMode = WGPUCullMode_None;
        rp_desc.multisample.count  = kViewportSampleCount;
        rp_desc.multisample.mask   = 0xFFFFFFFFu;

        sel_mask_pipeline_ = wgpuDeviceCreateRenderPipeline(device_, &rp_desc);
        if (!sel_mask_pipeline_) {
            Log::warn() << "wgpu selection mask pipeline creation failed";
            return false;
        }
    }

    // ---- Shared fullscreen resources. One BGL for both dilation passes:
    // each binds a different source texture through the same shape.
    WGPUBindGroupLayoutEntry entries[2] = {};
    entries[0].binding = 0;
    entries[0].visibility = WGPUShaderStage_Fragment;
    entries[0].texture.sampleType    = WGPUTextureSampleType_Float;
    entries[0].texture.viewDimension = WGPUTextureViewDimension_2D;
    entries[1].binding = 1;
    entries[1].visibility = WGPUShaderStage_Fragment;
    entries[1].buffer.type           = WGPUBufferBindingType_Uniform;
    entries[1].buffer.minBindingSize = sizeof(SelOutlineUniforms);

    WGPUBindGroupLayoutDescriptor bgl_desc = {};
    bgl_desc.entryCount = 2;
    bgl_desc.entries    = entries;
    bgl_desc.label      = svFromCStr("ifcviewer-wgpu.sel_outline_bgl");
    sel_outline_bgl_ = wgpuDeviceCreateBindGroupLayout(device_, &bgl_desc);

    WGPUPipelineLayoutDescriptor pl_desc = {};
    pl_desc.bindGroupLayoutCount = 1;
    pl_desc.bindGroupLayouts     = &sel_outline_bgl_;
    pl_desc.label                = svFromCStr("ifcviewer-wgpu.sel_outline_pipeline_layout");
    sel_outline_pipeline_layout_ = wgpuDeviceCreatePipelineLayout(device_, &pl_desc);

    WGPUShaderSourceWGSL wgsl_src = {};
    wgsl_src.chain.sType = WGPUSType_ShaderSourceWGSL;
    wgsl_src.code        = svFromCStr(SEL_OUTLINE_WGSL);
    WGPUShaderModuleDescriptor sm_desc = {};
    sm_desc.nextInChain = &wgsl_src.chain;
    sm_desc.label       = svFromCStr("ifcviewer-wgpu.sel_outline_wgsl");
    sel_outline_shader_module_ = wgpuDeviceCreateShaderModule(device_, &sm_desc);

    WGPUBufferDescriptor ub = {};
    ub.usage = WGPUBufferUsage_Uniform | WGPUBufferUsage_CopyDst;
    ub.size  = sizeof(SelOutlineUniforms);
    ub.label = svFromCStr("ifcviewer-wgpu.sel_outline_uniforms");
    sel_outline_uniform_buffer_ = wgpuDeviceCreateBuffer(device_, &ub);

    // ---- Horizontal dilation into the scratch target. Opaque write.
    {
        WGPUColorTargetState target = {};
        target.format    = kSelScratchFormat;
        target.writeMask = WGPUColorWriteMask_All;

        WGPUFragmentState frag = {};
        frag.module      = sel_outline_shader_module_;
        frag.entryPoint  = svFromCStr("fs_dilate_h");
        frag.targetCount = 1;
        frag.targets     = &target;

        WGPURenderPipelineDescriptor rp_desc = {};
        rp_desc.layout             = sel_outline_pipeline_layout_;
        rp_desc.label              = svFromCStr("ifcviewer-wgpu.sel_dilate_h_pipeline");
        rp_desc.vertex.module      = sel_outline_shader_module_;
        rp_desc.vertex.entryPoint  = svFromCStr("vs_main");
        rp_desc.vertex.bufferCount = 0;
        rp_desc.fragment           = &frag;
        rp_desc.depthStencil       = nullptr;
        rp_desc.primitive.topology = WGPUPrimitiveTopology_TriangleList;
        rp_desc.primitive.cullMode = WGPUCullMode_None;
        rp_desc.multisample.count  = 1;
        rp_desc.multisample.mask   = 0xFFFFFFFFu;

        sel_dilate_h_pipeline_ = wgpuDeviceCreateRenderPipeline(device_, &rp_desc);
        if (!sel_dilate_h_pipeline_) {
            Log::warn() << "wgpu selection dilate pipeline creation failed";
            return false;
        }
    }

    // ---- Vertical dilation + composite onto the resolved surface.
    {
        WGPUBlendState blend = {};
        blend.color.srcFactor = WGPUBlendFactor_SrcAlpha;
        blend.color.dstFactor = WGPUBlendFactor_OneMinusSrcAlpha;
        blend.color.operation = WGPUBlendOperation_Add;
        blend.alpha.srcFactor = WGPUBlendFactor_One;
        blend.alpha.dstFactor = WGPUBlendFactor_OneMinusSrcAlpha;
        blend.alpha.operation = WGPUBlendOperation_Add;

        WGPUColorTargetState target = {};
        target.format    = surface_view_format_;
        target.blend     = &blend;
        target.writeMask = WGPUColorWriteMask_All;

        WGPUFragmentState frag = {};
        frag.module      = sel_outline_shader_module_;
        frag.entryPoint  = svFromCStr("fs_outline");
        frag.targetCount = 1;
        frag.targets     = &target;

        WGPURenderPipelineDescriptor rp_desc = {};
        rp_desc.layout             = sel_outline_pipeline_layout_;
        rp_desc.label              = svFromCStr("ifcviewer-wgpu.sel_outline_pipeline");
        rp_desc.vertex.module      = sel_outline_shader_module_;
        rp_desc.vertex.entryPoint  = svFromCStr("vs_main");
        rp_desc.vertex.bufferCount = 0;
        rp_desc.fragment           = &frag;
        rp_desc.depthStencil       = nullptr;
        rp_desc.primitive.topology = WGPUPrimitiveTopology_TriangleList;
        rp_desc.primitive.cullMode = WGPUCullMode_None;
        rp_desc.multisample.count  = 1;
        rp_desc.multisample.mask   = 0xFFFFFFFFu;

        sel_outline_pipeline_ = wgpuDeviceCreateRenderPipeline(device_, &rp_desc);
        if (!sel_outline_pipeline_) {
            Log::warn() << "wgpu selection outline pipeline creation failed";
            return false;
        }
    }
    return true;
}

void ViewportCore::ensureSelectionOutlineTextures(int w, int h) {
    if (w == sel_mask_w_ && h == sel_mask_h_ && sel_mask_view_) return;
    releaseSelectionOutlineTextures();

    WGPUTextureDescriptor desc = {};
    desc.dimension     = WGPUTextureDimension_2D;
    desc.size.width    = std::uint32_t(w);
    desc.size.height   = std::uint32_t(h);
    desc.size.depthOrArrayLayers = 1;
    desc.mipLevelCount = 1;

    // Multisampled coverage target, matching the main pass so it can share
    // the depth attachment; resolved down to the single-sample mask the
    // dilation reads. The resolve is what gives the halo the same edge
    // antialiasing as the geometry it traces.
    desc.usage       = WGPUTextureUsage_RenderAttachment;
    desc.format      = WGPUTextureFormat_R8Unorm;
    desc.sampleCount = kViewportSampleCount;
    desc.label       = svFromCStr("ifcviewer-wgpu.sel_mask_msaa");
    sel_mask_msaa_texture_ = wgpuDeviceCreateTexture(device_, &desc);
    sel_mask_msaa_view_    = wgpuTextureCreateView(sel_mask_msaa_texture_, nullptr);

    desc.usage       = WGPUTextureUsage_RenderAttachment | WGPUTextureUsage_TextureBinding;
    desc.sampleCount = 1;
    desc.label       = svFromCStr("ifcviewer-wgpu.sel_mask");
    sel_mask_texture_ = wgpuDeviceCreateTexture(device_, &desc);
    sel_mask_view_    = wgpuTextureCreateView(sel_mask_texture_, nullptr);

    desc.format = kSelScratchFormat;
    desc.label  = svFromCStr("ifcviewer-wgpu.sel_scratch");
    sel_scratch_texture_ = wgpuDeviceCreateTexture(device_, &desc);
    sel_scratch_view_    = wgpuTextureCreateView(sel_scratch_texture_, nullptr);

    sel_mask_w_ = w;
    sel_mask_h_ = h;

    // The bind groups name the views we just replaced.
    if (sel_dilate_bind_group_) {
        wgpuBindGroupRelease(sel_dilate_bind_group_);
        sel_dilate_bind_group_ = nullptr;
    }
    if (sel_outline_bind_group_) {
        wgpuBindGroupRelease(sel_outline_bind_group_);
        sel_outline_bind_group_ = nullptr;
    }
}

void ViewportCore::releaseSelectionOutlineTextures() {
    if (sel_scratch_view_)       { wgpuTextureViewRelease(sel_scratch_view_);   sel_scratch_view_ = nullptr; }
    if (sel_scratch_texture_)    { wgpuTextureRelease(sel_scratch_texture_);    sel_scratch_texture_ = nullptr; }
    if (sel_mask_view_)          { wgpuTextureViewRelease(sel_mask_view_);      sel_mask_view_ = nullptr; }
    if (sel_mask_texture_)       { wgpuTextureRelease(sel_mask_texture_);       sel_mask_texture_ = nullptr; }
    if (sel_mask_msaa_view_)     { wgpuTextureViewRelease(sel_mask_msaa_view_); sel_mask_msaa_view_ = nullptr; }
    if (sel_mask_msaa_texture_)  { wgpuTextureRelease(sel_mask_msaa_texture_);  sel_mask_msaa_texture_ = nullptr; }
    sel_mask_w_ = sel_mask_h_ = 0;
}

bool ViewportCore::selectionOutlineActive() const {
    return selection_outline_enabled_ && selection_.count() > 0
        && sel_mask_pipeline_ && sel_outline_pipeline_ && sel_mask_view_;
}

void ViewportCore::encodeSelectionMaskPass(WGPUCommandEncoder enc) {
    if (!selectionOutlineActive() || !depth_view_ || !frame_bind_group_) return;

    WGPURenderPassColorAttachment color = {};
    color.view          = sel_mask_msaa_view_;
    color.resolveTarget = sel_mask_view_;
    color.loadOp        = WGPULoadOp_Clear;
    // Only the resolve is ever read, so the multisampled samples can go.
    color.storeOp       = WGPUStoreOp_Discard;
    color.clearValue    = {0.0, 0.0, 0.0, 0.0};
    color.depthSlice    = WGPU_DEPTH_SLICE_UNDEFINED;

    // Read-only depth: the scene's own z, already written by the main pass.
    // WebGPU requires the load/store ops be left undefined when a depth
    // attachment is read-only, which the zero-init here does.
    WGPURenderPassDepthStencilAttachment depth = {};
    depth.view            = depth_view_;
    depth.depthReadOnly   = true;
    depth.stencilReadOnly = true;

    WGPURenderPassDescriptor pass_desc = {};
    pass_desc.colorAttachmentCount   = 1;
    pass_desc.colorAttachments       = &color;
    pass_desc.depthStencilAttachment = &depth;
    pass_desc.label                  = svFromCStr("ifcviewer-wgpu.sel_mask_pass");

    WGPURenderPassEncoder pass = wgpuCommandEncoderBeginRenderPass(enc, &pass_desc);
    wgpuRenderPassEncoderSetPipeline(pass, sel_mask_pipeline_);
    wgpuRenderPassEncoderSetBindGroup(pass, 0, frame_bind_group_, 0, nullptr);

    // Same draw stream as the main pass, opaque and transparent together —
    // a selected element that happens to be translucent still gets a halo.
    for (const auto& [session_model_id, m] : models_gpu_) {
        if (m.hidden) continue;
        for (const auto& c : m.chunks) {
            if (!c.bind_group || c.total_visible_vertices == 0) continue;
            wgpuRenderPassEncoderSetBindGroup(pass, 1, c.bind_group, 0, nullptr);
            wgpuRenderPassEncoderDraw(pass, c.total_visible_vertices, 1, 0, 0);
        }
    }

    wgpuRenderPassEncoderEnd(pass);
    wgpuRenderPassEncoderRelease(pass);
}

void ViewportCore::encodeSelectionOutlinePass(WGPUCommandEncoder enc,
                                              WGPUTextureView surface_view,
                                              int dpr) {
    if (!selectionOutlineActive() || !surface_view || !sel_dilate_h_pipeline_) return;

    // Ring widths in LOGICAL pixels, scaled here so the halo looks the same
    // on a HiDPI canvas as it does on a 1x one.
    const float scale = float(std::max(1, dpr));
    SelOutlineUniforms u = {};
    u.inner_color[0] = 1.0f; u.inner_color[1] = 1.0f;
    u.inner_color[2] = 1.0f; u.inner_color[3] = 1.0f;
    u.outer_color[0] = 0.04f; u.outer_color[1] = 0.04f;
    u.outer_color[2] = 0.04f; u.outer_color[3] = 0.85f;
    u.inner_radius   = 2.0f * scale;
    u.outer_radius   = 3.0f * scale;
    wgpuQueueWriteBuffer(queue_, sel_outline_uniform_buffer_, 0, &u, sizeof(u));

    if (!sel_dilate_bind_group_) {
        WGPUBindGroupEntry e[2] = {};
        e[0].binding     = 0;
        e[0].textureView = sel_mask_view_;
        e[1].binding = 1;
        e[1].buffer  = sel_outline_uniform_buffer_;
        e[1].size    = sizeof(SelOutlineUniforms);
        WGPUBindGroupDescriptor bg = {};
        bg.layout     = sel_outline_bgl_;
        bg.entryCount = 2;
        bg.entries    = e;
        bg.label      = svFromCStr("ifcviewer-wgpu.sel_dilate_bind_group");
        sel_dilate_bind_group_ = wgpuDeviceCreateBindGroup(device_, &bg);
    }
    if (!sel_outline_bind_group_) {
        WGPUBindGroupEntry e[2] = {};
        e[0].binding     = 0;
        e[0].textureView = sel_scratch_view_;
        e[1].binding = 1;
        e[1].buffer  = sel_outline_uniform_buffer_;
        e[1].size    = sizeof(SelOutlineUniforms);
        WGPUBindGroupDescriptor bg = {};
        bg.layout     = sel_outline_bgl_;
        bg.entryCount = 2;
        bg.entries    = e;
        bg.label      = svFromCStr("ifcviewer-wgpu.sel_outline_bind_group");
        sel_outline_bind_group_ = wgpuDeviceCreateBindGroup(device_, &bg);
    }

    {
        WGPURenderPassColorAttachment color = {};
        color.view       = sel_scratch_view_;
        color.loadOp     = WGPULoadOp_Clear;
        color.storeOp    = WGPUStoreOp_Store;
        color.clearValue = {0.0, 0.0, 0.0, 1.0};
        color.depthSlice = WGPU_DEPTH_SLICE_UNDEFINED;

        WGPURenderPassDescriptor pass_desc = {};
        pass_desc.colorAttachmentCount = 1;
        pass_desc.colorAttachments     = &color;
        pass_desc.label                = svFromCStr("ifcviewer-wgpu.sel_dilate_h_pass");

        WGPURenderPassEncoder pass = wgpuCommandEncoderBeginRenderPass(enc, &pass_desc);
        wgpuRenderPassEncoderSetPipeline(pass, sel_dilate_h_pipeline_);
        wgpuRenderPassEncoderSetBindGroup(pass, 0, sel_dilate_bind_group_, 0, nullptr);
        wgpuRenderPassEncoderDraw(pass, 3, 1, 0, 0);
        wgpuRenderPassEncoderEnd(pass);
        wgpuRenderPassEncoderRelease(pass);
    }

    {
        WGPURenderPassColorAttachment color = {};
        color.view       = surface_view;
        color.loadOp     = WGPULoadOp_Load;
        color.storeOp    = WGPUStoreOp_Store;
        color.depthSlice = WGPU_DEPTH_SLICE_UNDEFINED;

        WGPURenderPassDescriptor pass_desc = {};
        pass_desc.colorAttachmentCount = 1;
        pass_desc.colorAttachments     = &color;
        pass_desc.label                = svFromCStr("ifcviewer-wgpu.sel_outline_pass");

        WGPURenderPassEncoder pass = wgpuCommandEncoderBeginRenderPass(enc, &pass_desc);
        wgpuRenderPassEncoderSetPipeline(pass, sel_outline_pipeline_);
        wgpuRenderPassEncoderSetBindGroup(pass, 0, sel_outline_bind_group_, 0, nullptr);
        wgpuRenderPassEncoderDraw(pass, 3, 1, 0, 0);
        wgpuRenderPassEncoderEnd(pass);
        wgpuRenderPassEncoderRelease(pass);
    }
}

// ===========================================================================
// Pick + raycast (#84-t)
// ===========================================================================

#include <unordered_set>

namespace {

// Slab method ray-AABB. inv_d is precomputed 1/dir per axis.
bool rayAabbSlab(const float ro[3], const float inv_d[3],
                 const float bmin[3], const float bmax[3]) {
    float tmin = 0.0f, tmax = std::numeric_limits<float>::infinity();
    for (int i = 0; i < 3; ++i) {
        const float t1 = (bmin[i] - ro[i]) * inv_d[i];
        const float t2 = (bmax[i] - ro[i]) * inv_d[i];
        tmin = std::max(tmin, std::min(t1, t2));
        tmax = std::min(tmax, std::max(t1, t2));
    }
    return tmax >= tmin && tmax >= 0.0f;
}

// Möller-Trumbore ray-triangle. Returns true on hit; t is in dir-units.
bool rayTriMT(const float ro[3], const float rd[3],
              const float v0[3], const float v1[3], const float v2[3],
              float& t_out) {
    constexpr float EPS = 1e-7f;
    const float e1[3] = {v1[0]-v0[0], v1[1]-v0[1], v1[2]-v0[2]};
    const float e2[3] = {v2[0]-v0[0], v2[1]-v0[1], v2[2]-v0[2]};
    const float h[3]  = {
        rd[1]*e2[2] - rd[2]*e2[1],
        rd[2]*e2[0] - rd[0]*e2[2],
        rd[0]*e2[1] - rd[1]*e2[0]
    };
    const float a = e1[0]*h[0] + e1[1]*h[1] + e1[2]*h[2];
    if (a > -EPS && a < EPS) return false;
    const float f = 1.0f / a;
    const float s[3] = {ro[0]-v0[0], ro[1]-v0[1], ro[2]-v0[2]};
    const float u = f * (s[0]*h[0] + s[1]*h[1] + s[2]*h[2]);
    if (u < 0.0f || u > 1.0f) return false;
    const float q[3] = {
        s[1]*e1[2] - s[2]*e1[1],
        s[2]*e1[0] - s[0]*e1[2],
        s[0]*e1[1] - s[1]*e1[0]
    };
    const float v = f * (rd[0]*q[0] + rd[1]*q[1] + rd[2]*q[2]);
    if (v < 0.0f || u + v > 1.0f) return false;
    const float t = f * (e2[0]*q[0] + e2[1]*q[1] + e2[2]*q[2]);
    if (t <= EPS) return false;
    t_out = t;
    return true;
}

// Slab-method ray-AABB intersection. Returns t_enter (clamped to >= 0)
// and the axis-aligned face normal at the entry.
bool rayAABBHit(const Eigen::Vector3f& origin, const Eigen::Vector3f& dir,
                const float mn[3], const float mx[3],
                float& t_enter, Eigen::Vector3f& face_normal) {
    float t_min = -std::numeric_limits<float>::infinity();
    float t_max =  std::numeric_limits<float>::infinity();
    const float o[3] = { origin.x(), origin.y(), origin.z() };
    const float d[3] = { dir.x(),    dir.y(),    dir.z()    };
    int   hit_axis = -1;
    float hit_sign = 0.0f;
    for (int i = 0; i < 3; ++i) {
        if (std::abs(d[i]) < 1e-8f) {
            if (o[i] < mn[i] || o[i] > mx[i]) return false;
            continue;
        }
        float t1 = (mn[i] - o[i]) / d[i];
        float t2 = (mx[i] - o[i]) / d[i];
        float sign_for_t1 = -1.0f;
        if (t1 > t2) { std::swap(t1, t2); sign_for_t1 = +1.0f; }
        if (t1 > t_min) {
            t_min    = t1;
            hit_axis = i;
            hit_sign = sign_for_t1;
        }
        t_max = std::min(t_max, t2);
        if (t_min > t_max) return false;
    }
    if (t_max < 0.0f) return false;
    t_enter = std::max(t_min, 0.0f);

    if (hit_axis < 0) {
        face_normal = -dir;
    } else {
        Eigen::Vector3f n(0, 0, 0);
        n[hit_axis] = hit_sign;
        face_normal = n;
    }
    return true;
}

} // namespace

bool ViewportCore::buildPickPipeline() {
    // Three color attachments: R32UInt object_id, RGBA16F packed normal, and
    // RGBA32F exact world position (so surface pick lands on the true face, not
    // a ray-AABB approximation).
    WGPUColorTargetState color_targets[3] = {};
    color_targets[0].format    = WGPUTextureFormat_R32Uint;
    color_targets[0].writeMask = WGPUColorWriteMask_All;
    color_targets[1].format    = WGPUTextureFormat_RGBA16Float;
    color_targets[1].writeMask = WGPUColorWriteMask_All;
    color_targets[2].format    = WGPUTextureFormat_RGBA32Float;
    color_targets[2].writeMask = WGPUColorWriteMask_All;

    WGPUFragmentState frag = {};
    frag.module      = main_shader_module_;
    frag.entryPoint  = svFromCStr("fs_pick");
    frag.targetCount = 3;
    frag.targets     = color_targets;

    WGPUDepthStencilState depth = {};
    depth.format               = WGPUTextureFormat_Depth32Float;
    depth.depthWriteEnabled    = WGPUOptionalBool_True;
    depth.depthCompare         = WGPUCompareFunction_Less;
    depth.stencilFront.compare = WGPUCompareFunction_Always;
    depth.stencilBack.compare  = WGPUCompareFunction_Always;

    WGPURenderPipelineDescriptor rp_desc = {};
    rp_desc.layout              = pipeline_layout_;
    rp_desc.label               = svFromCStr("ifcviewer-wgpu.pick_pipeline");
    rp_desc.vertex.module       = main_shader_module_;
    rp_desc.vertex.entryPoint   = svFromCStr("vs_pick");
    rp_desc.vertex.bufferCount  = 0;
    rp_desc.fragment            = &frag;
    rp_desc.depthStencil        = &depth;
    rp_desc.primitive.topology  = WGPUPrimitiveTopology_TriangleList;
    rp_desc.primitive.cullMode  = WGPUCullMode_Back;
    rp_desc.primitive.frontFace = WGPUFrontFace_CCW;
    rp_desc.multisample.count   = 1;
    rp_desc.multisample.mask    = 0xFFFFFFFFu;

    pick_pipeline_ = wgpuDeviceCreateRenderPipeline(device_, &rp_desc);
    if (!pick_pipeline_) {
        Log::warn() << "wgpu pick pipeline creation failed";
        return false;
    }
    // The x-ray marquee variant rides along so no caller has to know about it.
    // A failure here is not fatal: picksInRect falls back to the depth-tested
    // read, which is the pre-x-ray behaviour rather than a broken viewport.
    buildBoxPickPipeline();
    return true;
}

bool ViewportCore::buildBoxPickPipeline() {
    // No colour targets: fs_boxpick's only output is the atomic bit it sets, so
    // the pass writes no image at all. A render pass still needs one attachment
    // — the pick depth view serves, bound read-only.
    WGPUFragmentState frag = {};
    frag.module      = main_shader_module_;
    frag.entryPoint  = svFromCStr("fs_boxpick");
    frag.targetCount = 0;
    frag.targets     = nullptr;

    // Always/no-write is the whole trick: every fragment survives, so an
    // occluded object records its bit just as a front-most one does.
    WGPUDepthStencilState depth = {};
    depth.format               = WGPUTextureFormat_Depth32Float;
    depth.depthWriteEnabled    = WGPUOptionalBool_False;
    depth.depthCompare         = WGPUCompareFunction_Always;
    depth.stencilFront.compare = WGPUCompareFunction_Always;
    depth.stencilBack.compare  = WGPUCompareFunction_Always;

    WGPURenderPipelineDescriptor rp_desc = {};
    rp_desc.layout              = pipeline_layout_;
    rp_desc.label               = svFromCStr("ifcviewer-wgpu.box_pick_pipeline");
    rp_desc.vertex.module       = main_shader_module_;
    rp_desc.vertex.entryPoint   = svFromCStr("vs_pick");
    rp_desc.vertex.bufferCount  = 0;
    rp_desc.fragment            = &frag;
    rp_desc.depthStencil        = &depth;
    rp_desc.primitive.topology  = WGPUPrimitiveTopology_TriangleList;
    // No back-face cull. A box that lands inside a closed solid would otherwise
    // see none of its faces and miss the object entirely.
    rp_desc.primitive.cullMode  = WGPUCullMode_None;
    rp_desc.primitive.frontFace = WGPUFrontFace_CCW;
    rp_desc.multisample.count   = 1;
    rp_desc.multisample.mask    = 0xFFFFFFFFu;

    box_pick_pipeline_ = wgpuDeviceCreateRenderPipeline(device_, &rp_desc);
    if (!box_pick_pipeline_) {
        Log::warn() << "wgpu box-pick pipeline creation failed";
        return false;
    }
    return true;
}

void ViewportCore::ensurePickAttachments(int w, int h) {
    if (w <= 0 || h <= 0) return;
    if (w == pick_w_ && h == pick_h_ && pick_color_view_) return;

    if (pick_color_view_)     { wgpuTextureViewRelease(pick_color_view_); pick_color_view_ = nullptr; }
    if (pick_color_texture_)  { wgpuTextureRelease(pick_color_texture_);  pick_color_texture_ = nullptr; }
    if (pick_normal_view_)    { wgpuTextureViewRelease(pick_normal_view_); pick_normal_view_ = nullptr; }
    if (pick_normal_texture_) { wgpuTextureRelease(pick_normal_texture_); pick_normal_texture_ = nullptr; }
    if (pick_position_view_)    { wgpuTextureViewRelease(pick_position_view_); pick_position_view_ = nullptr; }
    if (pick_position_texture_) { wgpuTextureRelease(pick_position_texture_); pick_position_texture_ = nullptr; }
    if (pick_depth_view_)     { wgpuTextureViewRelease(pick_depth_view_); pick_depth_view_ = nullptr; }
    if (pick_depth_texture_)  { wgpuTextureRelease(pick_depth_texture_);  pick_depth_texture_ = nullptr; }

    WGPUTextureDescriptor cdesc = {};
    cdesc.usage         = WGPUTextureUsage_RenderAttachment | WGPUTextureUsage_CopySrc;
    cdesc.dimension     = WGPUTextureDimension_2D;
    cdesc.size.width    = std::uint32_t(w);
    cdesc.size.height   = std::uint32_t(h);
    cdesc.size.depthOrArrayLayers = 1;
    cdesc.format        = WGPUTextureFormat_R32Uint;
    cdesc.mipLevelCount = 1;
    cdesc.sampleCount   = 1;
    cdesc.label         = svFromCStr("ifcviewer-wgpu.pick_color");
    pick_color_texture_ = wgpuDeviceCreateTexture(device_, &cdesc);
    pick_color_view_    = wgpuTextureCreateView(pick_color_texture_, nullptr);

    WGPUTextureDescriptor ndesc = cdesc;
    ndesc.format = WGPUTextureFormat_RGBA16Float;
    ndesc.label  = svFromCStr("ifcviewer-wgpu.pick_normal");
    pick_normal_texture_ = wgpuDeviceCreateTexture(device_, &ndesc);
    pick_normal_view_    = wgpuTextureCreateView(pick_normal_texture_, nullptr);

    WGPUTextureDescriptor pdesc = cdesc;
    pdesc.format = WGPUTextureFormat_RGBA32Float;
    pdesc.label  = svFromCStr("ifcviewer-wgpu.pick_position");
    pick_position_texture_ = wgpuDeviceCreateTexture(device_, &pdesc);
    pick_position_view_    = wgpuTextureCreateView(pick_position_texture_, nullptr);

    WGPUTextureDescriptor ddesc = {};
    ddesc.usage         = WGPUTextureUsage_RenderAttachment;
    ddesc.dimension     = WGPUTextureDimension_2D;
    ddesc.size.width    = std::uint32_t(w);
    ddesc.size.height   = std::uint32_t(h);
    ddesc.size.depthOrArrayLayers = 1;
    ddesc.format        = WGPUTextureFormat_Depth32Float;
    ddesc.mipLevelCount = 1;
    ddesc.sampleCount   = 1;
    ddesc.label         = svFromCStr("ifcviewer-wgpu.pick_depth");
    pick_depth_texture_ = wgpuDeviceCreateTexture(device_, &ddesc);
    WGPUTextureViewDescriptor dvdesc = {};
    dvdesc.format          = WGPUTextureFormat_Depth32Float;
    dvdesc.dimension       = WGPUTextureViewDimension_2D;
    dvdesc.mipLevelCount   = 1;
    dvdesc.arrayLayerCount = 1;
    dvdesc.aspect          = WGPUTextureAspect_DepthOnly;
    pick_depth_view_ = wgpuTextureCreateView(pick_depth_texture_, &dvdesc);

    if (!pick_staging_buffer_) {
        // 256 B is the smallest aligned staging buffer for a single-row copy.
        WGPUBufferDescriptor sb = {};
        sb.size  = 256;
        sb.usage = WGPUBufferUsage_CopyDst | WGPUBufferUsage_MapRead;
        sb.label = svFromCStr("ifcviewer-wgpu.pick_staging");
        pick_staging_buffer_ = wgpuDeviceCreateBuffer(device_, &sb);
    }
    if (!pick_normal_staging_buffer_) {
        WGPUBufferDescriptor sb = {};
        sb.size  = 256;
        sb.usage = WGPUBufferUsage_CopyDst | WGPUBufferUsage_MapRead;
        sb.label = svFromCStr("ifcviewer-wgpu.pick_normal_staging");
        pick_normal_staging_buffer_ = wgpuDeviceCreateBuffer(device_, &sb);
    }
    if (!pick_position_staging_buffer_) {
        WGPUBufferDescriptor sb = {};
        sb.size  = 256;
        sb.usage = WGPUBufferUsage_CopyDst | WGPUBufferUsage_MapRead;
        sb.label = svFromCStr("ifcviewer-wgpu.pick_position_staging");
        pick_position_staging_buffer_ = wgpuDeviceCreateBuffer(device_, &sb);
    }
    pick_w_ = w;
    pick_h_ = h;
}

void ViewportCore::releasePickResources() {
    if (pick_color_view_)     { wgpuTextureViewRelease(pick_color_view_); pick_color_view_ = nullptr; }
    if (pick_color_texture_)  { wgpuTextureRelease(pick_color_texture_);  pick_color_texture_ = nullptr; }
    if (pick_normal_view_)    { wgpuTextureViewRelease(pick_normal_view_); pick_normal_view_ = nullptr; }
    if (pick_normal_texture_) { wgpuTextureRelease(pick_normal_texture_); pick_normal_texture_ = nullptr; }
    if (pick_position_view_)    { wgpuTextureViewRelease(pick_position_view_); pick_position_view_ = nullptr; }
    if (pick_position_texture_) { wgpuTextureRelease(pick_position_texture_); pick_position_texture_ = nullptr; }
    if (pick_depth_view_)     { wgpuTextureViewRelease(pick_depth_view_); pick_depth_view_ = nullptr; }
    if (pick_depth_texture_)  { wgpuTextureRelease(pick_depth_texture_);  pick_depth_texture_ = nullptr; }
    if (pick_staging_buffer_) { wgpuBufferRelease(pick_staging_buffer_);  pick_staging_buffer_ = nullptr; }
    if (pick_normal_staging_buffer_) {
        wgpuBufferRelease(pick_normal_staging_buffer_);
        pick_normal_staging_buffer_ = nullptr;
    }
    if (pick_position_staging_buffer_) {
        wgpuBufferRelease(pick_position_staging_buffer_);
        pick_position_staging_buffer_ = nullptr;
    }
    if (pick_pipeline_)            { wgpuRenderPipelineRelease(pick_pipeline_); pick_pipeline_ = nullptr; }
    if (box_pick_pipeline_)        { wgpuRenderPipelineRelease(box_pick_pipeline_); box_pick_pipeline_ = nullptr; }
    if (box_pick_staging_buffer_)  {
        wgpuBufferRelease(box_pick_staging_buffer_);
        box_pick_staging_buffer_ = nullptr;
    }
    box_pick_staging_capacity_ = 0;
    if (hit_flags_staging_buffer_) {
        wgpuBufferRelease(hit_flags_staging_buffer_);
        hit_flags_staging_buffer_ = nullptr;
    }
    hit_flags_staging_capacity_ = 0;
    pick_w_ = pick_h_ = 0;
}

// Encode the one-shot pick pass (object_id + optional normal targets) and
// copy the texel at (x, y) into the pick staging buffer(s), then submit.
// Shared by the synchronous desktop pickObjectAt and the async web pick —
// only the readback after this differs (blocking map-spin vs spontaneous
// callback). Assumes the caller validated bounds + attachments.
void ViewportCore::encodePickReadbackToStaging(int x_pixels, int y_pixels,
                                               bool want_normal) {
    // The current frame's visible_draws are already on the GPU (uploaded
    // by the last render's cullModelCpuUpload). Encode a one-shot pass.
    WGPUCommandEncoder enc = wgpuDeviceCreateCommandEncoder(device_, nullptr);

    WGPURenderPassColorAttachment color[3] = {};
    color[0].view       = pick_color_view_;
    color[0].loadOp     = WGPULoadOp_Clear;
    color[0].storeOp    = WGPUStoreOp_Store;
    color[0].clearValue = { 0.0, 0.0, 0.0, 0.0 };  // object_id == 0 means miss
    color[0].depthSlice = WGPU_DEPTH_SLICE_UNDEFINED;
    color[1].view       = pick_normal_view_;
    color[1].loadOp     = WGPULoadOp_Clear;
    color[1].storeOp    = WGPUStoreOp_Store;
    color[1].clearValue = { 0.5, 0.5, 0.5, 0.0 };
    color[1].depthSlice = WGPU_DEPTH_SLICE_UNDEFINED;
    color[2].view       = pick_position_view_;
    color[2].loadOp     = WGPULoadOp_Clear;
    color[2].storeOp    = WGPUStoreOp_Store;
    color[2].clearValue = { 0.0, 0.0, 0.0, 0.0 };
    color[2].depthSlice = WGPU_DEPTH_SLICE_UNDEFINED;

    WGPURenderPassDepthStencilAttachment depth = {};
    depth.view              = pick_depth_view_;
    depth.depthLoadOp       = WGPULoadOp_Clear;
    depth.depthStoreOp      = WGPUStoreOp_Store;
    depth.depthClearValue   = 1.0f;
    depth.stencilLoadOp     = WGPULoadOp_Undefined;
    depth.stencilStoreOp    = WGPUStoreOp_Undefined;
    depth.stencilReadOnly   = true;

    WGPURenderPassDescriptor pass_desc = {};
    pass_desc.colorAttachmentCount   = 3;
    pass_desc.colorAttachments       = color;
    pass_desc.depthStencilAttachment = &depth;
    pass_desc.label                  = svFromCStr("ifcviewer-wgpu.pick_pass");

    WGPURenderPassEncoder pass = wgpuCommandEncoderBeginRenderPass(enc, &pass_desc);
    wgpuRenderPassEncoderSetPipeline(pass, pick_pipeline_);
    wgpuRenderPassEncoderSetBindGroup(pass, 0, frame_bind_group_, 0, nullptr);
    for (const auto& [session_model_id, m] : models_gpu_) {
        if (m.hidden) continue;
        for (const auto& c : m.chunks) {
            if (!c.bind_group || c.total_visible_vertices == 0) continue;
            wgpuRenderPassEncoderSetBindGroup(pass, 1, c.bind_group, 0, nullptr);
            wgpuRenderPassEncoderDraw(pass, c.total_visible_vertices, 1, 0, 0);
        }
    }
    wgpuRenderPassEncoderEnd(pass);
    wgpuRenderPassEncoderRelease(pass);

    // Copy the single texel at (x, y) into the staging buffer.
    WGPUTexelCopyTextureInfo src = {};
    src.texture  = pick_color_texture_;
    src.aspect   = WGPUTextureAspect_All;
    src.origin.x = std::uint32_t(x_pixels);
    src.origin.y = std::uint32_t(y_pixels);

    WGPUTexelCopyBufferInfo dst = {};
    dst.buffer              = pick_staging_buffer_;
    dst.layout.bytesPerRow  = 256;
    dst.layout.rowsPerImage = 1;

    WGPUExtent3D extent = {};
    extent.width  = 1;
    extent.height = 1;
    extent.depthOrArrayLayers = 1;

    wgpuCommandEncoderCopyTextureToBuffer(enc, &src, &dst, &extent);

    if (want_normal) {
        WGPUTexelCopyTextureInfo nsrc = {};
        nsrc.texture  = pick_normal_texture_;
        nsrc.aspect   = WGPUTextureAspect_All;
        nsrc.origin.x = std::uint32_t(x_pixels);
        nsrc.origin.y = std::uint32_t(y_pixels);

        WGPUTexelCopyBufferInfo ndst = {};
        ndst.buffer              = pick_normal_staging_buffer_;
        ndst.layout.bytesPerRow  = 256;
        ndst.layout.rowsPerImage = 1;

        wgpuCommandEncoderCopyTextureToBuffer(enc, &nsrc, &ndst, &extent);

        // Exact world position too (surface pick wants both).
        WGPUTexelCopyTextureInfo psrc = nsrc;
        psrc.texture = pick_position_texture_;
        WGPUTexelCopyBufferInfo pdst = ndst;
        pdst.buffer  = pick_position_staging_buffer_;
        wgpuCommandEncoderCopyTextureToBuffer(enc, &psrc, &pdst, &extent);
    }

    WGPUCommandBuffer cmd = wgpuCommandEncoderFinish(enc, nullptr);
    wgpuQueueSubmit(queue_, 1, &cmd);
    wgpuCommandBufferRelease(cmd);
    wgpuCommandEncoderRelease(enc);
}

std::uint32_t ViewportCore::pickObjectAt(int x_pixels, int y_pixels,
                                         Eigen::Vector3f* normal_out) {
    if (normal_out) *normal_out = Eigen::Vector3f(0, 0, 1);
    if (!pick_pipeline_ || !device_ || !queue_ || models_gpu_.empty()) return 0;
    if (configured_w_ <= 0 || configured_h_ <= 0) return 0;
    if (x_pixels < 0 || y_pixels < 0 ||
        x_pixels >= configured_w_ || y_pixels >= configured_h_) return 0;

    ensurePickAttachments(configured_w_, configured_h_);
    if (!pick_color_view_ || !pick_depth_view_ || !pick_staging_buffer_) return 0;
    if (normal_out && !pick_normal_staging_buffer_) return 0;

    encodePickReadbackToStaging(x_pixels, y_pixels, normal_out != nullptr);

    // Sync wait — pick is rare (click), so the GPU stall is fine.
    struct MapReq { bool done = false; bool ok = false; };
    MapReq req;
    WGPUBufferMapCallbackInfo mcb = {};
    mcb.mode = kAsyncCbMode;
    mcb.callback = [](WGPUMapAsyncStatus status, WGPUStringView /*msg*/,
                      void* ud1, void* /*ud2*/) {
        auto* r = static_cast<MapReq*>(ud1);
        r->done = true;
        r->ok   = (status == WGPUMapAsyncStatus_Success);
    };
    mcb.userdata1 = &req;

    wgpuBufferMapAsync(pick_staging_buffer_, WGPUMapMode_Read, 0, 256, mcb);
    while (!req.done) waitTickInstance(instance_);
    if (!req.ok) return 0;

    const std::uint32_t* mapped = static_cast<const std::uint32_t*>(
        wgpuBufferGetConstMappedRange(pick_staging_buffer_, 0, 256));
    const std::uint32_t object_id = mapped ? mapped[0] : 0u;
    wgpuBufferUnmap(pick_staging_buffer_);

    if (normal_out && object_id != 0) {
        MapReq nreq;
        WGPUBufferMapCallbackInfo ncb = mcb;
        ncb.userdata1 = &nreq;
        wgpuBufferMapAsync(pick_normal_staging_buffer_, WGPUMapMode_Read, 0, 256, ncb);
        while (!nreq.done) waitTickInstance(instance_);
        if (nreq.ok) {
            Eigen::Vector3f n;
            if (decodeMappedPickNormal(n)) *normal_out = n;  // decodeMapped… unmaps
        }
    }

    return object_id;
}

bool ViewportCore::decodeMappedPickPosition(Eigen::Vector3f& out) {
    const float* p = static_cast<const float*>(
        wgpuBufferGetConstMappedRange(pick_position_staging_buffer_, 0, 256));
    bool ok = false;
    if (p && p[3] > 0.5f) {  // w == 1.0 for a real fragment, 0 for a cleared miss
        out = Eigen::Vector3f(p[0], p[1], p[2]);
        ok = true;
    }
    wgpuBufferUnmap(pick_position_staging_buffer_);
    return ok;
}

bool ViewportCore::decodeMappedPickNormal(Eigen::Vector3f& out) {
    const std::uint16_t* halves = static_cast<const std::uint16_t*>(
        wgpuBufferGetConstMappedRange(pick_normal_staging_buffer_, 0, 256));
    bool ok = false;
    if (halves) {
        // IEEE 754 half → float. Standard bit-fiddle (no STL helper pre-C++23).
        auto h2f = [](std::uint16_t h) -> float {
            const std::uint32_t sign     = std::uint32_t(h & 0x8000u) << 16;
            std::uint32_t       exponent = std::uint32_t(h & 0x7C00u) >> 10;
            std::uint32_t       mantissa = std::uint32_t(h & 0x03FFu);
            if (exponent == 0) {
                if (mantissa == 0) {
                    union { std::uint32_t u; float f; } v{ sign };
                    return v.f;
                }
                while ((mantissa & 0x0400u) == 0) { mantissa <<= 1; --exponent; }
                ++exponent;
                mantissa &= 0x03FFu;
            } else if (exponent == 0x1Fu) {
                exponent = 0xFFu;
            } else {
                exponent += (127u - 15u);
            }
            const std::uint32_t bits = sign | (exponent << 23) | (mantissa << 13);
            union { std::uint32_t u; float f; } v{ bits };
            return v.f;
        };
        const float nx = h2f(halves[0]) * 2.0f - 1.0f;
        const float ny = h2f(halves[1]) * 2.0f - 1.0f;
        const float nz = h2f(halves[2]) * 2.0f - 1.0f;
        Eigen::Vector3f n(nx, ny, nz);
        if (n.squaredNorm() > 1e-6f) { out = n.normalized(); ok = true; }
    }
    wgpuBufferUnmap(pick_normal_staging_buffer_);
    return ok;
}

// Route a pick result through the selection state machine. Mirrors the
// desktop ViewportWindow::mouseReleaseEvent semantics: no modifier replaces,
// add(=Shift) extends, remove(=Ctrl) subtracts, and an empty-space click
// (id == 0) with no modifier clears. Marks selection_ dirty so the next
// render's uploadSelectionFlagsIfDirty flushes the highlight.
void ViewportCore::applyPickToSelection(std::uint32_t object_id, bool add, bool remove) {
    if (object_id == 0) {
        if (!add && !remove) selection_.clear();
        return;
    }
    if (remove)      selection_.remove(object_id);
    else if (add)    selection_.add(object_id);
    else             selection_.replace(object_id);
}

void ViewportCore::applyMarqueeToSelection(const std::vector<std::uint32_t>& ids,
                                           bool add, bool remove) {
    if (!add && !remove) selection_.clear();   // plain marquee replaces
    for (std::uint32_t id : ids) {
        if (id == 0) continue;
        if (remove) selection_.remove(id);
        else        selection_.add(id);        // replace (post-clear) or add
    }
    host_->requestFrame();
}

void ViewportCore::hideSelected() {
    if (selection_.count() == 0) return;
    for (uint32_t id : selection_.selectionIds()) visibility_.hide(id);
    const size_t n = selection_.count();
    selection_.clear();   // hiding deselects, matching the desktop/GL behaviour
    Log::info().noquote().nospace() << "[wgpu] hid " << n << " selected";
    host_->requestFrame();
}

void ViewportCore::isolateSelected() {
    if (selection_.count() == 0) return;
    // Hide every object in a VISIBLE model that isn't selected. Model-hidden
    // objects stay model-hidden (element-level hiding on top is redundant), and
    // object_id 0 (unpickable) is skipped.
    const auto& sel_ids = selection_.selectionIds();
    for (const auto& [session_model_id, m] : models_gpu_) {
        if (m.hidden) continue;
        for (const InstanceInfo& inst : m.instances) {
            if (inst.object_id == 0) continue;
            if (sel_ids.find(inst.object_id) == sel_ids.end())
                visibility_.hide(inst.object_id);
        }
    }
    Log::info().noquote().nospace() << "[wgpu] isolated " << selection_.count();
    host_->requestFrame();
}

void ViewportCore::showAll() {
    if (visibility_.hiddenCount() == 0) return;
    visibility_.clear();
    Log::info() << "[wgpu] show all";
    host_->requestFrame();
}

void ViewportCore::hideAll() {
    // Element-level hide of everything in a visible model — the inverse of
    // showAll, and isolateSelected with an empty selection. Model-hidden
    // models are already gone from the cull, so they contribute nothing.
    for (const auto& [session_model_id, m] : models_gpu_) {
        if (m.hidden) continue;
        for (const InstanceInfo& inst : m.instances) visibility_.hide(inst.object_id);
    }
    Log::info().noquote().nospace() << "[wgpu] hid all (" << visibility_.hiddenCount() << ")";
    host_->requestFrame();
}

void ViewportCore::setObjectsVisible(const std::vector<std::uint32_t>& object_ids, bool visible) {
    for (std::uint32_t id : object_ids) {
        if (visible) visibility_.show(id);
        else         visibility_.hide(id);
    }
    host_->requestFrame();
}

void ViewportCore::setObjectsColor(const std::vector<std::uint32_t>& object_ids,
                                   std::uint32_t rgba8) {
    if (object_ids.empty()) return;
    const std::unordered_set<std::uint32_t> wanted(object_ids.begin(), object_ids.end());

    // One pass per model: patch the CPU mirror, then re-upload that model's
    // instance records only if it actually owned one of the ids.
    for (auto& [session_model_id, m] : models_gpu_) {
        bool touched = false;
        for (InstanceInfo& inst : m.instances) {
            if (inst.color_override_rgba8 == rgba8) continue;
            if (wanted.find(inst.object_id) == wanted.end()) continue;
            inst.color_override_rgba8 = rgba8;
            touched = true;
        }
        if (touched) uploadInstanceRecords(m);
    }
    host_->requestFrame();
}

void ViewportCore::clearObjectColors() {
    for (auto& [session_model_id, m] : models_gpu_) {
        bool touched = false;
        for (InstanceInfo& inst : m.instances) {
            if (inst.color_override_rgba8 == 0u) continue;
            inst.color_override_rgba8 = 0u;
            touched = true;
        }
        if (touched) uploadInstanceRecords(m);
    }
    host_->requestFrame();
}

void ViewportCore::toggleXray() {
    constexpr float kXrayOnCap = 0.3f;
    xray_alpha_cap_ = (xray_alpha_cap_ < 1.0f) ? 1.0f : kXrayOnCap;
    Log::info().noquote().nospace()
        << "[wgpu] x-ray " << (xray_alpha_cap_ < 1.0f ? "ON" : "OFF")
        << " (cap=" << xray_alpha_cap_ << ")";
    host_->requestFrame();
}

#if defined(__EMSCRIPTEN__)
void ViewportCore::pickObjectAtAsync(int x_pixels, int y_pixels,
                                     std::function<void(std::uint32_t)> cb) {
    // Async sibling of pickObjectAt for the web build, where the blocking
    // map-spin would hang the JS event loop. Encodes the same pick pass, then
    // maps the staging buffer with a spontaneous callback (AllowSpontaneous +
    // the browser microtask loop) that delivers object_id to `cb`. No normal
    // readback — object pick only (surface pick lands in a follow-up).
    auto miss = [&cb](std::uint32_t id) { if (cb) cb(id); };

    if (!pick_pipeline_ || !device_ || !queue_ || models_gpu_.empty()) { miss(0); return; }
    if (configured_w_ <= 0 || configured_h_ <= 0) { miss(0); return; }
    if (x_pixels < 0 || y_pixels < 0 ||
        x_pixels >= configured_w_ || y_pixels >= configured_h_) { miss(0); return; }

    ensurePickAttachments(configured_w_, configured_h_);
    if (!pick_color_view_ || !pick_depth_view_ || !pick_staging_buffer_) { miss(0); return; }

    // One pick in flight at a time. Clicks are far slower than a readback, so
    // dropping a pick issued while another is mapping is acceptable (and
    // avoids racing two maps on the same staging buffer).
    if (pick_async_in_flight_) { miss(0); return; }
    pick_async_in_flight_ = true;
    pick_async_cb_ = std::move(cb);

    encodePickReadbackToStaging(x_pixels, y_pixels, /*want_normal=*/false);

    WGPUBufferMapCallbackInfo mcb = {};
    mcb.mode = kAsyncCbMode;  // AllowSpontaneous on web
    mcb.callback = [](WGPUMapAsyncStatus status, WGPUStringView /*msg*/,
                      void* ud1, void* /*ud2*/) {
        auto* self = static_cast<ViewportCore*>(ud1);
        std::uint32_t object_id = 0;
        if (status == WGPUMapAsyncStatus_Success) {
            const std::uint32_t* mapped = static_cast<const std::uint32_t*>(
                wgpuBufferGetConstMappedRange(self->pick_staging_buffer_, 0, 256));
            object_id = mapped ? mapped[0] : 0u;
            wgpuBufferUnmap(self->pick_staging_buffer_);
        }
        auto cb = std::move(self->pick_async_cb_);
        self->pick_async_cb_ = nullptr;
        self->pick_async_in_flight_ = false;
        if (cb) cb(object_id);
    };
    mcb.userdata1 = this;
    wgpuBufferMapAsync(pick_staging_buffer_, WGPUMapMode_Read, 0, 256, mcb);
}
#endif  // __EMSCRIPTEN__

bool ViewportCore::encodeBoxPickToStaging(int& x, int& y, int& w, int& h,
                                          std::uint64_t& padded_bpr_out,
                                          std::uint64_t& needed_bytes_out) {
    if (w <= 0 || h <= 0) return false;
    if (!pick_pipeline_ || !device_ || !queue_ || models_gpu_.empty()) return false;
    if (configured_w_ <= 0 || configured_h_ <= 0) return false;
    if (x < 0) { w += x; x = 0; }
    if (y < 0) { h += y; y = 0; }
    if (x + w > configured_w_) w = configured_w_ - x;
    if (y + h > configured_h_) h = configured_h_ - y;
    if (w <= 0 || h <= 0) return false;

    ensurePickAttachments(configured_w_, configured_h_);
    if (!pick_color_view_ || !pick_depth_view_) return false;

    // Padded bytes-per-row. R32UInt = 4 B/texel; align to 256 B.
    constexpr std::uint64_t kWgpuBytesPerRowAlign = 256;
    const std::uint64_t unpadded_bpr = std::uint64_t(w) * 4;
    const std::uint64_t padded_bpr   = (unpadded_bpr + kWgpuBytesPerRowAlign - 1)
                                       / kWgpuBytesPerRowAlign
                                       * kWgpuBytesPerRowAlign;
    const std::uint64_t needed_bytes = padded_bpr * std::uint64_t(h);
    if (needed_bytes > box_pick_staging_capacity_) {
        if (box_pick_staging_buffer_) {
            wgpuBufferRelease(box_pick_staging_buffer_);
            box_pick_staging_buffer_ = nullptr;
        }
        const std::uint64_t cap = std::max<std::uint64_t>(needed_bytes * 2, 64 * 1024);
        WGPUBufferDescriptor sb = {};
        sb.size  = cap;
        sb.usage = WGPUBufferUsage_CopyDst | WGPUBufferUsage_MapRead;
        sb.label = svFromCStr("ifcviewer-wgpu.box_pick_staging");
        box_pick_staging_buffer_ = wgpuDeviceCreateBuffer(device_, &sb);
        box_pick_staging_capacity_ = cap;
    }
    if (!box_pick_staging_buffer_) return false;

    WGPUCommandEncoder enc = wgpuDeviceCreateCommandEncoder(device_, nullptr);

    WGPURenderPassColorAttachment color[3] = {};
    color[0].view       = pick_color_view_;
    color[0].loadOp     = WGPULoadOp_Clear;
    color[0].storeOp    = WGPUStoreOp_Store;
    color[0].clearValue = { 0, 0, 0, 0 };
    color[0].depthSlice = WGPU_DEPTH_SLICE_UNDEFINED;
    color[1].view       = pick_normal_view_;
    color[1].loadOp     = WGPULoadOp_Clear;
    color[1].storeOp    = WGPUStoreOp_Store;
    color[1].clearValue = { 0.5, 0.5, 0.5, 0 };
    color[1].depthSlice = WGPU_DEPTH_SLICE_UNDEFINED;
    color[2].view       = pick_position_view_;   // rendered (pipeline outputs 3), not read here
    color[2].loadOp     = WGPULoadOp_Clear;
    color[2].storeOp    = WGPUStoreOp_Store;
    color[2].clearValue = { 0, 0, 0, 0 };
    color[2].depthSlice = WGPU_DEPTH_SLICE_UNDEFINED;

    WGPURenderPassDepthStencilAttachment depth = {};
    depth.view            = pick_depth_view_;
    depth.depthLoadOp     = WGPULoadOp_Clear;
    depth.depthStoreOp    = WGPUStoreOp_Store;
    depth.depthClearValue = 1.0f;
    depth.stencilLoadOp   = WGPULoadOp_Undefined;
    depth.stencilStoreOp  = WGPUStoreOp_Undefined;
    depth.stencilReadOnly = true;

    WGPURenderPassDescriptor pass_desc = {};
    pass_desc.colorAttachmentCount   = 3;
    pass_desc.colorAttachments       = color;
    pass_desc.depthStencilAttachment = &depth;
    pass_desc.label                  = svFromCStr("ifcviewer-wgpu.box_pick_pass");

    WGPURenderPassEncoder pass = wgpuCommandEncoderBeginRenderPass(enc, &pass_desc);
    wgpuRenderPassEncoderSetPipeline(pass, pick_pipeline_);
    wgpuRenderPassEncoderSetBindGroup(pass, 0, frame_bind_group_, 0, nullptr);
    for (const auto& [session_model_id, m] : models_gpu_) {
        if (m.hidden) continue;
        for (const auto& c : m.chunks) {
            if (!c.bind_group || c.total_visible_vertices == 0) continue;
            wgpuRenderPassEncoderSetBindGroup(pass, 1, c.bind_group, 0, nullptr);
            wgpuRenderPassEncoderDraw(pass, c.total_visible_vertices, 1, 0, 0);
        }
    }
    wgpuRenderPassEncoderEnd(pass);
    wgpuRenderPassEncoderRelease(pass);

    WGPUTexelCopyTextureInfo src = {};
    src.texture  = pick_color_texture_;
    src.aspect   = WGPUTextureAspect_All;
    src.origin.x = std::uint32_t(x);
    src.origin.y = std::uint32_t(y);

    WGPUTexelCopyBufferInfo dst = {};
    dst.buffer              = box_pick_staging_buffer_;
    dst.layout.bytesPerRow  = std::uint32_t(padded_bpr);
    dst.layout.rowsPerImage = std::uint32_t(h);

    WGPUExtent3D extent = {};
    extent.width  = std::uint32_t(w);
    extent.height = std::uint32_t(h);
    extent.depthOrArrayLayers = 1;

    wgpuCommandEncoderCopyTextureToBuffer(enc, &src, &dst, &extent);

    WGPUCommandBuffer cmd = wgpuCommandEncoderFinish(enc, nullptr);
    wgpuQueueSubmit(queue_, 1, &cmd);
    wgpuCommandBufferRelease(cmd);
    wgpuCommandEncoderRelease(enc);

    padded_bpr_out   = padded_bpr;
    needed_bytes_out = needed_bytes;
    return true;
}

std::vector<std::uint32_t> ViewportCore::collectMappedBoxPickIds(
        std::uint64_t padded_bpr, int w, int h, std::uint64_t needed_bytes) {
    std::vector<std::uint32_t> out;
    const std::uint8_t* mapped = static_cast<const std::uint8_t*>(
        wgpuBufferGetConstMappedRange(box_pick_staging_buffer_, 0, needed_bytes));
    std::unordered_set<std::uint32_t> seen;
    if (mapped) {
        for (int row = 0; row < h; ++row) {
            const std::uint32_t* line = reinterpret_cast<const std::uint32_t*>(
                mapped + std::size_t(row) * std::size_t(padded_bpr));
            for (int col = 0; col < w; ++col) {
                const std::uint32_t id = line[col];
                if (id != 0) seen.insert(id);
            }
        }
    }
    wgpuBufferUnmap(box_pick_staging_buffer_);
    out.reserve(seen.size());
    for (std::uint32_t id : seen) out.push_back(id);
    return out;
}

bool ViewportCore::encodeXrayBoxPickToStaging(int& x, int& y, int& w, int& h,
                                              std::uint64_t& needed_bytes_out) {
    if (w <= 0 || h <= 0) return false;
    if (!box_pick_pipeline_ || !device_ || !queue_ || models_gpu_.empty()) return false;
    if (!hit_flags_buffer_ || hit_flags_words_ == 0) return false;
    if (configured_w_ <= 0 || configured_h_ <= 0) return false;
    if (x < 0) { w += x; x = 0; }
    if (y < 0) { h += y; y = 0; }
    if (x + w > configured_w_) w = configured_w_ - x;
    if (y + h > configured_h_) h = configured_h_ - y;
    if (w <= 0 || h <= 0) return false;

    ensurePickAttachments(configured_w_, configured_h_);
    if (!pick_depth_view_) return false;

    const std::uint64_t needed_bytes = std::uint64_t(hit_flags_words_) * sizeof(std::uint32_t);
    if (needed_bytes > hit_flags_staging_capacity_) {
        if (hit_flags_staging_buffer_) {
            wgpuBufferRelease(hit_flags_staging_buffer_);
            hit_flags_staging_buffer_ = nullptr;
        }
        const std::uint64_t cap = std::max<std::uint64_t>(needed_bytes * 2, 4 * 1024);
        WGPUBufferDescriptor sb = {};
        sb.size  = cap;
        sb.usage = WGPUBufferUsage_CopyDst | WGPUBufferUsage_MapRead;
        sb.label = svFromCStr("ifcviewer-wgpu.hit_flags_staging");
        hit_flags_staging_buffer_   = wgpuDeviceCreateBuffer(device_, &sb);
        hit_flags_staging_capacity_ = cap;
    }
    if (!hit_flags_staging_buffer_) return false;

    WGPUCommandEncoder enc = wgpuDeviceCreateCommandEncoder(device_, nullptr);

    // Every pick starts from no hits; the bits are pure output.
    wgpuCommandEncoderClearBuffer(enc, hit_flags_buffer_, 0, needed_bytes);

    // Depth is bound read-only and never compared (the pipeline is Always), so
    // whatever the last pass left in it is irrelevant.
    WGPURenderPassDepthStencilAttachment depth = {};
    depth.view            = pick_depth_view_;
    depth.depthLoadOp     = WGPULoadOp_Undefined;
    depth.depthStoreOp    = WGPUStoreOp_Undefined;
    depth.depthReadOnly   = true;
    depth.stencilLoadOp   = WGPULoadOp_Undefined;
    depth.stencilStoreOp  = WGPUStoreOp_Undefined;
    depth.stencilReadOnly = true;

    WGPURenderPassDescriptor pass_desc = {};
    pass_desc.colorAttachmentCount   = 0;
    pass_desc.colorAttachments       = nullptr;
    pass_desc.depthStencilAttachment = &depth;
    pass_desc.label                  = svFromCStr("ifcviewer-wgpu.xray_box_pick_pass");

    WGPURenderPassEncoder pass = wgpuCommandEncoderBeginRenderPass(enc, &pass_desc);
    // The scissor is what makes this a BOX pick: geometry is drawn full-screen
    // as usual, and only fragments landing in the marquee survive to set a bit.
    wgpuRenderPassEncoderSetScissorRect(pass, std::uint32_t(x), std::uint32_t(y),
                                        std::uint32_t(w), std::uint32_t(h));
    wgpuRenderPassEncoderSetPipeline(pass, box_pick_pipeline_);
    wgpuRenderPassEncoderSetBindGroup(pass, 0, frame_bind_group_, 0, nullptr);
    for (const auto& [session_model_id, m] : models_gpu_) {
        if (m.hidden) continue;
        for (const auto& c : m.chunks) {
            if (!c.bind_group || c.total_visible_vertices == 0) continue;
            wgpuRenderPassEncoderSetBindGroup(pass, 1, c.bind_group, 0, nullptr);
            wgpuRenderPassEncoderDraw(pass, c.total_visible_vertices, 1, 0, 0);
        }
    }
    wgpuRenderPassEncoderEnd(pass);
    wgpuRenderPassEncoderRelease(pass);

    wgpuCommandEncoderCopyBufferToBuffer(enc, hit_flags_buffer_, 0,
                                         hit_flags_staging_buffer_, 0, needed_bytes);

    WGPUCommandBuffer cmd = wgpuCommandEncoderFinish(enc, nullptr);
    wgpuQueueSubmit(queue_, 1, &cmd);
    wgpuCommandBufferRelease(cmd);
    wgpuCommandEncoderRelease(enc);

    needed_bytes_out = needed_bytes;
    return true;
}

std::vector<std::uint32_t> ViewportCore::collectMappedXrayHitIds(std::uint64_t needed_bytes) {
    std::vector<std::uint32_t> out;
    const std::uint32_t* words = static_cast<const std::uint32_t*>(
        wgpuBufferGetConstMappedRange(hit_flags_staging_buffer_, 0, needed_bytes));
    if (words) {
        const std::size_t n = std::size_t(needed_bytes / sizeof(std::uint32_t));
        for (std::size_t i = 0; i < n; ++i) {
            const std::uint32_t bits = words[i];
            if (!bits) continue;   // the overwhelmingly common case
            for (std::uint32_t b = 0; b < 32u; ++b) {
                if (!(bits & (1u << b))) continue;
                const std::uint32_t id = std::uint32_t(i) * 32u + b;
                if (id != 0) out.push_back(id);   // 0 is the "no object" sentinel
            }
        }
    }
    wgpuBufferUnmap(hit_flags_staging_buffer_);
    return out;
}

std::vector<std::uint32_t> ViewportCore::picksInRect(int x, int y, int w, int h) {
    // X-ray: select through, via the depth-less bitmask pass.
    if (xrayActive() && box_pick_pipeline_) {
        std::uint64_t hit_bytes = 0;
        if (!encodeXrayBoxPickToStaging(x, y, w, h, hit_bytes)) return {};
        struct MapReq { bool done = false; bool ok = false; };
        MapReq req;
        WGPUBufferMapCallbackInfo mcb = {};
        mcb.mode = kAsyncCbMode;
        mcb.callback = [](WGPUMapAsyncStatus status, WGPUStringView /*msg*/,
                          void* ud1, void* /*ud2*/) {
            auto* r = static_cast<MapReq*>(ud1);
            r->done = true;
            r->ok   = (status == WGPUMapAsyncStatus_Success);
        };
        mcb.userdata1 = &req;
        wgpuBufferMapAsync(hit_flags_staging_buffer_, WGPUMapMode_Read, 0, hit_bytes, mcb);
        while (!req.done) waitTickInstance(instance_);
        if (!req.ok) return {};
        return collectMappedXrayHitIds(hit_bytes);
    }

    std::uint64_t padded_bpr = 0, needed_bytes = 0;
    if (!encodeBoxPickToStaging(x, y, w, h, padded_bpr, needed_bytes)) return {};

    struct MapReq { bool done = false; bool ok = false; };
    MapReq req;
    WGPUBufferMapCallbackInfo mcb = {};
    mcb.mode = kAsyncCbMode;
    mcb.callback = [](WGPUMapAsyncStatus status, WGPUStringView /*msg*/,
                      void* ud1, void* /*ud2*/) {
        auto* r = static_cast<MapReq*>(ud1);
        r->done = true;
        r->ok   = (status == WGPUMapAsyncStatus_Success);
    };
    mcb.userdata1 = &req;
    wgpuBufferMapAsync(box_pick_staging_buffer_, WGPUMapMode_Read, 0, needed_bytes, mcb);
    while (!req.done) waitTickInstance(instance_);
    if (!req.ok) return {};
    return collectMappedBoxPickIds(padded_bpr, w, h, needed_bytes);
}

#if defined(__EMSCRIPTEN__)
void ViewportCore::picksInRectAsync(int x, int y, int w, int h,
                                    std::function<void(std::vector<std::uint32_t>)> cb) {
    auto miss = [&cb]() { if (cb) cb({}); };
    if (box_pick_async_in_flight_) { miss(); return; }

    // X-ray: select through. Same spontaneous-map dance, but the mapped buffer
    // is a per-object bitmask rather than a rect of the object_id image, so the
    // rect dims the other callback walks are not needed here.
    if (xrayActive() && box_pick_pipeline_) {
        std::uint64_t hit_bytes = 0;
        if (!encodeXrayBoxPickToStaging(x, y, w, h, hit_bytes)) { miss(); return; }
        box_pick_async_bytes_     = hit_bytes;
        box_pick_async_xray_      = true;
        box_pick_async_in_flight_ = true;
        box_pick_async_cb_        = std::move(cb);

        WGPUBufferMapCallbackInfo xcb = {};
        xcb.mode = kAsyncCbMode;
        xcb.callback = [](WGPUMapAsyncStatus status, WGPUStringView /*msg*/,
                          void* ud1, void* /*ud2*/) {
            auto* self = static_cast<ViewportCore*>(ud1);
            std::vector<std::uint32_t> ids;
            if (status == WGPUMapAsyncStatus_Success) {
                ids = self->collectMappedXrayHitIds(self->box_pick_async_bytes_);
            }
            auto done = std::move(self->box_pick_async_cb_);
            self->box_pick_async_cb_        = nullptr;
            self->box_pick_async_in_flight_ = false;
            self->box_pick_async_xray_      = false;
            if (done) done(std::move(ids));
        };
        xcb.userdata1 = this;
        wgpuBufferMapAsync(hit_flags_staging_buffer_, WGPUMapMode_Read, 0, hit_bytes, xcb);
        return;
    }

    std::uint64_t padded_bpr = 0, needed_bytes = 0;
    if (!encodeBoxPickToStaging(x, y, w, h, padded_bpr, needed_bytes)) { miss(); return; }

    // Stash the (clamped) rect so the spontaneous map callback can walk the
    // padded staging rows without recomputing.
    box_pick_async_w_          = w;
    box_pick_async_h_          = h;
    box_pick_async_padded_bpr_ = padded_bpr;
    box_pick_async_bytes_      = needed_bytes;
    box_pick_async_in_flight_  = true;
    box_pick_async_cb_         = std::move(cb);

    WGPUBufferMapCallbackInfo mcb = {};
    mcb.mode = kAsyncCbMode;  // AllowSpontaneous on web
    mcb.callback = [](WGPUMapAsyncStatus status, WGPUStringView /*msg*/,
                      void* ud1, void* /*ud2*/) {
        auto* self = static_cast<ViewportCore*>(ud1);
        std::vector<std::uint32_t> ids;
        if (status == WGPUMapAsyncStatus_Success) {
            ids = self->collectMappedBoxPickIds(self->box_pick_async_padded_bpr_,
                                                self->box_pick_async_w_,
                                                self->box_pick_async_h_,
                                                self->box_pick_async_bytes_);
        }
        auto cb = std::move(self->box_pick_async_cb_);
        self->box_pick_async_cb_ = nullptr;
        self->box_pick_async_in_flight_ = false;
        if (cb) cb(std::move(ids));
    };
    mcb.userdata1 = this;
    wgpuBufferMapAsync(box_pick_staging_buffer_, WGPUMapMode_Read, 0, needed_bytes, mcb);
}
#endif

bool ViewportCore::raycastSurfaceForObject(std::uint32_t object_id, int x_pixels, int y_pixels,
                                           const Eigen::Vector3f& mrt_normal,
                                           Eigen::Vector3f& world_pos_out,
                                           Eigen::Vector3f& world_normal_out,
                                           float& aabb_radius_out) {
    aabb_radius_out = 0.0f;
    if (object_id == 0) return false;

    // WebGPU forbids partial copies of Depth32Float, so ray-cast against
    // each instance carrying the picked object_id rather than reading
    // back per-pixel depth.
    Eigen::Matrix4f view, proj;
    buildViewProj(view, proj);
    Eigen::Matrix4f inv_vp;
    if (!tryInvert4f(proj * view, inv_vp)) return false;

    const float ndc_x = (2.0f * float(x_pixels) / float(configured_w_)) - 1.0f;
    const float ndc_y = 1.0f - (2.0f * float(y_pixels) / float(configured_h_));
    const Eigen::Vector4f far_clip(ndc_x, ndc_y, 1.0f, 1.0f);
    const Eigen::Vector4f far_w   = inv_vp * far_clip;
    if (std::abs(far_w.w()) < 1e-6f) return false;
    const Eigen::Vector3f far_world = far_w.head<3>() / far_w.w();

    const Eigen::Vector3f eye = orbitEye(camera_target_, camera_distance_,
                                         camera_yaw_deg_, camera_pitch_deg_);
    Eigen::Vector3f ray_dir = far_world - eye;
    if (ray_dir.squaredNorm() < 1e-8f) return false;
    ray_dir.normalize();

    float best_t = std::numeric_limits<float>::infinity();
    Eigen::Vector3f best_point;
    Eigen::Vector3f best_normal;
    float           best_radius = 0.0f;
    bool found = false;
    for (const auto& [session_model_id, m] : models_gpu_) {
        if (m.hidden) continue;
        for (const auto& inst : m.instances) {
            if (inst.object_id != object_id) continue;
            float t = 0.0f;
            Eigen::Vector3f n;
            if (!rayAABBHit(eye, ray_dir,
                            inst.world_aabb_min, inst.world_aabb_max,
                            t, n)) continue;
            if (t < best_t) {
                best_t      = t;
                best_point  = eye + ray_dir * t;
                best_normal = n;
                const float dx = inst.world_aabb_max[0] - inst.world_aabb_min[0];
                const float dy = inst.world_aabb_max[1] - inst.world_aabb_min[1];
                const float dz = inst.world_aabb_max[2] - inst.world_aabb_min[2];
                best_radius = 0.5f * std::sqrt(dx * dx + dy * dy + dz * dz);
                found       = true;
            }
        }
    }
    if (!found) return false;

    aabb_radius_out  = best_radius;
    world_pos_out    = best_point;
    // Prefer per-fragment normal from the pick MRT; fall back to AABB face.
    world_normal_out = (mrt_normal.squaredNorm() > 1e-3f) ? mrt_normal : best_normal;
    return true;
}

bool ViewportCore::pickSurfaceAt(int x_pixels, int y_pixels,
                                 std::uint32_t& object_id_out,
                                 Eigen::Vector3f& world_pos_out,
                                 Eigen::Vector3f& world_normal_out,
                                 float* aabb_radius_out) {
    if (aabb_radius_out) *aabb_radius_out = 0.0f;
    Eigen::Vector3f picked_normal(0, 0, 1);
    // pickObjectAt encodes + reads id + normal, and (now) stages the exact world
    // position into pick_position_staging_buffer_ in the same pass.
    const std::uint32_t id = pickObjectAt(x_pixels, y_pixels, &picked_normal);
    if (id == 0) return false;

    // Read the exact surface position from the pick MRT (sync map — desktop
    // path). This lands the hit on the true face rather than a ray-AABB point.
    if (pick_position_staging_buffer_) {
        struct MapReq { bool done = false; bool ok = false; };
        MapReq req;
        WGPUBufferMapCallbackInfo mcb = {};
        mcb.mode = kAsyncCbMode;
        mcb.callback = [](WGPUMapAsyncStatus s, WGPUStringView, void* u, void*) {
            auto* r = static_cast<MapReq*>(u); r->done = true;
            r->ok = (s == WGPUMapAsyncStatus_Success);
        };
        mcb.userdata1 = &req;
        wgpuBufferMapAsync(pick_position_staging_buffer_, WGPUMapMode_Read, 0, 256, mcb);
        while (!req.done) waitTickInstance(instance_);
        Eigen::Vector3f mrt_pos;
        if (req.ok && decodeMappedPickPosition(mrt_pos)) {
            world_pos_out    = mrt_pos;
            world_normal_out = picked_normal;
            object_id_out    = id;
            return true;
        }
    }

    // Fallback: ray-AABB (e.g. if the position read failed).
    float radius = 0.0f;
    if (!raycastSurfaceForObject(id, x_pixels, y_pixels, picked_normal,
                                 world_pos_out, world_normal_out, radius)) return false;
    if (aabb_radius_out) *aabb_radius_out = radius;
    object_id_out = id;
    return true;
}

#if defined(__EMSCRIPTEN__)
void ViewportCore::finishSurfaceAsync(SurfaceHit hit) {
    auto cb = std::move(surface_async_cb_);
    surface_async_cb_ = nullptr;
    pick_async_in_flight_ = false;
    if (cb) cb(hit);
}

void ViewportCore::pickSurfaceAtAsync(int x_pixels, int y_pixels,
                                      std::function<void(SurfaceHit)> cb) {
    auto miss = [&cb]() { if (cb) cb(SurfaceHit{}); };
    if (!pick_pipeline_ || !device_ || !queue_ || models_gpu_.empty()) { miss(); return; }
    if (configured_w_ <= 0 || configured_h_ <= 0) { miss(); return; }
    if (x_pixels < 0 || y_pixels < 0 ||
        x_pixels >= configured_w_ || y_pixels >= configured_h_) { miss(); return; }
    ensurePickAttachments(configured_w_, configured_h_);
    if (!pick_color_view_ || !pick_depth_view_ ||
        !pick_staging_buffer_ || !pick_normal_staging_buffer_) { miss(); return; }
    // Shares the single-pick staging buffers → shares the in-flight guard.
    if (pick_async_in_flight_) { miss(); return; }
    pick_async_in_flight_ = true;
    surface_async_x_  = x_pixels;
    surface_async_y_  = y_pixels;
    surface_async_id_ = 0;
    surface_async_cb_ = std::move(cb);

    // Render pick + normal MRTs, copy both texels to their staging buffers.
    encodePickReadbackToStaging(x_pixels, y_pixels, /*want_normal=*/true);

    // Map the object-id texel; then (chained) the normal texel; then raycast.
    WGPUBufferMapCallbackInfo idcb = {};
    idcb.mode = kAsyncCbMode;
    idcb.callback = [](WGPUMapAsyncStatus status, WGPUStringView /*msg*/,
                       void* ud1, void* /*ud2*/) {
        auto* self = static_cast<ViewportCore*>(ud1);
        std::uint32_t id = 0;
        if (status == WGPUMapAsyncStatus_Success) {
            const std::uint32_t* mapped = static_cast<const std::uint32_t*>(
                wgpuBufferGetConstMappedRange(self->pick_staging_buffer_, 0, 256));
            id = mapped ? mapped[0] : 0u;
            wgpuBufferUnmap(self->pick_staging_buffer_);
        }
        if (id == 0) { self->finishSurfaceAsync(SurfaceHit{}); return; }
        self->surface_async_id_ = id;

        // Chain: normal texel → then the exact-position texel → then deliver.
        WGPUBufferMapCallbackInfo ncb = {};
        ncb.mode = kAsyncCbMode;
        ncb.callback = [](WGPUMapAsyncStatus s2, WGPUStringView /*msg*/,
                          void* u1, void* /*u2*/) {
            auto* self = static_cast<ViewportCore*>(u1);
            self->surface_async_normal_ = Eigen::Vector3f::Zero();
            if (s2 == WGPUMapAsyncStatus_Success)
                self->decodeMappedPickNormal(self->surface_async_normal_);

            WGPUBufferMapCallbackInfo pcb = {};
            pcb.mode = kAsyncCbMode;
            pcb.callback = [](WGPUMapAsyncStatus s3, WGPUStringView /*msg*/,
                              void* u2, void* /*u3*/) {
                auto* self = static_cast<ViewportCore*>(u2);
                Eigen::Vector3f pos;
                const bool have_pos = (s3 == WGPUMapAsyncStatus_Success)
                                      && self->decodeMappedPickPosition(pos);
                const bool have_n   = self->surface_async_normal_.squaredNorm() > 1e-3f;
                SurfaceHit hit;
                if (have_pos && have_n) {
                    // True surface point + MRT normal — no ray-AABB.
                    hit.found        = true;
                    hit.object_id    = self->surface_async_id_;
                    hit.world_pos    = pos;
                    hit.world_normal = self->surface_async_normal_.normalized();
                } else {
                    // Fallback: ray-AABB (prefers the MRT position if we had it).
                    float radius = 0.0f;
                    Eigen::Vector3f p, n;
                    if (self->raycastSurfaceForObject(self->surface_async_id_,
                                                      self->surface_async_x_, self->surface_async_y_,
                                                      self->surface_async_normal_, p, n, radius)) {
                        hit.found        = true;
                        hit.object_id    = self->surface_async_id_;
                        hit.world_pos    = have_pos ? pos : p;
                        hit.world_normal = n;
                    }
                }
                self->finishSurfaceAsync(hit);
            };
            pcb.userdata1 = self;
            wgpuBufferMapAsync(self->pick_position_staging_buffer_, WGPUMapMode_Read, 0, 256, pcb);
        };
        ncb.userdata1 = self;
        wgpuBufferMapAsync(self->pick_normal_staging_buffer_, WGPUMapMode_Read, 0, 256, ncb);
    };
    idcb.userdata1 = this;
    wgpuBufferMapAsync(pick_staging_buffer_, WGPUMapMode_Read, 0, 256, idcb);
}
#endif

bool ViewportCore::pickMeshLocalAt(int x, int y, MeshLocalPick& out) {
    std::uint32_t obj_id = 0;
    Eigen::Vector3f world_pos, world_normal;
    if (!pickSurfaceAt(x, y, obj_id, world_pos, world_normal)) return false;

    // Use the OUTER session_model_id (the live map key) rather than inst.session_model_id —
    // InstanceInfo::session_model_id is stale across sessions.
    for (const auto& [session_model_id, m] : models_gpu_) {
        auto it = m.object_id_to_instance.find(obj_id);
        if (it == m.object_id_to_instance.end()) continue;
        const InstanceInfo& inst = m.instances[it->second];

        const Eigen::Matrix4f T = Eigen::Map<const Eigen::Matrix4f>(inst.transform);
        Eigen::Matrix4f Ti;
        if (!tryInvert4f(T, Ti)) return false;

        if (inst.mesh_id >= m.meshes.size()) return false;

        // Refine the AABB-face hit by re-projecting and Möller-Trumbore-
        // ing against the picked instance's CPU mesh shadow.
        Eigen::Vector3f refined_world_pos    = world_pos;
        Eigen::Vector3f refined_world_normal = world_normal;
        if (inst.mesh_id < m.mesh_triangles_cache.size()) {
            const auto& tris = m.mesh_triangles_cache[inst.mesh_id];
            if (!tris.indices.empty() && configured_w_ > 0 && configured_h_ > 0) {
                Eigen::Matrix4f view, proj;
                buildViewProj(view, proj);
                Eigen::Matrix4f inv_vp;
                if (tryInvert4f(proj * view, inv_vp)) {
                    const float ndc_x = (2.0f * float(x) / float(configured_w_)) - 1.0f;
                    const float ndc_y = 1.0f - (2.0f * float(y) / float(configured_h_));
                    const Eigen::Vector4f far_clip(ndc_x, ndc_y, 1.0f, 1.0f);
                    const Eigen::Vector4f far_w = inv_vp * far_clip;
                    if (std::abs(far_w.w()) >= 1e-6f) {
                        const Eigen::Vector3f far_world = far_w.head<3>() / far_w.w();
                        const Eigen::Vector3f eye = orbitEye(
                            camera_target_, camera_distance_,
                            camera_yaw_deg_, camera_pitch_deg_);
                        Eigen::Vector3f ray_dir = far_world - eye;
                        if (ray_dir.squaredNorm() > 1e-8f) {
                            ray_dir.normalize();
                            const Eigen::Vector4f ro_l4 = Ti * Eigen::Vector4f(eye.x(),     eye.y(),     eye.z(),     1.0f);
                            const Eigen::Vector4f rd_l4 = Ti * Eigen::Vector4f(ray_dir.x(), ray_dir.y(), ray_dir.z(), 0.0f);
                            const float ro_l[3] = { ro_l4.x(), ro_l4.y(), ro_l4.z() };
                            const float rd_l[3] = { rd_l4.x(), rd_l4.y(), rd_l4.z() };
                            const float ldn = std::sqrt(
                                rd_l[0]*rd_l[0] + rd_l[1]*rd_l[1] + rd_l[2]*rd_l[2]);
                            if (ldn > 0.0f) {
                                float best_t_world = std::numeric_limits<float>::infinity();
                                std::uint32_t best_tri = UINT32_MAX;
                                const std::size_t n_tris = tris.indices.size() / 3;
                                for (std::size_t t = 0; t < n_tris; ++t) {
                                    const std::uint32_t ia = tris.indices[3 * t + 0];
                                    const std::uint32_t ib = tris.indices[3 * t + 1];
                                    const std::uint32_t ic = tris.indices[3 * t + 2];
                                    if (3 * ia + 2 >= tris.positions.size()
                                     || 3 * ib + 2 >= tris.positions.size()
                                     || 3 * ic + 2 >= tris.positions.size()) continue;
                                    const float* va = &tris.positions[3 * ia];
                                    const float* vb = &tris.positions[3 * ib];
                                    const float* vc = &tris.positions[3 * ic];
                                    float t_local = 0.0f;
                                    if (!rayTriMT(ro_l, rd_l, va, vb, vc, t_local)) continue;
                                    const float t_world = t_local / ldn;
                                    if (t_world < best_t_world) {
                                        best_t_world = t_world;
                                        best_tri     = std::uint32_t(t);
                                    }
                                }
                                if (best_tri != UINT32_MAX) {
                                    refined_world_pos = eye + ray_dir * best_t_world;
                                    const std::uint32_t ia = tris.indices[3 * best_tri + 0];
                                    const std::uint32_t ib = tris.indices[3 * best_tri + 1];
                                    const std::uint32_t ic = tris.indices[3 * best_tri + 2];
                                    const float* va = &tris.positions[3 * ia];
                                    const float* vb = &tris.positions[3 * ib];
                                    const float* vc = &tris.positions[3 * ic];
                                    const float bax = vb[0]-va[0], bay = vb[1]-va[1], baz = vb[2]-va[2];
                                    const float cax = vc[0]-va[0], cay = vc[1]-va[1], caz = vc[2]-va[2];
                                    float n_local[3] = {
                                        bay*caz - baz*cay,
                                        baz*cax - bax*caz,
                                        bax*cay - bay*cax,
                                    };
                                    const float nl = std::sqrt(
                                        n_local[0]*n_local[0]
                                      + n_local[1]*n_local[1]
                                      + n_local[2]*n_local[2]);
                                    if (nl > 0.0f) {
                                        n_local[0] /= nl;
                                        n_local[1] /= nl;
                                        n_local[2] /= nl;
                                    }
                                    const float* M = inst.transform;
                                    Eigen::Vector3f n_world(
                                        M[0]*n_local[0] + M[4]*n_local[1] + M[8] *n_local[2],
                                        M[1]*n_local[0] + M[5]*n_local[1] + M[9] *n_local[2],
                                        M[2]*n_local[0] + M[6]*n_local[1] + M[10]*n_local[2]);
                                    if (n_world.squaredNorm() > 1e-12f) {
                                        n_world.normalize();
                                        refined_world_normal = n_world;
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }

        const Eigen::Vector4f mp = Ti * Eigen::Vector4f(refined_world_pos.x(),
                                            refined_world_pos.y(),
                                            refined_world_pos.z(), 1.0f);

        out.object_id     = obj_id;
        out.session_model_id      = session_model_id;
        out.mesh_id       = inst.mesh_id;
        out.mesh_local[0] = mp.x();
        out.mesh_local[1] = mp.y();
        out.mesh_local[2] = mp.z();
        out.world_pos [0] = refined_world_pos.x();
        out.world_pos [1] = refined_world_pos.y();
        out.world_pos [2] = refined_world_pos.z();
        out.world_normal[0] = refined_world_normal.x();
        out.world_normal[1] = refined_world_normal.y();
        out.world_normal[2] = refined_world_normal.z();
        std::memcpy(out.composed_transform, inst.transform,
                    sizeof(out.composed_transform));
        return true;
    }
    return false;
}

bool ViewportCore::raycast(const float origin[3], const float dir[3],
                           RaycastHit& out) const {
    float inv_d[3] = {
        std::abs(dir[0]) > 1e-20f ? 1.0f / dir[0] : std::numeric_limits<float>::infinity(),
        std::abs(dir[1]) > 1e-20f ? 1.0f / dir[1] : std::numeric_limits<float>::infinity(),
        std::abs(dir[2]) > 1e-20f ? 1.0f / dir[2] : std::numeric_limits<float>::infinity(),
    };

    float best_t = std::numeric_limits<float>::infinity();
    std::uint32_t best_oid = 0;
    float         best_normal[3] = {0, 0, 0};

    for (const auto& [session_model_id, m] : models_gpu_) {
        if (m.hidden) continue;
        for (std::uint32_t inst_idx = 0; inst_idx < std::uint32_t(m.instances.size()); ++inst_idx) {
            const InstanceInfo& inst = m.instances[inst_idx];
            if (!rayAabbSlab(origin, inv_d, inst.world_aabb_min, inst.world_aabb_max)) {
                continue;
            }
            if (inst.mesh_id >= m.mesh_triangles_cache.size()) continue;
            const auto& tris = m.mesh_triangles_cache[inst.mesh_id];
            if (tris.indices.empty()) continue;

            const Eigen::Matrix4f T = Eigen::Map<const Eigen::Matrix4f>(inst.transform);
            Eigen::Matrix4f Ti;
            if (!tryInvert4f(T, Ti)) continue;
            const Eigen::Vector4f ro_local4 = Ti * Eigen::Vector4f(origin[0], origin[1], origin[2], 1.0f);
            const Eigen::Vector4f rd_local4 = Ti * Eigen::Vector4f(dir[0],    dir[1],    dir[2],    0.0f);
            const float ro_local[3] = { ro_local4.x(), ro_local4.y(), ro_local4.z() };
            const float rd_local[3] = { rd_local4.x(), rd_local4.y(), rd_local4.z() };

            const std::size_t n_tris = tris.indices.size() / 3;
            for (std::size_t t = 0; t < n_tris; ++t) {
                const std::uint32_t ia = tris.indices[3 * t + 0];
                const std::uint32_t ib = tris.indices[3 * t + 1];
                const std::uint32_t ic = tris.indices[3 * t + 2];
                if (3 * ia + 2 >= tris.positions.size()
                 || 3 * ib + 2 >= tris.positions.size()
                 || 3 * ic + 2 >= tris.positions.size()) continue;
                const float* va = &tris.positions[3 * ia];
                const float* vb = &tris.positions[3 * ib];
                const float* vc = &tris.positions[3 * ic];
                float t_local = 0.0f;
                if (!rayTriMT(ro_local, rd_local, va, vb, vc, t_local)) continue;
                const float ldn = std::sqrt(rd_local[0]*rd_local[0]
                                          + rd_local[1]*rd_local[1]
                                          + rd_local[2]*rd_local[2]);
                if (ldn <= 0.0f) continue;
                const float t_world = t_local / ldn;
                if (t_world >= best_t) continue;
                best_t   = t_world;
                best_oid = inst.object_id;

                const float bax = vb[0]-va[0], bay = vb[1]-va[1], baz = vb[2]-va[2];
                const float cax = vc[0]-va[0], cay = vc[1]-va[1], caz = vc[2]-va[2];
                float n_local[3] = {
                    bay * caz - baz * cay,
                    baz * cax - bax * caz,
                    bax * cay - bay * cax,
                };
                const float nl = std::sqrt(n_local[0]*n_local[0]
                                         + n_local[1]*n_local[1]
                                         + n_local[2]*n_local[2]);
                if (nl > 0.0f) { n_local[0] /= nl; n_local[1] /= nl; n_local[2] /= nl; }
                const float* M = inst.transform;
                best_normal[0] = M[0]*n_local[0] + M[4]*n_local[1] + M[8]*n_local[2];
                best_normal[1] = M[1]*n_local[0] + M[5]*n_local[1] + M[9]*n_local[2];
                best_normal[2] = M[2]*n_local[0] + M[6]*n_local[1] + M[10]*n_local[2];
                const float wnl = std::sqrt(best_normal[0]*best_normal[0]
                                          + best_normal[1]*best_normal[1]
                                          + best_normal[2]*best_normal[2]);
                if (wnl > 0.0f) {
                    best_normal[0] /= wnl;
                    best_normal[1] /= wnl;
                    best_normal[2] /= wnl;
                }
            }
        }
    }
    if (!std::isfinite(best_t)) return false;
    out.object_id    = best_oid;
    out.distance     = best_t;
    out.world_pos[0] = origin[0] + best_t * dir[0];
    out.world_pos[1] = origin[1] + best_t * dir[1];
    out.world_pos[2] = origin[2] + best_t * dir[2];
    out.world_normal[0] = best_normal[0];
    out.world_normal[1] = best_normal[1];
    out.world_normal[2] = best_normal[2];
    return true;
}

// ===========================================================================
// Surface configuration (#84-u): configureSurface
// ===========================================================================

void ViewportCore::configureSurface(int width_px, int height_px) {
    WGPUSurfaceConfiguration cfg = {};
    cfg.device      = device_;
    cfg.format      = surface_format_;
    // When the surface's own format isn't sRGB (browser canvas), render to an
    // sRGB view of it so the shader's sRGB encode-cancel lands the same way it
    // does on desktop. Advertise the view format so the view is creatable.
    if (surface_view_format_ != surface_format_) {
        cfg.viewFormatCount = 1;
        cfg.viewFormats     = &surface_view_format_;
    }
    // CopySrc lets the screenshot path copy the surface texture back to
    // host memory. Trivial cost on all known backends.
    cfg.usage       = WGPUTextureUsage_RenderAttachment | WGPUTextureUsage_CopySrc;
    cfg.width       = std::uint32_t(width_px);
    cfg.height      = std::uint32_t(height_px);

    // Present mode preference order: Mailbox → Immediate → FifoRelaxed
    // → Fifo. Override with WGPU_PRESENT_MODE=...; otherwise pick the
    // first mode the surface actually advertises (asking for one that
    // isn't listed panics wgpu-native from Rust).
    //
    // Why Immediate sits above FifoRelaxed: Mailbox is the right answer
    // for an interactive viewer (vsync-aligned, no tearing, 1-frame
    // queue) but a meaningful subset of Linux Vulkan stacks (some
    // compositors, some driver/WSI combinations) silently don't expose
    // it. On those stacks Fifo's 2-3 frame queue doubles input-to-
    // photon latency; Immediate can tear but keeps latency at one
    // render-body. FifoRelaxed is the middle option.
    WGPUPresentMode preferred[4] = {
        WGPUPresentMode_Mailbox,
        WGPUPresentMode_Immediate,
        WGPUPresentMode_FifoRelaxed,
        WGPUPresentMode_Fifo,
    };
    const char* pm_name = "mailbox";
    if (const char* s = std::getenv("WGPU_PRESENT_MODE")) {
        WGPUPresentMode override_pm = WGPUPresentMode_Fifo;
        bool known = true;
        if      (std::strcmp(s, "fifo") == 0)         { override_pm = WGPUPresentMode_Fifo;        pm_name = "fifo"; }
        else if (std::strcmp(s, "fifo_relaxed") == 0) { override_pm = WGPUPresentMode_FifoRelaxed; pm_name = "fifo_relaxed"; }
        else if (std::strcmp(s, "mailbox") == 0)      { override_pm = WGPUPresentMode_Mailbox;     pm_name = "mailbox"; }
        else if (std::strcmp(s, "immediate") == 0)    { override_pm = WGPUPresentMode_Immediate;   pm_name = "immediate"; }
        else {
            known = false;
            Log::warn()
                << "[wgpu] unknown WGPU_PRESENT_MODE=" << s
                << " (expected fifo|fifo_relaxed|mailbox|immediate);"
                   " falling back to preference order";
        }
        if (known) {
            preferred[0] = override_pm;
            preferred[1] = WGPUPresentMode_Fifo;  // Fifo is the only guaranteed-supported mode
            preferred[2] = preferred[3] = WGPUPresentMode_Fifo;
        }
    }

    WGPUSurfaceCapabilities caps = {};
    wgpuSurfaceGetCapabilities(surface_, adapter_, &caps);
    auto supports = [&](WGPUPresentMode mode) {
        for (std::size_t i = 0; i < caps.presentModeCount; ++i) {
            if (caps.presentModes[i] == mode) return true;
        }
        return false;
    };

    // Diagnostic: dump the full advertised set on first configure. If
    // Mailbox is missing here the driver doesn't expose it (drives the
    // input-latency story); if Mailbox is listed but we still pick
    // Fifo, the preference order has a bug.
    if (!surface_configured_) {
        std::string advertised;
        for (std::size_t i = 0; i < caps.presentModeCount; ++i) {
            const char* name = "?";
            switch (caps.presentModes[i]) {
                case WGPUPresentMode_Fifo:        name = "fifo";         break;
                case WGPUPresentMode_FifoRelaxed: name = "fifo_relaxed"; break;
                case WGPUPresentMode_Mailbox:     name = "mailbox";      break;
                case WGPUPresentMode_Immediate:   name = "immediate";    break;
                default: break;
            }
            if (i > 0) advertised += ", ";
            advertised += name;
        }
        Log::info() << "[wgpu] surface advertises present modes: " << advertised;
    }
    WGPUPresentMode pm = WGPUPresentMode_Fifo;  // spec-guaranteed fallback
    for (WGPUPresentMode candidate : preferred) {
        if (supports(candidate)) { pm = candidate; break; }
    }
    switch (pm) {
        case WGPUPresentMode_Mailbox:      pm_name = "mailbox";      break;
        case WGPUPresentMode_FifoRelaxed:  pm_name = "fifo_relaxed"; break;
        case WGPUPresentMode_Immediate:    pm_name = "immediate";    break;
        case WGPUPresentMode_Fifo:         pm_name = "fifo";         break;
        default: break;
    }
    // Premultiplied is what lets setBackgroundColor's alpha reach the
    // compositor, so a clear below alpha 1 shows through to whatever the
    // viewport is stacked over. Not every surface advertises it, so pick it
    // only when offered and fall back to Auto — which composites opaquely and
    // discards the alpha channel — otherwise. The two are indistinguishable
    // at alpha 1, the default and the only value a caller that never touches
    // the background will see, so the fallback costs nothing there.
    auto supportsAlphaMode = [&](WGPUCompositeAlphaMode mode) {
        for (std::size_t i = 0; i < caps.alphaModeCount; ++i) {
            if (caps.alphaModes[i] == mode) return true;
        }
        return false;
    };
    const bool premultiplied =
        supportsAlphaMode(WGPUCompositeAlphaMode_Premultiplied);

    wgpuSurfaceCapabilitiesFreeMembers(caps);
    cfg.presentMode = pm;
    if (!surface_configured_) {
        const char* note = "";
        switch (pm) {
            case WGPUPresentMode_Mailbox:
                note = " (vsync-aligned, no queue lag -- default)"; break;
            case WGPUPresentMode_Fifo:
                note = " (strict vsync, may queue 2-3 frames)";    break;
            case WGPUPresentMode_FifoRelaxed:
                note = " (adaptive vsync -- sync if in budget, tear if not)"; break;
            case WGPUPresentMode_Immediate:
                note = " (vsync OFF -- framerate uncapped, may tear)";        break;
            default: break;
        }
        Log::info() << "[wgpu] present mode = " << pm_name << note;
    }
    cfg.alphaMode = premultiplied ? WGPUCompositeAlphaMode_Premultiplied
                                  : WGPUCompositeAlphaMode_Auto;
    surface_premultiplied_ = premultiplied;
    if (!surface_configured_) {
        Log::info() << "[wgpu] composite alpha = "
                    << (premultiplied ? "premultiplied (background alpha honoured)"
                                      : "auto (opaque -- background alpha ignored)");
    }

    wgpuSurfaceConfigure(surface_, &cfg);
    configured_w_       = width_px;
    configured_h_       = height_px;
    surface_configured_ = true;
    ensureDepthTexture(width_px, height_px);
    ensureMsaaColorTexture(width_px, height_px);
    ensureHizTextures(width_px, height_px);
    ensureSelectionOutlineTextures(width_px, height_px);
    // depth_view_ was just replaced; force the HiZ + edge bind groups
    // to rebuild against the new view on next encode.
    if (hiz_bind_group_) {
        wgpuBindGroupRelease(hiz_bind_group_);
        hiz_bind_group_ = nullptr;
    }
    if (edge_bind_group_) {
        wgpuBindGroupRelease(edge_bind_group_);
        edge_bind_group_ = nullptr;
    }
}

// ===========================================================================
// Small cross-chunk + capture helpers (#84-v)
// ===========================================================================

void ViewportCore::buildModelBindGroup(ModelGpuData& m) {
    if (!m.mesh_storage || !m.instance_storage) {
        // Empty model — no chunks, no bind groups; the draw loop will skip.
        return;
    }
    for (std::size_t ci = 0; ci < m.chunks.size(); ++ci) {
        buildChunkBindGroup(m, ci);
    }
}

void ViewportCore::captureNextFrameToPng(const std::string& path,
                                         bool quit_after) {
    pending_screenshot_path_ = path;
    pending_screenshot_quit_ = quit_after;
    host_->requestFrame();
}

// ===========================================================================
// Screenshot capture encode + finalize (#84-w)
// ===========================================================================

WGPUBuffer ViewportCore::encodeScreenshotCapture(
        WGPUCommandEncoder enc, WGPUTexture surface_texture,
        std::uint32_t& padded_bpr_out) {
    constexpr std::uint64_t kWgpuBytesPerRowAlign = 256;
    const std::uint32_t row_bytes_unpadded = std::uint32_t(configured_w_) * 4u;
    const std::uint32_t padded_bpr = std::uint32_t(
        (row_bytes_unpadded + kWgpuBytesPerRowAlign - 1)
        / kWgpuBytesPerRowAlign * kWgpuBytesPerRowAlign);
    const std::uint64_t total_bytes =
        std::uint64_t(padded_bpr) * std::uint64_t(configured_h_);

    WGPUBufferDescriptor bdesc = {};
    bdesc.size  = total_bytes;
    bdesc.usage = WGPUBufferUsage_CopyDst | WGPUBufferUsage_MapRead;
    bdesc.label = svFromCStr("ifcviewer-wgpu.capture");
    WGPUBuffer capture_buffer = wgpuDeviceCreateBuffer(device_, &bdesc);

    WGPUTexelCopyTextureInfo src = {};
    src.texture = surface_texture;
    src.aspect  = WGPUTextureAspect_All;

    WGPUTexelCopyBufferInfo dst = {};
    dst.buffer              = capture_buffer;
    dst.layout.bytesPerRow  = padded_bpr;
    dst.layout.rowsPerImage = std::uint32_t(configured_h_);

    WGPUExtent3D extent = {};
    extent.width  = std::uint32_t(configured_w_);
    extent.height = std::uint32_t(configured_h_);
    extent.depthOrArrayLayers = 1;

    wgpuCommandEncoderCopyTextureToBuffer(enc, &src, &dst, &extent);

    padded_bpr_out = padded_bpr;
    return capture_buffer;
}

void ViewportCore::finalizeScreenshotCapture(WGPUBuffer capture_buffer,
                                             std::uint32_t padded_bpr) {
    if (!capture_buffer) {
        pending_screenshot_path_.clear();
        pending_screenshot_quit_ = false;
        return;
    }

    struct MapReq { bool done = false; bool ok = false; };
    MapReq req;
    WGPUBufferMapCallbackInfo mcb = {};
    mcb.mode = kAsyncCbMode;
    mcb.callback = [](WGPUMapAsyncStatus status, WGPUStringView /*message*/,
                      void* ud1, void* /*ud2*/) {
        auto* r = static_cast<MapReq*>(ud1);
        r->done = true;
        r->ok   = (status == WGPUMapAsyncStatus_Success);
        if (!r->ok) Log::warn() << "wgpu MapAsync failed for screenshot";
    };
    mcb.userdata1 = &req;

    const std::uint64_t total_bytes =
        std::uint64_t(padded_bpr) * std::uint64_t(configured_h_);
    wgpuBufferMapAsync(capture_buffer, WGPUMapMode_Read,
                       0, std::size_t(total_bytes), mcb);
    while (!req.done) waitTickInstance(instance_);

    if (req.ok) {
        const std::uint8_t* mapped = static_cast<const std::uint8_t*>(
            wgpuBufferGetConstMappedRange(capture_buffer, 0, std::size_t(total_bytes)));

        // Assemble tightly-packed RGBA8. Surface is BGRA8 on most
        // backends (BGRA8Unorm = format 28). If a future surface is
        // already RGBA, skip the per-pixel swap.
        const bool is_bgra =
            surface_format_ == WGPUTextureFormat_BGRA8Unorm ||
            surface_format_ == WGPUTextureFormat_BGRA8UnormSrgb;
        const std::uint32_t w = std::uint32_t(configured_w_);
        const std::uint32_t h = std::uint32_t(configured_h_);
        std::vector<std::uint8_t> rgba(std::size_t(w) * std::size_t(h) * 4);
        for (std::uint32_t y = 0; y < h; ++y) {
            const std::uint8_t* src_row = mapped + std::size_t(y) * padded_bpr;
            std::uint8_t*       dst_row = rgba.data() + std::size_t(y) * std::size_t(w) * 4;
            if (is_bgra) {
                for (std::uint32_t x = 0; x < w; ++x) {
                    dst_row[x * 4 + 0] = src_row[x * 4 + 2];  // R <- B
                    dst_row[x * 4 + 1] = src_row[x * 4 + 1];  // G
                    dst_row[x * 4 + 2] = src_row[x * 4 + 0];  // B <- R
                    dst_row[x * 4 + 3] = src_row[x * 4 + 3];  // A
                }
            } else {
                std::memcpy(dst_row, src_row, std::size_t(w) * 4);
            }
        }
        wgpuBufferUnmap(capture_buffer);

        host_->saveScreenshotRgba8(pending_screenshot_path_,
                                   rgba.data(), int(w), int(h));
    }
    wgpuBufferRelease(capture_buffer);

    const bool quit_after = pending_screenshot_quit_;
    pending_screenshot_path_.clear();
    pending_screenshot_quit_ = false;
    if (quit_after) host_->quit();
}

// ===========================================================================
// Render loop (#84-x): render()
// ===========================================================================

#include <future>
#include <iomanip>
#include <sstream>

#include "Stopwatch.h"

namespace {

// degrees → radians. Inline-only, used inside render() for the
// focal-length derivation.
constexpr float degreesToRadians(float deg) {
    return deg * kPiF / 180.0f;
}

// Format a float with N decimals into the running Log line. Used to
// match GL's per-frame stats output where fixed-precision matters for
// side-by-side diffs.
std::string fmtF(double v, int prec) {
    std::ostringstream ss;
    ss << std::fixed << std::setprecision(prec) << v;
    return ss.str();
}

// sRGB → linear, used for the background-clear value so the wgpu
// surface (which is sRGB on most backends) renders the same colour as
// the GL viewport's GL_FRAMEBUFFER_SRGB-enabled pass.
inline float srgbToLinear(float c) {
    return (c <= 0.04045f) ? (c * (1.0f / 12.92f))
                           : std::pow((c + 0.055f) * (1.0f / 1.055f), 2.4f);
}

} // namespace

void ViewportCore::render() {
    if (!device_ || !queue_ || !surface_) return;
    // Device lost (e.g. GPU memory reclaimed by another client). Stop here so
    // we don't busy-loop reconfiguring a dead surface — that retry storm is
    // what otherwise freezes the tab. The page logs guidance to reload.
    if (device_lost_) return;

    Stopwatch frame_timer;
    frame_timer.start();

    // Drain any HiZ async readbacks completed since last frame.
    if (hiz_enabled_) drainHizReadbacks();

    uploadSelectionFlagsIfDirty();

    WGPUSurfaceTexture surf_tex = {};
    wgpuSurfaceGetCurrentTexture(surface_, &surf_tex);

    switch (surf_tex.status) {
        case WGPUSurfaceGetCurrentTextureStatus_SuccessOptimal:
        case WGPUSurfaceGetCurrentTextureStatus_SuccessSuboptimal:
            break;
        case WGPUSurfaceGetCurrentTextureStatus_Timeout:
        case WGPUSurfaceGetCurrentTextureStatus_Outdated:
        case WGPUSurfaceGetCurrentTextureStatus_Lost: {
            int w = 0, h = 0;
            host_->framebufferSize(w, h);
            if (w > 0 && h > 0) configureSurface(w, h);
            host_->requestFrame();
            return;
        }
        default:
            Log::warn() << "GetCurrentTexture status " << int(surf_tex.status);
            return;
    }

    // Render through an sRGB view of the surface texture. On desktop the
    // surface is already sRGB so the view format matches the texture (a plain
    // default view); on web the surface is plain Unorm and this view is its
    // sRGB sibling (advertised via cfg.viewFormats) so the shader's sRGB
    // encode-cancel lands correctly. The screenshot path still reads the base
    // texture, so its BGRA byte-order check stays on surface_format_.
    WGPUTextureViewDescriptor view_desc = {};
    view_desc.format          = surface_view_format_;
    view_desc.dimension       = WGPUTextureViewDimension_2D;
    view_desc.mipLevelCount   = 1;
    view_desc.arrayLayerCount = 1;
    view_desc.aspect          = WGPUTextureAspect_All;
    WGPUTextureView view = wgpuTextureCreateView(surf_tex.texture, &view_desc);

    updateFrameUniforms();

    // ---- Per-frame cull --------------------------------------------------
    last_visible_objects_   = 0;
    last_visible_triangles_ = 0;
    last_sub_draws_         = 0;
    hiz_reject_count_       = 0;
    Stopwatch cull_timer;
    cull_timer.start();
    cull_writes_this_frame_ = 0;
    cull_write_bytes_this_frame_ = 0;
    Eigen::Matrix4f vp_this_frame;
    {
        const Eigen::Vector3f target(camera_target_[0], camera_target_[1], camera_target_[2]);
        const Eigen::Vector3f eye = orbitEye(camera_target_, camera_distance_,
                                             camera_yaw_deg_, camera_pitch_deg_);
        Eigen::Matrix4f v, p;
        buildViewProj(v, p);
        const Eigen::Matrix4f vp = p * v;
        vp_this_frame = vp;
        float planes[6][4];
        extractFrustumPlanes(vp.data(), planes);

        // LOD focal: projected_px = world_radius * focal_px / view_z.
        const Eigen::Vector3f fwd_q = (target - eye).normalized();
        const Eigen::Vector3f world_up = (std::abs(camera_pitch_deg_) >= 89.0f)
                                     ? Eigen::Vector3f(0.0f, 1.0f, 0.0f)
                                     : Eigen::Vector3f(0.0f, 0.0f, 1.0f);
        const Eigen::Vector3f right_q  = fwd_q.cross(world_up).normalized();
        const Eigen::Vector3f up_q     = right_q.cross(fwd_q).normalized();
        const float eye_a[3]   = { eye.x(),     eye.y(),     eye.z()    };
        const float fwd_a[3]   = { fwd_q.x(),   fwd_q.y(),   fwd_q.z()  };
        const float right_a[3] = { right_q.x(), right_q.y(), right_q.z() };
        const float up_a[3]    = { up_q.x(),    up_q.y(),    up_q.z()    };
        const float focal_px = (configured_h_ > 0)
            ? (0.5f * float(configured_h_)
                / std::tan(degreesToRadians(camera_fov_y_deg_) * 0.5f))
            : 0.0f;

        // Motion detection.
        const bool camera_moved = has_prev_camera_
            && (camera_target_[0] != prev_camera_target_[0]
             || camera_target_[1] != prev_camera_target_[1]
             || camera_target_[2] != prev_camera_target_[2]
             || camera_distance_  != prev_camera_distance_
             || camera_yaw_deg_   != prev_camera_yaw_deg_
             || camera_pitch_deg_ != prev_camera_pitch_deg_);
        const bool use_motion_threshold =
            camera_moved && motion_min_pixel_radius_ > min_pixel_radius_;
        const float effective_min_px =
            use_motion_threshold ? motion_min_pixel_radius_ : min_pixel_radius_;
        last_cull_was_motion_ = use_motion_threshold;

        // HiZ stale-VP gate. Strict by default; WGPU_HIZ_MOTION=1 trusts
        // the stale pyramid across motion.
        static const bool hiz_trust_stale = []{
            const char* e = std::getenv("WGPU_HIZ_MOTION");
            return e && e[0] == '1';
        }();
        const bool hiz_vp_matches = hiz_valid_
            && (hiz_trust_stale || hiz_vp_ == vp_this_frame);
        const bool hiz_for_this_frame = hiz_enabled_ && hiz_vp_matches;

        // WGPU_HIZ_TRACE per-frame trace budget arm.
        static const bool hiz_trace_on = []{
            const char* e = std::getenv("WGPU_HIZ_TRACE");
            return e && e[0] == '1';
        }();
        if (hiz_trace_on && hiz_for_this_frame) {
            constexpr int kHizTracePerFrame = 12;
            hiz_trace_budget_.store(kHizTracePerFrame, std::memory_order_relaxed);
            Log::info()
                << "[hiz trace] frame: vp_match="
                << (hiz_vp_ == vp_this_frame ? "exact" : "loose")
                << " pyramid_mip0=" << hiz_mip_w_[0] << "x" << hiz_mip_h_[0]
                << " budget=" << kHizTracePerFrame;
        } else if (hiz_trace_on) {
            hiz_trace_budget_.store(0, std::memory_order_relaxed);
        }

        HizOccludedFn hiz_occluded;
        if (hiz_for_this_frame) {
            hiz_occluded = [this](const float mn[3], const float mx[3]) {
                return aabbOccludedByHiz(mn, mx);
            };
        }

        // Force sequential on Emscripten: std::async(std::launch::async)
        // without -pthread throws std::system_error from inside libstdc++,
        // and we link without exceptions so that becomes abort(). Until
        // COOP/COEP + -pthread wires the worker pool in #88, web stays
        // on the serial path.
#if defined(__EMSCRIPTEN__)
        if (false) {
#else
        if (cull_threads_enabled_) {
#endif
            std::vector<std::pair<std::uint32_t, std::future<std::uint32_t>>> futures;
            futures.reserve(models_gpu_.size());
            for (auto& [session_model_id, m] : models_gpu_) {
                if (m.hidden) continue;
                auto& m_ref = m;
                futures.emplace_back(session_model_id, std::async(std::launch::async,
                    [this, &m_ref, &planes, &eye_a, &fwd_a, &right_a, &up_a,
                     focal_px, effective_min_px, &hiz_occluded]() {
                        return cullModelCpuCompute(
                            m_ref, planes, eye_a, fwd_a, right_a, up_a,
                            focal_px,
                            effective_min_px, lod1_pixel_threshold_,
                            hiz_occluded);
                    }));
            }
            for (auto& [session_model_id, fut] : futures) {
                hiz_reject_count_ += fut.get();
            }
        } else {
            for (auto& [session_model_id, m] : models_gpu_) {
                if (m.hidden) continue;
                hiz_reject_count_ += cullModelCpuCompute(
                    m, planes, eye_a, fwd_a, right_a, up_a, focal_px,
                    effective_min_px, lod1_pixel_threshold_,
                    hiz_occluded);
            }
        }

        const double cull_compute_ms = double(cull_timer.nsecsElapsed()) / 1e6;
        Stopwatch upload_timer;
        upload_timer.start();
        for (auto& [session_model_id, m] : models_gpu_) {
            if (m.hidden) continue;
            cullModelCpuUpload(m);
            for (const auto& c : m.chunks) {
                last_visible_objects_   += c.total_visible_draws;
                last_visible_triangles_ += c.total_visible_vertices / 3u;
                if (c.total_visible_draws > 0) last_sub_draws_ += 1;
            }
        }
        last_cull_compute_ms_ = cull_compute_ms;
        last_cull_upload_ms_  = double(upload_timer.nsecsElapsed()) / 1e6;
    }

    const double cull_only_ms = double(cull_timer.nsecsElapsed()) / 1e6;
    last_cull_ms_ = cull_only_ms;

    Stopwatch stream_timer;
    stream_timer.start();
    driveStreamingLoads();
    const double stream_ms = double(stream_timer.nsecsElapsed()) / 1e6;
    last_stream_ms_ = stream_ms;

    // Snapshot camera state for next frame's motion detection.
    prev_camera_target_[0] = camera_target_[0];
    prev_camera_target_[1] = camera_target_[1];
    prev_camera_target_[2] = camera_target_[2];
    prev_camera_distance_  = camera_distance_;
    prev_camera_yaw_deg_   = camera_yaw_deg_;
    prev_camera_pitch_deg_ = camera_pitch_deg_;
    has_prev_camera_       = true;
    if (bench_total_ > 0 && bench_count_ >= bench_warmup_) {
        bench_cull_ms_total_   += cull_only_ms;
        bench_stream_ms_total_ += stream_ms;
    }

    WGPUCommandEncoder enc = wgpuDeviceCreateCommandEncoder(device_, nullptr);

    WGPURenderPassColorAttachment color = {};
    color.view          = msaa_color_view_;
    color.resolveTarget = view;
    color.loadOp        = WGPULoadOp_Clear;
    color.storeOp       = WGPUStoreOp_Store;
    // A premultiplied surface expects colour already scaled by alpha, so the
    // clear fades toward transparent instead of tinting what shows through:
    // leaving it unscaled would have the compositor add the background colour
    // on top of the layer behind. When the surface could only be configured
    // opaque the alpha is discarded anyway, and scaling would darken the
    // colour for nothing — so hold alpha at 1 and write it straight.
    const float bg_a = surface_premultiplied_ ? background_color_[3] : 1.0f;
    color.clearValue    = {
        srgbToLinear(background_color_[0]) * bg_a,
        srgbToLinear(background_color_[1]) * bg_a,
        srgbToLinear(background_color_[2]) * bg_a,
        bg_a,
    };
    color.depthSlice = WGPU_DEPTH_SLICE_UNDEFINED;

    WGPURenderPassDepthStencilAttachment depth = {};
    depth.view              = depth_view_;
    depth.depthLoadOp       = WGPULoadOp_Clear;
    depth.depthStoreOp      = WGPUStoreOp_Store;
    depth.depthClearValue   = 1.0f;
    depth.stencilLoadOp     = WGPULoadOp_Undefined;
    depth.stencilStoreOp    = WGPUStoreOp_Undefined;
    depth.depthReadOnly     = false;
    depth.stencilReadOnly   = true;

    WGPURenderPassDescriptor pass_desc = {};
    pass_desc.colorAttachmentCount = 1;
    pass_desc.colorAttachments     = &color;
    pass_desc.depthStencilAttachment = depth_view_ ? &depth : nullptr;

    WGPURenderPassEncoder pass = wgpuCommandEncoderBeginRenderPass(enc, &pass_desc);

    // Two-pass main render: opaque first, then transparent.
    if (main_pipeline_ && main_pipeline_no_cull_ && main_pipeline_transparent_
        && frame_bind_group_ && !models_gpu_.empty()) {
        wgpuRenderPassEncoderSetPipeline(pass,
            backface_culling_ ? main_pipeline_ : main_pipeline_no_cull_);
        wgpuRenderPassEncoderSetBindGroup(pass, 0, frame_bind_group_, 0, nullptr);

        for (const auto& [session_model_id, m] : models_gpu_) {
            if (m.hidden) continue;
            for (const auto& c : m.chunks) {
                if (!c.bind_group || c.opaque_visible_vertices == 0) continue;
                wgpuRenderPassEncoderSetBindGroup(pass, 1, c.bind_group, 0, nullptr);
                wgpuRenderPassEncoderDraw(pass,
                                          c.opaque_visible_vertices, 1, 0, 0);
            }
        }

        wgpuRenderPassEncoderSetPipeline(pass, main_pipeline_transparent_);
        for (const auto& [session_model_id, m] : models_gpu_) {
            if (m.hidden) continue;
            for (const auto& c : m.chunks) {
                if (!c.bind_group) continue;
                const std::uint32_t transparent_verts =
                    c.total_visible_vertices - c.opaque_visible_vertices;
                if (transparent_verts == 0) continue;
                wgpuRenderPassEncoderSetBindGroup(pass, 1, c.bind_group, 0, nullptr);
                wgpuRenderPassEncoderDraw(pass,
                                          transparent_verts, 1,
                                          c.opaque_visible_vertices, 0);
            }
        }
    }

    // Build the per-frame OverlayFrame snapshot.
    int viewport_w_px = 0, viewport_h_px = 0;
    host_->framebufferSize(viewport_w_px, viewport_h_px);
    const int dpr_int = std::max(1, int(host_->dpr()));

    OverlayFrame overlay_frame;
    overlay_frame.view_proj          = vp_this_frame;
    overlay_frame.camera_target      = Eigen::Vector3f(camera_target_[0],
                                                       camera_target_[1],
                                                       camera_target_[2]);
    overlay_frame.camera_distance    = camera_distance_;
    overlay_frame.camera_yaw_deg     = camera_yaw_deg_;
    overlay_frame.camera_pitch_deg   = camera_pitch_deg_;
    overlay_frame.camera_fov_y_deg   = camera_fov_y_deg_;
    overlay_frame.viewport_w_px      = viewport_w_px;
    overlay_frame.viewport_h_px      = viewport_h_px;
    overlay_frame.device_pixel_ratio = dpr_int;

    // Section-plane gizmo — shared renderer, drawn for desktop + web from here.
    // (The desktop's OverlayRenderer no longer draws it, to avoid doubling.)
    section_gizmo_.encode(pass, vp_this_frame, section_planes_,
                          viewport_w_px, viewport_h_px, dpr_int, section_selected_index_);

    // Orbit pivot indicator — same shared-renderer story. Drawn while the host
    // has it gated on (drag) or an afterglow is still running; in the latter
    // case keep frames coming so the one that clears it actually lands.
    const bool pivot_visible = pivotIndicatorVisible();
    axis_indicator_.encodePivot(pass, overlay_frame, pivot_visible);
    if (pivot_visible && pivot_indicator_timer_.isValid()) host_->requestFrame();

    // Remaining in-pass overlays (highlight triangles, overlay lines/points).
    // QtViewportHost forwards to overlays_.X(); the web host no-ops.
    host_->encodeOverlaysInMainPass(pass, overlay_frame);

    wgpuRenderPassEncoderEnd(pass);
    wgpuRenderPassEncoderRelease(pass);

    // Selection coverage, while the main pass's depth is still current. The
    // halo itself composites AFTER the edge pass, so the edge multiply does
    // not darken it.
    encodeSelectionMaskPass(enc);

    // Edge silhouette + HiZ resolve, before the surface-targeted overlays.
    if (edges_enabled_) encodeEdgePass(enc, view);

    encodeSelectionOutlinePass(enc, view, dpr_int);

    int hiz_submitted_slot = -1;
    if (hiz_enabled_) hiz_submitted_slot = encodeHizResolve(enc);

    // Corner axis gizmo on the resolved surface — shared renderer, ahead of the
    // host's own post-main overlays so marquee / labels still stack on top.
    axis_indicator_.encodeCornerAxis(enc, view, overlay_frame);

    // Remaining post-main overlays (marquee, labels) on the resolved surface.
    // QtViewportHost forwards to overlays_.X(); the web host no-ops.
    host_->encodeOverlaysPostMain(enc, view, overlay_frame);

    // Optional capture: encode copy on the same command buffer.
    WGPUBuffer    capture_buffer     = nullptr;
    std::uint32_t capture_padded_bpr = 0;
    const bool    want_capture       = !pending_screenshot_path_.empty();
    if (want_capture) {
        capture_buffer = encodeScreenshotCapture(
            enc, surf_tex.texture, capture_padded_bpr);
    }

    WGPUCommandBuffer cmd = wgpuCommandEncoderFinish(enc, nullptr);
    wgpuQueueSubmit(queue_, 1, &cmd);

    wgpuCommandBufferRelease(cmd);
    wgpuCommandEncoderRelease(enc);
    wgpuTextureViewRelease(view);

    if (want_capture) {
        finalizeScreenshotCapture(capture_buffer, capture_padded_bpr);
    }

    // ---- FrameStats emission ---------------------------------------------
    {
        const double this_frame_ms =
            double(frame_timer.nsecsElapsed()) / 1e6;
        frame_time_ms_sum_ -= frame_time_ms_window_[frame_time_ms_head_];
        frame_time_ms_window_[frame_time_ms_head_] = this_frame_ms;
        frame_time_ms_sum_ += this_frame_ms;
        frame_time_ms_head_ = (frame_time_ms_head_ + 1) % FRAME_TIME_WINDOW;
        if (frame_time_ms_count_ < FRAME_TIME_WINDOW) ++frame_time_ms_count_;
        const double avg_ms = frame_time_ms_count_ > 0
            ? frame_time_ms_sum_ / double(frame_time_ms_count_)
            : 0.0;

        std::uint32_t total_obj = 0, total_tri = 0, total_meshes = 0;
        for (const auto& [session_model_id, mm] : models_gpu_) {
            total_obj    += std::uint32_t(mm.instances.size());
            total_tri    += mm.index_count / 3;
            total_meshes += std::uint32_t(mm.meshes.size());
        }

        FrameStats stats;
        stats.fps               = avg_ms > 0.0 ? float(1000.0 / avg_ms) : 0.0f;
        stats.frame_time_ms     = float(avg_ms);
        stats.total_objects     = total_obj;
        stats.visible_objects   = last_visible_objects_;
        stats.total_triangles   = total_tri;
        stats.visible_triangles = last_visible_triangles_;
        stats.unique_meshes     = total_meshes;
        std::uint32_t draw_calls = 0;
        for (const auto& [session_model_id, mm] : models_gpu_) {
            if (mm.hidden) continue;
            for (const auto& c : mm.chunks) {
                if (c.is_resident && c.total_visible_draws > 0) ++draw_calls;
            }
        }
        stats.gl_draw_calls      = draw_calls;
        stats.indirect_sub_draws = last_sub_draws_;
        host_->onFrameStats(stats);
    }

#if !defined(__EMSCRIPTEN__)
    // On Dawn-web there is no explicit surface present — the browser
    // composites the canvas at the end of the current requestAnimationFrame
    // tick, so calling wgpuSurfacePresent aborts the wasm with
    // "wgpuSurfacePresent is unsupported (use requestAnimationFrame via
    // html5.h instead)". WebViewportHost::requestFrame keeps the render
    // loop ticking off RAF.
    wgpuSurfacePresent(surface_);
#endif
    wgpuTextureRelease(surf_tex.texture);

    if (last_cull_was_motion_) host_->requestFrame();

    // HiZ async readback handoff.
    if (hiz_enabled_ && hiz_submitted_slot >= 0) {
        Stopwatch hiz_timer;
        if (bench_total_ > 0) hiz_timer.start();
        startHizMap(hiz_submitted_slot, vp_this_frame);
        if (bench_total_ > 0 && bench_count_ >= bench_warmup_) {
            bench_hiz_readback_ms_total_ += double(hiz_timer.nsecsElapsed()) / 1e6;
        }
    }

    // ---- Interactive heartbeat log --------------------------------------
    if (bench_total_ == 0) {
        ++interactive_frame_count_;
        const float ms = float(frame_timer.nsecsElapsed()) / 1e6f;
        std::uint64_t total_vbo = 0, total_ebo = 0, total_ssbo = 0;
        std::uint32_t total_instances = 0;
        std::size_t chunks_total = 0, chunks_resident = 0;
        std::size_t chunks_frustum_vis = 0, chunks_missing = 0;
        for (const auto& [session_model_id, mo] : models_gpu_) {
            total_vbo  += mo.vram_bytes_vbo;
            total_ebo  += mo.vram_bytes_ebo;
            total_ssbo += mo.vram_bytes_ssbo;
            total_instances += mo.instance_count;
            for (const auto& c : mo.chunks) {
                ++chunks_total;
                if (c.is_resident) ++chunks_resident;
                if (c.frustum_visible_count > 0) {
                    ++chunks_frustum_vis;
                    if (!c.is_resident) ++chunks_missing;
                }
            }
        }
        const double mb = 1.0 / (1024.0 * 1024.0);
        Log::info()
            << "[frame] " << fmtF(ms > 0 ? 1000.0f / ms : 0.0f, 1) << " fps"
            << "  " << fmtF(ms, 2) << " ms"
            << "  obj " << last_visible_objects_ << "/" << total_instances
            << "  tri " << last_visible_triangles_
            << "  sub_draws " << last_sub_draws_
            << "  hiz_rej " << hiz_reject_count_
            << "  cull " << fmtF(last_cull_ms_, 2) << "ms"
            << " (compute " << fmtF(last_cull_compute_ms_, 2)
            << " upload " << fmtF(last_cull_upload_ms_, 2) << ")"
            << "  decode+apply " << fmtF(chunk_apply_ms_total_ / 1000.0, 2) << "s/"
            << chunk_apply_count_ << "ch ("
            << fmtF(double(chunk_apply_raw_bytes_) / (1024.0 * 1024.0), 0) << "MB raw)"
            << "  writes " << cull_writes_this_frame_
            << " (" << fmtF(double(cull_write_bytes_this_frame_) / 1024.0, 0) << "KB)"
            << "  stream " << fmtF(last_stream_ms_, 2) << "ms"
            << "  chunks " << chunks_resident << "/" << chunks_frustum_vis
            << "/" << chunks_total << " (missing " << chunks_missing << ")"
            << "  vram " << fmtF(double(total_vbo + total_ebo + total_ssbo) * mb, 1) << "MB"
            << "  models " << models_gpu_.size()
            << "  lod1 " << lod1_dbg_count_ << "/" << (lod1_dbg_count_ + lod0_dbg_eligible_count_)
            << " (saved " << lod1_dbg_tris_saved_ << " tris, "
            << lod0_dbg_no_lod1_count_ << " no-lod1)";
        lod1_dbg_count_ = 0;
        lod0_dbg_eligible_count_ = 0;
        lod0_dbg_no_lod1_count_ = 0;
        lod1_dbg_tris_saved_ = 0;
    }

    // ---- Benchmark integration + auto-quit -------------------------------
    if (bench_total_ > 0) {
        if (!bench_warm_done_) {
            constexpr int CONVERGE_FRAMES_REQUIRED = 5;
            constexpr int MAX_WARM_FRAMES          = 600;
            const bool worker_idle =
                streaming_thread_.inFlightApprox() == 0;
            if (streaming_loads_this_frame_ > 0 || !worker_idle) {
                bench_warm_streak_ = 0;
            } else {
                ++bench_warm_streak_;
            }
            ++bench_warm_frames_total_;
            const bool converged = bench_warm_streak_ >= CONVERGE_FRAMES_REQUIRED;
            const bool timed_out = bench_warm_frames_total_ >= MAX_WARM_FRAMES;
            if (converged) {
                Log::info() << "[bench warm] converged after "
                            << bench_warm_frames_total_ << " frames";
                bench_warm_done_ = true;
            } else if (timed_out) {
                Log::warn() << "[bench warm] timed out after "
                            << bench_warm_frames_total_
                            << " frames without convergence; starting bench anyway";
                bench_warm_done_ = true;
            } else {
                host_->requestFrame();
                return;
            }
        }

        const float ms = float(frame_timer.nsecsElapsed()) / 1e6f;

        if (bench_count_ >= bench_warmup_) {
            bench_frame_ms_.push_back(ms);
        }

        if ((bench_count_ % 50) == 0) {
            std::uint64_t total_vbo = 0, total_ebo = 0, total_ssbo = 0;
            std::uint32_t total_instances = 0;
            for (const auto& [session_model_id, mo] : models_gpu_) {
                total_vbo += mo.vram_bytes_vbo;
                total_ebo += mo.vram_bytes_ebo;
                total_ssbo += mo.vram_bytes_ssbo;
                total_instances += mo.instance_count;
            }
            const double mb = 1.0 / (1024.0 * 1024.0);
            const double avg_n  = double(std::max(1, bench_count_ - bench_warmup_ + 1));
            const double cull_ms   = bench_cull_ms_total_   / avg_n;
            const double stream_ms2 = bench_stream_ms_total_ / avg_n;
            Log::info()
                << "[frame] " << fmtF(ms > 0 ? 1000.0f / ms : 0.0f, 1) << " fps"
                << "  " << fmtF(ms, 2) << " ms"
                << "  obj " << last_visible_objects_ << "/" << total_instances
                << "  tri " << last_visible_triangles_
                << "  sub_draws " << last_sub_draws_
                << "  hiz_rej " << hiz_reject_count_
                << "  cull[wall " << fmtF(cull_ms, 2)
                << " | compute " << fmtF(last_cull_compute_ms_, 2)
                << " upload " << fmtF(last_cull_upload_ms_, 2) << "]ms"
                << "  stream[" << fmtF(stream_ms2, 2) << "]ms"
                << "  vram " << fmtF(double(total_vbo + total_ebo + total_ssbo) * mb, 1) << "MB"
                << "  models " << models_gpu_.size()
                << "  lod1 " << lod1_dbg_count_ << "/" << (lod1_dbg_count_ + lod0_dbg_eligible_count_)
                << " (saved " << lod1_dbg_tris_saved_ << " tris, "
                << lod0_dbg_no_lod1_count_ << " no-lod1)";
            lod1_dbg_count_ = 0;
            lod0_dbg_eligible_count_ = 0;
            lod0_dbg_no_lod1_count_ = 0;
            lod1_dbg_tris_saved_ = 0;
        }
        camera_yaw_deg_ = bench_yaw_start_
                        + bench_yaw_speed_ * float(bench_count_ + 1);
        ++bench_count_;

        if (bench_count_ >= bench_warmup_ + bench_total_) {
            std::vector<float> times = bench_frame_ms_;
            std::sort(times.begin(), times.end());
            auto pct = [&times](double p) -> float {
                if (times.empty()) return 0.0f;
                const std::size_t idx = std::min(times.size() - 1,
                    std::size_t(p * double(times.size() - 1)));
                return times[idx];
            };
            float sum = 0.0f;
            for (float f : times) sum += f;
            const float avg    = times.empty() ? 0.0f : sum / float(times.size());
            const float median = pct(0.5);
            const float p1     = pct(0.01);
            const float p99    = pct(0.99);

            const float total_sweep = bench_yaw_speed_ * float(bench_total_);
            Log::info() << "\n=== BENCHMARK (" << bench_total_ << " frames, orbit "
                        << total_sweep << "deg at " << bench_yaw_speed_ << "deg/frame) ===";
            Log::info() << "  avg: "    << avg    << " ms (" << (avg    > 0 ? 1000.0f/avg    : 0.0f) << " fps)";
            Log::info() << "  median: " << median << " ms (" << (median > 0 ? 1000.0f/median : 0.0f) << " fps)";
            Log::info() << "  p1: "  << p1  << " ms  p99: " << p99 << " ms";
            Log::info() << "  last frame: obj " << last_visible_objects_
                        << "  tri " << last_visible_triangles_
                        << "  sub_draws " << last_sub_draws_
                        << "  hiz_rej " << hiz_reject_count_;
            const double n = double(std::max(1, bench_total_));
            Log::info() << "  per-frame avg ms: cull=" << bench_cull_ms_total_ / n
                        << "  stream=" << bench_stream_ms_total_ / n
                        << "  hiz_readback=" << bench_hiz_readback_ms_total_ / n
                        << "  hiz=" << (hiz_enabled_ ? "on" : "off");
            Log::info() << "=== END BENCHMARK ===\n";

            bench_total_ = 0;
            host_->quit();
        } else {
            host_->requestFrame();
        }
    }
}

// ===========================================================================
// Section planes (#84-y)
// ===========================================================================

bool ViewportCore::addSectionPlaneAtSurface(const Eigen::Vector3f& point,
                                            const Eigen::Vector3f& normal,
                                            float visual_radius) {
    if (int(section_planes_.size()) >= kMaxSectionPlanes) {
        Log::warn() << "[wgpu section] cap reached (" << kMaxSectionPlanes
                    << " planes)";
        return false;
    }
    Eigen::Vector3f n = normal;
    if (n.squaredNorm() < 1e-8f) return false;
    n.normalize();
    // Auto-flip the normal so the camera-facing half gets cut away.
    const Eigen::Vector3f eye = orbitEye(camera_target_, camera_distance_,
                                         camera_yaw_deg_, camera_pitch_deg_);
    const Eigen::Vector3f eye_dir = eye - point;
    if (n.dot(eye_dir) < 0.0f) n = -n;

    SectionPlane p;
    p.n             = n;
    p.origin        = point;
    p.d             = -n.dot(point);
    p.visual_radius = (visual_radius > 0.0f) ? visual_radius : 1.0f;
    section_planes_.push_back(p);
    // The freshly added plane becomes the selected one.
    section_selected_index_ = int(section_planes_.size()) - 1;
    Log::info()
        << "[wgpu section] added plane #" << section_planes_.size() - 1
        << " origin=(" << point.x() << "," << point.y() << "," << point.z() << ")"
        << " normal=(" << n.x() << "," << n.y() << "," << n.z() << ")";
    host_->requestFrame();
    return true;
}

void ViewportCore::setSelectedSectionPlane(int index) {
    const int clamped = (index >= 0 && index < int(section_planes_.size())) ? index : -1;
    if (clamped == section_selected_index_) return;
    section_selected_index_ = clamped;
    host_->requestFrame();
}

void ViewportCore::removeSectionPlane(int index) {
    if (index < 0 || index >= int(section_planes_.size())) return;
    section_planes_.erase(section_planes_.begin() + index);
    // Keep the selection pointing at the same plane: clear it if it was the one
    // removed, shift it down if it sat after the removed index.
    if (section_selected_index_ == index) {
        section_selected_index_ = -1;
    } else if (section_selected_index_ > index) {
        --section_selected_index_;
    }
    Log::info() << "[wgpu section] removed plane " << index;
    host_->requestFrame();
}

void ViewportCore::clearSectionPlanes() {
    if (section_planes_.empty()) return;
    section_planes_.clear();
    section_selected_index_ = -1;
    Log::info() << "[wgpu section] cleared all planes";
    host_->requestFrame();
}

// Logical (CSS-px) viewport from the host framebuffer + DPR.
void ViewportCore::sectionLogicalViewport(int& w, int& h) const {
    int fb_w = 0, fb_h = 0;
    host_->framebufferSize(fb_w, fb_h);
    const int dpr = std::max(1, int(host_->dpr()));
    w = fb_w / dpr;
    h = fb_h / dpr;
}

int ViewportCore::hitTestSectionGizmo(int x, int y) {
    if (section_planes_.empty()) return -1;
    Eigen::Matrix4f view, proj;
    buildViewProj(view, proj);
    int w = 0, h = 0;
    sectionLogicalViewport(w, h);
    if (w <= 0 || h <= 0) return -1;
    return SectionGizmoRenderer::hitTest(x, y, section_planes_, view, proj, w, h);
}

bool ViewportCore::beginSectionDrag(int gizmo_index, int mouse_x, int mouse_y) {
    if (gizmo_index < 0 || gizmo_index >= int(section_planes_.size())) return false;
    section_drag_active_       = true;
    section_drag_index_        = gizmo_index;
    section_drag_start_origin_ = section_planes_[gizmo_index].origin;
    section_drag_start_mx_     = mouse_x;
    section_drag_start_my_     = mouse_y;
    return true;
}

void ViewportCore::updateSectionDrag(int mouse_x, int mouse_y) {
    if (!section_drag_active_) return;
    if (section_drag_index_ < 0 || section_drag_index_ >= int(section_planes_.size())) return;
    SectionPlane& p = section_planes_[section_drag_index_];

    int w = 0, h = 0;
    sectionLogicalViewport(w, h);
    if (w <= 0 || h <= 0) return;
    Eigen::Matrix4f view, proj;
    buildViewProj(view, proj);
    const Eigen::Matrix4f vp = proj * view;

    // Reproject the PRESS-TIME origin (and origin + n) every frame so the slide
    // stays smooth even if the camera moves mid-drag.
    auto to_screen = [&](const Eigen::Vector3f& world, Eigen::Vector2f& out) -> bool {
        const Eigen::Vector4f clip = vp * Eigen::Vector4f(world.x(), world.y(), world.z(), 1.0f);
        if (clip.w() <= 0.0f) return false;
        const float invw = 1.0f / clip.w();
        out = Eigen::Vector2f((clip.x() * invw * 0.5f + 0.5f) * float(w),
                              (1.0f - (clip.y() * invw * 0.5f + 0.5f)) * float(h));
        return true;
    };
    Eigen::Vector2f s_origin, s_n;
    if (!to_screen(section_drag_start_origin_, s_origin)) return;
    if (!to_screen(section_drag_start_origin_ + p.n, s_n)) return;
    const Eigen::Vector2f axis = s_n - s_origin;
    const float len2 = axis.squaredNorm();
    if (len2 < 1e-3f) return;  // arrow edge-on

    // Project the pixel delta onto the screen-space normal axis; the axis is 1 m
    // in world space, so (delta·axis)/|axis|² is the slide in metres.
    const Eigen::Vector2f delta(float(mouse_x - section_drag_start_mx_),
                                float(mouse_y - section_drag_start_my_));
    const float meters = delta.dot(axis) / len2;
    p.origin = section_drag_start_origin_ + p.n * meters;
    p.d      = -p.n.dot(p.origin);
    host_->requestFrame();
}
