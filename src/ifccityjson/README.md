# IFCCityJSON
Converter for CityJSON files and IFC. Currently only supports one-way conversion from CityJSON to IFC. 

-- WARNING --

IFCCityJSON only came into being 14/04/2021. Be prepared for lots of bugs, unfinished implementations and little to no documentation!

## Dependencies
- [IfcOpenShell](https://github.com/IfcOpenShell/IfcOpenShell) (also IfcOpenShell api is needed)
- [CJIO](https://github.com/cityjson/cjio)

## Usage of IFCCityJSON
Following command will execute a conversion from CityJSON to IFC
  
    python ifccityjson.py [-i input file] [-o output file] [-n name of identification attribute]

The example file that could be used is example/3D_BAG_example.json

    python ifccityjson.py -i example/3DBAG_example.json -o example/3DBAG_example.ifc -n identificatie

## Implemented geometries
- [x] "MultiPoint"
- [x] "MultiLineString"
- [x] "MultiSurface"
- [x] "CompositeSurface"
- [x] "Solid": exterior shell
- [ ] "Solid": interior shell
- [x] "MultiSolid"
- [x] "CompositeSolid"
- [ ] "GeometryInstance" 

## TODO
- [x] CityJSON Attributes as IFC properties in 'CityJSON_attributes' pset
- [x] Implement georeferencing
- [x] Do not use template IFC for new IFC file, but make IFC file from scratch
- [x] Create mapping to IFC for all CityJSON object types & semantic surfaces
- [ ] Implement conversion of all CitYJSON geometries
- [ ] Implement conversion of all LODs instead of only the most detailed
