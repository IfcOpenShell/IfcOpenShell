## A change log of the ifc2ca files

##### 14/07/20
- Add internal springs for point connection to elements and external springs for point connections according to the defined orientation

##### 27/05/20
- Add orientation for point, curve and surface geometries
- Calculate final geometry and orientation based on object placement transformation
- Add warnings in the json file to show any corrections considered while parsing the ifc file from ETABS with a model with rigid links
- Reduce file size by adding material and profile db in the json file and referencing them in the element objects
- Implement internal releases for curve-to-point connections with any arbitrary orientation

##### 22/03/20
- Calculation of section properties for I symmetric profile if not provided (assuming fillet radius is zero)
- Added geometry of planar structural surface members
- Refactored the ifc2ca.py script
- Added support for rigid links
- Added advanced meshing script to correctly simulate connections and independent meshing of structural elements (no common nodes)

##### 26/02/20
- Changed section to profile and added I profile
- Modified material and profile schema with mechanical and common properties
- Added geometry identification for point connection from representation
- Added connections along with supports based on the number of elements a connection is applied to

##### 09/02/20
- First implementation for straight structural curve elements and point connections
