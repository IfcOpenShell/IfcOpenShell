
IfcOpenShell 
============

<p align="center">
<img src="https://github.com/IfcOpenShell/IfcOpenShell/assets/88302/34901387-e2dd-4a0c-8e38-9ffc32a66cde">
</p>

IfcOpenShell is an open source ([LGPL]) software library for working with Industry Foundation Classes ([IFC]). Complete
parsing support is provided for [IFC2x3 TC1], [IFC4 Add2 TC1], IFC4x1, IFC4x2, and [IFC4x3 Add2]. Extensive geometric support
is implemented for the IFC releases [IFC2x3 TC1] and [IFC4 Add2 TC1]. Extending with support for arbitrary IFC schemas
is possible at compile-time when using C++ and at run-time when using Python.

In addition to a C++ and Python API, IfcOpenShell comes with an ecosystem of tools, notably including IfcConvert (an application
to convert IFC models to other formats), Bonsai (an add-on to Blender providing a graphical IFC authoring platform),
and many other libraries, CLI apps, and more. Support is also provided for auxiliary standards such as BCF and IDS.

For more information, see:

* [IfcOpenShell Website](http://ifcopenshell.org)
* [IfcOpenShell Documentation](https://docs.ifcopenshell.org)
  * [IfcOpenShell C++ Installation](https://docs.ifcopenshell.org/ifcopenshell/installation.html)
  * [IfcOpenShell Python Installation](https://docs.ifcopenshell.org/ifcopenshell-python/installation.html)
  * [IfcOpenShell Python Hello World Tutorial](https://docs.ifcopenshell.org/ifcopenshell-python/hello_world.html)
* [Bonsai Website](https://bonsaibim.org)
* [Bonsai Documentation](https://docs.bonsaibim.org/index.html)
  * [Add-on Installation](https://docs.bonsaibim.org/quickstart/installation.html)
  * [Exploring an IFC model](https://docs.bonsaibim.org/quickstart/explore_model.html)
 
Development is sponsored through your generous donations!

[![Open Collective Contributors](https://img.shields.io/opencollective/all/opensourcebim?label=Sponsors&color=22ce5f)](https://opencollective.com/opensourcebim/)

Contents
--------

| Name                      | Description                                                           | License             | Service |
| ------------------------- | --------------------------------------------------------------------- | ------------------- | ------- |
| bcf                       | Library to read and write BCF-XML and query OpenCDE BCF-API modules   | LGPL-3.0-or-later   | [![PyPI](https://img.shields.io/pypi/v/bcf-client?label=PyPI&color=006dad)](https://pypi.org/project/bcf-client/) [![Anaconda-Server Badge](https://anaconda.org/conda-forge/bcf-client/badges/version.svg)](https://anaconda.org/conda-forge/bcf-client) |
| bonsai                    | Add-on to Blender providing a graphical native IFC authoring platform | GPL-3.0-or-later    | [![Official](https://img.shields.io/badge/BonsaiBIM.org-Download-70ba35)](https://bonsaibim.org/download.html) [![GitHub Unstable](https://img.shields.io/github/v/release/ifcopenshell/ifcopenshell?filter=bonsai-*&label=GitHub-Unstable&color=f6f8fa)](https://github.com/IfcOpenShell/IfcOpenShell/releases?q=bonsai&expanded=true) [![Chocolatey](https://img.shields.io/chocolatey/v/blenderbim-nightly?label=Chocolatey&color=5c9fd8)](https://community.chocolatey.org/packages/blenderbim-nightly/) |
| bsdd                      | Library to query the bSDD API                                         | LGPL-3.0-or-later   | [![PyPI](https://img.shields.io/pypi/v/bsdd?label=PyPI&color=006dad)](https://pypi.org/project/bsdd/) |
| ifc2ca                    | Utility to convert IFC structural analysis models to Code_Aster       | LGPL-3.0-or-later   |
| ifc4d                     | Convert to and from IFC and project management software               | LGPL-3.0-or-later   | [![PyPI](https://img.shields.io/pypi/v/ifc4d?label=PyPI&color=006dad)](https://pypi.org/project/ifc4d/) |
| ifc5d                     | Report and optimise cost information from IFC                         | LGPL-3.0-or-later   | [![PyPI](https://img.shields.io/pypi/v/ifc5d?label=PyPI&color=006dad)](https://pypi.org/project/ifc5d/) |
| ifcbimtester              | Wrapper for Gherkin based unit testing for IFC models                 | LGPL-3.0-or-later   |
| ifcblender                | Historic Blender IFC import add-on                                    | LGPL-3.0-or-later\* |
| ifccityjson               | Convert CityJSON to IFC                                               | LGPL-3.0-or-later   | [![PyPI](https://img.shields.io/pypi/v/ifccityjson?label=PyPI&color=006dad)](https://pypi.org/project/ifccityjson/) |
| ifcclash                  | Clash detection library and CLI app                                   | LGPL-3.0-or-later   | [![PyPI](https://img.shields.io/pypi/v/ifcclash?label=PyPI&color=006dad)](https://pypi.org/project/ifcclash/) |
| ifcconvert                | CLI app to convert IFC to many other formats                          | LGPL-3.0-or-later\* | [![Official](https://img.shields.io/badge/IfcOpenShell.org-Download-70ba35)](https://docs.ifcopenshell.org/ifcconvert/installation.html) [![GitHub](https://img.shields.io/github/v/release/ifcopenshell/ifcopenshell?filter=ifcconvert-*&label=GitHub&color=f6f8fa)](https://github.com/IfcOpenShell/IfcOpenShell/releases?q=ifcconvert&expanded=true)
| ifccsv                    | Library and CLI app to export and import schedules from IFC           | LGPL-3.0-or-later   | [![PyPI](https://img.shields.io/pypi/v/ifccsv?label=PyPI&color=006dad)](https://pypi.org/project/ifccsv/) |
| ifcdiff                   | Compare changes between IFC models                                    | LGPL-3.0-or-later   | [![PyPI](https://img.shields.io/pypi/v/ifcdiff?label=PyPI&color=006dad)](https://pypi.org/project/ifcdiff/) |
| ifcfm                     | Extract IFC data for FM handover requirements                         | LGPL-3.0-or-later   | [![PyPI](https://img.shields.io/pypi/v/ifcfm?label=PyPI&color=006dad)](https://pypi.org/project/ifcfm/) |
| ifcmax                    | Historic extension for IFC support in 3DS Max                         | LGPL-3.0-or-later\* | [![Official](https://img.shields.io/badge/IfcOpenShell.org-Download-70ba35)](https://docs.ifcopenshell.org/ifcmax.html)
| ifcopenshell-python       | Python library for IFC manipulation                                   | LGPL-3.0-or-later\* | [![Official](https://img.shields.io/badge/IfcOpenShell.org-Download-70ba35)](https://docs.ifcopenshell.org/ifcopenshell-python/installation.html) [![GitHub](https://img.shields.io/github/v/release/ifcopenshell/ifcopenshell?filter=ifcopenshell-python-*&label=GitHub&color=f6f8fa)](https://github.com/IfcOpenShell/IfcOpenShell/releases?q=ifcopenshell-python&expanded=true) [![PyPI](https://img.shields.io/pypi/v/ifcopenshell?label=PyPI&color=006dad)](https://pypi.org/project/ifcopenshell/) [![Anaconda](https://img.shields.io/conda/vn/conda-forge/ifcopenshell?label=Anaconda&color=43b02a)](https://anaconda.org/conda-forge/ifcopenshell) [![Anaconda](https://img.shields.io/conda/vn/ifcopenshell/ifcopenshell?label=Anaconda-Unstable&color=43b02a)](https://anaconda.org/ifcopenshell/ifcopenshell) [![Docker](https://img.shields.io/docker/pulls/aecgeeks/ifcopenshell?label=Docker&color=1D63ED)](https://hub.docker.com/r/aecgeeks/ifcopenshell) [![AUR](https://img.shields.io/aur/version/ifcopenshell?label=AUR&color=1793d1)](https://aur.archlinux.org/packages/ifcopenshell) [![AUR Unstable](https://img.shields.io/aur/version/ifcopenshell-git?label=AUR-Unstable&color=1793d1)](https://aur.archlinux.org/packages/ifcopenshell-git) |
| ifcpatch                  | Utility to run pre-packaged scripts to manipulate IFCs                | LGPL-3.0-or-later   | [![PyPI](https://img.shields.io/pypi/v/ifcpatch?label=PyPI&color=006dad)](https://pypi.org/project/ifcpatch/) |
| ifcsverchok               | Blender Add-on for visual node programming with IFC                   | GPL-3.0-or-later    | [![GitHub Unstable](https://img.shields.io/github/v/release/ifcopenshell/ifcopenshell?filter=ifcsverchok-*.*.*.*&label=GitHub-Unstable&color=f6f8fa)](https://github.com/IfcOpenShell/IfcOpenShell/releases?q=ifcsverchok&expanded=true)
| ifctester                 | Library, CLI and webapp for IDS model auditing                        | LGPL-3.0-or-later   | [![PyPI](https://img.shields.io/pypi/v/ifctester?label=PyPI&color=006dad)](https://pypi.org/project/ifctester/) |

The IfcOpenShell C++ codebase is split into multiple interal libraries:

| Name                      | Description                                                           | License             |
| ------------------------- | --------------------------------------------------------------------- | ------------------- |
| ifcgeom                   | Internal library for IfcOpenShell                                     | LGPL-3.0-or-later\* |
| ifcgeom\_schema\_agnostic | Internal library for IfcOpenShell                                     | LGPL-3.0-or-later\* |
| ifcgeomserver             | Internal library for IfcOpenShell                                     | LGPL-3.0-or-later\* |
| ifcjni                    | Internal library for IfcOpenShell                                     | LGPL-3.0-or-later\* |
| ifcparse                  | Internal library for IfcOpenShell                                     | LGPL-3.0-or-later\* |
| ifcwrap                   | Internal library for IfcOpenShell                                     | LGPL-3.0-or-later\* |
| qtviewer                  | Internal library for IfcOpenShell                                     | LGPL-3.0-or-later\* |
| serializers               | Internal library for IfcOpenShell                                     | LGPL-3.0-or-later\* |

[LGPL]: https://github.com/IfcOpenShell/IfcOpenShell/tree/master/COPYING.LESSER "LGPL-3.0-or-later"
[IFC]: https://technical.buildingsmart.org/standards/ifc/ "IFC"
[IFC2x3 TC1]: https://standards.buildingsmart.org/IFC/RELEASE/IFC2x3/TC1/HTML/ "IFC2x3 TC1"
[IFC4 Add2 TC1]: https://standards.buildingsmart.org/IFC/RELEASE/IFC4/ADD2_TC1/HTML/ "IFC4 Add2 TC1"
[IFC4x3 Add2]: https://standards.buildingsmart.org/IFC/RELEASE/IFC4_3/ "IFC4x3 Add2"
[Visual Studio]: https://www.visualstudio.com/ "Visual Studio"
[Visual C++ Build Tools]: http://landinghub.visualstudio.com/visual-cpp-build-tools "Visual C++ Build Tools"
[MSYS2]: https://msys2.github.io/ "MSYS2"
[win/readme.md]: https://github.com/IfcOpenShell/IfcOpenShell/tree/master/win/readme.md "win/readme.md"
[nix/build-all.py]: https://github.com/IfcOpenShell/IfcOpenShell/tree/master/nix/build-all.py "nix/build-all.py"
