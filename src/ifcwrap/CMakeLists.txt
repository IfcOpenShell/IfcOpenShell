FIND_PACKAGE(SWIG)

IF(SWIG_FOUND)

INCLUDE(${SWIG_USE_FILE})  

FIND_PACKAGE(PythonLibs)

IF(PYTHONLIBS_FOUND)

INCLUDE_DIRECTORIES(${PYTHON_INCLUDE_PATH})

INCLUDE_DIRECTORIES(${CMAKE_CURRENT_SOURCE_DIR})

SET(CMAKE_SWIG_FLAGS "")

SET_SOURCE_FILES_PROPERTIES(IfcPython.i PROPERTIES CPLUSPLUS ON)
SWIG_ADD_MODULE(ifcopenshell_wrapper python IfcPython.i)
SWIG_LINK_LIBRARIES(ifcopenshell_wrapper ${PYTHON_LIBRARIES} IfcParse IfcGeom TKernel TKMath TKBRep TKGeomBase TKGeomAlgo TKG3d TKG2d TKShHealing TKTopAlgo TKMesh TKPrim TKBool TKBO TKFillet TKOffset ${ICU_LIBRARIES})

# To install IfcPython let's get the site-packages dir from python
EXECUTE_PROCESS(COMMAND python -c "import sys; from distutils.sysconfig import get_python_lib; sys.stdout.write(get_python_lib())"
	OUTPUT_VARIABLE python_package_dir)

INSTALL(FILES 
		"${CMAKE_BINARY_DIR}/ifcwrap/ifcopenshell_wrapper.py"
        "${CMAKE_CURRENT_SOURCE_DIR}/../ifcopenshell-python/ifcopenshell/__init__.py"
        "${CMAKE_CURRENT_SOURCE_DIR}/../ifcopenshell-python/ifcopenshell/guid.py"
	DESTINATION "${python_package_dir}/ifcopenshell")
INSTALL(FILES
        "${CMAKE_CURRENT_SOURCE_DIR}/../ifcopenshell-python/ifcopenshell/geom/__init__.py"
	DESTINATION "${python_package_dir}/ifcopenshell/geom")
INSTALL(TARGETS _ifcopenshell_wrapper DESTINATION "${python_package_dir}/ifcopenshell")

ENDIF(PYTHONLIBS_FOUND)

ENDIF(SWIG_FOUND)