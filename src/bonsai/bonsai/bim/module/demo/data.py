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

# Every module has a data.py file to load data for its interface panels to
# display. When a panel needs to show information that doesn't come from a
# Blender property, it gets that data from one of these classes. This separation
# of "fetching data" and "displaying data" is a common concept that makes UI
# code much simpler, more efficient, and less error-prone to refresh data.

import bonsai.tool as tool


# All data must have a refresh function. The refresh function simply sets all
# data class to be not yet loaded. So the next time the interface is drawn to
# the user, it will force the data to be reloaded.
def refresh():
    # When you define your own data classes, just add to this list!
    DemoData.is_loaded = False


# This is a sample data class. It correlates to a single interface panel. Panels
# should not share data classes. This makes it easy to write your interface
# without having your code mixed in with other parts of the interface. As a
# convention, the class is named the same name as the panel.
class DemoData:
    # All data classes must have two variables. One to store all the data it has
    # loaded and another to store the load state.
    data = {}
    is_loaded = False

    # Every data class must have a load function. This lets us load data in a
    # predictable manner.
    @classmethod
    def load(cls):
        # The load function always has two responsibilities: populate the data,
        # and set is_loaded to true.
        cls.data = {
            "has_project": cls.has_project(),
            "project_name": cls.project_name(),
        }
        cls.is_loaded = True

    @classmethod
    def has_project(cls):
        # Here, we check whether or not there is an active IFC project in our
        # Blender session.
        return bool(tool.Ifc.get())

    @classmethod
    def project_name(cls):
        # Imagine how messy our UI code would be if all of this was mixed in
        # with our layout code. Here, it's isolated and testable, and the UX
        # becomes easier to maintain and change.
        ifc = tool.Ifc.get()
        if ifc:
            return ifc.by_type("IfcProject")[0].Name or "Unnamed"
