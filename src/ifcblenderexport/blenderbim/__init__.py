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


# process *.pth in /libs/site/packages to setup globally importable modules
# 3 levels deep required by occ static ../../ path
cwd = os.path.dirname(os.path.realpath(__file__))
site.addsitedir(os.path.join(cwd, "libs", "site", "packages"))

# main import
from .bim import *


# Explicitely expose bim.xx when imported with from blenderbim import *
# Other bim still are importable using explicit from blenderbim.bim import xxx
__all__ = ["export_ifc", "import_ifc"]


if __name__ == "__main__":
    register()
