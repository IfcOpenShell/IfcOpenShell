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

    // Zero offset = no vertex rebasing (see the header note).  The placement
    // is left untouched, so local coords + placement stay consistent; only the
    // float-precision headroom differs from the streamer bake.
    std::optional<StreamedMesh> new_mesh;
    const UniqueMesh unique_mesh = mesh_registry_.resolve(
        kSessionModelId, *o, Eigen::Vector3d::Zero(), new_mesh);
    if (new_mesh) serializer_.onMeshReady(*new_mesh);

    serializer_.onInstanceReady(makeStreamedInstance(
        kSessionModelId, object_id, *o, unique_mesh, mesh_registry_.aabb(unique_mesh.mesh_id)));
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
