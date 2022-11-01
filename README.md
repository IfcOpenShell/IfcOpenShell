
IfcOpenShell 
============

IfcOpenShell is an open source ([LGPL]) software library for working with Industry Foundation Classes ([IFC]). Complete
parsing support is provided for [IFC2x3 TC1], [IFC4 Add2 TC1], IFC4x1, IFC4x3, and IFC4x3. Extensive geometric support
is implemented for the IFC releases [IFC2x3 TC1] and [IFC4 Add2 TC1]. Extending with support for arbitrary IFC schemas
is possible at compile-time when using C++ and at run-time when using Python.

In addition to a C++ and Python API, IfcOpenShell comes with an ecosystem of tools, notably including IfcConvert (an application to convert IFC models to
other formats), the BlenderBIM Add-on (an add-on to Blender providing a graphical IFC authoring platform), and many
other libraries, CLI apps, and more. Support is also provided for auxiliary standards such as BCF and IDS.

For more information, see:

* [IfcOpenShell Website](http://ifcopenshell.org)
* [IfcOpenShell Documentation](http://blenderbim.org/docs-python)
  * [IfcOpenShell C++ Installation](https://blenderbim.org/docs-python/ifcopenshell/installation.html)
  * [IfcOpenShell Python Installation](https://blenderbim.org/docs-python/ifcopenshell-python/installation.html)
  * [IfcOpenShell Python Hello World Tutorial](https://blenderbim.org/docs-python/ifcopenshell-python/hello_world.html)
* [BlenderBIM Add-on Website](https://blenderbim.org)
* [BlenderBIM Add-on Documentation](http://blenderbim.org/docs)
  * [Add-on Installation](https://blenderbim.org/docs/users/installation.html)
  * [Exploring an IFC model](https://blenderbim.org/docs/users/exploring_an_ifc_model.html)

| Service                                         | Status                                                                                                                                       |
| ----------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------- |
| Anaconda Daily Build                            | [![Anaconda-Server Badge](https://img.shields.io/conda/vn/ifcopenshell/ifcopenshell)](https://anaconda.org/ifcopenshell/ifcopenshell)        |
| Anaconda v0.7.0 Stable                          | [![Anaconda-Server Badge](https://img.shields.io/conda/vn/conda-forge/ifcopenshell)](https://anaconda.org/conda-forge/ifcopenshell)          |
| PyPi Daily Build                                | [![PyPi Badge](https://img.shields.io/pypi/v/ifcopenshell)](https://pypi.org/project/ifcopenshell/)                                          |
| ArchLinux AUR Package                           | [![AUR Badge](https://img.shields.io/aur/version/ifcopenshell-git)](https://aur.archlinux.org/packages/ifcopenshell-git)                     |
| BlenderBIM Add-on Chocolatey (under moderation) | [![Chocolatey Badge](https://img.shields.io/chocolatey/v/blenderbim-nightly)](https://community.chocolatey.org/packages/blenderbim-nightly/) |
| Sponsor development on OpenCollective           | [![Financial Contributors](https://opencollective.com/opensourcebim/tiers/badge.svg)](https://opencollective.com/opensourcebim/)             |
| Docker hub                                      | [![Docker Pulls](https://img.shields.io/docker/pulls/aecgeeks/ifcopenshell)](https://hub.docker.com/r/aecgeeks/ifcopenshell)                 |

Contents
--------

Those marked with an asterisk are part of IfcOpenShell.

| Name                      | Description                                                           | License             |
| ------------------------- | ----------------------------------------------------------------------| ------------------- |
| bcf                       | Library to read and write BCF-XML and query OpenCDE BCF-API modules   | LGPL-3.0-or-later   |
| blenderbim                | Add-on to Blender providing a graphical native IFC authoring platform | GPL-3.0-or-later    |
| bsdd                      | Library to query the bSDD API                                         | LGPL-3.0-or-later   |
| ifc2ca                    | Utility to convert IFC structural analysis models to Code_Aster       | LGPL-3.0-or-later   |
| ifc4d                     | Convert to and from IFC and project management software               | LGPL-3.0-or-later   |
| ifc5d                     | Report and optimise cost information from IFC                         | LGPL-3.0-or-later   |
| ifcbimtester              | Wrapper for Gherkin based unit testing for IFC models                 | LGPL-3.0-or-later   |
| ifcblender                | Historic Blender IFC import add-on                                    | LGPL-3.0-or-later\* |
| ifccityjson               | Convert CityJSON to IFC                                               | LGPL-3.0-or-later   |
| ifcclash                  | Clash detection library and CLI app                                   | LGPL-3.0-or-later   |
| ifccobie                  | Extract IFC data for COBie handover requirements                      | LGPL-3.0-or-later   |
| ifcconvert                | CLI app to convert IFC to many other formats                          | LGPL-3.0-or-later\* |
| ifccsv                    | Library and CLI app to export and import schedules from IFC           | LGPL-3.0-or-later   |
| ifcdiff                   | Compare changes between IFC models                                    | LGPL-3.0-or-later   |
| ifcfm                     | Extract IFC data for FM handover requirements                         | LGPL-3.0-or-later   |
| ifcgeom                   | Internal library for IfcOpenShell                                     | LGPL-3.0-or-later\* |
| ifcgeom\_schema\_agnostic | Internal library for IfcOpenShell                                     | LGPL-3.0-or-later\* |
| ifcgeomserver             | Internal library for IfcOpenShell                                     | LGPL-3.0-or-later\* |
| ifcjni                    | Internal library for IfcOpenShell                                     | LGPL-3.0-or-later\* |
| ifcmax                    | Historic extension for IFC support in 3DS Max                         | LGPL-3.0-or-later\* |
| ifcopenshell-python       | Python library for IFC manipulation                                   | LGPL-3.0-or-later\* |
| ifcparse                  | Internal library for IfcOpenShell                                     | LGPL-3.0-or-later\* |
| ifcpatch                  | Utility to run pre-packaged scripts to manipulate IFCs                | LGPL-3.0-or-later   |
| ifcsverchok               | Blender Add-on for visual node programming with IFC                   | GPL-3.0-or-later    |
| ifctester                 | Library, CLI and webapp for IDS model auditing                        | LGPL-3.0-or-later   |
| ifcwrap                   | Internal library for IfcOpenShell                                     | LGPL-3.0-or-later\* |
| qtviewer                  | Internal library for IfcOpenShell                                     | LGPL-3.0-or-later\* |
| serializers               | Internal library for IfcOpenShell                                     | LGPL-3.0-or-later\* |

[LGPL]: https://github.com/IfcOpenShell/IfcOpenShell/tree/master/COPYING.LESSER "LGPL-3.0-or-later"
[IFC]: https://technical.buildingsmart.org/standards/ifc/ "IFC"
[IFC2x3 TC1]: https://standards.buildingsmart.org/IFC/RELEASE/IFC2x3/TC1/HTML/ "IFC2x3 TC1"
[IFC4 Add2 TC1]: https://standards.buildingsmart.org/IFC/RELEASE/IFC4/ADD2_TC1/HTML/ "IFC4 Add2 TC1"
[Visual Studio]: https://www.visualstudio.com/ "Visual Studio"
[Visual C++ Build Tools]: http://landinghub.visualstudio.com/visual-cpp-build-tools "Visual C++ Build Tools"
[MSYS2]: https://msys2.github.io/ "MSYS2"
[win/readme.md]: https://github.com/IfcOpenShell/IfcOpenShell/tree/master/win/readme.md "win/readme.md"
[nix/build-all.py]: https://github.com/IfcOpenShell/IfcOpenShell/tree/master/nix/build-all.py "nix/build-all.py"
