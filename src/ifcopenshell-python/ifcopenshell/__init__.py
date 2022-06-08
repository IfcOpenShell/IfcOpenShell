# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2021 Thomas Krijnen <thomas@aecgeeks.com>
#
# This file is part of IfcOpenShell.
#
# IfcOpenShell is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# IfcOpenShell is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with IfcOpenShell.  If not, see <http://www.gnu.org/licenses/>.

"""The entry module for IfcOpenShell

Typically used for opening an IFC via a filepath, or accessing one of the
submodules.

Example::

    import ifcopenshell
    print(ifcopenshell.version) # v0.7.0-1b1fd1e6
    model = ifcopenshell.open("/path/to/model.ifc")
"""

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
from .entity_instance import entity_instance, register_schema_attributes

READ_ERROR = ifcopenshell_wrapper.file_open_status.READ_ERROR
NO_HEADER = ifcopenshell_wrapper.file_open_status.NO_HEADER
UNSUPPORTED_SCHEMA = ifcopenshell_wrapper.file_open_status.UNSUPPORTED_SCHEMA


class Error(Exception):
    """Error used when a generic problem occurs"""
    pass


class SchemaError(Error):
    """Error used when an IFC schema related problem occurs"""
    pass


def open(fn):
    """Loads an IFC dataset from a filepath

    :param fn: Filepath to the IFC model
    :type fn: string
    :returns: A file object
    :rtype: ifcopenshell.file.file

    Example::

        ifc_file = ifcopenshell.open("/path/to/model.ifc")
    """
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
    """Creates a new IFC entity that does not belong to an IFC file object

    Note that it is more common to create entities within a existing file
    object. See :meth:`ifcopenshell.file.file.create_entity`.

    :param type: Case insensitive name of the IFC class
    :type type: string
    :param schema: The IFC schema identifier
    :type schema: string
    :param args: The positional arguments of the IFC class
    :param kwargs: The keyword arguments of the IFC class
    :returns: An entity instance
    :rtype: ifcopenshell.entity_instance.entity_instance

    Example::

        person = ifcopenshell.create_entity("IfcPerson") # #0=IfcPerson($,$,$,$,$,$,$,$)
        model = ifcopenshell.file()
        model.add(person) # #1=IfcPerson($,$,$,$,$,$,$,$)
    """
    e = entity_instance((schema, type))
    attrs = list(enumerate(args)) + [(e.wrapped_data.get_argument_index(name), arg) for name, arg in kwargs.items()]
    for idx, arg in attrs:
        e[idx] = arg
    return e


gcroot = []


def register_schema(schema):
    """Registers a custom IFC schema

    :param schema: A schema object
    :type schema: ifcopenshell.express.schema_class.SchemaClass

    Example::

        schema = ifcopenshell.express.parse("/path/to/ifc-custom.exp")
        ifcopenshell.register_schema(schema)
        ifcopenshell.file(schema="IFC_CUSTOM")
    """
    gcroot.append(schema)
    ifcopenshell_wrapper.register_schema(schema.schema)
    register_schema_attributes(schema.schema)


from .main import *
