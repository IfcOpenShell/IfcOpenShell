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

#ifndef AXISINDICATORRENDERER_H
#define AXISINDICATORRENDERER_H

#include <webgpu/webgpu.h>

#include <Eigen/Dense>

#include "OverlayFrame.h"
#include "ViewportFog.h"

// Qt-free renderer for the RGB axis indicator, in its three guises:
//
//   - the corner gizmo: a fixed 110x110 px triad in the viewport's
//     bottom-left corner, drawn on the resolved surface with its own ortho
//     projection so only the camera's direction moves it;
//   - the pivot indicator: the same triad drawn in world space at the orbit
//     target while the user is navigating, depth-tested against the scene
//     with a dim x-ray pass behind it;
//   - the origin axes: Blender's floor axes. X (red) and Y (green) only,
//     through world 0,0,0 along world X and Y, fading into the background
//     with the grid. No Z line — Blender's floor does not draw one;
//   - the survey point: not a triad but an amber survey marker (triangle
//     and centre cross) facing the screen, on the false origin. The false
//     origin is drawn at viewer (0,0,0), so that is where this sits.
//
// Lifted out of the Qt-coupled OverlayRenderer so BOTH the desktop and web
// builds draw one identical indicator from a single place (ViewportCore::render
// calls it on both) — same move SectionGizmoRenderer made.
class AxisIndicatorRenderer {
public:
    AxisIndicatorRenderer() = default;
    ~AxisIndicatorRenderer();
    AxisIndicatorRenderer(const AxisIndicatorRenderer&)            = delete;
    AxisIndicatorRenderer& operator=(const AxisIndicatorRenderer&) = delete;

    // Create the shared triad VBO, the uniform buffer (seven dynamic-offset
    // slots: corner / pivot / pivot-xray / origin / origin-xray / survey /
    // survey-xray), and the pipelines.
    // `color_format` is the render target's format; `sample_count` the MSAA
    // count of the main pass the pivot draws into (the corner gizmo always
    // targets the resolved, single-sampled surface). Returns false — and
    // leaves the renderer inert — if pipeline creation fails.
    bool init(WGPUDevice device, WGPUQueue queue,
              WGPUTextureFormat color_format, int sample_count);
    void destroy();
    bool ready() const { return corner_pipeline_ != nullptr; }

    // Orbit pivot indicator, drawn into the already-open main MSAA pass so it
    // shares depth with the scene. `visible` is the viewport's UI gate (orbit /
    // pan drag, wheel-zoom afterglow); when false this is a cheap no-op.
    void encodePivot(WGPURenderPassEncoder pass, const OverlayFrame& f,
                     bool visible);

    // Survey marker at `origin`: a fixed-size screen-facing triangle with a
    // centre cross, depth-tested with a strong x-ray pass behind geometry.
    // `visible` false is a no-op.
    void encodeSurveyPoint(WGPURenderPassEncoder pass, const OverlayFrame& f,
                           const Eigen::Vector3f& origin, bool visible);

    // Floor axes through `origin`, red along `x_dir` and green along `y_dir`
    // (unit vectors), from -size to +size metres. Depth-tested 1 px lines.
    // `fog` is the same distance fade the grid uses, so the axes dissolve
    // into the background with the floor. `visible` false is a cheap no-op.
    void encodeOrigin(WGPURenderPassEncoder pass, const OverlayFrame& f,
                      const Eigen::Vector3f& origin,
                      const Eigen::Vector3f& x_dir, const Eigen::Vector3f& y_dir,
                      float size_metres,
                      const ViewportFog& fog,
                      const Eigen::Vector3f& eye, const Eigen::Vector3f& forward,
                      bool visible);

    // Corner axis gizmo (bottom-left, 110x110 px). Opens its own load-op pass
    // on the resolved surface, so it must run after the main pass has resolved.
    void encodeCornerAxis(WGPUCommandEncoder enc, WGPUTextureView surface_view,
                          const OverlayFrame& f);

private:
    WGPUDevice          device_          = nullptr;
    WGPUQueue           queue_           = nullptr;
    WGPUShaderModule    shader_          = nullptr;
    WGPUBindGroupLayout bgl_             = nullptr;
    WGPUPipelineLayout  layout_          = nullptr;
    WGPUBindGroup       bind_group_      = nullptr;
    WGPUBuffer          vertex_buffer_   = nullptr;
    WGPUBuffer          uniform_buffer_  = nullptr;
    WGPURenderPipeline  pivot_pipeline_      = nullptr;
    WGPURenderPipeline  pivot_xray_pipeline_ = nullptr;
    WGPURenderPipeline  corner_pipeline_     = nullptr;
    // Origin axes are a line list (Three.js LineBasicMaterial), not the
    // screen-sized triad. Separate shader + VBO so a kilometre-long segment
    // is clipped by the GPU instead of a screen-space quad.
    WGPUShaderModule    origin_line_shader_       = nullptr;
    WGPUBuffer          origin_line_buffer_       = nullptr;
    WGPURenderPipeline  origin_line_pipeline_     = nullptr;
    WGPURenderPipeline  origin_line_xray_pipeline_ = nullptr;
    WGPUShaderModule    survey_shader_        = nullptr;
    WGPUBuffer          survey_buffer_        = nullptr;
    uint32_t            survey_vertex_count_  = 0;
    WGPURenderPipeline  survey_pipeline_      = nullptr;
    WGPURenderPipeline  survey_xray_pipeline_ = nullptr;

    // Shared screen-sized triad (orbit pivot). `scale_distance` sizes the
    // arms to ~30 logical px at that distance from the eye.
    void encodeWorldTriad(WGPURenderPassEncoder pass, const OverlayFrame& f,
                          const Eigen::Vector3f& origin, float scale_distance,
                          bool visible, float arm_css_px,
                          uint32_t slot_visible, uint32_t slot_xray);
};

#endif  // AXISINDICATORRENDERER_H
