cmake_minimum_required (VERSION 2.6)
project (IfcOpenShell)

# Find Open CASCADE header files
IF("$ENV{OCC_INCLUDE_DIR}" STREQUAL "") 
	SET(OCC_INCLUDE_DIR "/usr/include/opencascade/" CACHE FILEPATH "Open CASCADE header files")
	MESSAGE(STATUS "Looking for opencascade include files in: ${OCC_INCLUDE_DIR}")
	MESSAGE(STATUS "Use OCC_INCLUDE_DIR to specify another directory")
ELSE()
	SET(OCC_INCLUDE_DIR $ENV{OCC_INCLUDE_DIR} CACHE FILEPATH "Open CASCADE header files")
	MESSAGE(STATUS "Looking for opencascade include files in: ${OCC_INCLUDE_DIR}")
ENDIF()

FIND_FILE(gp_Pnt_hxx "gp_Pnt.hxx" ${OCC_INCLUDE_DIR})
IF(gp_Pnt_hxx)
	MESSAGE(STATUS "Header files found")
ELSE()
	MESSAGE(FATAL_ERROR "Unable to find header files, aborting")
ENDIF()


# Find Open CASCADE library files
IF("$ENV{OCC_LIBRARY_DIR}" STREQUAL "") 
	SET(OCC_LIBRARY_DIR "/usr/lib/" CACHE FILEPATH "Open CASCADE library files")
	MESSAGE(STATUS "Looking for opencascade library files in: ${OCC_LIBRARY_DIR}")
	MESSAGE(STATUS "Use OCC_LIBRARY_DIR to specify another directory")
ELSE()
	SET(OCC_LIBRARY_DIR $ENV{OCC_LIBRARY_DIR} CACHE FILEPATH "Open CASCADE library files")
	MESSAGE(STATUS "Looking for opencascade library files in: ${OCC_LIBRARY_DIR}")
ENDIF()

FIND_LIBRARY(libTKernel "TKernel" ${OCC_LIBRARY_DIR})
IF(libTKernel)
	MESSAGE(STATUS "Library files found")
ELSE()
	MESSAGE(FATAL_ERROR "Unable to find library files, aborting")
ENDIF()

INCLUDE(CheckIncludeFileCXX)

MACRO(CHECK_ADD_OCE_OCC_DEF INCLUDE)
	STRING(REPLACE . _ STR ${INCLUDE})
	STRING(TOUPPER ${STR} STR)
	CHECK_INCLUDE_FILE_CXX("${INCLUDE}" FOUND_${STR})
	IF(FOUND_${STR})
		ADD_DEFINITIONS(-DOCE_HAVE_${STR})
		ADD_DEFINITIONS(-DHAVE_${STR})
	ENDIF(FOUND_${STR})
ENDMACRO(CHECK_ADD_OCE_OCC_DEF)

CHECK_ADD_OCE_OCC_DEF(limits)
CHECK_ADD_OCE_OCC_DEF(climits)
CHECK_ADD_OCE_OCC_DEF(limits.h)  
CHECK_ADD_OCE_OCC_DEF(fstream)
CHECK_ADD_OCE_OCC_DEF(fstream.h)
CHECK_ADD_OCE_OCC_DEF(iomanip)
CHECK_ADD_OCE_OCC_DEF(iomanip.h)
CHECK_ADD_OCE_OCC_DEF(iostream)  
CHECK_ADD_OCE_OCC_DEF(iostream.h)

ADD_DEFINITIONS(-O3)
ADD_DEFINITIONS(-fPIC)

INCLUDE_DIRECTORIES(${OCC_INCLUDE_DIR})
ADD_LIBRARY(IfcParse STATIC ../src/ifcparse/IfcEnum.cpp ../src/ifcparse/IfcTypes.cpp ../src/ifcparse/IfcParse.cpp ../src/ifcparse/IfcGeom.cpp ../src/ifcparse/IfcGeomObjects.cpp)

LINK_DIRECTORIES (${IfcOpenShell_BINARY_DIR} /usr/lib) 
ADD_EXECUTABLE(IfcObj ../src/ifcobj/IfcObj.cpp)
TARGET_LINK_LIBRARIES (IfcObj IfcParse TKAdvTools TKMath TKernel TKBRep TKGeomBase TKGeomAlgo TKBool TKMesh TKShHealing TKFillet) 

# Build python wrapper using separate CMakeLists.txt
ADD_SUBDIRECTORY(../src/ifcwrap .)
