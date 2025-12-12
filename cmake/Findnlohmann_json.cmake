#
# Input variables:
# - `JSON_INCLUDE_DIR`
# If input variables are not specified, try to find nlohmann_json config.
# Input variables could also be provided as environment variables.
#
# Output targets:
# - `nlohmann_json::nlohmann_json`

UNIFY_ENVVARS_AND_CACHE(JSON_INCLUDE_DIR)

if(NOT JSON_INCLUDE_DIR)
    find_package(nlohmann_json CONFIG)
    mark_as_advanced(nlohmann_json)
    if(nlohmann_json_DIR)
        return()
    endif()
endif()

find_path(json_header_path "nlohmann/json.hpp" HINTS "${JSON_INCLUDE_DIR}")
mark_as_advanced(json_header_path)

if(json_header_path)
    message(STATUS "JSON for Modern C++ header file found in '${json_header_path}'.")
    add_library(nlohmann_json::nlohmann_json INTERFACE IMPORTED)
    target_include_directories(nlohmann_json::nlohmann_json INTERFACE ${json_header_path})
    return()
endif()

message(FATAL_ERROR "Unable to find JSON for Modern C++ header file / package, aborting")
