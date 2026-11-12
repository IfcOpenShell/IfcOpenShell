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

#include "WgpuDynamicOffsets.h"

#ifdef __EMSCRIPTEN__
#include <emscripten/em_js.h>
#endif

namespace ifcviewer {

#ifdef __EMSCRIPTEN__

namespace {
EM_JS(void, ifcv_set_bind_group_dynamic_js,
      (WGPURenderPassEncoder pass, uint32_t group_index, WGPUBindGroup group,
       uint32_t offsets_ptr, uint32_t count), {
    // HEAPU32.slice() copies into a freshly allocated buffer of exactly
    // `count` elements; .subarray() would alias the whole heap again and
    // reintroduce the bug this function exists to avoid.
    var start = offsets_ptr >>> 2;
    var small = HEAPU32.slice(start, start + count);
    WebGPU.getJsObject(pass).setBindGroup(
        group_index, WebGPU.getJsObject(group), small, 0, count);
});
}  // namespace

void setBindGroupDynamic(WGPURenderPassEncoder pass, uint32_t group_index,
                         WGPUBindGroup group, uint32_t count,
                         const uint32_t* offsets) {
    if (count == 0) {
        wgpuRenderPassEncoderSetBindGroup(pass, group_index, group, 0, nullptr);
        return;
    }
    ifcv_set_bind_group_dynamic_js(pass, group_index, group,
                                   uint32_t(reinterpret_cast<uintptr_t>(offsets)), count);
}

#else

void setBindGroupDynamic(WGPURenderPassEncoder pass, uint32_t group_index,
                         WGPUBindGroup group, uint32_t count,
                         const uint32_t* offsets) {
    wgpuRenderPassEncoderSetBindGroup(pass, group_index, group, count, offsets);
}

#endif

}  // namespace ifcviewer
