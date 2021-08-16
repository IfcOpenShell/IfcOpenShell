
# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2020, 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of BlenderBIM Add-on.
#
# BlenderBIM Add-on is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# BlenderBIM Add-on is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with BlenderBIM Add-on.  If not, see <http://www.gnu.org/licenses/>.

bl_info = {
    "name": "BlenderBIM",
    "description": "Author, import, and export files in the " "Industry Foundation Classes (.ifc) file format",
    "author": "Dion Moult, IfcOpenShell",
    "blender": (2, 80, 0),
    "version": (0, 0, 999999),
    "location": "File > Export, File > Import, Scene / Object / Material / Mesh Properties",
    "tracker_url": "https://github.com/IfcOpenShell/IfcOpenShell/issues",
    "category": "Import-Export",
}

import os
import site


# process *.pth in /libs/site/packages to setup globally importable modules
# 3 levels deep required by occ static ../../ path
# TODO: 3 levels deep is no longer required as we no longer bundle OCC
cwd = os.path.dirname(os.path.realpath(__file__))
site.addsitedir(os.path.join(cwd, "libs", "site", "packages"))


# main import
from .bim import *


# Explicitely expose bim.xx when imported with from blenderbim import *
# Other bim still are importable using explicit from blenderbim.bim import xxx
__all__ = ["export_ifc", "import_ifc"]


if __name__ == "__main__":
    register()
