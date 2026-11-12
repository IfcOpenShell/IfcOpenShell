
Example of building examples outside of the IfcOpenShell build tree.

```powershell
$IFCOPENSHELL_ROOT="L:\Projects\Github\IfcOpenShell"
$PREFIX_PATH="$IFCOPENSHELL_ROOT\_deps\boost_1_86_0\stage\vs2022-x64"
$PREFIX_PATH+=";$IFCOPENSHELL_ROOT\_installed-vs2022-x64"
$PREFIX_PATH+=";$IFCOPENSHELL_ROOT\_deps-vs2022-x64-installed\rocksdb"
$PREFIX_PATH+=";$IFCOPENSHELL_ROOT\_deps-vs2022-x64-installed\zstd"
$PREFIX_PATH+=";L:\Software\usr\libxml2"

# + Support for IfcHouse and IfcAlignment examples.
$PREFIX_PATH+=";L:\Software\usr\eigen-3.3.9"
$PREFIX_PATH+=";L:\Projects\Github\IfcOpenShell\_deps-vs2022-x64-installed\cgal"
$PREFIX_PATH+=";L:\Projects\Github\IfcOpenShell\_deps-vs2022-x64-installed\mpir"
$PREFIX_PATH+=";L:\Projects\Github\IfcOpenShell\_deps-vs2022-x64-installed\mpfr"
$PREFIX_PATH+=";L:\Projects\Github\IfcOpenShell\_deps-vs2022-x64-installed\opencascade-7.8.1-new-layout"

cmake .. -G Ninja -DCMAKE_PREFIX_PATH="$PREFIX_PATH" -DCMAKE_BUILD_TYPE=Release
ninja -v
./IfcParseExamples.exe "../IfcParseExamples_test.ifc"
# Scanning file...
# Done scanning file
# Done resolving references
# Found 3 elements in ..\IfcParseExamples_test.ifc:
# #182=IfcBuildingElementPart('0fmaoBJgz0kPBavO$EJkPn',#181,'Cube',$,$,#193,#183,$)
# #111=IfcWall('1lfiJzSCH1a8vjDuSLL4Ii',#110,'Cube',$,$,#119,#114,$)
# #150=IfcWindow('1eE0btB_54tBL59wLXKO1B',#149,'Cube',$,$,#188,#151,$,$,$)
```
