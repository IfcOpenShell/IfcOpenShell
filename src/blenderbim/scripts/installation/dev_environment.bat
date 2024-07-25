@echo off

echo SETUP BLENDERBIM ADD-ON LIVE DEVELOPMENT ENVIRONMENT
echo Update BLENDER, BLENDER_VERSION, PYTHON_VERSION, BBIM_REPO, BLENDER_USER_NAME in the script bellow.
echo Put the script at the root of your IfcOpenShell git repository
echo This script needs to be run as administrator (to create symbolic links)
echo Make sure you have followed these steps before proceeding :)

pause

SET BLENDER_VERSION=4.2
SET PYTHON_VERSION=3.11
SET BBIM_REPO=user_default
rem Can be useful e.g. if you're running script from administrator account
rem and need to setup dev environment for some other user.
SET BLENDER_USER_NAME=%USERNAME%

SET BLENDER=%HOMEDRIVE%\Users\%BLENDER_USER_NAME%\AppData\Roaming\Blender Foundation\Blender\%BLENDER_VERSION%
SET BLENDER_LOCAL=%BLENDER%\extensions\.local\lib\python%PYTHON_VERSION%\site-packages
SET BLENDERBIM=%BLENDER_LOCAL%\blenderbim
SET BLENDER_EXT=%BLENDER%\extensions\%BBIM_REPO%\blenderbim

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
mklink /D "%BLENDER_LOCAL%\bcf" "%CD%\src\bcf\bcf"
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
