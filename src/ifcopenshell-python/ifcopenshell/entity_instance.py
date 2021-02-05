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

import functools
import numbers
import itertools

from . import ifcopenshell_wrapper

try:
    import logging
except ImportError as e:
    logging = type("logger", (object,), {"exception": staticmethod(lambda s: print(s))})


class entity_instance(object):
    """This is the base Python class for all IFC objects.

    An instantiated entity_instance will have methods of Python and the IFC class itself.

    Example::

        ifc_file = ifcopenshell.open(file_path)
        products = ifc_file.by_type("IfcProduct")
        print(products[0].__class__)
        >>> <class 'ifcopenshell.entity_instance.entity_instance'>
        print(products[0].Representation)
        >>> #423=IfcProductDefinitionShape($,$,(#409,#421))
    """

    def __init__(self, e):
        if isinstance(e, tuple):
            e = ifcopenshell_wrapper.new_IfcBaseClass(*e)
        super(entity_instance, self).__setattr__("wrapped_data", e)

    def __getattr__(self, name):
        INVALID, FORWARD, INVERSE = range(3)
        attr_cat = self.wrapped_data.get_attribute_category(name)
        if attr_cat == FORWARD:
            return entity_instance.wrap_value(
                self.wrapped_data.get_argument(self.wrapped_data.get_argument_index(name))
            )
        elif attr_cat == INVERSE:
            return entity_instance.wrap_value(self.wrapped_data.get_inverse(name))
        else:
            raise AttributeError(
                "entity instance of type '%s' has no attribute '%s'" % (self.wrapped_data.is_a(), name)
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
    def wrap_value(v):
        def wrap(e):
            return entity_instance(e)

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
        attr_idx = attr if isinstance(attr, numbers.Integral) else self.wrapped_data.get_argument_index(attr)
        return self.wrapped_data.get_argument_type(attr_idx)

    def attribute_name(self, attr_idx):
        """Return the name of a positional attribute of the element

        :param attr_idx: The index of the attribute
        :type attr_idx: int
        :rtype: string
        """
        return self.wrapped_data.get_argument_name(attr_idx)

    def __setattr__(self, key, value):
        self[self.wrapped_data.get_argument_index(key)] = value

    def __getitem__(self, key):
        if key < 0 or key >= len(self):
            raise IndexError("Attribute index {} out of range for instance of type {}".format(key, self.is_a()))
        return entity_instance.wrap_value(self.wrapped_data.get_argument(key))

    def __setitem__(self, idx, value):
        attr_type = real_attr_type = self.attribute_type(idx).title().replace(" ", "")
        real_attr_type = real_attr_type.replace("Derived", "None")
        attr_type = attr_type.replace("Binary", "String")
        attr_type = attr_type.replace("Enumeration", "String")

        if value is None:
            if attr_type != "Derived":
                self.wrapped_data.setArgumentAsNull(idx)
        else:
            valid = attr_type != "Derived"
            if valid:
                try:
                    if isinstance(value, unicode):
                        value = value.encode("utf-8")
                except BaseException:
                    pass

                try:
                    if attr_type != "Derived":
                        getattr(self.wrapped_data, "setArgumentAs%s" % attr_type)(
                            idx, entity_instance.unwrap_value(value)
                        )
                except BaseException as e:
                    valid = False

            if not valid:
                raise ValueError(
                    "Expected %s for attribute %s.%s, got %r"
                    % (real_attr_type, self.is_a(), self.attribute_name(idx), value)
                )

        return value

    def __len__(self):
        return len(self.wrapped_data)

    def __repr__(self):
        return repr(self.wrapped_data)

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
        return self.wrapped_data == other.wrapped_data

    def __hash__(self):
        return hash((self.id(), self.wrapped_data.file_pointer()))

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

    def get_info(self, include_identifier=True, recursive=False, return_type=dict, ignore=()):
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
                logging.exception("unhandled exception while getting id / type info on {}".format(self))
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

                        attr_value = entity_instance.walk(is_instance, get_info_, attr_value)
                    yield self.attribute_name(i), attr_value
                except BaseException:
                    logging.exception("unhandled exception occurred setting attribute name for {}".format(self))

        return return_type(_())

    __dict__ = property(get_info)
    
    def get_info_2(self, include_identifier=True, recursive=False, return_type=dict, ignore=()):
        assert include_identifier
        assert recursive
        assert return_type is dict
        assert len(ignore) == 0
        return ifcopenshell_wrapper.get_info_cpp(self.wrapped_data)
