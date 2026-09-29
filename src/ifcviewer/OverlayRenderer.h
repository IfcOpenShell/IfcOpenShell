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

#include <QHash>
#include <QString>

#include <Eigen/Dense>

#include <webgpu/webgpu.h>

#include <cstdint>
#include <vector>

#include "OverlayFrame.h"
#include "SectionPlane.h"

// The Qt-coupled viewport overlays: the marquee drag rect, measure-tool
// lines / points / highlight patches, and the QPainter-rasterised labels
// and HUD. Mirrors GL's OverlayRenderer split so ViewportWindow.cpp
// doesn't have to carry ~1.5k lines of pipeline plumbing.
//
// The Qt-free overlays live in their own shared renderers so the web build
// gets them too: SectionGizmoRenderer and AxisIndicatorRenderer (corner
// axis gizmo + orbit pivot), both driven by ViewportCore::render.
//
// Lifecycle: init() once after the device is up, destroy() before the
// device dies. Pipelines are immutable after init; only per-frame
// uniforms get re-written.
//
// Threading: all calls are main-thread only — they touch the wgpu queue.
class OverlayRenderer {
public:
    OverlayRenderer() = default;
    ~OverlayRenderer();

    OverlayRenderer(const OverlayRenderer&)            = delete;
    OverlayRenderer& operator=(const OverlayRenderer&) = delete;

    bool init(WGPUInstance instance, WGPUDevice device, WGPUQueue queue,
              WGPUTextureFormat surface_format, int sample_count);
    void destroy();

    // ---- Inside the main MSAA pass, after geometry ----
    // These share depth with the scene so they're correctly occluded.

    // Section-plane gizmos moved to the shared SectionGizmoRenderer, and the
    // orbit pivot to AxisIndicatorRenderer (both drawn by ViewportCore for
    // desktop + web).

    // Replace the highlight-triangle list. `world_xyz` is 3 floats per
    // vertex, 3 vertices per triangle, in world space (post-composed-
    // transform). Empty disables the overlay. Color is RGBA in [0, 1] —
    // alpha < 1 gives the translucent patch shading the Area tool uses.
    // Drawn inside the main MSAA pass so depth-test hides patches
    // behind closer geometry; depth-write stays off so later overlays
    // can still draw over the highlight.
    void setHighlightTriangles(const std::vector<float>& world_xyz,
                               float r, float g, float b, float a);
    void encodeHighlightTriangles(WGPURenderPassEncoder pass,
                                  const OverlayFrame& f);

    // One stylistic group of world-space line segments. Mirrors GL
    // OverlayRenderer::LineGroup so callers can target either backend
    // with one struct.
    struct LineGroup {
        std::vector<float> world_xyz;          // 6 floats per segment (a, b)
        float color[4]        = {1, 1, 1, 1};  // inner color
        float stroke_color[4] = {0, 0, 0, 1};  // halo (alpha 0 = no stroke)
        float line_width      = 1.5f;          // inner full-width (px)
        float stroke_extra    = 0.5f;          // halo per side (px)
        float dash_period_px  = 0.0f;          // 0 = solid
        float dash_on_ratio   = 0.6f;          // [0..1], only when period > 0
    };

    // Replace the overlay-line set. Each call CPU-expands every segment
    // into six vertices (two triangles), uploads the concatenated
    // expanded buffer once, and writes one uniform slot per group; the
    // next encodeOverlayLines() draws them in order. Empty `groups`
    // clears the set so subsequent encodes are no-ops.
    void setOverlayLines(const std::vector<LineGroup>& groups);

    // Encode the most-recently set line groups. One draw per group with
    // a dynamic uniform offset; the shader handles stroke + dash from
    // per-group uniforms. Drawn inside the main MSAA pass so the lines
    // are depth-tested against geometry.
    void encodeOverlayLines(WGPURenderPassEncoder pass,
                            const OverlayFrame& f);

    // Replace the overlay-point set. World-space positions are CPU-
    // expanded into screen-space quads at encode time. `pixel_size` is
    // the inner-disc diameter (px); when `stroke_a > 0` each quad picks
    // up a `stroke_extra`-pixel halo per side. Empty `world_xyz` clears
    // the set. Mirrors GL OverlayRenderer::setOverlayPoints.
    void setOverlayPoints(const std::vector<float>& world_xyz,
                          float r, float g, float b, float a,
                          float pixel_size,
                          float stroke_r, float stroke_g,
                          float stroke_b, float stroke_a,
                          float stroke_extra);

    // Encode the most-recently set point list. Single draw covering all
    // points; the shader does the sprite-distance pick + AA. Drawn
    // inside the main MSAA pass so depth-test correctly hides points
    // behind closer geometry.
    void encodeOverlayPoints(WGPURenderPassEncoder pass,
                             const OverlayFrame& f);

    // World-anchored text label. Mirrors GL OverlayRenderer::Label so
    // measure-tool readouts can target either backend.
    struct Label {
        float   world_pos[3];
        QString text;
    };
    void setOverlayLabels(const std::vector<Label>& labels);

    // Top-left HUD text (tool prompts, length / area readouts). Empty
    // string hides it. Each newline starts a new line in the same rect.
    void setHudText(const QString& text);

    // Encode all currently-set labels + the HUD. Per-string textures are
    // rasterised via QPainter into a small QImage on first sight and
    // cached by content; per-frame work is just projection, vertex
    // assembly, and one draw per visible label. Drawn on the resolved
    // surface (no depth test, no MSAA), so labels stack on top of every
    // overlay above.
    void encodeLabels(WGPUCommandEncoder enc,
                      WGPUTextureView surface_view,
                      const OverlayFrame& f);

    // ---- After the edge silhouette pass, on the resolved surface ----
    // (The corner axis gizmo also draws here — from ViewportCore, via
    // AxisIndicatorRenderer.)

    // Marquee box-select drag rect (translucent fill + thick outline).
    // No-op when `active` is false.
    void encodeMarquee(WGPUCommandEncoder enc,
                       WGPUTextureView surface_view,
                       const OverlayFrame& f,
                       Eigen::Vector2i start_logical_px,
                       Eigen::Vector2i current_logical_px,
                       bool active);

    // Shared with the viewport's main FrameUniforms: same cap so the
    // viewport's clip-plane array and the gizmo visualiser agree on
    // how many planes can ever be active.
    static constexpr int kMaxSectionPlanes = 6;

private:
    bool buildMarquee();
    bool buildOverlayLines();
    bool buildOverlayPoints();
    bool buildHighlightTriangles();
    bool buildLabels();

    // Rasterise a single string at `font_pt` with dark-grey padded
    // background + white text, upload as an RGBA8 texture, build the
    // matching bind group. Width/height are the texture's physical-pixel
    // dimensions and are also what encodeLabels uses to size the quad.
    struct LabelTexture {
        WGPUTexture     texture    = nullptr;
        WGPUTextureView view       = nullptr;
        WGPUBindGroup   bind_group = nullptr;
        int             width_px   = 0;
        int             height_px  = 0;
    };
    LabelTexture* getOrCreateLabelTexture(const QString& cache_key,
                                          const QString& text,
                                          int font_pt,
                                          int dpr);
    void releaseLabelTextures();

    WGPUInstance        instance_       = nullptr;
    WGPUDevice          device_         = nullptr;
    WGPUQueue           queue_          = nullptr;
    WGPUTextureFormat   surface_format_ = WGPUTextureFormat_Undefined;
    int                 sample_count_   = 1;

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

    // ---- Overlay lines (per-group dynamic offset, resizable buffers) ----
    // Vertex buffer holds the concatenated expansion of every group's
    // segments (8 floats × 6 verts per segment). Uniform buffer holds
    // one 256-byte slot per group; the bind group binds a single 128-byte
    // window that the encoder rebinds via dynamic offset.
    WGPUShaderModule    overlay_line_shader_module_   = nullptr;
    WGPUBindGroupLayout overlay_line_bgl_             = nullptr;
    WGPUPipelineLayout  overlay_line_pipeline_layout_ = nullptr;
    WGPURenderPipeline  overlay_line_pipeline_        = nullptr;
    WGPUBuffer          overlay_line_vertex_buffer_   = nullptr;
    uint64_t            overlay_line_vertex_capacity_ = 0;
    WGPUBuffer          overlay_line_uniform_buffer_  = nullptr;
    uint32_t            overlay_line_uniform_slots_   = 0;
    WGPUBindGroup       overlay_line_bind_group_      = nullptr;
    static constexpr uint32_t kOverlayLineUniformSlotSize = 256;

    // Per-group draw record. setOverlayLines() populates one per
    // LineGroup; encodeOverlayLines() iterates and issues one draw each.
    struct OverlayLineDraw {
        uint32_t first_vertex = 0;
        uint32_t vertex_count = 0;
    };
    std::vector<OverlayLineDraw> overlay_line_draws_;

    // ---- Overlay points (sprite-style, quad-expanded per point) ----
    // Single draw per encode covering every point in the set. Vertex
    // buffer holds 6 verts × 8 bytes per point (vec3 world + vec2 corner).
    // Uniforms are global to the set (one inner + one stroke color).
    WGPUShaderModule    overlay_point_shader_module_   = nullptr;
    WGPUBindGroupLayout overlay_point_bgl_             = nullptr;
    WGPUPipelineLayout  overlay_point_pipeline_layout_ = nullptr;
    WGPURenderPipeline  overlay_point_pipeline_        = nullptr;
    WGPUBuffer          overlay_point_vertex_buffer_   = nullptr;
    uint64_t            overlay_point_vertex_capacity_ = 0;
    WGPUBuffer          overlay_point_uniform_buffer_  = nullptr;
    WGPUBindGroup       overlay_point_bind_group_      = nullptr;
    uint32_t            overlay_point_vertex_count_    = 0;

    // ---- Highlight triangles (translucent world-space triangle list) ----
    // One pipeline + one uniform buffer (view_proj + RGBA tint). Vertex
    // buffer grows on demand to fit the current set; empty set ⇒ encode
    // is a no-op.
    WGPUShaderModule    highlight_shader_module_   = nullptr;
    WGPUBindGroupLayout highlight_bgl_             = nullptr;
    WGPUPipelineLayout  highlight_pipeline_layout_ = nullptr;
    WGPURenderPipeline  highlight_pipeline_        = nullptr;
    WGPUBuffer          highlight_vertex_buffer_   = nullptr;
    uint64_t            highlight_vertex_capacity_ = 0;
    WGPUBuffer          highlight_uniform_buffer_  = nullptr;
    WGPUBindGroup       highlight_bind_group_      = nullptr;
    uint32_t            highlight_vertex_count_    = 0;
    float               highlight_color_[4]        = {0, 0, 0, 0};

    // ---- Labels + HUD text (textured quads, cached by content) ----
    // One QPainter-rasterised QImage per unique text string, uploaded as
    // an RGBA8 texture and re-used across frames. Per-frame work is
    // projection + vertex assembly + draws; no allocation in the steady
    // state. Bind groups are layout-shared across all label textures so
    // every cache entry holds its own bind_group ready to bind.
    WGPUShaderModule    label_shader_module_    = nullptr;
    WGPUBindGroupLayout label_bgl_              = nullptr;
    WGPUPipelineLayout  label_pipeline_layout_  = nullptr;
    WGPURenderPipeline  label_pipeline_         = nullptr;
    WGPUSampler         label_sampler_          = nullptr;
    WGPUBuffer          label_vertex_buffer_    = nullptr;
    uint64_t            label_vertex_capacity_  = 0;
    QHash<QString, LabelTexture> label_tex_cache_;
    std::vector<Label>  labels_;
    QString             hud_text_;
};

#endif  // WGPUOVERLAYRENDERER_H
