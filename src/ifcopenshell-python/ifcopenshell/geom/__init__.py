###############################################################################
#                                                                             #
# This file is part of IfcOpenShell.                                          #
#                                                                             #
# IfcOpenShell is free software: you can redistribute it and/or modify        #
# it under the terms of the Lesser GNU General Public License as published by #
# the Free Software Foundation, either version 3.0 of the License, or         #
# (at your option) any later version.                                         #
#                                                                             #
# IfcOpenShell is distributed in the hope that it will be useful,             #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the                #
# Lesser GNU General Public License for more details.                         #
#                                                                             #
# You should have received a copy of the Lesser GNU General Public License    #
# along with this program. If not, see <http://www.gnu.org/licenses/>.        #
#                                                                             #
###############################################################################

import os
import sys

from .. import ifcopenshell_wrapper

settings = ifcopenshell_wrapper.settings

# Hide templating precision to the user by choosing based on Python's 
# internal float type. This is probably always going to be a double.
for ty in (ifcopenshell_wrapper.iterator_single_precision, ifcopenshell_wrapper.iterator_double_precision):
    if ty.mantissa_size() == sys.float_info.mant_dig: 
        _iterator = ty


# Make sure people are able to use python's platform agnostic paths
class iterator(_iterator):
    def __init__(self, settings, filename):
        _iterator.__init__(self, settings, os.path.abspath(filename))


def create_shape(settings, inst): 
    return ifcopenshell_wrapper.create_shape(settings, inst.wrapped_data)


def iterate(settings, filename):
    it = iterator(settings, filename)
    if it.findContext():
        while True:
            yield it.get()
            if not it.next(): break
