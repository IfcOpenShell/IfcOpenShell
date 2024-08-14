# IfcPatch - IFC patching utiliy
# Copyright (C) 2020, 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of IfcPatch.
#
# IfcPatch is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# IfcPatch is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with IfcPatch.  If not, see <http://www.gnu.org/licenses/>.

import ifcopenshell
import ifcopenshell.util.element


class Patcher:
    def __init__(self, src, file, logger):
        """Optimise the filesize of an IFC model

        It is possible to non-losslessly optimise the filesize of an IFC model.

        Note that this is usually not recommended. Optimising runs a risk of
        losing some indirect semantic data critical for native IFC authoring.
        Most parties who recommend optimisation are not aware of these risks.
        Optimising is only safe in the context of read-only IFCs.

        If filesize is an issue, another approach would be to use IFCZIP
        instead to compress the model. Optimising the model only typically
        affects filesize and has minimal impact on load times. Large filesizes
        can usually be solved through other means. Consult the bonsai Add-on
        documentation on dealing with large models for more details.

        Warning: this optimise recipe is very, very slow. Please consider using
        RecycleNonRootedElements instead.

        Example:

        .. code:: python

            ifcpatch.execute({"input": "input.ifc", "file": model, "recipe": "Optimise", "arguments": []})
        """
        self.src = src
        self.file = file
        self.logger = logger
        self.optimized_file = ifcopenshell.file(schema=self.file.schema)

    def patch(self):
        from toposort import toposort_flatten as toposort

        def generate_instances_and_references():
            """
            Generator which yields an entity id and
            the set of all of its references contained in its attributes.
            """
            for inst in self.file:
                yield inst.id(), set(i.id() for i in self.file.traverse(inst)[1:] if i.id())

        instance_mapping = {}

        def map_value(v):
            """
            Recursive function which replicates an entity instance, with
            its attributes, mapping references to already registered
            instances. Indeed, because of the toposort we know that
            forward attribute value instances are mapped before the instances
            that reference them.
            """
            if isinstance(v, (list, tuple)):
                # lists are recursively traversed
                return type(v)(map(map_value, v))
            elif isinstance(v, ifcopenshell.entity_instance):
                if v.id() == 0:
                    # express simple types are not part of the toposort and just copied
                    return self.optimized_file.create_entity(v.is_a(), v[0])

                return instance_mapping[v]
            else:
                # a plain python value can just be returned
                return v

        info_to_id = {}

        for id in toposort(dict(generate_instances_and_references())):
            inst = self.file[id]
            info = inst.get_info(include_identifier=False, recursive=True, return_type=frozenset)
            if info in info_to_id:
                mapped = instance_mapping[inst] = instance_mapping[self.file[info_to_id[info]]]

            else:
                info_to_id[info] = id
                instance_mapping[inst] = self.optimized_file.create_entity(inst.is_a(), *map(map_value, inst))

        self.file = self.optimized_file
