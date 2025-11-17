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
import functools
import importlib
import numbers
import itertools
import operator
import subprocess
import sys
import time
from typing import Union, Any, TypeVar, overload, TYPE_CHECKING, cast, NoReturn
from collections.abc import Callable, Sequence

from . import ifcopenshell_wrapper
from . import settings

if TYPE_CHECKING:
    import ifcopenshell

try:
    import logging
except ImportError:
    logging = type("logger", (object,), {"exception": staticmethod(lambda s: print(s))})

T = TypeVar("T")


def set_derived_attribute(*args):
    raise TypeError("Unable to set derived attribute")


def set_unsupported_attribute(*args):
    raise TypeError("This is an unsupported attribute type")


# For every schema and its entities populate a list
# of functions for every entity attribute (including
# inherited attributes) to set that particular
# attribute by index.
# For example. IFC2X3.IfcWall with have a list of
# 9 methods. The first will point at
# ifcopenshell.ifcopenshell_wrapper.entity_instance.setArgumentAsString
# because the first attribute GlobalId ultimately
# is of type string.
# Previously, resolving the appropriate function was
# done for each invocation of __setitem__. Now this
# mapping is built once during initialization of the
# module.
MethodList = list[Callable[[ifcopenshell_wrapper.entity_instance, int, Any], Union[None, NoReturn]]]
"""List of setter methods for class attributes."""
_method_dict: dict[str, MethodList] = {}
"""Mapping of entity classes (e.g. 'IFC4.IfcWall') to MethodLists."""


def register_schema_attributes(schema: ifcopenshell_wrapper.schema_definition) -> None:
    for decl in schema.declarations():
        if hasattr(decl, "argument_types"):
            fq_name = ".".join((schema.name(), decl.name()))

            # get type strings as reported by IfcOpenShell C++
            type_strs = decl.argument_types()
            type_strs = cast(Sequence[str], type_strs)

            # convert case for setter function
            type_strs = [x.title().replace(" ", "") for x in type_strs]

            # binary and enumeration are passed from python as string as well
            type_strs = [x.replace("Binary", "String") for x in type_strs]
            type_strs = [x.replace("Enumeration", "String") for x in type_strs]

            # prefix to get method names
            fn_names = ["setArgumentAs" + x for x in type_strs]

            # resolve to actual functions in wrapper
            functions = [
                (
                    set_derived_attribute
                    if mname == "setArgumentAsDerived"
                    else (
                        set_unsupported_attribute
                        if mname == "setArgumentAsUnknown"
                        else getattr(ifcopenshell_wrapper.entity_instance, mname)
                    )
                )
                for mname in fn_names
            ]

            _method_dict[fq_name] = functions


for nm in ifcopenshell_wrapper.schema_names():
    schema = ifcopenshell_wrapper.schema_by_name(nm)
    register_schema_attributes(schema)


class entity_instance:
    """Represents an entity (wall, slab, property, etc) of an IFC model

    An IFC model consists of entities. Examples of entities include walls,
    slabs, doors and so on. Entities can also be non-physical things, like
    properties, systems, construction tasks, colours, geometry, and more.

    Entities are defined through an **IFC Class**. There are hundreds of **IFC
    Classes** defined as part of the ISO standard by the buildingSMART
    International organisation. The **IFC Class** defines the attributes of an
    entity, as well as the data types and whether or not an attribute is
    mandatory or optional.

    IfcOpenShell's API dynamically implements the IFC schema. You will not find
    documentation about available **IFC Classes**, or what attributes they
    have.  Please consult the buildingSMART official documentation or start
    reading :doc:`/introduction/introduction_to_ifc`.

    In addition to the Python methods you see documented here, an instantiated
    entity_instance will have attributes defined by its IFC class. For example,
    an entity instance which is an IfcWall class will have a ``Name``
    attribute, and an IfcColourRgb will have a ``Red`` attribute. Please
    consult the buildingSMART official documentation.

    Example:

    .. code:: python

        model = ifcopenshell.open(file_path)
        walls = model.by_type("IfcWall")
        wall = walls[0]

        print(wall) # #38=IFCWALL('2MEinnTPbCMwLOgceaQZFu',$,$,'My Wall',$,#52,#47,$,$);
        print(wall.is_a()) # IfcWall

        # Note: the `Name` attribute is dynamic, based on the IFC class.
        print(wall.Name) # My Wall

        # Attributes are ordered and may also be accessed via index.
        print(wall[3]) # My Wall

        print(wall.__class__) # <class 'ifcopenshell.entity_instance'>
    """

    wrapped_data: ifcopenshell_wrapper.entity_instance
    method_list: Union[MethodList, None] = None

    def __init__(
        self,
        e: Union[ifcopenshell_wrapper.entity_instance, tuple[str, str]],
        file: Union[ifcopenshell.file, None] = None,
    ):
        """
        :param e: Wrapper's ``entity_instance`` or a tuple ``(schema_identifier, ifc_class)``.
        """
        # Instances of this class will be created and removed very often,
        # so it's important to keep it very optimized.

        if isinstance(e, tuple):
            e = ifcopenshell_wrapper.new_IfcBaseClass(*e)
        object.__setattr__(self, "wrapped_data", e)

        # Make sure the file is not gc'ed while we have live instances
        e.file = file

    def __del__(self):
        """
        #2471 while the precise chain of action is unclear, creating
        instance references prevents file gc, even with all instance
        refs deleted. This is a work-around for that.
        """
        # Avoid infinite recursion if entity is failed to initialize
        # and wrapped_data is unset. Hacky since we override
        # both __dict__ and __dir__.
        try:
            wrapped_data = object.__getattribute__(self, "wrapped_data")
            wrapped_data.file = None
        except AttributeError:
            return

    @property
    def file(self):
        # ugh circular imports, name collisions
        from . import file

        return file.from_pointer(self.wrapped_data.file_pointer())

    def __getattr__(self, name: str) -> Any:
        """
        Any aggregate attributes (e.g. `SET`) are returns as Python tuples.

        Inverse attributes are always returned as tuples, even it's not a set origially in IFC
        (e.g. IfcFeatureElementSubtraction.VoidsElements)
        """
        INVALID, FORWARD, INVERSE = range(3)
        attr_cat = self.wrapped_data.get_attribute_category(name)
        if attr_cat == FORWARD:
            idx = self.wrapped_data.get_argument_index(name)
            if _method_dict[self.is_a(True)][idx] != set_derived_attribute:
                # A bit ugly, but we fall through to derived attribute handling below
                return entity_instance.wrap_value(self.wrapped_data.get_argument(idx), self.wrapped_data.file)
        elif attr_cat == INVERSE:
            vs = entity_instance.wrap_value(self.wrapped_data.get_inverse(name), self.wrapped_data.file)
            if settings.unpack_non_aggregate_inverses:
                schema_name = self.wrapped_data.is_a(True).split(".")[0]
                ent: ifcopenshell_wrapper.entity
                ent = ifcopenshell_wrapper.schema_by_name(schema_name).declaration_by_name(self.is_a())
                inv = next(i for i in ent.all_inverse_attributes() if i.name() == name)
                if (inv.bound1(), inv.bound2()) == (-1, -1):
                    if vs:
                        vs = vs[0]
                    else:
                        vs = None
            return vs

        # derived attribute perhaps?
        schema_name = self.wrapped_data.is_a(True).split(".")[0]
        try:
            rules = importlib.import_module(f"ifcopenshell.express.rules.{schema_name}")
        except:
            import os

            current_dir_files = {fn.lower(): fn for fn in os.listdir(".")}
            exp_filename = schema_name.lower() + ".exp"
            schema_path = current_dir_files.get(exp_filename)
            if schema_path is None:
                raise Exception(
                    f"Couldn't find express file '{schema_name.lower()}.exp' in the current folder: '{os.getcwd()}'."
                )
            fn = schema_path[:-4] + ".py"
            if not os.path.exists(fn):
                subprocess.run(
                    [sys.executable, "-m", "ifcopenshell.express.rule_compiler", schema_path, fn], check=True
                )
                time.sleep(1.0)
            rules = importlib.import_module(schema_name)

        def yield_supertypes():
            decl = ifcopenshell_wrapper.schema_by_name(schema_name).declaration_by_name(self.is_a())
            while decl:
                yield decl.name()
                decl = decl.supertype()

        for sty in yield_supertypes():
            fn = getattr(rules, f"calc_{sty}_{name}", None)
            if fn:
                return fn(self)

        if attr_cat != FORWARD:
            raise AttributeError(
                "entity instance of type '%s' has no attribute '%s'" % (self.wrapped_data.is_a(True), name)
            )

    @staticmethod
    def walk(f: Callable[[Any], bool], g: Callable[[Any], Any], value: Any) -> Any:
        """Applies a transformation to `value` based on a given condition.

        If value is a nested structure (e.g., a list or a tuple) will apply
        transformation to it's elements.

        :param f: A callable that takes a single argument and returns a boolean
            value. It represents the condition.
        :param g: A callable that takes a single argument and returns a
            transformed value. It represents the transformation.
        :param value: Any object, the input value to be processed
        :return: Transformed value

        Example:

        .. code:: python

            # Define condition and transformation functions
            condition = lambda v: v == old
            transform = lambda v: new

            # Usage example
            attribute_value = element.RelatedElements
            print(old in attribute_value, new in attribute_value) # True, False

            result = element.walk(condition, transform, element.RelatedElements)
            print(old in attribute_value, new in attribute_value) # False, True
        """

        if isinstance(value, (tuple, list)):
            return tuple(map(functools.partial(entity_instance.walk, f, g), value))
        elif f(value):
            return g(value)
        else:
            return value

    @staticmethod
    def wrap_value(v, file: ifcopenshell.file):
        def wrap(e: ifcopenshell_wrapper.entity_instance) -> entity_instance:
            return entity_instance(e, file)

        def is_instance(e: Any) -> bool:
            return isinstance(e, ifcopenshell_wrapper.entity_instance)

        return entity_instance.walk(is_instance, wrap, v)

    @staticmethod
    def unwrap_value(v):
        def unwrap(e):
            return e.wrapped_data

        def is_instance(e):
            return isinstance(e, entity_instance)

        return entity_instance.walk(is_instance, unwrap, v)

    def attribute_type(self, attr: Union[int, str]) -> str:
        """Return the data type of a positional attribute of the element

        :param attr: The index or name of the attribute
        """
        attr_idx = attr if isinstance(attr, numbers.Integral) else self.wrapped_data.get_argument_index(attr)
        return self.wrapped_data.get_argument_type(attr_idx)

    def attribute_name(self, attr_idx: int) -> str:
        """Return the name of a positional attribute of the element

        :param attr_idx: The index of the attribute
        """
        return self.wrapped_data.get_argument_name(attr_idx)

    def __setattr__(self, key: str, value: Any) -> None:
        index = self.wrapped_data.get_argument_index(key)
        try:
            self[index] = value
        except IndexError as e:
            # get_argument_index returns 0xFFFFFFFF if attribute is not found
            if index == 0xFFFFFFFF:
                raise AttributeError(
                    "entity instance of type '%s' has no attribute '%s'" % (self.wrapped_data.is_a(True), key)
                )
            raise e

    def __getitem__(self, key: int) -> Any:
        if key < 0 or key >= len(self):
            raise IndexError("Attribute index {} out of range for instance of type {}".format(key, self.is_a()))
        return entity_instance.wrap_value(self.wrapped_data.get_argument(key), self.wrapped_data.file)

    def __setitem__(self, idx: int, value: T) -> T:
        if self.wrapped_data.file and self.wrapped_data.file.transaction:
            self.wrapped_data.file.transaction.store_edit(self, idx, value)

        if self.method_list is None:
            super().__setattr__("method_list", _method_dict[self.is_a(True)])

        method = self.method_list[idx]

        if value is None:
            if method is not set_derived_attribute:
                try:
                    self.wrapped_data.setArgumentAsNull(idx)
                except RuntimeError as e:
                    if e.args == ("Attribute not set",):
                        raise TypeError(
                            "attribute '%s' is not optional for entity instance of type '%s'"
                            % (self.wrapped_data.get_argument_name(idx), self.wrapped_data.is_a(True))
                        )
                    raise e
        else:
            try:
                self.method_list[idx](self.wrapped_data, idx, entity_instance.unwrap_value(value))
            except TypeError:
                raise TypeError(
                    "attribute '%s' for entity '%s' is expecting value of type '%s', got '%s'."
                    % (
                        self.wrapped_data.get_argument_name(idx),
                        self.wrapped_data.is_a(True),
                        self.wrapped_data.get_argument_type(idx),
                        type(value).__name__,
                    )
                )

        return value

    def __len__(self):
        return len(self.wrapped_data)

    def __repr__(self):
        return repr(self.wrapped_data)

    def to_string(self, valid_spf=True) -> str:
        """Returns a string representation of the current entity instance.
        Equal to str(self) when valid_spf=False. When valid_spf is True
        returns a representation of the string that conforms to valid Step
        Physical File notation. The difference being entity names in upper
        case and string attribute values with unicode values encoded per
        the specific control directives.
        """

        return self.wrapped_data.to_string(valid_spf)

    @overload
    def is_a(self) -> str: ...
    @overload
    def is_a(self, ifc_class: str) -> bool: ...
    @overload
    def is_a(self, with_schema: bool) -> str: ...
    def is_a(self, *args: Union[str, bool]) -> Union[str, bool]:
        """Return the IFC class name of an instance, or checks if an instance belongs to a class.

        The check will also return true if a parent class name is provided.

        :param args: If specified, is a case insensitive IFC class name to check
            or if specified as a boolean then will define whether
            returned IFC class name should include schema name
            (e.g. "IFC4.IfcWall" if `True` and "IfcWall" if `False`).
            If omitted will act as `False`.
        :returns: Either the name of the class, or a boolean if it passes the check

        Example:

        .. code:: python

            f = ifcopenshell.file()
            f.create_entity('IfcPerson')
            f.is_a()
            >>> 'IfcPerson'
            f.is_a('IfcPerson')
            >>> True
        """
        return self.wrapped_data.is_a(*args)

    def id(self) -> int:
        """Return the STEP numerical identifier"""
        return self.wrapped_data.id()

    def __eq__(self, other: entity_instance) -> bool:
        if not isinstance(self, type(other)):
            return False
        elif None in (self.wrapped_data.file, other.wrapped_data.file):
            # when not added to a file, we can only compare attribute values
            # and we need this for where rule evaluation
            return self.get_info_2(recursive=True, include_identifier=False) == other.get_info_2(
                recursive=True, include_identifier=False
            )
        else:
            # Proper entity instances have a stable identity by means of the numeric
            # step id. Selected type instances (such as IfcPropertySingleValue.NominalValue
            # always have id=0, so we compare <type, value, file pointer>
            if self.id():
                return self.wrapped_data == other.wrapped_data
            else:
                return (self.is_a(), self[0], self.wrapped_data.file_pointer()) == (
                    other.is_a(),
                    other[0],
                    other.wrapped_data.file_pointer(),
                )

    def is_entity(self) -> bool:
        """Tests whether the instance is an entity type as opposed to a simple data type.

        :return: True if the instance is an entity
        """
        schema_name = self.wrapped_data.is_a(True).split(".")[0]
        decl = ifcopenshell_wrapper.schema_by_name(schema_name).declaration_by_name(self.is_a())
        return isinstance(decl, ifcopenshell_wrapper.entity)

    def compare(self, other, op, reverse=False):
        """Compares with another instance.

        For simple types the declaration name is not taken into account:

        >>> f = ifcopenshell.file()
        >>> f.createIfcInteger(0) < f.createIfcPositiveInteger(1)
        True

        For entity types the declaration name is taken into account:

        >>> f.createIfcWall('a') < f.createIfcWall('b')
        True

        >>> f.createIfcWallStandardCase('a') < f.createIfcWall('b')
        False

        Comparing simple types with different underlying types throws an exception:

        >>> f.createIfcInteger(0) < f.createIfcLabel('x')
        Traceback (most recent call last):
        File "<stdin>", line 1, in <module>
        File "entity_instance.py", line 371, in compare
            return op(a, b)
        TypeError: '<' not supported between instances of 'int' and 'str'

        :param other: Right hand side (or lhs when reverse = True)
        :param op: The comparison operator (likely from the operator module)
        :param reverse: When true swaps lhs and rhs. Defaults to False.

        :return: bool: The comparison predicate applied to self and other
        """

        if isinstance(other, entity_instance):
            a, b = map(tuple, (self, other))
            if any(map(entity_instance.is_entity, (self, other))):
                a = (self.is_a(),) + a
                b = (other.is_a(),) + b
        elif self.is_entity():
            a = tuple(self)
            b = other
            if isinstance(b, list):
                b = tuple(b)
            if not isinstance(b, tuple):
                b = (b,)
        else:
            a = self[0]
            b = other

        if reverse:
            a, b = b, a

        return op(a, b)

    __le__ = functools.partialmethod(compare, op=operator.le)
    __lt__ = functools.partialmethod(compare, op=operator.lt)
    __ge__ = functools.partialmethod(compare, op=operator.ge)
    __gt__ = functools.partialmethod(compare, op=operator.gt)
    __rle__ = functools.partialmethod(compare, op=operator.le, reverse=True)
    __rlt__ = functools.partialmethod(compare, op=operator.lt, reverse=True)
    __rge__ = functools.partialmethod(compare, op=operator.ge, reverse=True)
    __rgt__ = functools.partialmethod(compare, op=operator.gt, reverse=True)

    def __hash__(self):
        # Proper entity instances have a stable identity by means of the numeric
        # step id. Selected type instances (such as IfcPropertySingleValue.NominalValue
        # always have id=0, so we hash <type, value, file pointer>
        if id_ := self.id():
            return hash((id_, self.wrapped_data.file_pointer()))
        else:
            return hash((self.is_a(), self[0], self.wrapped_data.file_pointer()))

    def __dir__(self):
        return sorted(
            set(
                itertools.chain(
                    dir(type(self)),
                    map(str, self.wrapped_data.get_attribute_names()),
                    map(str, self.wrapped_data.get_inverse_attribute_names()),
                )
            )
        )

    def get_info(
        self,
        include_identifier: bool = True,
        recursive: bool = False,
        return_type: Union[type[dict], type] = dict,
        ignore: Sequence[str] = (),
        scalar_only: bool = False,
    ) -> dict[str, Any]:
        """Return a dictionary of the entity_instance's properties (Python and IFC) and their values.

        Resulting dictionary keys: 'id', 'type', all entity attribute names.

        :param include_identifier: Whether or not to include the STEP numerical identifier
        :param recursive: Whether or not to convert referenced IFC elements into dictionaries too. All attributes also apply recursively
        :param return_type: The return data type to be casted into
        :param ignore: A list of attribute names to ignore
        :param scalar_only: Filters out all values that are IFC instances
        :returns: A dictionary of properties and their corresponding values

        Example:

        .. code:: python

            ifc_file = ifcopenshell.open(file_path)
            products = ifc_file.by_type("IfcProduct")
            obj_info = products[0].get_info()
            print(obj_info.keys())
            >>> dict_keys(['Description', 'Name', 'BuildingAddress', 'LongName', 'GlobalId', 'ObjectPlacement', 'OwnerHistory', 'ObjectType',
            >>> ...'ElevationOfTerrain', 'CompositionType', 'id', 'Representation', 'type', 'ElevationOfRefHeight'])
        """

        def _():
            try:
                if include_identifier:
                    yield "id", self.id()
                yield "type", self.is_a()
            except BaseException:
                logging.exception("unhandled exception while getting id / type info on {}".format(self))
            for i in range(len(self)):
                try:
                    if self.wrapped_data.get_attribute_names()[i] in ignore:
                        continue
                    attr_value = self[i]

                    to_include = {"v": True}

                    if recursive or scalar_only:

                        def is_instance(e):
                            return isinstance(e, entity_instance)

                        def get_info_(inst):
                            return entity_instance.get_info(
                                inst,
                                include_identifier=include_identifier,
                                recursive=recursive,
                                return_type=return_type,
                                ignore=ignore,
                            )

                        def do_ignore(inst):
                            to_include["v"] = False
                            return None

                        attr_value = entity_instance.walk(
                            is_instance, get_info_ if recursive else do_ignore, attr_value
                        )

                    if to_include["v"]:
                        yield self.attribute_name(i), attr_value
                except BaseException:
                    logging.exception("unhandled exception occurred setting attribute name for {}".format(self))

        return return_type(_())

    __dict__ = property(get_info)

    def get_info_2(
        self,
        include_identifier: bool = True,
        recursive: bool = False,
        return_type: type[dict] = dict,
        ignore: Sequence[str] = (),
    ) -> dict[str, Any]:
        """More perfomant version of `.get_info()` but with limited arguments values.\n
        Method has exactly the same signature as `.get_info()` but it doesn't support getting information non-recursively.

        Currently supported arguments values:
            * recursive: `True` (will fail with default `False` value from `.get_info()`)
            * return_type: `dict`
            * ignore: `()` (empty tuple)
        """

        assert recursive
        assert return_type is dict
        assert len(ignore) == 0
        return ifcopenshell_wrapper.get_info_cpp(self.wrapped_data, include_identifier)
