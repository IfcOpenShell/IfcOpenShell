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

# Every module has an operator.py file to define all of the buttons that a user
# can click on from the Blender interface. Blender calls these buttons
# "Operators", since they correlate to a single user operation.

import bpy
import bonsai.tool as tool
import bonsai.core.alignment as core


# Each button correlates to a class like the one below. In this case, we're
# creating a new button that will execute a hello world feature.
class BuildAlignment(bpy.types.Operator, tool.Ifc.Operator):
    # Every operator has a unique ID. If you enable Python tooltips and hover
    # over any button in the interface, you will see each button will run a
    # function that uses this ID. For example, hovering over this button will
    # show that the code it executes is "bpy.ops.bim.demonstrate_hello_world()"
    bl_idname = "bim.build_alignment"

    # In the interface, this button will have the text "Build Alignment".
    bl_label = "Build Alignment"

    # This code means that the user can undo or redo after pressing the button.
    bl_options = {"REGISTER", "UNDO"}

    # When hovering over the button, this helpful description will be shown.
    bl_description = "Builds a dummy alignment"

    # When the button is pressed, this _execute() function will run.
    def _execute(self, context):
        # Every operator should do one thing only: execute a core function. In
        # order to execute a core function, the operator's responsibility is to
        # pass in all of the inputs the core needs to do its job.

        # A core function simply tells tools what to do, so a core function will
        # always need at least one tool as an input.
        core.build_alignment(tool.Alignment)

