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

:: Enable the delayed environment variable expansion needed in vs-cfg.cmd.
setlocal EnableDelayedExpansion

:: Read Python related variables from BuildDepsCache.txt
for /f "delims== tokens=1,2" %%G in (BuildDepsCache.txt) do set %%G=%%H

call vs-cfg.cmd %1

pushd ..
set CMAKE_INSTALL_PREFIX=%CD%\installed-vs%VS_VER%-%TARGET_ARCH%
popd

set BUILD_DIR=build-vs%VS_VER%-%TARGET_ARCH%
IF NOT EXIST ..\%BUILD_DIR%. mkdir ..\%BUILD_DIR%
pushd ..\%BUILD_DIR%

set BOOST_ROOT=%DEPS_DIR%\boost
REM set BOOST_INCLUDEDIR=%DEPS_DIR%\boost
set BOOST_LIBRARYDIR=%DEPS_DIR%\boost\stage\vs%VS_VER%-%VS_PLATFORM%\lib
set ICU_INCLUDE_DIR=%INSTALL_DIR%\icu\include
set ICU_LIBRARY_DIR=%INSTALL_DIR%\icu\lib
set OCC_INCLUDE_DIR=%INSTALL_DIR%\oce\include\oce
set OCC_LIBRARY_DIR=%INSTALL_DIR%\oce\Win%ARCH_BITS%\lib
set OPENCOLLADA_INCLUDE_DIR=%INSTALL_DIR%\OpenCOLLADA\include\opencollada
set OPENCOLLADA_LIBRARY_DIR=%INSTALL_DIR%\OpenCOLLADA\lib\opencollada
if "%PY_VER_MAJOR_MINOR%"=="" set PY_VER_MAJOR_MINOR=34
if "%PYTHONPATH%"=="" set PYTHONPATH=%INSTALL_DIR%\Python%PY_VER_MAJOR_MINOR%
set PYTHON_INCLUDE_DIR=%PYTHONPATH%\include
set PYTHON_LIBRARY=%PYTHONPATH%\libs\python%PY_VER_MAJOR_MINOR%.lib
set SWIG_DIR=%INSTALL_DIR%\swigwin
set PATH=%PATH%;%SWIG_DIR%;%PYTHONPATH%
:: TODO 3ds Max SDK?

echo.
cecho {0A}Script configuration:{# #}{\n}
echo   CMake Generator = %GENERATOR%
echo   All arguments   = %*
echo.
cecho {0A}Dependency Environment Variables for %PROJECT_NAME%:{# #}{\n}
echo    BOOST_ROOT              = %BOOST_ROOT%
REM echo    BOOST_INCLUDEDIR = %BOOST_INCLUDEDIR%
echo    BOOST_LIBRARYDIR        = %BOOST_LIBRARYDIR%
echo    ICU_INCLUDE_DIR         = %ICU_INCLUDE_DIR%
echo    ICU_LIBRARY_DIR         = %ICU_LIBRARY_DIR%
echo    OCC_INCLUDE_DIR         = %OCC_INCLUDE_DIR%
echo    OCC_LIBRARY_DIR         = %OCC_LIBRARY_DIR%
echo    OPENCOLLADA_INCLUDE_DIR = %OPENCOLLADA_INCLUDE_DIR%
echo    OPENCOLLADA_LIBRARY_DIR = %OPENCOLLADA_LIBRARY_DIR%
echo    PYTHONPATH              = %PYTHONPATH%
echo    PYTHON_INCLUDE_DIR      = %PYTHON_INCLUDE_DIR%
echo    PYTHON_LIBRARY          = %PYTHON_LIBRARY%
echo    SWIG_DIR                = %SWIG_DIR%
echo.
echo    CMAKE_INSTALL_PREFIX    = %CMAKE_INSTALL_PREFIX%
echo.

set CMAKELISTS_DIR=..\cmake
REM IF NOT EXIST %PROJECT_NAME%.sln. (
    IF EXIST CMakeCache.txt. del /Q CMakeCache.txt
    cecho {0D}Running CMake for %PROJECT_NAME%.{# #}{\n}
    IF "%2"=="" (
        REM No extra arguments provided, trust that GENERATOR is set properly.
        cmake.exe %CMAKELISTS_DIR% -G %GENERATOR% -DCMAKE_INSTALL_PREFIX="%CMAKE_INSTALL_PREFIX%"
    ) ELSE (
        REM Extra arguments has been provided. As CMake options are typically of format -DSOMETHING:BOOL=ON,
        REM i.e. they contain an equal sign, they will mess up the batch file argument parsing if the arguments are passed on
        REM by splitting them %2 %3 %4 %5 %6 %7 %8 %9. In the extra argument case trust that user has provided the generator
        REM as the first argument as pass all arguments as is by using %*.
        cmake.exe %CMAKELISTS_DIR% -G %*
    )
    IF NOT %ERRORLEVEL%==0 GOTO :Error
REM ) ELSE (
    REM cecho {0A}%PROJECT_NAME%.sln exists. Skipping CMake call for %PROJECT_NAME%.{# #}{\n}
    REM cecho {0A}Delete %CD%\%PROJECT_NAME%.sln to trigger a CMake rerun.{# #}{\n}
REM )
echo.

goto :Finish

:Error
echo.
cecho {0C}An error occurred! Aborting!{# #}{\n}
goto :Finish

:Finish
popd
set PATH=%ORIGINAL_PATH%
endlocal
