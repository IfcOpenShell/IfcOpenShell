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

for /f "tokens=2,* delims= " %%a in ("%*") do set ALL_BUT_FIRST_TWO=%%b

:: Use "yes" trick to break the pause in build-deps.cmd
echo y>y.txt
call .\build-deps %1 %2<y.txt
if not %ERRORLEVEL%==0 goto :EOF
del .\y.txt
call .\run-cmake %1 %ALL_BUT_FIRST_TWO%
if not %ERRORLEVEL%==0 goto :EOF
call .\build-ifcopenshell %1 %2
ECHO %ERRORLEVEL%
if not %ERRORLEVEL%==0 goto :EOF
call .\install-ifcopenshell %1 %2
