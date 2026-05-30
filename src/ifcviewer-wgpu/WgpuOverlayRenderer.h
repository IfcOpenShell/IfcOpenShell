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

#ifndef WGPUOVERLAYRENDERER_H
#define WGPUOVERLAYRENDERER_H

#include <QMatrix4x4>
#include <QPoint>
#include <QVector3D>

#include <webgpu/webgpu.h>

#include <cstdint>
#include <vector>

// Per-frame snapshot of viewport state that every overlay needs. Built once
// at the top of render() and passed by const-ref to each encodeX() call so
// the overlay renderer never reaches back into the viewport.
struct WgpuOverlayFrame {
    QMatrix4x4 view_proj;
    QVector3D  camera_target;
    float      camera_distance     = 5.0f;
    float      camera_yaw_deg      = 0.0f;
    float      camera_pitch_deg    = 0.0f;
    float      camera_fov_y_deg    = 45.0f;
    int        viewport_w_px       = 0;
    int        viewport_h_px       = 0;
    int        device_pixel_ratio  = 1;
};

// One section plane as the visualizer consumes it. The viewport owns the
// authoritative state vector (the section tool mutates it); the overlay
// reads from a non-owning span every frame. Held by value because the
// struct is small and copies happen at most six times per frame.
struct WgpuSectionPlane {
    QVector3D n;             // unit normal (camera-facing after auto-flip)
    float     d;             // -dot(n, origin)
    QVector3D origin;        // surface point at the moment the plane was added
    float     visual_radius; // unused by the visualizer (kept here so the
                             // section tool's state struct round-trips
                             // through this overlay-facing definition).
};

// All viewport overlays in one place: axis indicator (corner + pivot),
// section plane gizmos, and the marquee drag rect. Mirrors GL's
// OverlayRenderer split so WgpuViewportWindow.cpp doesn't have to
// carry ~1.5k lines of pipeline plumbing.
//
// Lifecycle: init() once after the device is up, destroy() before the
// device dies. Pipelines are immutable after init; only per-frame
// uniforms get re-written.
//
// Threading: all calls are main-thread only — they touch the wgpu queue.
class WgpuOverlayRenderer {
public:
    WgpuOverlayRenderer() = default;
    ~WgpuOverlayRenderer();

    WgpuOverlayRenderer(const WgpuOverlayRenderer&)            = delete;
    WgpuOverlayRenderer& operator=(const WgpuOverlayRenderer&) = delete;

    bool init(WGPUInstance instance, WGPUDevice device, WGPUQueue queue,
              WGPUTextureFormat surface_format, int sample_count);
    void destroy();

    // ---- Inside the main MSAA pass, after geometry ----
    // Both share depth with the scene so they're correctly occluded.

    // Orbit pivot indicator. `visible` is the viewport's UI gate (orbit
    // drag / wheel-zoom afterglow). When false this is a cheap no-op.
    void encodePivot(WGPURenderPassEncoder pass,
                     const WgpuOverlayFrame& f,
                     bool visible);

    // Per-plane wireframe gizmo (2 × 2 m quad outline + arrow shaft +
    // arrow head). Drawn at each plane's origin in its local basis;
    // colour comes from Bonsai's decorator_color_error.
    void encodeSectionGizmos(WGPURenderPassEncoder pass,
                             const WgpuOverlayFrame& f,
                             const std::vector<WgpuSectionPlane>& planes);

    // ---- After the edge silhouette pass, on the resolved surface ----

    // Corner axis gizmo (bottom-left, 110×110 px). Independent ortho
    // projection — only the camera direction matters.
    void encodeCornerAxis(WGPUCommandEncoder enc,
                          WGPUTextureView surface_view,
                          const WgpuOverlayFrame& f);

    // Marquee box-select drag rect (translucent fill + thick outline).
    // No-op when `active` is false.
    void encodeMarquee(WGPUCommandEncoder enc,
                       WGPUTextureView surface_view,
                       const WgpuOverlayFrame& f,
                       QPoint start_logical_px,
                       QPoint current_logical_px,
                       bool active);

    // Shared with the viewport's main FrameUniforms: same cap so the
    // viewport's clip-plane array and the gizmo visualiser agree on
    // how many planes can ever be active.
    static constexpr int kMaxSectionPlanes = 6;

private:
    bool buildAxisIndicator();
    bool buildSectionVisualizer();
    bool buildMarquee();

    WGPUInstance        instance_       = nullptr;
    WGPUDevice          device_         = nullptr;
    WGPUQueue           queue_          = nullptr;
    WGPUTextureFormat   surface_format_ = WGPUTextureFormat_Undefined;
    int                 sample_count_   = 1;

    // ---- Axis indicator (shared shape, three pipelines) ----
    // Slot 0 = corner gizmo. Slots 1/2 = pivot visible/x-ray.
    WGPUShaderModule    axis_shader_module_       = nullptr;
    WGPUBindGroupLayout axis_bgl_                 = nullptr;
    WGPUPipelineLayout  axis_pipeline_layout_     = nullptr;
    WGPURenderPipeline  axis_pivot_pipeline_      = nullptr;
    WGPURenderPipeline  axis_pivot_xray_pipeline_ = nullptr;
    WGPURenderPipeline  axis_corner_pipeline_     = nullptr;
    WGPUBuffer          axis_vertex_buffer_       = nullptr;
    WGPUBuffer          axis_uniform_buffer_      = nullptr;
    WGPUBindGroup       axis_bind_group_          = nullptr;
    static constexpr uint32_t kAxisUniformSlotSize = 256;

    // ---- Section plane gizmos (1 pipeline, dynamic offset per plane) ----
    WGPUShaderModule    section_shader_module_    = nullptr;
    WGPUBindGroupLayout section_bgl_              = nullptr;
    WGPUPipelineLayout  section_pipeline_layout_  = nullptr;
    WGPURenderPipeline  section_pipeline_         = nullptr;
    WGPUBuffer          section_vertex_buffer_    = nullptr;
    WGPUBuffer          section_uniform_buffer_   = nullptr;
    WGPUBindGroup       section_bind_group_       = nullptr;
    static constexpr uint32_t kSectionUniformSlotSize = 256;

    // ---- Marquee (fill + outline pipelines, one uniform buffer) ----
    WGPUShaderModule    marquee_shader_module_      = nullptr;
    WGPUBindGroupLayout marquee_bgl_                = nullptr;
    WGPUPipelineLayout  marquee_pipeline_layout_    = nullptr;
    WGPURenderPipeline  marquee_pipeline_           = nullptr;
    WGPURenderPipeline  marquee_fill_pipeline_      = nullptr;
    WGPUBuffer          marquee_vertex_buffer_      = nullptr;
    WGPUBuffer          marquee_fill_vertex_buffer_ = nullptr;
    WGPUBuffer          marquee_uniform_buffer_     = nullptr;
    WGPUBindGroup       marquee_bind_group_         = nullptr;
};

#endif  // WGPUOVERLAYRENDERER_H
