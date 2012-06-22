
OPTION( QT_USE_QTVIEWER "IfcOpenShell QT GUI Viewer, QT environment required" OFF )


IF (QT_USE_QTVIEWER)


# Find QT header files
SET(QT_MIN_VERSION "4.5.0")
FIND_PACKAGE(Qt4 REQUIRED)
FIND_PACKAGE(Qt4 COMPONENTS QtCore QtGui QtOpenGL)

INCLUDE(${QT_USE_FILE})
SET(CMAKE_PACKAGE_QTGUI TRUE)

# Find QT header files
IF("$ENV{QT_INCLUDE_DIR}" STREQUAL "") 
        SET(QT_INCLUDE_DIR "/usr/include/QT4/" CACHE FILEPATH "QT4 header files")
        MESSAGE(STATUS "Looking for QT4 include files in: ${QT_INCLUDE_DIR}")
        MESSAGE(STATUS "Use QT_INCLUDE_DIR to specify another directory")
ELSE()
        SET(QT_INCLUDE_DIR $ENV{QT_INCLUDE_DIR} CACHE FILEPATH "QT4 header files")
        MESSAGE(STATUS "Looking for QT4 include files in: ${QT_INCLUDE_DIR}")
ENDIF()


INCLUDE_DIRECTORIES(${QT_INCLUDE_DIR})

SET(QTviewer_SRCS
        ../../src/qtviewer/mainwindow.h
        ../../src/qtviewer/mainwindow.cpp
        ../../src/qtviewer/main.cpp
)
SET(QTviewer_MOC_SRCS 
        ../../src/qtviewer/mainwindow.h
)

QT_WRAP_CPP(QTviewer QTviewer_SRCS ${QTviewer_MOC_SRCS})

ADD_EXECUTABLE(  QTviewer ${QTviewer_SRCS} ${QTviewer_MOC_SRCS})
#http://www.qtcentre.org/wiki/index.php?title=Compiling_Qt4_apps_with_CMake

TARGET_LINK_libRARIES (QTviewer IfcParse IfcGeom ${QT_LIBRARIES} TKernel TKMath TKBRep TKGeomBase TKGeomAlgo TKG3d TKG2d TKShHealing TKTopAlgo TKMesh TKPrim TKBool TKBO TKFillet)


ENDIF (QT_USE_QTVIEWER)
