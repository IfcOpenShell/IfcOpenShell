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

#ifndef IFCVIEWSERIALIZER_H
#define IFCVIEWSERIALIZER_H

#include "SidecarSerializer.h"
#include "StreamedRecords.h"

#include "../ifcgeom/geometry_serializer.h"

#include <cstdint>
#include <string>
#include <unordered_map>
#include <vector>

// .ifcview geometry serializer: bakes the viewer's sidecar cache from a normal
// IfcGeom iteration — one accumulate per triangulation element, then
// writeSidecar() in finalize().  Qt-free on purpose, so it can live in the
// runtime-loadable serializer plugin (src/serializers/geometry_ifcview_plugin.cpp)
// and be driven by IfcConvert or any other registry consumer.
//
// Two deliberate differences from the live streamer bake:
//  - no vertex rebasing: the bake emits mesh-local coords as the iterator made
//    them and leaves the placement untouched (the rebase is the viewer's
//    float-precision optimisation for far-from-origin meshes);
//  - no georeferencing: the CoordinateOperation cache stays identity, so a
//    plugin-baked sidecar loads in project coordinates.
class IfcViewSerializer : public ifcopenshell::geom::write_only_geometry_serializer {
public:
    IfcViewSerializer(const std::string& output_path,
                      const ifcopenshell::geom::settings& settings,
                      ifcopenshell::logger* logger = nullptr);

    bool ready() override;
    bool isTesselated() const override { return true; }
    void writeHeader() override {}
    void write(const ifcopenshell::geom::triangulation_element* o) override;
    void write(const ifcopenshell::geom::native_element* /*o*/) override {}
    void finalize() override;
    void setUnitNameAndMagnitude(const std::string& /*name*/, float /*magnitude*/) override {}
    void setFile(ifcopenshell::file& /*file*/) override {}

private:
    std::string output_path_;
    SidecarSerializer serializer_;

    // Mesh dedup keyed on the triangulation's geom.id(), same as the streamer:
    // repeated geometry becomes one mesh + N instances.  object_ids are
    // model-local here; the viewer reassigns session-global ids at install.
    std::unordered_map<std::string, uint32_t> geom_to_local_mesh_id_;
    std::vector<MeshAabb> mesh_aabbs_;
    std::vector<ElementInfo> elements_;
    uint32_t next_object_id_ = 1;
    uint32_t total_meshes_ = 0;
};

#endif // IFCVIEWSERIALIZER_H
