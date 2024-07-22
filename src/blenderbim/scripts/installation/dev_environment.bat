@echo off

rem SETUP BLENDER-BIM LIVE DEVELOPMENT ENVIRONMENT
rem Update BLENDER_VERSION, PYTHON_VERSION, BBIM_REPO in the script bellow.
rem Put the script to the folder where IfcOpenShell git repository is located
rem (script will try to clone IfcOpenShell.git if it's not present).
SET BLENDER_VERSION=4.2
SET PYTHON_VERSION=3.11
SET BBIM_REPO=user_default

SET BLENDER=%appdata%\Blender Foundation\Blender\%BLENDER_VERSION%
SET BLENDER_LOCAL=%BLENDER%\extensions\.local\lib\python%PYTHON_VERSION%\site-packages
SET BLENDERBIM=%BLENDER_LOCAL%\blenderbim
SET BLENDER_EXT=%BLENDER%\extensions\%BBIM_REPO%\blenderbim

git clone https://github.com/IfcOpenShell/IfcOpenShell.git
cd IfcOpenShell

echo Removing the Blender add-on Python code...
del "%BLENDER_EXT%\__init__.py"
rd /S /Q "%BLENDERBIM%"

echo Replacing them with links to the Git repository...
mklink "%BLENDER_EXT%\__init__.py" "%CD%\src\blenderbim\blenderbim\__init__.py"
mklink /D "%BLENDERBIM%" "%CD%\src\blenderbim\blenderbim"

echo Copy over compiled IfcOpenShell files...
copy "%BLENDER_LOCAL%\ifcopenshell\*_wrapper*" "%CD%\src\ifcopenshell-python\ifcopenshell\"

echo Remove the IfcOpenShell dependency...
rd /S /Q "%BLENDER_LOCAL%\ifcopenshell"

echo Replace them with links to the Git repository...
mklink /D "%BLENDER_LOCAL%\ifcopenshell" "%CD%\src\ifcopenshell-python\ifcopenshell"

echo Remove and link other IfcOpenShell utilities...
del "%BLENDER_LOCAL%\ifccsv.py"
del "%BLENDER_LOCAL%\ifcdiff.py"
del "%BLENDER_LOCAL%\bsdd.py"
rd /S /Q "%BLENDER_LOCAL%\bcf"
rd /S /Q "%BLENDER_LOCAL%\ifc4d"
rd /S /Q "%BLENDER_LOCAL%\ifc5d"
rd /S /Q "%BLENDER_LOCAL%\ifccityjson"
rd /S /Q "%BLENDER_LOCAL%\ifcclash"
rd /S /Q "%BLENDER_LOCAL%\ifcpatch"
rd /S /Q "%BLENDER_LOCAL%\ifctester"
rd /S /Q "%BLENDER_LOCAL%\ifcfm"

mklink "%BLENDER_LOCAL%\ifccsv.py" "%CD%\src\ifccsv\ifccsv.py"
mklink "%BLENDER_LOCAL%\ifcdiff.py" "%CD%\src\ifcdiff\ifcdiff.py"
mklink "%BLENDER_LOCAL%\bsdd.py" "%CD%\src\bsdd\bsdd.py"
mklink /D "%BLENDER_LOCAL%\bcf" "%CD%\src\bcf\src\bcf"
mklink /D "%BLENDER_LOCAL%\ifc4d" "%CD%\src\ifc4d\ifc4d"
mklink /D "%BLENDER_LOCAL%\ifc5d" "%CD%\src\ifc5d\ifc5d"
mklink /D "%BLENDER_LOCAL%\ifccityjson" "%CD%\src\ifccityjson\ifccityjson"
mklink /D "%BLENDER_LOCAL%\ifcclash" "%CD%\src\ifcclash\ifcclash"
mklink /D "%BLENDER_LOCAL%\ifcpatch" "%CD%\src\ifcpatch\ifcpatch"
mklink /D "%BLENDER_LOCAL%\ifctester" "%CD%\src\ifctester\ifctester"
mklink /D "%BLENDER_LOCAL%\ifcfm" "%CD%\src\ifcfm\ifcfm"

echo Manually downloading some third party dependencies...
curl https://raw.githubusercontent.com/jsGanttImproved/jsgantt-improved/master/dist/jsgantt.js -o "%BLENDERBIM%\bim\data\gantt\jsgantt.js"
curl https://raw.githubusercontent.com/jsGanttImproved/jsgantt-improved/master/dist/jsgantt.css -o "%BLENDERBIM%\bim\data\gantt\jsgantt.css"
curl -L https://github.com/BrickSchema/Brick/releases/download/nightly/Brick.ttl -o "%BLENDERBIM%\bim\schema\Brick.ttl"

pause
