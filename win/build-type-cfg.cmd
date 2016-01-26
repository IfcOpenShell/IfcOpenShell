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
::::::::::::::::::::::::::::::::::::::::::::::::::::::: ::::::::::::::::::::::::::

:: This script initializes various CMake build configuration type related variables.
:: This batch file expects CMake build configuration type as %1.

@echo off

:: Set up variables depending on the used build configuration type.
set BUILD_CFG=%1

:: The default build types provided by CMake
set BUILD_CFG_MINSIZEREL=MinSizeRel
set BUILD_CFG_RELEASE=Release
set BUILD_CFG_RELWITHDEBINFO=RelWithDebInfo
set BUILD_CFG_DEBUG=Debug
set BUILD_CFG_DEFAULT=%BUILD_CFG_RELWITHDEBINFO%

IF "!BUILD_CFG!"=="" (
    set BUILD_CFG=%BUILD_CFG_DEFAULT%
    call utils\cecho.cmd 0 14 "%~nx0: Warning: BUILD_CFG not specified - using the default %BUILD_CFG_DEFAULT%"
)
IF NOT !BUILD_CFG!==%BUILD_CFG_MINSIZEREL% IF NOT !BUILD_CFG!==%BUILD_CFG_RELEASE% (
IF NOT !BUILD_CFG!==%BUILD_CFG_RELWITHDEBINFO% IF NOT !BUILD_CFG!==%BUILD_CFG_DEBUG% (
    call utils\cecho.cmd 0 12 "%~nx0: Invalid or unsupported CMake build configuration type passed: !BUILD_CFG!. Cannot proceed."
    exit /b 1
))

:: DEBUG_OR_RELEASE and DEBUG_OR_RELEASE_LOWERCASE are "Debug" and "debug" for Debug build and "Release" and
:: "release" for all of the Release variants.
:: POSTFIX_D, POSTFIX_UNDERSCORE_D and POSTFIX_UNDERSCORE_DEBUG are helpers for performing file copies and
:: checking for existence of files. In release build these variables are empty.
set DEBUG_OR_RELEASE=Release
set DEBUG_OR_RELEASE_LOWERCASE=release
set POSTFIX_D=
set POSTFIX_UNDERSCORE_D=
set POSTFIX_UNDERSCORE_DEBUG=
IF %BUILD_CFG%==Debug (
    set DEBUG_OR_RELEASE=Debug
    set DEBUG_OR_RELEASE_LOWERCASE=debug
    set POSTFIX_D=d
    set POSTFIX_UNDERSCORE_D=_d
    set POSTFIX_UNDERSCORE_DEBUG=_debug
)
