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

from __future__ import annotations
import os
import re
import numbers
import time
import zipfile
import functools
import ifcopenshell
import weakref
import types
from pathlib import Path
from typing import Any, Optional, TYPE_CHECKING, Union, overload, Literal, TypedDict
from collections.abc import Callable, Generator
from typing_extensions import assert_never

from . import ifcopenshell_wrapper
from .entity_instance import entity_instance

from ifcopenshell.util.mvd_info import MvdInfo, LARK_AVAILABLE

if TYPE_CHECKING:
    import ifcopenshell.util.schema

    InverseReference = tuple[int, Any]
    ElementInverses = dict[int, list[InverseReference]]

    class CreateOperation(TypedDict):
        action: Literal["create"]
        value: Any

    class EditOperation(TypedDict):
        action: Literal["edit"]
        id: int
        index: int
        old: Any
        new: Any

    class DeleteOperation(TypedDict):
        action: Literal["delete"]
        inverses: ElementInverses
        value: Any

    class BatchDeleteOperation(TypedDict):
        action: Literal["batch_delete"]
        inverses: ElementInverses

    TransactionOperation = Union[CreateOperation, EditOperation, DeleteOperation, BatchDeleteOperation]

HEADER_FIELDS = {
    "file_description": [
        "description",
        "implementation_level",
    ],
    "file_name": [
        "name",
        "time_stamp",
        "author",
        "organization",
        "preprocessor_version",
        "originating_system",
        "authorization",
    ],
}


class UndoSystemError(Exception):
    def __init__(self, message: str, transaction: Transaction):
        super().__init__(message)
        self.transaction = transaction


class Transaction:
    operations: list[TransactionOperation]
    batch_inverses: list[ElementInverses]
    batch_delete_ids: set[int]

    def __init__(self, ifc_file: file):
        self.file: file = ifc_file
        self.operations = []
        self.is_batched = False
        self.batch_delete_index = 0
        self.batch_delete_ids = set()
        self.batch_inverses = []

    def serialise_entity_instance(self, element: ifcopenshell.entity_instance) -> dict[str, Any]:
        info = element.get_info()
        for key, value in info.items():
            info[key] = self.serialise_value(element, value)
        return info

    def serialise_value(self, element, value) -> Any:
        return element.walk(
            lambda v: isinstance(v, entity_instance),
            lambda v: {"id": v.id()} if v.id() else {"type": v.is_a(), "value": v.wrappedValue},
            value,
        )

    def unserialise_value(self, element, value) -> Any:
        return element.walk(
            lambda v: isinstance(v, dict),
            lambda v: self.file.by_id(v["id"]) if v.get("id") else self.file.create_entity(v["type"], v["value"]),
            value,
        )

    def batch(self) -> None:
        self.is_batched = True
        self.batch_delete_index = len(self.operations)
        self.batch_delete_ids = set()
        self.batch_inverses = []

    def unbatch(self) -> None:
        for inverses in self.batch_inverses:
            if inverses:
                self.operations.insert(self.batch_delete_index, {"action": "batch_delete", "inverses": inverses})
        self.is_batched = False
        self.batch_delete_index = 0
        self.batch_delete_ids = set()
        self.batch_inverses = []

    def store_create(self, element: ifcopenshell.entity_instance) -> None:
        if element.id():
            self.operations.append({"action": "create", "value": self.serialise_entity_instance(element)})

    def store_edit(self, element: ifcopenshell.entity_instance, index: int, value: Any) -> None:
        if element.id():
            self.operations.append(
                {
                    "action": "edit",
                    "id": element.id(),
                    "index": index,
                    "old": self.serialise_value(element, element[index]),
                    "new": self.serialise_value(element, value),
                }
            )

    def store_delete(self, element: ifcopenshell.entity_instance) -> None:
        inverses = {}
        if self.is_batched:
            if element.id() not in self.batch_delete_ids:
                self.batch_inverses.append(self.get_element_inverses(element))
            self.batch_delete_ids.add(element.id())
        else:
            inverses = self.get_element_inverses(element)
        self.operations.append(
            {"action": "delete", "inverses": inverses, "value": self.serialise_entity_instance(element)}
        )

    def get_element_inverses(self, element: ifcopenshell.entity_instance) -> ElementInverses:
        inverses: ElementInverses = {}
        for inverse in self.file.get_inverse(element):
            inverse_references: list[InverseReference] = []
            for i, attribute in enumerate(inverse):
                if self.has_element_reference(attribute, element):
                    inverse_references.append((i, self.serialise_value(inverse, attribute)))
            inverses[inverse.id()] = inverse_references
        return inverses

    def has_element_reference(self, value: Any, element: ifcopenshell.entity_instance) -> bool:
        if isinstance(value, (tuple, list)):
            for v in value:
                if self.has_element_reference(v, element):
                    return True
            return False
        return value == element

    def rollback(self) -> None:
        for operation in self.operations[::-1]:
            if operation["action"] == "create":
                element = self.file.by_id(operation["value"]["id"])
                if hasattr(element, "GlobalId") and element.GlobalId is None:
                    # hack, otherwise ifcopenshell gets upset
                    element.GlobalId = "x"
                self.file.remove(element)
            elif operation["action"] == "edit":
                element = self.file.by_id(operation["id"])
                try:
                    element[operation["index"]] = self.unserialise_value(element, operation["old"])
                except:
                    # Catch discrepancy where IfcOpenShell creates but doesn't allow editing of invalid values
                    pass
            elif operation["action"] == "delete":
                e = self.file.create_entity(operation["value"]["type"], id=operation["value"]["id"])
                for k, v in operation["value"].items():
                    try:
                        setattr(e, k, self.unserialise_value(e, v))
                    except:
                        # Catch discrepancy where IfcOpenShell creates but doesn't allow editing of invalid values
                        pass
                for inverse_id, data in operation["inverses"].items():
                    inverse = self.file.by_id(inverse_id)
                    for index, value in data:
                        inverse[index] = self.unserialise_value(inverse, value)
            elif operation["action"] == "batch_delete":
                for inverse_id, data in operation["inverses"].items():
                    inverse = self.file.by_id(inverse_id)
                    for index, value in data:
                        inverse[index] = self.unserialise_value(inverse, value)
            else:
                assert_never(operation["action"])

    def commit(self) -> None:
        for operation in self.operations:
            if operation["action"] == "create":
                e = self.file.create_entity(operation["value"]["type"], id=operation["value"]["id"])
                for k, v in operation["value"].items():
                    try:
                        setattr(e, k, self.unserialise_value(e, v))
                    except:
                        # Catch discrepancy where IfcOpenShell creates but doesn't allow editing of invalid values
                        pass
            elif operation["action"] == "edit":
                element = self.file.by_id(operation["id"])
                element[operation["index"]] = self.unserialise_value(element, operation["new"])
            elif operation["action"] == "delete":
                element = self.file.by_id(operation["value"]["id"])
                self.file.remove(element)
            elif operation["action"] == "batch_delete":
                pass
            else:
                assert_never(operation["action"])


file_dict: dict[int, tuple[weakref.ReferenceType[file], int]] = {}
"""Mapping of internal IfcFile pointer address to existing ``ifcopenshell.file``
and the timestamp when it was created.

Needed only to quickly access related from ``entity_instance`` it's ``file``.
"""

READ_ERROR = ifcopenshell_wrapper.file_open_status.READ_ERROR
NO_HEADER = ifcopenshell_wrapper.file_open_status.NO_HEADER
UNSUPPORTED_SCHEMA = ifcopenshell_wrapper.file_open_status.UNSUPPORTED_SCHEMA
INVALID_SYNTAX = ifcopenshell_wrapper.file_open_status.INVALID_SYNTAX

# TODO: Workaround for old builds, remove after build stabilizes.
try:
    UNKNOWN = ifcopenshell_wrapper.file_open_status.UNKNOWN
except:
    UNKNOWN = 5  # Workaround

import struct


def consume_buffer(val, inner):
    while val:
        s = struct.unpack("@q", val[:8])[0]
        val = val[8:]
        yield inner(val[0:s])
        val = val[s:]


binary_deserializers = (
    lambda __, _: None,
    lambda __, _: None,
    lambda __, val: struct.unpack("@i", val)[0],
    lambda __, val: val[0] == 1,
    # @todo 3 state
    lambda __, val: val[0] == 1,
    lambda __, val: struct.unpack("@d", val)[0],
    lambda __, val: val.decode("utf-8"),
    lambda __, val: val.decode("utf-8"),
    lambda storage, val: ifcopenshell_wrapper.schema_by_name(storage.schema_identifier)
    .declarations()[struct.unpack("@q", val[:8])[0]]
    .enumeration_items()[struct.unpack("@q", val[8:])[0]],
    lambda storage, val: storage.by_id((val[0] == 105, struct.unpack("@q", val[1:])[0])),
    lambda __, _: (),
    lambda __, val: struct.unpack("@" + "i" * (len(val) // 4), val),
    lambda __, val: struct.unpack("@" + "d" * (len(val) // 8), val),
    lambda __, val: tuple(consume_buffer(val, lambda inner: inner.decode("utf-8"))),
    lambda __, val: tuple(consume_buffer(val, lambda inner: inner.decode("utf-8"))),
    lambda storage, val: tuple(
        storage.by_id((val[i * 9] == 105, struct.unpack("@q", val[i * 9 + 1 : i * 9 + 9])[0]))
        for i in range(len(val) // 9)
    ),
    lambda __, _: ((),),
    lambda __, val: tuple(
        consume_buffer(val, lambda inner: struct.unpack("@" + 105 * (len(inner) // struct.calcsize("@i")), inner))
    ),
    lambda __, val: tuple(
        consume_buffer(val, lambda inner: struct.unpack("@" + "d" * (len(inner) // struct.calcsize("@d")), inner))
    ),
    lambda storage, val: tuple(
        consume_buffer(
            val,
            lambda inner: tuple(
                storage.by_id((inner[i * 9] == 105, struct.unpack("@q", inner[i * 9 + 1 : i * 9 + 9])[0]))
                for i in range(len(inner) // 9)
            ),
        )
    ),
)


@functools.cache
def attribute_lookup(schema_name, entity_name):
    decl = ifcopenshell_wrapper.schema_by_name(schema_name).declaration_by_name(entity_name)
    attributes = decl.as_entity().all_attributes()
    di = {v: k for k, v in enumerate(a.name() for a in attributes)}
    all_inverses = decl.as_entity().all_inverse_attributes()
    for inv in all_inverses:

        def visit(decl):
            yield decl.index_in_schema()
            for ty in decl.subtypes():
                yield from visit(ty)

        attribute_index = inv.entity_reference().attribute_index(inv.attribute_reference())
        entity_indices = list(visit(inv.entity_reference()))
        di[inv.name()] = (entity_indices, attribute_index)
    return di


@functools.cache
def entity_name_lookup(schema_name, index):
    return ifcopenshell_wrapper.schema_by_name(schema_name).declarations()[index].name()


class rocksdb_lazy_instance:
    __slots__ = ("storage", "name")

    def _transform_value(self, val: bytes) -> Any:
        if not val:
            return None
        # ord('A') is 65
        return binary_deserializers[val[0] - 65](self.storage, val[1:])

    def __init__(self, storage, name):
        self.storage = storage
        self.name = name

    @functools.cache
    def is_a(self):
        if self.name.startswith("h|"):
            return self.name[2:]
        idx = struct.unpack("@q", self.storage.read(f"{self.name}|_"))[0]
        return entity_name_lookup(self.storage.schema_identifier, idx)

    def __getattr__(self, name):
        attr = attribute_lookup(self.storage.schema_identifier, self.is_a()).get(name)
        if isinstance(attr, int):
            return self[attr]
        else:
            entity_indices, attribute_index = attr

            def _():
                for index_in_schema in entity_indices:
                    buffer = self.storage.read(f"v|{self.name[2:]}|{index_in_schema}|{attribute_index}") or b""
                    yield from map(self.storage.by_id, struct.unpack("<" + "I" * (len(buffer) // 4), buffer))

            return list(_())

    def __getitem__(self, index):
        return self._transform_value(self.storage.read(f"{self.name}|{index}"))

    @functools.cache
    def __len__(self):
        return (
            max(
                map(
                    int,
                    filter(
                        lambda s: s.isdigit(),
                        (k.split(b"|")[2] for k, v in self.storage.prefix(f"{self.name}|").items()),
                    ),
                ),
                default=-1,
            )
            + 1
        )

    def __iter__(self):
        for i in range(len(self)):
            yield self[i]

    def __repr__(self):
        pre = f"#{self.name[2:]}=" if self.name.startswith("i|") else ""

        def val_repr(val):
            if isinstance(val, rocksdb_lazy_instance):
                if val.name[0] == "i":
                    return f"#{val.name[2:]}"
                else:
                    return repr(val)
            elif isinstance(val, (tuple, list)):
                return f'({",".join(map(val_repr, val))})'
            elif val is None:
                return "$"
            else:
                return repr(val)

        return f'{pre}{self.is_a()}({",".join(map(val_repr, self))})'

    def id(self):
        if self.name.startswith("i|"):
            return int(self.name[2:])
        else:
            # compatibility with C++
            return 0

    def __bool__(self):
        return len(self) > 0

    @property
    def _comparison_tuple(self):
        return self.storage.file.file_pointer(), self.name

    def __eq__(self, other):
        if not isinstance(other, rocksdb_lazy_instance):
            return False
        return self._comparison_tuple == other._comparison_tuple

    def __hash__(self):
        return hash(self._comparison_tuple)


class rocksdb_file_storage:
    def __init__(self, file, prefix=""):
        self.file = file
        self._prefix = prefix

    def items(self):
        it = self.file.wrapped_data.key_value_store_iter(self._prefix)
        while it and it.valid():
            yield it.key(), it.value()
            it.next()

    def read(self, key):
        return self.file.wrapped_data.key_value_store_query(key)

    def by_id(self, name):
        if isinstance(name, tuple):
            inst = rocksdb_lazy_instance(self, f'{"i" if name[0] else "t"}|{name[1]}')
        else:
            inst = rocksdb_lazy_instance(self, f"i|{name}")
        if not inst:
            raise KeyError(f"Instance with name {name} not found in file")
        return inst

    def by_type(self, ty: str):
        def visit(decl):
            yield decl.index_in_schema()
            for ty in decl.subtypes():
                yield from visit(ty)

        decl = ifcopenshell_wrapper.schema_by_name(self.schema_identifier).declaration_by_name(ty)

        def _():
            for index in visit(decl):
                buff = self.read(f"t|{index}") or b""
                yield from map(self.by_id, struct.unpack("@" + "q" * (len(buff) // 8), buff))

        return list(_())

    __getitem__ = by_id

    def __iter__(self):
        previous = None
        for k, v in self.items():
            if k.startswith(b"i|"):
                name = int(k[2:].split(b"|")[0])
                if name != previous:
                    previous = name
                    yield rocksdb_lazy_instance(self, f"i|{name}")

    def prefix(self, prefix):
        return rocksdb_file_storage(self.file, self._prefix + prefix)

    @functools.cached_property
    def schema_identifier(self):
        """Full IFC schema version: IFC2X3_TC1, IFC4_ADD2, IFC4X3_ADD2, etc."""
        return rocksdb_lazy_instance(self, f"h|file_schema")[0][0]

    @functools.cached_property
    def schema(self) -> ifcopenshell.util.schema.IFC_SCHEMA:
        """General IFC schema version: IFC2X3, IFC4, IFC4X3."""
        prefixes = ("IFC", "X", "_ADD", "_TC")
        reg = "".join(f"(?P<{s}>{s}\\d+)?" for s in prefixes)
        match = re.match(reg, self.schema_identifier)
        version_tuple = tuple(
            map(
                lambda pp: int(pp[1][len(pp[0]) :]) if pp[1] else None,
                ((p, match.group(p)) for p in prefixes),
            )
        )
        return "".join("".join(map(str, t)) if t[1] else "" for t in zip(prefixes, version_tuple[0:2]))


class file_header:
    def __init__(self, file, header_data):
        self.file = file
        self.header_data = header_data

    @property
    def file_description(self) -> entity_instance:
        return entity_instance.wrap_value(self.header_data.file_description_py(), file=self.file)

    @property
    def file_name(self) -> entity_instance:
        return entity_instance.wrap_value(self.header_data.file_name_py(), file=self.file)

    @property
    def file_schema(self) -> entity_instance:
        return entity_instance.wrap_value(self.header_data.file_schema_py(), file=self.file)


class file:
    """Base class for containing IFC files.

    Class has instance methods for filtering by element Id, Type, etc.
    Instantiated objects can be subscripted by Id or Guid

    Example:

    .. code:: python

        model = ifcopenshell.open(file_path)
        products = model.by_type("IfcProduct")
        print(products[0].id(), products[0].GlobalId) # 122 2XQ$n5SLP5MBLyL442paFx
        print(products[0] == model[122] == model["2XQ$n5SLP5MBLyL442paFx"]) # True
    """

    wrapped_data: ifcopenshell_wrapper.file
    units: dict[str, entity_instance] = {}
    history_size: int = 64
    history: list[Transaction]
    """Chronological order - from oldest to newest."""
    future: list[Transaction]
    """Reversed chronological order - from newest to oldest."""

    to_delete: Union[set[ifcopenshell.entity_instance], None] = None
    """Entities for batch removal."""

    def __init__(
        self,
        f: Optional[ifcopenshell_wrapper.file] = None,
        schema: Optional[ifcopenshell.util.schema.IFC_SCHEMA] = None,
        schema_version: Optional[tuple[int, int, int, int]] = None,
    ):
        """Create a new blank IFC model

        This IFC model does not have any entities in it yet. See the
        ``create_entity`` function for how to create new entities. All data is
        stored in memory. If you wish to write the IFC model to disk, see the
        ``write`` function.

        :param f: The underlying IfcOpenShell file object to be wrapped. This
            is an internal implementation detail and should generally be left
            as None by users.
        :param schema: Which IFC schema to use, chosen from "IFC2X3", "IFC4",
            or "IFC4X3". These refer to the ISO approved versions of IFC.
            Defaults to "IFC4" if not specified, which is currently recommended
            for all new projects.
        :param schema_version: If you want to specify an exact version of IFC
            that may not be an ISO approved version, use this argument instead
            of ``schema``. IFC versions on technical.buildingsmart.org are
            described using 4 integers representing the major, minor, addendum,
            and corrigendum number. For example, (4, 0, 2, 1) refers to IFC4
            ADD2 TC1, which is the official version approved by ISO when people
            refer to "IFC4". Generally you should not use this argument unless
            you are testing non-ISO IFC releases.

        Example:

        .. code:: python

            # Create a new IFC4 model, create a wall, then save it to an IFC-SPF file.
            model = ifcopenshell.file()
            model.create_entity("IfcWall")
            model.write("/path/to/model.ifc")

            # Create a new IFC4X3 model
            model = ifcopenshell.file(schema="IFC4X3")

            # A poweruser testing out a particular version of IFC4X3
            model = ifcopenshell.file(schema_version=(4, 3, 0, 1))
        """
        if schema_version:
            prefixes = ("IFC", "X", "_ADD", "_TC")
            schema = "".join("".join(map(str, t)) if t[1] else "" for t in zip(prefixes, schema_version))
        else:
            schema = {"IFC4X3": "IFC4X3_ADD2"}.get(schema, schema)
        if f is not None:
            self.wrapped_data = f
            if not f.good():
                from . import Error, SchemaError

                exc, msg = {
                    READ_ERROR: lambda: (IOError, "Unable to open file for reading"),
                    NO_HEADER: lambda: (Error, "Unable to parse IFC SPF header"),
                    UNSUPPORTED_SCHEMA: lambda: (
                        SchemaError,
                        "Unsupported schema: %s" % ",".join(self.header.file_schema.schema_identifiers),
                    ),
                    INVALID_SYNTAX: lambda: (Error, "Syntax error during parse, check logs"),
                    # This is the case when passing uninitialized_tag
                    UNKNOWN: lambda: (None, None),
                }[f.good().value()]()
                if exc is not None:
                    raise exc(msg)
        else:
            args = filter(None, [schema])
            args = map(ifcopenshell_wrapper.schema_by_name, args)
            self.wrapped_data = ifcopenshell_wrapper.file(*args)
        self.history = []
        self.future = []
        self.transaction: Optional[Transaction] = None

        # we store a tuple of C++ file pointer address and creation time stamp so that
        # when memory addresses get recycled we do not run into collisions when the
        # address is used as a cache key.
        file_dict[self.wrapped_data.file_pointer()] = (weakref.ref(self), time.monotonic_ns())

    @property
    def identifier(self) -> tuple[int, int]:
        """Pair of C++ file pointer address and creation time stamp to uniquely identify a file
        over the life time of ifcopenshell module that should be mostly safe except in pathological
        cases

        Returns:
            tuple[int, int]: Pair of C++ file pointer address and creation time stamp
        """
        return (self.wrapped_data.file_pointer(), file_dict[self.wrapped_data.file_pointer()][1])

    def __del__(self) -> None:
        # Avoid infinite recursion if file is failed to initialize
        # and wrapped_data is unset.
        if "wrapped_data" not in dir(self):
            return
        del file_dict[self.file_pointer()]

    def set_history_size(self, size: int) -> None:
        self.history_size = size
        while len(self.history) > self.history_size:
            self.history.pop(0)

    def begin_transaction(self) -> None:
        if self.history_size:
            self.transaction = Transaction(self)

    def end_transaction(self) -> None:
        if self.transaction:
            self.history.append(self.transaction)
            if len(self.history) > self.history_size:
                self.history.pop(0)
            self.future = []
            self.transaction = None

    def discard_transaction(self) -> None:
        if self.transaction:
            self.transaction.rollback()
        self.transaction = None

    def undo(self) -> None:
        if not self.history:
            return
        transaction = self.history.pop()
        try:
            transaction.rollback()
        except Exception as e:
            raise UndoSystemError("Error during transaction undo.", transaction) from e
        self.future.append(transaction)

    def redo(self) -> None:
        if not self.future:
            return
        transaction = self.future.pop()
        try:
            transaction.commit()
        except Exception as e:
            raise UndoSystemError("Error during transaction redo.", transaction) from e
        self.history.append(transaction)

    def create_entity(self, type: str, *args: Any, **kwargs: Any) -> ifcopenshell.entity_instance:
        """Create a new IFC entity in the file.

        You can also use dynamic methods similar to `ifc_file.createIfcWall(...)`
        to create IFC entities. They work exactly the same as if you would do
        `ifc_file.create_entity("IfcWall", ...)` but the resulting typing
        is not as accurate as for `create_entity` due to a dynamic nature
        of those methods.

        :param type: Case insensitive name of the IFC class
        :param args: The positional arguments of the IFC class
        :param kwargs: The keyword arguments of the IFC class
        :returns: An entity instance

        Example:

        .. code:: python

            f = ifcopenshell.file()
            f.create_entity("IfcPerson")
            # >>> #1=IfcPerson($,$,$,$,$,$,$,$)
            f.create_entity("IfcPerson", "Foobar")
            # >>> #2=IfcPerson('Foobar',$,$,$,$,$,$,$)
            f.create_entity("IfcPerson", Identification="Foobar")
            # >>> #3=IfcPerson('Foobar',$,$,$,$,$,$,$)
        """
        eid = kwargs.pop("id", -1)

        e = entity_instance((self.schema_identifier, type), self)

        # Create pairs of {attribute index, attribute value}.
        # Keyword arguments are mapped to their corresponding
        # numeric index with get_argument_index().

        # @todo we should probably check that values for
        # attributes are not passed as duplicates using
        # both regular arguments and keyword arguments.
        kwargs_attrs = [(e.wrapped_data.get_argument_index(name), arg) for name, arg in kwargs.items()]
        attrs = list(enumerate(args)) + kwargs_attrs

        if len(attrs) > len(e):
            raise ValueError(
                "entity instance of type '%s' has only %s attributes but %s attributes were provided."
                % (e.is_a(True), len(e), len(attrs))
            )

        # Don't store these attributes as transactions
        # as the creation it self is already stored with
        # it's arguments
        if attrs:
            transaction = self.transaction
            self.transaction = None

        try:
            for idx, arg in attrs:
                e[idx] = arg
        except IndexError:
            invalid_attrs = []
            for (attr_index, _), attr_name in zip(kwargs_attrs, kwargs):
                if attr_index == 0xFFFFFFFF:
                    invalid_attrs.append(attr_name)
            raise ValueError(
                "entity instance of type '%s' doesn't have the following attributes: %s."
                % (e.is_a(True), ", ".join(invalid_attrs))
            )

        # Restore transaction status
        if attrs:
            self.transaction = transaction

        # Once the values are populated add the instance
        # to the file.
        self.wrapped_data.add(e.wrapped_data, eid)

        # The file container now handles the lifetime of
        # this instance. Tell SWIG that it is no longer
        # the owner.
        e.wrapped_data.this.disown()

        if self.transaction:
            self.transaction.store_create(e)

        return e

    @property
    def schema(self) -> ifcopenshell.util.schema.IFC_SCHEMA:
        """General IFC schema version: IFC2X3, IFC4, IFC4X3."""
        prefixes = ("IFC", "X", "_ADD", "_TC")
        reg = "".join(f"(?P<{s}>{s}\\d+)?" for s in prefixes)
        match = re.match(reg, self.wrapped_data.schema)
        version_tuple = tuple(
            map(
                lambda pp: int(pp[1][len(pp[0]) :]) if pp[1] else None,
                ((p, match.group(p)) for p in prefixes),
            )
        )
        return "".join("".join(map(str, t)) if t[1] else "" for t in zip(prefixes, version_tuple[0:2]))

    @property
    def schema_identifier(self) -> str:
        """Full IFC schema version: IFC2X3_TC1, IFC4_ADD2, IFC4X3_ADD2, etc."""
        return self.wrapped_data.schema

    @property
    def schema_version(self) -> tuple[int, int, int, int]:
        """Numeric representation of the full IFC schema version.

        E.g. IFC4X3_ADD2 is represented as (4, 3, 2, 0).
        """
        schema = self.wrapped_data.schema
        version = []
        for prefix in ("IFC", "X", "_ADD", "_TC"):
            number = re.search(prefix + r"(\d)", schema)
            version.append(int(number.group(1)) if number else 0)
        return tuple(version)

    @property
    def mvd(self):
        if not LARK_AVAILABLE:
            return None
        return MvdInfo(self.header)

    def __getattr__(self, attr) -> Union[Any, Callable[..., ifcopenshell.entity_instance]]:
        if attr[0:6] == "create":
            return functools.partial(self.create_entity, attr[6:])
        else:
            return getattr(self.wrapped_data, attr)

    def __getitem__(self, key: Union[numbers.Integral, str, bytes]) -> entity_instance:
        if isinstance(key, numbers.Integral):
            return entity_instance(self.wrapped_data.by_id(key), self)
        elif isinstance(key, (str, bytes)):
            return entity_instance(self.wrapped_data.by_guid(str(key)), self)

    def by_id(self, id: int) -> ifcopenshell.entity_instance:
        """Return an IFC entity instance filtered by IFC ID.

        :param id: STEP numerical identifier

        :raises RuntimeError: If `id` is not found.

        :returns: An ifcopenshell.entity_instance
        """
        return self[id]

    def by_guid(self, guid: str) -> ifcopenshell.entity_instance:
        """Return an IFC entity instance filtered by IFC GUID.

        :param guid: GlobalId value in 22-character encoded form

        :raises RuntimeError: If `guid` is not found.

        :returns: An ifcopenshell.entity_instance
        """
        return self[guid]

    def add(self, inst: ifcopenshell.entity_instance, _id: int = None) -> ifcopenshell.entity_instance:
        """Adds an entity including any dependent entities to an IFC file.
        If the entity already exists, it is not re-added. Existence of entity is checked by it's `.identity()`.

        :param inst: The entity instance to add
        :returns: An ifcopenshell.entity_instance
        """

        if self.transaction:
            max_id = self.wrapped_data.getMaxId()
        inst.wrapped_data.this.disown()
        result = entity_instance(self.wrapped_data.add(inst.wrapped_data, -1 if _id is None else _id), self)
        if self.transaction:
            added_elements = [e for e in self.traverse(result) if e.id() > max_id]
            [self.transaction.store_create(e) for e in reversed(added_elements)]
        return result

    def by_type(self, type: str, include_subtypes=True) -> list[ifcopenshell.entity_instance]:
        """Return IFC objects filtered by IFC Type and wrapped with the entity_instance class.

        If an IFC type class has subclasses, all entities of those subclasses are also returned.

        :param type: The case insensitive type of IFC class to return.
        :param include_subtypes: Whether or not to return subtypes of the IFC class

        :raises RuntimeError: If `type` is not found in IFC schema.

        :returns: A list of ifcopenshell.entity_instance objects
        """
        if include_subtypes:
            return [entity_instance(e, self) for e in self.wrapped_data.by_type(type)]
        return [entity_instance(e, self) for e in self.wrapped_data.by_type_excl_subtypes(type)]

    def traverse(
        self, inst: ifcopenshell.entity_instance, max_levels: Optional[int] = None, breadth_first: bool = False
    ) -> list[ifcopenshell.entity_instance]:
        """Get a list of all referenced instances for a particular instance including itself

        :param inst: The entity instance to get all sub instances
        :param max_levels: How far deep to recursively fetch sub instances. None or -1 means infinite.
        :param breadth_first: Whether to use breadth-first search, the default is depth-first.
        :returns: A list of ifcopenshell.entity_instance objects
        """
        if max_levels is None:
            max_levels = -1

        if breadth_first:
            fn = self.wrapped_data.traverse_breadth_first
        else:
            fn = self.wrapped_data.traverse

        return [entity_instance(e, self) for e in fn(inst.wrapped_data, max_levels)]

    @overload
    def get_inverse(
        self,
        inst: ifcopenshell.entity_instance,
        allow_duplicate: Literal[False] = False,
        with_attribute_indices: bool = False,
    ) -> set[ifcopenshell.entity_instance]: ...
    @overload
    def get_inverse(
        self,
        inst: ifcopenshell.entity_instance,
        allow_duplicate: Literal[True],
        with_attribute_indices: bool = False,
    ) -> list[ifcopenshell.entity_instance]: ...
    @overload
    def get_inverse(
        self,
        inst: ifcopenshell.entity_instance,
        allow_duplicate: bool,
        with_attribute_indices: bool = False,
    ) -> Union[list[ifcopenshell.entity_instance], set[ifcopenshell.entity_instance]]: ...
    def get_inverse(
        self,
        inst: ifcopenshell.entity_instance,
        allow_duplicate: bool = False,
        with_attribute_indices: bool = False,
    ) -> Union[list[ifcopenshell.entity_instance], set[ifcopenshell.entity_instance]]:
        """Return a list of entities that reference this entity

        Warning: this is a slow function, especially when there is a large
        number of inverses (such as for a shared owner history). If you are
        only interested in the total number of inverses (typically 0, 1, or N),
        consider using :func:`get_total_inverses`.

        :param inst: The entity instance to get inverse relationships
        :param allow_duplicate: Returns a `list` when True, `set` when False
        :param with_attribute_indices: Returns pairs of <i, idx>
           where i[idx] is inst or contains inst. Requires allow_duplicate=True
        :returns: A list or set of ifcopenshell.entity_instance objects.
        """
        if with_attribute_indices and not allow_duplicate:
            raise ValueError("with_attribute_indices requires allow_duplicate to be True")

        inverses = [entity_instance(e, self) for e in self.wrapped_data.get_inverse(inst.wrapped_data)]

        if allow_duplicate:
            if with_attribute_indices:
                idxs = self.wrapped_data.get_inverse_indices(inst.wrapped_data)
                # TODO: include in typing.
                return list(zip(inverses, idxs))
            else:
                return inverses

        return set(inverses)

    def get_total_inverses(self, inst: ifcopenshell.entity_instance) -> int:
        """Returns the number of entities that reference this entity

        This is equivalent to `len(model.get_inverse(element))`, but
        significantly faster.

        :param inst: The entity instance to get inverse relationships
        :returns: The total number of references
        """
        return self.wrapped_data.get_total_inverses(inst.wrapped_data)

    def remove(self, inst: ifcopenshell.entity_instance) -> None:
        """Deletes an IFC object in the file.

        Attribute values in other entity instances that reference the deleted
        object will be set to null. In the case of a list or set of references,
        the reference to the deleted will be removed from the aggregate.

        :param inst: The entity instance to delete
        """
        if self.transaction:
            self.transaction.store_delete(inst)
        return self.wrapped_data.remove(inst.wrapped_data)

    def batch(self):
        """Low-level mechanism to speed up deletion of large subgraphs"""
        if self.transaction:
            self.transaction.batch()
        return self.wrapped_data.batch()

    def unbatch(self):
        """Low-level mechanism to speed up deletion of large subgraphs"""
        if self.transaction:
            self.transaction.unbatch()
        return self.wrapped_data.unbatch()

    def __iter__(self) -> Generator[ifcopenshell.entity_instance, None, None]:
        return iter(self[id] for id in self.wrapped_data.entity_names())

    def assign_header_from(self, other: ifcopenshell.file) -> None:
        for k, vs in HEADER_FIELDS.items():
            for v in vs:
                try:
                    setattr(getattr(self.header, k), v, getattr(getattr(other.header, k), v))
                except:
                    pass  # Header is invalid

    def write(self, path: os.PathLike | str, format: Optional[str] = None, zipped: bool = False) -> None:
        """Write ifc model to file.

        :param format: Force use of a specific format. Guessed from file name
            if None.  Supported formats : .ifc, .ifcZIP (equivalent to
            format=".ifc" with zipped=True)
        :param zipped: zip the file after it is written

        Example:

        .. code:: python

            model.write("path/to/model.ifc")
            model.write("path/to/model.ifcZIP")
            model.write("path/to/model.anyextension", format=".ifc")
        """
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        if format == None:
            format = ifcopenshell.guess_format(path)
        if format == ".ifcXML":
            raise NotImplementedError("Writing .ifcXML files is not supported")
        if format == ".ifcZIP":
            return self.write(path, ".ifc", zipped=True)
        self.wrapped_data.write(str(path))

        if zipped:
            unzipped_path = path.with_suffix(format)
            path.rename(unzipped_path)
            with zipfile.ZipFile(path, "w") as zip_file:
                zip_file.write(
                    unzipped_path,
                    unzipped_path.name,
                    compress_type=zipfile.ZIP_DEFLATED,
                )
                unzipped_path.unlink()
        return

    @staticmethod
    def from_string(s: str) -> file:
        return file(ifcopenshell_wrapper.read(s))

    @staticmethod
    def from_pointer(address: int) -> file:
        assert (f := file_dict[address][0]()) is not None
        return f

    def to_string(self) -> str:
        return self.wrapped_data.to_string()

    @property
    def header(self) -> file_header:
        # TODO: Workaround for old builds, remove after build stabilizes.
        # TODO: No need for `wrapped_data.header` to be a method - should use `@property`?
        header = self.wrapped_data.header
        if isinstance(header, types.MethodType):
            return file_header(self, self.wrapped_data.header())
        else:
            return self.wrapped_data.header

    @property
    def storage(self) -> Optional[rocksdb_file_storage]:
        """
        Returns:
            Optional[rocksdb_file_storage]: underlying key-value store interface when opened as a RocksDB-backed file
        """
        if self.wrapped_data.storage_mode() == 1:
            return rocksdb_file_storage(self)
