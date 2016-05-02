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

@echo off

setlocal EnableDelayedExpansion

call vs-cfg.cmd %1
if not %ERRORLEVEL%==0 GOTO :Error
:: Use "yes" trick to break the pause in build-deps.cmd
echo y | call .\build-deps %1 %2
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
