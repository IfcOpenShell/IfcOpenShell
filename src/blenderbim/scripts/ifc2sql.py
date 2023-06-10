import os
import json
import itertools
import ifcopenshell
import ifcopenshell.util.schema
import ifcopenshell.util.attribute

import sqlite3
import mysql.connector


class Ifc2Sql:
    def execute(self):
        self.sql_type = "sqlite"
        # self.sql_type = "mysql"

        self.full_schema = False
        self.is_strict = False
        self.should_get_psets = True
        self.should_expand = True
        self.should_get_geometry_blob = True
        self.should_skip_geometry_data = True

        filepath = "/home/dion/test2.ifc"
        self.file = ifcopenshell.open(filepath)
        self.schema = ifcopenshell.ifcopenshell_wrapper.schema_by_name(self.file.schema)

        if self.sql_type == "sqlite":
            db_file = "/home/dion/test.db"
            os.remove(db_file)
            self.db = sqlite3.connect(db_file)
        elif self.sql_type == "mysql":
            self.db = mysql.connector.connect(
                host="localhost",
                user="root",
                password="root",
                database="test"
            )

        self.create_id_map()
        if self.should_get_psets:
            self.create_pset_table()

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

        self.db.close()

    def create_id_map(self):
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
        c = self.db.cursor()
        c.execute(statement)

    def create_pset_table(self):
        statement = """
        CREATE TABLE IF NOT EXISTS psets (
            ifc_id integer NOT NULL,
            pset_name text,
            name text,
            value text
        );
        """
        c = self.db.cursor()
        c.execute(statement)

    def create_sqlite_table(self, ifc_class, declaration):
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
            print(attribute.name(), primitive)
            if primitive in ("string", "enum"):
                data_type = "TEXT"
            elif primitive in ("entity", "integer", "boolean"):
                data_type = "INTEGER"
            elif primitive == "float":
                data_type = "REAL"
            elif self.should_expand and self.is_entity_list(primitive):
                data_type = "INTEGER"
            elif isinstance(primitive, tuple):
                data_type = "JSON"
            else:
                print(attribute, primitive)  # Not implemented?
            if not self.is_strict or derived[i]:
                optional = ""
            else:
                optional = "" if attribute.optional() else " NOT NULL"
            comma = "" if i == total_attributes - 1 else ","
            statement += f" `{attribute.name()}` {data_type}{optional}{comma}"
        statement += ");"
        print(statement)
        c = self.db.cursor()
        c.execute(statement)

    def create_mysql_table(self, ifc_class, declaration):
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
            elif self.should_expand and self.is_entity_list(primitive):
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
        print(statement)
        c = self.db.cursor()
        c.execute(statement)

    def insert_data(self, ifc_class):
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
                    attribute = self.serialise_value(element, attribute)
                    values.append(attribute)
                elif isinstance(attribute, tuple):
                    attribute = self.serialise_value(element, attribute)
                    values.append(json.dumps(attribute))
                else:
                    values.append(attribute)

            if self.should_expand:
                print(values)
                rows.extend(self.get_permutations(values, nested_indices))
            else:
                rows.append(values)

            id_map_rows.append([element.id(), ifc_class])

            if self.should_get_psets:
                psets = ifcopenshell.util.element.get_psets(element)
                if psets:
                    print(psets)
                for pset_name, pset_data in psets.items():
                    for prop_name, value in pset_data.items():
                        if prop_name == "id":
                            continue
                        pset_rows.append([element.id(), pset_name, prop_name, value])
        c = self.db.cursor()

        print(rows)

        if rows:
            if self.sql_type == "sqlite":
                c.executemany(f"INSERT INTO {ifc_class} VALUES ({','.join(['?']*len(rows[0]))});", rows)
                c.executemany("INSERT INTO id_map VALUES (?, ?);", id_map_rows)
                if pset_rows:
                    c.executemany("INSERT INTO psets VALUES (?, ?, ?, ?);", pset_rows)
            elif self.sql_type == "mysql":
                c.executemany(f"INSERT INTO {ifc_class} VALUES ({','.join(['%s']*len(rows[0]))});", rows)
                c.executemany("INSERT INTO id_map VALUES (%s, %s);", id_map_rows)
                if pset_rows:
                    c.executemany("INSERT INTO psets VALUES (%s, %s, %s, %s);", pset_rows)

        self.db.commit()

    def serialise_value(self, element, value):
        return element.walk(
            lambda v: isinstance(v, ifcopenshell.entity_instance),
            lambda v: v.id() if v.id() else {"type": v.is_a(), "value": v.wrappedValue},
            value,
        )

    def get_permutations(self, lst, indexes):
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

    def is_entity_list(self, primitive):
        if not isinstance(primitive, tuple):
            return False
        elif primitive[0] == "select":
            return False
        elif primitive[1] == "entity":
            return True
        elif isinstance(primitive[1], tuple):
            return self.is_entity_list(primitive[1])
        return False


Ifc2Sql().execute()
