find_package(Doxygen REQUIRED)
find_package(Sphinx REQUIRED)

set(SPHINX_SOURCE ${CMAKE_CURRENT_SOURCE_DIR})
set(SPHINX_BUILD ${CMAKE_CURRENT_BINARY_DIR}/docs/sphinx)

MESSAGE(STATUS "SPHINX BUILD ${CMAKE_CURRENT_BINARY_DIR}")

file(MAKE_DIRECTORY ./output/doxygen)
set(OUTPUT_FOLDER ./output)

if (DOXYGEN_FOUND)

	MESSAGE(STATUS "${PROJECT_SOURCE_DIR}")
	MESSAGE(STATUS "${DOXYGEN_OUTPUT_DIR}/html/index.html")



	# # Find all the public headers
		# #get_target_property(IFC_GEOM_PUBLIC_HEADER_DIR IfcGeom INTERFACE_INCLUDE_DIRECTORIES)
	# file(GLOB_RECURSE CAT_CUTIFIER_PUBLIC_HEADERS ${CAT_CUTIFIER_PUBLIC_HEADER_DIR}/*.h)

	
	# file(GLOB SERIALIZERS_H_FILES C://Users//jlutt//Documents//IfcOpenShell//src//testdoc/*.h)
	# set(DOXYGEN_INPUT_DIR  C://Users//jlutt//Documents//IfcOpenShell//src//testdoc)
	
	
	# file(GLOB SERIALIZERS_H_FILES C://Users//jlutt//Documents//IfcOpenShell//src//serializers/*.h)
	
	
	# set(DOXYGEN_OUTPUT_DIR C://Users//jlutt//Documents//IfcOpenShell//docs/doxygen)
	# set(DOXYGEN_INDEX_FILE C://Users//jlutt//Documents//IfcOpenShell//docs/doxygen/html/index.html)

	# set(DOXYFILE_IN C://Users//jlutt//Documents//IfcOpenShell//docs//Doxyfile.in)
	# set(DOXYFILE_OUT C://Users//jlutt//Documents//IfcOpenShell//docs//Doxyfile.out)

	# #Replace variables inside @@ with the current values
	# configure_file(${DOXYFILE_IN} ${DOXYFILE_OUT} @ONLY)


add_custom_target(Sphinx ALL
                  COMMAND
                  ${SPHINX_EXECUTABLE} -b html
				  ${SPHINX_SOURCE} C://Users//jlutt//Documents//IfcOpenShell//docs//output//sphinx
                  WORKING_DIRECTORY C://Users//jlutt//Documents//IfcOpenShell//docs//output
				  #WORKING_DIRECTORY ${OUTPUT_FOLDER}
                  COMMENT "Generating documentation with Sphinx")
				  
				  

add_custom_target(pyrealsense2_docs ALL
                  COMMAND make html
                  WORKING_DIRECTORY C://Users//jlutt//Documents//IfcOpenShell//src//ifcblenderexport//docs
				  OUTPUT C://Users//jlutt//Documents//IfcOpenShell//src//ifcblenderexport//docs
                  COMMENT "Generating documentation with Sphinx")
	

	
else (DOXYGEN_FOUND)
  message("Doxygen need to be installed to generate the doxygen documentation")
endif (DOXYGEN_FOUND)
