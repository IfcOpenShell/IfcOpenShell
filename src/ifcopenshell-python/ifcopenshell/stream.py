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

from __future__ import annotations

try:
    import os
    import re

    import ifcopenshell.util.attribute
    import ifcopenshell.util.schema
    from .file import file
    from . import ifcopenshell_wrapper
    from .entity_instance import entity_instance

    from lark import Lark, Transformer
    from typing import Any, NoReturn, Union, Optional

    class StreamTransformer(Transformer):
        file: file

        def string(self, items):
            return str(items[0])[1:-1]

        def float(self, items):
            return float(items[0])

        def ifcint(self, items):
            return int(items[0])

        def null(self, items):
            return None

        def derived(self, items):
            return None

        def enum(self, items):
            if items[0] == ".T.":
                return True
            elif items[0] == ".F.":
                return False
            elif items[0] == ".U.":
                return "UNKNOWN"
            return str(items[0])[1:-1]

        def list(self, items):
            # List is always called twice, I think due to an ambiguity in the Lark
            # definition between a list and an arg, but I'm not quite sure.
            # print('calling list with', items)
            if items and isinstance(items[0], dict):
                return tuple(items[0]["list"])
            return {"list": items}

        def inline_type(self, items):
            # inline_type is also always called twice. Why?
            if items and isinstance(items[0], dict):
                return items[0]["inline_type"]
            entity = ifcopenshell.create_entity(items[0])
            entity[0] = items[1]
            return {"inline_type": entity}

        def reference(self, items):
            return self.file.by_id(int(items[0][1:]))

        def arg(self, items):
            return items[0]

        def args(self, items):
            return items

        def start(self, items):
            return (int(items[0]), str(items[1]), items[2])

    class stream(file):
        def __init__(self, filepath: str):
            self.history_size = 64
            self.history = []
            self.future = []
            self.transaction = None

            self.filepath = filepath

            self.file = open(filepath, "r")
            self.id_map: dict[int, str] = {}
            self.class_map: dict[str, list[int]] = {}
            self.id_offset: dict[int, int] = {}
            self.reference_pattern = re.compile(r"#(\d+)")
            self.entity_cache: dict[int, stream_entity] = {}
            self.inverses: dict[int, list[int]] = {}

            # common.INT doesn't support negative integers.
            grammar = r"""
                start: "#" NUMBER "=" TYPE "(" args ")" ";"

                args: arg ("," arg)*

                arg: STRING        -> string
                    | FLOAT        -> float
                    | IFCINT       -> ifcint
                    | NULL         -> null
                    | DERIVED      -> derived
                    | ENUM         -> enum
                    | REFERENCE    -> reference
                    | list         -> list
                    | inline_type  -> inline_type

                list: "(" arg? ("," arg)* ")"
                inline_type: TYPE "(" arg ")"
                REFERENCE: "#" /[0-9]+/

                TYPE: CNAME
                NUMBER: INT

                STRING: "'" /([^']|'')*/ "'"
                IFCINT: /-?[0-9]+/
                FLOAT: /-?[0-9]+\.[0-9]*([Ee]-?[0-9]+)?/
                NULL: "$"
                DERIVED: "*"
                ENUM: "." CNAME "."

                %import common.INT
                %import common.CNAME
            """

            transformer = StreamTransformer()
            transformer.file = self
            self.parser = Lark(grammar, parser="lalr", transformer=transformer)

            exclude_classes = [
                "IfcObjectPlacement",
                "IfcPresentationItem",
                "IfcPresentationStyle",
                "IfcProductRepresentation",
                "IfcRepresentation",
                "IfcRepresentationItem",
            ]
            exclude_classes = []

            exclude = set()

            offset = 0
            newline_character = len(os.linesep)
            for line in self.file:
                line = line.strip()
                if line.startswith("#"):
                    step_id, ifc_class = line.split("(")[0].split("=")
                    step_id = int(step_id.strip()[1:])
                    ifc_class = ifc_class.strip()

                    if ifc_class in exclude:
                        offset += len(line) + newline_character
                        continue

                    for reference_id in self.reference_pattern.findall(line[1:]):
                        self.inverses.setdefault(int(reference_id), []).append(step_id)

                    self.id_map[step_id] = ifc_class
                    self.class_map.setdefault(ifc_class, []).append(step_id)
                    self.id_offset[step_id] = offset
                elif line.startswith("FILE_SCHEMA"):
                    self._schema = line.split("'")[1]
                    self.ifc_schema = ifcopenshell.schema_by_name(self.schema)
                    for ifc_class in exclude_classes:
                        declaration = self.ifc_schema.declaration_by_name(ifc_class)
                        exclude.update([st.name().upper() for st in ifcopenshell.util.schema.get_subtypes(declaration)])
                offset += len(line) + newline_character

            self.preprocess_schema()

        def preprocess_schema(self) -> None:
            self.ifc_class_names = {}
            self.ifc_class_subtypes = {}
            self.ifc_class_attributes: dict[str, dict[str, ifcopenshell_wrapper.attribute]] = {}
            self.ifc_class_inverse_attributes = {}
            self.ifc_class_references = {}
            self.ifc_class_inverses = {}

            for declaration in self.ifc_schema.entities():
                self.ifc_class_names[declaration.name().upper()] = declaration.name()

                self.ifc_class_subtypes[declaration.name()] = ifcopenshell.util.schema.get_subtypes(declaration)
                self.ifc_class_attributes[declaration.name()] = {a.name(): a for a in declaration.all_attributes()}
                self.ifc_class_inverse_attributes[declaration.name()] = {
                    a.name(): a for a in declaration.all_inverse_attributes()
                }

                entity = []
                entity_list = []
                for attribute in declaration.all_attributes():
                    primitive = ifcopenshell.util.attribute.get_primitive_type(attribute)
                    if primitive == "entity":
                        entity.append(attribute.name())

                        attribute_entity = attribute.type_of_attribute().declared_type()
                        for subtype in ifcopenshell.util.schema.get_subtypes(attribute_entity):
                            self.ifc_class_inverses.setdefault(subtype.name(), {})
                            self.ifc_class_inverses[subtype.name()].setdefault(declaration.name(), [])
                            self.ifc_class_inverses[subtype.name()][declaration.name()].append(attribute.name())

                    elif self.is_entity_list(attribute):
                        entity_list.append(attribute.name())

                        for entity_name in re.findall("<entity (.*?)>", str(attribute)):
                            attribute_entity = self.ifc_schema.declaration_by_name(entity_name)
                            for subtype in ifcopenshell.util.schema.get_subtypes(attribute_entity):
                                # self.ifc_class_inverses.setdefault(subtype.name(), set()).add(declaration.name())
                                self.ifc_class_inverses.setdefault(subtype.name(), {})
                                self.ifc_class_inverses[subtype.name()].setdefault(declaration.name(), [])
                                self.ifc_class_inverses[subtype.name()][declaration.name()].append(attribute.name())

                self.ifc_class_references[declaration.name()] = {"entity": entity, "entity_list": entity_list}

        def clear_cache(self) -> None:
            self.entity_cache = {}

        def create_entity(self, type, *args, **kawrgs) -> NoReturn:
            """Not supported during streaming."""
            assert False, "Not supported during streaming."

        def by_id(self, id: int) -> Union[stream_entity, None]:
            entity = self.entity_cache.get(id, None)
            if entity:
                return entity
            ifc_class = self.id_map.get(id, None)
            if ifc_class:
                entity = stream_entity(id, self.ifc_class_names[ifc_class], self)
                self.entity_cache[id] = entity
                return entity

        def by_type(self, type: str, include_subtypes: bool = True) -> list[stream_entity]:
            results = []
            subtypes = self.ifc_class_subtypes[type] if include_subtypes else self.ifc_class_subtypes[type][0:1]
            for subtype in subtypes:
                results.extend([self.by_id(i) for i in self.class_map.get(subtype.name().upper(), [])])
            return results

        def traverse(
            self, inst: stream_entity, max_levels: Optional[int, None] = None, breadth_first: bool = False
        ) -> list[stream_entity]:
            results = [inst]
            queue = [inst]
            while queue:
                if max_levels is not None:
                    max_levels -= 1

                cur = queue.pop()
                level_results = set()

                for reference_id in self.reference_pattern.findall(str(cur)[1:]):
                    result = self.by_id(int(reference_id))
                    results.append(result)
                    if max_levels is None or max_levels:
                        queue.append(result)

            return results

        def get_inverse(
            self, inst: stream_entity, allow_duplicate: bool = False, with_attribute_indices: bool = False
        ) -> tuple[stream_entity, ...]:
            return {self.by_id(e) for e in self.inverses.get(inst.stream_wrapper.id, [])}

        def is_entity_list(self, attribute: ifcopenshell_wrapper.attribute) -> bool:
            attribute = str(attribute.type_of_attribute())
            if (attribute.startswith("<list") or attribute.startswith("<set")) and "<entity" in attribute:
                for data_type in re.findall("<(.*?) .*?>", attribute):
                    if data_type not in ("list", "set", "select", "entity"):
                        return False
                return True
            return False

        def __del__(self) -> None:
            # Override to avoid clean up unrelated to stream file.
            pass

        @property
        def wrapped_data(self) -> NoReturn:  # pyright: ignore[reportIncompatibleVariableOverride]
            class_name = type(self).__name__
            raise Exception(
                f"No `wrapped_data` for {class_name}. `ifcopenshell.{class_name}` is probably confused with `ifcopenshell.file`."
            )

        @property
        def header(self) -> NoReturn:
            raise NotImplementedError("`stream.header` is not implemented yet.")

        @property
        def schema(self) -> ifcopenshell.util.schema.IFC_SCHEMA:
            return self._schema

        @property
        def schema_identifier(self) -> str:
            # The best option we've got for mimicing `file.schema_identifier`.
            return self._schema

    class stream_entity(entity_instance):
        stream_wrapper: stream_wrapper

        def __init__(self, id: int, ifc_class: str, file: stream = None):
            if not ifc_class:
                print(id, ifc_class, file)
                assert False
            e = ifcopenshell_wrapper.new_IfcBaseClass(file.schema, ifc_class)
            s = stream_wrapper(id, ifc_class, file)
            super(entity_instance, self).__setattr__("wrapped_data", e)
            super(entity_instance, self).__setattr__("stream_wrapper", s)

        def id(self) -> int:
            return self.stream_wrapper.id

        def __repr__(self) -> str:
            offset = self.stream_wrapper.file.id_offset[self.stream_wrapper.id]
            self.stream_wrapper.file.file.seek(offset)
            return self.stream_wrapper.file.file.readline().strip()

        def __del__(self) -> None:
            pass

        def __getitem__(self, key: int) -> Any:
            return self.__getattr__(list(self.stream_wrapper.attributes.keys())[key])

        def __setattr__(self, key: str, value: int) -> NoReturn:
            """Not supported during streaming."""
            assert False, "Not supported during streaming."

        def __getattr__(self, name: str) -> Any:
            INVALID, FORWARD, INVERSE = range(3)
            attr_cat = self.wrapped_data.get_attribute_category(name)
            if attr_cat == FORWARD:
                if self.stream_wrapper.attribute_cache:
                    return self.stream_wrapper.attribute_cache[name]

                offset = self.stream_wrapper.file.id_offset[self.stream_wrapper.id]
                self.stream_wrapper.file.file.seek(offset)
                line = self.stream_wrapper.file.file.readline()
                attributes = self.stream_wrapper.file.parser.parse(line.strip())[2]

                for i, attribute in enumerate(self.stream_wrapper.attributes.values()):
                    self.stream_wrapper.attribute_cache[attribute.name()] = attributes[i]
                return self.stream_wrapper.attribute_cache[name]
            elif attr_cat == INVERSE:
                if self.stream_wrapper.inverse_attribute_cache:
                    results = self.stream_wrapper.inverse_attribute_cache.get(name, None)
                    if results is not None:
                        return results

                results = []

                element_ids = self.stream_wrapper.file.inverses.get(self.stream_wrapper.id, [])
                if not element_ids:
                    self.stream_wrapper.inverse_attribute_cache[name] = tuple()
                    return self.stream_wrapper.inverse_attribute_cache[name]

                attribute = self.stream_wrapper.inverse_attributes[name]
                entity_class = attribute.entity_reference().name()
                declaration = self.stream_wrapper.file.ifc_schema.declaration_by_name(entity_class)
                forward_name = attribute.attribute_reference().name()

                subtypes = [st.name() for st in ifcopenshell.util.schema.get_subtypes(declaration)]
                for element_id in element_ids:
                    ifc_class = self.stream_wrapper.file.ifc_class_names[self.stream_wrapper.file.id_map[element_id]]
                    if ifc_class in subtypes:
                        potential_result = self.stream_wrapper.file.by_id(element_id)
                        forward_value = getattr(potential_result, forward_name, None)
                        if not forward_value:
                            pass
                        elif isinstance(forward_value, tuple):
                            if self.stream_wrapper.id in [e.id() for e in forward_value]:
                                results.append(potential_result)
                        elif forward_value.id() == self.stream_wrapper.id:
                            results.append(potential_result)

                self.stream_wrapper.inverse_attribute_cache[name] = tuple(results)
                return self.stream_wrapper.inverse_attribute_cache[name]

            raise AttributeError(
                "entity instance of type '%s' has no attribute '%s'" % (self.wrapped_data.is_a(True), name)
            )

        def __eq__(self, other: stream_entity) -> bool:
            if not isinstance(self, type(other)):
                return False
            elif None in (self.stream_wrapper.file, other.stream_wrapper.file):
                assert False  # not implemented
            if self.stream_wrapper.id:
                return self.stream_wrapper.id == other.stream_wrapper.id
            assert False  # not implemented

        def __hash__(self) -> int:
            if self.stream_wrapper.id:
                return hash((self.stream_wrapper.id, self.stream_wrapper.file.filepath))

        def get_info(
            self, include_identifier=True, recursive=False, return_type=dict, ignore=(), scalar_only=False
        ) -> dict[str, Any]:
            info = {"id": self.stream_wrapper.id, "type": self.stream_wrapper.ifc_class}
            if not self.stream_wrapper.attribute_cache:
                self.__getitem__(0)  # This will get all attributes
            info.update(self.stream_wrapper.attribute_cache)
            return info

    class stream_wrapper:
        def __init__(self, id: int, ifc_class: str, file: stream):
            self.id = id
            self.ifc_class = ifc_class
            self.file = file
            self.attributes = self.file.ifc_class_attributes[self.ifc_class]
            self.inverse_attributes = self.file.ifc_class_inverse_attributes[self.ifc_class]
            self.attribute_cache: dict[str, Any] = {}
            self.inverse_attribute_cache = {}

        def __repr__(self) -> str:
            return f"stream_wrapper '#{self.id}={self.ifc_class}(...)'"

except ImportError as e:
    import sys

    print(f"No stream support: {e}", file=sys.stderr)
