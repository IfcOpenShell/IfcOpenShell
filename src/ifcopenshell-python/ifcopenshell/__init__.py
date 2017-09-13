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

from __future__ import print_function

import os
import sys

if hasattr(os, 'uname'):
    platform_system = os.uname()[0].lower()
else:
    platform_system = 'windows'
    
if sys.maxsize == (1 << 31) - 1:
    platform_architecture = '32bit'
else:
    platform_architecture = '64bit'
    
python_version_tuple = tuple(sys.version.split(' ')[0].split('.'))

python_distribution = os.path.join(platform_system,
    platform_architecture,
    'python%s.%s' % python_version_tuple[:2])
sys.path.append(os.path.abspath(os.path.join(
    os.path.dirname(__file__),
    'lib', python_distribution)))

try:
    from . import ifcopenshell_wrapper
except Exception as e:
    if int(python_version_tuple[0]) == 2:
        # Only for py2, as py3 has exception chaining
        import traceback
        traceback.print_exc()
        print('-' * 64)
    raise ImportError("IfcOpenShell not built for '%s'" % python_distribution)
    
from . import guid
from .file import file
from .entity_instance import entity_instance

def open(fn=None):
    return file(ifcopenshell_wrapper.open(os.path.abspath(fn))) if fn else file()


def create_entity(type,*args,**kwargs):
    e = entity_instance(type)
    attrs = list(enumerate(args)) + \
        [(e.wrapped_data.get_argument_index(name), arg) for name, arg in kwargs.items()]
    for idx, arg in attrs: e[idx] = arg
    return e


version = ifcopenshell_wrapper.version()
schema_identifier = ifcopenshell_wrapper.schema_identifier()
get_supertype = ifcopenshell_wrapper.get_supertype
get_log = ifcopenshell_wrapper.get_log
