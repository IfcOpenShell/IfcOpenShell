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

#include "Measurement.h"

#include "ViewportWindow.h"

#include <cmath>
#include <cstring>
#include <unordered_map>
#include <vector>

namespace {

double meshLocalVolume(const ViewportWindow::MeshTriangles& tris) {
    // Signed tetrahedra from the origin: V = sum( a · (b × c) ) / 6.
    // Absolute value at the end so winding convention doesn't matter.
    double sum = 0.0;
    const size_t n = tris.indices.size();
    for (size_t i = 0; i + 2 < n; i += 3) {
        const uint32_t ia = tris.indices[i + 0];
        const uint32_t ib = tris.indices[i + 1];
        const uint32_t ic = tris.indices[i + 2];
        const float* a = &tris.positions[3 * ia];
        const float* b = &tris.positions[3 * ib];
        const float* c = &tris.positions[3 * ic];
        const double cx = double(b[1]) * c[2] - double(b[2]) * c[1];
        const double cy = double(b[2]) * c[0] - double(b[0]) * c[2];
        const double cz = double(b[0]) * c[1] - double(b[1]) * c[0];
        sum += double(a[0]) * cx + double(a[1]) * cy + double(a[2]) * cz;
    }
    return std::abs(sum) / 6.0;
}

double det3(const float M[16]) {
    // Upper-left 3x3 of a column-major 4x4: M[col * 4 + row].
    const double m00 = M[0],  m10 = M[1],  m20 = M[2];
    const double m01 = M[4],  m11 = M[5],  m21 = M[6];
    const double m02 = M[8],  m12 = M[9],  m22 = M[10];
    return m00 * (m11 * m22 - m12 * m21)
         - m01 * (m10 * m22 - m12 * m20)
         + m02 * (m10 * m21 - m11 * m20);
}

} // namespace

double volumeOfObjects(ViewportWindow& vp,
                       const std::vector<uint32_t>& object_ids) {
    if (object_ids.empty()) return 0.0;

    // Group selected instances by (model_id, mesh_id) so each unique mesh
    // is read back at most once per call.  Each entry stores the |det| of
    // every instance of that mesh in the request.
    std::unordered_map<uint64_t, std::vector<double>> by_mesh;
    by_mesh.reserve(object_ids.size());
    for (uint32_t oid : object_ids) {
        ViewportWindow::InstanceLookup lk;
        if (!vp.findInstance(oid, lk)) continue;
        const uint64_t key = (uint64_t(lk.model_id) << 32) | lk.mesh_id;
        by_mesh[key].push_back(std::abs(det3(lk.placement_transformation)));
    }

    double total = 0.0;
    ViewportWindow::MeshTriangles tris;
    for (const auto& [key, dets] : by_mesh) {
        const uint32_t model_id = uint32_t(key >> 32);
        const uint32_t mesh_id  = uint32_t(key & 0xffffffffu);
        if (!vp.readbackMeshTriangles(model_id, mesh_id, tris)) continue;
        const double v = meshLocalVolume(tris);
        for (double d : dets) total += v * d;
    }
    return total;
}
