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

:: Read cached variables from the most recently modified BuildDepsCache.txt.
for /f "tokens=*" %%f in ('dir BuildDepsCache-*.txt /o:-n /t:a /b') do (
    for /f "delims== tokens=1,2" %%G in (%%f) do set %%G=%%H
)

set GENERATOR=%1
if (%1)==() (
    if not defined GEN_SHORTHAND (
        echo BuildDepsCache file does not exist and/or GEN_SHORTHAND missing from it. Run build-deps.cmd to create it.
        set IFCOS_PAUSE_ON_ERROR=pause
        goto :Error
    )
    set GENERATOR=%GEN_SHORTHAND%
    echo Generator not passed, but GEN_SHORTHAND=!GENERATOR! read from BuildDepsCache
    echo.
)
call vs-cfg.cmd %GENERATOR%
IF NOT %ERRORLEVEL%==0 GOTO :Error
:: As CMake options are typically of format -DSOMETHING:BOOL=ON or -DSOMETHING=1, i.e. they contain an equal sign,
:: they will mess up the batch file argument parsing if the arguments are passed on by splitting them %2 %3 %4 %5
:: %6 %7 %8 %9. Work around that, http://scripts.dragon-it.co.uk/scripts.nsf/docs/batch-search-replace-substitute
if not (%1)==() (
    set ARGUMENTS=%*
    call set ARGUMENTS=%%ARGUMENTS:%1=%%
)

pushd ..
set CMAKE_INSTALL_PREFIX=%CD%\installed-vs%VS_VER%-%TARGET_ARCH%
popd

IF NOT EXIST ..\%BUILD_DIR%. mkdir ..\%BUILD_DIR%
pushd ..\%BUILD_DIR%

set BOOST_ROOT=%DEPS_DIR%\boost
REM set BOOST_INCLUDEDIR=%DEPS_DIR%\boost\boost
set BOOST_LIBRARYDIR=%DEPS_DIR%\boost\stage\vs%VS_VER%-%VS_PLATFORM%\lib
set ICU_INCLUDE_DIR=%INSTALL_DIR%\icu\include
set ICU_LIBRARY_DIR=%INSTALL_DIR%\icu\lib
if not defined OCC_INCLUDE_DIR set OCC_INCLUDE_DIR=%INSTALL_DIR%\oce\include\oce
if not defined OCC_LIBRARY_DIR set OCC_LIBRARY_DIR=%INSTALL_DIR%\oce\Win%ARCH_BITS%\lib
set OPENCOLLADA_INCLUDE_DIR=%INSTALL_DIR%\OpenCOLLADA\include\opencollada
set OPENCOLLADA_LIBRARY_DIR=%INSTALL_DIR%\OpenCOLLADA\lib\opencollada
if not defined PY_VER_MAJOR_MINOR set PY_VER_MAJOR_MINOR=34
if not defined PYTHONHOME set PYTHONHOME=%INSTALL_DIR%\Python%PY_VER_MAJOR_MINOR%
set PYTHON_INCLUDE_DIR=%PYTHONHOME%\include
set PYTHON_LIBRARY=%PYTHONHOME%\libs\python%PY_VER_MAJOR_MINOR%.lib
set PYTHON_EXECUTABLE=%PYTHONHOME%\python.exe
set SWIG_DIR=%INSTALL_DIR%\swigwin
set PATH=%PATH%;%SWIG_DIR%;%PYTHONHOME%
set THREEDS_MAX_SDK_HOME=C:\Program Files\Autodesk\3ds Max 2016 SDK\maxsdk

echo.
call cecho.cmd 0 10 "Script configuration:"
echo   Generator = %GENERATOR%
echo   Arguments = %ARGUMENTS%
echo.
call cecho.cmd 0 10 "Dependency Environment Variables for %PROJECT_NAME%:"
echo    BOOST_ROOT              = %BOOST_ROOT%
echo    BOOST_LIBRARYDIR        = %BOOST_LIBRARYDIR%
echo    ICU_INCLUDE_DIR         = %ICU_INCLUDE_DIR%
echo    ICU_LIBRARY_DIR         = %ICU_LIBRARY_DIR%
echo    OCC_INCLUDE_DIR         = %OCC_INCLUDE_DIR%
echo    OCC_LIBRARY_DIR         = %OCC_LIBRARY_DIR%
echo    OPENCOLLADA_INCLUDE_DIR = %OPENCOLLADA_INCLUDE_DIR%
echo    OPENCOLLADA_LIBRARY_DIR = %OPENCOLLADA_LIBRARY_DIR%
echo    PYTHONHOME              = %PYTHONHOME%
echo    PYTHON_INCLUDE_DIR      = %PYTHON_INCLUDE_DIR%
echo    PYTHON_LIBRARY          = %PYTHON_LIBRARY%
echo    PYTHON_EXECUTABLE       = %PYTHON_EXECUTABLE%
echo    SWIG_DIR                = %SWIG_DIR%
echo    THREEDS_MAX_SDK_HOME    = %THREEDS_MAX_SDK_HOME%
echo.
echo    CMAKE_INSTALL_PREFIX    = %CMAKE_INSTALL_PREFIX%
echo.

set CMAKELISTS_DIR=..\cmake
:: Delete CMakeCache.txt if command-line options were provided for this batch script.
if not (%1)==() if exist CMakeCache.txt. del /Q CMakeCache.txt
call cecho.cmd 0 13 "Running CMake for %PROJECT_NAME%."
cmake.exe %CMAKELISTS_DIR% -G %GENERATOR% -DCMAKE_INSTALL_PREFIX="%CMAKE_INSTALL_PREFIX%" %ARGUMENTS%
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
