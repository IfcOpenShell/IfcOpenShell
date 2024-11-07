# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2022 Dion Moult <dion@thinkmoult.com>
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

# ############################################################################ #

# Hey there! Welcome to the Bonsai code. Please feel free to reach
# out if you have any questions or need further guidance. Happy hacking!

# ############################################################################ #

# Every module has a __init__.py file to load all of its classes. Every
# operation, property, and interface needs to be registered with the Blender
# system when the add-on loads. This is where it happens.

import bpy
from . import ui, prop, operator

# You'll need to provide a list of every one of your classes here. If you forget
# to specify your class, it won't load and you won't be able to use that
# operator, property, or interface.
classes = (
    operator.BuildAlignment,
    prop.BIMAlignmentBuilderProperties,
    ui.BIM_PT_alignment,
)


# When the add-on loads, this register function is called. This allows you to
# perform additional tasks during startup. If you need to store custom
# properties, this is where you tell Blender where they are going to be stored.
# You might see more advanced registrations happening in other modules.
def register():
    # Properties are usually stored on bpy.types.Scene when they are something
    # that affects everything in the project, or bpy.types.Object when they
    # affect a single BIM element.
    bpy.types.Scene.BIMAlignmentBuilderProperties = bpy.props.PointerProperty(type=prop.BIMAlignmentBuilderProperties)


# When someone disables the add-on, we need to unload everything we loaded. This
# does the reverse of the register function.
def unregister():
    del bpy.types.Scene.BIMAlignmentBuilderProperties
