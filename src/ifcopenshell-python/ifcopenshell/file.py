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

import numbers
import functools

from . import ifcopenshell_wrapper
from .entity_instance import entity_instance

try:
    # Python 2
    basestring
except NameError:
    # Python 3 or newer
    basestring = (str, bytes)


class file(object):
    """
    Base class for containing IFC files.

    Class has instance methods for filtering by element Id, Type, etc.

    Instantiated objects can be subscripted by Id or Guid

    example:

    ifc_file = ifcopenshell.open(file_path)
    products = ifc_file.by_type("IfcProduct")

    print(products[0].id(), products[0].GlobalId)
    >>> 122 2XQ$n5SLP5MBLyL442paFx

    # Subscripting
    print(products[0] == ifc_file[122] == ifc_file['2XQ$n5SLP5MBLyL442paFx'])
    >>> True
    """
    def __init__(self, f=None, schema=None):
        if f is not None:
            self.wrapped_data = f
        else:
            args = filter(None, [schema])
            args = map(ifcopenshell_wrapper.schema_by_name, args)
            self.wrapped_data = ifcopenshell_wrapper.file(*args)

    def create_entity(self, type, *args, **kwargs):
        e = entity_instance((self.schema, type))
        self.wrapped_data.add(e.wrapped_data)
        e.wrapped_data.this.disown()
        attrs = list(enumerate(args)) + \
            [(e.wrapped_data.get_argument_index(name), arg) for name, arg in kwargs.items()]
        for idx, arg in attrs:
            e[idx] = arg
        return e

    def __getattr__(self, attr):
        if attr[0:6] == 'create':
            return functools.partial(self.create_entity, attr[6:])
        else:
            return getattr(self.wrapped_data, attr)

    def __getitem__(self, key):
        if isinstance(key, numbers.Integral):
            return entity_instance(self.wrapped_data.by_id(key))
        elif isinstance(key, basestring):
            return entity_instance(self.wrapped_data.by_guid(str(key)))

    def by_id(self, id):
        """
        Return IFC objects filtered by IFC ID.

        Returned objects are unwrapped IFC objects.
        """
        return self[id]

    def by_guid(self, guid):
        """
        Return IFC objects filtered by IFC GUID.

        Returned objects are unwrapped IFC objects.
        """
        return self[guid]

    def add(self, inst):
        inst.wrapped_data.this.disown()
        return entity_instance(self.wrapped_data.add(inst.wrapped_data))

    def by_type(self, type):
        """
        Return IFC objects filtered by IFC Type and wrapped with the entity_instance class.

        See ifcopenshell.entity_instance for class methods and properties
        """
        return [entity_instance(e) for e in self.wrapped_data.by_type(type)]

    def traverse(self, inst, max_levels=None):
        if max_levels is None:
            max_levels = -1
        return [entity_instance(e) for e in self.wrapped_data.traverse(inst.wrapped_data, max_levels)]

    def get_inverse(self, inst):
        return [entity_instance(e) for e in self.wrapped_data.get_inverse(inst.wrapped_data)]

    def remove(self, inst):
        return self.wrapped_data.remove(inst.wrapped_data)

    def __iter__(self):
        return iter(self[id] for id in self.wrapped_data.entity_names())

    @staticmethod
    def from_string(s):
        return file(ifcopenshell_wrapper.read(s))
