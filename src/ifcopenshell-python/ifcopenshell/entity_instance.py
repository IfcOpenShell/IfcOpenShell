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


class entity_instance_mixin:
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

    @property
    def file(self):
        raise NotImplementedError

    def __getattr__(self, name: str) -> Any:
        if name in ("this", "thisown") or name.startswith("_swig_"):
            return object.__getattr__(self, name)
        """
        Any aggregate attributes (e.g. `SET`) are returns as Python tuples.

        Inverse attributes are returned as tuples, even it's not a set origially in IFC
        (e.g. IfcFeatureElementSubtraction.VoidsElements)
        (unless settings.unpack_non_aggregate_inverses is used, which is necessary for express rule execution)
        """
        INVALID, FORWARD, INVERSE, DERIVED = range(4)
        attr_cat = self.get_attribute_category(name)
        if attr_cat == INVALID:
            raise AttributeError(
                "entity instance of type '%s' has no attribute '%s'" % (self.is_a(True), name)
            )
        elif attr_cat == FORWARD:
            idx = self.get_argument_index(name)
            return self.get_argument(idx)
        elif attr_cat == INVERSE:
            vs = self.get_inverse(name)
            if settings.unpack_non_aggregate_inverses:
                schema_name = self.is_a(True).split(".")[0]
                ent: ifcopenshell_wrapper.entity
                ent = ifcopenshell_wrapper.schema_by_name(schema_name).declaration_by_name(self.is_a())
                inv = next(i for i in ent.all_inverse_attributes() if i.name() == name)
                if (inv.bound1(), inv.bound2()) == (-1, -1):
                    if vs:
                        vs = vs[0]
                    else:
                        vs = None
            return vs
        elif attr_cat == DERIVED:
            schema_name = self.is_a(True).split(".")[0]
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
            return tuple(map(functools.partial(entity_instance_mixin.walk, f, g), value))
        elif f(value):
            return g(value)
        else:
            return value

    def __setattr__(self, key: str, value: Any) -> None:
        if key in ("this", "thisown") or key.startswith("_swig_"):
            return object.__setattr__(self, key, value)

        index = self.get_argument_index(key)
        try:
            self[index] = value
        except IndexError as e:
            # get_argument_index returns 0xFFFFFFFF if attribute is not found
            if index == 0xFFFFFFFF:
                raise AttributeError(
                    "entity instance of type '%s' has no attribute '%s'" % (self.is_a(True), key)
                )
            raise e

    def __getitem__(self, key: int) -> Any:
        if key < 0 or key >= len(self):
            raise IndexError("Attribute index {} out of range for instance of type {}".format(key, self.is_a()))
        return self.get_argument(key)

    def __setitem__(self, idx: int, value: T) -> T:
        if self.file and self.file.transaction:
            self.file.transaction.store_edit(self, idx, value)
        
        self.set_attribute_value_py(idx, value)

        return value


    def __eq__(self, other: entity_instance_mixin) -> bool:
        if not isinstance(self, type(other)):
            return False
        else:
            raise NotImplementedError
        
    def is_entity(self) -> bool:
        """Tests whether the instance is an entity type as opposed to a simple data type.

        :return: True if the instance is an entity
        """
        schema_name = self.is_a(True).split(".")[0]
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

        if isinstance(other, entity_instance_mixin):
            a, b = map(tuple, (self, other))
            if any(map(entity_instance_mixin.is_entity, (self, other))):
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
            return hash((id_, self.file_pointer()))
        else:
            return hash((self.is_a(), self[0], self.file_pointer()))

    def __dir__(self):
        return sorted(
            set(
                itertools.chain(
                    dir(type(self)),
                    map(str, self.get_attribute_names()),
                    map(str, self.get_inverse_attribute_names()),
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
                    if self.get_attribute_names()[i] in ignore:
                        continue
                    attr_value = self[i]

                    to_include = {"v": True}

                    if recursive or scalar_only:

                        def is_instance(e):
                            return isinstance(e, entity_instance_mixin)

                        def get_info_(inst):
                            return entity_instance_mixin.get_info(
                                inst,
                                include_identifier=include_identifier,
                                recursive=recursive,
                                return_type=return_type,
                                ignore=ignore,
                            )

                        def do_ignore(inst):
                            to_include["v"] = False
                            return None

                        attr_value = entity_instance_mixin.walk(
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
        return ifcopenshell_wrapper.get_info_cpp(self, include_identifier)
