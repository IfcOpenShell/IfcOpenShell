# IFCCityJSON
Converter for CityJSON files and IFC. Currently only supports one-way conversion from CityJSON to IFC. 

-- WARNING --

IFCCityJSON only came into being 14/04/2021. Be prepared for lots of bugs, unfinished implementations and little to no documentation!

## Dependencies
- [IfcOpenShell](https://github.com/IfcOpenShell/IfcOpenShell)
- [CJIO](https://github.com/cityjson/cjio)

## Usage of IFCCityJSON
Following command will execute a conversion from CityJSON to IFC
  
    python ifccityjson.py [-i input file] [-o output file] [-n name of identification attribute]

The example file that could be used is example/3D_BAG_example.json

    python ifccityjson.py -i example/3DBAG_example.json -o example/3DBAG_example.ifc -n identificatie

## Implemented geometries
- [ ] "MultiPoint"
- [ ] "MultiLineString"
- [x] "MultiSurface"
- [ ] "CompositeSurface"
- [x] "Solid": exterior shell
- [ ] "Solid": interior shell
- [x] "MultiSolid"
- [x] "CompositeSolid"
- [ ] "GeometryInstance" 

## TODO
- [x] CityJSON Attributes as IFC properties in 'CityJSON_attributes' pset
- [x] Implement georeferencing
- [ ] Do not use template IFC for new IFC file, but make IFC file from scratch
