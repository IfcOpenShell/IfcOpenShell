IfcConvert
==========

IfcConvert is a command-line application for converting IFC geometry into file
formats such as OBJ, DAE, GLB, STP, IGS, XML, SVG, H5, and IFC itself.

For other formats, you may use other IfcOpenShell utilities as shown in the
table below.

+-------------------------+-------------------------+----------------------+
| From Format             | To Format               | Tool                 |
+=========================+=========================+======================+
| .ifc                    | .obj, .dae, .glb, .stp, | IfcConvert           |
|                         | .igs, .xml, .svg, .h5,  |                      |
|                         | .ifc                    |                      |
+-------------------------+-------------------------+----------------------+
| .ifc                    | .dae, .abc, .usd, .obj, | Bonsai_              |
|                         | .ply, .stl, .fbx, .glb, |                      |
|                         | .gltf, .x3d, .dxf       |                      |
+-------------------------+-------------------------+----------------------+
| .ifc                    | .ifcZIP, .ifcXML, .ifc  | IfcOpenShell-Python_ |
+-------------------------+-------------------------+----------------------+
| .ifc                    | .ifcJSON                | Ifc2JSON_            |
+-------------------------+-------------------------+----------------------+
| .ifc                    | .ifc                    | IfcPatch_            |
|                         | (IFC2X3, IFC4, IFC4X3), |                      |
|                         | SQLite, MySQL           |                      |
+-------------------------+-------------------------+----------------------+
| .ifc                    | .json (Code_Aster),     | Ifc2CA_              |
|                         | .comm (Code_Aster)      |                      |
+-------------------------+-------------------------+----------------------+
| .ifc                    | .xml (Oracle P6),       | Ifc4D_               |
|                         | .xml (MS Project)       |                      |
+-------------------------+-------------------------+----------------------+
| .ifc                    | .csv, .ods, .xlsx       | Ifc5D_               |
+-------------------------+-------------------------+----------------------+
| .ifc                    | .csv, .ods, .xlsx,      | IfcCSV_              |
|                         | Pandas DataFrame        |                      |
+-------------------------+-------------------------+----------------------+
| .csv                    | .ifc                    | Ifc5D_               |
+-------------------------+-------------------------+----------------------+
| .csv                    | .ifc                    | IfcCSV_              |
+-------------------------+-------------------------+----------------------+
| .dxf                    | .ifc                    | Bonsai_              |
+-------------------------+-------------------------+----------------------+
| .obj                    | .ifc                    | Bonsai_              |
+-------------------------+-------------------------+----------------------+
| .json (CityJSON)        | .ifc                    | IfcCityJSON_         |
+-------------------------+-------------------------+----------------------+
| .xer (Oracle P6)        | .ifc                    | Ifc4D_               |
+-------------------------+-------------------------+----------------------+
| .xml (Oracle P6)        | .ifc                    | Ifc4D_               |
+-------------------------+-------------------------+----------------------+
| .xml (MS Project)       | .ifc                    | Ifc4D_               |
+-------------------------+-------------------------+----------------------+
| .xml (Powerproject)     | .ifc                    | Ifc4D_               |
+-------------------------+-------------------------+----------------------+

.. _IfcOpenShell-Python: ifcopenshell-python.html
.. _IfcPatch: ifcpatch.html
.. _Ifc2CA: ifc2ca.html
.. _IfcCSV: ifccsv.html
.. _Ifc4D: ifc4d.html
.. _Ifc5D: ifc5d.html
.. _IfcCityJSON: ifccityjson.html
.. _Ifc2JSON: other.html
.. _Bonsai: bonsai.html

.. toctree::
   :hidden:
   :maxdepth: 1
   :caption: Contents:

   ifcconvert/installation
   ifcconvert/usage
