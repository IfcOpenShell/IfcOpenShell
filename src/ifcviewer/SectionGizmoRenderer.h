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

#ifndef SECTIONGIZMORENDERER_H
#define SECTIONGIZMORENDERER_H

#include <webgpu/webgpu.h>

#include <Eigen/Dense>

#include <vector>

#include "SectionPlane.h"

// Qt-free renderer for the section-plane gizmo — a red quad outline plus a
// normal arrow, drawn with anti-aliased thick lines. Lifted out of the
// Qt-coupled OverlayRenderer so BOTH the desktop and web builds draw one
// identical gizmo from a single place (ViewportCore::render calls it on both).
//
// The gizmo is plane-local geometry scaled by each plane's visual radius and
// oriented by a stable tangent/bitangent basis derived from the plane normal.
class SectionGizmoRenderer {
public:
    SectionGizmoRenderer() = default;
    ~SectionGizmoRenderer();
    SectionGizmoRenderer(const SectionGizmoRenderer&)            = delete;
    SectionGizmoRenderer& operator=(const SectionGizmoRenderer&) = delete;

    // Create the pipeline, gizmo VBO, and per-plane uniform buffer. `color_format`
    // is the render target's format; `sample_count` the MSAA count. Returns false
    // (and leaves the renderer inert) if pipeline creation fails.
    bool init(WGPUDevice device, WGPUQueue queue,
              WGPUTextureFormat color_format, int sample_count);
    void destroy();
    bool ready() const { return pipeline_ != nullptr; }

    // Draw one gizmo per plane into an already-open render pass (the main pass).
    void encode(WGPURenderPassEncoder pass, const Eigen::Matrix4f& view_proj,
                const std::vector<SectionPlane>& planes,
                int viewport_w_px, int viewport_h_px, int device_pixel_ratio);

    // Screen-space hit test: index of the plane whose gizmo (arrow segment,
    // origin→origin+normal) the (x, y) logical-pixel point lies within
    // `tolerance_px` of, or -1. Pure math — no GPU. Nearest wins.
    static int hitTest(int x, int y, const std::vector<SectionPlane>& planes,
                       const Eigen::Matrix4f& view, const Eigen::Matrix4f& proj,
                       int viewport_w_px, int viewport_h_px,
                       float tolerance_px = 12.0f);

private:
    WGPUDevice          device_         = nullptr;
    WGPUQueue           queue_          = nullptr;
    WGPURenderPipeline  pipeline_       = nullptr;
    WGPUPipelineLayout  layout_         = nullptr;
    WGPUBindGroupLayout bgl_            = nullptr;
    WGPUBindGroup       bind_group_     = nullptr;
    WGPUBuffer          vertex_buffer_  = nullptr;
    WGPUBuffer          uniform_buffer_ = nullptr;
    WGPUShaderModule    shader_         = nullptr;
    int                 vertex_count_   = 0;
};

#endif  // SECTIONGIZMORENDERER_H
