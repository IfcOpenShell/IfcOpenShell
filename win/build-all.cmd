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

:: The first argument is assumed to be a CMake generator and it is passed for build-deps, run-cmake, build-ifcopenshell,
:: and install-ifcopenshell. The second argument is assumed to be a build configuration type and it is passed for build-deps,
:: build-ifcopenshell and install-ifcopenshell. The rest of the arguments are passed for run-cmake.
:: Usage example for doing an optimized vs2015-x64 build with debug information and using IFC 4:
:: > build-all.cmd vs2015-x64 RelWithDebInfo -DUSE_IFC4=1 -DENABLE_BUILD_OPTIMIZATIONS=1

@if not defined ECHO_ON ( echo off )

setlocal EnableDelayedExpansion

call vs-cfg.cmd %1
if not %ERRORLEVEL%==0 GOTO :Error

call cecho.cmd 0 12 "WARNING: build-all.cmd is deprecated since 11 Sep 2026 and will be removed very shortly."
call cecho.cmd 0 12 "Use `python build-all.py` instead. It's intended to be a drop-in replacement, so exactly the same args apply,"
call cecho.cmd 0 12 "except CMake args now need to be passed after `"--`", e.g. `python build-all.py vs2022-x64 -- -DGLTF_SUPPORT=ON`."
echo.

:: Use "yes" trick to break the pause in build-deps.py
echo y | python build-deps.py %1 %2
if not %ERRORLEVEL%==0 goto :EOF
:: Same trick as in run-cmake.bat
set ARGUMENTS=%*
if not (%1)==() call set ARGUMENTS=%%ARGUMENTS:%1=%%
if not (%2)==() call set ARGUMENTS=%%ARGUMENTS:%2=%%
call .\run-cmake %1 %ARGUMENTS%
if not %ERRORLEVEL%==0 goto :EOF
call .\build-ifcopenshell %1 %2
ECHO %ERRORLEVEL%
if not %ERRORLEVEL%==0 goto :EOF
call .\install-ifcopenshell %1 %2
