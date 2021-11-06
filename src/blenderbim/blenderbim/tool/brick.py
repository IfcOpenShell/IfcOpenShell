# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of BlenderBIM Add-on.
#
# BlenderBIM Add-on is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# BlenderBIM Add-on is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with BlenderBIM Add-on.  If not, see <http://www.gnu.org/licenses/>.

import os
import bpy
import brickschema
import blenderbim.core.tool
import blenderbim.tool as tool


class Brick(blenderbim.core.tool.Brick):
    @classmethod
    def set_user(cls, user):
        bpy.context.scene.BIMOwnerProperties.active_user_id = user.id()

    @classmethod
    def add_brick_breadcrumb(cls):
        new = bpy.context.scene.BIMBrickProperties.brick_breadcrumbs.add()
        new.name = bpy.context.scene.BIMBrickProperties.active_brick_class

    @classmethod
    def clear_brick_browser(cls):
        bpy.context.scene.BIMBrickProperties.bricks.clear()

    @classmethod
    def clear_project(cls):
        BrickStore.graph = None
        bpy.context.scene.BIMBrickProperties.active_brick_class == ""
        bpy.context.scene.BIMBrickProperties.brick_breadcrumbs.clear()

    @classmethod
    def get_item_class(cls, item):
        query = BrickStore.graph.query(
            """
            PREFIX brick: <https://brickschema.org/schema/Brick#>
            SELECT ?class WHERE {
               <{item}> a ?class .
            }
            LIMIT 1
        """.replace(
                "{item}", item
            )
        )
        for row in query:
            return row.get("class").toPython().split("#")[-1]

    @classmethod
    def import_brick_classes(cls, brick_class):
        query = BrickStore.graph.query(
            """
            PREFIX brick: <https://brickschema.org/schema/Brick#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            SELECT ?group (count(?item) as ?total_items) WHERE {
                ?group rdfs:subClassOf brick:{brick_class} .
                ?item rdf:type/rdfs:subClassOf* ?group
            }
            GROUP BY ?group
            ORDER BY asc(?group)
        """.replace(
                "{brick_class}", brick_class
            )
        )
        for row in query:
            new = bpy.context.scene.BIMBrickProperties.bricks.add()
            new.name = row.get("group").toPython().split("#")[-1]
            new.uri = row.get("group").toPython()
            new.total_items = row.get("total_items").toPython()

    @classmethod
    def import_brick_items(cls, brick_class):
        query = BrickStore.graph.query(
            """
            PREFIX brick: <https://brickschema.org/schema/Brick#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            SELECT ?item WHERE {
                ?item rdf:type brick:{brick_class}
            }
            ORDER BY asc(?item)
        """.replace(
                "{brick_class}", brick_class
            )
        )
        for row in query:
            new = bpy.context.scene.BIMBrickProperties.bricks.add()
            new.name = row.get("item").toPython().split("#")[-1]
            new.uri = row.get("item").toPython()

    @classmethod
    def load_brick_file(cls, filepath):
        if not BrickStore.schema:
            BrickStore.schema = brickschema.Graph()
            cwd = os.path.dirname(os.path.realpath(__file__))
            schema_path = os.path.join(cwd, "..", "bim", "schema", "Brick.ttl")
            BrickStore.schema.load_file(schema_path)
        BrickStore.graph = brickschema.Graph().load_file(filepath) + BrickStore.schema

    @classmethod
    def pop_brick_breadcrumb(cls):
        crumb = bpy.context.scene.BIMBrickProperties.brick_breadcrumbs[-1]
        name = crumb.name
        last_index = len(bpy.context.scene.BIMBrickProperties.brick_breadcrumbs) - 1
        bpy.context.scene.BIMBrickProperties.brick_breadcrumbs.remove(last_index)
        return name

    @classmethod
    def select_browser_item(cls, item):
        name = item.split("#")[-1]
        props = bpy.context.scene.BIMBrickProperties
        props.active_brick_index = props.bricks.find(name)

    @classmethod
    def set_active_brick_class(cls, brick_class):
        bpy.context.scene.BIMBrickProperties.active_brick_class = brick_class


class BrickStore:
    schema = None
    graph = None

    @staticmethod
    def purge():
        BrickStore.schema = None
        BrickStore.graph = None
