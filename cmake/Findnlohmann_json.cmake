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
    find_package(nlohmann_json ${nlohmann_json_FIND_VERSION} CONFIG)
    mark_as_advanced(nlohmann_json)
    if(nlohmann_json_DIR)
        return()
    endif()
endif()

find_path(json_header_path "nlohmann/json.hpp" HINTS "${JSON_INCLUDE_DIR}")
mark_as_advanced(json_header_path)

if(json_header_path)
    file(STRINGS "${json_header_path}/nlohmann/json.hpp" json_version_major_line REGEX "^#define NLOHMANN_JSON_VERSION_MAJOR")
    file(STRINGS "${json_header_path}/nlohmann/json.hpp" json_version_minor_line REGEX "^#define NLOHMANN_JSON_VERSION_MINOR")
    file(STRINGS "${json_header_path}/nlohmann/json.hpp" json_version_patch_line REGEX "^#define NLOHMANN_JSON_VERSION_PATCH")
    string(REGEX REPLACE "^#define NLOHMANN_JSON_VERSION_MAJOR ([0-9]+)$" "\\1" json_version_major "${json_version_major_line}")
    string(REGEX REPLACE "^#define NLOHMANN_JSON_VERSION_MINOR ([0-9]+)$" "\\1" json_version_minor "${json_version_minor_line}")
    string(REGEX REPLACE "^#define NLOHMANN_JSON_VERSION_PATCH ([0-9]+)$" "\\1" json_version_patch "${json_version_patch_line}")
    set(nlohmann_json_VERSION "${json_version_major}.${json_version_minor}.${json_version_patch}")

    include(FindPackageHandleStandardArgs)
    find_package_handle_standard_args(nlohmann_json
        REQUIRED_VARS json_header_path
        VERSION_VAR nlohmann_json_VERSION
    )

    add_library(nlohmann_json::nlohmann_json INTERFACE IMPORTED)
    target_include_directories(nlohmann_json::nlohmann_json INTERFACE ${json_header_path})
    return()
endif()

message(FATAL_ERROR "Unable to find JSON for Modern C++ header file / package, aborting")
