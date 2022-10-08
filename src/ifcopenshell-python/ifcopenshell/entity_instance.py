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
import numbers
import itertools

from . import ifcopenshell_wrapper

try:
    import logging
except ImportError as e:
    logging = type("logger", (object,), {"exception": staticmethod(lambda s: print(s))})


def set_derived_atribute(*args):
    raise TypeError("Unable to set derived attribute")


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
_method_dict = {}


def register_schema_attributes(schema):
    for decl in schema.declarations():
        if hasattr(decl, "argument_types"):
            fq_name = ".".join((schema.name(), decl.name()))

            # get type strings as reported by IfcOpenShell C++
            type_strs = decl.argument_types()

            # convert case for setter function
            type_strs = [x.title().replace(" ", "") for x in type_strs]

            # binary and enumeration are passed from python as string as well
            type_strs = [x.replace("Binary", "String") for x in type_strs]
            type_strs = [x.replace("Enumeration", "String") for x in type_strs]

            # prefix to get method names
            fn_names = ["setArgumentAs" + x for x in type_strs]

            # resolve to actual functions in wrapper
            functions = [
                set_derived_atribute
                if mname == "setArgumentAsDerived"
                else getattr(ifcopenshell_wrapper.entity_instance, mname)
                for mname in fn_names
            ]

            _method_dict[fq_name] = functions


for nm in ifcopenshell_wrapper.schema_names():
    schema = ifcopenshell_wrapper.schema_by_name(nm)
    register_schema_attributes(schema)


class entity_instance(object):
    """Base class for all IFC objects.

    An instantiated entity_instance will have methods of Python and the IFC class itself.

    Example::

        ifc_file = ifcopenshell.open(file_path)
        products = ifc_file.by_type("IfcProduct")
        print(products[0].__class__)
        >>> <class 'ifcopenshell.entity_instance.entity_instance'>
        print(products[0].Representation)
        >>> #423=IfcProductDefinitionShape($,$,(#409,#421))
    """

    def __init__(self, e, file=None):
        if isinstance(e, tuple):
            e = ifcopenshell_wrapper.new_IfcBaseClass(*e)
        super(entity_instance, self).__setattr__("wrapped_data", e)
        super(entity_instance, self).__setattr__("method_list", None)

        # Make sure the file is not gc'ed while we have live instances
        self.wrapped_data.file = file

    def __del__(self):
        """
        #2471 while the precise chain of action is unclear, creating
        instance references prevents file gc, even with all instance
        refs deleted. This is a work-around for that.
        """
        self.wrapped_data.file = None

    def __getattr__(self, name):
        INVALID, FORWARD, INVERSE = range(3)
        attr_cat = self.wrapped_data.get_attribute_category(name)
        if attr_cat == FORWARD:
            return entity_instance.wrap_value(
                self.wrapped_data.get_argument(
                    self.wrapped_data.get_argument_index(name)
                ),
                self.wrapped_data.file,
            )
        elif attr_cat == INVERSE:
            return entity_instance.wrap_value(
                self.wrapped_data.get_inverse(name), self.wrapped_data.file
            )
        else:
            raise AttributeError(
                "entity instance of type '%s' has no attribute '%s'"
                % (self.wrapped_data.is_a(True), name)
            )

    @staticmethod
    def walk(f, g, value):
        if isinstance(value, (tuple, list)):
            return tuple(map(functools.partial(entity_instance.walk, f, g), value))
        elif f(value):
            return g(value)
        else:
            return value

    @staticmethod
    def wrap_value(v, file):
        def wrap(e):
            return entity_instance(e, file)

        def is_instance(e):
            return isinstance(e, ifcopenshell_wrapper.entity_instance)

        return entity_instance.walk(is_instance, wrap, v)

    @staticmethod
    def unwrap_value(v):
        def unwrap(e):
            return e.wrapped_data

        def is_instance(e):
            return isinstance(e, entity_instance)

        return entity_instance.walk(is_instance, unwrap, v)

    def attribute_type(self, attr):
        """Return the data type of a positional attribute of the element

        :param attr: The index of the attribute
        :type attr: int
        :rtype: string
        """
        attr_idx = (
            attr
            if isinstance(attr, numbers.Integral)
            else self.wrapped_data.get_argument_index(attr)
        )
        return self.wrapped_data.get_argument_type(attr_idx)

    def attribute_name(self, attr_idx):
        """Return the name of a positional attribute of the element

        :param attr_idx: The index of the attribute
        :type attr_idx: int
        :rtype: string
        """
        return self.wrapped_data.get_argument_name(attr_idx)

    def __setattr__(self, key, value):
        index = self.wrapped_data.get_argument_index(key)
        self[index] = value

    def __getitem__(self, key):
        if key < 0 or key >= len(self):
            raise IndexError(
                "Attribute index {} out of range for instance of type {}".format(
                    key, self.is_a()
                )
            )
        return entity_instance.wrap_value(
            self.wrapped_data.get_argument(key), self.wrapped_data.file
        )

    def __setitem__(self, idx, value):
        if self.wrapped_data.file and self.wrapped_data.file.transaction:
            self.wrapped_data.file.transaction.store_edit(self, idx, value)

        if self.method_list is None:
            super(entity_instance, self).__setattr__(
                "method_list", _method_dict[self.is_a(True)]
            )

        method = self.method_list[idx]

        if value is None:
            if method is not set_derived_atribute:
                self.wrapped_data.setArgumentAsNull(idx)
        else:
            self.method_list[idx](
                self.wrapped_data, idx, entity_instance.unwrap_value(value)
            )

        return value

    def __len__(self):
        return len(self.wrapped_data)

    def __repr__(self):
        return repr(self.wrapped_data)
        
    def to_string(self, valid_spf=True):
        """Returns a string representation of the current entity instance.
        Equal to str(self) when valid_spf=False. When valid_spf is True
        returns a representation of the string that conforms to valid Step
        Physical File notation. The difference being entity names in upper
        case and string attribute values with unicode values encoded per
        the specific control directives.
        """
        
        return self.wrapped_data.to_string(valid_spf)

    def is_a(self, *args):
        """Return the IFC class name of an instance, or checks if an instance belongs to a class.

        The check will also return true if a parent class name is provided.

        :param args: If specified, is a case insensitive IFC class name to check
        :type args: string
        :returns: Either the name of the class, or a boolean if it passes the check
        :rtype: string|bool

        Example::

            f = ifcopenshell.file()
            f.create_entity('IfcPerson')
            f.is_a()
            >>> 'IfcPerson'
            f.is_a('IfcPerson')
            >>> True
        """
        return self.wrapped_data.is_a(*args)

    def id(self):
        """Return the STEP numerical identifier

        :rtype: int
        """
        return self.wrapped_data.id()

    def __eq__(self, other):
        if not isinstance(self, type(other)):
            return False
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

    def __hash__(self):
        # Proper entity instances have a stable identity by means of the numeric
        # step id. Selected type instances (such as IfcPropertySingleValue.NominalValue
        # always have id=0, so we hash <type, value, file pointer>
        if self.id():
            return hash((self.id(), self.wrapped_data.file_pointer()))
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
        self, include_identifier=True, recursive=False, return_type=dict, ignore=()
    ):
        """Return a dictionary of the entity_instance's properties (Python and IFC) and their values.

        :param include_identifier: Whether or not to include the STEP numerical identifier
        :type include_identifier: bool
        :param recursive: Whether or not to convert referenced IFC elements into dictionaries too. All attributes also apply recursively
        :type recursive: bool
        :param return_type: The return data type to be casted into
        :type return_type: dict|list|other
        :param ignore: A list of attribute names to ignore
        :type ignore: set|list
        :returns: A dictionary of properties and their corresponding values
        :rtype: dict

        Example::

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
                logging.exception(
                    "unhandled exception while getting id / type info on {}".format(
                        self
                    )
                )
            for i in range(len(self)):
                try:
                    if self.wrapped_data.get_attribute_names()[i] in ignore:
                        continue
                    attr_value = self[i]
                    if recursive:

                        def is_instance(e):
                            return isinstance(e, entity_instance)

                        def get_info_(inst):
                            # for ty in ignore:
                            #     if inst.is_a(ty):
                            #         return None
                            return entity_instance.get_info(
                                inst,
                                include_identifier=include_identifier,
                                recursive=recursive,
                                return_type=return_type,
                                ignore=ignore,
                            )

                        attr_value = entity_instance.walk(
                            is_instance, get_info_, attr_value
                        )
                    yield self.attribute_name(i), attr_value
                except BaseException:
                    logging.exception(
                        "unhandled exception occurred setting attribute name for {}".format(
                            self
                        )
                    )

        return return_type(_())

    __dict__ = property(get_info)

    def get_info_2(
        self, include_identifier=True, recursive=False, return_type=dict, ignore=()
    ):
        assert include_identifier
        assert recursive
        assert return_type is dict
        assert len(ignore) == 0
        return ifcopenshell_wrapper.get_info_cpp(self.wrapped_data)
