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
from __future__ import print_function

import functools
import numbers
import itertools

from . import ifcopenshell_wrapper

try:
    import logging
except ImportError as e:
    logging = type('logger', (object,), {'exception': staticmethod(lambda s: print(s))})


class entity_instance(object):
    def __init__(self, e):
        if isinstance(e, str):
            e = ifcopenshell_wrapper.new_IfcBaseClass(e)
        super(entity_instance, self).__setattr__('wrapped_data', e)

    def __getattr__(self, name):
        INVALID, FORWARD, INVERSE = range(3)
        attr_cat = self.wrapped_data.get_attribute_category(name)
        if attr_cat == FORWARD:
            return entity_instance.wrap_value(
                self.wrapped_data.get_argument(self.wrapped_data.get_argument_index(name)))
        elif attr_cat == INVERSE:
            return entity_instance.wrap_value(self.wrapped_data.get_inverse(name))
        else:
            raise AttributeError(
                "entity instance of type '%s' has no attribute '%s'" % (self.wrapped_data.is_a(), name))

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
        wrap = lambda e: entity_instance(e)
        is_instance = lambda e: isinstance(e, ifcopenshell_wrapper.entity_instance)
        return entity_instance.walk(is_instance, wrap, v)

    @staticmethod
    def unwrap_value(v):
        unwrap = lambda e: e.wrapped_data
        is_instance = lambda e: isinstance(e, entity_instance)
        return entity_instance.walk(is_instance, unwrap, v)

    def attribute_type(self, attr):
        attr_idx = attr if isinstance(attr, numbers.Integral) else self.wrapped_data.get_argument_index(attr)
        return self.wrapped_data.get_argument_type(attr_idx)

    def attribute_name(self, attr_idx):
        return self.wrapped_data.get_argument_name(attr_idx)

    def __setattr__(self, key, value):
        self[self.wrapped_data.get_argument_index(key)] = value

    def __getitem__(self, key):
        if key < 0 or key >= len(self):
            raise IndexError("Attribute index {} out of range for instance of type {}".format(key, self.is_a()))
        return entity_instance.wrap_value(self.wrapped_data.get_argument(key))

    def __setitem__(self, idx, value):
        if value is None:
            self.wrapped_data.setArgumentAsNull(idx)
        else:
            attr_type = self.attribute_type(idx).title().replace(' ', '')
            attr_type = attr_type.replace('Binary', 'String')
            attr_type = attr_type.replace('Enumeration', 'String')
            try:
                if isinstance(value, unicode): value = value.encode("utf-8")
            except:
                pass
            getattr(self.wrapped_data, "setArgumentAs%s" % attr_type)(idx, entity_instance.unwrap_value(value))
        return value

    def __len__(self):
        return len(self.wrapped_data)

    def __repr__(self):
        return repr(self.wrapped_data)

    def is_a(self, *args):
        return self.wrapped_data.is_a(*args)

    def id(self):
        return self.wrapped_data.id()

    def __eq__(self, other):
        if type(self) != type(other): return False
        return self.wrapped_data == other.wrapped_data

    def __hash__(self):
        return hash((self.id(), self.wrapped_data.file_pointer()))

    def __dir__(self):
        return sorted(set(itertools.chain(
            dir(type(self)),
            map(str, self.wrapped_data.get_attribute_names()),
            map(str, self.wrapped_data.get_inverse_attribute_names())
        )))

    def get_info(self, include_identifier=True, recursive=False, return_type=dict, ignore=()):
        def _():
            try:
                if include_identifier:
                    yield "id", self.id()
                yield "type", self.is_a()
            except:
                logging.exception("unhandled exception while getting id / type info on {}".format(self))
            for i in range(len(self)):
                try:
                    if self.wrapped_data.get_attribute_names()[i] in ignore:
                        continue
                    attr_value = self[i]
                    if recursive:
                        is_instance = lambda e: isinstance(e, entity_instance)
                        def get_info_(inst):
                            # for ty in ignore:
                            #     if inst.is_a(ty):
                            #         return None
                            return entity_instance.get_info(inst,
                                include_identifier=include_identifier,
                                recursive=recursive,
                                return_type=return_type,
                                ignore=ignore
                            )
                        attr_value = entity_instance.walk(is_instance, get_info_, attr_value)
                    yield self.attribute_name(i), attr_value
                except:
                    logging.exception("unhandled exception occured setting attribute name for {}".format(self))
        return return_type(_())

    __dict__ = property(get_info)
