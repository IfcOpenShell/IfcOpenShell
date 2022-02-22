# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2022 Dion Moult <dion@thinkmoult.com>
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

# ############################################################################ #

# Hey there! Welcome to the BlenderBIM Add-on code. Please feel free to reach
# out if you have any questions or need further guidance. Happy hacking!

# ############################################################################ #

# Every module has an operator.py file to define all of the buttons that a user
# can click on from the Blender interface. Blender calls these buttons
# "Operators", since they correlate to a single user operation.

import bpy
import blenderbim.tool as tool
import blenderbim.core.demo as core
import blenderbim.bim.handler


# Each button correlates to a class like the one below. In this case, we're
# creating a new button that will execute a hello world feature.
class DemonstrateHelloWorld(bpy.types.Operator, tool.Ifc.Operator):
    # Every operator has a unique ID. If you enable Python tooltips and hover
    # over any button in the interface, you will see each button will run a
    # function that uses this ID. For example, hovering over this button will
    # show that the code it executes is "bpy.ops.bim.demonstrate_hello_world()"
    bl_idname = "bim.demonstrate_hello_world"

    # In the interface, this button will have the text "Print Hello World".
    bl_label = "Print Hello World"

    # This code means that the user can undo or redo after pressing the button.
    bl_options = {"REGISTER", "UNDO"}

    # When hovering over the button, this helpful description will be shown.
    bl_description = "Prints the text 'Hello World'"

    # When the button is pressed, this _execute() function will run.
    def _execute(self, context):
        # Every operator should do one thing only: execute a core function. In
        # order to execute a core function, the operator's responsibility is to
        # pass in all of the inputs the core needs to do its job.

        # A core function simply tells tools what to do, so a core function will
        # always need at least one tool as an input.
        core.demonstrate_hello_world(tool.Demo)


# This class, just like the one above, will correlate to another button in the
# interface. It has a different ID and a different label.
class DemonstrateRenameProject(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.demonstrate_rename_project"
    bl_label = "Rename IFC Project"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Renames your IFC project name and prints the name"

    def _execute(self, context):
        # This core function requires three inputs: two tools, and a name
        # string. In this case, the name is taken from some custom Blender
        # properties. Generally, the inputs to the core function will come from
        # properties (such as an input field) or data from the scene (like the
        # actively selected object).
        core.demonstrate_rename_project(tool.Ifc, tool.Demo, name=bpy.context.scene.BIMDemoProperties.name)
