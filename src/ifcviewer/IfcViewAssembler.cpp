// This file was generated with the assistance of an AI coding tool.
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

#include "IfcViewAssembler.h"

#include "LodBuilder.h"
#include "IfcViewLayout.h"
#include "VertexQuantization.h"

#include <cstring>
#include <limits>
#include <utility>

void IfcViewAssembler::onMeshReady(const StreamedMesh& mesh) {
    if (mesh.vertices.empty() || mesh.indices.empty()) return;

    // Streamer format: 7 floats/vertex (pos3 + normal3 + color-as-float).
    const size_t n_verts = mesh.vertices.size() / INSTANCED_VERTEX_STRIDE_FLOATS;

    // Recompute a tight local AABB from the actual vertex positions, same
    // way ViewportWindow::uploadStreamedMesh does so the .ifcview byte layout
    // matches the live-render path.
    float bmin[3] = {  std::numeric_limits<float>::infinity(),
                       std::numeric_limits<float>::infinity(),
                       std::numeric_limits<float>::infinity() };
    float bmax[3] = { -std::numeric_limits<float>::infinity(),
                      -std::numeric_limits<float>::infinity(),
                      -std::numeric_limits<float>::infinity() };
    for (size_t i = 0; i < n_verts; ++i) {
        const float* vertex = mesh.vertices.data() + i * INSTANCED_VERTEX_STRIDE_FLOATS;
        for (int a = 0; a < 3; ++a) {
            if (vertex[a] < bmin[a]) bmin[a] = vertex[a];
            if (vertex[a] > bmax[a]) bmax[a] = vertex[a];
        }
    }
    float extent_recip[3];
    for (int a = 0; a < 3; ++a) {
        float ext = bmax[a] - bmin[a];
        extent_recip[a] = ext > 0.0f ? 1.0f / ext : 0.0f;
    }

    const size_t vb_offset = ifcview_data_.vertices.size();
    ifcview_data_.vertices.resize(vb_offset + n_verts * INSTANCED_VERTEX_STRIDE_BYTES);
    for (size_t i = 0; i < n_verts; ++i) {
        quantizeVertex(mesh.vertices.data() + i * INSTANCED_VERTEX_STRIDE_FLOATS,
                       bmin, extent_recip,
                       ifcview_data_.vertices.data() + vb_offset
                           + i * INSTANCED_VERTEX_STRIDE_BYTES);
    }

    const size_t ib_offset = ifcview_data_.indices.size();
    ifcview_data_.indices.insert(ifcview_data_.indices.end(),
                                 mesh.indices.begin(), mesh.indices.end());

    MeshInfo info;
    info.vbo_byte_offset = static_cast<uint32_t>(vb_offset);
    info.vertex_count    = static_cast<uint32_t>(n_verts);
    info.ebo_byte_offset = static_cast<uint32_t>(ib_offset * sizeof(uint32_t));
    info.index_count     = static_cast<uint32_t>(mesh.indices.size());
    for (int a = 0; a < 3; ++a) {
        info.local_aabb_min[a] = bmin[a];
        info.local_aabb_max[a] = bmax[a];
    }
    info.first_instance = 0;
    info.instance_count = 0;
    info.lod1_ebo_byte_offset = 0;
    info.lod1_index_count     = 0;

    if (ifcview_data_.meshes.size() <= mesh.mesh_id) {
        ifcview_data_.meshes.resize(mesh.mesh_id + 1);
    }
    ifcview_data_.meshes[mesh.mesh_id] = info;
}

void IfcViewAssembler::onInstanceReady(const StreamedInstance& instance_record) {
    InstanceInfo instance;
    instance.mesh_id              = instance_record.mesh_id;
    instance.object_id            = instance_record.object_id;
    instance.color_override_rgba8 = instance_record.color_override_rgba8;
    instance.session_model_id             = instance_record.session_model_id;

    // The streamer's instance transform is the double-precision
    // placement_transformation.  The cached float transform/world_aabb is only
    // an identity-stage baseline; applyCachedModel recomposes from placement
    // against the consumer's stage matrices at load time.
    std::memcpy(instance.placement_transformation, instance_record.transform,
                sizeof(instance.placement_transformation));
    for (int i = 0; i < 16; ++i) {
        instance.transform[i] = static_cast<float>(instance_record.transform[i]);
    }
    std::memcpy(instance.world_aabb_min, instance_record.world_aabb_min, sizeof(instance.world_aabb_min));
    std::memcpy(instance.world_aabb_max, instance_record.world_aabb_max, sizeof(instance.world_aabb_max));

    ifcview_data_.instances.push_back(instance);
}

IfcViewData IfcViewAssembler::finalize(const ModelGeoref& georef,
                                        const std::vector<ElementInfo>& elements) {
    // Per-mesh instance_count, matching ViewportWindow::finalizeModel.
    for (auto& mesh : ifcview_data_.meshes) {
        mesh.first_instance = 0;
        mesh.instance_count = 0;
    }
    for (const auto& inst : ifcview_data_.instances) {
        if (inst.mesh_id < ifcview_data_.meshes.size()) {
            ++ifcview_data_.meshes[inst.mesh_id].instance_count;
        }
    }

    ifcview_data_.has_coordinate_operation = georef.has_coordinate_operation ? 1 : 0;
    Eigen::Map<Eigen::Matrix<double, 4, 4, Eigen::ColMajor>>(
        ifcview_data_.coordinate_operation_meters) = georef.coordinate_operation_meters;
    ifcview_data_.project_length_to_meters = georef.units.project_length_to_meters;
    ifcview_data_.map_unit_to_meters       = georef.units.map_unit_to_meters;

    for (const auto& info : elements) {
        ElementTableRecord packed;
        packed.object_id = info.object_id;
        packed.session_model_id  = info.session_model_id;
        packed.ifc_id    = info.ifc_id;

        packed.guid_offset = static_cast<uint32_t>(ifcview_data_.string_table.size());
        packed.guid_length = static_cast<uint32_t>(info.guid.size());
        ifcview_data_.string_table += info.guid;

        packed.name_offset = static_cast<uint32_t>(ifcview_data_.string_table.size());
        packed.name_length = static_cast<uint32_t>(info.name.size());
        ifcview_data_.string_table += info.name;

        packed.type_offset = static_cast<uint32_t>(ifcview_data_.string_table.size());
        packed.type_length = static_cast<uint32_t>(info.type.size());
        ifcview_data_.string_table += info.type;

        ifcview_data_.elements.push_back(packed);
    }

    buildLods(ifcview_data_);

    // Lay geometry out in streaming-chunk order and bake the chunk TOC (v14).
    // Lives here (not in the callers) so every producer — the live loader and
    // the .ifcview bake paths — gets the contiguous layout, since a .ifcview
    // written without it streams with network read amplification.
    reorderIfcViewByMorton(ifcview_data_);

    return std::exchange(ifcview_data_, IfcViewData{});
}
