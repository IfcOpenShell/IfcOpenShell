@echo off

:: This is a batch file to set the environment variables for the project
:: It is not necessary for conda compilation, but it provides you with type hints when working with the c++ libraries
:: OpenCascade, CGAL, Eigen, etc distributed using conda-forge in your IDE.
::
:: mamba env update -f environment.build.yml --prune
:: mamba activate ifcopenshell-build
::
:: Note!
:: You have to add a .env file next to this env.bat file where you set PREFIX=<path to your conda env>
set CONDA_BUILD=1
set MY_PY_VER=311

:: set this file's parent directory as a variable
set THIS_DIR=%~dp0

:: read the .env file located in THIS_DIR and set the environment variables.
:: the .env file should contain a line like this:
:: PREFIX=C:\Users\your_user_name\mambaforge3\envs\ifcopenshell-build
for /f "tokens=*" %%i in (%THIS_DIR%.env) do set %%i

set LIBRARY_PREFIX=%PREFIX%/Library
set CMAKE_PREFIX_PATH=%PREFIX%;%LIBRARY_PREFIX%/include;%LIBRARY_PREFIX%/lib;%LIBRARY_PREFIX%/bin

set OCC_LIBRARY_DIR=%LIBRARY_PREFIX%/lib
set OCC_INCLUDE_DIR=%LIBRARY_PREFIX%/include/opencascade

set CGAL_DIR=%LIBRARY_PREFIX%/lib/cmake/CGAL
set CGAL_INCLUDE_DIR=%LIBRARY_PREFIX%/include
set EIGEN_DIR=%LIBRARY_PREFIX%/include/eigen3
set LIBXML2_INCLUDE_DIR=%LIBRARY_PREFIX%/include/libxml2
set LIBXML2_LIBRARIES=%LIBRARY_PREFIX%/lib/libxml2.lib
set Boost_LIBRARY_DIR=%LIBRARY_PREFIX%/lib
set Boost_INCLUDE_DIR=%LIBRARY_PREFIX%/include
set Boost_USE_STATIC_LIBS=OFF

set GMP_INCLUDE_DIR=%LIBRARY_PREFIX%/include
set GMP_LIBRARY_DIR=%LIBRARY_PREFIX%/lib
set MPFR_LIBRARY_DIR=%LIBRARY_PREFIX%/lib

set HDF5_INCLUDE_DIR=%LIBRARY_PREFIX%/include
set HDF5_LIBRARY_DIR=%LIBRARY_PREFIX%/lib
set JSON_INCLUDE_DIR=%LIBRARY_PREFIX%/include

set HDF5_SUPPORT=ON
set BUILD_IFCPYTHON=ON
set BUILD_IFCGEOM=ON
set COLLADA_SUPPORT=OFF
set BUILD_EXAMPLES=OFF
set BUILD_GEOMSERVER=OFF
set GLTF_SUPPORT=ON
set BUILD_CONVERT=ON
set BUILD_IFCMAX=OFF
set IFCXML_SUPPORT=ON

set PYTHON_EXECUTABLE=%PREFIX%/python.exe
set PYTHON_LIBRARY=%PREFIX%/libs/python%MY_PY_VER%.lib