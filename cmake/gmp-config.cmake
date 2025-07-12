if(CMAKE_SYSTEM_NAME MATCHES "Linux")
    set(GMP_LIBRARY_DIR "/usr/lib/x86_64-linux-gnu")
    set(GMP_INCLUDE_DIR "/usr/include/x86_64-linux-gnu")
elseif(CMAKE_SYSTEM_NAME MATCHES "WIN32")
    set(GMP_LIBRARY_DIR "C:/Program Files (x86)/GMP/lib")
elseif(CMAKE_SYSTEM_NAME MATCHES "APPLE")
    set(GMP_LIBRARY_DIR "/usr/local/lib")
else()
    message(FATAL_ERROR "Unsupported platform for GMP library")
endif()

find_path(GMP_INCLUDE_DIR NAMES gmp.h PATHS ${GMP_INCLUDE_DIR}/include NO_DEFAULT_PATH)
if(NOT GMP_INCLUDE_DIR)
    message(FATAL_ERROR "Unable to find GMP include files, aborting")
endif()

find_library(libGMP NAMES gmp PATHS ${GMP_LIBRARY_DIR} NO_DEFAULT_PATH)

if(NOT libGMP)
    message(FATAL_ERROR "Unable to find GMP library files, aborting")
endif()

set(gmp_LIBRARIES_TARGETS "${libGMP}")
