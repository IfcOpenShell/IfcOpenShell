cmake_minimum_required (VERSION 2.6)
project (IfcOpenShell)

FIND_PACKAGE(Boost REQUIRED COMPONENTS program_options)
MESSAGE(STATUS "Boost include files found in ${Boost_INCLUDE_DIRS}")
MESSAGE(STATUS "Boost libraries found in ${Boost_LIBRARY_DIRS}")

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

IF("$ENV{ICU_INCLUDE_DIR}" STREQUAL "")
    MESSAGE(STATUS "No ICU include directory specified")
ElSE()
    SET(ICU_INCLUDE_DIR CACHE FILEPATH "ICU header files")
ENDIF()

IF("$ENV{ICU_LIBRARY_DIR}" STREQUAL "")
    MESSAGE(STATUS "No ICU library directory specified")
ElSE()
    SET(ICU_LIBRARY_DIR CACHE FILEPATH "ICU library files")
ENDIF()

FIND_LIBRARY(icu "icuuc" /usr/lib /usr/lib64 /usr/local/lib /usr/local/lib64 ${ICU_LIBRARY_DIR})

IF(icu)
    MESSAGE(STATUS "ICU libraries found")
    ADD_DEFINITIONS(-DHAVE_ICU)
ELSE()
    MESSAGE(STATUS "Unable to find ICU library files, continuing")	
ENDIF()

IF("$ENV{OPENCOLLADA_INCLUDE_DIR}" STREQUAL "")
    MESSAGE(STATUS "No OpenCOLLADA include directory specified")
    SET(OPENCOLLADA_INCLUDE_DIR "/usr/local/include/opencollada" CACHE FILEPATH "OpenCOLLADA header files")
ElSE()
    SET(OPENCOLLADA_INCLUDE_DIR "$ENV{OPENCOLLADA_INCLUDE_DIR}" CACHE FILEPATH "OpenCOLLADA header files")
ENDIF()

IF("$ENV{OPENCOLLADA_LIBRARY_DIR}" STREQUAL "")
    MESSAGE(STATUS "No OpenCOLLADA library directory specified")
    SET(OPENCOLLADA_LIBRARY_DIR "/usr/local/lib/opencollada" CACHE FILEPATH "OpenCOLLADA library files")
ElSE()
    SET(OPENCOLLADA_LIBRARY_DIR "$ENV{OPENCOLLADA_LIBRARY_DIR}" CACHE FILEPATH "OpenCOLLADA library files")
ENDIF()

SET(OPENCOLLADA_INCLUDE_DIRS "${OPENCOLLADA_INCLUDE_DIR}/COLLADABaseUtils" "${OPENCOLLADA_INCLUDE_DIR}/COLLADAStreamWriter")

FIND_FILE(COLLADASWStreamWriter_h "COLLADASWStreamWriter.h" ${OPENCOLLADA_INCLUDE_DIRS})
IF(COLLADASWStreamWriter_h)
    MESSAGE(STATUS "OpenCOLLADA header files found")
    ADD_DEFINITIONS(-DWITH_OPENCOLLADA)
    SET(OPENCOLLADA_LIBRARIES 
        GeneratedSaxParser MathMLSolver OpenCOLLADABaseUtils
        OpenCOLLADAFramework OpenCOLLADASaxFrameworkLoader
        OpenCOLLADAStreamWriter UTF buffer ftoa pcre
    )
ELSE()
    MESSAGE(STATUS "OpenCOLLADA header files not found, continuing without COLLADA support")
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

IF(MSVC)
    ADD_DEFINITIONS(-D_UNICODE)
ElSE(MSVC)
    ADD_DEFINITIONS(-fPIC -Wno-non-virtual-dtor)
ENDIF(MSVC)

INCLUDE_DIRECTORIES(${INCLUDE_DIRECTORIES} ${OCC_INCLUDE_DIR} ${OPENCOLLADA_INCLUDE_DIRS} /usr/inc /usr/local/inc /usr/local/include/oce ${ICU_INCLUDE_DIR} ${Boost_INCLUDE_DIRS})

ADD_LIBRARY(IfcParse STATIC
  ../src/ifcparse/Ifc2x3-latebound.cpp
  ../src/ifcparse/Ifc2x3.cpp
  ../src/ifcparse/Ifc4-latebound.cpp
  ../src/ifcparse/Ifc4.cpp
  ../src/ifcparse/IfcCharacterDecoder.cpp
  ../src/ifcparse/IfcGlobalId.cpp
  ../src/ifcparse/IfcHierarchyHelper.cpp
  ../src/ifcparse/IfcLateBoundEntity.cpp
  ../src/ifcparse/IfcParse.cpp
  ../src/ifcparse/IfcSIPrefix.cpp
  ../src/ifcparse/IfcSpfHeader.cpp
  ../src/ifcparse/IfcUtil.cpp
  ../src/ifcparse/IfcWrite.cpp
)

ADD_LIBRARY(IfcGeom STATIC
  ../src/ifcgeom/IfcGeomCurves.cpp
  ../src/ifcgeom/IfcGeomFaces.cpp
  ../src/ifcgeom/IfcGeomFunctions.cpp
  ../src/ifcgeom/IfcGeomHelpers.cpp
  ../src/ifcgeom/IfcGeomMaterial.cpp
  ../src/ifcgeom/IfcGeomRenderStyles.cpp
  ../src/ifcgeom/IfcGeomRepresentation.cpp
  ../src/ifcgeom/IfcGeomShapes.cpp
  ../src/ifcgeom/IfcGeomWires.cpp
  ../src/ifcgeom/IfcRegister.cpp
)

IF(icu)
    TARGET_LINK_LIBRARIES(IfcParse icuuc)
ENDIF()

TARGET_LINK_LIBRARIES(IfcGeom IfcParse)

LINK_DIRECTORIES (${LINK_DIRECTORIES} ${IfcOpenShell_BINARY_DIR} ${OCC_LIBRARY_DIR} ${OPENCOLLADA_LIBRARY_DIR} /usr/lib /usr/lib64 /usr/local/lib /usr/local/lib64 ${ICU_LIBRARY_DIR} ${Boost_LIBRARY_DIRS}) 

ADD_EXECUTABLE(IfcConvert
    ../src/ifcconvert/ColladaSerializer.cpp
    ../src/ifcconvert/IfcConvert.cpp
    ../src/ifcconvert/OpenCascadeBasedSerializer.cpp
    ../src/ifcconvert/WavefrontObjSerializer.cpp
    ../src/ifcconvert/XmlSerializer.cpp
)

TARGET_LINK_LIBRARIES (IfcConvert IfcParse IfcGeom TKernel TKMath TKBRep TKGeomBase TKGeomAlgo TKG3d TKG2d TKShHealing TKTopAlgo TKMesh TKPrim TKBool TKBO TKFillet TKSTEP TKSTEPBase TKSTEPAttr TKXSBase TKSTEP209 TKIGES TKOffset ${Boost_LIBRARIES} ${OPENCOLLADA_LIBRARIES})

ADD_EXECUTABLE(IfcGeomServer
    ../src/ifcgeomserver/IfcGeomServer.cpp
)

TARGET_LINK_LIBRARIES (IfcGeomServer IfcParse IfcGeom TKernel TKMath TKBRep TKGeomBase TKGeomAlgo TKG3d TKG2d TKShHealing TKTopAlgo TKMesh TKPrim TKBool TKBO TKFillet TKSTEP TKSTEPBase TKSTEPAttr TKXSBase TKSTEP209 TKIGES TKOffset)

# Build python wrapper using separate CMakeLists.txt
ADD_SUBDIRECTORY(../src/ifcwrap ifcwrap)

# Build IfcParseExamples using separate CMakeLists.txt
ADD_SUBDIRECTORY(../src/examples examples)

# ADD_SUBDIRECTORY(../src/qtviewer qtviewer)

# CMake installation targets
SET(include_files_geom
    ../src/ifcgeom/IfcGeom.h
    ../src/ifcgeom/IfcGeomElement.h
    ../src/ifcgeom/IfcGeomIterator.h
    ../src/ifcgeom/IfcGeomIteratorSettings.h
    ../src/ifcgeom/IfcGeomMaterial.h
    ../src/ifcgeom/IfcGeomRenderStyles.h
    ../src/ifcgeom/IfcGeomRepresentation.h
    ../src/ifcgeom/IfcGeomShapeType.h
    ../src/ifcgeom/IfcRegister.h
    ../src/ifcgeom/IfcRegisterConvertCurve.h
    ../src/ifcgeom/IfcRegisterConvertFace.h
    ../src/ifcgeom/IfcRegisterConvertShape.h
    ../src/ifcgeom/IfcRegisterConvertShapes.h
    ../src/ifcgeom/IfcRegisterConvertWire.h
    ../src/ifcgeom/IfcRegisterCreateCache.h
    ../src/ifcgeom/IfcRegisterDef.h
    ../src/ifcgeom/IfcRegisterGeomHeader.h
    ../src/ifcgeom/IfcRegisterPurgeCache.h
    ../src/ifcgeom/IfcRegisterShapeType.h
    ../src/ifcgeom/IfcRegisterUndef.h
    ../src/ifcgeom/IfcRepresentationShapeItem.h
)

SET(include_files_parse
    ../src/ifcparse/Ifc2x3-latebound.h
    ../src/ifcparse/Ifc2x3.h
    ../src/ifcparse/Ifc2x3enum.h
    ../src/ifcparse/Ifc4-latebound.h
    ../src/ifcparse/Ifc4.h
    ../src/ifcparse/Ifc4enum.h
    ../src/ifcparse/IfcCharacterDecoder.h
    ../src/ifcparse/IfcEntityDescriptor.h
    ../src/ifcparse/IfcException.h
    ../src/ifcparse/IfcFile.h
    ../src/ifcparse/IfcGlobalId.h
    ../src/ifcparse/IfcHierarchyHelper.h
    ../src/ifcparse/IfcLateBoundEntity.h
    ../src/ifcparse/IfcParse.h
    ../src/ifcparse/IfcSIPrefix.h
    ../src/ifcparse/IfcSpfHeader.h
    ../src/ifcparse/IfcSpfStream.h
    ../src/ifcparse/IfcUtil.h
    ../src/ifcparse/IfcWritableEntity.h
    ../src/ifcparse/IfcWrite.h
    ../src/ifcparse/SharedPointer.h
)
INSTALL(FILES ${include_files_geom} DESTINATION include/ifcgeom)
INSTALL(FILES ${include_files_parse} DESTINATION include/ifcparse)
INSTALL(TARGETS IfcConvert DESTINATION bin)
INSTALL(TARGETS IfcParse IfcGeom DESTINATION lib)
