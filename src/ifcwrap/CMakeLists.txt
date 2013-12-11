FIND_PACKAGE(SWIG)

IF(SWIG_FOUND)

INCLUDE(${SWIG_USE_FILE})  

FIND_PACKAGE(PythonLibs)

IF(PYTHONLIBS_FOUND)

INCLUDE_DIRECTORIES(${PYTHON_INCLUDE_PATH})

INCLUDE_DIRECTORIES(${CMAKE_CURRENT_SOURCE_DIR})

SET(CMAKE_SWIG_FLAGS "")

SET_SOURCE_FILES_PROPERTIES(IfcPython.i PROPERTIES CPLUSPLUS ON)
SWIG_ADD_MODULE(IfcImport python IfcPython.i)
SWIG_LINK_LIBRARIES(IfcImport ${PYTHON_LIBRARIES} IfcParse IfcGeom TKernel TKMath TKBRep TKGeomBase TKGeomAlgo TKG3d TKG2d TKShHealing TKTopAlgo TKMesh TKPrim TKBool TKBO TKFillet)

# To install IfcPython let's get the site-packackes dir from python
EXECUTE_PROCESS(COMMAND python -c "from distutils.sysconfig import get_python_lib as x; print (x())"
	OUTPUT_VARIABLE python_package_dir)

# Strip trailing whitespace from python print
STRING(REPLACE "\r" "" python_package_dir "${python_package_dir}")
STRING(REPLACE "\n" "" python_package_dir "${python_package_dir}")

INSTALL(FILES 
		"${CMAKE_BINARY_DIR}/ifcwrap/IfcImport.py"
	DESTINATION "${python_package_dir}")
INSTALL(TARGETS _IfcImport DESTINATION "${python_package_dir}")

ENDIF(PYTHONLIBS_FOUND)

ENDIF(SWIG_FOUND)