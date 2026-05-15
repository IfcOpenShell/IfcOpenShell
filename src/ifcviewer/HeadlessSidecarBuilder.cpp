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

#include "HeadlessSidecarBuilder.h"

#include "Federation.h"
#include "GeometryStreamer.h"
#include "LodBuilder.h"
#include "SidecarCache.h"
#include "VertexQuantization.h"

#include <QEventLoop>

#include <Eigen/Dense>

#include <cstring>
#include <limits>

HeadlessSidecarBuilder::HeadlessSidecarBuilder(QObject* parent)
    : QObject(parent)
{
}

void HeadlessSidecarBuilder::onMeshReady(const MeshChunk& chunk) {
    if (chunk.vertices.empty() || chunk.indices.empty()) return;

    // Streamer format: 7 floats/vertex (pos3 + normal3 + color-as-float).
    const size_t n_verts = chunk.vertices.size() / INSTANCED_VERTEX_STRIDE_FLOATS;

    // Recompute a tight local AABB from the actual vertex positions, same
    // way ViewportWindow::uploadMeshChunk does so the .ifcview byte layout
    // matches the GPU-readback path.
    float bmin[3] = {  std::numeric_limits<float>::infinity(),
                       std::numeric_limits<float>::infinity(),
                       std::numeric_limits<float>::infinity() };
    float bmax[3] = { -std::numeric_limits<float>::infinity(),
                      -std::numeric_limits<float>::infinity(),
                      -std::numeric_limits<float>::infinity() };
    for (size_t i = 0; i < n_verts; ++i) {
        const float* v = chunk.vertices.data() + i * INSTANCED_VERTEX_STRIDE_FLOATS;
        for (int a = 0; a < 3; ++a) {
            if (v[a] < bmin[a]) bmin[a] = v[a];
            if (v[a] > bmax[a]) bmax[a] = v[a];
        }
    }
    float extent_recip[3];
    for (int a = 0; a < 3; ++a) {
        float ext = bmax[a] - bmin[a];
        extent_recip[a] = ext > 0.0f ? 1.0f / ext : 0.0f;
    }

    const size_t vb_offset = sidecar_data_.vertices.size();
    sidecar_data_.vertices.resize(vb_offset + n_verts * INSTANCED_VERTEX_STRIDE_BYTES);
    for (size_t i = 0; i < n_verts; ++i) {
        quantizeVertex(chunk.vertices.data() + i * INSTANCED_VERTEX_STRIDE_FLOATS,
                       bmin, extent_recip,
                       sidecar_data_.vertices.data() + vb_offset
                           + i * INSTANCED_VERTEX_STRIDE_BYTES);
    }

    const size_t ib_offset = sidecar_data_.indices.size();
    sidecar_data_.indices.insert(sidecar_data_.indices.end(),
                                 chunk.indices.begin(), chunk.indices.end());

    MeshInfo info;
    info.vbo_byte_offset = static_cast<uint32_t>(vb_offset);
    info.vertex_count    = static_cast<uint32_t>(n_verts);
    info.ebo_byte_offset = static_cast<uint32_t>(ib_offset * sizeof(uint32_t));
    info.index_count     = static_cast<uint32_t>(chunk.indices.size());
    for (int a = 0; a < 3; ++a) {
        info.local_aabb_min[a] = bmin[a];
        info.local_aabb_max[a] = bmax[a];
    }
    info.first_instance = 0;
    info.instance_count = 0;
    info.lod1_ebo_byte_offset = 0;
    info.lod1_index_count     = 0;

    if (sidecar_data_.meshes.size() <= chunk.local_mesh_id) {
        sidecar_data_.meshes.resize(chunk.local_mesh_id + 1);
    }
    sidecar_data_.meshes[chunk.local_mesh_id] = info;
}

void HeadlessSidecarBuilder::onInstanceReady(const InstanceChunk& chunk) {
    InstanceCpu inst;
    inst.mesh_id              = chunk.local_mesh_id;
    inst.object_id            = chunk.object_id;
    inst.color_override_rgba8 = chunk.color_override_rgba8;
    inst.model_id             = chunk.model_id;

    // The streamer's chunk.transform is the placement_transformation.  With
    // identity stage matrices (no FederatedFalseOrigin / ModelTransformation
    // / CoordinateOperation applied yet), transform == placement_transformation
    // and chunk.world_aabb_* is already the world AABB.  ViewportWindow's
    // applyCachedModel will recompose against the consumer's stage matrices
    // at load time, so the cached transform/world_aabb is just a sensible
    // identity-stage baseline.
    std::memcpy(inst.placement_transformation, chunk.transform,
                sizeof(inst.placement_transformation));
    std::memcpy(inst.transform, chunk.transform, sizeof(inst.transform));
    std::memcpy(inst.world_aabb_min, chunk.world_aabb_min, sizeof(inst.world_aabb_min));
    std::memcpy(inst.world_aabb_max, chunk.world_aabb_max, sizeof(inst.world_aabb_max));

    sidecar_data_.instances.push_back(inst);
}

bool HeadlessSidecarBuilder::build(const QString& ifc_path,
                                   const QString& anchor_path,
                                   int num_threads) {
    sidecar_data_ = SidecarData{};
    last_error_.clear();

    // Streamer lives on the calling thread; its worker_thread_ is its own
    // internal QThread.  AutoConnection routes meshReady/instanceReady
    // through our local event loop.
    GeometryStreamer streamer;

    QEventLoop loop;
    bool failed = false;

    connect(&streamer, &GeometryStreamer::meshReady,
            this, &HeadlessSidecarBuilder::onMeshReady);
    connect(&streamer, &GeometryStreamer::instanceReady,
            this, &HeadlessSidecarBuilder::onInstanceReady);
    connect(&streamer, &GeometryStreamer::finished,
            &loop, &QEventLoop::quit);
    connect(&streamer, &GeometryStreamer::cancelled,
            &loop, &QEventLoop::quit);
    connect(&streamer, &GeometryStreamer::errorOccurred, this,
            [&](const QString& msg) {
        last_error_ = msg;
        failed = true;
        loop.quit();
    });

    streamer.loadFile(ifc_path.toStdString(),
                      /*start_object_id*/ 1,
                      /*model_id*/ 1,
                      num_threads);

    loop.exec();

    if (failed) return false;

    // Per-mesh instance_count, matching ViewportWindow::finalizeModel.
    for (auto& mesh : sidecar_data_.meshes) {
        mesh.first_instance = 0;
        mesh.instance_count = 0;
    }
    for (const auto& inst : sidecar_data_.instances) {
        if (inst.mesh_id < sidecar_data_.meshes.size()) {
            ++sidecar_data_.meshes[inst.mesh_id].instance_count;
        }
    }

    // CoordinateOperation cache from the IFC the streamer just parsed.
    if (auto* file = streamer.ifcFile()) {
        ModelGeoref georef = computeModelGeoref(file);
        sidecar_data_.has_coordinate_operation = georef.has_coordinate_operation ? 1 : 0;
        Eigen::Map<Eigen::Matrix<double, 4, 4, Eigen::ColMajor>>(
            sidecar_data_.coordinate_operation_meters) = georef.coordinate_operation_meters;
        sidecar_data_.project_length_to_meters = georef.units.project_length_to_meters;
        sidecar_data_.map_unit_to_meters       = georef.units.map_unit_to_meters;
    }

    // Element metadata accumulated by the streamer's worker thread.
    for (const auto& info : streamer.drainElements()) {
        PackedElementInfo packed;
        packed.object_id = info.object_id;
        packed.model_id  = info.model_id;
        packed.ifc_id    = info.ifc_id;
        packed.parent_id = info.parent_id;

        packed.guid_offset = static_cast<uint32_t>(sidecar_data_.string_table.size());
        packed.guid_length = static_cast<uint32_t>(info.guid.size());
        sidecar_data_.string_table += info.guid;

        packed.name_offset = static_cast<uint32_t>(sidecar_data_.string_table.size());
        packed.name_length = static_cast<uint32_t>(info.name.size());
        sidecar_data_.string_table += info.name;

        packed.type_offset = static_cast<uint32_t>(sidecar_data_.string_table.size());
        packed.type_length = static_cast<uint32_t>(info.type.size());
        sidecar_data_.string_table += info.type;

        sidecar_data_.elements.push_back(packed);
    }

    buildLods(sidecar_data_);

    if (!writeSidecar(anchor_path.toStdString(), sidecar_data_)) {
        last_error_ = "writeSidecar failed";
        return false;
    }

    return true;
}
