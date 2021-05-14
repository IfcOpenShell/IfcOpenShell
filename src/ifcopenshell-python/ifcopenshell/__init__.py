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

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import sys

if hasattr(os, "uname"):
    platform_system = os.uname()[0].lower()
else:
    platform_system = "windows"

if sys.maxsize == (1 << 31) - 1:
    platform_architecture = "32bit"
else:
    platform_architecture = "64bit"

python_version_tuple = tuple(sys.version.split(" ")[0].split("."))

python_distribution = os.path.join(platform_system, platform_architecture, "python%s.%s" % python_version_tuple[:2])
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "lib", python_distribution)))

try:
    from . import ifcopenshell_wrapper
except Exception as e:
    if int(python_version_tuple[0]) == 2:
        # Only for py2, as py3 has exception chaining
        import traceback

        traceback.print_exc()
        print("-" * 64)
    raise ImportError("IfcOpenShell not built for '%s'" % python_distribution)

from . import guid
from .file import file
from .entity_instance import entity_instance

READ_ERROR = ifcopenshell_wrapper.file_open_status.READ_ERROR
NO_HEADER = ifcopenshell_wrapper.file_open_status.NO_HEADER
UNSUPPORTED_SCHEMA = ifcopenshell_wrapper.file_open_status.UNSUPPORTED_SCHEMA


class Error(Exception):
    pass


class SchemaError(Error):
    pass


def open(fn):
    f = ifcopenshell_wrapper.open(os.path.abspath(fn))
    if f.good():
        return file(f)
    else:
        exc, msg = {
            READ_ERROR: (IOError, "Unable to open file for reading"),
            NO_HEADER: (Error, "Unable to parse IFC SPF header"),
            UNSUPPORTED_SCHEMA: (
                SchemaError,
                "Unsupported schema: %s" % ",".join(f.header.file_schema.schema_identifiers),
            ),
        }[f.good().value()]
        raise exc(msg)


def create_entity(type, schema="IFC4", *args, **kwargs):
    e = entity_instance((schema, type))
    attrs = list(enumerate(args)) + [(e.wrapped_data.get_argument_index(name), arg) for name, arg in kwargs.items()]
    for idx, arg in attrs:
        e[idx] = arg
    return e


gcroot = []


def register_schema(schema):
    gcroot.append(schema)
    ifcopenshell_wrapper.register_schema(schema.schema)


from .main import *
