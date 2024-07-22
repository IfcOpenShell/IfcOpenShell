@echo off

rem SETUP BLENDER-BIM LIVE DEVELOPMENT ENVIRONMENT
rem Setup blenderbim addon location below (probably just need to change "x.x" for your Blender version).
rem Put the script to the folder where IfcOpenShell git repository is located
rem (script will try to clone IfcOpenShell.git if it's not present).
SET blenderbim=%appdata%\Blender Foundation\Blender\x.x\scripts\addons\blenderbim

git clone https://github.com/IfcOpenShell/IfcOpenShell.git
cd IfcOpenShell

echo Removing the Blender add-on Python code...
rd /S /Q "%blenderbim%\core\"
rd /S /Q "%blenderbim%\tool\"
rd /S /Q "%blenderbim%\bim\"

echo Replacing them with links to the Git repository...
mklink /D "%blenderbim%\core" "%cd%\src\blenderbim\blenderbim\core"
mklink /D "%blenderbim%\tool" "%cd%\src\blenderbim\blenderbim\tool"
mklink /D "%blenderbim%\bim" "%cd%\src\blenderbim\blenderbim\bim"

echo Copy over compiled IfcOpenShell files...
copy "%blenderbim%\libs\site\packages\ifcopenshell\*_wrapper*" "%cd%\src\ifcopenshell-python\ifcopenshell\"

echo Remove the IfcOpenShell dependency...
rd /S /Q "%blenderbim%\libs\site\packages\ifcopenshell"

echo Replace them with links to the Git repository...
mklink /D "%blenderbim%\libs\site\packages\ifcopenshell" "%cd%\src\ifcopenshell-python\ifcopenshell"

echo Remove and link other IfcOpenShell utilities...
del "%blenderbim%\libs\site\packages\ifccsv.py"
del "%blenderbim%\libs\site\packages\ifcdiff.py"
del "%blenderbim%\libs\site\packages\bsdd.py"
rd /S /Q "%blenderbim%\libs\site\packages\bcf"
rd /S /Q "%blenderbim%\libs\site\packages\ifc4d"
rd /S /Q "%blenderbim%\libs\site\packages\ifc5d"
rd /S /Q "%blenderbim%\libs\site\packages\ifccityjson"
rd /S /Q "%blenderbim%\libs\site\packages\ifcclash"
rd /S /Q "%blenderbim%\libs\site\packages\ifcpatch"
rd /S /Q "%blenderbim%\libs\site\packages\ifctester"
rd /S /Q "%blenderbim%\libs\site\packages\ifcfm"
rd /S /Q "%blenderbim%\libs\desktop"

mklink "%blenderbim%\libs\site\packages\ifccsv.py" "%cd%\src\ifccsv\ifccsv.py"
mklink "%blenderbim%\libs\site\packages\ifcdiff.py" "%cd%\src\ifcdiff\ifcdiff.py"
mklink "%blenderbim%\libs\site\packages\bsdd.py" "%cd%\src\bsdd\bsdd.py"
mklink /D "%blenderbim%\libs\site\packages\bcf" "%cd%\src\bcf\src\bcf"
mklink /D "%blenderbim%\libs\site\packages\ifc4d" "%cd%\src\ifc4d\ifc4d"
mklink /D "%blenderbim%\libs\site\packages\ifc5d" "%cd%\src\ifc5d\ifc5d"
mklink /D "%blenderbim%\libs\site\packages\ifccityjson" "%cd%\src\ifccityjson\ifccityjson"
mklink /D "%blenderbim%\libs\site\packages\ifcclash" "%cd%\src\ifcclash\ifcclash"
mklink /D "%blenderbim%\libs\site\packages\ifcpatch" "%cd%\src\ifcpatch\ifcpatch"
mklink /D "%blenderbim%\libs\site\packages\ifctester" "%cd%\src\ifctester\ifctester"
mklink /D "%blenderbim%\libs\site\packages\ifcfm" "%cd%\src\ifcfm\ifcfm"
mklink /D "%blenderbim%\libs\desktop" "%cd%\src\blenderbim\blenderbim\libs\desktop"

echo Manually downloading some third party dependencies...
curl https://raw.githubusercontent.com/jsGanttImproved/jsgantt-improved/master/dist/jsgantt.js -o "%blenderbim%\bim\data\gantt\jsgantt.js"
curl https://raw.githubusercontent.com/jsGanttImproved/jsgantt-improved/master/dist/jsgantt.css -o "%blenderbim%\bim\data\gantt\jsgantt.css"
curl -L https://github.com/BrickSchema/Brick/releases/download/nightly/Brick.ttl -o "%blenderbim%\bim\schema\Brick.ttl"

pause
