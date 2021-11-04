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

import bpy
import blenderbim.tool as tool
from blenderbim.tool.brick import BrickStore


def refresh():
    BrickschemaData.is_loaded = False


class BrickschemaData:
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        cls.data = {"is_loaded": cls.get_is_loaded(), "attributes": cls.attributes()}
        cls.is_loaded = True

    @classmethod
    def get_is_loaded(cls):
        return BrickStore.graph is not None

    @classmethod
    def attributes(cls):
        if BrickStore.graph is None:
            return []
        props = bpy.context.scene.BIMBrickProperties
        try:
            brick = props.bricks[props.active_brick_index]
        except:
            return []
        results = []
        uri = brick.uri
        query = BrickStore.graph.query(
            """
            PREFIX brick: <https://brickschema.org/schema/Brick#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            SELECT DISTINCT ?name ?value ?sp ?sv WHERE {
               <{uri}> ?name ?value .
               OPTIONAL {
               { ?name rdfs:range brick:TimeseriesReference . }
                UNION
               { ?name a brick:EntityProperty . }
                ?value ?sp ?sv }
            }
        """.replace(
                "{uri}", uri
            )
        )
        for row in query:
            results.append(
                {
                    "name": row.get("name").toPython().split("#")[-1],
                    "value": row.get("value").toPython().split("#")[-1],
                    "is_uri": "#" in row.get("value").toPython(),
                    "value_uri": row.get("value").toPython(),
                }
            )
        return results
