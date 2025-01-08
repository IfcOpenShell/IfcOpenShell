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

"""Welcome to IfcOpenShell! IfcOpenShell provides a way to read and write IFCs.

IfcOpenShell can open IFC files, read entities (such as walls, buildings,
properties, systems, etc), edit attributes, write out ``.ifc`` files and more.

This module provides primitive functions to interact with IFC, including:

- For most users, you can open and read IFC models, see docs for :func:`open`.
  This returns an :class:`file` object representing the IFC model. You can then
  query the model to filter elements.
- For developers, you can query the schema itself, see docs for
  :func:`schema_by_name`. This returns a schema object which you can use to
  analyse the definitions of IFC classes and data types.

You may also be interested in:

- For model authoring and editing operations, see :mod:`ifcopenshell.api`.
- For extracting information from models, see :mod:`ifcopenshell.util`.
- For processing geometry, see :mod:`ifcopenshell.geom`.


For more details, consult https://docs.ifcopenshell.org/

Example:

.. code:: python

    import ifcopenshell

    print(ifcopenshell.version)

    model = ifcopenshell.open("/path/to/model.ifc")
    walls = model.by_type("IfcWall")

    for wall in walls:
        print(wall.Name)
"""
from __future__ import annotations
import os
import sys
import zipfile
import tempfile
from pathlib import Path
from typing import Optional, Union, TYPE_CHECKING, Any, overload, Literal

if TYPE_CHECKING:
    import ifcopenshell.express.schema_class


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
except Exception:
    raise ImportError("IfcOpenShell not built for '%s'" % python_distribution)

from .file import file
from . import guid
from .entity_instance import entity_instance, register_schema_attributes
from .sql import sqlite, sqlite_entity

# explicitly specify available imported symbols
# (it's a requirement for a typed library)
__all__ = [
    "ifcopenshell_wrapper",
    "file",
    "guid",
    "entity_instance",
    "sqlite",
    "sqlite_entity",
    "stream",
    "stream_entity",
]

try:
    from .stream import stream, stream_entity
except:
    pass


class Error(Exception):
    """Error used when a generic problem occurs"""

    pass


class SchemaError(Error):
    """Error used when an IFC schema related problem occurs"""

    pass


@overload
def open(
    path: Union[os.PathLike, str], format: Optional[str] = None, *, should_stream: Literal[False] = False
) -> Union[file, sqlite]: ...
@overload
def open(path: Union[os.PathLike, str], format: Optional[str] = None, *, should_stream: Literal[True]) -> stream: ...
@overload
def open(
    path: Union[os.PathLike, str], format: Optional[str] = None, *, should_stream: bool
) -> Union[file, sqlite, stream]: ...
def open(
    path: Union[os.PathLike, str], format: Optional[str] = None, should_stream: bool = False
) -> Union[file, sqlite, stream]:
    """Loads an IFC dataset from a filepath

    :param should_stream: Whether to open the file in streaming mode. Could be useful
        for reading large files.

    You can specify a file format. If no format is given, it is guessed from
    its extension. Currently supported specified format: .ifc | .ifcZIP |
    .ifcXML.

    You can then filter by element ID, class, etc, and subscript by id or guid.

    Example:

    .. code:: python

        model = ifcopenshell.open("/path/to/model.ifc")
        model = ifcopenshell.open("/path/to/model.ifcXML")
        model = ifcopenshell.open("/path/to/model.any_extension", ".ifc")

        products = model.by_type("IfcProduct")
        print(products[0].id(), products[0].GlobalId) # 122 2XQ$n5SLP5MBLyL442paFx
        print(products[0] == model[122] == model["2XQ$n5SLP5MBLyL442paFx"]) # True
    """
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(f"File does not exist: '{path}'.")
    if format is None:
        format = guess_format(path)
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
    return file(f)


def create_entity(type: str, schema: str = "IFC4", *args: Any, **kwargs: Any) -> entity_instance:
    """Creates a new IFC entity that does not belong to an IFC file object

    Note that it is more common to create entities within a existing file
    object. See :meth:`ifcopenshell.file.create_entity`.

    :param type: Case insensitive name of the IFC class
    :param schema: The IFC schema identifier
    :param args: The positional arguments of the IFC class
    :param kwargs: The keyword arguments of the IFC class
    :returns: An entity instance

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


def register_schema(schema: ifcopenshell.express.schema_class.SchemaClass) -> None:
    """Registers a custom IFC schema

    :param schema: A schema object

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


def schema_by_name(
    schema: Optional[str] = None,
    schema_version: Optional[tuple[int, ...]] = None,
) -> ifcopenshell_wrapper.schema_definition:
    """Returns an object allowing you to query the IFC schema itself

    :param schema: Which IFC schema to use, chosen from "IFC2X3", "IFC4",
        or "IFC4X3". These refer to the ISO approved versions of IFC.
    :param schema_version: If you want to specify an exact version of IFC
        that may not be an ISO approved version, use this argument instead
        of ``schema``. IFC versions on technical.buildingsmart.org are
        described using 4 integers representing the major, minor, addendum,
        and corrigendum number. For example, (4, 0, 2, 1) refers to IFC4
        ADD2 TC1, which is the official version approved by ISO when people
        refer to "IFC4". Generally you should not use this argument unless
        you are testing non-ISO IFC releases.
    :return: Schema definition object.
    """
    assert schema_version or schema, "Either schema or schema_version must be specified."
    if schema_version:
        prefixes = ("IFC", "X", "_ADD", "_TC")
        schema = "".join("".join(map(str, t)) if t[1] else "" for t in zip(prefixes, schema_version))
    else:
        schema = {"IFC4X3": "IFC4X3_ADD2"}.get(schema, schema)
    return ifcopenshell_wrapper.schema_by_name(schema)


def guess_format(path: Path) -> Union[str, None]:
    """Guesses the IFC format using file extension

    IFCs may be serialised as different formats. The most common is a ``.ifc``
    file, which is plaintext and stores data using the STEP Physical File
    format. IFC can also be stored as a Zipfile, XML, JSON, or SQL.

    This will return the canonical form of the format. For example, if a path
    has the extension of .xml or .ifcxml (case insensitive), it will return
    .ifcXML.

    Users generally won't call this function. The :func:`open` function uses
    this internally to guess the file format.

    :return: Either .ifc, .ifcZIP, .ifcXML, .ifcJSON, .ifcSQLite, or None.
    """
    suffix = path.suffix.lower()
    if suffix == ".ifc":
        return ".ifc"
    elif suffix in (".ifczip", ".zip"):
        return ".ifcZIP"
    elif suffix in (".ifcxml", ".xml"):
        return ".ifcXML"
    elif suffix in (".ifcjson", ".json"):
        return ".ifcJSON"
    elif suffix in (".ifcsqlite", ".sqlite", ".db"):
        return ".ifcSQLite"
    return None


version_core = ifcopenshell_wrapper.version()
__version__ = version = "0.0.0"
get_log = ifcopenshell_wrapper.get_log
