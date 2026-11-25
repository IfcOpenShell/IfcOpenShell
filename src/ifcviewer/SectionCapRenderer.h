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


// This file was generated with the assistance of an AI coding tool.

#ifndef SECTIONCAPRENDERER_H
#define SECTIONCAPRENDERER_H

#include <webgpu/webgpu.h>

#include <Eigen/Dense>

#include <vector>

#include "SectionPlane.h"

// How a section cut's cap is drawn. Sizes are in logical pixels, so the hatch
// holds its apparent scale on screen whatever the zoom or display scaling.
struct SectionCapStyle {
    enum class Hatch { None, Diagonal, Cross };
    Hatch hatch         = Hatch::Diagonal;
    float spacing_px    = 8.0f;
    float line_width_px = 1.0f;
    // sRGB, straight alpha. The hatch lines are blended over the fill.
    float hatch_color[4] = {0.0f, 0.0f, 0.0f, 0.55f};
    // Blended over the cut object's own colour; alpha 0 keeps that colour.
    // The fill is always as opaque as the object, whatever its colour.
    float fill_color[4]  = {0.0f, 0.0f, 0.0f, 0.0f};
    // The bold line along the cut edge, drawn just inside the cap. Width 0
    // draws none. Two cut objects that touch are told apart by colour and
    // opacity alone, so neighbours that share both get no line between them.
    float outline_width_px = 2.0f;
    float outline_color[4] = {0.0f, 0.0f, 0.0f, 1.0f};
};

// Caps section cuts: fills the cross-section where a section plane slices
// through a solid, so a cut model reads as solid instead of hollow.
//
// It works on parity. ViewportCore draws the clipped scene into `accumView()`
// with additive blending, back faces as +(colour * opacity, opacity) and
// front faces as the negative. Everything that survives the clip lies behind
// the point where a pixel's view ray enters the kept region, so the faces of
// a closed solid cancel unless that entry point is inside it. What is left is
// the colour and opacity of the solid being cut. encodeComposite() then
// paints those pixels at the depth of the entry point, as see-through as the
// object is.
//
// Only an object whose bounding box crosses a section plane takes part, so
// nothing behind the cut is capped by mistake. A mesh that is not closed can
// still leave a wrong remainder where a plane does pass through it.
class SectionCapRenderer {
public:
    // Signed and blendable, which the accumulation needs.
    static constexpr WGPUTextureFormat kAccumFormat = WGPUTextureFormat_RGBA16Float;

    SectionCapRenderer() = default;
    ~SectionCapRenderer();
    SectionCapRenderer(const SectionCapRenderer&)            = delete;
    SectionCapRenderer& operator=(const SectionCapRenderer&) = delete;

    // `color_format` and `sample_count` are those of the main pass, which the
    // composite draws into. Returns false (and stays inert) on failure.
    bool init(WGPUDevice device, WGPUQueue queue,
              WGPUTextureFormat color_format, int sample_count);
    void destroy();

    // (Re)allocate the single-sample accumulation target. Idempotent when the
    // size matches.
    void ensureTarget(int w, int h);
    void releaseTarget();

    bool ready() const { return pipeline_ && accum_view_; }
    WGPUTextureView accumView() const { return accum_view_; }

    // Draw the caps into the open main pass, after the scene and before the
    // overlays. Writes depth, so later depth-tested passes see the cap.
    void encodeComposite(WGPURenderPassEncoder pass, const Eigen::Matrix4f& view_proj,
                         const std::vector<SectionPlane>& planes,
                         float device_pixel_ratio, const SectionCapStyle& style);

    // Whether the view ray through (ndc_x, ndc_y) enters the kept region
    // through a section plane, which is where a cap can be. Fills the entry
    // point and that plane's normal. The composite shader makes the same test
    // per pixel. Pure math, no GPU.
    static bool rayEntry(const Eigen::Matrix4f& view_proj,
                         const std::vector<SectionPlane>& planes,
                         float ndc_x, float ndc_y,
                         Eigen::Vector3f& point_out, Eigen::Vector3f& normal_out);

private:
    WGPUDevice          device_         = nullptr;
    WGPUQueue           queue_          = nullptr;
    WGPURenderPipeline  pipeline_       = nullptr;
    WGPUPipelineLayout  layout_         = nullptr;
    WGPUBindGroupLayout bgl_            = nullptr;
    WGPUBindGroup       bind_group_     = nullptr;
    WGPUBuffer          uniform_buffer_ = nullptr;
    WGPUShaderModule    shader_         = nullptr;
    WGPUTexture         accum_texture_  = nullptr;
    WGPUTextureView     accum_view_     = nullptr;
    int                 accum_w_        = 0;
    int                 accum_h_        = 0;
};

#endif  // SECTIONCAPRENDERER_H
