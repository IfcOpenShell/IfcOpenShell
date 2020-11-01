import ifcopenshell
import ifcopenshell.util.element
from toposort import toposort_flatten as toposort


class Patcher:
    def __init__(self, src, file, logger, args=None):
        self.src = src
        self.file = file
        self.logger = logger
        self.args = args
        self.optimized_file = ifcopenshell.file(schema=self.file.schema)

    def patch(self):
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
