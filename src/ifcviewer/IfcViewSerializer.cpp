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

#include "IfcViewSerializer.h"

#include "SidecarCache.h"

#include <utility>

// Sidecar sessions are single-model; object ids are model-LOCAL and get
// globalized by the viewer when the cached model is installed.
static constexpr uint32_t kSessionModelId = 1;

IfcViewSerializer::IfcViewSerializer(const std::string& output_path,
                                     const ifcopenshell::geom::settings& settings,
                                     ifcopenshell::logger* logger)
    : write_only_geometry_serializer(settings, logger)
    , output_path_(output_path)
{
}

bool IfcViewSerializer::ready() {
    // The file is opened (and the directory is expected to exist) by
    // writeSidecar at finalize() time.
    return true;
}

void IfcViewSerializer::write(const ifcopenshell::geom::triangulation_element* o) {
    if (!o) return;

    const auto& geom = o->geometry();
    if (geom.verts().empty() || geom.faces().empty()) return;

    const uint32_t object_id = next_object_id_++;

    ElementInfo info;
    info.object_id = object_id;
    info.session_model_id = kSessionModelId;
    info.ifc_id = o->id();
    info.guid = o->guid();
    info.name = o->name();
    info.type = o->type();
    elements_.push_back(std::move(info));

    const std::string& geom_id = geom.id();
    uint32_t local_mesh_id;
    bool first_sight = false;
    if (geom_id.empty()) {
        local_mesh_id = total_meshes_++;
        first_sight = true;
    } else {
        auto it = geom_to_local_mesh_id_.find(geom_id);
        if (it == geom_to_local_mesh_id_.end()) {
            local_mesh_id = total_meshes_++;
            geom_to_local_mesh_id_.emplace(geom_id, local_mesh_id);
            first_sight = true;
        } else {
            local_mesh_id = it->second;
        }
    }

    if (first_sight) {
        // Zero offset = no vertex rebasing (see the header note).  The
        // placement is left untouched, so local coords + placement stay
        // consistent; only the float-precision headroom differs from the
        // streamer bake.
        const Eigen::Vector3d offset = Eigen::Vector3d::Zero();
        StreamedMesh streamed_mesh = buildStreamedMesh(kSessionModelId, local_mesh_id, o, offset);

        MeshAabb mesh_aabb;
        for (int a = 0; a < 3; ++a) {
            mesh_aabb.lmin[a] = streamed_mesh.local_aabb_min[a];
            mesh_aabb.lmax[a] = streamed_mesh.local_aabb_max[a];
        }
        mesh_aabb.has_offset = false;
        if (mesh_aabbs_.size() <= local_mesh_id) mesh_aabbs_.resize(local_mesh_id + 1);
        mesh_aabbs_[local_mesh_id] = mesh_aabb;

        if (!streamed_mesh.indices.empty()) {
            serializer_.onMeshReady(streamed_mesh);
        }
    }

    StreamedInstance inst = makeStreamedInstance(
        kSessionModelId, local_mesh_id, object_id, *o, mesh_aabbs_[local_mesh_id]);
    serializer_.onInstanceReady(inst);
}

void IfcViewSerializer::finalize() {
    // Georeferencing is intentionally not baked yet (see the header note):
    // the coordinate-operation cache stays identity/no-op so this plugin does
    // not need the viewer's IfcParse-side georef pipeline.
    SidecarData data = serializer_.finalize(ModelGeoref{}, elements_);

    if (!writeSidecar(output_path_, data)) {
        logger().error("SER", 40, "Unable to write sidecar file '" + output_path_ + "'");
        return;
    }
    logger().notice("SER", 41, "Sidecar written to '" + output_path_ + "'");
}
