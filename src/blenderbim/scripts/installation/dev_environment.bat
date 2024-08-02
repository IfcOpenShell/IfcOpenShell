@echo off

echo SETUP BLENDERBIM ADD-ON LIVE DEVELOPMENT ENVIRONMENT
echo Update REPO_PATH, BLENDER_PATH, PACKAGE_PATH, BLENDERBIM_PATH in the script below.
echo This script needs to be run as administrator (to create symbolic links)
echo Make sure you have followed these steps before proceeding :)

pause

SET REPO_PATH=%HOMEDRIVE%\Users\%USERNAME%\Where\Your\Git\Repository\Is\Cloned\IfcOpenShell
SET BLENDER_PATH=%HOMEDRIVE%\Users\%USERNAME%\AppData\Roaming\Blender Foundation\Blender\4.2
SET PACKAGE_PATH=%BLENDER_PATH%\extensions\.local\lib\python3.11\site-packages
SET BLENDERBIM_PATH=%BLENDER_PATH%\extensions\user_default\blenderbim

echo Changing to the Git repository directory...
cd %REPO_PATH%

echo Copy over compiled IfcOpenShell files...
copy "%PACKAGE_PATH%\ifcopenshell\*_wrapper*" "%CD%\src\ifcopenshell-python\ifcopenshell\"

echo Remove extension and link to Git...
del "%BLENDERBIM_PATH%\__init__.py"
rd /S /Q "%PACKAGE_PATH%\blenderbim"
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

mklink "%BLENDERBIM_PATH%\__init__.py" "%CD%\src\blenderbim\blenderbim\__init__.py"
mklink /D "%PACKAGE_PATH%\blenderbim" "%CD%\src\blenderbim\blenderbim"
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
curl https://raw.githubusercontent.com/jsGanttImproved/jsgantt-improved/master/dist/jsgantt.js -o "%PACKAGE_PATH%\blenderbim\bim\data\gantt\jsgantt.js"
curl https://raw.githubusercontent.com/jsGanttImproved/jsgantt-improved/master/dist/jsgantt.css -o "%PACKAGE_PATH%\blenderbim\bim\data\gantt\jsgantt.css"
curl -L https://github.com/BrickSchema/Brick/releases/download/nightly/Brick.ttl -o "%PACKAGE_PATH%\blenderbim\bim\schema\Brick.ttl"

pause
