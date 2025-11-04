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
import re
import json
import types
import numpy as np
import numpy.typing as npt
import ifcopenshell
import ifcopenshell.util.attribute
import ifcopenshell.util.schema
from pathlib import Path
from typing import Any, NoReturn, Union, Optional, TYPE_CHECKING, TypedDict
from . import ifcopenshell_wrapper
from .file import file
from .entity_instance import entity_instance

if TYPE_CHECKING:
    import sqlite3

try:
    import sqlite3
except ImportError as e:
    print(f"No SQL support: {e}")


class GeometryCache(TypedDict):
    shapes: dict[int, GeometryCacheShape]
    geometry: dict[str, GeometryCacheGeometry]


class GeometryCacheShape(TypedDict):
    co: list[float]
    """Object location."""
    matrix: npt.NDArray[np.float64]
    geometry: Union[str, None]
    """Element's geometry id (same value as in ``Representation.id``).

    Is set to ``None` when no geometry is available for the element.
    """


class GeometryCacheGeometry(TypedDict):
    verts: npt.NDArray[np.float64]
    edges: npt.NDArray[np.int32]
    faces: npt.NDArray[np.int32]
    material_ids: npt.NDArray[np.int32]
    materials: list[int]


class sqlite(file):
    mvd_str: str
    """As in `header.file_description.description`."""

    def __init__(self, filepath: str):
        """
        Open existing sqlite IFC database.

        To create a new database from IFC file consider using Ifc2Sql IfcPatch:

        https://docs.ifcopenshell.org/autoapi/ifcpatch/recipes/Ifc2Sql/index.html

        :param filepath: Path to sqlite database.
        """

        if not Path(filepath).exists():
            raise FileNotFoundError(f"File doesn't exist: {filepath}")

        self.history_size = 64
        self.history = []
        self.future = []
        self.transaction = None

        self.filepath = filepath
        self.db = sqlite3.connect(self.filepath)
        self.db.row_factory = sqlite3.Row

        # import mysql.connector
        # self.db = mysql.connector.connect(
        #    host="localhost",
        #    user="root",
        #    password="root",
        #    database="test"
        # )

        self.cursor = self.db.cursor()

        try:
            self.cursor.execute("SELECT preprocessor, schema, mvd FROM metadata LIMIT 1")
            row = self.cursor.fetchone()
            if row[0] != "IfcOpenShell-1.0.0":
                assert False, "SQLite schema not supported."
        except:
            assert False, "SQLite schema not supported."

        self._schema = row[1]
        self.mvd_str = row[2]
        self.ifc_schema = ifcopenshell.schema_by_name(self.schema)

        self.cursor.execute("SELECT ifc_id, ifc_class FROM id_map")
        self.id_map: dict[int, str] = {}
        self.class_map: dict[str, list[int]] = {}
        self.entity_cache: dict[int, sqlite_entity] = {}
        for row in self.cursor.fetchall():
            ifc_id, ifc_class = row
            self.id_map[ifc_id] = ifc_class
            self.class_map.setdefault(ifc_class, []).append(ifc_id)

        self.preprocess_schema()

    def preprocess_schema(self) -> None:
        self.ifc_class_subtypes: dict[str, Any] = {}
        self.ifc_class_attributes: dict[str, dict[str, ifcopenshell_wrapper.attribute]] = {}
        self.ifc_class_inverse_attributes: dict[str, Any] = {}
        self.ifc_class_references = {}
        self.ifc_class_inverses = {}

        for declaration in self.ifc_schema.entities():
            # print('Dealing with declaration', declaration.name())

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
                    # print('is an entity list', attribute.name())
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
        """Not supported for sqlite database."""
        assert False, "Not supported for sqlite database."

    def by_id(self, id: int) -> Union[sqlite_entity, None]:
        entity = self.entity_cache.get(id, None)
        if entity:
            return entity
        ifc_class = self.id_map.get(id, None)
        if ifc_class:
            entity = sqlite_entity(id, ifc_class, self)
            self.entity_cache[id] = entity
            return entity
        self.cursor.execute("SELECT ifc_id, ifc_class FROM id_map WHERE ifc_id = ? LIMIT 1", (id,))
        row = self.cursor.fetchone()
        if row:
            _, ifc_class = row
            self.id_map[id] = ifc_class
            entity = sqlite_entity(id, ifc_class, self)
            self.entity_cache[id] = entity
            return entity

    def by_type(self, type: str, include_subtypes: bool = True) -> list[sqlite_entity]:
        # TODO use cached subtypes
        import ifcopenshell.util.schema

        if self.class_map:
            results = []
            subtypes = self.ifc_class_subtypes[type] if include_subtypes else self.ifc_class_subtypes[type][0:1]
            for subtype in subtypes:
                results.extend([self.by_id(i) for i in self.class_map.get(subtype.name(), [])])
            return results
        if include_subtypes:
            declaration = self.ifc_schema.declaration_by_name(type)
            subtypes = ",".join([f"'{st.name()}'" for st in ifcopenshell.util.schema.get_subtypes(declaration)])
            self.cursor.execute(f"SELECT ifc_id, ifc_class FROM id_map WHERE ifc_class IN ({subtypes})")
            rows = self.cursor.fetchall()
            return [self.by_id(r[0]) for r in rows]
        self.cursor.execute(f"SELECT ifc_id FROM id_map WHERE ifc_class='{type}'")
        rows = self.cursor.fetchall()
        return [self.by_id(r[0]) for r in rows]

    def traverse(
        self, inst: sqlite_entity, max_levels: Optional[int] = None, breadth_first: bool = False
    ) -> list[sqlite_entity]:
        results = [inst]
        queue = [inst]
        while queue:
            if max_levels is not None:
                max_levels -= 1

            cur = queue.pop()
            reference_attributes = self.ifc_class_references[cur.sqlite_wrapper.ifc_class]
            attributes = reference_attributes["entity"] + reference_attributes["entity_list"]
            if not attributes:
                continue

            for attribute in attributes:
                result = getattr(cur, attribute, [])
                if not result:
                    continue
                elif isinstance(result, tuple):
                    results.extend(result)
                    if max_levels is None or max_levels:
                        queue.extend(result)
                else:
                    results.append(result)
                    if max_levels is None or max_levels:
                        queue.append(result)
        # print('traverse results', results)
        return results

    def get_inverse(
        self, inst: sqlite_entity, allow_duplicate: bool = False, with_attribute_indices: bool = False
    ) -> set[sqlite_entity]:
        query = (
            f"SELECT inverses FROM {inst.sqlite_wrapper.ifc_class} WHERE `ifc_id` = {inst.sqlite_wrapper.id} LIMIT 1"
        )
        self.cursor.execute(query)
        row = self.cursor.fetchone()
        if not row or not row[0]:
            return set()
        return {self.by_id(e) for e in json.loads(row[0])}

    def is_entity_list(self, attribute: ifcopenshell_wrapper.attribute) -> bool:
        attribute = str(attribute.type_of_attribute())
        if (attribute.startswith("<list") or attribute.startswith("<set")) and "<entity" in attribute:
            for data_type in re.findall("<(.*?) .*?>", attribute):
                if data_type not in ("list", "set", "select", "entity"):
                    return False
            return True
        return False

    def get_geometry(self, ids: list[int]) -> GeometryCache:
        import numpy as np

        ids_csv = ",".join(map(str, ids))
        query = f"SELECT ifc_id, x, y, z, matrix, geometry, verts, edges, faces, material_ids, materials FROM shape LEFT JOIN geometry ON shape.geometry = geometry.id WHERE `ifc_id` IN ({ids_csv})"
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        shapes: dict[int, GeometryCacheShape] = {}
        geometry: dict[str, GeometryCacheGeometry] = {}
        for row in rows:
            if row["geometry"] and row["geometry"] not in geometry:
                # Same data types as in ifcopenshell.util.shape.
                geometry[row["geometry"]] = {
                    "verts": np.frombuffer(row["verts"], dtype="d") if row["verts"] else np.empty(0, dtype="d"),
                    "edges": np.frombuffer(row["edges"], dtype="i") if row["edges"] else np.empty(0, dtype="i"),
                    "faces": np.frombuffer(row["faces"], dtype="i") if row["faces"] else np.empty(0, dtype="i"),
                    "material_ids": (
                        np.frombuffer(row["material_ids"], dtype="i") if row["material_ids"] else np.empty(0, dtype="i")
                    ),
                    "materials": json.loads(row["materials"]) if row["materials"] else [],
                }
            shapes[row["ifc_id"]] = {
                "co": [row["x"], row["y"], row["z"]],
                "matrix": np.copy(np.frombuffer(row["matrix"], dtype="d").reshape((4, 4))),
                "geometry": row["geometry"],
            }
        ids_without_geometry = set(ids) - set(shapes.keys())
        for id in ids_without_geometry:
            shapes[id] = {
                "co": [0.0, 0.0, 0.0],
                "matrix": np.eye(4),
                "geometry": None,
            }
        return {"shapes": shapes, "geometry": geometry}

    def __del__(self) -> None:
        # Override to avoid clean up data unrelated to sqlite file.
        pass

    @property
    def wrapped_data(self) -> NoReturn:  # pyright: ignore[reportIncompatibleVariableOverride]
        class_name = type(self).__name__
        raise Exception(
            f"No `wrapped_data` for {class_name}. `ifcopenshell.{class_name}` is probably confused with `ifcopenshell.file`."
        )

    @property
    def schema(self) -> ifcopenshell.util.schema.IFC_SCHEMA:
        return self._schema

    @property
    def schema_identifier(self) -> str:
        # The best option we've got for mimicing `file.schema_identifier`.
        return self._schema

    @property
    def header(self) -> types.SimpleNamespace:
        # Mimicking `file_header` object from `ifcopenshell.file`.
        header = types.SimpleNamespace(
            file_description=types.SimpleNamespace(description=(self.mvd_str,)),
        )
        return header


class sqlite_entity(entity_instance):
    sqlite_wrapper: sqlite_wrapper

    def __init__(self, id: int, ifc_class: str, file: sqlite = None):
        if not ifc_class:
            print(id, ifc_class, file)
            assert False
        e = ifcopenshell_wrapper.new_IfcBaseClass(file.schema, ifc_class)
        s = sqlite_wrapper(id, ifc_class, file)
        super(entity_instance, self).__setattr__("wrapped_data", e)
        super(entity_instance, self).__setattr__("sqlite_wrapper", s)

    def id(self) -> int:
        return self.sqlite_wrapper.id

    def __del__(self) -> None:
        pass

    def __getitem__(self, key: int) -> Any:
        return self.__getattr__(list(self.sqlite_wrapper.attributes.keys())[key])

    def __setattr__(self, key: str, value: Any) -> None:
        # query = f"UPDATE `{self.sqlite_wrapper.ifc_class}` SET `{key}`='' WHERE `ifc_id` = {self.sqlite_wrapper.id}"
        query = f"UPDATE `{self.sqlite_wrapper.ifc_class}` SET `{key}` = ? WHERE ifc_id = {self.sqlite_wrapper.id}"
        self.sqlite_wrapper.file.cursor.execute(query, (value,))
        self.sqlite_wrapper.file.db.commit()
        self.sqlite_wrapper.attribute_cache = {}

    def __getattr__(self, name: str) -> Any:
        # print("*" * 100)
        # print("GETATTR", self.sqlite_wrapper.id, self.sqlite_wrapper.ifc_class, name)

        INVALID, FORWARD, INVERSE = range(3)
        attr_cat = self.wrapped_data.get_attribute_category(name)
        if attr_cat == FORWARD:
            if self.sqlite_wrapper.attribute_cache:
                # print(self.sqlite_wrapper.ifc_class)
                # print(self.sqlite_wrapper.attribute_cache)
                return self.sqlite_wrapper.attribute_cache[name]

            # print('first time for', self.sqlite_wrapper.ifc_class)

            # print("IT IS A FORWARD")
            query = f"SELECT * FROM {self.sqlite_wrapper.ifc_class} WHERE `ifc_id` = {self.sqlite_wrapper.id} LIMIT 1"
            self.sqlite_wrapper.file.cursor.execute(query)
            row = self.sqlite_wrapper.file.cursor.fetchone()

            for attribute in self.sqlite_wrapper.attributes.values():
                # attribute = self.sqlite_wrapper.attributes[name]
                aname = attribute.name()
                primitive = ifcopenshell.util.attribute.get_primitive_type(attribute)

                if not row or row[aname] is None:
                    self.sqlite_wrapper.attribute_cache[aname] = None
                elif primitive == "entity":
                    self.sqlite_wrapper.attribute_cache[aname] = self.sqlite_wrapper.file.by_id(row[aname])
                elif isinstance(primitive, tuple):
                    if isinstance(row[aname], int):
                        self.sqlite_wrapper.attribute_cache[aname] = self.sqlite_wrapper.file.by_id(row[aname])
                    else:
                        self.sqlite_wrapper.attribute_cache[aname] = self.unserialise_value(json.loads(row[aname]))
                else:
                    self.sqlite_wrapper.attribute_cache[aname] = row[aname]
                if isinstance(self.sqlite_wrapper.attribute_cache[aname], list):
                    self.sqlite_wrapper.attribute_cache[aname] = tuple(self.sqlite_wrapper.attribute_cache[aname])
            return self.sqlite_wrapper.attribute_cache[name]
        elif attr_cat == INVERSE:
            if self.sqlite_wrapper.inverse_attribute_cache:
                results = self.sqlite_wrapper.inverse_attribute_cache.get(name, None)
                if results is not None:
                    return results

            results = []

            query = f"SELECT inverses FROM {self.sqlite_wrapper.ifc_class} WHERE `ifc_id` = {self.sqlite_wrapper.id} LIMIT 1"
            self.sqlite_wrapper.file.cursor.execute(query)
            row = self.sqlite_wrapper.file.cursor.fetchone()
            if not row or not row[0]:
                self.sqlite_wrapper.inverse_attribute_cache[name] = tuple()
                return self.sqlite_wrapper.inverse_attribute_cache[name]

            attribute = self.sqlite_wrapper.inverse_attributes[name]
            entity_class = attribute.entity_reference().name()
            declaration = self.sqlite_wrapper.file.ifc_schema.declaration_by_name(entity_class)
            forward_name = attribute.attribute_reference().name()

            subtypes = [st.name() for st in ifcopenshell.util.schema.get_subtypes(declaration)]
            element_ids = json.loads(row[0])
            for element_id in element_ids:
                ifc_class = self.sqlite_wrapper.file.id_map[element_id]
                if ifc_class in subtypes:
                    potential_result = self.sqlite_wrapper.file.by_id(element_id)
                    forward_value = getattr(potential_result, forward_name, None)
                    if not forward_value:
                        pass
                    elif isinstance(forward_value, tuple):
                        if self.sqlite_wrapper.id in [e.id() for e in forward_value]:
                            results.append(potential_result)
                    elif forward_value.id() == self.sqlite_wrapper.id:
                        results.append(potential_result)

            self.sqlite_wrapper.inverse_attribute_cache[name] = tuple(results)
            return self.sqlite_wrapper.inverse_attribute_cache[name]

        raise AttributeError(
            "entity instance of type '%s' has no attribute '%s'" % (self.wrapped_data.is_a(True), name)
        )

    def unserialise_value(self, value):
        if isinstance(value, (tuple, list)):
            for i, value2 in enumerate(value):
                value[i] = self.unserialise_value(value2)
            return value
        elif isinstance(value, int):
            return self.sqlite_wrapper.file.by_id(value)
        elif isinstance(value, dict):
            value2 = ifcopenshell.create_entity(value["type"])
            value2[0] = value["value"]
            return value2
        return value

    def __eq__(self, other: sqlite_entity) -> bool:
        if not isinstance(self, type(other)):
            return False
        elif None in (self.sqlite_wrapper.file, other.sqlite_wrapper.file):
            assert False  # not implemented
        if self.sqlite_wrapper.id:
            return self.sqlite_wrapper.id == other.sqlite_wrapper.id
        assert False  # not implemented

    def __repr__(self):
        sqlite_wrapper = self.sqlite_wrapper
        attribute_cache = sqlite_wrapper.attribute_cache
        attr_strs: list[str] = []

        if not attribute_cache:
            self.__getitem__(0)  # This will get all attributes

        def serialize_attr_value(value: Any) -> str:
            if value is None:
                attr_str = "$"
            # Enums are not represented correctly but that should do.
            elif isinstance(value, str):
                attr_str = f"'{value}'"
            elif isinstance(value, (int, float)):
                attr_str = str(value)
            elif isinstance(value, sqlite_entity):
                attr_str = f"#{value.sqlite_wrapper.id}"
            elif isinstance(value, entity_instance):
                attr_str = str(value)
            elif isinstance(value, tuple):
                attr_str = ",".join(serialize_attr_value(v) for v in value)
                attr_str = f"({attr_str})"
            else:
                attr_str = f"-"
            return attr_str

        for attr_name in sqlite_wrapper.attributes:
            value = attribute_cache[attr_name]
            attr_strs.append(serialize_attr_value(value))
        attr_str = ",".join(attr_strs)
        return f"#{sqlite_wrapper.id}={sqlite_wrapper.ifc_class.upper()}({attr_str});"

    def __hash__(self) -> int:
        if self.sqlite_wrapper.id:
            return hash((self.sqlite_wrapper.id, self.sqlite_wrapper.file.filepath))

    def get_info(
        self, include_identifier=True, recursive=False, return_type=dict, ignore=(), scalar_only=False
    ) -> dict[str, Any]:
        info = {"id": self.sqlite_wrapper.id, "type": self.sqlite_wrapper.ifc_class}
        if not self.sqlite_wrapper.attribute_cache:
            self.__getitem__(0)  # This will get all attributes
        info.update(self.sqlite_wrapper.attribute_cache)
        return info

    @property
    def file(self) -> sqlite:
        return self.sqlite_wrapper.file


class sqlite_wrapper:
    def __init__(self, id: int, ifc_class: str, file: sqlite):
        self.id = id
        self.ifc_class = ifc_class
        self.file = file
        self.attributes = self.file.ifc_class_attributes[self.ifc_class]
        self.inverse_attributes = self.file.ifc_class_inverse_attributes[self.ifc_class]
        self.attribute_cache: dict[str, Any] = {}
        self.inverse_attribute_cache = {}

    def __repr__(self) -> str:
        return f"sqlite_wrapper '#{self.id}={self.ifc_class}(...)'"
