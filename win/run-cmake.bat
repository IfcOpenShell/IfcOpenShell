:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
::                                                                             ::
:: This file is part of IfcOpenShell.                                          ::
::                                                                             ::
:: IfcOpenShell is free software: you can redistribute it and/or modify        ::
:: it under the terms of the Lesser GNU General Public License as published by ::
:: the Free Software Foundation, either version 3.0 of the License, or         ::
:: (at your option) any later version.                                         ::
::                                                                             ::
:: IfcOpenShell is distributed in the hope that it will be useful,             ::
:: but WITHOUT ANY WARRANTY; without even the implied warranty of              ::
:: MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the                ::
:: Lesser GNU General Public License for more details.                         ::
::                                                                             ::
:: You should have received a copy of the Lesser GNU General Public License    ::
:: along with this program. If not, see <http://www.gnu.org/licenses/>.        ::
::                                                                             ::
:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
::
:: Example usage:
::   run-cmake.bat vs2022-x64
::   run-cmake.bat vs2022-x64 -DGLTF_SUPPORT=ON -DHDF5_SUPPORT=OFF
::
:: Used environment variables:
:: - `ADD_COMMIT_SHA` - if defined then `ADD_COMMIT_SHA` and `VERSION_OVERRIDE` cmake args will be set to `ON`.
:: - `USE_NINJA` - if defined then the Ninja generator will be used instead of the Visual Studio.


@if not defined ECHO_ON ( echo off )
echo.

set PROJECT_NAME=IfcOpenShell

setlocal EnableDelayedExpansion
set IFCOS_PAUSE_ON_ERROR=

set GENERATOR=%1

:: If no GENERATOR was provided, read cached variables from any BuildDepsCache-XXX.txt
:: found in this directory; note that if more than one is present, the result could be wrong!
if (%1)==() (
	for /f "tokens=*" %%f in ('dir BuildDepsCache-*.txt /o:-n /t:a /b') do (
		for /f "delims== tokens=1,2" %%G in (%%f) do set %%G=%%H
	)

    if not defined GEN_SHORTHAND (
        echo BuildDepsCache file does not exist and/or GEN_SHORTHAND missing from it. Run build-deps.cmd to create it.
        set IFCOS_PAUSE_ON_ERROR=pause
        goto :Error
    )
    set GENERATOR=!GEN_SHORTHAND!
    echo Generator not passed, but GEN_SHORTHAND=!GENERATOR! read from BuildDepsCache
    echo.
)

call vs-cfg.cmd %GENERATOR%
IF NOT %ERRORLEVEL%==0 GOTO :Error

:: If cached variables are still undefined,
:: read them from the specific BuildDepsCache-XXX.txt.
set "_test=0"
if not defined OCC_INCLUDE_DIR set _test=1
if not defined OCC_LIBRARY_DIR set _test=1
if %_test% EQU 1 (
	IF DEFINED VS_TOOLSET (
		set "BUILD_DEPS_CACHE_PATH=BuildDepsCache-%VS_PLATFORM%-%VS_TOOLSET%.txt"
	) ELSE (
		set "BUILD_DEPS_CACHE_PATH=BuildDepsCache-%VS_PLATFORM%.txt"
	)

	for /f "tokens=*" %%f in ('dir !BUILD_DEPS_CACHE_PATH! /o:-n /t:a /b') do (
		for /f "delims== tokens=1,2" %%G in (%%f) do set %%G=%%H
	)
)

:: As CMake options are typically of format -DSOMETHING:BOOL=ON or -DSOMETHING=1, i.e. they contain an equal sign,
:: they will mess up the batch file argument parsing if the arguments are passed on by splitting them %2 %3 %4 %5
:: %6 %7 %8 %9. Work around that, http://scripts.dragon-it.co.uk/scripts.nsf/docs/batch-search-replace-substitute
if not (%1)==() (
    set ARGUMENTS=%*
    call set ARGUMENTS=%%ARGUMENTS:%1=%%
)

pushd ..
set CMAKE_INSTALL_PREFIX=%CD%\_installed-%GEN_SHORTHAND%
popd

IF NOT EXIST ..\%BUILD_DIR%. mkdir ..\%BUILD_DIR%
pushd ..\%BUILD_DIR%

:: Legacy setup.
if not defined BOOST_INSTALL_DIR (
    set BOOST_INSTALL_DIR=%DEPS_DIR%\boost_1_86_0\stage\%GEN_SHORTHAND%
)

set OPENCOLLADA_INSTALL_DIR=%INSTALL_DIR%\OpenCOLLADA
set LIBXML2_INCLUDE_DIR=%DEPS_DIR%\OpenCOLLADA\Externals\LibXML\include
set LIBXML2_LIBRARIES=%INSTALL_DIR%\OpenCOLLADA\lib\opencollada\xml.lib
set HDF5_INSTALL_DIR=%INSTALL_DIR%\HDF5-%HDF5_VERSION%-win%ARCH_BITS%

set PYTHON_EXECUTABLE=%PYTHONHOME%\python.exe
for /f "usebackq delims=" %%v in (`
    call "%PYTHON_EXECUTABLE%" -c "import sys; print(f'{sys.version_info[0]}{sys.version_info[1]}')"
`) do set "PY_VER_MAJOR_MINOR=%%v"
set PYTHON_INCLUDE_DIR=%PYTHONHOME%\include
set PYTHON_LIBRARY=%PYTHONHOME%\libs\python%PY_VER_MAJOR_MINOR%.lib

:: `swigwin` is a legacy installation folder name, before we started using versioned folders.
:: we can remove it later.
if not defined SWIG_INSTALL_DIR set SWIG_INSTALL_DIR=%INSTALL_DIR%\swigwin
set JSON_INCLUDE_DIR=%INSTALL_DIR%\json
if defined ADD_COMMIT_SHA (
    set ADD_COMMIT_SHA=ON
    set VERSION_OVERRIDE=ON
) else (
    set ADD_COMMIT_SHA=OFF
    set VERSION_OVERRIDE=OFF
)

set CGAL_INSTALL_DIR=%INSTALL_DIR%\cgal
set GMP_INSTALL_DIR=%INSTALL_DIR%\mpir
set MPFR_INSTALL_DIR=%INSTALL_DIR%\mpfr
:: We don't install Eigen currently,
:: so there's no Eigen3config.cmake and therefore we provide path explicitly.
set EIGEN_DIR=%INSTALL_DIR%\Eigen
set TBB_INSTALL_DIR=%INSTALL_DIR%\tbb
set USD_INSTALL_DIR=%INSTALL_DIR%\usd
set ROCKSDB_INSTALL_DIR=%INSTALL_DIR%\rocksdb
set ZSTD_INSTALL_DIR=%INSTALL_DIR%\zstd

echo.
call cecho.cmd 0 10 "Script configuration:"
echo   Generator    = %GENERATOR%
echo   Architecture = %VS_PLATFORM%
echo   Toolset      = %VS_TOOLSET%
echo   Arguments    = %ARGUMENTS%
echo.
call cecho.cmd 0 10 "Dependency Environment Variables for %PROJECT_NAME%:"
echo    BOOST_INSTALL_DIR       = %BOOST_INSTALL_DIR%
:: OCC_INCLUDE_DIR / OCC_LIBRARY_DIR are legacy vars, they're not defined by build-deps.cmd anymore.
echo    OCC_INCLUDE_DIR         = %OCC_INCLUDE_DIR%
echo    OCC_LIBRARY_DIR         = %OCC_LIBRARY_DIR%
echo    OCC_INSTALL_DIR         = %OCC_INSTALL_DIR%
echo    OPENCOLLADA_INSTALL_DIR = %OPENCOLLADA_INSTALL_DIR%
echo    LIBXML2_INCLUDE_DIR     = %LIBXML2_INCLUDE_DIR%
echo    LIBXML2_LIBRARIES       = %LIBXML2_LIBRARIES%
echo    HDF5_INSTALL_DIR        = %HDF5_INSTALL_DIR%
echo    PYTHONHOME              = %PYTHONHOME%
echo    PYTHON_INCLUDE_DIR      = %PYTHON_INCLUDE_DIR%
echo    PYTHON_LIBRARY          = %PYTHON_LIBRARY%
echo    PYTHON_EXECUTABLE       = %PYTHON_EXECUTABLE%
echo    SWIG_INSTALL_DIR        = %SWIG_INSTALL_DIR%
echo    JSON_INCLUDE_DIR        = %JSON_INCLUDE_DIR%
echo.
echo    CGAL_INSTALL_DIR        = %CGAL_INSTALL_DIR%
:: echo    CGAL_LIBRARY_DIR        = %CGAL_LIBRARY_DIR%
echo    GMP_INSTALL_DIR         = %GMP_INSTALL_DIR%
echo    MPFR_INSTALL_DIR        = %MPFR_INSTALL_DIR%
echo    EIGEN_DIR               = %EIGEN_DIR%
echo    TBB_INSTALL_DIR         = %TBB_INSTALL_DIR%
echo    USD_INSTALL_DIR         = %USD_INSTALL_DIR%
echo    ROCKSDB_INSTALL_DIR     = %ROCKSDB_INSTALL_DIR%
echo    ZSTD_INSTALL_DIR        = %ZSTD_INSTALL_DIR%
echo    CCACHE_INSTALL_DIR      = %CCACHE_INSTALL_DIR%
echo.
echo    CMAKE_INSTALL_PREFIX    = %CMAKE_INSTALL_PREFIX%
echo.

set CMAKELISTS_DIR=..\cmake
:: Delete CMakeCache.txt if command-line options were provided for this batch script.
if not (%1)==() if exist CMakeCache.txt. del /Q CMakeCache.txt
echo "Running CMake for %PROJECT_NAME%."

set CMAKE_PREFIX_PATH=%HDF5_INSTALL_DIR%;%OPENCOLLADA_INSTALL_DIR%;%SWIG_INSTALL_DIR%
set CMAKE_PREFIX_PATH=%CMAKE_PREFIX_PATH%;%ROCKSDB_INSTALL_DIR%;%ZSTD_INSTALL_DIR%
set CMAKE_PREFIX_PATH=%CMAKE_PREFIX_PATH%;%BOOST_INSTALL_DIR%;%CCACHE_INSTALL_DIR%
set CMake_PREFIX_PATH=%CMAKE_PREFIX_PATH%;%USD_INSTALL_DIR%;%TBB_INSTALL_DIR%
set CMAKE_PREFIX_PATH=%CMAKE_PREFIX_PATH%;%OCC_INSTALL_DIR%;%CGAL_INSTALL_DIR%
set CMAKE_PREFIX_PATH=%CMAKE_PREFIX_PATH%;%GMP_INSTALL_DIR%;%MPFR_INSTALL_DIR%

:: Not fully supported - not available from install-ifcopenshell
:: and some logs are still showing Visual Studio generators.
:: Needed just for debugging.
if defined USE_NINJA (
    set GENERATOR=Ninja
    set ARCH_OPTION=
) else (
    set GENERATOR=%GENERATOR%
    set ARCH_OPTION=-A %VS_PLATFORM%
)

IF NOT "%VS_TOOLSET_HOST%"=="" (
    set VS_TOOLSET_OPTION=-T %VS_TOOLSET_HOST%
)

cmake.exe %CMAKELISTS_DIR% -G %GENERATOR% %ARCH_OPTION% %VS_TOOLSET_OPTION% ^
    -DCMAKE_INSTALL_PREFIX="%CMAKE_INSTALL_PREFIX%" ^
    -DWITH_ROCKSDB=On -DWITH_ZSTD=On ^
    -DCMAKE_PREFIX_PATH="%CMAKE_PREFIX_PATH%" ^
    -DADD_COMMIT_SHA=%ADD_COMMIT_SHA% -DVERSION_OVERRIDE=%VERSION_OVERRIDE% ^
    %ARGUMENTS%

IF NOT %ERRORLEVEL%==0 GOTO :Error

echo.

set IFCOS_SCRIPT_RET=0
goto :Finish

:Error
echo.
call "%~dp0\utils\cecho.cmd" 0 12 "An error occurred! Aborting!"
%IFCOS_PAUSE_ON_ERROR%
set IFCOS_SCRIPT_RET=1
goto :Finish

:Finish
popd
exit /b %IFCOS_SCRIPT_RET%
