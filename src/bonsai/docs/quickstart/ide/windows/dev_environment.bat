@echo off

setlocal enabledelayedexpansion


rem ADAPT setting REPO_PATH to use custom path for IfcOpenShell repository.
rem Otherwise by default it is assumed script is executed from IfcOpenShell directory.
SET REPO_PATH=%HOMEDRIVE%\Users\%USERNAME%\Documents\bonsaiDevel\IfcOpenShell
SET BLENDER_PATH=%HOMEDRIVE%\Users\%USERNAME%\AppData\Roaming\Blender Foundation\Blender\4.2
SET PACKAGE_PATH=%BLENDER_PATH%\extensions\.local\lib\python3.11\site-packages
SET BONSAI_PATH=%BLENDER_PATH%\extensions\raw_githubusercontent_com\bonsai

echo SETUP BONSAI ADD-ON LIVE DEVELOPMENT ENVIRONMENT
echo Update REPO_PATH, BLENDER_PATH, PACKAGE_PATH, BONSAI_PATH in the script above.
echo This script needs to be run as administrator (to create symbolic links)
echo Make sure you have followed these steps before proceeding :)
echo.
echo Currently set paths:
if not defined REPO_PATH (
    echo REPO_PATH is not set, assuming we're already in IfcOpenShell directory.
    set REPO_PATH=%cd%
)
rem Print summary of paths
echo.
echo Please review if the following is right:
echo PWD: %CD%
echo REPO PATH (.....\IfcOpenshell): %REPO_PATH%
echo BLENDER PATH: %BLENDER_PATH%
echo PACKAGE PATH (.....\extensions\.local\lib\python3.11\site-packages): %PACKAGE_PATH%
echo BONSAI PATH (.....\extensions\raw_githubusercontent_com\bonsai): %BONSAI_PATH%
echo.
rem Prompt user to continue
pause


echo Changing to the Git repository directory...
cd %REPO_PATH%

rem Add files that need to be ignored in push to GiHub (.gitignore)
set "FILE=.gitignore"
set "STRING=*.so"

rem Check if the file exists and contains the string
if not exist "%FILE%" (
    echo %STRING% >> "%FILE%"
    echo "%FILE%" does not exist
    echo Added '%STRING%' to %FILE%
) else (
    findstr /L "%STRING%" "%FILE%" >nul
    if errorlevel 1 (
        echo %STRING% >> "%FILE%"
        echo %STRING% not found in %FILE%
        echo Added %STRING% to %FILE%
    ) else (
        echo '%STRING%' already exists in %FILE%
    )
)

echo Copy over compiled IfcOpenShell files...
copy "%PACKAGE_PATH%\ifcopenshell\*_wrapper*" "%CD%\src\ifcopenshell-python\ifcopenshell\"

echo Remove extension and link to Git...
del "%BONSAI_PATH%\__init__.py"
rd /S /Q "%PACKAGE_PATH%\bonsai"
rd /S /Q "%PACKAGE_PATH%\ifcopenshell"
del "%PACKAGE_PATH%\ifccsv.py"
del "%PACKAGE_PATH%\ifcdiff.py"
del "%PACKAGE_PATH%\bsdd.py"
rd /S /Q "%PACKAGE_PATH%\bcf"
rd /S /Q "%PACKAGE_PATH%\ifc4d"
rd /S /Q "%PACKAGE_PATH%\ifc5d"
rd /S /Q "%PACKAGE_PATH%\ifccityjson"
rd /S /Q "%PACKAGE_PATH%\ifcclash"
rd /S /Q "%PACKAGE_PATH%\ifcpatch"
rd /S /Q "%PACKAGE_PATH%\ifctester"
rd /S /Q "%PACKAGE_PATH%\ifcfm"

mklink "%BONSAI_PATH%\__init__.py" "%CD%\src\bonsai\bonsai\__init__.py"
mklink /D "%PACKAGE_PATH%\bonsai" "%CD%\src\bonsai\bonsai"
mklink /D "%PACKAGE_PATH%\ifcopenshell" "%CD%\src\ifcopenshell-python\ifcopenshell"
mklink "%PACKAGE_PATH%\ifccsv.py" "%CD%\src\ifccsv\ifccsv.py"
mklink "%PACKAGE_PATH%\ifcdiff.py" "%CD%\src\ifcdiff\ifcdiff.py"
mklink "%PACKAGE_PATH%\bsdd.py" "%CD%\src\bsdd\bsdd.py"
mklink /D "%PACKAGE_PATH%\bcf" "%CD%\src\bcf\bcf"
mklink /D "%PACKAGE_PATH%\ifc4d" "%CD%\src\ifc4d\ifc4d"
mklink /D "%PACKAGE_PATH%\ifc5d" "%CD%\src\ifc5d\ifc5d"
mklink /D "%PACKAGE_PATH%\ifccityjson" "%CD%\src\ifccityjson\ifccityjson"
mklink /D "%PACKAGE_PATH%\ifcclash" "%CD%\src\ifcclash\ifcclash"
mklink /D "%PACKAGE_PATH%\ifcpatch" "%CD%\src\ifcpatch\ifcpatch"
mklink /D "%PACKAGE_PATH%\ifctester" "%CD%\src\ifctester\ifctester"
mklink /D "%PACKAGE_PATH%\ifcfm" "%CD%\src\ifcfm\ifcfm"

echo Manually downloading some third party dependencies...
curl https://raw.githubusercontent.com/jsGanttImproved/jsgantt-improved/master/dist/jsgantt.js -o "%PACKAGE_PATH%\bonsai\bim\data\gantt\jsgantt.js"
curl https://raw.githubusercontent.com/jsGanttImproved/jsgantt-improved/master/dist/jsgantt.css -o "%PACKAGE_PATH%\bonsai\bim\data\gantt\jsgantt.css"
IF NOT EXIST "%PACKAGE_PATH%\bonsai\bim\schema" mkdir "%PACKAGE_PATH%\bonsai\bim\schema"
curl -L https://github.com/BrickSchema/Brick/releases/download/nightly/Brick.ttl -o "%PACKAGE_PATH%\bonsai\bim\schema\Brick.ttl"


pause