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

:: This batch file expects CMake generator as %1 and build configuration type as %2. If not provided,
:: a deduced generator will be used for %1 and BUILD_CFG_DEFAULT for %2 (both set in vs-cfg.cmd)
:: Possible extra parameters are passed for the MSBuild call.

@echo off
set PROJECT_NAME=IfcOpenShell
echo.

:: Enable the delayed environment variable expansion needed in VSConfig.cmd.
setlocal EnableDelayedExpansion
set IFCOS_PAUSE_ON_ERROR=

:: Read cached variables from the most recently modified BuildDepsCache.txt.
for /f "tokens=*" %%f in ('dir BuildDepsCache-*.txt /o:-n /t:a /b') do (
    for /f "delims== tokens=1,2" %%G in (%%f) do set %%G=%%H
)

set GENERATOR=%1
if (%1)==() (
    if not defined GEN_SHORTHAND (
        echo BuildDepsCache file does and/or GEN_SHORTHAND missing from it. Run build-deps.cmd to create it.
        set IFCOS_PAUSE_ON_ERROR=pause
        goto :Error
    )
    set GENERATOR=%GEN_SHORTHAND%
    echo Generator not passed, but GEN_SHORTHAND=!GENERATOR! read from BuildDepsCache
    echo.
)
call vs-cfg.cmd %GENERATOR%
IF NOT %ERRORLEVEL%==0 GOTO :Error
call build-type-cfg.cmd %2
IF NOT %ERRORLEVEL%==0 GOTO :Error

echo.
if not defined IFCOS_NUM_BUILD_PROCS set IFCOS_NUM_BUILD_PROCS=%NUMBER_OF_PROCESSORS%
call cecho.cmd 0 13 "* IFCOS_NUM_BUILD_PROCS`t= %IFCOS_NUM_BUILD_PROCS%"
echo.

call cecho.cmd 0 13 "Building %VS_PLATFORM% %BUILD_CFG% %PROJECT_NAME%"
cmake --build ..\%BUILD_DIR% -- /nologo /m:%IFCOS_NUM_BUILD_PROCS% /p:Platform=%VS_PLATFORM% /p:Configuration=%BUILD_CFG% ^
    %3 %4 %5 %6 %7 %8 %9
IF NOT %ERRORLEVEL%==0 GOTO :Error

echo.
call cecho.cmd 0 10 "%VS_PLATFORM% %BUILD_CFG% %PROJECT_NAME% build finished."
set IFCOS_SCRIPT_RET=0
goto :End

:Error
echo.
call "%~dp0\utils\cecho.cmd" 0 12 "%VS_PLATFORM% %BUILD_CFG% %PROJECT_NAME% build failed!"
%IFCOS_PAUSE_ON_ERROR%
set IFCOS_SCRIPT_RET=1

:End
exit /b %IFCOS_SCRIPT_RET%
