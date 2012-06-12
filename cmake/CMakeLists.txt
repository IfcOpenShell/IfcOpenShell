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

FIND_FILE(gp_Pnt_hxx "gp_Pnt.hxx" ${OCC_INCLUDE_DIR} /usr/inc /usr/local/inc /usr/local/include/oce)
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

FIND_LIBRARY(libTKernel "TKernel" ${OCC_LIBRARY_DIR} /usr/lib /usr/lib64 /usr/local/lib /usr/local/lib64)
IF(libTKernel)
	MESSAGE(STATUS "Library files found")
ELSE()
	MESSAGE(FATAL_ERROR "Unable to find library files, aborting")
ENDIF()

FIND_LIBRARY(icu "icuuc" /usr/lib /usr/lib64 /usr/local/lib /usr/local/lib64)

IF(icu)
	MESSAGE(STATUS "ICU libraries found")
    ADD_DEFINITIONS(-DHAVE_ICU)
ELSE()
	MESSAGE(STATUS "Unable to find ICU library files, continuing")	
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

IF(NOT CMAKE_BUILD_TYPE)
 	SET(CMAKE_BUILD_TYPE "Release")
ENDIF(NOT CMAKE_BUILD_TYPE)

IF(NOT MSVC)
    ADD_DEFINITIONS(-fPIC -Wno-non-virtual-dtor)
ENDIF(NOT MSVC)

INCLUDE_DIRECTORIES(${OCC_INCLUDE_DIR} /usr/inc /usr/local/inc /usr/local/include/oce)
ADD_LIBRARY(IfcParse STATIC 
  ../src/ifcparse/Ifc2x3.cpp
  ../src/ifcparse/IfcUtil.cpp
  ../src/ifcparse/IfcParse.cpp
  ../src/ifcparse/IfcCharacterDecoder.cpp
)

ADD_LIBRARY(IfcGeom STATIC
  ../src/ifcgeom/IfcGeomCurves.cpp
  ../src/ifcgeom/IfcGeomFaces.cpp
  ../src/ifcgeom/IfcGeomFunctions.cpp
  ../src/ifcgeom/IfcGeomHelpers.cpp
  ../src/ifcgeom/IfcGeomObjects.cpp
  ../src/ifcgeom/IfcGeomShapes.cpp
  ../src/ifcgeom/IfcGeomWires.cpp
  ../src/ifcgeom/IfcRegister.cpp
)

IF(icu)
    TARGET_LINK_LIBRARIES(IfcParse icuuc)
ENDIF()

TARGET_LINK_LIBRARIES(IfcGeom IfcParse)

LINK_DIRECTORIES (${IfcOpenShell_BINARY_DIR} ${OCC_LIBRARY_DIR} /usr/lib /usr/lib64 /usr/local/lib /usr/local/lib64) 
ADD_EXECUTABLE(IfcObj ../src/ifcobj/IfcObj.cpp)

IF(MINGW)
TARGET_LINK_libRARIES (IfcObj IfcParse IfcGeom libTKernel libTKMath TKBRep.dll.a TKGeomBase.dll.a TKGeomAlgo.dll.a TKG3d.dll.a TKG2d.dll.a TKShHealing.dll.a TKTopAlgo.dll.a TKMesh.dll.a TKPrim.dll.a TKBool.dll.a TKBO.dll.a TKFillet.dll.a)
ENDIF(MINGW)
IF(MSVC)
TARGET_LINK_LIBRARIES (IfcObj IfcParse.lib IfcGeom.lib TKernel.lib TKMath.lib TKBRep.lib TKGeomBase.lib TKGeomAlgo.lib TKG3d.lib TKG2d.lib TKShHealing.lib TKTopAlgo.lib TKMesh.lib TKPrim.lib TKBool.lib TKBO.lib TKFillet.lib)
ENDIF(MSVC)
IF(UNIX)
TARGET_LINK_LIBRARIES (IfcObj IfcParse IfcGeom TKernel TKMath TKBRep TKGeomBase TKGeomAlgo TKG3d TKG2d TKShHealing TKTopAlgo TKMesh TKPrim TKBool TKBO TKFillet)
ENDIF(UNIX)

# Build python wrapper using separate CMakeLists.txt
ADD_SUBDIRECTORY(../src/ifcwrap ifcwrap)

# Build IfcParseExamples using separate CMakeLists.txt
ADD_SUBDIRECTORY(../src/examples examples)

# CMake installation targets
SET(include_files_geom
    ../src/ifcgeom/IfcGeom.h
    ../src/ifcgeom/IfcGeomObjects.h
    ../src/ifcgeom/IfcRegister.h
    ../src/ifcgeom/IfcRegisterConvertCurve.h
    ../src/ifcgeom/IfcRegisterConvertFace.h
    ../src/ifcgeom/IfcRegisterConvertShape.h
    ../src/ifcgeom/IfcRegisterConvertShapes.h
    ../src/ifcgeom/IfcRegisterConvertWire.h
    ../src/ifcgeom/IfcRegisterCreateCache.h
    ../src/ifcgeom/IfcRegisterDef.h
    ../src/ifcgeom/IfcRegisterGeomHeader.h
    ../src/ifcgeom/IfcRegisterIsShapeCollection.h
    ../src/ifcgeom/IfcRegisterPurgeCache.h
    ../src/ifcgeom/IfcRegisterUndef.h
    ../src/ifcgeom/IfcShapeList.h
)
SET(include_files_parse
    ../src/ifcparse/Ifc2x3.h
    ../src/ifcparse/Ifc2x3enum.h
    ../src/ifcparse/IfcCharacterDecoder.h
    ../src/ifcparse/IfcException.h
    ../src/ifcparse/IfcFile.h
    ../src/ifcparse/IfcParse.h
    ../src/ifcparse/IfcUtil.h
    ../src/ifcparse/SharedPointer.h
)
INSTALL(FILES ${include_files_geom} DESTINATION include/ifcgeom)
INSTALL(FILES ${include_files_parse} DESTINATION include/ifcparse)
INSTALL(TARGETS IfcObj DESTINATION bin)
INSTALL(TARGETS IfcParse IfcGeom DESTINATION lib)
