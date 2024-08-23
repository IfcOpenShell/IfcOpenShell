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

# Every module has a ui.py file to define its interface. Interfaces describe how
# panels, buttons, labels, and input fields are laid out.

import bpy
from bonsai.bim.module.demo.data import DemoData


# Every panel in the interface correlates to one of these classes. If you enable
# the "Developer Extras" option in Blender, then you can actually right click on
# any panel in Blender, and click "Edit Source". This will bring you to a ui.py
# file like this one where you can see this code. Pretty neat!
class BIM_PT_demo(bpy.types.Panel):
    # Every panel has a title.
    bl_label = "Bonsai Demo"

    # Every panel must have an ID. It must be unique. For example, you may want
    # to later reference the panel (such as if you want to create a nested
    # subpanel).
    bl_idname = "BIM_PT_demo"

    # This tells the panel to appear in the properties section (in the bottom
    # right by default) of the Blender interface.
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"

    # This tells the panel to appear in the "scene" tab of the properties panel.
    bl_context = "scene"

    # Every panel has a draw function. This draws all the layout of the panel,
    # including all of its labels, buttons, and so on. Note that if the panel is
    # hidden, this draw function will not be called.
    def draw(self, context):
        # Before drawing any content, the panel must load any dynamic variables
        # that it will show. Most panels have dynamic content, which display
        # changing data from your BIM model. You must load that data first. The
        # two lines are always the same, "if not loaded, then load".
        if not DemoData.is_loaded:
            # Each panel should have its own data class that it loads data from.
            # Note that we only load data if it hasn't already been loaded.
            # This is because interface panels are drawn continuously. This
            # draw() function will be called every time you scroll or move your
            # mouse over it. Loading data is slow, so we only refresh data when
            # we have to.
            DemoData.load()

        # Interface panels often show properties. For convenience, define where
        # the properties are stored for the module.
        self.props = context.scene.BIMDemoProperties

        # This defines a new "row" in our layout. When a new row is defined, the
        # things on that row, like buttons, labels, and input fields, show on a
        # new line.
        row = self.layout.row()
        # This is the simplest interface element - a label placed in our row.
        # If you enable the "Icon Viewer" add-on, you can view a list of
        # Blender's built-in icons to choose from in the Blender text editor's
        # side panel.
        row.label(text="This is a demo panel", icon="INFO")

        # Our interface can contain simple logic. For example, if we don't have
        # an IFC project, show an error message and don't draw anything else.
        # The ui.py should always have very simple logic. Details like how to
        # determine whether we have a project is delegated to the data loader.
        if not DemoData.data["has_project"]:
            row = self.layout.row()
            row.label(text="Load or create an IFC project first", icon="ERROR")
            return

        row = self.layout.row()
        # When you want to show a button in the interface, you have to specify
        # an operator. Operators are defined in operator.py. You reference an
        # operator using its unique ID.
        row.operator("bim.demonstrate_hello_world")

        # Blender properties can be used to affect what your panel shows. Notice
        # how the logic is very simple. Only use simple boolean predicates and
        # loops in your layout. No complex logic should ever been seen in the
        # interface code.
        if self.props.message:
            row = self.layout.row()
            row.label(text=self.props.message)

        row = self.layout.row(align=True)
        row.label(text="Project Name")
        # Sometimes you need data that doesn't come from Blender properties,
        # like from your IFC model. In this case, just get some data from your
        # data loader. For those familiar with how templating languages work,
        # this is exactly the same.
        row.label(text=DemoData.data["project_name"])

        row = self.layout.row()
        # We've seen how to show text labels and buttons using operators. What
        # about text input fields, number sliders, dropdowns, checkboxes, and
        # scrollable lists? The way Blender works is that you simply show a
        # Blender property in your interface. The data type of that property
        # determines which UI widget is shown. A text property will show a text
        # field. A number property will show a number slider. An enum property
        # will show a drop down. And so on. In this case, our name property is a
        # text data type, so expect to see a text input field show up here.
        row.prop(self.props, "name")
        row = self.layout.row()
        # Here's another button, referencing another operator.
        row.operator("bim.demonstrate_rename_project")

        if self.props.show_hints:
            row = self.layout.row()
            row.label(text="Name cannot be blank!")


class BIM_PT_webui_demo(bpy.types.Panel):
    bl_label = "Web UI Demo"
    bl_idname = "BIM_PT_webui_demo"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    # we specify that this panel is closed by default
    bl_options = {"DEFAULT_CLOSED"}
    # here we reference the demo panel to create a sub panel
    # for the web UI demo
    bl_parent_id = "BIM_PT_demo"

    def draw(self, context):
        self.props = context.scene.BIMDemoProperties

        row = self.layout.row()
        # we create an input field for the property webui_message
        row.prop(self.props, "webui_message")

        row = self.layout.row()
        # here we create a button referencing the operator send_webui_message
        row.operator("bim.send_webui_demo_message")
