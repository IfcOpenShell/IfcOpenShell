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

# Note: these tests are commented out as they are for learning purposes only. If
# you want to run these tests, uncomment it :)

"""

# Testing the core might seem strange if you haven't written this type of
# abstract test before. You essentially want to test that things are called in
# the right sequence. This seems almost like writing the code twice, like in
# double entry bookkeeping in accounting. However, it guards against typos,
# helps document intention of different logical flows, and ensures that all
# permutations of logic flows meet sanity checks.

# We always call the module we're testing the "test subject". This makes our
# tests simple to read: just look for where the "subject" is called!
import bonsai.core.demo as subject

# These are like mocks, stubs, or spy objects. They don't do anything, but they
# let us check our test expectations.
from test.core.bootstrap import ifc, demo


# Let's test the hello world function.
class TestDemonstrateHelloWorld:
    # This function has only one logical flow, there is no benefit to describing
    # it further, so we have a test_run function. We need to specify all the
    # mock objects we need in the signature.
    def test_run(self, demo):
        # We set an expectation that in this default sequence of events, the
        # demo tool should have the set_message called with the "Hello, World!"
        # string as its argument. Notice how our test also reads like English.
        demo.set_message("Hello, World!").should_be_called()
        # After we've finished specifying our test expectations, let's run the
        # test subject!
        subject.demonstrate_hello_world(demo)


# Another test, but this time with two logical flows.
class TestDemonstrateRenameProject:
    # The default logical flow is where we rename the project successfully.
    def test_renaming_the_project(self, ifc, demo):
        # This time, we describe an expectation that the demo tool should have
        # its get_project() function called with no attributes. When it is
        # called, we expect it to return "project" as a string.

        # This might sound strange. How is get_project implemented? Does it
        # actually return a string? We don't know, and we don't care. That's a
        # detail that our core isn't interested in. All our core is interested
        # in is that we get back a project - we're arbitrarily using a string to
        # represent it.
        demo.get_project().should_be_called().will_return("project")
        # Here, again, we're not interested in the details. However, we are
        # interested in checking that the project we previously retrieved is
        # passed verbatim into the Ifc tool.
        ifc.run("attribute.edit_attributes", product="project", attributes={"Name": "name"}).should_be_called()
        demo.clear_name_field().should_be_called()
        demo.hide_user_hints().should_be_called()
        # Let's test our test subject! Notice that just like the arbitrary
        # string "project", we've specified an arbitrary input string of "name".
        subject.demonstrate_rename_project(ifc, demo, name="name")

    # One alternative flow is when no name is provided. What happens then?
    def test_showing_a_hint_if_no_name_provided(self, ifc, demo):
        demo.show_user_hints().should_be_called()
        subject.demonstrate_rename_project(ifc, demo, name=None)

"""
