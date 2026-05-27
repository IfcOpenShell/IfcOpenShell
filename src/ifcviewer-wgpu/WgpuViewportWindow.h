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

#ifndef WGPUVIEWPORTWINDOW_H
#define WGPUVIEWPORTWINDOW_H

#include <QWindow>
#include <QColor>
#include <QPoint>
#include <QString>

#include <webgpu/webgpu.h>

#include <cstdint>
#include <deque>
#include <unordered_map>

#include "SidecarCache.h"
#include "WgpuModelGpuData.h"

// Stage-2 wgpu viewport: opens a native QWindow, brings up a wgpu instance/
// adapter/device, configures a surface against the platform-native window
// handle, and clears to background_color_ on every UpdateRequest. Models
// loaded from `.ifcview` sidecars are uploaded as wgpu buffers (no draw
// path yet — that's stage 3).
//
// Mirrors the lifecycle shape of the GL ViewportWindow so subsequent stages
// can grow this into a full IFC renderer without restructuring the host.
class WgpuViewportWindow : public QWindow {
    Q_OBJECT
public:
    explicit WgpuViewportWindow(QWindow* parent = nullptr);
    ~WgpuViewportWindow();

    void setBackgroundColor(const QColor& color);

    // Queue a sidecar path to be loaded after wgpu init completes. Safe to
    // call before the window is exposed. The path is resolved against the
    // working directory and read via SidecarCache::readSidecar (which
    // normalises stem → .ifcview).
    void queueLoadSidecar(const QString& path);

    // Synchronous load + GPU upload. Requires wgpu init to have completed
    // (i.e. the window has been exposed at least once). Returns the
    // assigned model_id, or 0 on failure.
    uint32_t loadSidecar(const QString& path);

    // Restore a finalised model from a SidecarData struct: allocate wgpu
    // buffers, upload vertex/index/mesh/instance bytes, register in
    // models_gpu_. Replaces any existing state for model_id.
    void applyCachedModel(uint32_t model_id, SidecarData data);

    void removeModel(uint32_t model_id);
    void resetScene();

    size_t modelCount() const { return models_gpu_.size(); }

    // Frame the union of all loaded models' world AABBs. No-op on empty
    // scenes. Called automatically after the first model loads; clients
    // can re-invoke to re-frame.
    void viewAll();

    // Queue a one-shot framebuffer capture: the next rendered frame is
    // copied back to host memory and saved to `path` as PNG. If
    // `quit_after` is true, QCoreApplication::quit() is called once the
    // PNG is written. Use this for headless verification and pixel-diff
    // parity testing against the GL backend.
    void captureNextFrameToPng(const QString& path, bool quit_after = true);

    // Benchmark mode: render N timed frames (after a small warmup), yaw-
    // sweeping the camera at 0.5°/frame, then print a stats block on
    // stderr and QCoreApplication::quit(). Mirrors the GL minimal's
    // --benchmark output format so a script can diff them line for line.
    void setBenchmarkFrames(int frames);

protected:
    void exposeEvent(QExposeEvent* event) override;
    void resizeEvent(QResizeEvent* event) override;
    bool event(QEvent* event) override;
    void mousePressEvent(QMouseEvent* event) override;
    void mouseReleaseEvent(QMouseEvent* event) override;
    void mouseMoveEvent(QMouseEvent* event) override;
    void wheelEvent(QWheelEvent* event) override;

private:
    bool initWgpu();
    bool createSurface();
    void configureSurface(int width_px, int height_px);
    void render();
    void shutdown();

    bool  buildPipelines();
    void  buildModelBindGroup(WgpuModelGpuData& m);
    void  ensureDepthTexture(int w, int h);
    void  releaseDepthTexture();
    void  updateFrameUniforms();
    void  flushPendingSidecarQueue();
    bool  computeSceneAabb(float mn[3], float mx[3]) const;

    // Cull `m`'s instances against the supplied frustum planes (world-space,
    // ax+by+cz+d >= 0 means inside), bucket survivors by mesh_id, and write
    // the flat visible-index list into m.visible_buffer via wgpuQueueWriteBuffer.
    // After return, m.mesh_draws is the per-mesh draw schedule for the frame.
    void  cullModelCpu(WgpuModelGpuData& m, const float planes[6][4]);

    bool wgpu_initialized_ = false;
    bool surface_configured_ = false;
    int  configured_w_ = 0;
    int  configured_h_ = 0;

    WGPUInstance      instance_       = nullptr;
    WGPUAdapter       adapter_        = nullptr;
    WGPUDevice        device_         = nullptr;
    WGPUQueue         queue_          = nullptr;
    WGPUSurface       surface_        = nullptr;
    WGPUTextureFormat surface_format_ = WGPUTextureFormat_Undefined;

    // Render pipeline + bind group layouts (built once after init).
    WGPUShaderModule       main_shader_module_ = nullptr;
    WGPUBindGroupLayout    frame_bgl_          = nullptr;  // group 0
    WGPUBindGroupLayout    model_bgl_          = nullptr;  // group 1
    WGPUPipelineLayout     pipeline_layout_    = nullptr;
    WGPURenderPipeline     main_pipeline_      = nullptr;

    // Per-frame uniform (view-proj + lighting), bound at group 0.
    WGPUBuffer    frame_uniform_buffer_ = nullptr;
    WGPUBindGroup frame_bind_group_     = nullptr;

    // Depth attachment, recreated on surface resize.
    WGPUTexture     depth_texture_ = nullptr;
    WGPUTextureView depth_view_    = nullptr;
    int             depth_w_       = 0;
    int             depth_h_       = 0;

    QColor background_color_ = QColor("#202329");

    // Camera (orbit, right-handed Y-up world → wait, BIM is +Z up).
    // Mirrors the GL viewport's defaults; mouse navigation lands later.
    float camera_target_[3] = { 0.0f, 0.0f, 0.0f };
    float camera_distance_  = 50.0f;
    float camera_yaw_deg_   = 45.0f;
    float camera_pitch_deg_ = 30.0f;
    float camera_fov_y_deg_ = 45.0f;
    float camera_near_      = 0.1f;
    float camera_far_       = 10000.0f;

    // Per-model state, keyed by viewport-assigned model_id.
    std::unordered_map<uint32_t, WgpuModelGpuData> models_gpu_;
    uint32_t next_model_id_ = 1;

    // Sidecar paths queued before init completes.
    std::deque<QString> pending_sidecars_;

    // Set after the first model load triggers a viewAll(); prevents
    // subsequent loads from snapping the camera away from where the
    // user pointed it.
    bool initial_view_applied_ = false;

    // Pending one-shot screenshot, captured at the end of the next render().
    QString pending_screenshot_path_;
    bool    pending_screenshot_quit_ = false;

    // Mouse navigation state. LMB drag orbits, MMB drag pans, wheel zooms.
    // No Blender/Maya preset selection yet — that arrives with the AppSettings
    // port (post-task-12). Selection is unbound (no pick pass), so LMB is
    // safe to dedicate to orbit for now.
    Qt::MouseButton nav_active_button_ = Qt::NoButton;
    QPoint          nav_last_pos_;

    // Benchmark mode. setBenchmarkFrames(N) arms it; render() integrates the
    // yaw, captures per-frame ms after warmup, and prints + quits when the
    // target frame count is hit.
    int   bench_total_    = 0;
    int   bench_count_    = 0;
    int   bench_warmup_   = 5;
    float bench_yaw_start_ = 0.0f;
    float bench_yaw_speed_ = 0.5f;  // degrees per frame
    std::vector<float> bench_frame_ms_;

    // Per-frame stat snapshot from the last cull. Sum of m.mesh_draws across
    // visible models. Exposed via the benchmark summary; will grow into a
    // proper FrameStats signal when stage 11's host integration arrives.
    uint32_t last_visible_objects_   = 0;
    uint32_t last_visible_triangles_ = 0;
    uint32_t last_sub_draws_         = 0;
};

#endif // WGPUVIEWPORTWINDOW_H
