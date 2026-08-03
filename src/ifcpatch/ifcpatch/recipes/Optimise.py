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

import logging

import ifcopenshell


def _toposort(graph: dict[int, set[int]], logger: logging.Logger) -> list[int]:
    """Flatten a dependency graph of entity ids into dependency order.

    Uses igraph's C-backed topological sort when available, otherwise falls
    back to the stdlib graphlib topological sort with a warning.
    """
    try:
        import igraph
    except ImportError:
        logger.warning(
            "igraph is not installed, falling back to the slower stdlib graphlib. "
            "Install python-igraph for better performance."
        )
        from graphlib import TopologicalSorter

        return list(TopologicalSorter(graph).static_order())

    ids = list(graph)
    index = {id_: i for i, id_ in enumerate(ids)}
    for references in graph.values():
        for reference in references:
            if reference not in index:
                index[reference] = len(ids)
                ids.append(reference)
    edges = [(index[reference], index[id_]) for id_, references in graph.items() for reference in references]
    order = igraph.Graph(n=len(ids), edges=edges, directed=True).topological_sorting(mode="out")
    return [ids[i] for i in order]


class Patcher:
    def __init__(self, file, logger):
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

        Warning: this optimise recipe is slower than RecycleNonRootedElements,
        as it performs a full, transitive fold instead of a single pass.
        Consider RecycleNonRootedElements first if a quicker, partial
        optimisation is acceptable.

        Example:

        .. code:: python

            ifcpatch.execute({"input": "input.ifc", "file": model, "recipe": "Optimise", "arguments": []})
        """
        self.file = file
        self.logger = logger
        self.optimized_file = ifcopenshell.file(schema=self.file.schema)

    def patch(self):
        def generate_instances_and_references():
            """
            Generator which yields an entity id and
            the set of all of its references contained in its attributes.
            """
            for inst in self.file:
                yield inst.id(), set(i.id() for i in self.file.traverse(inst, max_levels=1)[1:] if i.id())

        instance_mapping = {}

        def map_value(v, as_key=False):
            """
            Recursive function which either replicates an entity instance
            with its attributes mapped to already registered instances
            (as_key=False), or builds a hashable canonical key for it
            (as_key=True), reusing already-folded references instead of
            re-expanding their attribute subtrees.
            """
            if isinstance(v, (list, tuple)):
                return type(v)(map_value(item, as_key=as_key) for item in v)
            elif isinstance(v, ifcopenshell.entity_instance):
                if v.id() == 0:
                    # express simple types are not part of the toposort and just copied
                    if as_key:
                        return ("__type__", v.is_a(), v[0])
                    return self.optimized_file.create_entity(v.is_a(), v[0])
                mapped = instance_mapping[v]
                if as_key:
                    return ("__id__", mapped.id())
                return mapped
            else:
                # a plain python value can just be returned
                return v

        info_to_id = {}

        for id in _toposort(dict(generate_instances_and_references()), self.logger):
            inst = self.file[id]
            info = map_value(inst.get_info(include_identifier=False, recursive=False, return_type=tuple), as_key=True)
            if info in info_to_id:
                mapped = instance_mapping[inst] = instance_mapping[self.file[info_to_id[info]]]

            else:
                info_to_id[info] = id
                instance_mapping[inst] = self.optimized_file.create_entity(inst.is_a(), *map(map_value, inst))

        self.file = self.optimized_file
