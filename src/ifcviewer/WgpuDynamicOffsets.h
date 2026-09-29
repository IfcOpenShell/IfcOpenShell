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

#ifndef WGPUDYNAMICOFFSETS_H
#define WGPUDYNAMICOFFSETS_H

#include <cstdint>

#include <webgpu/webgpu.h>

namespace ifcviewer {

// setBindGroup with dynamic offsets. Always use this instead of calling
// wgpuRenderPassEncoderSetBindGroup with a nonzero offset count.
//
// Emscripten's generated WebGPU shim implements the dynamic-offset path as
//
//     pass.setBindGroup(index, group, HEAPU32, ptr >>> 2, count);
//
// where HEAPU32 is the persistent view over the *entire* wasm linear memory.
// Browsers validate the byte length of the whole backing buffer handed to
// setBindGroup, not the (start, length) slice actually read, and reject
// anything over 2 GB:
//
//     TypeError: GPURenderPassEncoder.setBindGroup: Argument 3 can't be an
//     ArrayBuffer or an ArrayBufferView larger than 2 GB
//
// So once the heap grows past 2^31 bytes every dynamic-offset draw throws, on
// every frame, for the life of the page -- and this build deliberately allows
// that (ALLOW_MEMORY_GROWTH with MAXIMUM_MEMORY=4 GB, because large
// federations need the headroom). The offsets are only a handful of uint32_t,
// so the web implementation copies them into a small short-lived Uint32Array.
// Native builds forward straight through; wgpu-native reads the pointer
// directly and has no such limit.
//
// Defined out-of-line in WgpuDynamicOffsets.cpp: the web path is an EM_JS
// function, and EM_JS emits real per-translation-unit symbols that collide at
// link time if instantiated in more than one TU.
void setBindGroupDynamic(WGPURenderPassEncoder pass, uint32_t group_index,
                         WGPUBindGroup group, uint32_t count,
                         const uint32_t* offsets);

}  // namespace ifcviewer

#endif
