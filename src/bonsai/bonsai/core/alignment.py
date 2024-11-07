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
def build_alignment(alignment):
    # We're telling the demo tool to set a message. We aren't interested how the
    # tool works, that's a detail. We aren't interested in the interface, like
    # where the message is shown. You can name these functions whatever you feel
    # best describes what's going on, like if you had to describe the feature to
    # someone else.
    alignment.build()

