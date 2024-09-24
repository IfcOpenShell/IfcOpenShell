# IfcPatch - IFC patching utiliy
# Copyright (C) 2023 Dion Moult <dion@thinkmoult.com>
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


import os
import re
import json
import time
import tempfile
import typing
import itertools
import numpy as np
import multiprocessing
import ifcopenshell
import ifcopenshell.geom
import ifcopenshell.util.attribute
import ifcopenshell.util.element
import ifcopenshell.util.placement
import ifcopenshell.util.schema
import ifcopenshell.util.shape
import ifcopenshell.util.unit
from typing import Any

SQLTypes = typing.Literal["SQLite", "MySQL"]

try:
    import sqlite3
except:
    print("No SQLite support")
    SQLTypes = typing.Literal["MySQL"]

try:
    import mysql.connector
except:
    print("No MySQL support")
    SQLTypes = typing.Literal["SQLite"]


class Patcher:
    def __init__(
        self,
        src,
        file,
        logger,
        sql_type: SQLTypes = "SQLite",
        host: str = "localhost",
        username: str = "root",
        password: str = "pass",
        database: str = "test",
    ):
        """Convert an IFC-SPF model to SQLite or MySQL.

        There are certain controls which are hardcoded in this recipe that you
        may modify, including:

        - full_schema: if True, will create tables for all IFC classes,
          regardless if they are used or not in the dataset. If False, will
          only create tables for classes in the dataset.
        - is_strict: whether or not to enforce null or not null. If your
          dataset might contain invalid data, set this to False.
        - should_expand: if True, entities with attributes containing lists of
          entities will be separated into multiple rows. This means the ifc_id
          is no longer a unique primary key. If False, lists will be stored as
          JSON.
        - should_get_psets: if True, a separate psets table will be created to
          make it easy to query properties. This is in addition to regular IFC
          tables like IfcPropertySet.
        - should_get_geometry: Whether or not to process and store explicit
          geometry data as a blob in a separate geometry and shape table.
        - should_skip_geometry_data: Whether or not to also create tables for
          IfcRepresentation and IfcRepresentationItem classes. These tables are
          unnecessary if you are not interested in geometry.

        :param sql_type: Choose between "SQLite" or "MySQL"
        :type sql_type: typing.Literal["SQLite", "MySQL"]

        Example:

        .. code:: python

            # Convert to SQLite, SQLite databse will be saved to a temporary file.
            sqlite_temp_filepath = ifcpatch.execute(
                {"input": "input.ifc", "file": model, "recipe": "Ifc2Sql", "arguments": ["sqlite"]}
            )
        """
        self.src = src
        self.file = file
        self.logger = logger
        self.sql_type = sql_type.lower()
        self.host = host
        self.username = username
        self.password = password
        self.database = database

    def patch(self) -> None:
        self.full_schema = True  # Set true for ifcopenshell.sqlite
        self.is_strict = False
        self.should_expand = False  # Set false for ifcopenshell.sqlite
        self.should_get_inverses = True  # Set true for ifcopenshell.sqlite
        self.should_get_psets = True
        self.should_get_geometry = True  # Set true for ifcopenshell.sqlite
        self.should_skip_geometry_data = False  # Set false for ifcopenshell.sqlite

        self.schema = ifcopenshell.ifcopenshell_wrapper.schema_by_name(self.file.schema)

        if self.sql_type == "sqlite":
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".ifcsqlite")
            db_file = tmp.name
            self.db = sqlite3.connect(db_file)
            self.c = self.db.cursor()
            self.file_patched = db_file
        elif self.sql_type == "mysql":
            self.db = mysql.connector.connect(
                host=self.host, user=self.username, password=self.password, database=self.database
            )
            self.c = self.db.cursor()
            self.file_patched = None

        self.create_id_map()
        self.create_metadata()

        if self.should_get_psets:
            self.create_pset_table()

        if self.should_get_geometry:
            self.create_geometry_table()
            self.create_geometry()

        if self.full_schema:
            ifc_classes = [d.name() for d in self.schema.declarations() if str(d).startswith("<entity")]
        else:
            ifc_classes = self.file.wrapped_data.types()

        for ifc_class in ifc_classes:
            declaration = self.schema.declaration_by_name(ifc_class)

            if self.should_skip_geometry_data:
                if ifcopenshell.util.schema.is_a(declaration, "IfcRepresentation") or ifcopenshell.util.schema.is_a(
                    declaration, "IfcRepresentationItem"
                ):
                    continue

            if self.sql_type == "sqlite":
                self.create_sqlite_table(ifc_class, declaration)
            elif self.sql_type == "mysql":
                self.create_mysql_table(ifc_class, declaration)
            self.insert_data(ifc_class)

        if self.should_get_geometry:
            if self.sql_type == "sqlite":
                if self.shape_rows:
                    self.c.executemany("INSERT INTO shape VALUES (?, ?, ?, ?, ?, ?);", self.shape_rows.values())
                if self.geometry_rows:
                    self.c.executemany("INSERT INTO geometry VALUES (?, ?, ?, ?, ?, ?);", self.geometry_rows.values())
            elif self.sql_type == "mysql":
                if self.shape_rows:
                    self.c.executemany("INSERT INTO shape VALUES (%s, %s, %s, %s, %s, %s);", self.shape_rows.values())
                # Do row by row in case of max_allowed_packet
                for row in self.geometry_rows.values():
                    self.c.execute("INSERT INTO geometry VALUES (%s, %s, %s, %s, %s, %s);", row)

        self.db.commit()
        self.db.close()

    def create_geometry(self) -> None:
        self.unit_scale = ifcopenshell.util.unit.calculate_unit_scale(self.file)

        self.shape_rows = {}
        self.geometry_rows = {}

        if self.file.schema in ("IFC2X3", "IFC4"):
            self.elements = self.file.by_type("IfcElement") + self.file.by_type("IfcProxy")
        else:
            self.elements = self.file.by_type("IfcElement")

        self.settings = ifcopenshell.geom.settings()
        self.settings.set("apply-default-materials", False)

        self.body_contexts = [
            c.id()
            for c in self.file.by_type("IfcGeometricRepresentationSubContext")
            if c.ContextIdentifier in ["Body", "Facetation"]
        ]
        # Ideally, all representations should be in a subcontext, but some BIM programs don't do this correctly
        self.body_contexts.extend(
            [
                c.id()
                for c in self.file.by_type("IfcGeometricRepresentationContext", include_subtypes=False)
                if c.ContextType == "Model"
            ]
        )
        self.settings.set("context-ids", self.body_contexts)

        products = self.elements
        iterator = ifcopenshell.geom.iterator(self.settings, self.file, multiprocessing.cpu_count(), include=products)
        valid_file = iterator.initialize()
        checkpoint = time.time()
        progress = 0
        total = len(products)
        while True:
            progress += 1
            if progress % 250 == 0:
                percent_created = round(progress / total * 100)
                percent_preprocessed = iterator.progress()
                percent_average = (percent_created + percent_preprocessed) / 2
                print(
                    "{} / {} ({}% created, {}% preprocessed) elements processed in {:.2f}s ...".format(
                        progress, total, percent_created, percent_preprocessed, time.time() - checkpoint
                    )
                )
                checkpoint = time.time()
            shape = iterator.get()
            if shape:
                if shape.geometry.id not in self.geometry_rows:
                    v = np.array(shape.geometry.verts).tobytes()
                    e = np.array(shape.geometry.edges).tobytes()
                    f = np.array(shape.geometry.faces).tobytes()
                    mids = np.array(shape.geometry.material_ids).tobytes()
                    m = json.dumps([m.instance_id() for m in shape.geometry.materials])
                    self.geometry_rows[shape.geometry.id] = [shape.geometry.id, v, e, f, mids, m]
                m = ifcopenshell.util.shape.get_shape_matrix(shape)
                m[0][3] /= self.unit_scale
                m[1][3] /= self.unit_scale
                m[2][3] /= self.unit_scale
                x, y, z = m[:, 3][0:3]
                self.shape_rows[shape.id] = [shape.id, float(x), float(y), float(z), m.tobytes(), shape.geometry.id]
            if not iterator.next():
                break

    def create_id_map(self) -> None:
        if self.sql_type == "sqlite":
            statement = (
                "CREATE TABLE IF NOT EXISTS id_map (ifc_id integer PRIMARY KEY NOT NULL UNIQUE, ifc_class text);"
            )
        elif self.sql_type == "mysql":
            statement = """
            CREATE TABLE `id_map` (
              `ifc_id` int(10) unsigned NOT NULL,
              `ifc_class` varchar(255) NOT NULL,
              PRIMARY KEY (`ifc_id`)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;
            """
        self.c.execute(statement)

    def create_metadata(self) -> None:
        # There is no "standard" SQL serialisation, so we propose a convention
        # of a "metadata" table to hold high level metadata. This includes the
        # preprocessor field to uniquely identify the "variant" of SQL schema
        # used. If someone wants their own SQL schema variant, they can
        # identify it using the preprocessor field.
        # IfcOpenShell-1.0.0 represents a schema where 1 table = 1 declaration.
        # IfcOpenShell-2.0.0 represents a schema where tables represent types.
        metadata = ["IfcOpenShell-1.0.0", self.file.schema, self.file.header.file_description.description[0]]
        if self.sql_type == "sqlite":
            statement = "CREATE TABLE IF NOT EXISTS metadata (preprocessor text, schema text, mvd text);"
            self.c.execute(statement)
            self.c.execute("INSERT INTO metadata VALUES (?, ?, ?);", metadata)
        elif self.sql_type == "mysql":
            statement = """
            CREATE TABLE `metadata` (
              `preprocessor` varchar(255) NOT NULL,
              `schema` varchar(255) NOT NULL,
              `mvd` varchar(255) NOT NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;
            """
            self.c.execute(statement)
            self.c.execute("INSERT INTO metadata VALUES (%s, %s, %s);", metadata)

    def create_pset_table(self) -> None:
        statement = """
        CREATE TABLE IF NOT EXISTS psets (
            ifc_id integer NOT NULL,
            pset_name text,
            name text,
            value text
        );
        """
        self.c.execute(statement)

    def create_geometry_table(self) -> None:
        statement = """
        CREATE TABLE IF NOT EXISTS shape (
            ifc_id integer NOT NULL,
            x real,
            y real,
            z real,
            matrix blob,
            geometry text
        );
        """
        self.c.execute(statement)

        statement = """
        CREATE TABLE IF NOT EXISTS geometry (
            id text NOT NULL,
            verts blob,
            edges blob,
            faces blob,
            material_ids blob,
            materials json
        );
        """

        if self.sql_type == "mysql":
            # mediumblob holds up to 16mb, longblob holds up to 4gb
            statement = statement.replace("blob", "mediumblob")

        self.c.execute(statement)

    def create_sqlite_table(self, ifc_class: str, declaration: ifcopenshell.ifcopenshell_wrapper.declaration) -> None:
        statement = f"CREATE TABLE IF NOT EXISTS {ifc_class} ("

        if self.should_expand:
            statement += "ifc_id INTEGER NOT NULL"
        else:
            statement += "ifc_id INTEGER PRIMARY KEY NOT NULL UNIQUE"

        total_attributes = declaration.attribute_count()

        if total_attributes:
            statement += ","

        derived = declaration.derived()
        for i in range(0, total_attributes):
            attribute = declaration.attribute_by_index(i)
            primitive = ifcopenshell.util.attribute.get_primitive_type(attribute)
            data_type = "TEXT"
            if primitive in ("string", "enum"):
                data_type = "TEXT"
            elif primitive in ("entity", "integer", "boolean"):
                data_type = "INTEGER"
            elif primitive == "float":
                data_type = "REAL"
            elif self.should_expand and self.is_entity_list(attribute):
                data_type = "INTEGER"
            elif isinstance(primitive, tuple):
                data_type = "JSON"
            elif primitive == "binary":
                data_type = "TEXT"
            else:
                print("Possibly not implemented attribute data type:", attribute, primitive)
            if not self.is_strict or derived[i]:
                optional = ""
            else:
                optional = "" if attribute.optional() else " NOT NULL"
            comma = "" if i == total_attributes - 1 else ","
            statement += f" `{attribute.name()}` {data_type}{optional}{comma}"
        if self.should_get_inverses:
            statement += ", inverses JSON"
        statement += ");"
        self.c.execute(statement)

    def create_mysql_table(self, ifc_class: str, declaration: ifcopenshell.ifcopenshell_wrapper.declaration) -> None:
        declaration = self.schema.declaration_by_name(ifc_class)
        statement = f"CREATE TABLE IF NOT EXISTS {ifc_class} ("
        statement += "`ifc_id` int(10) unsigned NOT NULL,"

        derived = declaration.derived()
        for attribute in declaration.all_attributes():
            primitive = ifcopenshell.util.attribute.get_primitive_type(attribute)
            if primitive in ("string", "enum"):
                if "IfcText" in str(attribute.type_of_attribute()):
                    data_type = "text"
                else:
                    data_type = "varchar(255)"
            elif primitive == "entity":
                data_type = "int(10) unsigned"
            elif primitive == "boolean":
                data_type = "tinyint(1)"
            elif primitive == "integer":
                data_type = "int(10)"
                if "Positive" in str(attribute.type_of_attribute()):
                    data_type += " unsigned"
            elif primitive == "float":
                data_type = "decimal(10,0)"
            elif self.should_expand and self.is_entity_list(attribute):
                data_type = "int(10) unsigned"
            elif isinstance(primitive, tuple):
                data_type = "JSON"
            else:
                print(attribute, primitive)  # Not implemented?
            if not self.is_strict or derived[i]:
                optional = "DEFAULT NULL"
            else:
                optional = "DEFAULT NULL" if attribute.optional() else "NOT NULL"
            statement += f" `{attribute.name()}` {data_type} {optional},"

        if self.should_expand:
            statement = statement[0:-1]
        else:
            statement += " PRIMARY KEY (`ifc_id`)"

        statement += ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;"
        self.c.execute(statement)

    def insert_data(self, ifc_class: str) -> None:
        elements = self.file.by_type(ifc_class, include_subtypes=False)

        rows = []
        id_map_rows = []
        pset_rows = []

        for element in elements:
            nested_indices = []
            values = [element.id()]
            for i, attribute in enumerate(element):
                if isinstance(attribute, ifcopenshell.entity_instance):
                    if attribute.id():
                        values.append(attribute.id())
                    else:
                        values.append(json.dumps({"type": attribute.is_a(), "value": attribute.wrappedValue}))
                elif (
                    self.should_expand
                    and attribute
                    and isinstance(attribute, tuple)
                    and isinstance(attribute[0], ifcopenshell.entity_instance)
                ):
                    nested_indices.append(i + 1)
                    serialised_attribute = self.serialise_value(element, attribute)
                    if attribute[0].id():
                        values.append(serialised_attribute)
                    else:
                        values.append(json.dumps(serialised_attribute))
                elif isinstance(attribute, tuple):
                    attribute = self.serialise_value(element, attribute)
                    values.append(json.dumps(attribute))
                else:
                    values.append(attribute)

            if self.should_get_inverses:
                values.append(json.dumps([e.id() for e in self.file.get_inverse(element)]))

            if self.should_expand:
                rows.extend(self.get_permutations(values, nested_indices))
            else:
                rows.append(values)

            id_map_rows.append([element.id(), ifc_class])

            if self.should_get_psets:
                psets = ifcopenshell.util.element.get_psets(element)
                for pset_name, pset_data in psets.items():
                    for prop_name, value in pset_data.items():
                        if prop_name == "id":
                            continue
                        if isinstance(value, list):
                            value = json.dumps(value)
                        pset_rows.append([element.id(), pset_name, prop_name, value])

            if self.should_get_geometry:
                if element.id() not in self.shape_rows and getattr(element, "ObjectPlacement", None):
                    m = ifcopenshell.util.placement.get_local_placement(element.ObjectPlacement)
                    x, y, z = m[:, 3][0:3]
                    self.shape_rows[element.id()] = [element.id(), float(x), float(y), float(z), m.tobytes(), None]

        if self.sql_type == "sqlite":
            if rows:
                self.c.executemany(f"INSERT INTO {ifc_class} VALUES ({','.join(['?']*len(rows[0]))});", rows)
                self.c.executemany("INSERT INTO id_map VALUES (?, ?);", id_map_rows)
            if pset_rows:
                self.c.executemany("INSERT INTO psets VALUES (?, ?, ?, ?);", pset_rows)
        elif self.sql_type == "mysql":
            if rows:
                self.c.executemany(f"INSERT INTO {ifc_class} VALUES ({','.join(['%s']*len(rows[0]))});", rows)
                self.c.executemany("INSERT INTO id_map VALUES (%s, %s);", id_map_rows)
            if pset_rows:
                self.c.executemany("INSERT INTO psets VALUES (%s, %s, %s, %s);", pset_rows)

    def serialise_value(self, element: ifcopenshell.entity_instance, value: Any) -> Any:
        return element.walk(
            lambda v: isinstance(v, ifcopenshell.entity_instance),
            lambda v: v.id() if v.id() else {"type": v.is_a(), "value": v.wrappedValue},
            value,
        )

    def get_permutations(self, lst: list[Any], indexes: list[int]) -> list[Any]:
        nested_lists = [lst[i] for i in indexes]

        # Generate the Cartesian product of the nested lists
        products = list(itertools.product(*nested_lists))

        # Place the elements of each product back in their original positions
        final_lists = []
        for product in products:
            temp_list = lst[:]
            for i, index in enumerate(indexes):
                temp_list[index] = product[i]
            final_lists.append(temp_list)

        return final_lists

    def is_entity_list(self, attribute: ifcopenshell.ifcopenshell_wrapper.attribute) -> bool:
        attribute = str(attribute.type_of_attribute())
        if (attribute.startswith("<list") or attribute.startswith("<set")) and "<entity" in attribute:
            for data_type in re.findall("<(.*?) .*?>", attribute):
                if data_type not in ("list", "set", "select", "entity"):
                    return False
            return True
        return False
