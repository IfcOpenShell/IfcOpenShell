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

import os
import sys
import site

bl_info = {
    "name": "BlenderBIM",
    "description": "Transforms Blender into a native Building Information Model authoring platform using IFC.",
    "author": "IfcOpenShell Contributors",
    "blender": (3, 1, 0),
    "version": (0, 0, 999999),
    "location": "File Menu, Scene Properties Tab. See documentation for more.",
    "doc_url": "https://docs.blenderbim.org/",
    "tracker_url": "https://github.com/IfcOpenShell/IfcOpenShell/issues",
    "category": "System",
}

if sys.modules.get("bpy", None):
    # Process *.pth in /libs/site/packages to setup globally importable modules
    # This is 3 levels deep as required by the static RPATH of ../../ from dependencies taken from Anaconda
    # site.addsitedir(os.path.join(os.path.dirname(os.path.realpath(__file__)), "libs", "site", "packages"))
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.realpath(__file__)), "libs", "site", "packages"))

    import blenderbim.bim

    def register():
        blenderbim.bim.register()

    def unregister():
        blenderbim.bim.unregister()
