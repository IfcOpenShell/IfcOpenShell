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

#ifndef SIDECARLAYOUT_H
#define SIDECARLAYOUT_H

#include "SidecarCache.h"

// Reorder a sidecar's geometry for streaming locality.
//
// The streaming loader chunks meshes by 3D Morton (Z-order) over their
// centroids, then greedy-packs them into ~16 MB chunks; a chunk is always a
// CONSECUTIVE run of that sorted order. But a freshly-baked sidecar stores
// vertices / indices / meshes in mesh-id (iterator) order, which has no
// relation to the spatial chunking — so a chunk's meshes are scattered through
// the file, and streaming one chunk over a network either issues hundreds of
// tiny range requests or reads (and discards) everything in between (~3×
// bandwidth amplification was measured on a 113 MB model).
//
// This pass permutes meshes into the loader's Morton order and rebuilds the
// vertex / index / instance sections to match, so that each spatial chunk
// becomes a CONTIGUOUS byte range. The loader then re-runs the same Morton
// sort, gets the identity permutation, and reads each chunk as one contiguous
// range — no amplification, ~1 request per chunk, and chunks appear
// progressively as they arrive.
//
// Pure transform (no Qt / no wgpu): meshes, vertices, indices (LOD0 + LOD1),
// and instances are all rebuilt in the new order with vbo/ebo/lod1 offsets,
// MeshInfo.first_instance, and InstanceCpu.mesh_id remapped consistently.
// Index values are mesh-local, so they move unchanged. Element/georef/string
// data is mesh-independent and untouched. No-op for < 2 meshes.
//
// Also populates `sd.chunks` (the v14 TOC): the loader must build chunks from
// this rather than re-deriving the plan, because the float Morton quantisation
// isn't bit-identical across toolchains (x86 baker vs wasm loader) — a re-derived
// plan disagrees on boundary meshes and the contiguity is lost.
//
// Run at bake (writeSidecar path) or as a one-shot migration over existing
// .ifcview files (read → reorder → write).
void reorderSidecarByMorton(SidecarData& sd);

#endif  // SIDECARLAYOUT_H
