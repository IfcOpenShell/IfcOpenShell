# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
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

# Note: these tests are commented out as they are for learning purposes only. If
# you want to run these tests, uncomment it :)

"""

# Because our tools have well defined, isolated functions, it means we can test
# them very easily in isolation. Tests are fun, fast, and easy to setup!

import bpy
import ifcopenshell
import bonsai.core.tool
import bonsai.tool as tool
from test.bim.bootstrap import NewFile
from bonsai.tool.demo import Demo as subject


# Our first test is that our tool implements all the abstract methods defined by
# the `core/tool.py` interface. Anytime the core wants something that the tools
# don't provide, this test will catch it. This type of test comes for free in
# other languages, but not Python, so we test it explicitly.
class TestImplementsTool(NewFile):
    def test_run(self):
        assert isinstance(subject(), bonsai.core.tool.Demo)


# These are fairly boring tests. What it does demonstrate is that no matter how
# complex a BIM application can get, it can always be reduced down to small,
# easily tested functions. Note that these functions actually are concrete
# implementations, so that means that you need to use Blender headlessly to run
# these tests.
class TestClearNameField(NewFile):
    def test_run(self):
        bpy.context.scene.BIMDemoProperties.name = "name"
        subject.clear_name_field()
        assert bpy.context.scene.BIMDemoProperties.name == ""


class TestGetProject(NewFile):
    def test_run(self):
        # Sometimes, there is a bit of preparation work to setup a scenario that
        # can be tested. In this case, we need to set an active IFC dataset with
        # a project. This is normal.
        ifc = ifcopenshell.file()
        project = ifc.createIfcProject()
        tool.Ifc.set(ifc)
        assert subject.get_project() == project


class TestHideUserHints(NewFile):
    def test_run(self):
        bpy.context.scene.BIMDemoProperties.show_hints = True
        subject.hide_user_hints()
        assert bpy.context.scene.BIMDemoProperties.show_hints == False


class TestSetMessage(NewFile):
    def test_run(self):
        bpy.context.scene.BIMDemoProperties.message = ""
        subject.set_message("message")
        assert bpy.context.scene.BIMDemoProperties.message == "message"


class TestShowUserHints(NewFile):
    def test_run(self):
        bpy.context.scene.BIMDemoProperties.show_hints = False
        subject.show_user_hints()
        assert bpy.context.scene.BIMDemoProperties.show_hints == True

"""
