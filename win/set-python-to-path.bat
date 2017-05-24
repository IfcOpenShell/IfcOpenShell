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

:: Pass x86 or x64 as %1, if not specified x64 assumed.

@echo off
set TARGET_ARCH=%1
if "%TARGET_ARCH%"=="" set TARGET_ARCH=x64
if not exist "%~dp0BuildDepsCache-%TARGET_ARCH%.txt". (
    echo %~dp0BuildDepsCache-%TARGET_ARCH%.txt does not exist
    goto :EOF
)
for /f "usebackq delims== tokens=1,2" %%G in ("%~dp0BuildDepsCache-%TARGET_ARCH%.txt") do set %%G=%%H
if not defined PYTHONHOME (
    echo PYTHONHOME not defined
    goto :EOF
)

echo %PYTHONHOME% set to PATH
set PATH=%PYTHONHOME%;%PATH%
