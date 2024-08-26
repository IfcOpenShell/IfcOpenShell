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

# Every module has a core.py file to define all of its core functions. A core
# function describes what happens when the user wants to do something like
# pressing a button.

# Think of a core function as a short poem of pseudocode that describes what
# happens in different usecases. A core should be no more than 50 lines of code,
# even in the most complex of features. A core simply delegates tasks to tools
# in a sequence that describes the flow of logic in a feature - in other words,
# it tells tools to do different things. You will notice that the core doesn't
# have any code that deals with Blender or IFC directly - these are all little
# details that are hidden away in tools. The core is not interested in these
# details, the core is only concerned with the big picture.

# Imagine, no matter how complex a software can be, every feature can be
# described in regular sentences in under 50 lines. That is the purpose of the
# core.


# Here's the simplest possible core function. It does one thing only. Remember:
# core functions delegate tasks to tools, so all core functions need at least
# one tool.
def demonstrate_hello_world(demo):
    # We're telling the demo tool to set a message. We aren't interested how the
    # tool works, that's a detail. We aren't interested in the interface, like
    # where the message is shown. You can name these functions whatever you feel
    # best describes what's going on, like if you had to describe the feature to
    # someone else.
    demo.set_message("Hello, World!")


# Here's a slightly more complex core function. It uses two tools. By default,
# you'll want to use your module's tool (in this case, "Demo") for all tasks,
# except for changing IFC data, where you'll use the "Ifc" tool. At a glance,
# simply by seeing what tools are used, this gives you an idea about what
# aspects (or dependencies) a core function cares about. This function also has
# an non-tool input called "name". Non-tool inputs should be keyword arguments
# with possible default values.
def demonstrate_rename_project(ifc, demo, name=None):
    # As you can see, core functions read almost like pseudocode. A great way to
    # code a new feature is to write out what it does in English first, then
    # change them into tool functions. You can choose any function you want, and
    # you can see a list of every single tool function in # `core/tool.py`.
    if name:
        project = demo.get_project()
        ifc.run("attribute.edit_attributes", product=project, attributes={"Name": name})
        demo.clear_name_field()
        demo.hide_user_hints()
    else:
        demo.show_user_hints()


# here this core function uses the web tool to send a message to the web UI
# we call the send_webui_data method to send any kind of data to the web UI
def send_webui_demo_message(web, message="Hello"):
    web.send_webui_data(data=message, data_key="demo_message", event="demo_data")
