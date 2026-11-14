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

#ifndef GRIDHELPERRENDERER_H
#define GRIDHELPERRENDERER_H

#include "ViewportGridSpec.h"
#include "ViewportFog.h"

#include <webgpu/webgpu.h>

#include <Eigen/Dense>

#include <string>
#include <vector>

// Sparse RGB axis-aligned line grids on configurable planes, shared by desktop + web.
class GridHelperRenderer {
public:
    GridHelperRenderer() = default;
    ~GridHelperRenderer();
    GridHelperRenderer(const GridHelperRenderer&)            = delete;
    GridHelperRenderer& operator=(const GridHelperRenderer&) = delete;

    bool init(WGPUDevice device, WGPUQueue queue,
              WGPUTextureFormat color_format, int sample_count);
    void destroy();
    bool ready() const { return pipeline_ != nullptr; }

    void encode(WGPURenderPassEncoder pass, const Eigen::Matrix4f& view_proj,
                const ViewportFog& fog, const Eigen::Vector3f& eye,
                const Eigen::Vector3f& forward,
                int viewport_w_px, int viewport_h_px, int device_pixel_ratio);

    // Grid specs are in world coordinates. This is the false-origin matrix
    // that takes them into the viewer frame the GPU draws in.
    void setWorldToViewer(const Eigen::Matrix4d& world_to_viewer);

    void upsertGrid(const ViewportGridSpec& spec);
    bool removeGrid(const std::string& id);
    void clearGrids();
    const std::vector<ViewportGridSpec>& grids() const { return grids_; }

    void setMasterVisible(bool visible) { master_visible_ = visible; }
    bool masterVisible() const { return master_visible_; }

    void setVisible(bool visible) { setMasterVisible(visible); }
    bool visible() const { return masterVisible() && hasVisibleGrid(); }

private:
    static constexpr uint32_t kUniformSlotSize = 256;

    bool hasVisibleGrid() const;
    void rebuildVertices();

    WGPUDevice          device_          = nullptr;
    WGPUQueue           queue_           = nullptr;
    WGPURenderPipeline  pipeline_        = nullptr;
    WGPUPipelineLayout  pipeline_layout_ = nullptr;
    WGPUBindGroupLayout bgl_             = nullptr;
    WGPUBindGroup       bind_group_      = nullptr;
    WGPUShaderModule    shader_module_   = nullptr;
    WGPUBuffer          vertex_buffer_   = nullptr;
    WGPUBuffer          uniform_buffer_  = nullptr;
    int                 vertex_count_    = 0;
    bool                master_visible_  = true;
    std::vector<ViewportGridSpec> grids_;
    Eigen::Matrix4d     world_to_viewer_ = Eigen::Matrix4d::Identity();
};

#endif  // GRIDHELPERRENDERER_H
