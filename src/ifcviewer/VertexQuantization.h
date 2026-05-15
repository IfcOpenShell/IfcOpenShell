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

// Inline helpers that turn streamer-format vertices (7 floats per vertex:
// pos3 + normal3 + color-as-float) into the 12 B quantized VBO layout used
// by both the viewport's GPU buffers and the .ifcview sidecar.  Shared
// between ViewportWindow::uploadMeshChunk and HeadlessSidecarBuilder so
// the on-disk format stays identical to what the viewer would have
// produced via the GPU readback path.

#ifndef VERTEXQUANTIZATION_H
#define VERTEXQUANTIZATION_H

#include "InstancedGeometry.h"

#include <cmath>
#include <cstdint>
#include <cstring>

// Meyer et al. octahedral normal encode.  Input unit vector -> [-1,1]^2.
inline void octEncodeNormal(const float n[3], float out[2]) {
    float ax = std::fabs(n[0]), ay = std::fabs(n[1]), az = std::fabs(n[2]);
    float denom = ax + ay + az;
    if (denom < 1e-12f) { out[0] = 0.0f; out[1] = 0.0f; return; }
    float px = n[0] / denom;
    float py = n[1] / denom;
    if (n[2] < 0.0f) {
        float sx = px >= 0.0f ? 1.0f : -1.0f;
        float sy = py >= 0.0f ? 1.0f : -1.0f;
        float nx = (1.0f - std::fabs(py)) * sx;
        float ny = (1.0f - std::fabs(px)) * sy;
        px = nx; py = ny;
    }
    out[0] = px;
    out[1] = py;
}

// Quantize a streamer-format vertex (pos3 + normal3 + color-as-float) into
// the 12 B VBO record, given the mesh's tight local AABB.  `extent_recip`
// is 1/(max-min) per axis, or 0 for degenerate axes.
inline void quantizeVertex(const float src[INSTANCED_VERTEX_STRIDE_FLOATS],
                           const float aabb_min[3],
                           const float extent_recip[3],
                           uint8_t dst[INSTANCED_VERTEX_STRIDE_BYTES]) {
    // Position -> u16 normalized.
    uint16_t* p = reinterpret_cast<uint16_t*>(dst + INSTANCED_VERTEX_POS_OFFSET);
    for (int a = 0; a < 3; ++a) {
        float t = (src[a] - aabb_min[a]) * extent_recip[a];
        if (t < 0.0f) t = 0.0f; else if (t > 1.0f) t = 1.0f;
        p[a] = static_cast<uint16_t>(t * 65535.0f + 0.5f);
    }
    // Normal -> oct i8x2.  int8 gives ~1.4° worst-case error — fine for BIM.
    float oct[2];
    octEncodeNormal(src + 3, oct);
    int8_t* n = reinterpret_cast<int8_t*>(dst + INSTANCED_VERTEX_NORMAL_OFFSET);
    for (int a = 0; a < 2; ++a) {
        float v = oct[a];
        if (v < -1.0f) v = -1.0f; else if (v > 1.0f) v = 1.0f;
        n[a] = static_cast<int8_t>(std::lrintf(v * 127.0f));
    }
    // Color passes through — streamer packs 4 bytes into the 7th float slot.
    std::memcpy(dst + INSTANCED_VERTEX_COLOR_OFFSET, src + 6, 4);
}

#endif // VERTEXQUANTIZATION_H
