################################################################################
#                                                                              #
# Standalone wgpu memory-allocation probe. No Qt, no surface, just wgpu.       #
# Built only when BUILD_BONSAIVIEWER_WGPU is on so it tracks the same          #
# wgpu_native version as the viewer.                                           #
#                                                                              #
################################################################################

message("Running CMakeLists.txt in /src/wgpu-mem-probe")

add_executable(WgpuMemProbe main.cpp)

target_link_libraries(WgpuMemProbe PRIVATE wgpu_native)

if(UNIX AND NOT APPLE AND WGPU_NATIVE_LIB_DIR)
    set_target_properties(WgpuMemProbe PROPERTIES
        BUILD_RPATH "${WGPU_NATIVE_LIB_DIR}"
    )
endif()
