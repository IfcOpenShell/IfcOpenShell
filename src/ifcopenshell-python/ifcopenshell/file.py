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


class Transaction:
    def __init__(self, ifc_file):
        self.file = ifc_file
        self.operations = []

    def serialise_entity_instance(self, info):
        for key, value in info.items():
            if isinstance(value, entity_instance):
                info[key] = {"type": "single", "id": value.id()}
            elif isinstance(value, tuple) and isinstance(value[0], entity_instance):
                info[key] = {"type": "multiple", "ids": [v.id() for v in value]}
        return info

    def store_create(self, element):
        self.operations.append({'action': 'create', 'value': self.serialise_entity_instance(element.get_info())})

    def store_edit(self, element, index, value):
        self.operations.append({'action': 'edit', 'id': element.id(), 'index': index, 'old': element[index], 'new': value})

    def store_delete(self, element):
        inverses = {}
        for inverse in self.file.get_inverse(element):
            inverse_references = []
            for i, attribute in enumerate(inverse):
                if attribute == element:
                    inverse_references.append((i, 'single'))
                elif isinstance(attribute, tuple) and element in attribute:
                    inverse_references.append((i, 'multiple'))
            inverses[inverse.id()] = inverse_references
        self.operations.append({
            'action': 'delete', 'inverses': inverses, 'value': self.serialise_entity_instance(element.get_info())
        })

    def undo(self):
        self.file.wrapped_data.recalculate_id_counter()
        for operation in self.operations[::-1]:
            print('UNDOING OPERATION', operation)
            if operation['action'] == 'create':
                element = self.file.by_id(operation['value']['id'])
                if hasattr(element, "GlobalId"):
                    # hack, otherwise ifcopenshell gets upset
                    element.GlobalId = 'x'
                self.file.remove(element)
                self.file.wrapped_data.recalculate_id_counter()
            elif operation['action'] == 'edit':
                element = self.file.by_id(operation['id'])
                element[operation['index']] = operation['old']
            elif operation['action'] == 'delete':
                e = self.file.create_entity(operation['value']['type'])
                for k, v in operation['value'].items():
                    if isinstance(v, dict):
                        if v['type'] == 'single':
                            v = self.file.by_id(v['id'])
                        elif v['type'] == 'multiple':
                            v = [self.file.by_id(i) for i in v['ids']]
                    try:
                        setattr(e, k, v)
                    except:
                        pass
                for inverse_id, data in operation['inverses'].items():
                    inverse = self.file.by_id(inverse_id)
                    for index, data_type in data:
                        if data_type == 'single':
                            inverse[index] = e
                        elif data_type == 'multiple':
                            if inverse[index] is None:
                                inverse[index] = (e)
                            else:
                                new = list(inverse[index])
                                new.append(e)
                                inverse[index] = new

    def redo(self):
        for operation in self.operations:
            if operation['action'] == 'create':
                e = self.file.create_entity(operation['value']['type'])
                for k, v in operation['value'].items():
                    if isinstance(v, dict):
                        if v['type'] == 'single':
                            v = self.file.by_id(v['id'])
                        elif v['type'] == 'multiple':
                            v = [self.file.by_id(i) for i in v['ids']]
                    try:
                        setattr(e, k, v)
                    except:
                        pass
            elif operation['action'] == 'edit':
                element = self.file.by_id(operation['id'])
                element[operation['index']] = operation['new']
            elif operation['action'] == 'delete':
                element = self.file.by_id(operation['value']['id'])
                self.file.remove(element)
                self.file.wrapped_data.recalculate_id_counter()



class file(object):
    """Base class for containing IFC files.

    Class has instance methods for filtering by element Id, Type, etc.
    Instantiated objects can be subscripted by Id or Guid

    Example::

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
        self.history_size = 5
        self.history = [None] * self.history_size
        self.current_history_index = self.history_size - 1
        self.transaction = None

    def begin_transaction(self):
        self.transaction = Transaction(self)

    def end_transaction(self):
        if self.transaction:
            self.history.append(self.transaction)
            self.history.pop(0)
            self.transaction = None

    def discard_transaction(self):
        self.transaction = None

    def undo(self):
        if self.current_history_index < 0:
            return
        event = self.history[self.current_history_index]
        if event:
            event.undo()
            self.current_history_index -= 1

    def redo(self):
        if self.current_history_index + 1 >= self.history_size:
            return
        event = self.history[self.current_history_index + 1]
        if event:
            event.redo()
            self.current_history_index += 1

    def create_entity(self, type, *args, **kwargs):
        """Create a new IFC entity in the file.

        :param type: Case insensitive name of the IFC class
        :type type: string
        :param args: The positional arguments of the IFC class
        :param kwargs: The keyword arguments of the IFC class
        :returns: An entity instance
        :rtype: ifcopenshell.entity_instance.entity_instance

        Example::

            f = ifcopenshell.file()
            f.create_entity('IfcPerson')
            >>> #1=IfcPerson($,$,$,$,$,$,$,$)
            f.create_entity('IfcPerson', 'Foobar')
            >>> #2=IfcPerson('Foobar',$,$,$,$,$,$,$)
            f.create_entity('IfcPerson', Identification='Foobar')
            >>> #3=IfcPerson('Foobar',$,$,$,$,$,$,$)
        """
        e = entity_instance((self.schema, type))
        # Hack, can a entity access its file?
        e.wrapped_data.file = self
        self.wrapped_data.add(e.wrapped_data)
        e.wrapped_data.this.disown()
        attrs = list(enumerate(args)) + [(e.wrapped_data.get_argument_index(name), arg) for name, arg in kwargs.items()]
        for idx, arg in attrs:
            e[idx] = arg
        if self.transaction:
            self.transaction.store_create(e)
        return e

    def __getattr__(self, attr):
        if attr[0:6] == "create":
            return functools.partial(self.create_entity, attr[6:])
        else:
            return getattr(self.wrapped_data, attr)

    def __getitem__(self, key):
        if isinstance(key, numbers.Integral):
            e = entity_instance(self.wrapped_data.by_id(key))
            # Hack, can a entity access its file?
            e.wrapped_data.file = self
            return e
        elif isinstance(key, basestring):
            e = entity_instance(self.wrapped_data.by_guid(str(key)))
            # Hack, can a entity access its file?
            e.wrapped_data.file = self
            return e

    def by_id(self, id):
        """Return an IFC entity instance filtered by IFC ID.

        :param id: STEP numerical identifier
        :type id: int
        :returns: An ifcopenshell.entity_instance.entity_instance
        :rtype: ifcopenshell.entity_instance.entity_instance
        """
        return self[id]

    def by_guid(self, guid):
        """Return an IFC entity instance filtered by IFC GUID.

        :param guid: GlobalId value in 22-character encoded form
        :type guid: string
        :returns: An ifcopenshell.entity_instance.entity_instance
        :rtype: ifcopenshell.entity_instance.entity_instance
        """
        return self[guid]

    def add(self, inst):
        """Adds an entity including any dependent entities to an IFC file.

        If the entity already exists, it is not re-added."""
        inst.wrapped_data.this.disown()
        return entity_instance(self.wrapped_data.add(inst.wrapped_data))

    def by_type(self, type, include_subtypes=True):
        """Return IFC objects filtered by IFC Type and wrapped with the entity_instance class.

        If an IFC type class has subclasses, all entities of those subclasses are also returned.

        :param type: The case insensitive type of IFC class to return.
        :type type: string
        :param include_subtypes: Whether or not to return subtypes of the IFC class
        :type include_subtypes: bool
        :returns: A list of ifcopenshell.entity_instance.entity_instance objects
        :rtype: list
        """
        if include_subtypes:
            return [entity_instance(e) for e in self.wrapped_data.by_type(type)]
        return [entity_instance(e) for e in self.wrapped_data.by_type_excl_subtypes(type)]

    def traverse(self, inst, max_levels=None):
        """Get a list of all referenced instances for a particular instance including itself

        :param inst: The entity instance to get all sub instances
        :type inst: ifcopenshell.entity_instance.entity_instance
        :param max_levels: How far deep to recursively fetch sub instances. None or -1 means infinite.
        :type max_levels: None|int
        :returns: A list of ifcopenshell.entity_instance.entity_instance objects
        :rtype: list
        """
        if max_levels is None:
            max_levels = -1
        return [entity_instance(e) for e in self.wrapped_data.traverse(inst.wrapped_data, max_levels)]

    def get_inverse(self, inst):
        """Return a list of entities that reference this entity

        :param inst: The entity instance to get inverse relationships
        :type inst: ifcopenshell.entity_instance.entity_instance
        :returns: A list of ifcopenshell.entity_instance.entity_instance objects
        :rtype: list
        """
        return [entity_instance(e) for e in self.wrapped_data.get_inverse(inst.wrapped_data)]

    def remove(self, inst):
        """Deletes an IFC object in the file.

        Attribute values in other entity instances that reference the deleted
        object will be set to null. In the case of a list or set of references,
        the reference to the deleted will be removed from the aggregate.

        :param inst: The entity instance to delete
        :type inst: ifcopenshell.entity_instance.entity_instance
        :rtype: None
        """
        if self.transaction:
            self.transaction.store_delete(inst)
        return self.wrapped_data.remove(inst.wrapped_data)
        
    def batch(self):
        """Low-level mechanism to speed up deletion of large subgraphs"""
        return self.wrapped_data.batch()
        
    def unbatch(self):
        """Low-level mechanism to speed up deletion of large subgraphs"""
        return self.wrapped_data.unbatch()

    def __iter__(self):
        return iter(self[id] for id in self.wrapped_data.entity_names())

    @staticmethod
    def from_string(s):
        return file(ifcopenshell_wrapper.read(s))
