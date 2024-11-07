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

# Every module has a prop.py file to define Blender properties. Any time you
# want an interface widget like an input field, dropdown, checkbox, or number
# slider, you need a Blender property to store that widget's data. If you want
# to store data that will affect the Blender interface, you also need a
# property. Properties are stored in the .blend file, so when your user closes
# their Blender session, and reopens it, things are how they left it.

import bpy
from bpy.types import PropertyGroup

# Properties have many different data types. We won't use all of them in this
# demo module, but this is a list for your reference.
from bpy.props import (
    PointerProperty,
    StringProperty,
    EnumProperty,
    BoolProperty,
    IntProperty,
    FloatProperty,
    FloatVectorProperty,
    CollectionProperty,
)


# All properties must belong in a property group. Usually, you'd have a group
# named after your module.
class BIMAlignmentBuilderProperties(PropertyGroup):
    # This first property is a string. This means that in the interface, it will
    # represent a text input field. We can give it a name and a default value.
    # The name will be the label shown next to the input field in the interface.
    name: StringProperty(name="Name", default="New Project Name")
    # Not all properties need to be shown using their equivalent input widget.
    # In this case, we can store a message string, but we will never show it as
    # an input text field in the ui.py.
    message: StringProperty(name="Message")
    show_hints: BoolProperty(name="Show Hints", default=False)
    #webui_message: StringProperty(name="Web UI Message", default="Hello, Web UI!")
