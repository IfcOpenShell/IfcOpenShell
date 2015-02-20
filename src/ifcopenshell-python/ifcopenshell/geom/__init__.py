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

def has_occ():
    try: import OCC.BRepTools
    except: return False
    return True


has_occ = has_occ()
wrap_shape_creation = lambda settings, shape: shape
if has_occ:
    import occ_utils as utils
    wrap_shape_creation = lambda settings, shape: utils.create_shape_from_serialization(shape) if getattr(settings, 'use_python_opencascade', False) else shape


# Subclass the settings module to provide an additional
# setting to enable pythonOCC when available
class settings(ifcopenshell_wrapper.settings):
    if has_occ:
        USE_PYTHON_OPENCASCADE = -1
        def set(self, *args):
            setting, value = args
            if setting == settings.USE_PYTHON_OPENCASCADE:
                self.set(settings.USE_BREP_DATA, value)
                self.set(settings.USE_WORLD_COORDS, value)
                self.set(settings.DISABLE_TRIANGULATION, value)
                self.use_python_opencascade = value
            else:
                ifcopenshell_wrapper.settings.set(self, *args)


# Hide templating precision to the user by choosing based on Python's 
# internal float type. This is probably always going to be a double.
for ty in (ifcopenshell_wrapper.iterator_single_precision, ifcopenshell_wrapper.iterator_double_precision):
    if ty.mantissa_size() == sys.float_info.mant_dig: 
        _iterator = ty


# Make sure people are able to use python's platform agnostic paths
class iterator(_iterator):
    def __init__(self, settings, filename):
        self.settings = settings
        _iterator.__init__(self, settings, os.path.abspath(filename))
    if has_occ:
        def get(self):
            return wrap_shape_creation(self.settings, _iterator.get(self))


def create_shape(settings, inst): 
    return wrap_shape_creation(settings, ifcopenshell_wrapper.create_shape(settings, inst.wrapped_data))


def iterate(settings, filename):
    it = iterator(settings, filename)
    if it.findContext():
        while True:
            yield it.get()
            if not it.next(): break


