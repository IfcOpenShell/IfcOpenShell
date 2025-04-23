# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2021 Nathan Hild <nathan.hild@gmail.com>
#
# This file is part of Bonsai.
#
# Bonsai is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Bonsai is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Bonsai.  If not, see <http://www.gnu.org/licenses/>.

"""
Disabling addon without issues is crucial for extension update to work.

Use operators instead of `blender --command extension remove`
to ensure disable and enable occur in the same Blender session.
"""


import bpy
import bonsai.tool as tool

bonsai_name = tool.Blender.get_blender_addon_package_name()
bpy.ops.preferences.addon_disable(module=bonsai_name)
bpy.ops.preferences.addon_enable(module=bonsai_name)
