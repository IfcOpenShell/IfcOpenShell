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

@echo off
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

:: tfk: todo remove duplication
set BOOST_VERSION=1.86.0
set BOOST_VER=%BOOST_VERSION:.=_%

set BOOST_ROOT=%DEPS_DIR%\boost_%BOOST_VER%
set BOOST_LIBRARYDIR=%BOOST_ROOT%\stage\%GEN_SHORTHAND%\lib
if not defined OCC_INCLUDE_DIR set OCC_INCLUDE_DIR=%INSTALL_DIR%\oce\include\oce
if not defined OCC_LIBRARY_DIR set OCC_LIBRARY_DIR=%INSTALL_DIR%\oce\Win%ARCH_BITS%\lib
set OPENCOLLADA_INCLUDE_DIR=%INSTALL_DIR%\OpenCOLLADA\include\opencollada
set OPENCOLLADA_LIBRARY_DIR=%INSTALL_DIR%\OpenCOLLADA\lib\opencollada
set LIBXML2_INCLUDE_DIR=%DEPS_DIR%\OpenCOLLADA\Externals\LibXML\include
set LIBXML2_LIBRARIES=%INSTALL_DIR%\OpenCOLLADA\lib\opencollada\xml.lib
set HDF5_INCLUDE_DIR=%INSTALL_DIR%\HDF5-%HDF5_VERSION%-win%ARCH_BITS%\include
set HDF5_LIBRARY_DIR=%INSTALL_DIR%\HDF5-%HDF5_VERSION%-win%ARCH_BITS%\lib
if not defined PY_VER_MAJOR_MINOR set PY_VER_MAJOR_MINOR=311
if not defined PYTHONHOME set PYTHONHOME=%INSTALL_DIR%\Python%PY_VER_MAJOR_MINOR%
set PYTHON_INCLUDE_DIR=%PYTHONHOME%\include
set PYTHON_LIBRARY=%PYTHONHOME%\libs\python%PY_VER_MAJOR_MINOR%.lib
set PYTHON_EXECUTABLE=%PYTHONHOME%\python.exe
set SWIG_DIR=%INSTALL_DIR%\swigwin
set PATH=%PATH%;%SWIG_DIR%;%PYTHONHOME%
set JSON_INCLUDE_DIR=%INSTALL_DIR%\json
if not defined ADD_COMMIT_SHA set ADD_COMMIT_SHA=Off

set CGAL_INCLUDE_DIR=%INSTALL_DIR%\cgal\include
:: set CGAL_LIBRARY_DIR=%INSTALL_DIR%\cgal\lib
set GMP_INCLUDE_DIR=%INSTALL_DIR%\mpir
set GMP_LIBRARY_DIR=%INSTALL_DIR%\mpir
set MPFR_INCLUDE_DIR=%INSTALL_DIR%\mpfr
set MPFR_LIBRARY_DIR=%INSTALL_DIR%\mpfr
set EIGEN_DIR=%INSTALL_DIR%\Eigen
set USD_INCLUDE_DIR=%INSTALL_DIR%\usd\include
set USD_LIBRARY_DIR=%INSTALL_DIR%\usd\lib
set TBB_INCLUDE_DIR=%INSTALL_DIR%\tbb\include
set TBB_LIBRARY_DIR=%INSTALL_DIR%\tbb\lib

echo.
call cecho.cmd 0 10 "Script configuration:"
echo   Generator    = %GENERATOR%
echo   Architecture = %VS_PLATFORM%
echo   Toolset      = %VS_TOOLSET%
echo   Arguments    = %ARGUMENTS%
echo.
call cecho.cmd 0 10 "Dependency Environment Variables for %PROJECT_NAME%:"
echo    BOOST_ROOT              = %BOOST_ROOT%
echo    BOOST_LIBRARYDIR        = %BOOST_LIBRARYDIR%
echo    OCC_INCLUDE_DIR         = %OCC_INCLUDE_DIR%
echo    OCC_LIBRARY_DIR         = %OCC_LIBRARY_DIR%
echo    OPENCOLLADA_INCLUDE_DIR = %OPENCOLLADA_INCLUDE_DIR%
echo    OPENCOLLADA_LIBRARY_DIR = %OPENCOLLADA_LIBRARY_DIR%
echo    LIBXML2_INCLUDE_DIR     = %LIBXML2_INCLUDE_DIR%
echo    LIBXML2_LIBRARIES       = %LIBXML2_LIBRARIES%
echo    HDF5_INCLUDE_DIR        = %HDF5_INCLUDE_DIR%
echo    HDF5_LIBRARY_DIR        = %HDF5_LIBRARY_DIR%
echo    PYTHONHOME              = %PYTHONHOME%
echo    PYTHON_INCLUDE_DIR      = %PYTHON_INCLUDE_DIR%
echo    PYTHON_LIBRARY          = %PYTHON_LIBRARY%
echo    PYTHON_EXECUTABLE       = %PYTHON_EXECUTABLE%
echo    SWIG_DIR                = %SWIG_DIR%
echo    JSON_INCLUDE_DIR        = %JSON_INCLUDE_DIR%
echo.
echo    CGAL_INCLUDE_DIR        = %CGAL_INCLUDE_DIR%
:: echo    CGAL_LIBRARY_DIR        = %CGAL_LIBRARY_DIR%
echo    GMP_INCLUDE_DIR         = %GMP_INCLUDE_DIR%
echo    GMP_LIBRARY_DIR         = %GMP_LIBRARY_DIR%
echo    MPFR_INCLUDE_DIR        = %MPFR_INCLUDE_DIR%
echo    MPFR_LIBRARY_DIR        = %MPFR_LIBRARY_DIR%
echo    EIGEN_DIR               = %EIGEN_DIR%
echo    USD_INCLUDE_DIR         = %USD_INCLUDE_DIR%
echo    USD_LIBRARY_DIR         = %USD_LIBRARY_DIR%
echo    TBB_INCLUDE_DIR         = %TBB_INCLUDE_DIR%
echo    TBB_LIBRARY_DIR         = %TBB_LIBRARY_DIR%
echo.
echo    CMAKE_INSTALL_PREFIX    = %CMAKE_INSTALL_PREFIX%
echo.

set CMAKELISTS_DIR=..\cmake
:: Delete CMakeCache.txt if command-line options were provided for this batch script.
if not (%1)==() if exist CMakeCache.txt. del /Q CMakeCache.txt
call cecho.cmd 0 13 "Running CMake for %PROJECT_NAME%."

IF NOT "%VS_TOOLSET_HOST%"=="" (
	cmake.exe %CMAKELISTS_DIR% -G %GENERATOR% -A %VS_PLATFORM% -T %VS_TOOLSET_HOST% -DCMAKE_INSTALL_PREFIX="%CMAKE_INSTALL_PREFIX%" -DBoost_NO_BOOST_CMAKE=On -DADD_COMMIT_SHA=%ADD_COMMIT_SHA% %ARGUMENTS%
) ELSE (
	cmake.exe %CMAKELISTS_DIR% -G %GENERATOR% -A %VS_PLATFORM% -DCMAKE_INSTALL_PREFIX="%CMAKE_INSTALL_PREFIX%" -DBoost_NO_BOOST_CMAKE=On -DADD_COMMIT_SHA=%ADD_COMMIT_SHA% %ARGUMENTS%
)

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
