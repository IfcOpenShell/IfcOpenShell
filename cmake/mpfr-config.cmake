message(STATUS "CMAKE_SYSTEM_NAME:  ${CMAKE_SYSTEM_NAME}")
if(CMAKE_SYSTEM_NAME MATCHES "Linux")
    set(MPFR_LIBRARY_DIR "/usr/lib/x86_64-linux-gnu")
    set(MPFR_INCLUDE_DIR "/usr/include/x86_64-linux-gnu")
elseif(CMAKE_SYSTEM_NAME MATCHES "win32")
    set(MPFR_LIBRARY_DIR "C:/Program Files (x86)/MPFR/lib")
elseif(CMAKE_SYSTEM_NAME MATCHES "Apple")
    set(MPFR_LIBRARY_DIR "/usr/local/lib")
else()
    message(FATAL_ERROR "Unsupported platform for MPFR library")
endif()

find_path(MPFR_INCLUDE_DIR NAMES mpfr.h PATHS ${MPFR_INCLUDE_DIR}/include NO_DEFAULT_PATH)
if(NOT MPFR_INCLUDE_DIR)
    message(FATAL_ERROR "Unable to find MPFR include files, aborting")
endif()

find_library(libMPFR NAMES mpfr mpir PATHS ${MPFR_LIBRARY_DIR} NO_DEFAULT_PATH)

if(NOT libMPFR)
    message(FATAL_ERROR "Unable to find MPFR library files, aborting")
endif()

set(mpfr_LIBRARIES_TARGETS "${libMPFR}")