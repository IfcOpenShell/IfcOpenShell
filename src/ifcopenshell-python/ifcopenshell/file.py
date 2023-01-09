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

import os
from pathlib import Path
import numbers
import functools
import zipfile

import ifcopenshell.util.element
import ifcopenshell.util.file
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
        self.is_batched = False
        self.batch_delete_index = 0
        self.batch_delete_ids = set()
        self.batch_inverses = []

    def serialise_entity_instance(self, element):
        info = element.get_info()
        for key, value in info.items():
            info[key] = self.serialise_value(element, value)
        return info

    def serialise_value(self, element, value):
        return element.walk(
            lambda v: isinstance(v, entity_instance),
            lambda v: {"id": v.id()} if v.id() else {"type": v.is_a(), "value": v.wrappedValue},
            value,
        )

    def unserialise_value(self, element, value):
        return element.walk(
            lambda v: isinstance(v, dict),
            lambda v: self.file.by_id(v["id"]) if v.get("id") else self.file.create_entity(v["type"], v["value"]),
            value,
        )

    def batch(self):
        self.is_batched = True
        self.batch_delete_index = len(self.operations)
        self.batch_delete_ids = set()
        self.batch_inverses = []

    def unbatch(self):
        for inverses in self.batch_inverses:
            if inverses:
                self.operations.insert(self.batch_delete_index, {"action": "batch_delete", "inverses": inverses})
        self.is_batched = False
        self.batch_delete_index = 0
        self.batch_delete_ids = set()
        self.batch_inverses = []

    def store_create(self, element):
        if element.id():
            self.operations.append({"action": "create", "value": self.serialise_entity_instance(element)})

    def store_edit(self, element, index, value):
        self.operations.append(
            {
                "action": "edit",
                "id": element.id(),
                "index": index,
                "old": self.serialise_value(element, element[index]),
                "new": self.serialise_value(element, value),
            }
        )

    def store_delete(self, element):
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

    def get_element_inverses(self, element):
        inverses = {}
        for inverse in self.file.get_inverse(element):
            inverse_references = []
            for i, attribute in enumerate(inverse):
                if ifcopenshell.util.element.has_element_reference(attribute, element):
                    inverse_references.append((i, self.serialise_value(inverse, attribute)))
            inverses[inverse.id()] = inverse_references
        return inverses

    def rollback(self):
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

    def commit(self):
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


class file(object):
    """Base class for containing IFC files.

    Class has instance methods for filtering by element Id, Type, etc.
    Instantiated objects can be subscripted by Id or Guid

    Example:

    .. code:: python

        ifc_file = ifcopenshell.open(file_path)
        products = ifc_file.by_type("IfcProduct")
        print(products[0].id(), products[0].GlobalId) # 122 2XQ$n5SLP5MBLyL442paFx
        print(products[0] == ifc_file[122] == ifc_file["2XQ$n5SLP5MBLyL442paFx"]) # True
    """

    def __init__(self, f=None, schema=None):
        """Create a new file object"""
        if f is not None:
            self.wrapped_data = f
        else:
            args = filter(None, [schema])
            args = map(ifcopenshell_wrapper.schema_by_name, args)
            self.wrapped_data = ifcopenshell_wrapper.file(*args)
        self.history_size = 64
        self.history = []
        self.future = []
        self.transaction = None

    def set_history_size(self, size):
        self.history_size = size
        while len(self.history) > self.history_size:
            self.history.pop(0)

    def begin_transaction(self):
        if self.history_size:
            self.transaction = Transaction(self)

    def end_transaction(self):
        if self.transaction:
            self.history.append(self.transaction)
            if len(self.history) > self.history_size:
                self.history.pop(0)
            self.future = []
            self.transaction = None

    def discard_transaction(self):
        if self.transaction:
            self.transaction.rollback()
        self.transaction = None

    def undo(self):
        if not self.history:
            return
        transaction = self.history.pop()
        transaction.rollback()
        self.future.append(transaction)

    def redo(self):
        if not self.future:
            return
        transaction = self.future.pop()
        transaction.commit()
        self.history.append(transaction)

    def create_entity(self, type, *args, **kwargs):
        """Create a new IFC entity in the file.

        :param type: Case insensitive name of the IFC class
        :type type: string
        :param args: The positional arguments of the IFC class
        :param kwargs: The keyword arguments of the IFC class
        :returns: An entity instance
        :rtype: ifcopenshell.entity_instance.entity_instance

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

        e = entity_instance((self.schema, type), self)

        # Create pairs of {attribute index, attribute value}.
        # Keyword arguments are mapped to their corresponding
        # numeric index with get_argument_index().

        # @todo we should probably check that values for
        # attributes are not passed as duplicates using
        # both regular arguments and keyword arguments.
        attrs = list(enumerate(args)) + [(e.wrapped_data.get_argument_index(name), arg) for name, arg in kwargs.items()]

        # Don't store these attributes as transactions
        # as the creation it self is already stored with
        # it's arguments
        if attrs:
            transaction = self.transaction
            self.transaction = None

        for idx, arg in attrs:
            e[idx] = arg

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

    def __getattr__(self, attr):
        if attr[0:6] == "create":
            return functools.partial(self.create_entity, attr[6:])
        else:
            return getattr(self.wrapped_data, attr)

    def __getitem__(self, key):
        if isinstance(key, numbers.Integral):
            return entity_instance(self.wrapped_data.by_id(key), self)
        elif isinstance(key, basestring):
            return entity_instance(self.wrapped_data.by_guid(str(key)), self)

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

    def add(self, inst, _id=None):
        """Adds an entity including any dependent entities to an IFC file.

        If the entity already exists, it is not re-added."""
        if self.transaction:
            max_id = self.wrapped_data.getMaxId()
        inst.wrapped_data.this.disown()
        result = entity_instance(self.wrapped_data.add(inst.wrapped_data, -1 if _id is None else _id), self)
        if self.transaction:
            added_elements = [e for e in self.traverse(result) if e.id() > max_id]
            [self.transaction.store_create(e) for e in reversed(added_elements)]
        return result

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
            return [entity_instance(e, self) for e in self.wrapped_data.by_type(type)]
        return [entity_instance(e, self) for e in self.wrapped_data.by_type_excl_subtypes(type)]

    def traverse(self, inst, max_levels=None, breadth_first=False):
        """Get a list of all referenced instances for a particular instance including itself

        :param inst: The entity instance to get all sub instances
        :type inst: ifcopenshell.entity_instance.entity_instance
        :param max_levels: How far deep to recursively fetch sub instances. None or -1 means infinite.
        :type max_levels: None|int
        :param breadth_first: Whether to use breadth-first search, the default is depth-first.
        :type max_levels: bool
        :returns: A list of ifcopenshell.entity_instance.entity_instance objects
        :rtype: list
        """
        if max_levels is None:
            max_levels = -1

        if breadth_first:
            fn = self.wrapped_data.traverse_breadth_first
        else:
            fn = self.wrapped_data.traverse

        return [entity_instance(e, self) for e in fn(inst.wrapped_data, max_levels)]

    def get_inverse(self, inst, allow_duplicate=False, with_attribute_indices=False):
        """Return a list of entities that reference this entity

        :param inst: The entity instance to get inverse relationships
        :type inst: ifcopenshell.entity_instance.entity_instance
        :param allow_duplicate: Returns a `list` when True, `set` when False
        :param with_attribute_indices: Returns pairs of <i, idx>
           where i[idx] is inst or contains inst. Requires allow_duplicate=True
        :returns: A list of ifcopenshell.entity_instance.entity_instance objects
        :rtype: list
        """
        if with_attribute_indices and not allow_duplicate:
            raise ValueError("with_attribute_indices requires allow_duplicate to be True")

        inverses = [entity_instance(e, self) for e in self.wrapped_data.get_inverse(inst.wrapped_data)]

        if allow_duplicate:
            if with_attribute_indices:
                idxs = self.wrapped_data.get_inverse_indices(inst.wrapped_data)
                return list(zip(inverses, idxs))
            else:
                return inverses

        return set(inverses)

    def get_total_inverses(self, inst):
        """Returns the number of entities that reference this entity

        :param inst: The entity instance to get inverse relationships
        :type inst: ifcopenshell.entity_instance.entity_instance
        :returns: The total number of references
        :rtype: int
        """
        return self.wrapped_data.get_total_inverses(inst.wrapped_data)

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
        if self.transaction:
            self.transaction.batch()
        return self.wrapped_data.batch()

    def unbatch(self):
        """Low-level mechanism to speed up deletion of large subgraphs"""
        if self.transaction:
            self.transaction.unbatch()
        return self.wrapped_data.unbatch()

    def __iter__(self):
        return iter(self[id] for id in self.wrapped_data.entity_names())

    def write(self, path: "os.PathLike | str", format=None, zipped=False) -> None:
        """Write ifc model to file.

        :param format: Force use of a specific format. Guessed from file name if None.
        Supported formats : .ifc, .ifcXML, .ifcZIP (equivalent to format=".ifc" with zipped=True)
        For zipped .ifcXML use format=".ifcXML" with zipped=True
        :param zipped: zip the file after it is written

        Examples:
        >>> model.write("path/to/model.ifc")
        >>> model.write("path/to/model.ifcXML")
        >>> model.write("path/to/model.ifcZIP")
        >>> model.write("path/to/model.ifcZIP", format=".ifcXML", zipped=True)
        >>> model.write("path/to/model.anyextension", format=".ifcXML")
        """
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        if format == None:
            format = ifcopenshell.util.file.guess_format(path)
        if format == ".ifcXML":
            serializer = ifcopenshell_wrapper.XmlSerializer(self, str(path))
            serializer.finalize()
            if zipped:
                unzipped_path = path.with_suffix(format)
                path.rename(unzipped_path)
                with zipfile.ZipFile(path, "w") as zip_file:
                    zip_file.write(unzipped_path, unzipped_path.name, compress_type=zipfile.ZIP_DEFLATED)
                unzipped_path.unlink()
            return
        if format == ".ifcZIP":
            return self.write(path, ".ifc", zipped=True)
        self.wrapped_data.write(str(path))
        if zipped:
            unzipped_path = path.with_suffix(format)
            path.rename(unzipped_path)
            with zipfile.ZipFile(path, "w") as zip_file:
                zip_file.write(unzipped_path, unzipped_path.name, compress_type=zipfile.ZIP_DEFLATED)
                unzipped_path.unlink()
        return

    @staticmethod
    def from_string(s):
        return file(ifcopenshell_wrapper.read(s))
