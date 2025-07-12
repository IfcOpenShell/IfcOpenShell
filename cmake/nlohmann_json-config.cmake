    find_path(json_header_path "nlohmann/json.hpp" HINTS ${JSON_INCLUDE_DIR})
    set(JSON_INCLUDE_DIR ${json_header_path})

    if(json_header_path)
        message(STATUS "JSON for Modern C++ header file found in ${JSON_INCLUDE_DIR}")
    else()
        message(FATAL_ERROR "Unable to find JSON for Modern C++ header file, aborting")
    endif()