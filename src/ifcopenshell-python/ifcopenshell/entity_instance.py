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


from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import functools
import importlib
import numbers
import itertools
import operator
import functools
import subprocess
import sys
import time
from typing import Union, Any, Callable, TypeVar, overload

from . import ifcopenshell_wrapper
from . import settings

try:
    import logging
except ImportError as e:
    logging = type("logger", (object,), {"exception": staticmethod(lambda s: print(s))})

T = TypeVar("T")

# poor man's enum
ATTR_INVALID, ATTR_FORWARD, ATTR_INVERSE, ATTR_FORWARD_DERIVED = range(4)

class entity_instance(object):
    """Base class for all IFC objects.

    An instantiated entity_instance will have methods of Python and the IFC class itself.

    Example:

    .. code:: python

        ifc_file = ifcopenshell.open(file_path)
        products = ifc_file.by_type("IfcProduct")
        print(products[0].__class__)
        >>> <class 'ifcopenshell.entity_instance.entity_instance'>
        print(products[0].Representation)
        >>> #423=IfcProductDefinitionShape($,$,(#409,#421))
    """

    @property
    def file(self):
        # ugh circular imports, name collisions
        from . import file

        return file.from_pointer(self.file_pointer())

    def __getattr__(self, name):
        attr_cat = self.get_attribute_category(name)
        if attr_cat == ATTR_FORWARD:
            idx = self.get_argument_index(name)
            return self.get_argument(idx)
        elif attr_cat == ATTR_INVERSE:
            vs = self.get_inverse(name)
            if settings.unpack_non_aggregate_inverses:
                schema_name = self.is_a(True).split(".")[0]
                ent = ifcopenshell_wrapper.schema_by_name(schema_name).declaration_by_name(self.is_a())
                inv = [i for i in ent.all_inverse_attributes() if i.name() == name][0]
                if (inv.bound1(), inv.bound2()) == (-1, -1):
                    if vs:
                        vs = vs[0]
                    else:
                        vs = None
            return vs
    
        # derived attribute perhaps?
        schema_name = self.is_a(True).split(".")[0]
        try:
            rules = importlib.import_module(f"ifcopenshell.express.rules.{schema_name}")
        except:
            import os
            current_dir_files = {fn.lower(): fn for fn in os.listdir('.')}
            schema_path = current_dir_files.get(schema_name.lower() + '.exp')
            fn = schema_path[:-4] + '.py'
            if not os.path.exists(fn):
                subprocess.run([sys.executable, "-m", "ifcopenshell.express.rule_compiler", schema_path, fn], check=True)
                time.sleep(1.)
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
                "entity instance of type '%s' has no attribute '%s'" % (self.is_a(True), name)
            )

    @staticmethod
    def walk(f: Callable[[Any], bool], g: Callable[[Any], Any], value: Any) -> Any:
        """
         Applies transformation to `value` based on a given condition.
         If value is a nested structure (e.g., a list or a tuple) will apply transformation to it's elements.
        .

         :param f: A callable that takes a single argument and returns a boolean value. It represents the condition
         :type f: Callable
         :param g: A callable that takes a single argument and returns a transformed value. It represents the transformation
         :type g: Callable
         :param value: Any object, the input value to be processed
         :type value: Any
         :return: Transformed value
         :rtype: Any

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

    def attribute_type(self, attr: int) -> str:
        """Return the data type of a positional attribute of the element

        :param attr: The index of the attribute
        :type attr: int
        :rtype: string
        """
        attr_idx = attr if isinstance(attr, numbers.Integral) else self.get_argument_index(attr)
        return self.get_argument_type(attr_idx)

    def attribute_name(self, attr_idx: int) -> str:
        """Return the name of a positional attribute of the element

        :param attr_idx: The index of the attribute
        :type attr_idx: int
        :rtype: string
        """
        return self.get_argument_name(attr_idx)

    def __setattr__(self, key: str, value: Any) -> None:
        index = self.get_argument_index(key)
        self[index] = value

    def __getitem__(self, key: int) -> Any:
        if key < 0 or key >= len(self):
            raise IndexError("Attribute index {} out of range for instance of type {}".format(key, self.is_a()))
        return self.get_argument(key)

    def __setitem__(self, idx: int, value: T) -> T:
        if self.file and self.file.transaction:
            self.file.transaction.store_edit(self, idx, value)
    
        self.setAttribute(idx, value)
    
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

        return self.to_string(valid_spf)

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
        :type args: Union[str, bool]
        :returns: Either the name of the class, or a boolean if it passes the check
        :rtype: Union[str, bool]

        Example:

        .. code:: python

            f = ifcopenshell.file()
            f.create_entity('IfcPerson')
            f.is_a()
            >>> 'IfcPerson'
            f.is_a('IfcPerson')
            >>> True
        """
        return self.is_a(*args)

    def id(self) -> int:
        """Return the STEP numerical identifier

        :rtype: int
        """
        return self.id()

    def __eq__(self, other):
        if not isinstance(self, type(other)):
            return False
        elif None in (self.file, other.file):
            # when not added to a file, we can only compare attribute values
            # and we need this for where rule evaluation
            return self.get_info(recursive=True, include_identifier=False) == other.get_info(
                recursive=True, include_identifier=False
            )
        else:
            # Proper entity instances have a stable identity by means of the numeric
            # step id. Selected type instances (such as IfcPropertySingleValue.NominalValue
            # always have id=0, so we compare <type, value, file pointer>
            if self.id():
                return self.wrapped_data == other.wrapped_data
            else:
                return (self.is_a(), self[0], self.file_pointer()) == (
                    other.is_a(),
                    other[0],
                    other.file_pointer(),
                )

    def is_entity(self) -> bool:
        """Tests whether the instance is an entity type as opposed to a simple data type.

        Returns:
            bool: True if the instance is an entity
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

        Args:
            other (_type_): Right hand side (or lhs when reverse = True)
            op (_type_): The comparison operator (likely from the operator module)
            reverse (bool, optional): When true swaps lhs and rhs. Defaults to False.

        Returns:
            bool: The comparison predicate applied to self and other
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
        if self.id():
            return hash((self.id(), self.file_pointer()))
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
        self, include_identifier=True, recursive=False, return_type=dict, ignore=(), scalar_only=False
    ) -> dict:
        """Return a dictionary of the entity_instance's properties (Python and IFC) and their values.

        :param include_identifier: Whether or not to include the STEP numerical identifier
        :type include_identifier: bool
        :param recursive: Whether or not to convert referenced IFC elements into dictionaries too. All attributes also apply recursively
        :type recursive: bool
        :param return_type: The return data type to be casted into
        :type return_type: dict|list|other
        :param ignore: A list of attribute names to ignore
        :type ignore: set|list
        :param scalar_only: Filters out all values that are IFC instances
        :type scalar_only: bool
        :returns: A dictionary of properties and their corresponding values
        :rtype: dict

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

    # @todo this is no longer possible with the direct integration into the swig type
    # __dict__ = property(get_info)

    def get_info_2(self, include_identifier=True, recursive=False, return_type=dict, ignore=()):
        """More perfomant version of `.get_info()` but with limited arguments values.\n
        Method has exactly the same signature as `.get_info()` but it doesn't support getting information non-recursively.

        Currently supported arguments values:
            * include_identifier: `True`
            * recursive: `True` (will fail with default `False` value from `.get_info()`)
            * return_type: `dict`
            * ignore: `()` (empty tuple)
        """

        assert include_identifier
        assert recursive
        assert return_type is dict
        assert len(ignore) == 0
        return ifcopenshell_wrapper.get_info_cpp(self.wrapped_data)
