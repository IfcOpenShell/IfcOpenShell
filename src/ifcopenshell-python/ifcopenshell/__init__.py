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

Example:

.. code:: python

    import ifcopenshell
    print(ifcopenshell.version) # v0.7.0-1b1fd1e6
    model = ifcopenshell.open("/path/to/model.ifc")
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import sys
import tempfile
import zipfile
from pathlib import Path

import ifcopenshell.util.file

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
from .sql import sqlite, sqlite_entity
try:
    from .stream import stream, stream_entity
except: pass

READ_ERROR = ifcopenshell_wrapper.file_open_status.READ_ERROR
NO_HEADER = ifcopenshell_wrapper.file_open_status.NO_HEADER
UNSUPPORTED_SCHEMA = ifcopenshell_wrapper.file_open_status.UNSUPPORTED_SCHEMA


class Error(Exception):
    """Error used when a generic problem occurs"""
    pass


class SchemaError(Error):
    """Error used when an IFC schema related problem occurs"""
    pass


def open(path: "os.PathLike | str", format: str = None, should_stream: bool = False) -> file:
    """Loads an IFC dataset from a filepath

    You can specify a file format. If no format is given, it is guessed from its extension.
    Currently supported specified format : .ifc | .ifcZIP | .ifcXML

    Examples:
        model = ifcopenshell.open("/path/to/model.ifc")
        model = ifcopenshell.open("/path/to/model.ifcXML")
        model = ifcopenshell.open("/path/to/model.any_extension", ".ifc")
    """
    path = Path(path)
    if format is None:
        format = ifcopenshell.util.file.guess_format(path)
    if format == ".ifcXML":
        f = ifcopenshell_wrapper.parse_ifcxml(str(path.absolute()))
        if f:
            return file(f)
        raise IOError(f"Failed to parse .ifcXML file from {path}")
    if format == ".ifcZIP":
        with tempfile.TemporaryDirectory() as unzipped_path:
            with zipfile.ZipFile(path) as zf:
                for name in zf.namelist():
                    if Path(name).suffix.lower() in (".ifc", ".ifcxml"):
                        return open(zf.extract(name, unzipped_path))
                else:
                    raise LookupError(f"No .ifc or .ifcXML file found in {path}")
    if format == ".ifcSQLite":
        return sqlite(path)
    if should_stream:
        return stream(path)
    f = ifcopenshell_wrapper.open(str(path.absolute()))
    if f.good():
        return file(f)
    else:
        exc, msg = {
            READ_ERROR: (IOError, "Unable to open file for reading"),
            NO_HEADER: (Error, "Unable to parse IFC SPF header"),
            UNSUPPORTED_SCHEMA: (
                SchemaError,
                "Unsupported schema: %s"
                % ",".join(f.header.file_schema.schema_identifiers),
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

    Example:

    .. code:: python

        person = ifcopenshell.create_entity("IfcPerson") # #0=IfcPerson($,$,$,$,$,$,$,$)
        model = ifcopenshell.file()
        model.add(person) # #1=IfcPerson($,$,$,$,$,$,$,$)
    """
    e = entity_instance((schema, type))
    attrs = list(enumerate(args)) + [(e.wrapped_data.get_argument_index(name), arg) for name, arg in kwargs.items()]
    for idx, arg in attrs:
        e[idx] = arg
    return e


def register_schema(schema):
    """Registers a custom IFC schema

    :param schema: A schema object
    :type schema: ifcopenshell.express.schema_class.SchemaClass

    Example:

    .. code:: python

        schema = ifcopenshell.express.parse("/path/to/ifc-custom.exp")
        ifcopenshell.register_schema(schema)
        ifcopenshell.file(schema="IFC_CUSTOM")
    """
    schema.schema.this.disown()
    schema.disown()
    ifcopenshell_wrapper.register_schema(schema.schema)
    register_schema_attributes(schema.schema)


def schema_by_name(schema=None, schema_version=None):
    """Returns an object allowing you to query the IFC schema itself

    :param schema: Which IFC schema to use, chosen from "IFC2X3", "IFC4",
        or "IFC4X3". These refer to the ISO approved versions of IFC.
    :type schema: string
    :param schema_version: If you want to specify an exact version of IFC
        that may not be an ISO approved version, use this argument instead
        of ``schema``. IFC versions on technical.buildingsmart.org are
        described using 4 integers representing the major, minor, addendum,
        and corrigendum number. For example, (4, 0, 2, 1) refers to IFC4
        ADD2 TC1, which is the official version approved by ISO when people
        refer to "IFC4". Generally you should not use this argument unless
        you are testing non-ISO IFC releases.
    :type schema_version: tuple[int]
    """
    if schema_version:
        prefixes = ("IFC", "X", "_ADD", "_TC")
        schema = "".join("".join(map(str, t)) if t[1] else "" for t in zip(prefixes, schema_version))
    else:
        schema = {"IFC4X3": "IFC4X3_ADD1"}.get(schema, schema)
    return ifcopenshell_wrapper.schema_by_name(schema)


from .main import *
