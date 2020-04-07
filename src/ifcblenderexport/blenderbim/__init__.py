bl_info = {
    "name": "BlenderBIM",
    "description": "Author, import, and export files in the "
        "Industry Foundation Classes (.ifc) file format",
    "author": "Dion Moult, IfcOpenShell",
    "blender": (2, 80, 0),
    "version": (0, 0, 999999),
    "location": "File > Export, File > Import, Scene / Object / Material / Mesh Properties",
    "tracker_url": "https://github.com/IfcOpenShell/IfcOpenShell/issues",
    "category": "Import-Export"
    }

import os
import site

# process ifcopenshell.pth in /scripts/addons
site.addsitedir(os.path.join(os.path.dirname(os.path.realpath(__file__)), "scripts", "addons"))

import bim as blenderbim
import ifcopenshell


def register():
    blenderbim.register()


def unregister():
    blenderbim.unregister()


if __name__ == "__main__":
    register()
